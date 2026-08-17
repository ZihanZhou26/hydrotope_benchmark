#!/usr/bin/env python3
"""Wall-power ansatz fitting with exact QQ consistency checks."""

import json
import time
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import permutations, product
from pathlib import Path
from typing import Callable, Dict, List, Sequence, Tuple

import common
from common import frac_to_str
import exact_oracle

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
WALL_CATALOG = common.build_wall_catalog()

WALL_ENTRIES = []
for _wall in WALL_CATALOG:
    if _wall["kind"] not in ("diff", "sum"):
        continue
    if _wall["kind"] == "diff":
        i_list = common.subset_bits(int(_wall["I_mask"]))
        j_list = common.subset_bits(int(_wall["J_mask"]))
        if len(i_list) != 1 or len(j_list) != 1:
            raise RuntimeError("unexpected wall mask shape")
        WALL_ENTRIES.append(("D", i_list[0], j_list[0]))
    else:
        i_list = common.subset_bits(int(_wall["I_mask"]))
        if len(i_list) != 1:
            raise RuntimeError("unexpected wall mask shape")
        WALL_ENTRIES.append(("S", i_list[0], int(_wall["plus_anchor"])))

PERMS_3 = list(permutations(range(3)))
GROUP_ACTIONS = []
for perm_m in PERMS_3:
    for perm_p in PERMS_3:
        for do_swap in (False, True):
            GROUP_ACTIONS.append((perm_m, perm_p, do_swap))


def _frac_to_dict(v) -> Fraction:
    if isinstance(v, Fraction):
        return v
    return common.parse_fraction(v)


def _wall_value(kind: str, i: int, j: int, omega: Sequence[Fraction]) -> Fraction:
    if kind == "D":
        return omega[i] * omega[i] - omega[3 + j] * omega[3 + j]
    if kind == "S":
        t = omega[0] * omega[0] + omega[1] * omega[1] + omega[2] * omega[2]
        return omega[i] * omega[i] + omega[3 + j] * omega[3 + j] - t
    raise ValueError("unknown wall kind")


def _transform_idx(idx: int, perm_m: Tuple[int, int, int], perm_p: Tuple[int, int, int], do_swap: bool) -> int:
    if not do_swap:
        if idx < 3:
            return perm_m[idx]
        return 3 + perm_p[idx - 3]

    if idx < 3:
        return 3 + perm_m[idx]
    return perm_p[idx - 3]


def _transform_wall(kind: str, i: int, j: int, perm_m: Tuple[int, int, int], perm_p: Tuple[int, int, int], do_swap: bool) -> Tuple[str, int, int, int]:
    if not do_swap:
        return kind, perm_m[i], perm_p[j], 1
    sign_factor = -1 if kind == "D" else 1
    return kind, perm_p[j], perm_m[i], sign_factor


def _transform_omega(omega: Sequence[Fraction], perm_m: Tuple[int, int, int], perm_p: Tuple[int, int, int], do_swap: bool) -> Tuple[Fraction, ...]:
    if not do_swap:
        return (
            omega[perm_m[0]],
            omega[perm_m[1]],
            omega[perm_m[2]],
            omega[3 + perm_p[0]],
            omega[3 + perm_p[1]],
            omega[3 + perm_p[2]],
        )
    return (
        omega[3 + perm_p[0]],
        omega[3 + perm_p[1]],
        omega[3 + perm_p[2]],
        omega[perm_m[0]],
        omega[perm_m[1]],
        omega[perm_m[2]],
    )


def _transform_exp(exp: Tuple[int, ...], perm_m: Tuple[int, int, int], perm_p: Tuple[int, int, int], do_swap: bool) -> Tuple[int, ...]:
    out = [0] * 6
    for i, e in enumerate(exp):
        ni = _transform_idx(i, perm_m, perm_p, do_swap)
        out[ni] = e
    return tuple(out)


def _positive_power(x: Fraction, r: int) -> Fraction:
    return x ** r if x > 0 else Fraction(0, 1)


def _eval_monomial_exp(exp: Tuple[int, ...], omega: Sequence[Fraction]) -> Fraction:
    total = Fraction(1, 1)
    for i, pwr in enumerate(exp):
        if pwr:
            total *= omega[i] ** pwr
    return total


def _eval_wallpower_feature(feature: Dict[str, object], omega: Sequence[Fraction]) -> Fraction:
    r = int(feature["r"])
    total = Fraction(0, 1)
    for term in feature["terms"]:
        kind, i, j, eps, exp = term
        q = _wall_value(kind, i, j, omega)
        total += _positive_power(eps * q, r) * _eval_monomial_exp(exp, omega)
    return total


def _eval_p8_feature(feature: Dict[str, object], omega: Sequence[Fraction]) -> Fraction:
    total = Fraction(0, 1)
    for exp in feature["terms"]:
        total += _eval_monomial_exp(exp, omega)
    return total


def _eval_feature(feature: Dict[str, object], omega: Sequence[Fraction]) -> Fraction:
    if feature["family"].startswith("H"):
        return _eval_wallpower_feature(feature, omega)
    return _eval_p8_feature(feature, omega)


def _eval_elementary_feature(feature: Dict[str, object], inv: Dict[str, Fraction]) -> Fraction:
    s = inv["s"]
    p = inv["p"]
    r = inv["r"]
    t = inv["t"]

    if feature["family"] == "E17":
        return (s ** feature["a"]) * (p ** feature["b"]) * (r ** feature["c"]) * (t ** feature["d"])

    if feature["family"] == "E12":
        base = Fraction(0, 1)
        for coeff, c, d in feature["sym_terms"]:
            base += coeff * (r ** c) * (t ** d)
        return (s ** feature["a"]) * (p ** feature["b"]) * base

    if feature["family"].startswith("R"):
        base = Fraction(0, 1)
        for coeff, rc, tc in feature["rt_terms"]:
            base += coeff * (r ** rc) * (t ** tc)
        return (s ** feature["a"]) * (p ** feature["b"]) * base

    raise ValueError("unexpected elementary family")


def _eval_feature_for_row(feature: Dict[str, object], row: Dict[str, object]) -> Fraction:
    if feature["family"].startswith("H"):
        return _eval_feature(feature, row["omega"])
    if feature["family"].startswith("P"):
        return _eval_p8_feature(feature, row["omega"])
    if feature["family"].startswith("E") or feature["family"].startswith("R"):
        return _eval_elementary_feature(feature, row["_elementary_invariants"])
    return _eval_feature(feature, row["omega"])


