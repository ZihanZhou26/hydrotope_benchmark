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

# Deterministic affine families (w2,w3,w4,w5) = c + d*t
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

TARGET_COMP = {
    (2, 0): {
        "status": "degenerate",
        "reason": "same-side pair: h = 2*w_a*w_b",
    },
    (1, 1): {
        "status": "degenerate",
        "reason": "mixed pair: q_T=0 or external zero on mixed branches",
    },
    (3, 0): {
        "status": "scan",
    },
    (2, 1): {
        "status": "scan",
    },
}


def _frac_to_sym(v: Fraction) -> sp.Rational:
    return sp.Rational(v.numerator, v.denominator)


def _to_fraction14(v) -> Fraction:
    return Fraction(f"{float(v):.14f}")


def _pair_orbit_members(mask: int) -> List[int]:
    perms = [tuple(p) for p in permutations(range(3))]
    out = set()
    for pm in perms:
        for pp in perms:
            for swap in (False, True):
                m = 0
                for i in range(6):
                    if not ((mask >> i) & 1):
                        continue
                    j = i
                    if swap:
                        j = i + 3 if i < 3 else i - 3
                    if j < 3:
                        j = pm[j]
                    else:
                        j = 3 + pp[j - 3]
                    m |= 1 << j
                out.add(m)
                out.add((1 << 6) - 1 - m)
    return sorted(out)


def _orbit_composition(mask: int) -> tuple:
    m_count = len(common.subset_bits(mask & 0b111))
    p_count = len(common.subset_bits(mask >> 3))
    return tuple(sorted((m_count, p_count), reverse=True))


def _internal_orbit_reps():
    seen = set()
    out = []
    for mask in common.internal_subset_bits(6):
        if mask in seen:
            continue
        orbit = _pair_orbit_members(mask)
        for m in orbit:
            seen.add(m)
        comp = _orbit_composition(orbit[0])
        if comp not in TARGET_COMP:
            continue
        out.append((comp, orbit[0], orbit))
    return sorted(out)


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


def _q_expr(omega_sym: Sequence[sp.Expr], mask: int) -> sp.Expr:
    q = sp.Integer(0)
    for i in range(6):
        if (mask >> i) & 1:
            q += common.SIG_FULL[i] * omega_sym[i] * omega_sym[i]
    return sp.expand(q)


def _h_expr(omega_sym: Sequence[sp.Expr], mask: int, q_sign: int) -> sp.Expr:
    wsum = sp.Integer(0)
    for i in common.subset_bits(mask):
        wsum += omega_sym[i]
    q = _q_expr(omega_sym, mask)
    return sp.expand(wsum * wsum - q_sign * q)


def _to_float_ratio(dct: Dict[str, Fraction], key: str) -> float:
    val = dct[key]
    return abs(float(val))


def _omega_from_family_and_t(family: Sequence[tuple], t: Fraction) -> List[Fraction]:
    free = [c + d * t for c, d in family]
    return list(common.solve_from_free(free, common.SIG_FULL))


def _h_and_q(omega: Sequence[Fraction], mask: int):
    wsum = Fraction(0)
    for i in common.subset_bits(mask):
        wsum += omega[i]
    q = common.q_T_for_mask(omega, mask, common.SIG_FULL)
    h = wsum * wsum - (Fraction(1) if q > 0 else Fraction(-1)) * q
    return h, q


def _validate_candidate(omega: Sequence[Fraction], target_orbit: set, wall_catalog) -> Tuple[bool, str]:
    free = [omega[1], omega[2], omega[3], omega[4]]
    if sum(free) == 0:
        return False, "free_sum_zero"
    if any(w == 0 for w in omega):
        return False, "zero_omega"

    wall_args = [w * w for w in omega]
    for wall in wall_catalog:
        if common.wall_value(wall_args, wall) == 0:
            return False, f"wall_zero:{wall['id']}"

    for mask in common.internal_subset_bits(6):
        if mask in target_orbit:
            continue
        h, _ = common.h_T(omega, mask, common.SIG_FULL)
        if h == 0:
            return False, f"other_triple_h_zero:{mask}"

    return True, "ok"


def _root_candidates(family: Sequence[tuple], target_mask: int, q_sign: int):
    omega_sym = _symbolic_omegas_from_family(family)
    h_expr = _h_expr(omega_sym, target_mask, q_sign)
    num = sp.together(h_expr).as_numer_denom()[0]
    num = sp.expand(num)

    poly = sp.Poly(num, T)
    if poly.total_degree() < 1:
        return []

    roots = sp.nroots(poly.as_expr(), n=80, maxsteps=120)
    out = []
    for root in roots:
        if abs(complex(root).imag) > 1e-16:
            continue
        t0 = _to_fraction14(float(complex(root).real))
        try:
            omega = _omega_from_family_and_t(family, t0)
        except Exception:
            continue
        h_v, q_v = _h_and_q(omega, target_mask)
        if abs(float(h_v)) > 1e-8:
            continue
        if q_sign > 0 and q_v <= 0:
            continue
        if q_sign < 0 and q_v >= 0:
            continue

        out.append((t0, h_v, q_v, omega))
    return out


