#!/usr/bin/env python3
"""One-sided wall smoothness diagnostics from wall-approach data.

Inputs:
- `data/wall_approaches.json`

Outputs:
- `data/wall_smoothness.json`
- `data/wall_smoothness.txt`
"""

import json
import time
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import common


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

ORDERS = (4, 5, 6)
MAX_K = 4
DECIMAL_PLACES = 80
ZERO_TOL = Decimal("1e-70")
STABLE_REL_TOL = Decimal("1e-18")
STABLE_ABS_TOL = Decimal("1e-70")


def _frac_to_fraction(v) -> Fraction:
    if isinstance(v, Fraction):
        return v
    return common.parse_fraction(v)


def _frac_to_decimal(frac: Fraction, places: int = DECIMAL_PLACES) -> str:
    with localcontext() as ctx:
        ctx.prec = places + 40
        d = Decimal(frac.numerator) / Decimal(frac.denominator)
        return format(d, f".{places}f")


def _solve_linear_exact(A: List[List[Fraction]], b: List[Fraction]):
    if not A:
        return None, {"status": "empty", "matrix_rank": 0, "matrix_rank_aug": 0}

    m = len(A)
    n = len(A[0])
    if m != n:
        return None, {"status": f"non-square matrix m={m} n={n}", "matrix_rank": 0, "matrix_rank_aug": 0}

    aug = [list(row) + [b[i]] for i, row in enumerate(A)]
    row = 0
    pivots: Dict[int, int] = {}
    for col in range(n):
        pivot = None
        for rr in range(row, m):
            if aug[rr][col] != 0:
                pivot = rr
                break
        if pivot is None:
            continue

        aug[row], aug[pivot] = aug[pivot], aug[row]
        inv = Fraction(1, 1) / aug[row][col]
        aug[row] = [x * inv for x in aug[row]]

        for rr in range(m):
            if rr == row:
                continue
            factor = aug[rr][col]
            if factor == 0:
                continue
            aug[rr] = [x - factor * y for x, y in zip(aug[rr], aug[row])]

        pivots[col] = row
        row += 1

    for rr in range(m):
        if all(v == 0 for v in aug[rr][:-1]) and aug[rr][-1] != 0:
            return None, {"status": "inconsistent", "matrix_rank": row, "matrix_rank_aug": row + 1}

    coeffs = [Fraction(0) for _ in range(n)]
    for col, rr in pivots.items():
        coeffs[col] = aug[rr][-1]

    return coeffs, {"status": "ok", "matrix_rank": row, "matrix_rank_aug": row}


def _fit_one_sided(points: Sequence[Tuple[Fraction, Fraction]], order: int):
    if len(points) < order:
        return None, {"status": "insufficient_points", "requested": order, "available": len(points)}

    sample = points[:order]
    A = []
    b = []
    for x, y in sample:
        row = [Fraction(1)]
        for p in range(1, order):
            row.append(x ** p)
        A.append(row)
        b.append(y)

    coeffs, meta = _solve_linear_exact(A, b)
    if coeffs is None:
        return None, meta

    keep = min(order - 1, MAX_K)
    fit_meta = dict(meta)
    fit_meta["order"] = order
    fit_meta["kept_max_power"] = keep
    return coeffs[: keep + 1], fit_meta


def _fraction_payload(value: Fraction) -> Dict[str, str]:
    return {
        "fraction": common.frac_to_str(value),
        "decimal": _frac_to_decimal(value),
    }


def _is_zero_like(frac: Fraction, tol: Decimal = ZERO_TOL) -> bool:
    return _decimal_abs(frac) <= tol


def _decimal_abs(frac: Fraction) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = DECIMAL_PLACES + 40
        return abs(Decimal(frac.numerator) / Decimal(frac.denominator))


def _sign_safe(frac: Fraction, tol: Decimal = ZERO_TOL) -> int:
    mag = _decimal_abs(frac)
    if mag <= tol:
        return 0
    return 1 if frac > 0 else -1


def _analyze_k_series(values_by_order: Dict[int, Fraction]) -> Dict[str, object]:
    if not values_by_order:
        return {
            "status": "missing",
            "all_orders": [],
            "all_zero_within_tolerance": False,
            "stable_nonzero_with_tolerance": False,
        }

    orders = sorted(values_by_order)
    payload: Dict[str, object] = {
        "all_orders": orders,
        "status": "ok",
        "all_zero_within_tolerance": True,
        "stable_nonzero_with_tolerance": False,
        "values": {},
    }

    values = []
    signs = []
    magnitudes = []
    for order in orders:
        val = values_by_order[order]
        payload["values"][str(order)] = _fraction_payload(val)
        if _is_zero_like(val):
            signs.append(0)
        else:
            payload["all_zero_within_tolerance"] = False
            signs.append(_sign_safe(val))
            magnitudes.append(_decimal_abs(val))

    if magnitudes and all(s != 0 for s in signs):
        if len(set(signs)) == 1:
            max_mag = max(magnitudes)
            min_mag = min(magnitudes)
            spread = max_mag - min_mag
            threshold = max(STABLE_ABS_TOL, STABLE_REL_TOL * max_mag)
            if spread <= threshold:
                payload["stable_nonzero_with_tolerance"] = True

    if payload["all_zero_within_tolerance"]:
        payload["status"] = "agree"
    elif payload["stable_nonzero_with_tolerance"]:
        payload["status"] = "differ_stable"
    else:
        payload["status"] = "mismatch"

    if magnitudes:
        payload["min_abs_decimal"] = str(min(magnitudes))
        payload["max_abs_decimal"] = str(max(magnitudes))

    return payload