def _is_generic_kinematic(omega: Sequence[Fraction]) -> bool:
    if any(w == 0 for w in omega):
        return False

    a2 = [w * w for w in omega]
    for wall in WALL_CATALOG:
        if common.wall_value(a2, wall) == 0:
            return False

    for mask in common.internal_subset_bits(6):
        bits = mask.bit_count() if hasattr(int, "bit_count") else bin(mask).count("1")
        if bits not in (2, 3):
            continue
        h, _ = common.h_T(omega, mask, common.SIG_FULL)
        if h == 0:
            return False
    return True


def _pairwise_sum_two(v: Sequence[Fraction]) -> Fraction:
    return v[0] * v[1] + v[0] * v[2] + v[1] * v[2]


def _elementary_invariants(omega: Sequence[Fraction]) -> Dict[str, Fraction]:
    u = tuple(-w for w in omega[:3])
    v = omega[3:]
    s_u = sum(u)
    s_v = sum(v)
    p_u = _pairwise_sum_two(u)
    p_v = _pairwise_sum_two(v)
    r = u[0] * u[1] * u[2]
    t = v[0] * v[1] * v[2]
    return {
        "s_u": s_u,
        "s_v": s_v,
        "p_u": p_u,
        "p_v": p_v,
        "r": r,
        "t": t,
        "s": s_u if s_u == s_v else s_u,
        "p": p_u if p_u == p_v else p_u,
    }


def _attach_elementary_invariants(rows: List[Dict[str, object]]) -> None:
    for row in rows:
        row["_elementary_invariants"] = _elementary_invariants(row["omega"])


def _elementary_signature_checks(rows: List[Dict[str, object]]) -> Dict[str, object]:
    s_ok = 0
    p_ok = 0
    bad_samples = []
    for row in rows:
        inv = row["_elementary_invariants"]
        if inv["s_u"] == inv["s_v"]:
            s_ok += 1
        if inv["p_u"] == inv["p_v"]:
            p_ok += 1
        if inv["s_u"] != inv["s_v"] or inv["p_u"] != inv["p_v"]:
            bad_samples.append(row["sample_id"])
    return {
        "samples_checked": len(rows),
        "s_eq_count": s_ok,
        "p_eq_count": p_ok,
        "s_and_p_ok": s_ok == len(rows) and p_ok == len(rows),
        "bad_samples": bad_samples,
    }


def _pairwise_to_cube_identity_checks(rows: List[Dict[str, object]]) -> Dict[str, object]:
    exact_count = 0
    bad_samples = []
    for row in rows:
        omega = row["omega"]
        lhs = Fraction(1, 1)
        for i in range(3):
            for j in range(3):
                lhs *= omega[i] + omega[3 + j]

        inv = row["_elementary_invariants"]
        rhs = -(inv["r"] - inv["t"]) ** 3
        if lhs == rhs:
            exact_count += 1
        else:
            bad_samples.append(row["sample_id"])

    return {
        "samples_checked": len(rows),
        "exact_count": exact_count,
        "fail_count": len(rows) - exact_count,
        "status": "ok" if exact_count == len(rows) else "failed",
        "bad_samples": bad_samples,
    }


def _merged_word_sq(omega: Sequence[Fraction]) -> str:
    idx = sorted(range(6), key=lambda i: (omega[i] * omega[i], omega[i], i))
    return "".join("M" if i < 3 else "P" for i in idx)


def _signature_key_from_signs(sign_map: Dict[str, int], wall_catalog=WALL_CATALOG) -> str:
    return common.serialize_signs(sign_map, wall_catalog)


def _composition_tuples(total: int, parts: int, prefix: List[int], out: List[Tuple[int, ...]]) -> None:
    if len(prefix) == parts - 1:
        rem = total - sum(prefix)
        if rem >= 0:
            out.append(tuple(prefix + [rem]))
        return
    start = 0
    for v in range(total - sum(prefix) + 1):
        prefix.append(v)
        _composition_tuples(total, parts, prefix, out)
        prefix.pop()


def _generate_exponent_vectors(total_degree: int, vars_count: int = 6) -> List[Tuple[int, ...]]:
    out: List[Tuple[int, ...]] = []
    _composition_tuples(total_degree, vars_count, [], out)
    return out