def _other_min_h(omega: Sequence[Fraction], target_orbit: set) -> Fraction:
    vals = []
    for mask in common.internal_subset_bits(6):
        if mask in target_orbit:
            continue
        h, _ = common.h_T(omega, mask, common.SIG_FULL)
        vals.append(abs(h))
    return min(vals) if vals else Fraction(0)


def _wall_min_info(omega: Sequence[Fraction], wall_catalog):
    a = [w * w for w in omega]
    best_abs = None
    best_id = ""
    for wall in wall_catalog:
        v = common.wall_value(a, wall)
        abs_v = abs(v)
        if best_abs is None or abs_v < best_abs:
            best_abs = abs_v
            best_id = str(wall["id"])
    return best_abs, best_id


def _evaluate_side(orbit_mask: int, family, t_center: Fraction, sign: int, wall_catalog, target_orbit: Sequence[int]):
    samples = []
    target_set = set(target_orbit)
    for d in DECADES:
        t = t_center + sign * Fraction(1, 10**d)
        try:
            omega = _omega_from_family_and_t(family, t)
        except Exception:
            continue

        free = [omega[1], omega[2], omega[3], omega[4]]
        if sum(free) == 0 or any(w == 0 for w in omega):
            continue

        h_v, q_v = _h_and_q(omega, orbit_mask)
        if q_v == 0:
            continue

        ok, reason = _validate_candidate(omega, target_set, wall_catalog)
        if not ok:
            if reason.startswith("other_triple_h_zero"):
                continue
            if reason.startswith("wall_zero"):
                continue
            if reason.startswith("free_sum_zero") or reason.startswith("zero_omega"):
                continue
            continue

        try:
            row = exact_oracle.evaluate_omega(omega, "pole-side", wall_catalog)
        except Exception:
            continue

        other_min = _other_min_h(omega, target_set)
        wall_min, wall_min_id = _wall_min_info(omega, wall_catalog)
        a_h = row.A_im * h_v
        a_h2 = a_h * h_v

        samples.append(
            {
                "side": sign,
                "decade": d,
                "delta": common.frac_to_str(Fraction(1, 10**d)),
                "t": common.frac_to_str(t),
                "A_im": common.frac_to_str(row.A_im),
                "h": common.frac_to_str(h_v),
                "q": common.frac_to_str(q_v),
                "A_h": common.frac_to_str(a_h),
                "A_h2": common.frac_to_str(a_h2),
                "other_min_h": common.frac_to_str(other_min),
                "wall_min": common.frac_to_str(wall_min),
                "wall_min_id": wall_min_id,
                "wall_signature": row.wall_signature,
                "wall_signature_swap": row.wall_signature_swap,
                "free_w": [common.frac_to_str(x) for x in free],
                "omega": [common.frac_to_str(x) for x in omega],
                "float": {
                    "A_abs": abs(float(row.A_im)),
                    "h_abs": abs(float(h_v)),
                    "q_abs": abs(float(q_v)),
                    "A_h_abs": abs(float(a_h)),
                    "A_h2_abs": abs(float(a_h2)),
                },
            }
        )

    return samples


def _ratio_check(values: List[float], lo=0.03, hi=0.3) -> bool:
    if len(values) < 3:
        return False
    values = [abs(v) for v in values if abs(v) > 0]
    if len(values) < 3:
        return False
    final = values[-3:]
    r1 = final[1] / final[0]
    r2 = final[2] / final[1]
    return lo <= r1 <= hi and lo <= r2 <= hi


def _q_bounded_ok(values: List[float]) -> bool:
    values = [abs(v) for v in values]
    if len(values) < 3:
        return False
    final = values[-3:]
    if min(final) <= 1e-8:
        return False
    return max(final) / min(final) < 2.0


def _parse_other_min_h(row: dict) -> float:
    try:
        return abs(float(common.parse_fraction(row["other_min_h"])))
    except Exception:
        return 0.0


