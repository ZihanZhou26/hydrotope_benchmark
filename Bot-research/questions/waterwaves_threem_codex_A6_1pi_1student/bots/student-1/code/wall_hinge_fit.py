#!/usr/bin/env python3
"""Batch wall-hinge oracle fitting and word-census diagnostics.

Outputs:
- data/wall_hinge_fit.json
- data/wall_hinge_fit.txt
- data/fresh_structure_oracle.jsonl
- data/word_census.json
"""

import json
import time
from collections import Counter
from fractions import Fraction
from itertools import combinations_with_replacement, permutations, product
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import common
from common import frac_to_str
import exact_oracle

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
WALL_CATALOG = common.build_wall_catalog()
WALL_ENTRIES = []
for _wall in WALL_CATALOG:
    if _wall["kind"] != "diff" and _wall["kind"] != "sum":
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


def _signature_key_from_signs(sign_map: Dict[str, int], wall_catalog) -> str:
    return common.serialize_signs(sign_map, wall_catalog)


def _positive_cube(x: Fraction) -> Fraction:
    return x ** 3 if x > 0 else Fraction(0, 1)


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


def _mask_iter_by_size(total: int, sizes: Iterable[int]) -> List[int]:
    out = []
    for m in common.internal_subset_bits(total):
        bits = m.bit_count() if hasattr(int, "bit_count") else bin(m).count("1")
        if bits in sizes:
            out.append(m)
    return out


def _is_generic_kinematic(omega: Sequence[Fraction], wall_catalog=WALL_CATALOG) -> bool:
    if any(w == 0 for w in omega):
        return False

    a2 = [w * w for w in omega]
    for wall in wall_catalog:
        if common.wall_value(a2, wall) == 0:
            return False

    for mask in _mask_iter_by_size(6, (2, 3)):
        h, _ = common.h_T(omega, mask, common.SIG_FULL)
        if h == 0:
            return False
    return True


def _merged_word(omega: Sequence[Fraction], key: str = "value") -> str:
    if key == "value":
        idx = sorted(range(6), key=lambda i: (omega[i], i))
    elif key == "sq":
        idx = sorted(range(6), key=lambda i: (omega[i] * omega[i], omega[i], i))
    else:
        raise ValueError("invalid merged-word key")
    return "".join("M" if i < 3 else "P" for i in idx)


def _swap_word(word: str) -> str:
    return "".join("P" if c == "M" else "M" for c in word)


def _canonical_orbit_word(word: str) -> str:
    candidates = [
        word,
        _swap_word(word),
        word[::-1],
        _swap_word(word)[::-1],
    ]
    return min(candidates)


def _sign_pair(omega: Sequence[Fraction]) -> Tuple[int, int, int, int]:
    m_pos = sum(1 for i in range(3) if omega[i] > 0)
    m_neg = sum(1 for i in range(3) if omega[i] < 0)
    p_pos = sum(1 for i in range(3, 6) if omega[i] > 0)
    p_neg = sum(1 for i in range(3, 6) if omega[i] < 0)
    return (m_pos, m_neg, p_pos, p_neg)