def _coerce_rows_to_fractions(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for row in rows:
        row["A_im"] = _frac_to_dict(row["A_im"])
        row["A_re"] = _frac_to_dict(row["A_re"])
        row["omega"] = [_frac_to_dict(x) for x in row["omega"]]
        row["_elementary_invariants"] = _elementary_invariants(row["omega"])
        out.append(row)
    return out


def _fraction_grid(max_abs: int, max_den: int) -> List[Fraction]:
    vals = []
    for d in range(1, max_den + 1):
        for n in range(1, max_abs + 1):
            vals.append(Fraction(-n, d))
            vals.append(Fraction(n, d))
    return vals


def _grid_stages() -> List[Tuple[int, int]]:
    return [
        (4, 1),
        (4, 2),
        (6, 2),
        (6, 3),
        (8, 3),
        (8, 4),
        (10, 4),
        (10, 5),
        (12, 6),
        (12, 7),
        (12, 8),
    ]


def _wall_power_terms(
    kind: str,
    i: int,
    j: int,
    eps: int,
    exp: Tuple[int, ...],
) -> List[Tuple[str, int, int, int, Tuple[int, ...]]]:
    seen = set()
    for perm_m, perm_p, do_swap in GROUP_ACTIONS:
        t_kind, ti, tj, t_sign = _transform_wall(kind, i, j, perm_m, perm_p, do_swap)
        t_exp = _transform_exp(exp, perm_m, perm_p, do_swap)
        t_eps = eps * t_sign
        seen.add((t_kind, ti, tj, t_eps, t_exp))

    out = []
    for term in sorted(seen):
        out.append(term)
    return out


def _wall_term_id(term: Tuple[str, int, int, int, Tuple[int, ...]]) -> str:
    kind, i, j, eps, exp = term
    return "%s|%s:%s|eps=%s|%s" % (
        kind,
        i,
        j,
        eps,
        ",".join(str(v) for v in exp),
    )


def _build_h_features(r: int, kind_filter: str = None) -> Tuple[List[Dict[str, object]], int]:
    exp_total = 8 - 2 * r
    exps = _generate_exponent_vectors(exp_total)
    raw_count = 0
    features: List[Dict[str, object]] = []
    seen: Dict[str, bool] = {}
    for kind, wi, wj in WALL_ENTRIES:
        if kind_filter and kind != kind_filter:
            continue
        for _eps in (-1, 1):
            raw_count += len(exps)
            for exp in exps:
                terms = _wall_power_terms(kind, wi, wj, _eps, exp)
                rep_key = "|".join(_wall_term_id(t) for t in terms)
                if rep_key in seen:
                    continue
                seen[rep_key] = True
                features.append(
                    {
                        "family": f"H{r}",
                        "r": r,
                        "kind": kind,
                        "wall": [wi, wj],
                        "epsilon": _eps,
                        "exponent": list(exp),
                        "orbit_representative_key": rep_key,
                        "id": f"H{r}|eps={_eps}|wall={wi},{wj}|exp={exp}|rep={rep_key}",
                        "terms": terms,
                        "expanded_term_count": len(terms),
                    }
                )
    return features, raw_count


def _p8_term_id(exp: Tuple[int, ...]) -> str:
    return ",".join(str(x) for x in exp)


def _build_p8_features(total_degree: int = 8) -> List[Dict[str, object]]:
    raw = _generate_exponent_vectors(total_degree)
    seen = {}
    features = []

    for exp in raw:
        orbit = set()
        for perm_m, perm_p, do_swap in GROUP_ACTIONS:
            orbit.add(_transform_exp(exp, perm_m, perm_p, do_swap))
        rep = min(orbit)
        if rep in seen:
            continue
        seen[rep] = True
        rep_key = ";".join(_p8_term_id(t) for t in sorted(orbit))
        features.append(
            {
                "family": "P8",
                "degree": total_degree,
                "orbit_representative_key": rep_key,
                "id": f"P8|rep={rep_key}",
                "terms": sorted(orbit),
                "expanded_term_count": len(orbit),
                "monomial_representative": rep,
            }
        )

    return features


def _build_elementary_features() -> Tuple[List[Dict[str, object]], List[Dict[str, object]], List[Tuple[int, int, int, int]]]:
    raw: List[Tuple[int, int, int, int]] = []
    for a in range(9):
        for b in range(9):
            for c in range(3):
                for d in range(3):
                    if a + 2 * b + 3 * c + 3 * d == 8:
                        raw.append((a, b, c, d))

    raw_features = [
        {
            "family": "E17",
            "weighted_degree": 8,
            "a": a,
            "b": b,
            "c": c,
            "d": d,
            "id": f"E17|a={a}|b={b}|c={c}|d={d}",
            "expanded_term_count": 1,
        }
        for a, b, c, d in raw
    ]

    orbits: Dict[Tuple[int, int, int, int], List[Tuple[int, int, int, int]]] = defaultdict(list)
    for a, b, c, d in raw:
        key = (a, b, min(c, d), max(c, d))
        orbits[key].append((a, b, c, d))

    sym_features = []
    for idx, ((a, b, c_low, c_high), reps) in enumerate(sorted(orbits.items())):
        sym_expr = [(Fraction(1, 1), reps[0][2], reps[0][3])]
        if c_low != c_high:
            sym_expr.append((Fraction(1, 1), reps[1][2], reps[1][3]))

        sym_features.append(
            {
                "family": "E12",
                "weighted_degree": 8,
                "a": a,
                "b": b,
                "sym_terms": sorted(sym_expr),
                "id": f"E12|a={a}|b={b}|orbit={c_low},{c_high}|idx={idx}",
                "expanded_term_count": len(sym_expr),
            }
        )

    return raw_features, raw, sym_features


def _build_ratio_features(d: int) -> Tuple[List[Dict[str, object]], int]:
    if d not in (1, 2, 3):
        raise ValueError("ratio exponent d must be 1, 2, or 3")

    degree = 8 + 3 * d
    raw: List[Tuple[int, int, int, int]] = []
    for a in range(degree + 1):
        for b in range(degree // 2 + 1):
            for c in range(degree // 3 + 1):
                for e in range(degree // 3 + 1):
                    if a + 2 * b + 3 * c + 3 * e == degree:
                        raw.append((a, b, c, e))
    raw_count = len(raw)

    parity = "even" if (d % 2 == 0) else "odd"
    second_coeff = Fraction(1, 1) if parity == "even" else Fraction(-1, 1)

    orbits: Dict[Tuple[int, int, int, int], List[Tuple[int, int, int, int]]] = defaultdict(list)
    for a, b, c, e in raw:
        if parity == "odd" and c == e:
            continue
        key = (a, b, min(c, e), max(c, e))
        orbits[key].append((a, b, c, e))

    features: List[Dict[str, object]] = []
    for idx, ((a, b, c_low, c_high), reps) in enumerate(sorted(orbits.items())):
        rt_expr: List[Tuple[Fraction, int, int]] = [(Fraction(1, 1), c_low, c_high)]
        if c_low != c_high:
            rt_expr.append((second_coeff, c_high, c_low))

        features.append(
            {
                "family": f"R{d}",
                "ratio_power": d,
                "weighted_degree": degree,
                "a": a,
                "b": b,
                "rt_terms": sorted(rt_expr),
                "id": f"R{d}|a={a}|b={b}|rt={c_low},{c_high}|idx={idx}",
                "expanded_term_count": len(rt_expr),
                "parity": parity,
            }
        )

    return features, raw_count


def _matrix_rank(matrix: List[List[Fraction]]) -> int:
    if not matrix:
        return 0
    a = [list(row) for row in matrix]
    m = len(a)
    n = len(a[0])
    row = 0
    col = 0
    rank = 0
    while row < m and col < n:
        pivot = row
        while pivot < m and a[pivot][col] == 0:
            pivot += 1
        if pivot == m:
            col += 1
            continue

        a[row], a[pivot] = a[pivot], a[row]
        pv = a[row][col]
        a[row] = [x / pv for x in a[row]]

        for rr in range(m):
            if rr == row:
                continue
            factor = a[rr][col]
            if factor == 0:
                continue
            a[rr] = [x - factor * y for x, y in zip(a[rr], a[row])]
        row += 1
        col += 1
        rank += 1
    return rank


def _matrix_rank_mod(matrix: List[List[Fraction]], mod: int) -> int:
    if mod <= 2:
        raise ValueError("modulus must be greater than 2")
    if not matrix:
        return 0
    m = len(matrix)
    n = len(matrix[0])
    a: List[List[int]] = []
    for row in matrix:
        out = []
        for x in row:
            den = x.denominator % mod
            if den == 0:
                raise ZeroDivisionError("denominator divisible by modulus")
            num = x.numerator % mod
            out.append((num * pow(den, -1, mod)) % mod)
        a.append(out)

    row = 0
    col = 0
    rank = 0
    while row < m and col < n:
        pivot = row
        while pivot < m and a[pivot][col] % mod == 0:
            pivot += 1
        if pivot == m:
            col += 1
            continue

        a[row], a[pivot] = a[pivot], a[row]
        inv = pow(a[row][col], -1, mod)
        a[row] = [(x * inv) % mod for x in a[row]]

        for rr in range(m):
            if rr == row:
                continue
            factor = a[rr][col]
            if factor == 0:
                continue
            a[rr] = [(x - factor * y) % mod for x, y in zip(a[rr], a[row])]

        row += 1
        col += 1
        rank += 1
    return rank


def _modular_rank_guard(train_X: List[List[Fraction]], train_y: List[Fraction], mod: int = 1_000_000_007) -> Dict[str, object]:
    out: Dict[str, object] = {"modulus": mod}
    try:
        a_rank = _matrix_rank_mod(train_X, mod)
        aug = [row[:] + [y] for row, y in zip(train_X, train_y)]
        aug_rank = _matrix_rank_mod(aug, mod)
    except ZeroDivisionError as err:
        out["status"] = "skipped_denominator_not_invertible"
        out["reason"] = str(err)
        return out

    out["status"] = "ok"
    out["rank"] = a_rank
    out["aug_rank"] = aug_rank
    out["suggest_inconsistency"] = aug_rank > a_rank
    return out


def _find_first_inconsistent_prefix(X: List[List[Fraction]], y: List[Fraction], meta: List[Dict[str, object]]) -> Dict[str, object]:
    for k in range(1, len(X) + 1):
        a = [row[:] for row in X[:k]]
        b = y[:k]
        m = len(a)
        n = len(a[0]) if a else 0

        aug = [a[i] + [b[i]] for i in range(m)]
        row = 0
        col = 0
        while row < m and col < n:
            pivot = row
            while pivot < m and aug[pivot][col] == 0:
                pivot += 1
            if pivot == m:
                col += 1
                continue

            aug[row], aug[pivot] = aug[pivot], aug[row]
            pv = aug[row][col]
            aug[row] = [x / pv for x in aug[row]]

            for rr in range(m):
                if rr == row:
                    continue
                factor = aug[rr][col]
                if factor == 0:
                    continue
                aug[rr] = [x - factor * y for x, y in zip(aug[rr], aug[row])]
            row += 1
            col += 1

        inconsistent = False
        for rr in range(m):
            if all(v == 0 for v in aug[rr][:-1]) and aug[rr][-1] != 0:
                inconsistent = True
                break

        if inconsistent:
            bad = meta[k - 1]
            return {
                "prefix_rows": k,
                "conflict_row": {
                    "sample_id": bad.get("sample_id"),
                    "split": bad.get("split"),
                    "wall_key": bad.get("wall_key"),
                    "A_im": frac_to_str(bad.get("A_im", 0)),
                },
                "rankA": _matrix_rank([row[:] for row in X[:k]]),
                "rankAug": _matrix_rank([row[:] + [b[i]] for i, row in enumerate(X[:k])]),
            }
    return None


def _solve_linear_exact(A: List[List[Fraction]], b: List[Fraction]):
    if not A:
        return None, {"status": "empty", "matrix_rank": 0, "matrix_rank_aug": 0}

    m = len(A)
    n = len(A[0])
    aug = [list(row) + [b[i]] for i, row in enumerate(A)]
    row = 0
    pivots = [-1] * n

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
    for col, rr in enumerate(pivots):
        if rr != -1:
            coeffs[col] = aug[rr][-1]
    return coeffs, {"status": "ok", "matrix_rank": row, "matrix_rank_aug": row, "num_free": n - row}


def _residual_summary(vals: List[Fraction]) -> Dict[str, object]:
    if not vals:
        return {"count": 0, "max_abs": "0", "mean_abs": "0"}
    mags = [abs(v) for v in vals]
    return {
        "count": len(vals),
        "max_abs": frac_to_str(max(mags)),
        "mean_abs": frac_to_str(sum(mags, Fraction(0)) / len(mags)),
    }


def _eval_residual(coeffs: List[Fraction], features: List[Dict[str, object]], omega: Sequence[Fraction], target: Fraction) -> Fraction:
    pred = Fraction(0)
    for c, f in zip(coeffs, features):
        pred += c * _eval_feature(f, omega)
    return target - pred


def _eval_residual_for_row(coeffs: List[Fraction], features: List[Dict[str, object]], row: Dict[str, object], target: Fraction) -> Fraction:
    pred = Fraction(0)
    for c, f in zip(coeffs, features):
        if f["family"].startswith("E") or f["family"].startswith("R"):
            pred += c * _eval_feature_for_row(f, row)
        else:
            pred += c * _eval_feature(f, row["omega"])
    return target - pred


def _build_design_matrix(
    features: List[Dict[str, object]],
    rows: List[Dict[str, object]],
) -> Tuple[List[List[Fraction]], List[Fraction], List[Dict[str, object]], List[Dict[str, object]], List[List[Fraction]]]:
    if not rows:
        return [], [], [], [], []

    columns: List[List[Fraction]] = []
    kept_features: List[Dict[str, object]] = []
    for feature in features:
        col = []
        for row in rows:
            if feature["family"].startswith("E") or feature["family"].startswith("R"):
                col.append(_eval_feature_for_row(feature, row))
            else:
                col.append(_eval_feature(feature, row["omega"]))
        if any(v != 0 for v in col):
            columns.append(col)
            kept_features.append(feature)

    if not columns:
        return [], [], [], [], []

    X = [[columns[c][r] for c in range(len(columns))] for r in range(len(rows))]
    y = [row["A_im"] for row in rows]
    meta = [{"sample_id": row["sample_id"], "split": row.get("split", "train"), "wall_key": row.get("wall_key")} for row in rows]
    return X, y, meta, kept_features, columns


def _feature_dictionary_report(features: List[Dict[str, object]], name: str) -> Dict[str, object]:
    return {
        "name": name,
        "count": len(features),
        "max_expanded_terms": max((f["expanded_term_count"] for f in features), default=0),
    }


def _fit(
    features: List[Dict[str, object]],
    rows: List[Dict[str, object]],
    fit_name: str,
    require_disjoint_holdout: bool = True,
    raw_feature_count: int = None,
    require_train_overhang: int = 20,
    modular_prefilter: bool = False,
    modular_modulus: int = 1_000_000_007,
) -> Dict[str, object]:
    rows_sorted = sorted(rows, key=lambda r: r["sample_id"])
    train_rows = [r for r in rows_sorted if r["split"] == "train"]
    hold_rows = [r for r in rows_sorted if r["split"] == "holdout"]

    out = {
        "name": fit_name,
        "requested_feature_count": len(features),
    }

    train_X, train_y, train_meta, kept_features, _ = _build_design_matrix(features, train_rows)
    out["kept_feature_count"] = len(kept_features)
    if raw_feature_count is not None:
        out["raw_feature_count"] = raw_feature_count
    if not kept_features or not train_rows:
        out["status"] = "failed"
        out["reason"] = "no nonzero features or no train rows"
        return out

    if len(kept_features) > max(0, len(train_rows) - require_train_overhang):
        out["status"] = "insufficient_train_rows"
        out["reason"] = f"kept_features={len(kept_features)} > train_rows-{require_train_overhang}"
        out["feature_family_counts"] = {
            "num_rows_train": len(train_rows),
            "num_rows_holdout": len(hold_rows),
        }
        return out

    if modular_prefilter:
        out["modular_prefilter"] = _modular_rank_guard(train_X, train_y, mod=modular_modulus)

    hold_X, hold_y, hold_meta, _, _ = _build_design_matrix(kept_features, hold_rows)

    rankA = _matrix_rank([row[:] for row in train_X])
    aug = [row[:] + [y] for row, y in zip(train_X, train_y)]
    rank_aug = _matrix_rank(aug)
    contradiction = _find_first_inconsistent_prefix(train_X, train_y, train_meta)

    coeffs, fit_meta = _solve_linear_exact(train_X, train_y)
    out["feature_family_counts"] = {
        "feature_count": len(kept_features),
        "num_rows_train": len(train_rows),
        "num_rows_holdout": len(hold_rows),
        "matrix_rank": rankA,
        "matrix_rank_aug": rank_aug,
        "first_inconsistent_prefix": contradiction,
    }
    out["fit_meta"] = fit_meta

    if coeffs is None:
        out["status"] = "inconsistent"
        return out

    train_res = [_eval_residual_for_row(coeffs, kept_features, row, target) for row, target in zip(train_rows, train_y)]
    out["train_residuals"] = _residual_summary(train_res)

    if hold_X:
        hold_res = [_eval_residual_for_row(coeffs, kept_features, row, target) for row, target in zip(hold_rows, hold_y)]
        out["holdout_residuals"] = _residual_summary(hold_res)
        out["holds_out_exact"] = all(v == 0 for v in hold_res)
    else:
        out["holdout_residuals"] = {"count": 0, "max_abs": "0", "mean_abs": "0"}
        out["holds_out_exact"] = True

    if require_disjoint_holdout and not out["holds_out_exact"]:
        out["status"] = "holdout_failed"
    else:
        out["status"] = "ok"

    if out["status"] == "ok":
        nz = [(f, c) for f, c in zip(kept_features, coeffs) if c != 0]
        out["nonzero_coefficients"] = [
            {
                "feature_id": f["id"],
                "coefficient": frac_to_str(c),
                "expanded_term_count": f["expanded_term_count"],
                "representative_key": f.get("orbit_representative_key", f.get("id")),
                "evaluator": f"{frac_to_str(c)} * Φ[{f['id']}]",
            }
            for f, c in nz
        ]
        out["nonzero_coefficient_count"] = len(nz)
        if nz:
            out["max_expanded_term_count"] = max(item["expanded_term_count"] for item in out["nonzero_coefficients"])
        else:
            out["max_expanded_term_count"] = 0

    return out


def _run_sanity_checks(features: List[Dict[str, object]], rows: List[Dict[str, object]], test_points: int = 3) -> Dict[str, object]:
    check_rows = [r for r in rows if r["split"] == "train"][:test_points]
    inv = []
    homo = []

    for row in check_rows:
        omega = row["omega"]
        scaled = [Fraction(2, 1) * x for x in omega]
        for f in features:
            if f["family"].startswith("E"):
                base = _eval_feature_for_row(f, row)
                scaled_row = {
                    "omega": scaled,
                    "split": row.get("split", "train"),
                    "_elementary_invariants": _elementary_invariants(scaled),
                }
                homo.append(base * (2 ** 8) == _eval_feature_for_row(f, scaled_row))
            else:
                base = _eval_feature(f, omega)
                homo.append(base * (2 ** 8) == _eval_feature(f, scaled))
            for perm_m, perm_p, do_swap in GROUP_ACTIONS:
                t_omega = _transform_omega(omega, perm_m, perm_p, do_swap)
                if f["family"].startswith("E"):
                    transformed = dict(row)
                    transformed["omega"] = t_omega
                    transformed["_elementary_invariants"] = _elementary_invariants(t_omega)
                    inv.append(_eval_feature_for_row(f, transformed) == base)
                else:
                    inv.append(_eval_feature(f, t_omega) == base)

    return {
        "tested_rows": len(check_rows),
        "invariance_passed": all(inv),
        "homogeneity_passed": all(homo),
        "invariance_failure_count": inv.count(False),
        "homogeneity_failure_count": homo.count(False),
    }


def _check_hinge_compatibility(rows: List[Dict[str, object]], h3_features: List[Dict[str, object]]) -> Dict[str, object]:
    out = {
        "wall_hinge_fit_json_available": False,
        "h3_count_match": False,
        "details": "",
    }
    path = DATA_DIR / "wall_hinge_fit.json"
    if not path.exists():
        out["details"] = "wall_hinge_fit.json missing"
        return out

    try:
        payload = json.loads(path.read_text())
        hinge_h3_count = payload["dictionary"]["H3"]["count"]
        out["wall_hinge_fit_json_available"] = True
        out["wall_hinge_count"] = hinge_h3_count
        out["h3_count_match"] = (len(h3_features) == hinge_h3_count)
        out["details"] = "h3 count match" if out["h3_count_match"] else "h3 count mismatch"
    except Exception as err:
        out["details"] = str(err)
    return out


def _check_fresh_rows_against_oracle(rows: List[Dict[str, object]], n: int = 5) -> Dict[str, object]:
    checks = []
    for row in rows[:n]:
        omega = row["omega"]
        sample_id = row["sample_id"]
        try:
            res = exact_oracle.evaluate_omega(omega, sample_id + "-recheck", WALL_CATALOG)
        except Exception as err:
            checks.append(
                {
                    "sample_id": sample_id,
                    "status": "eval_failed",
                    "error": str(err),
                }
            )
            continue
        checks.append(
            {
                "sample_id": sample_id,
                "status": "ok" if res.A_im == row["A_im"] else "mismatch",
                "stored": frac_to_str(row["A_im"]),
                "rechecked": frac_to_str(res.A_im),
                "delta": frac_to_str(res.A_im - row["A_im"]),
            }
        )
    return {"requested": n, "checks": checks, "all_match": all(c.get("status") == "ok" for c in checks)}


def _run_elementary_invariant_diagnostic(
    rows: List[Dict[str, object]],
    elem_features_17: List[Dict[str, object]],
    elem_features_12: List[Dict[str, object]],
) -> Dict[str, object]:
    equality = _elementary_signature_checks(rows)
    equality["status"] = "ok" if equality["s_and_p_ok"] else "failed"
    pairwise_identity = _pairwise_to_cube_identity_checks(rows)

    global_17 = _fit(elem_features_17, rows, "elementary_full_17")
    global_12 = _fit(elem_features_12, rows, "elementary_sym_12")
    feature_rank = global_17.get("feature_family_counts", {}).get("matrix_rank", len(elem_features_17))

    by_word: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_word[row["merged_word_omega_sq"]].append(row)

    per_word = {}
    for word, word_rows in sorted(by_word.items()):
        if len(word_rows) <= feature_rank:
            continue
        for r in word_rows:
            r["split"] = "train"
        diag = _fit(elem_features_17, word_rows, f"elementary_17_word_{word}", require_disjoint_holdout=False, require_train_overhang=0)
        per_word[word] = {
            "rows": len(word_rows),
            "status": diag.get("status"),
            "matrix_rank": diag.get("feature_family_counts", {}).get("matrix_rank"),
            "matrix_rank_aug": diag.get("feature_family_counts", {}).get("matrix_rank_aug"),
        }

    ratio_diagnostics: Dict[str, Dict[str, object]] = {}
    for d in (1, 2, 3):
        features, raw_feature_count = _build_ratio_features(d)
        eligible_rows = []
        denom_zero_rows = 0
        for row in rows:
            inv = row["_elementary_invariants"]
            denom = inv["r"] - inv["t"]
            if denom == 0:
                denom_zero_rows += 1
                continue
            scaled = dict(row)
            scaled["A_im"] = row["A_im"] * (denom ** d)
            eligible_rows.append(scaled)

        if eligible_rows:
            fit = _fit(
                features,
                eligible_rows,
                f"ratio_numerator_d{d}",
                raw_feature_count=raw_feature_count,
                require_train_overhang=0,
            )
        else:
            fit = {
                "name": f"ratio_numerator_d{d}",
                "status": "failed",
                "reason": "no nonzero (r-t) rows",
            }

        ratio_diagnostics[f"d_{d}"] = {
            "parity": "odd" if d % 2 else "even",
            "weighted_degree": 8 + 3 * d,
            "requested_feature_count": len(features),
            "raw_feature_count": raw_feature_count,
            "eligible_rows": len(eligible_rows),
            "zero_denominator_rows": denom_zero_rows,
            "status": fit.get("status"),
            "reason": fit.get("reason"),
            "matrix_rank": fit.get("feature_family_counts", {}).get("matrix_rank"),
            "matrix_rank_aug": fit.get("feature_family_counts", {}).get("matrix_rank_aug"),
            "holds_out_exact": fit.get("holds_out_exact", False),
        }

    return {
        "equalities": equality,
        "pairwise_identity": pairwise_identity,
        "global_full_17": {
            "status": global_17.get("status"),
            "matrix_rank": global_17.get("feature_family_counts", {}).get("matrix_rank"),
            "matrix_rank_aug": global_17.get("feature_family_counts", {}).get("matrix_rank_aug"),
            "train_rows": len([r for r in rows if r["split"] == "train"]),
            "holdout_rows": len([r for r in rows if r["split"] == "holdout"]),
            "requested_feature_count": len(elem_features_17),
            "kept_feature_count": global_17.get("kept_feature_count"),
        },
        "global_sym_12": {
            "status": global_12.get("status"),
            "matrix_rank": global_12.get("feature_family_counts", {}).get("matrix_rank"),
            "matrix_rank_aug": global_12.get("feature_family_counts", {}).get("matrix_rank_aug"),
            "train_rows": len([r for r in rows if r["split"] == "train"]),
            "holdout_rows": len([r for r in rows if r["split"] == "holdout"]),
            "requested_feature_count": len(elem_features_12),
            "kept_feature_count": global_12.get("kept_feature_count"),
        },
        "per_word_full_17": per_word,
        "ratio_numerator": ratio_diagnostics,
    }


def _word_census_requirement(rows: List[Dict[str, object]]) -> Dict[str, object]:
    counts = Counter(row["merged_word_omega_sq"] for row in rows)
    return {
        "counts": dict(counts),
        "distinct_count": len(counts),
        "has_all_8": len(counts) == 8,
        "has8": [w for w in sorted(counts) if len(counts) == 8],
    }


def _build_fresh_rows_v2(target_total: int = 360, max_total: int = 600) -> Tuple[List[Dict[str, object]], Counter, int]:
    rows = []
    seen = set()
    word_counts = Counter()
    stage_idx = 0
    stage_list = _grid_stages()
    split_stage = 0

    while split_stage < len(stage_list) and len(rows) < max_total:
        max_abs, max_den = stage_list[split_stage]
        free_values = _fraction_grid(max_abs, max_den)

        for free in product(free_values, repeat=4):
            if sum(free) == 0:
                continue

            try:
                omega = common.solve_from_free(free, common.SIG_FULL)
            except Exception:
                continue

            if not _is_generic_kinematic(omega):
                continue

            key = tuple((w.numerator, w.denominator) for w in omega)
            if key in seen:
                continue
            seen.add(key)

            sample_id = f"fresh-v2-{len(rows)+1:04d}"
            try:
                a_re, a_im = exact_oracle.run_bg_exact(omega)
            except Exception:
                continue

            wall_sig_no_swap, wall_key = common.canonicalize_wall_signatures(omega, WALL_CATALOG, (0, 1, 2), (3, 4, 5), allow_swap=False)
            wall_sig_swap, wall_key_swap = common.canonicalize_wall_signatures(omega, WALL_CATALOG, (0, 1, 2), (3, 4, 5), allow_swap=True)

            wall_raw = _signature_key_from_signs(common.wall_sign_map(omega, WALL_CATALOG), WALL_CATALOG)

            word = _merged_word_sq(omega)
            word_counts[word] += 1

            rows.append(
                {
                    "sample_id": sample_id,
                    "free_w": [frac_to_str(x) for x in free],
                    "omega": [frac_to_str(x) for x in omega],
                    "A_re": frac_to_str(a_re),
                    "A_im": frac_to_str(a_im),
                    "wall_key": wall_key,
                    "wall_signature": wall_key,
                    "wall_signature_raw": wall_raw,
                    "wall_signs": wall_sig_no_swap,
                    "wall_signature_swap": wall_key_swap,
                    "merged_word_omega_sq": word,
                }
            )

            if len(rows) >= target_total and len(word_counts) == 8:
                return rows, word_counts, split_stage
            if len(rows) >= max_total:
                return rows, word_counts, split_stage

        stage_idx += 1
        split_stage = stage_idx

    return rows, word_counts, split_stage


def _extend_rows(rows: List[Dict[str, object]], seen: set, word_counts: Counter, start_stage: int, target_total: int, max_total: int = 600) -> Tuple[List[Dict[str, object]], int]:
    added_rows, added_words, end_stage = _build_fresh_rows_v2(target_total=target_total, max_total=max_total)
    if not rows:
        return added_rows, end_stage

    # append only unseen new rows
    for row in added_rows[len(rows):]:
        key = (row["sample_id"], row["wall_key"])
        if key in seen:
            continue
        rows.append(row)
        if row["merged_word_omega_sq"]:
            word_counts[row["merged_word_omega_sq"]] += 1
        seen.add(key)

    return rows, end_stage


def _load_fresh_rows(path: Path) -> List[Dict[str, object]]:
    rows = []
    with path.open("r") as f:
        for line in f:
            row = json.loads(line)
            row["A_im"] = _frac_to_dict(row["A_im"])
            row["A_re"] = _frac_to_dict(row["A_re"])
            row["omega"] = [_frac_to_dict(x) for x in row["omega"]]
            row["_elementary_invariants"] = _elementary_invariants(row["omega"])
            rows.append(row)
    return rows


def _serialize_for_json(obj: object):
    if isinstance(obj, Fraction):
        return frac_to_str(obj)
    if isinstance(obj, dict):
        return {k: _serialize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize_for_json(v) for v in obj]
    if isinstance(obj, tuple):
        return [_serialize_for_json(v) for v in obj]
    return obj


def _write_fresh_rows(rows: List[Dict[str, object]], split_at: int) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out = DATA_DIR / "fresh_structure_oracle_v2.jsonl"
    rows_sorted = sorted(rows, key=lambda x: x["sample_id"])
    for i, row in enumerate(rows_sorted):
        row["split"] = "train" if i < split_at else "holdout"

    with out.open("w") as f:
        for row in rows_sorted:
            payload = _serialize_for_json(row)
            f.write(json.dumps(payload, sort_keys=True) + "\n")
    return out


def main():
    start = time.time()
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    rows, word_counts, stage_idx = _build_fresh_rows_v2(target_total=600, max_total=600)
    if len(rows) < 360:
        raise RuntimeError(f"insufficient fresh rows generated: {len(rows)}")
    if len(word_counts) < 8:
        raise RuntimeError(f"missing merged sq word coverage: {dict(word_counts)}")
    rows = _coerce_rows_to_fractions(rows)
    rows = sorted(rows, key=lambda x: x["sample_id"])

    d1_features, d1_raw = _build_h_features(1, kind_filter="D")
    h2_features_d, h2d_raw = _build_h_features(2, kind_filter="D")
    h2_features_s, h2s_raw = _build_h_features(2, kind_filter="S")
    h2_features_b, h2_raw = _build_h_features(2, kind_filter=None)
    h3_features_d, h3d_raw = _build_h_features(3, kind_filter="D")
    h3_features_s, h3s_raw = _build_h_features(3, kind_filter="S")
    h3_features_b, h3_raw = _build_h_features(3, kind_filter=None)
    h4_features_d, h4d_raw = _build_h_features(4, kind_filter="D")
    h4_features_s, h4s_raw = _build_h_features(4, kind_filter="S")
    h4_features_b, h4_raw = _build_h_features(4, kind_filter=None)
    p8_features = _build_p8_features(8)
    elem_features_17, _, elem_features_12 = _build_elementary_features()

    if len(h3_features_b) != 26:
        raise RuntimeError(f"H3 feature count drifted: {len(h3_features_b)}")

    wallpower_b = h2_features_b + h3_features_b + h4_features_b
    wallpower_d = h2_features_d + h3_features_d + h4_features_d
    wallpower_s = h2_features_s + h3_features_s + h4_features_s

    split_at = max(300, len(rows) - 60)
    for idx, row in enumerate(rows):
        row["split"] = "train" if idx < split_at else "holdout"

    _write_fresh_rows(rows, split_at)
    rows = _load_fresh_rows(DATA_DIR / "fresh_structure_oracle_v2.jsonl")

    train_rows = [r for r in rows if r["split"] == "train"]
    hold_rows = [r for r in rows if r["split"] == "holdout"]

    # staged diagnostics
    diag_h2 = _fit(h2_features_b, rows, "H2_only")
    diag_h2_h3 = _fit(h2_features_b + h3_features_b, rows, "H2_plus_H3")
    diag_h2_h3_h4 = _fit(wallpower_b, rows, "H2_plus_H3_plus_H4")
    diag_full = _fit(wallpower_b + p8_features, rows, "H2_plus_H3_plus_H4_plus_P8")

    # higher-priority D1/S3/P8 mixed diagnostics (exact QQ consistency checks)
    diag_d1 = _fit(d1_features, rows, "D1_only", modular_prefilter=True, require_train_overhang=20)
    diag_d1_s3 = _fit(
        d1_features + h3_features_s,
        rows,
        "D1_plus_S3",
        modular_prefilter=True,
        require_train_overhang=20,
    )
    diag_d1_s3_p8 = _fit(
        d1_features + h3_features_s + p8_features,
        rows,
        "D1_plus_S3_plus_P8",
        modular_prefilter=True,
        require_train_overhang=20,
    )

    # final wall-power family split by wall kind only (for report and consistency context)
    diag_h2_h3_h4_d = _fit(wallpower_d, rows, "WallPower_D_only", require_train_overhang=20)
    diag_h2_h3_h4_s = _fit(wallpower_s, rows, "WallPower_S_only", require_train_overhang=20)

    sanity = _run_sanity_checks(wallpower_b + p8_features, rows)
    hinge_check = _check_hinge_compatibility(rows, h3_features_b)
    word_census = _word_census_requirement(rows)
    rechecks = _check_fresh_rows_against_oracle(rows, n=5)
    elementary_invariant_diagnostic = _run_elementary_invariant_diagnostic(rows, elem_features_17, elem_features_12)

    out = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
        "fresh_rows": {
            "requested": 600,
            "actual": len(rows),
            "train_count": len(train_rows),
            "holdout_count": len(hold_rows),
            "holdout_distinct_kinematics": len({tuple((w.numerator, w.denominator) for w in r["omega"]) for r in hold_rows}),
            "wall_orbital_keys": len({r["wall_key"] for r in rows}),
            "word_sq_distinct": len(word_counts),
            "word_sq_counts": dict(word_counts),
            "split_source_stage_index": stage_idx,
            "train_overhang": len(train_rows) - len(wallpower_b),
        },
        "dictionary": {
            "H2": {
                **_feature_dictionary_report(h2_features_b, "H2"),
                "raw_candidate_count": h2_raw,
            },
            "H3": {
                **_feature_dictionary_report(h3_features_b, "H3"),
                "raw_candidate_count": h3_raw,
            },
            "D1": {
                "count": len(d1_features),
                "raw_candidate_count": d1_raw,
                "max_expanded_terms": max((f["expanded_term_count"] for f in d1_features), default=0),
            },
            "H4": {
                **_feature_dictionary_report(h4_features_b, "H4"),
                "raw_candidate_count": h4_raw,
            },
            "P8": {
                "count": len(p8_features),
                "max_expanded_terms": max((f["expanded_term_count"] for f in p8_features), default=0),
            },
        },
        "staged_diagnostics": {
            "D1_only": diag_d1,
            "D1_plus_S3": diag_d1_s3,
            "D1_plus_S3_plus_P8": diag_d1_s3_p8,
            "H2_only": diag_h2,
            "H2_plus_H3": diag_h2_h3,
            "H2_plus_H3_plus_H4": diag_h2_h3_h4,
            "H2_plus_H3_plus_H4_plus_P8": diag_full,
            "H2_plus_H3_plus_H4_D_only_rank": diag_h2_h3_h4_d.get("feature_family_counts", {}).get("matrix_rank"),
            "H2_plus_H3_plus_H4_S_only_rank": diag_h2_h3_h4_s.get("feature_family_counts", {}).get("matrix_rank"),
        },
        "fits": {
            "D1_only": diag_d1,
            "D1_plus_S3": diag_d1_s3,
            "D1_plus_S3_plus_P8": diag_d1_s3_p8,
            "H2_only": diag_h2,
            "H2_plus_H3": diag_h2_h3,
            "H2_plus_H3_plus_H4": diag_h2_h3_h4,
            "H2_plus_H3_plus_H4_plus_P8": diag_full,
        },
        "D_S_ranks_for_final_wallpower": {
            "D": diag_h2_h3_h4_d,
            "S": diag_h2_h3_h4_s,
            "H2_plus_H3_plus_H4_union": {
                "requested": len(wallpower_b),
                "kept": len([f for f in wallpower_b if f is not None]),
            },
        },
        "sanity": sanity,
        "wall_hinge_agreement": hinge_check,
        "fresh_row_recheck": rechecks,
        "sq_word_census": word_census,
        "elementary_invariant_diagnostic": elementary_invariant_diagnostic,
        "performance": {
            "rows_generated": len(rows),
            "candidate_stages_used": stage_idx,
            "max_features_wallpower": len(wallpower_b),
        },
    }

    # prefer full exact dictionary for the compact nonzero evaluator only when exact fit holds
    final_fit = diag_full if diag_full.get("status") == "ok" else None
    if final_fit is not None:
        out["final_exact_wallpower_plus_p8_nonzero_terms"] = final_fit.get("nonzero_coefficients", [])

    out_path = DATA_DIR / "wall_power_fit.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2, sort_keys=True, default=str)

    txt_out = DATA_DIR / "wall_power_fit.txt"
    report_lines = [
        "wall_power_fit summary",
        f"fresh rows total: {len(rows)} (train={len(train_rows)}, holdout={len(hold_rows)})",
        f"square-word classes found: {len(word_counts)} / 8",
        f"H2 features dedup: {len(h2_features_b)} raw={h2_raw}",
        f"H3 features dedup: {len(h3_features_b)} raw={h3_raw}",
        f"H4 features dedup: {len(h4_features_b)} raw={h4_raw}",
        f"D1 wall-only features dedup: {len(d1_features)} raw={d1_raw}",
        f"P8 features: {len(p8_features)}",
        f"D1-only rank={diag_d1.get('feature_family_counts', {}).get('matrix_rank')} status={diag_d1.get('status')} modguard={diag_d1.get('modular_prefilter', {}).get('status')}",
        f"D1+S3 rank={diag_d1_s3.get('feature_family_counts', {}).get('matrix_rank')} status={diag_d1_s3.get('status')} modguard={diag_d1_s3.get('modular_prefilter', {}).get('status')}",
        f"D1+S3+P8 rank={diag_d1_s3_p8.get('feature_family_counts', {}).get('matrix_rank')} status={diag_d1_s3_p8.get('status')} modguard={diag_d1_s3_p8.get('modular_prefilter', {}).get('status')}",
        f"H2-only rank={diag_h2.get('feature_family_counts', {}).get('matrix_rank')} status={diag_h2.get('status')}",
        f"H2+H3 rank={diag_h2_h3.get('feature_family_counts', {}).get('matrix_rank')} status={diag_h2_h3.get('status')}",
        f"H2+H3+H4 rank={diag_h2_h3_h4.get('feature_family_counts', {}).get('matrix_rank')} status={diag_h2_h3_h4.get('status')}",
        f"H2+H3+H4+P8 rank={diag_full.get('feature_family_counts', {}).get('matrix_rank')} status={diag_full.get('status')}",
        f"D-only WallPower rank={diag_h2_h3_h4_d.get('feature_family_counts', {}).get('matrix_rank')} status={diag_h2_h3_h4_d.get('status')}",
        f"S-only WallPower rank={diag_h2_h3_h4_s.get('feature_family_counts', {}).get('matrix_rank')} status={diag_h2_h3_h4_s.get('status')}",
        f"sanity invariance: pass={sanity.get('invariance_passed')} failures={sanity.get('invariance_failure_count')}",
        f"sanity homogeneity: pass={sanity.get('homogeneity_passed')} failures={sanity.get('homogeneity_failure_count')}",
        f"wall_hinge H3 count match: {hinge_check.get('h3_count_match', False)}",
        f"fresh recheck (first {rechecks.get('requested')}) all_match={rechecks.get('all_match')}",
        f"elementary 17 rank={elementary_invariant_diagnostic['global_full_17'].get('matrix_rank')} status={elementary_invariant_diagnostic['global_full_17'].get('status')}",
        f"elementary sym12 rank={elementary_invariant_diagnostic['global_sym_12'].get('matrix_rank')} status={elementary_invariant_diagnostic['global_sym_12'].get('status')}",
        f"elementary per-word_17 fits={len(elementary_invariant_diagnostic['per_word_full_17'])}",
        f"elementary pairwise identity pass={elementary_invariant_diagnostic['pairwise_identity'].get('status')} fails={elementary_invariant_diagnostic['pairwise_identity'].get('fail_count')}",
        f"ratio d1 [N_1/(r-t)] status={elementary_invariant_diagnostic['ratio_numerator']['d_1'].get('status')} rank={elementary_invariant_diagnostic['ratio_numerator']['d_1'].get('matrix_rank')}",
        f"ratio d2 [N_2/(r-t)^2] status={elementary_invariant_diagnostic['ratio_numerator']['d_2'].get('status')} rank={elementary_invariant_diagnostic['ratio_numerator']['d_2'].get('matrix_rank')}",
        f"ratio d3 [N_3/(r-t)^3] status={elementary_invariant_diagnostic['ratio_numerator']['d_3'].get('status')} rank={elementary_invariant_diagnostic['ratio_numerator']['d_3'].get('matrix_rank')}",
        f"outputs: {out_path} {txt_out} {DATA_DIR / 'fresh_structure_oracle_v2.jsonl'}",
        f"elapsed_s={time.time() - start:.1f}",
    ]
    txt_out.write_text("\n".join(report_lines) + "\n")

    print("\n".join(report_lines))


if __name__ == "__main__":
    main()