def _classify(records: List[dict]) -> Dict[str, object]:
    by_side: Dict[int, List[dict]] = {-1: [], 1: []}
    for rec in records:
        by_side[rec["side"]].append(rec)

    info = {
        "h_ratio_ok": True,
        "q_bounded_ok": True,
        "other_min_h_ok": True,
        "classification": "unresolved",
        "sample_count": len(records),
    }

    other_rows = []
    for side in (-1, 1):
        rows = sorted(by_side[side], key=lambda x: x["decade"])
        if len(rows) == 0:
            info["h_ratio_ok"] = False
            info["q_bounded_ok"] = False
            info["other_min_h_ok"] = False
            return info
        if len(rows) < 3:
            info["h_ratio_ok"] = False
            info["q_bounded_ok"] = False
            info["other_min_h_ok"] = False
            return info

        other_rows.extend([_parse_other_min_h(r) for r in rows])

        if not _ratio_check([r["float"]["h_abs"] for r in rows]):
            info["h_ratio_ok"] = False
        if not _q_bounded_ok([r["float"]["q_abs"] for r in rows]):
            info["q_bounded_ok"] = False

    if other_rows:
        info["other_min_h_ok"] = min(other_rows) > 1e-8
    else:
        info["other_min_h_ok"] = False

    if not (info["h_ratio_ok"] and info["q_bounded_ok"] and info["other_min_h_ok"]):
        return info
    if info["sample_count"] != 12:
        return info

    side_simple_ok = []
    side_bounded_ok = []
    for side in (-1, 1):
        rows = sorted(by_side[side], key=lambda x: x["decade"])
        a_vals = [r["float"]["A_abs"] for r in rows if r["float"]["A_abs"] > 0]
        ah_vals = [r["float"]["A_h_abs"] for r in rows if r["float"]["A_h_abs"] > 0]

        if len(a_vals) < 3 or len(ah_vals) < 3:
            side_simple_ok.append(False)
            side_bounded_ok.append(False)
            continue

        a_tail = a_vals[-3:]
        ah_tail = ah_vals[-3:]
        ratio1 = a_tail[1] / a_tail[0]
        ratio2 = a_tail[2] / a_tail[1]
        simple_ok = 5 <= ratio1 <= 20 and 5 <= ratio2 <= 20 and min(ah_tail) > 0 and max(ah_tail) / min(ah_tail) < 2
        bounded_ok = max(a_tail) / min(a_tail) < 2 or a_tail[-1] <= 1e-12

        side_simple_ok.append(simple_ok)
        side_bounded_ok.append(bounded_ok)

    if all(side_simple_ok):
        info["classification"] = "simple"
    elif all(side_bounded_ok):
        info["classification"] = "bounded_or_removable"
    else:
        info["classification"] = "unresolved"

    return info


def _write_report(entries: List[dict]):
    lines = []
    for entry in entries:
        if not entry["found"]:
            lines.append(
                f"{entry['comp']} status={entry['status']} reason={entry['scan_status']} found={entry['found']}"
            )
            continue
        checks = entry.get("checks", {})
        lines.append(
            f"{entry['comp']} family={entry.get('family')} sign={entry.get('q_sign')} "
            f"samples={len(entry.get('samples', []))} class={checks.get('classification')} "
            f"h_ratio_ok={checks.get('h_ratio_ok')} q_bounded_ok={checks.get('q_bounded_ok')} "
            f"other_min_h_ok={checks.get('other_min_h_ok')}"
        )
    (DATA_DIR / "pole_report.txt").write_text("\n".join(lines) + "\n")


def main():
    wall_catalog = common.build_wall_catalog()
    entries = []

    for comp, rep, orbit in _internal_orbit_reps():
        comp_meta = TARGET_COMP[comp]
        entry = {
            "orbit": str(rep),
            "comp": str(comp),
            "orbit_masks": orbit,
            "status": comp_meta["status"],
            "scan_status": comp_meta.get("reason", ""),
            "found": False,
            "samples": [],
            "checks": {
                "classification": "not_located",
            },
        }

        if comp_meta["status"] != "scan":
            entries.append(entry)
            continue

        accepted = False
        for fi, family in enumerate(FAMILIES):
            for q_sign in (1, -1):
                candidates = _root_candidates(family, rep, q_sign)
                if not candidates:
                    continue

                for t_root, h_root, q_root, omega_root in candidates:
                    free_root = [omega_root[1], omega_root[2], omega_root[3], omega_root[4]]
                    sample_rows = []
                    sample_rows.extend(_evaluate_side(rep, family, t_root, -1, wall_catalog, orbit))
                    sample_rows.extend(_evaluate_side(rep, family, t_root, 1, wall_catalog, orbit))

                    checks = _classify(sample_rows)
                    if not (
                        checks.get("sample_count", 0) == 12
                        and checks.get("h_ratio_ok", False)
                        and checks.get("q_bounded_ok", False)
                        and checks.get("other_min_h_ok", False)
                    ):
                        continue

                    entry.update(
                        {
                            "found": True,
                            "family": fi,
                            "q_sign": q_sign,
                            "t_root": common.frac_to_str(t_root),
                            "omega_root": [common.frac_to_str(x) for x in omega_root],
                            "free_root": [common.frac_to_str(x) for x in free_root],
                            "q_root": common.frac_to_str(q_root),
                            "h_root": common.frac_to_str(h_root),
                            "samples": sample_rows,
                            "checks": checks,
                            "scan_status": "isolated_root_found",
                        }
                    )
                    accepted = True
                    break
                if accepted:
                    break
            if accepted:
                break

        entries.append(entry)

    (DATA_DIR / "pole_approaches.json").write_text(json.dumps(entries, indent=2))
    _write_report(entries)


if __name__ == "__main__":
    main()
