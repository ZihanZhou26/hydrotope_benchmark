import json
from fractions import Fraction
from itertools import permutations
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import sympy as sp

import common
import exact_oracle

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

T = sp.symbols("t", rational=True)
DECADES = range(2, 8)

FAMILIES = [
    [(Fraction(1, 1), Fraction(1, 1)), (Fraction(-2, 1), Fraction(1, 1)), (Fraction(1, 2), Fraction(0, 1)), (Fraction(1, 3), Fraction(0, 1))],
    [(Fraction(2, 1), Fraction(2, 1)), (Fraction(-3, 1), Fraction(1, 1)), (Fraction(1, 1), Fraction(0, 1)), (Fraction(1, 2), Fraction(0, 1))],
    [(Fraction(1, 1), Fraction(0, 1)), (Fraction(-3, 2), Fraction(1, 1)), (Fraction(-2, 1), Fraction(0, 1)), (Fraction(1, 4), Fraction(1, 1))],
    [(Fraction(3, 1), Fraction(-1, 1)), (Fraction(-1, 1), Fraction(1, 1)), (Fraction(2, 1), Fraction(0, 1)), (Fraction(-1, 2), Fraction(0, 1))],
    [(Fraction(-1, 1), Fraction(2, 1)), (Fraction(4, 1), Fraction(-1, 1)), (Fraction(1, 1), Fraction(0, 1)), (Fraction(-1, 3), Fraction(1, 1))],
    [(Fraction(2, 1), Fraction(0, 1)), (Fraction(-5, 2), Fraction(1, 1)), (Fraction(3, 1), Fraction(0, 1)), (Fraction(-1, 1), Fraction(1, 1))],
    [(Fraction(-3, 1), Fraction(1, 1)), (Fraction(4, 1), Fraction(1, 1)), (Fraction(-1, 2), Fraction(0, 1)), (Fraction(1, 1), Fraction(-1, 1))],
    [(Fraction(5, 2), Fraction(-1, 1)), (Fraction(-3, 2), Fraction(1, 1)), (Fraction(1, 1), Fraction(0, 1)), (Fraction(1, 1), Fraction(0, 1))],
    [(Fraction(1, 2), Fraction(1, 1)), (Fraction(-1, 1), Fraction(1, 1)), (Fraction(2, 1), Fraction(1, 1)), (Fraction(-1, 2), Fraction(-1, 1))],
    [(Fraction(3, 1), Fraction(1, 1)), (Fraction(-2, 1), Fraction(2, 1)), (Fraction(-1, 1), Fraction(0, 1)), (Fraction(1, 4), Fraction(0, 1))],
    [(Fraction(-2, 1), Fraction(1, 1)), (Fraction(1, 1), Fraction(1, 1)), (Fraction(3, 2), Fraction(0, 1)), (Fraction(-1, 2), Fraction(1, 1))],
    [(Fraction(2, 1), Fraction(1, 1)), (Fraction(-4, 1), Fraction(1, 1)), (Fraction(1, 3), Fraction(0, 1)), (Fraction(1, 2), Fraction(-1, 1))],
]


def _frac_to_sym(v: Fraction) -> sp.Rational:
    return sp.Rational(v.numerator, v.denominator)


def _to_fraction14(v) -> Fraction:
    return Fraction(f"{float(v):.14f}")


def _symbolic_omegas_from_family(family: Sequence[tuple]):
    vals = [
        _frac_to_sym(c) + _frac_to_sym(d) * T for c, d in family
    ]
    w2, w3, w4, w5 = vals
    free_sum = w2 + w3 + w4 + w5
    qsum = -w2 * w2 - w3 * w3 + w4 * w4 + w5 * w5
    w6 = (qsum - free_sum * free_sum) / (2 * free_sum)
    w1 = -(free_sum + w6)
    return [sp.expand(w1), w2, w3, w4, w5, w6]


def _family_omega(family: Sequence[tuple], t: Fraction):
    free = [c + d * t for c, d in family]
    return list(common.solve_from_free(free, common.SIG_FULL))


def _wall_expr(wall, omega_sym: Sequence[sp.Expr]) -> sp.Expr:
    I_mask = int(wall["I_mask"])
    J_mask = int(wall["J_mask"])
    kind = str(wall.get("kind", "diff"))

    sI = sp.Integer(0)
    for i in common.subset_bits(I_mask):
        sI += omega_sym[i] * omega_sym[i]

    if kind in ("diff", "boundary"):
        sJ = sp.Integer(0)
        for j in common.subset_bits(J_mask):
            sJ += omega_sym[3 + j] * omega_sym[3 + j]
        return sp.expand(sI - sJ)

    if kind == "sum":
        j = int(wall.get("plus_anchor", 0))
        sM = omega_sym[0] * omega_sym[0] + omega_sym[1] * omega_sym[1] + omega_sym[2] * omega_sym[2]
        return sp.expand(sI + omega_sym[3 + j] * omega_sym[3 + j] - sM)

    raise ValueError(f"unknown wall kind {kind}")


