import json
from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path

import common

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

GROUPS = (
    ("A", "A", True),
    ("A", "A", False),
    ("A", "C", False),
    ("A", "R", False),
    ("C", "C", True),
    ("C", "C", False),
    ("C", "R", False),
    ("R", "R", True),
    ("R", "R", False),
)


class CategoryFeature(object):
    def __init__(self, r, category):
        self.r = r
        self.category = category
        self.name = f"r{r}_{_category_name(category)}"

    @staticmethod
    def _positive_cube(x):
        return x ** 3 if x > 0 else Fraction(0)

    @staticmethod
    def _b(omega_sq, I, target):
        x = sum(omega_sq[i] for i in I)
        out = Fraction(0)
        for r in range(len(target) + 1):
            for idxs in combinations(target, r):
                s = sum(omega_sq[i] for i in idxs)
                out += ((-1) ** r) * CategoryFeature._positive_cube(x - s)
        return out

    @staticmethod
    def _pair_set(groups, category):
        g1, g2, diag = category
        a_set = tuple(groups[g1])
        b_set = tuple(groups[g2])
        if len(a_set) == 0 or len(b_set) == 0:
            return []

        if g1 == g2:
            if diag:
                return [(u, u) for u in a_set]
            return [(a_set[i], a_set[j]) for i in range(len(a_set)) for j in range(i + 1, len(a_set))]

        return [(u, v) for u in a_set for v in b_set]

    @staticmethod
    def _q(omega, groups, category):
        pairs = CategoryFeature._pair_set(groups, category)
        val = Fraction(0)
        for u, v in pairs:
            val += Fraction(omega[u]) * Fraction(omega[v])
        return val

    def _group_from_I(self, I, base_side):
        I_set = tuple(I)
        if base_side == "M":
            A = I_set
            C = tuple(i for i in (0, 1, 2) if i not in A)
            return {
                "A": A,
                "C": C,
                "R": (3, 4, 5),
            }
        if base_side == "P":
            A = tuple(i + 3 for i in I_set)
            C = tuple(i + 3 for i in (0, 1, 2) if i not in I_set)
            return {
                "A": A,
                "C": C,
                "R": (0, 1, 2),
            }
        raise ValueError("base side must be M or P")

    def eval(self, omega):
        omega = [Fraction(w) for w in omega]
        omega_sq = [w * w for w in omega]

        val = Fraction(0)

        for I_mask in common.iter_subsets(3, self.r, self.r):
            I = tuple(common.subset_bits(I_mask))

            m_groups = self._group_from_I(I, "M")
            q_M = self._q(omega, m_groups, self.category)
            val += self._b(omega_sq, I, (3, 4, 5)) * q_M

        for I_mask in common.iter_subsets(3, self.r, self.r):
            I_local = tuple(common.subset_bits(I_mask))
            I = tuple(i + 3 for i in I_local)
            swap_groups = self._group_from_I(I_local, "P")
            q_P = self._q(omega, swap_groups, self.category)
            val += self._b(omega_sq, I, (0, 1, 2)) * q_P

        return val


def _category_name(cat):
    a, b, diag = cat
    if a == b:
        return f"{a}_{b}_{'diag' if diag else 'off'}"
    return f"{a}_{b}"


def _to_frac(v):
    if isinstance(v, Fraction):
        return v
    return common.parse_fraction(v)


def build_features(max_r):
    features = []

    for r in (1, 2):
        if r > max_r:
            break

        for cat in GROUPS:
            feat = CategoryFeature(r, cat)
            if _feature_is_nonempty(2 if False else r, cat):
                # lightweight non-empty probe below handles true structural non-empty categories
                features.append(feat)

    # remove any accidental empties and dedupe category names deterministically
    seen = set()
    out = []
    for f in features:
        if f.name in seen:
            continue
        seen.add(f.name)
        out.append(f)
    return out


def _feature_is_nonempty(r, category):
    # structural existence check from combinatorics only
    for I_mask in common.iter_subsets(3, r, r):
        I = tuple(common.subset_bits(I_mask))
        base_groups = {"A": I, "C": tuple(i for i in (0, 1, 2) if i not in I), "R": (3, 4, 5)}
        if CategoryFeature._pair_set(base_groups, category):
            return True
    return False


def _load_samples(path):
    rows = []
    with path.open("r") as f:
        for ln in f:
            if ln.strip():
                rows.append(json.loads(ln))
    return rows


def _build_dataset(rows, features):
    X = []
    y = []
    meta = []
    for rec in rows:
        try:
            omega = [_to_frac(v) for v in rec["omega"]]
            val = _to_frac(rec["A_im"])
        except Exception:
            continue

        feats = [f.eval(omega) for f in features]
        if all(v == 0 for v in feats):
            continue

        X.append(feats)
        y.append(val)
        meta.append(
            {
                "sample_id": rec.get("sample_id"),
                "base_id": rec.get("base_id"),
                "wall_signature": rec.get("wall_signature"),
                "y": common.frac_to_str(val),
            }
        )

    return X, y, meta