def _build_order_payload(points: Dict[int, List[Tuple[Fraction, Fraction]]], orbit: str) -> Dict[str, object]:
    side_payload: Dict[str, object] = {}
    side_diff_payload: Dict[str, Dict[str, object]] = {}

    for side in (-1, 1):
        side_points = points[side]
        side_payload[str(side)] = {}
        side_payload[str(side)]["interpolations"] = {}
        if len(side_points) < max(ORDERS):
            side_payload[str(side)]["status"] = "insufficient_points"
            side_payload[str(side)]["point_count"] = len(side_points)
            continue

        side_payload[str(side)]["point_count"] = len(side_points)
        side_payload[str(side)]["interpolations"] = {}
        side_payload[str(side)]["status"] = "ok"

        for order in ORDERS:
            coeffs, fit_meta = _fit_one_sided(side_points, order)
            if coeffs is None:
                side_payload[str(side)]["interpolations"][str(order)] = {
                    "status": fit_meta.get("status"),
                    "order": order,
                    "reason": fit_meta,
                }
                continue

            side_payload[str(side)]["interpolations"][str(order)] = {
                "status": "ok",
                "order": order,
                "kept_max_power": len(coeffs) - 1,
                "coefficients": {
                    str(k): _fraction_payload(c)
                    for k, c in enumerate(coeffs)
                },
            }

    for order in ORDERS:
        left_interpolations = side_payload["-1"].get("interpolations", {})
        right_interpolations = side_payload["1"].get("interpolations", {})
        left = left_interpolations.get(str(order), {})
        right = right_interpolations.get(str(order), {})
        if left.get("status") != "ok" or right.get("status") != "ok":
            continue

        keep = min(order - 1, MAX_K)
        coeffs_l = [
            _frac_to_fraction(left_interpolations[str(order)]["coefficients"][str(k)]["fraction"])
            for k in range(keep + 1)
        ]
        coeffs_r = [
            _frac_to_fraction(right_interpolations[str(order)]["coefficients"][str(k)]["fraction"])
            for k in range(keep + 1)
        ]

        diffs = {}
        for k in range(keep + 1):
            dif = coeffs_l[k] - coeffs_r[k]
            diffs[str(k)] = _fraction_payload(dif)
        side_diff_payload[str(order)] = {
            "kept_max_power": keep,
            "differences": diffs,
        }

    coefficient_diagnostics = {}
    for k in range(MAX_K + 1):
        by_order = {}
        for order in ORDERS:
            order_payload = side_diff_payload.get(str(order))
            if not order_payload:
                continue
            diff_payload = order_payload["differences"].get(str(k))
            if diff_payload is None:
                continue
            by_order[order] = _frac_to_fraction(diff_payload["fraction"])
        coefficient_diagnostics[str(k)] = _analyze_k_series(by_order)

    expected_map = {
        "(1, 1)": {0: "agree", 1: "differ_stable"},
        "(1, 2)": {0: "agree", 1: "agree", 2: "agree", 3: "differ_stable"},
    }
    pattern_checks = {}
    expected = expected_map.get(orbit, {})
    for k_str, mode in expected.items():
        kdiag = coefficient_diagnostics.get(str(k_str), {})
        status = kdiag.get("status")
        if mode == "agree":
            pattern_ok = status == "agree"
        else:
            pattern_ok = status == "differ_stable"
        pattern_checks[f"k={k_str}"] = {
            "mode": mode,
            "status": status,
            "pass": pattern_ok,
        }

    pattern_ok = all(item.get("pass") for item in pattern_checks.values()) if pattern_checks else False

    return {
        "sides": side_payload,
        "order_differences": side_diff_payload,
        "coefficient_diagnostics_by_k": coefficient_diagnostics,
        "pattern_checks": pattern_checks,
        "pattern_checks_passed": pattern_ok,
    }