def _canonical_sign_pair(pair: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    m_pos, m_neg, p_pos, p_neg = pair
    candidates = [
        pair,
        (p_pos, p_neg, m_pos, m_neg),
        (m_neg, m_pos, p_neg, p_pos),
        (p_neg, p_pos, m_neg, m_pos),
    ]
    return min(candidates)


def _free_fractions_for_small_grid() -> List[Fraction]:
    nums = [-4, -3, -2, -1, 1, 2, 3, 4]
    out = []
    for d in (1,):
        for n in nums:
            out.append(Fraction(n, d))
    out = sorted(set(out), key=lambda x: (abs(x.numerator) / x.denominator, x))
    return out


def _free_fractions_for_census_grid() -> List[Fraction]:
    nums = [-4, -3, -2, -1, 1, 2, 3, 4]
    denoms = (1, 2)
    out = []
    for n in nums:
        for d in denoms:
            out.append(Fraction(n, d))
    out = sorted(set(out), key=lambda x: (abs(x.numerator) / x.denominator, x.denominator, x))
    return out


def _build_fresh_rows(target: int = 160) -> List[Dict[str, object]]:
    rows = []
    seen = set()
    free_values = _free_fractions_for_small_grid()
    wall_catalog = WALL_CATALOG

    for free in product(free_values, repeat=4):
        if sum(free) == 0:
            continue

        try:
            omega = common.solve_from_free(free, common.SIG_FULL)
        except Exception:
            continue

        if not _is_generic_kinematic(omega, wall_catalog=wall_catalog):
            continue

        key = tuple((w.numerator, w.denominator) for w in omega)
        if key in seen:
            continue

        seen.add(key)

        sample_id = f"fresh-{len(rows)+1:04d}"
        try:
            res = exact_oracle.evaluate_omega(omega, sample_id, wall_catalog)
        except Exception as err:
            # safety: exact oracle failed (should be rare); keep deterministic skip
            continue

        wall_no_swap, wall_key = common.canonicalize_wall_signatures(
            omega,
            wall_catalog,
            (0, 1, 2),
            (3, 4, 5),
            allow_swap=False,
        )

        wall_counts = {
            "M": {
                "positive": sum(1 for i in range(3) if omega[i] > 0),
                "negative": sum(1 for i in range(3) if omega[i] < 0),
            },
            "P": {
                "positive": sum(1 for i in range(3, 6) if omega[i] > 0),
                "negative": sum(1 for i in range(3, 6) if omega[i] < 0),
            },
        }

        rows.append(
            {
                "sample_id": sample_id,
                "free_w": [frac_to_str(x) for x in free],
                "omega": [frac_to_str(x) for x in omega],
                "A_im": frac_to_str(res.A_im),
                "A_re": frac_to_str(res.A_re),
                "wall_key": wall_key,
                "wall_signature": wall_key,
                "wall_signature_raw": _signature_key_from_signs(common.wall_sign_map(omega, wall_catalog), wall_catalog),
                "wall_signs": res.wall_signs,
                "wall_signature_swap": res.wall_signature_swap,
                "sign_counts": wall_counts,
                "merged_word_omega": _merged_word(omega, "value"),
                "merged_word_omega_sq": _merged_word(omega, "sq"),
            }
        )

        if len(rows) >= target:
            break

    return rows


def _write_fresh_rows(rows: List[Dict[str, object]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / "fresh_structure_oracle.jsonl"

    rows_sorted = sorted(rows, key=lambda x: x["sample_id"])
    split_at = max(80, len(rows_sorted) - 30)
    if split_at < 80:
        split_at = 80
    for i, row in enumerate(rows_sorted):
        row["split"] = "train" if i < split_at else "holdout"

    with out_path.open("w") as f:
        for row in rows_sorted:
            f.write(json.dumps(row, sort_keys=True) + "\n")

    return out_path


def _load_fresh_rows(path: Path) -> List[Dict[str, object]]:
    rows = []
    with path.open("r") as f:
        for line in f:
            row = json.loads(line)
            row["A_im"] = _frac_to_dict(row["A_im"])
            row["omega"] = [_frac_to_dict(x) for x in row["omega"]]
            rows.append(row)
    return rows


def _term_tuple_from_data(kind: str, i: int, j: int, eps: int, u: int, v: int) -> Tuple[str, int, int, int, int, int]:
    if u > v:
        u, v = v, u
    return (kind, i, j, eps, u, v)


def _term_id(term: Tuple[str, int, int, int, int, int]) -> str:
    kind, i, j, eps, u, v = term
    return f"{kind}|{i}:{j}|eps={eps}|{u}:{v}"


def _collect_h3_terms(
    kind: str,
    i: int,
    j: int,
    eps: int,
    mon_u: int,
    mon_v: int,
) -> List[Tuple[str, int, int, int, int, int]]:
    seen = set()
    for perm_m, perm_p, do_swap in GROUP_ACTIONS:
        t_kind, ti, tj, t_sign = _transform_wall(kind, i, j, perm_m, perm_p, do_swap)
        uu = _transform_idx(mon_u, perm_m, perm_p, do_swap)
        vv = _transform_idx(mon_v, perm_m, perm_p, do_swap)
        t_eps = eps * t_sign
        term = _term_tuple_from_data(t_kind, ti, tj, t_eps, uu, vv)
        seen.add(term)

    out = []
    for term in sorted(seen):
        out.append(term)
    return out


def _build_feature_id(feature_kind: str, rep_key: str, source: Tuple[str, str, int, int, int]) -> str:
    if feature_kind == "H3":
        kind, eps, i, j, mon = source
        return f"{kind}|eps={eps}|wall={i},{j}|mono={mon}|rep={rep_key}"
    return f"P8|rep={rep_key}"


def _h3_raw_count(kind_filter: str = None) -> int:
    count = 0
    for kind, _, _ in WALL_ENTRIES:
        if kind_filter and kind != kind_filter:
            continue
        for _eps in (-1, 1):
            count += len(list(combinations_with_replacement(range(6), 2))
            )
    return count


def _build_h3_features(kind_filter: str = None) -> Tuple[List[Dict[str, object]], int]:
    raw_count = _h3_raw_count(kind_filter)
    seen = {}
    features: List[Dict[str, object]] = []

    for kind, wi, wj in WALL_ENTRIES:
        if kind_filter and kind != kind_filter:
            continue
        for eps in (-1, 1):
            for mon_u, mon_v in combinations_with_replacement(range(6), 2):
                terms = _collect_h3_terms(kind, wi, wj, eps, mon_u, mon_v)
                rep_key = "|".join(_term_id(t) for t in terms)
                if rep_key in seen:
                    continue
                seen[rep_key] = True
                source = (kind, str(eps), mon_u, mon_v, wi)
                features.append(
                    {
                        "family": "H3",
                        "kind": kind,
                        "wall": [wi, wj],
                        "epsilon": eps,
                        "monomial": [mon_u, mon_v],
                        "orbit_representative_key": rep_key,
                        "id": _build_feature_id("H3", rep_key, source),
                        "terms": terms,
                        "expanded_term_count": len(terms),
                    }
                )

    return features, raw_count


def _composition_tuples(total: int, parts: int, prefix: List[int], out: List[Tuple[int, ...]], start: int = 0) -> None:
    if len(prefix) == parts - 1:
        rem = total - sum(prefix)
        if rem >= 0:
            out.append(tuple(prefix + [rem]))
        return
    for v in range(total - sum(prefix) + 1):
        prefix.append(v)
        _composition_tuples(total, parts, prefix, out, start + 1)
        prefix.pop()


def _generate_exponent_vectors(total_degree: int = 8, vars_count: int = 6) -> List[Tuple[int, ...]]:
    out: List[Tuple[int, ...]] = []
    _composition_tuples(total_degree, vars_count, [], out)
    return out


def _transform_exponent_vector(exp: Tuple[int, ...], perm_m: Tuple[int, int, int], perm_p: Tuple[int, int, int], do_swap: bool) -> Tuple[int, ...]:
    out = [0] * 6
    for i, e in enumerate(exp):
        ni = _transform_idx(i, perm_m, perm_p, do_swap)
        out[ni] = e
    return tuple(out)


def _build_p8_features(total_degree: int = 8) -> List[Dict[str, object]]:
    raw: List[Tuple[int, ...]] = _generate_exponent_vectors(total_degree)
    seen = {}
    features = []

    for exp in raw:
        orbit = set()
        for perm_m, perm_p, do_swap in GROUP_ACTIONS:
            orbit.add(_transform_exponent_vector(exp, perm_m, perm_p, do_swap))

        rep = min(orbit)
        if rep in seen:
            continue
        seen[rep] = True
        rep_key = ";".join(
            ",".join(str(e) for e in t) for t in sorted(orbit)
        )
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


def _eval_monomial_exp(exp: Tuple[int, ...], omega: Sequence[Fraction]) -> Fraction:
    val = Fraction(1, 1)
    for i, pwr in enumerate(exp):
        if pwr == 0:
            continue
        val *= omega[i] ** pwr
    return val


def _eval_h3_feature(feature: Dict[str, object], omega: Sequence[Fraction]) -> Fraction:
    s = Fraction(0, 1)
    for term in feature["terms"]:
        kind, i, j, eps, u, v = term
        w = _wall_value(kind, i, j, omega)
        s += (omega[u] * omega[v]) * _positive_cube(eps * w)
    return s


def _eval_p8_feature(feature: Dict[str, object], omega: Sequence[Fraction]) -> Fraction:
    total = Fraction(0, 1)
    for exp in feature["terms"]:
        total += _eval_monomial_exp(exp, omega)
    return total


def _eval_feature(feature: Dict[str, object], omega: Sequence[Fraction]) -> Fraction:
    if feature["family"] == "H3":
        return _eval_h3_feature(feature, omega)
    return _eval_p8_feature(feature, omega)


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


def _find_first_inconsistent_prefix(X: List[List[Fraction]], y: List[Fraction], meta: List[Dict[str, object]]) -> Dict[str, object]:
    for k in range(1, len(X) + 1):
        a = [row[:] for row in X[:k]]
        b = y[:k]
        m = len(a)
        n = len(a[0]) if a else 0
        row = 0
        col = 0
        piv = 0
        rank = 0
        aug = [a[i] + [b[i]] for i in range(m)]
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
            rank += 1

        inconsistent = False
        for rr in range(m):
            if all(v == 0 for v in aug[rr][:n]) and aug[rr][n] != 0:
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
                "rankA": rank,
                "rankAug": rank + 1,
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
            return None, {
                "status": "inconsistent",
                "matrix_rank": row,
                "matrix_rank_aug": row + 1,
            }

    coeffs = [Fraction(0) for _ in range(n)]
    for col, rr in enumerate(pivots):
        if rr != -1:
            coeffs[col] = aug[rr][-1]

    return coeffs, {
        "status": "ok",
        "matrix_rank": row,
        "matrix_rank_aug": row,
        "num_free": n - row,
    }


def _residual_summary(vals: List[Fraction]) -> Dict[str, object]:
    if not vals:
        return {"count": 0, "max_abs": "0", "mean_abs": "0"}
    mags = [abs(v) for v in vals]
    return {
        "count": len(vals),
        "max_abs": frac_to_str(max(mags)),
        "mean_abs": frac_to_str(sum(mags, Fraction(0)) / len(mags)),
    }


def _build_design_matrix(
    features: List[Dict[str, object]],
    rows: List[Dict[str, object]],
) -> Tuple[List[List[Fraction]], List[Fraction], List[Dict[str, object]], List[Dict[str, object]]]:
    X = []
    y = []
    meta = []
    kept_features = []

    for feature in features:
        col = []
        nonzero = False
        for row in rows:
            val = _eval_feature(feature, row["omega"])
            col.append(val)
            if val != 0:
                nonzero = True
        if nonzero:
            kept_features.append(feature)

    for row in rows:
        omega = row["omega"]
        row_vals = []
        for feature in kept_features:
            row_vals.append(_eval_feature(feature, omega))
        X.append(row_vals)
        y.append(row["A_im"])
        meta.append({"sample_id": row["sample_id"], "split": row["split"], "wall_key": row.get("wall_key")})

    # Remove zero columns across all rows (already above via nonzero check)
    return X, y, meta, kept_features


def _fit(features: List[Dict[str, object]], rows: List[Dict[str, object]], fit_name: str) -> Dict[str, object]:
    rows_sorted = sorted(rows, key=lambda r: r["sample_id"])
    train_rows = [r for r in rows_sorted if r["split"] == "train"]
    hold_rows = [r for r in rows_sorted if r["split"] == "holdout"]

    train_X, train_y, train_meta, kept_features = _build_design_matrix(features, train_rows)
    hold_X, hold_y, hold_meta, _ = _build_design_matrix(kept_features, hold_rows)

    out = {
        "name": fit_name,
        "requested_feature_count": len(features),
        "kept_feature_count": len(kept_features),
    }

    if not kept_features:
        out.update(
            {
                "status": "failed",
                "reason": "no nonzero features",
                "rows": len(rows_sorted),
            }
        )
        return out

    rankA = _matrix_rank([row[:] for row in train_X])
    rank_aug = None
    aug = [r[:] + [y] for r, y in zip(train_X, train_y)]
    rank_aug = _matrix_rank(aug)

    contradiction = _find_first_inconsistent_prefix(train_X, train_y, train_meta)

    coeffs, fit_meta = _solve_linear_exact(train_X, train_y)

    out["feature_family_counts"] = {
        "feature_count": len(kept_features),
        "raw_feature_count": len(features),
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

    res_train = [_eval_residual(coeffs, kept_features, omega, target) for omega, target in zip([r["omega"] for r in train_rows], train_y)]
    out["train_residuals"] = _residual_summary(res_train)

    if hold_X:
        res_hold = [_eval_residual(coeffs, kept_features, row["omega"], _frac_to_dict(row["A_im"]) if not isinstance(row["A_im"], Fraction) else row["A_im"]) for row in hold_rows]
        out["holdout_residuals"] = _residual_summary(res_hold)
        out["holds_out_exact"] = all(v == 0 for v in res_hold)
    else:
        out["holdout_residuals"] = {"count": 0, "max_abs": "0", "mean_abs": "0"}
        out["holds_out_exact"] = True

    if not out["holds_out_exact"]:
        out["status"] = "holdout_failed"
    else:
        out["status"] = "ok"

    nz = [(f, c) for f, c in zip(kept_features, coeffs) if c != 0]
    out["nonzero_coefficients"] = [
        {
            "feature_id": f["id"],
            "coefficient": frac_to_str(c),
            "expanded_term_count": f["expanded_term_count"],
            "representative_key": f["orbit_representative_key"],
        }
        for f, c in nz
    ]
    out["nonzero_coefficient_count"] = len(nz)

    if nz:
        out["max_expanded_term_count"] = max(item["expanded_term_count"] for item in out["nonzero_coefficients"])
    else:
        out["max_expanded_term_count"] = 0

    return out


def _eval_residual(coeffs: List[Fraction], features: List[Dict[str, object]], omega: Sequence[Fraction], target: Fraction) -> Fraction:
    pred = Fraction(0)
    for c, f in zip(coeffs, features):
        pred += c * _eval_feature(f, omega)
    return target - pred


def _feature_dictionary_report(features: List[Dict[str, object]], name: str) -> Dict[str, object]:
    return {
        "name": name,
        "count": len(features),
        "max_expanded_terms": max((f["expanded_term_count"] for f in features), default=0),
        "term_count_examples": [
            {"feature_id": f["id"], "expanded_terms": f["expanded_term_count"], "rep": f["orbit_representative_key"][:80]}
            for f in features[:5]
        ],
    }


def _run_sanity_checks(h3_features: List[Dict[str, object]], rows: List[Dict[str, object]], test_points: int = 3) -> Dict[str, object]:
    check_rows = rows[:test_points]
    inv = []
    homo = []

    for idx, row in enumerate(check_rows):
        omega = row["omega"]
        scaled = [Fraction(2, 1) * x for x in omega]

        for f in h3_features:
            base = _eval_feature(f, omega)
            scaled_val = _eval_feature(f, scaled)
            homo.append(base * (2 ** 8) == scaled_val)

            for perm_m, perm_p, do_swap in GROUP_ACTIONS[:]:
                omega_t = _transform_omega(omega, perm_m, perm_p, do_swap)
                tval = _eval_feature(f, omega_t)
                inv.append(tval == base)

    ok_inv = all(inv)
    ok_homo = all(homo)
    return {
        "tested_rows": min(test_points, len(check_rows)),
        "invariance_passed": ok_inv,
        "homogeneity_passed": ok_homo,
        "invariance_failure_count": inv.count(False),
        "homogeneity_failure_count": homo.count(False),
    }


def _word_census(target_count: int = 5000) -> Dict[str, object]:
    seen = set()
    words = {
        "a_raw": Counter(),
        "b_raw": Counter(),
        "b_canonical": Counter(),
        "c_raw": Counter(),
        "c_canonical": Counter(),
        "e_raw": Counter(),
        "e_canonical": Counter(),
    }
    reps = {
        "a_raw": {},
        "b_raw": {},
        "b_canonical": {},
        "c_raw": {},
        "c_canonical": {},
        "e_raw": {},
        "e_canonical": {},
    }

    free_values = _free_fractions_for_census_grid()

    for free in product(free_values, repeat=4):
        if sum(free) == 0:
            continue

        try:
            omega = common.solve_from_free(free, common.SIG_FULL)
        except Exception:
            continue

        if not _is_generic_kinematic(omega):
            continue

        key = tuple((x.numerator, x.denominator) for x in omega)
        if key in seen:
            continue

        seen.add(key)

        a_pos = sum(1 for i in range(3) if omega[i] > 0)
        p_pos = sum(1 for i in range(3, 6) if omega[i] > 0)
        pair_a = f"M:{a_pos},P:{p_pos}"
        words["a_raw"][pair_a] += 1
        if pair_a not in reps["a_raw"]:
            reps["a_raw"][pair_a] = [frac_to_str(x) for x in omega]

        b = _merged_word(omega, "value")
        b_can = _canonical_orbit_word(b)
        words["b_raw"][b] += 1
        words["b_canonical"][b_can] += 1
        if b not in reps["b_raw"]:
            reps["b_raw"][b] = [frac_to_str(x) for x in omega]
        if b_can not in reps["b_canonical"]:
            reps["b_canonical"][b_can] = [frac_to_str(x) for x in omega]

        c = _merged_word(omega, "sq")
        c_can = _canonical_orbit_word(c)
        words["c_raw"][c] += 1
        words["c_canonical"][c_can] += 1
        if c not in reps["c_raw"]:
            reps["c_raw"][c] = [frac_to_str(x) for x in omega]
        if c_can not in reps["c_canonical"]:
            reps["c_canonical"][c_can] = [frac_to_str(x) for x in omega]

        e = _sign_pair(omega)
        e_raw = "M(+/-):{}:{}, P(+/-):{}:{}".format(*e)
        e_can = "M(+/-):{}:{}, P(+/-):{}:{}".format(*_canonical_sign_pair(e))
        words["e_raw"][e_raw] += 1
        words["e_canonical"][e_can] += 1
        if e_raw not in reps["e_raw"]:
            reps["e_raw"][e_raw] = [frac_to_str(x) for x in omega]
        if e_can not in reps["e_canonical"]:
            reps["e_canonical"][e_can] = [frac_to_str(x) for x in omega]

        if len(seen) >= target_count:
            break

    def _make_block(name: str):
        return {
            "counts": {k: words[f"{name}_raw"][k] for k in words[f"{name}_raw"]} if name in ("a", "b", "c", "e") else {},
            "representatives": reps if False else {},
        }

    return {
        "requested_points": target_count,
        "actual_points": len(seen),
        "classifications": {
            "a_raw": {
                "counts": dict(words["a_raw"]),
                "representatives": {k: v for k, v in reps["a_raw"].items()},
                "has_exactly_8": (len(words["a_raw"]) == 8),
            },
            "b_raw": {
                "counts": dict(words["b_raw"]),
                "representatives": {k: v for k, v in reps["b_raw"].items()},
                "has_exactly_8": (len(words["b_raw"]) == 8),
            },
            "b_canonical_orbit": {
                "counts": dict(words["b_canonical"]),
                "representatives": {k: v for k, v in reps["b_canonical"].items()},
                "has_exactly_8": (len(words["b_canonical"]) == 8),
            },
            "c_raw": {
                "counts": dict(words["c_raw"]),
                "representatives": {k: v for k, v in reps["c_raw"].items()},
                "has_exactly_8": (len(words["c_raw"]) == 8),
            },
            "c_canonical_orbit": {
                "counts": dict(words["c_canonical"]),
                "representatives": {k: v for k, v in reps["c_canonical"].items()},
                "has_exactly_8": (len(words["c_canonical"]) == 8),
            },
            "e_canonical_orbit_under_setswap_and_sign": {
                "counts": dict(words["e_canonical"]),
                "representatives": {k: v for k, v in reps["e_canonical"].items()},
                "has_exactly_8": (len(words["e_canonical"]) == 8),
            },
            "e_raw": {
                "counts": dict(words["e_raw"]),
                "representatives": {k: v for k, v in reps["e_raw"].items()},
                "has_exactly_8": (len(words["e_raw"]) == 8),
            },
        },
        "classifications_with_exactly_8": {
            "a_raw": len(words["a_raw"]) == 8,
            "b_raw": len(words["b_raw"]) == 8,
            "b_canonical": len(words["b_canonical"]) == 8,
            "c_raw": len(words["c_raw"]) == 8,
            "c_canonical": len(words["c_canonical"]) == 8,
            "e_raw": len(words["e_raw"]) == 8,
            "e_canonical": len(words["e_canonical"]) == 8,
        },
    }


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


def main():
    start = time.time()
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    fresh_rows = _build_fresh_rows(150)
    if len(fresh_rows) < 110:
        raise RuntimeError(f"insufficient fresh rows generated: {len(fresh_rows)}")

    fresh_path = _write_fresh_rows(fresh_rows)
    rows = _load_fresh_rows(fresh_path)

    train_rows = [r for r in rows if r["split"] == "train"]
    hold_rows = [r for r in rows if r["split"] == "holdout"]

    h3_features_both, h3_raw = _build_h3_features(None)
    h3_features_d, h3d_raw = _build_h3_features("D")
    h3_features_s, h3s_raw = _build_h3_features("S")
    p8_features = _build_p8_features(8)

    diag_d = _fit(h3_features_d, rows, "H3_D")
    diag_s = _fit(h3_features_s, rows, "H3_S")
    diag_b = _fit(h3_features_both, rows, "H3_both")

    fit_h3 = _fit(h3_features_both, rows, "H3_only")
    fit_h3_p8 = _fit(h3_features_both + p8_features, rows, "H3_plus_P8")

    sanity = _run_sanity_checks(h3_features_both, rows)
    rechecks = _check_fresh_rows_against_oracle(rows, n=5)

    word_census = _word_census(5000)

    result = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
        "fresh_rows": {
            "requested": 150,
            "actual": len(rows),
            "train_count": len(train_rows),
            "holdout_count": len(hold_rows),
            "holdout_distinct_kinematics": len({tuple((w.numerator, w.denominator) for w in r["omega"]) for r in hold_rows}),
            "wall_orbital_keys": len({r["wall_key"] for r in rows}),
        },
        "dictionary": {
            "H3": {
                **_feature_dictionary_report(h3_features_both, "H3"),
                "raw_candidate_count": h3_raw,
            },
            "P8": {
                "count": len(p8_features),
                "max_expanded_terms": max((f["expanded_term_count"] for f in p8_features), default=0),
            },
        },
        "sanity": sanity,
        "staged_diagnostics": {
            "H3_D_only": diag_d,
            "H3_S_only": diag_s,
            "H3_both": diag_b,
        },
        "fits": {
            "H3_only": fit_h3,
            "H3_plus_P8": fit_h3_p8,
        },
        "fresh_row_recheck": rechecks,
    }

    word_out = DATA_DIR / "word_census.json"
    with word_out.open("w") as f:
        json.dump(word_census, f, indent=2, sort_keys=True)

    out_payload = DATA_DIR / "wall_hinge_fit.json"
    with out_payload.open("w") as f:
        json.dump(result, f, indent=2, sort_keys=True, default=str)

    # compact text report
    report_lines = [
        "wall_hinge_fit summary",
        f"fresh rows total: {len(rows)} (train={len(train_rows)}, holdout={len(hold_rows)})",
        f"wall_orbit keys: {len({r['wall_key'] for r in rows})}",
        f"H3 features (dedup): {len(h3_features_both)} raw={h3_raw}",
        f"P8 features (dedup): {len(p8_features)}",
        f"H3 diag D-only: rank={diag_d.get('feature_family_counts', {}).get('matrix_rank')} / raw={h3d_raw}",
        f"H3 diag S-only: rank={diag_s.get('feature_family_counts', {}).get('matrix_rank')} / raw={h3s_raw}",
        f"H3 diag both: rank={diag_b.get('feature_family_counts', {}).get('matrix_rank')}",
        f"Fit H3 only status: {fit_h3.get('status')} train-rank={fit_h3.get('feature_family_counts', {}).get('matrix_rank')}",
        f"Fit H3+P8 status: {fit_h3_p8.get('status')} train-rank={fit_h3_p8.get('feature_family_counts', {}).get('matrix_rank')}",
        f"H3+P8 nonzero coeff count: {fit_h3_p8.get('nonzero_coefficient_count')}",
        f"H3+P8 max expanded terms: {fit_h3_p8.get('max_expanded_term_count')}",
        f"sanity invariance: pass={sanity.get('invariance_passed')} failures={sanity.get('invariance_failure_count')}",
        f"sanity homogeneity: pass={sanity.get('homogeneity_passed')} failures={sanity.get('homogeneity_failure_count')}",
        f"fresh recheck (first {rechecks.get('requested')}) all_match={rechecks.get('all_match')}",
        f"word census classifications with count==8: {[name for name, flag in word_census['classifications_with_exactly_8'].items() if flag]}",
        f"word census points: {word_census['actual_points']}",
        f"outputs: {out_payload} {word_out} {fresh_path}",
    ]
    report = "\n".join(report_lines)

    txt_path = DATA_DIR / "wall_hinge_fit.txt"
    txt_path.write_text(report + "\n")

    print(report)
    print(f"elapsed_s={time.time() - start:.1f}")


if __name__ == "__main__":
    main()