def _matrix_rank(matrix):
    if not matrix:
        return 0

    a = [list(map(Fraction, row)) for row in matrix]
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
        pivot_val = a[row][col]
        a[row] = [x / pivot_val for x in a[row]]

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


def _matrix_rank_aug(matrix, rhs):
    if not matrix:
        return 0, 0

    a = [list(map(Fraction, row)) + [Fraction(rv)] for row, rv in zip(matrix, rhs)]
    m = len(a)
    n = len(a[0]) - 1

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
        pivot_val = a[row][col]
        a[row] = [x / pivot_val for x in a[row]]

        for rr in range(m):
            if rr == row:
                continue
            factor = a[rr][col]
            if factor == 0:
                continue
            a[rr] = [x - factor * y for x, y in zip(a[rr], a[row])]

        rank += 1
        row += 1
        col += 1

    rank_aug = 0
    for rr in range(m):
        if any(v != 0 for v in a[rr][:n]):
            rank_aug += 1
        elif a[rr][n] != 0:
            return rank, rank + 1

    return rank, rank_aug


def _find_first_inconsistent_prefix(X, y, meta):
    for k in range(1, len(X) + 1):
        rankA, rankAug = _matrix_rank_aug(X[:k], y[:k])
        if rankAug > rankA:
            row = meta[k - 1]
            return {
                "prefix_rows": k,
                "conflict_row": {
                    "sample_id": row.get("sample_id"),
                    "base_id": row.get("base_id"),
                    "wall_signature": row.get("wall_signature"),
                    "exact_y": row.get("y"),
                },
                "rankA": rankA,
                "rankAug": rankAug,
            }
    return None


def _solve_linear_exact(A, b):
    m = len(A)
    if m == 0:
        return [], {"status": "empty", "matrix_rank": 0, "matrix_rank_aug": 0}

    n = len(A[0])
    aug = [list(map(Fraction, row)) + [Fraction(b[i])] for i, row in enumerate(A)]
    row = 0
    pivots = [-1] * n

    for col in range(n):
        pivot_row = None
        for rr in range(row, m):
            if aug[rr][col] != 0:
                pivot_row = rr
                break
        if pivot_row is None:
            continue

        aug[row], aug[pivot_row] = aug[pivot_row], aug[row]
        inv_pivot = Fraction(1, 1) / aug[row][col]
        aug[row] = [x * inv_pivot for x in aug[row]]

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

    return coeffs, {"status": "ok", "matrix_rank": row}


def _residual_summary(vals):
    if not vals:
        return {"count": 0, "max_abs": "0", "mean_abs": "0"}

    mags = [abs(v) for v in vals]
    return {
        "count": len(mags),
        "max_abs": common.frac_to_str(max(mags)),
        "mean_abs": common.frac_to_str(sum(mags, Fraction(0)) / len(mags)),
    }


def _eval(coeffs, X, y):
    out = []
    for row, yy in zip(X, y):
        pred = sum(c * x for c, x in zip(coeffs, row))
        out.append(yy - pred)
    return out


def _row_test_split(X, y, meta):
    bases = []
    for item in meta:
        b = item.get("base_id")
        if b not in bases:
            bases.append(b)

    if not bases:
        return [], [], []

    n_train = max(1, int(0.75 * len(bases)))
    train_set = set(bases[:n_train])

    tr_idx = []
    te_idx = []
    for i, item in enumerate(meta):
        if item.get("base_id") in train_set:
            tr_idx.append(i)
        else:
            te_idx.append(i)

    return tr_idx, te_idx, bases


def _fit_with_split(rows, features):
    X, y, meta = _build_dataset(rows, features)
    tr_idx, te_idx, _ = _row_test_split(X, y, meta)

    Xtr = [X[i] for i in tr_idx]
    ytr = [y[i] for i in tr_idx]
    mtr = [meta[i] for i in tr_idx]
    Xte = [X[i] for i in te_idx]
    yte = [y[i] for i in te_idx]

    rankA, rankAug = _matrix_rank_aug(Xtr, ytr)
    coeffs, fit_meta = _solve_linear_exact(Xtr, ytr)

    if coeffs is None:
        return None, {
            "status": "inconsistent",
            "feature_names": [f.name for f in features],
            "feature_count": len(features),
            "train_count": len(tr_idx),
            "test_count": len(te_idx),
            "matrix_rank": rankA,
            "matrix_rank_aug": rankAug,
            "first_inconsistent_prefix": _find_first_inconsistent_prefix(Xtr, ytr, mtr),
            "fit_meta": fit_meta,
        }

    rtr = _eval(coeffs, Xtr, ytr)
    rte = _eval(coeffs, Xte, yte) if Xte else []

    return coeffs, {
        "status": "consistent",
        "feature_names": [f.name for f in features],
        "feature_count": len(features),
        "train_count": len(tr_idx),
        "test_count": len(te_idx),
        "matrix_rank": rankA,
        "matrix_rank_aug": rankAug,
        "train_residuals": _residual_summary(rtr),
        "test_residuals": _residual_summary(rte),
        "fit_meta": fit_meta,
    }