def _wall_value(wall, omega: Sequence[Fraction]) -> Fraction:
    a2 = [w * w for w in omega]
    return common.wall_value(a2, wall)


def _wall_orbits():
    wall_catalog = common.build_wall_catalog()
    buckets = {}
    for wall in wall_catalog:
        key = tuple(wall.get("subset_size_orbit", wall.get("subset_sizes", [])))
        buckets.setdefault(key, []).append(wall)

    out = []
    for key in [(1, 1), (1, 2)]:
        if key not in buckets:
            continue
        out.append((key, buckets[key]))
    return out


def _validate(omega: Sequence[Fraction], target_wall_id, wall_catalog, ext_catalog) -> Tuple[bool, str]:
    free = [omega[1], omega[2], omega[3], omega[4]]
    if sum(free) == 0:
        return False, "free_sum_zero"
    if any(w == 0 for w in omega):
        return False, "zero_omega"

    for wall in ext_catalog:
        if _wall_value(wall, omega) == 0:
            return False, f"external_wall_zero:{wall['id']}"

    for wall in wall_catalog:
        if wall["id"] == target_wall_id:
            continue
        if _wall_value(wall, omega) == 0:
            return False, f"wall_zero:{wall['id']}"

    for mask in common.internal_subset_bits(6):
        h, _ = common.h_T(omega, mask, common.SIG_FULL)
        if h == 0:
            return False, f"other_triple_zero:{mask}"

    return True, "ok"


def _other_min_h(omega: Sequence[Fraction], target_wall):
    target_masks = set()
    for wall in target_wall:
        target_masks.update([int(wall["I_mask"]), int(wall["J_mask"])])

    vals = []
    for mask in common.internal_subset_bits(6):
        if mask in target_masks:
            continue
        h, _ = common.h_T(omega, mask, common.SIG_FULL)
        vals.append(abs(h))
    return min(vals) if vals else Fraction(0)


def _nearest_other_wall(omega: Sequence[Fraction], wall_catalog, exclude_id):
    best = None
    best_id = ""
    a = [w * w for w in omega]
    for wall in wall_catalog:
        wall_id = str(wall["id"])
        if wall_id == exclude_id:
            continue
        val = common.wall_value(a, wall)
        abs_val = abs(val)
        if best is None or abs_val < best:
            best = abs_val
            best_id = wall_id
    return best, best_id


def _nearest_triple_pole(omega: Sequence[Fraction]):
    best_abs = None
    best_mask = None
    best_h = Fraction(0)
    for mask in common.internal_subset_bits(6):
        h, _ = common.h_T(omega, mask, common.SIG_FULL)
        abs_h = abs(h)
        if best_abs is None or abs_h < best_abs:
            best_abs = abs_h
            best_mask = mask
            best_h = h
    return best_mask, best_h, best_abs


def _to_wall_family_solutions(wall, family, wall_catalog, ext_catalog):
    omega_sym = _symbolic_omegas_from_family(family)
    expr = _wall_expr(wall, omega_sym)
    num = sp.together(expr).as_numer_denom()[0]
    poly = sp.Poly(sp.expand(num), T)
    if poly.total_degree() < 1:
        return []

    roots = sp.nroots(poly.as_expr(), n=60, maxsteps=120)
    out = []

    for root in roots:
        if abs(complex(root).imag) > 1e-16:
            continue
        t0 = _to_fraction14(float(complex(root).real))
        try:
            omega = _family_omega(family, t0)
        except Exception:
            continue
        try:
            q_expr_val = expr.subs(T, sp.Rational(t0.numerator, t0.denominator))
            if abs(complex(q_expr_val.evalf(80))) > 1e-8:
                continue
        except Exception:
            continue

        q_target = _wall_value(wall, omega)
        if abs(float(q_target)) >= 1e-8:
            continue
        ok, _ = _validate(omega, str(wall["id"]), wall_catalog, ext_catalog)
        if not ok:
            continue
        out.append((t0, q_target, omega))

    return out


def _ratio_check(values: List[float], lo=0.03, hi=0.3) -> bool:
    if len(values) < 3:
        return False
    values = [abs(v) for v in values]
    final = values[-3:]
    return lo <= final[1] / final[0] <= hi and lo <= final[2] / final[1] <= hi


def _classify(samples: List[dict]) -> Dict[str, object]:
    by_side = {-1: [], 1: []}
    for s in samples:
        by_side[s["side"]].append(s)

    info = {
        "q_ratio_ok": True,
        "q_nonzero": True,
        "class": "not_located",
        "sample_count": len(samples),
    }

    for side in (-1, 1):
        rows = sorted(by_side[side], key=lambda x: x["decade"])
        if len(rows) == 0:
            info["q_ratio_ok"] = False
            return info
        if len(rows) < 3:
            info["q_ratio_ok"] = False
            return info

        q_vals = [float(s["float"]["q_abs"]) for s in rows]
        if not all(v > 1e-8 for v in q_vals):
            info["q_nonzero"] = False
            return info
        if not _ratio_check(q_vals):
            info["q_ratio_ok"] = False

    if info["q_ratio_ok"] and info["sample_count"] == 12:
        info["class"] = "covered"
    elif info["q_ratio_ok"]:
        info["class"] = "not_located"
    else:
        info["class"] = "rejected_scaling"
        return info
    return info