def main():
    start = time.time()
    wall_path = DATA_DIR / "wall_approaches.json"
    if not wall_path.exists():
        raise FileNotFoundError(f"missing input: {wall_path}")

    entries = json.loads(wall_path.read_text())
    expected_orbits = {"(1, 1)", "(1, 2)"}

    report: Dict[str, object] = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
        "settings": {
            "interpolation_orders": list(ORDERS),
            "kept_max_power": MAX_K,
            "decimal_places": DECIMAL_PLACES,
            "zero_tolerance": str(ZERO_TOL),
            "stable_abs_tolerance": str(STABLE_ABS_TOL),
            "stable_rel_tolerance": str(STABLE_REL_TOL),
        },
        "orbits": {},
    }

    orbit_payloads = report["orbits"]
    found_orbits = []

    for entry in entries:
        orbit = str(entry.get("orbit"))
        if orbit not in expected_orbits:
            continue

        found_orbits.append(orbit)
        samples = [s for s in entry.get("samples", []) if s.get("side") in (-1, 1)]
        points = {
            -1: [],
            1: [],
        }
        for sample in samples:
            side = int(sample.get("side"))
            if side not in (-1, 1):
                continue
            q = _frac_to_fraction(sample.get("q"))
            y = _frac_to_fraction(sample.get("A_im"))
            points[side].append((q, y))

        for side in (-1, 1):
            points[side].sort(key=lambda xy: xy[0])

        orbit_payload = {
            "found": bool(entry.get("found", False)),
            "sample_count_by_side": {
                "-1": len(points[-1]),
                "1": len(points[1]),
            },
            "first_ten_ordered_q_by_side": {
                "-1": [common.frac_to_str(q) for q, _ in points[-1][:6]],
                "1": [common.frac_to_str(q) for q, _ in points[1][:6]],
            },
            "first_ten_ordered_A_im_by_side": {
                "-1": [common.frac_to_str(y) for _, y in points[-1][:6]],
                "1": [common.frac_to_str(y) for _, y in points[1][:6]],
            },
        }

        orbit_payload.update(_build_order_payload(points, orbit))
        orbit_payloads[orbit] = orbit_payload

    for orbit in sorted(expected_orbits):
        if orbit not in orbit_payloads:
            report["orbits"][orbit] = {
                "found": False,
                "error": "orbit not present in wall_approaches.json",
            }

    txt_out = DATA_DIR / "wall_smoothness.txt"
    report_lines = [
        "wall_smoothness summary",
        f"input: {wall_path}",
        f"found_orbits: {found_orbits}",
        f"orders: {list(ORDERS)}",
        f"kept powers: 0..{MAX_K} (truncated per order)",
        f"machine tolerances: zero={ZERO_TOL}, stable_abs={STABLE_ABS_TOL}, stable_rel={STABLE_REL_TOL}",
    ]

    for orbit in sorted(expected_orbits):
        entry = report["orbits"][orbit]
        report_lines.append(f"orbit={orbit} found={entry.get('found')} sample_counts={entry.get('sample_count_by_side')}")
        if not entry.get("found"):
            report_lines.append(f"  status: {entry.get('error')}")
            continue

        patt = entry.get("pattern_checks", {})
        report_lines.append(f"  pattern checks: {patt}")
        report_lines.append(
            f"  pattern checks passed: {entry.get('pattern_checks_passed', False)}"
        )

        for side in ("-1", "1"):
            interp = entry["sides"][side]["interpolations"]
            report_lines.append(f"  side={side} samples={entry['sides'][side]['point_count']}")
            for order in ORDERS:
                payload = interp.get(str(order), {})
                report_lines.append(f"    order={order} status={payload.get('status', 'missing')}")
                coeffs = payload.get("coefficients", {})
                if isinstance(coeffs, dict) and coeffs:
                    values = [c.get("decimal", "") for _, c in sorted(coeffs.items(), key=lambda kv: int(kv[0]))]
                    report_lines.append("      coeffs=" + ", ".join(values[:5]))

    for orbit in sorted(expected_orbits):
        entry = report["orbits"][orbit]
        diagnostics = entry.get("coefficient_diagnostics_by_k", {})
        if not diagnostics:
            continue
        report_lines.append(f"orbit={orbit} coefficient side-difference diagnostics:")
        for k in sorted(diagnostics, key=lambda k: int(k)):
            diag = diagnostics[k]
            report_lines.append(
                f"  k={k} status={diag.get('status')} all_zero={diag.get('all_zero_within_tolerance')} "
                f"stable={diag.get('stable_nonzero_with_tolerance')}"
            )

    report_lines.append(f"outputs: {DATA_DIR / 'wall_smoothness.json'} {txt_out}")
    report_lines.append(f"elapsed_s={time.time() - start:.1f}")

    (DATA_DIR / "wall_smoothness.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=str))
    txt_out.write_text("\n".join(report_lines) + "\n")
    print("\n".join(report_lines))


if __name__ == "__main__":
    main()