def _evaluate_wall_approaches(coeffs, features):
    wall_path = DATA_DIR / "wall_approaches.json"
    if not wall_path.exists():
        return {"status": "missing wall_approaches.json"}

    payload = json.loads(wall_path.read_text())
    out_rows = []
    for e in payload:
        rows = e.get("samples", [])
        evaluated = []
        for s in rows:
            try:
                omega = [_to_frac(x) for x in s["omega"]]
                y = _to_frac(s["A_im"])
                feats = [f.eval(omega) for f in features]
                pred = sum(ci * xi for ci, xi in zip(coeffs, feats))
                evaluated.append({"sample_id": s.get("sample_id"), "residual": common.frac_to_str(y - pred)})
            except Exception:
                continue
        out_rows.append({"orbit": e.get("orbit"), "found": e.get("found"), "rows": evaluated})
    return {"count": len(out_rows), "rows": out_rows}


def _run_individual_feature_invariance(rows, features, min_records=3):
    if len(rows) < min_records:
        return {
            "status": "skipped",
            "reason": "insufficient_records",
            "passed": False,
            "tested_records": [],
            "failures": [],
        }

    selected = []
    seen = set()
    for rec in rows:
        b = rec.get("base_id")
        if b in seen:
            continue
        selected.append(rec)
        seen.add(b)
        if len(selected) >= min_records:
            break

    perms = [tuple(p) for p in permutations(range(3))]
    failures = []

    for rec in selected:
        try:
            omega = [_to_frac(v) for v in rec["omega"]]
        except Exception:
            continue

        for f in features:
            base = f.eval(omega)
            for pm in perms:
                for pp in perms:
                    omega_perm = [
                        omega[pm[0]],
                        omega[pm[1]],
                        omega[pm[2]],
                        omega[3 + pp[0]],
                        omega[3 + pp[1]],
                        omega[3 + pp[2]],
                    ]
                    if f.eval(omega_perm) != base:
                        failures.append(
                            {
                                "record": rec.get("sample_id"),
                                "base_id": rec.get("base_id"),
                                "feature": f.name,
                                "transform": "perm",
                                "minus": list(pm),
                                "plus": list(pp),
                                "base": common.frac_to_str(base),
                                "transformed": common.frac_to_str(f.eval(omega_perm)),
                            }
                        )

                    omega_swap = [
                        omega[3 + pm[0]],
                        omega[3 + pm[1]],
                        omega[3 + pm[2]],
                        omega[pp[0]],
                        omega[pp[1]],
                        omega[pp[2]],
                    ]
                    if f.eval(omega_swap) != base:
                        failures.append(
                            {
                                "record": rec.get("sample_id"),
                                "base_id": rec.get("base_id"),
                                "feature": f.name,
                                "transform": "swap",
                                "minus": list(pm),
                                "plus": list(pp),
                                "base": common.frac_to_str(base),
                                "transformed": common.frac_to_str(f.eval(omega_swap)),
                            }
                        )

    return {
        "status": "passed" if len(failures) == 0 else "failed",
        "passed": len(failures) == 0,
        "tested_records": [r.get("sample_id") for r in selected],
        "failures": failures,
    }


def main():
    sample_path = DATA_DIR / "oracle_samples.jsonl"
    rows = _load_samples(sample_path)

    features_r1 = build_features(1)
    features_r12 = build_features(2)

    invariance = _run_individual_feature_invariance(rows, features_r12, min_records=3)

    report = {
        "basis_counts": {
            "r1": len(features_r1),
            "r1+r2": len(features_r12),
        },
        "invariance": invariance,
        "r1": {},
        "r1+r2": {},
    }

    for tag, feats in {"r1": features_r1, "r1+r2": features_r12}.items():
        if not invariance["passed"]:
            report[tag]["status"] = "skipped"
            report[tag]["feature_names"] = [f.name for f in feats]
            report[tag]["feature_count"] = len(feats)
            report[tag]["skip_reason"] = "feature_invariance_failed"
            continue

        coeffs, fit = _fit_with_split(rows, feats)
        entry = dict(fit)
        entry["status"] = fit.get("status")

        if coeffs is None:
            report[tag] = entry
            continue

        entry["coefficients"] = {f.name: common.frac_to_str(c) for f, c in zip(feats, coeffs) if c != 0}
        entry["wall_approach_eval"] = _evaluate_wall_approaches(coeffs, feats)
        report[tag] = entry

    (DATA_DIR / "h1_fit_report.json").write_text(json.dumps(report, indent=2))

    with (DATA_DIR / "h1_fit_report.txt").open("w") as f:
        f.write("r1 basis = %s\n" % report["basis_counts"]["r1"])
        f.write("r1+r2 basis = %s\n" % report["basis_counts"]["r1+r2"])
        f.write("r1 status=%s\n" % report["r1"].get("status"))
        f.write("r1+r2 status=%s\n" % report["r1+r2"].get("status"))
        f.write("r1+r2 rank=%s/%s\n" % (report["r1+r2"].get("matrix_rank"), report["r1+r2"].get("matrix_rank_aug")))
        f.write("invariance_passed=%s\n" % report["invariance"].get("passed"))


if __name__ == "__main__":
    main()