def _evaluate_side(wall, family, t_center: Fraction, sign: int, wall_catalog, ext_catalog):
    samples = []
    for d in DECADES:
        t = t_center + sign * Fraction(1, 10**d)
        try:
            omega = _family_omega(family, t)
        except Exception:
            continue

        free = [omega[1], omega[2], omega[3], omega[4]]
        if sum(free) == 0 or any(w == 0 for w in omega):
            continue

        q_target = _wall_value(wall, omega)
        if abs(float(q_target)) < 1e-8:
            continue

        ok, _ = _validate(omega, str(wall["id"]), wall_catalog, ext_catalog)
        if not ok:
            continue

        try:
            row = exact_oracle.evaluate_omega(omega, "wall-side", wall_catalog)
        except Exception:
            continue

        nearest_other_wall = _nearest_other_wall(omega, wall_catalog, str(wall["id"]))
        nearest_pole_mask, nearest_pole_h, nearest_pole_abs = _nearest_triple_pole(omega)
        other_min_h = _other_min_h(omega, [wall])

        samples.append(
            {
                "side": sign,
                "decade": d,
                "delta": common.frac_to_str(Fraction(1, 10**d)),
                "t": common.frac_to_str(t),
                "A_im": common.frac_to_str(row.A_im),
                "q": common.frac_to_str(q_target),
                "wall_min_other": {
                    "id": nearest_other_wall[1],
                    "abs": common.frac_to_str(nearest_other_wall[0]),
                },
                "nearest_pole": {
                    "mask": nearest_pole_mask,
                    "h": common.frac_to_str(nearest_pole_h),
                    "abs": common.frac_to_str(nearest_pole_abs),
                },
                "other_min_h": common.frac_to_str(other_min_h),
                "wall_signature": row.wall_signature,
                "wall_signature_swap": row.wall_signature_swap,
                "wall_signature_raw": row.raw_wall_signature,
                "free_w": [common.frac_to_str(x) for x in free],
                "omega": [common.frac_to_str(x) for x in omega],
                "float": {
                    "A_abs": abs(float(row.A_im)),
                    "q_abs": abs(float(q_target)),
                    "other_min_h_abs": float(abs(other_min_h)),
                },
            }
        )

    return samples


def _write_report(entries: List[dict]):
    lines = []
    for entry in entries:
        line = (
            f"orbit={entry['orbit']} status={entry['status']} "
            f"found={entry['found']} samples={len(entry.get('samples', []))} class={entry.get('checks', {}).get('class')}"
        )
        lines.append(line)
    (DATA_DIR / "wall_report.txt").write_text("\n".join(lines) + "\n")


def main():
    wall_catalog = common.build_wall_catalog()
    ext_catalog = common.build_external_wall_catalog()

    entries = []
    for orbit_key, walls in _wall_orbits():
        rep = walls[0]
        entry = {
            "orbit": str(orbit_key),
            "wall_ids": [str(w["id"]) for w in walls],
            "found": False,
            "samples": [],
            "status": "scan",
        }

        accepted = False
        for fi, family in enumerate(FAMILIES):
            sols = _to_wall_family_solutions(rep, family, wall_catalog, ext_catalog)
            if not sols:
                continue

            for t_root, q_root, omega_root in sols:
                sample_rows = []
                sample_rows.extend(_evaluate_side(rep, family, t_root, -1, wall_catalog, ext_catalog))
                sample_rows.extend(_evaluate_side(rep, family, t_root, 1, wall_catalog, ext_catalog))
                checks = _classify(sample_rows)
                if not (checks.get("q_ratio_ok", False) and checks.get("sample_count", 0) == 12):
                    continue

                entry.update(
                    {
                        "found": True,
                        "family": fi,
                        "t_root": common.frac_to_str(t_root),
                        "q_root": common.frac_to_str(q_root),
                        "omega_root": [common.frac_to_str(x) for x in omega_root],
                        "samples": sample_rows,
                        "checks": checks,
                    }
                )
                accepted = True
                break
            if accepted:
                break

        if not accepted:
            entry["checks"] = {
                "class": "not_located",
                "q_ratio_ok": False,
                "q_nonzero": False,
                "sample_count": 0,
            }

        entries.append(entry)

    (DATA_DIR / "wall_approaches.json").write_text(json.dumps(entries, indent=2))
    _write_report(entries)


if __name__ == "__main__":
    main()
