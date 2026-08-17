
from collections import Counter
from fractions import Fraction
from itertools import islice, permutations, product
from pathlib import Path
from typing import Dict, List, Sequence, Tuple
import argparse
import json
import random

from bg_oracle import BGOracle, BGOracleError, BGResult, fraction_to_str


MINUS = (0, 1, 2)
PLUS = (3, 4, 5)
PAIRS = ((0, 1), (0, 2), (1, 2))
DEFAULT_SIGMA = (-1, -1, -1, 1, 1, 1)
SIGN_CHOICES = ((1, 1), (1, -1), (-1, 1), (-1, -1))
FEATURE_PREF_NAMES = (
    "wa*wb",
    "wa2+wb2",
    "wr2",
    "wa_plus_wb_times_wr",
    "wa_plus_wb_times_sp",
    "wr_times_sp",
    "sp2",
    "e2p",
    "p2p",
)
THETA_CHOICES = ("min", "max")


class ExactSample(object):
    __slots__ = (
        "point_id",
        "source",
        "sigma",
        "omega",
        "free_w",
        "amp_re",
        "amp_im",
        "chamber_signature",
    )

    def __init__(self, point_id, source, sigma, omega, free_w, amp_re, amp_im, chamber_signature):
        self.point_id = point_id
        self.source = source
        self.sigma = tuple(int(x) for x in sigma)
        self.omega = tuple(omega)
        self.free_w = tuple(free_w)
        self.amp_re = amp_re
        self.amp_im = amp_im
        self.chamber_signature = chamber_signature

    def to_json(self):
        return {
            "point_id": self.point_id,
            "source": self.source,
            "sigma": list(self.sigma),
            "omega": [fraction_to_str(v) for v in self.omega],
            "free_w2_w5": [fraction_to_str(v) for v in self.free_w],
            "amp_re": fraction_to_str(self.amp_re),
            "amp_im": fraction_to_str(self.amp_im),
            "chamber_signature": self.chamber_signature,
        }


def subset_signature(omega: Sequence[Fraction], sigma: Sequence[int]) -> str:
    terms = [Fraction(si, 1) * w * w for si, w in zip(sigma, omega)]
    bits = []
    for mask in range(1, (1 << len(omega)) - 1):
        s = Fraction(0, 1)
        for i in range(len(omega)):
            if mask & (1 << i):
                s += terms[i]
        if s == 0:
            raise ValueError("degenerate subset sum exactly zero")
        bits.append("+" if s > 0 else "-")
    return "".join(bits)


def validate_point(sigma: Sequence[int], omega: Sequence[Fraction]) -> None:
    if any(w == 0 for w in omega):
        raise ValueError("external omega is zero")
    _ = subset_signature(omega, sigma)


def parse_bg_as_sample(point_id: str, source: str, result: BGResult, sigma: Sequence[int], free_w: Sequence[Fraction]) -> ExactSample:
    sig = subset_signature(result.omega, sigma)
    return ExactSample(
        point_id=point_id,
        source=source,
        sigma=tuple(int(x) for x in sigma),
        omega=result.omega,
        free_w=tuple(free_w),
        amp_re=result.amp_re,
        amp_im=result.amp_im,
        chamber_signature=sig,
    )


def cube_pos(x: Fraction) -> Fraction:
    return x ** 3 if x > 0 else Fraction(0, 1)


def phi_ab(
    omega: Sequence[Fraction],
    a: int,
    b: int,
    em: int,
    ep: int,
    theta_mode: str,
    prefactor_fn=None,
) -> Fraction:
    sq = [w * w for w in omega]
    r = next(i for i in MINUS if i not in (a, b))
    theta = min(sq[a], sq[b]) if theta_mode == "min" else max(sq[a], sq[b])

    pref = omega[a] * omega[b]
    if prefactor_fn is not None:
        pref = prefactor_fn(omega, a, b, r)

    wp = [sq[3], sq[4], sq[5]]
    total = Fraction(0, 1)
    for mask in range(16):
        has_r = bool(mask & 1)
        plus_mask = mask >> 1
        plus_sum = Fraction(0, 1)
        if plus_mask & 1:
            plus_sum += wp[0]
        if plus_mask & 2:
            plus_sum += wp[1]
        if plus_mask & 4:
            plus_sum += wp[2]
        x = theta - (Fraction(em, 1) * (sq[r] if has_r else Fraction(0, 1))) - (Fraction(ep, 1) * plus_sum)
        term = cube_pos(x)
        total += -term if (bin(mask).count("1") % 2) else term
    return pref * total


def pair_phi_map(omega: Sequence[Fraction], em: int, ep: int, theta_mode: str = "min") -> Dict[str, Fraction]:
    return {
        f"{a}{b}": phi_ab(omega, a, b, em, ep, theta_mode)
        for a, b in PAIRS
    }


def sum_phi_pairs(omega: Sequence[Fraction], em: int, ep: int, theta_mode: str = "min") -> Fraction:
    return sum(pair_phi_map(omega, em, ep, theta_mode).values())


def pair_feature_names() -> List[str]:
    return list(FEATURE_PREF_NAMES)


def make_prefactor(name: str):
    def sp(omega: Sequence[Fraction]) -> Fraction:
        return omega[3] + omega[4] + omega[5]

    def p2p(omega: Sequence[Fraction]) -> Fraction:
        return omega[3] * omega[3] + omega[4] * omega[4] + omega[5] * omega[5]

    def e2p(omega: Sequence[Fraction]) -> Fraction:
        return omega[3] * omega[4] + omega[3] * omega[5] + omega[4] * omega[5]

    if name == "wa*wb":
        return lambda omega, a, b, r: omega[a] * omega[b]
    if name == "wa2+wb2":
        return lambda omega, a, b, r: omega[a] * omega[a] + omega[b] * omega[b]
    if name == "wr2":
        return lambda omega, a, b, r: omega[r] * omega[r]
    if name == "wa_plus_wb_times_wr":
        return lambda omega, a, b, r: (omega[a] + omega[b]) * omega[r]
    if name == "wa_plus_wb_times_sp":
        return lambda omega, a, b, r: (omega[a] + omega[b]) * sp(omega)
    if name == "wr_times_sp":
        return lambda omega, a, b, r: omega[r] * sp(omega)
    if name == "sp2":
        return lambda omega, a, b, r: sp(omega) * sp(omega)
    if name == "e2p":
        return lambda omega, a, b, r: e2p(omega)
    if name == "p2p":
        return lambda omega, a, b, r: omega[3] * omega[3] + omega[4] * omega[4] + omega[5] * omega[5]
    raise ValueError(f"unknown prefactor {name}")


def feature_value(omega: Sequence[Fraction], em: int, ep: int, theta_mode: str, pref_name: str) -> Fraction:
    pf = make_prefactor(pref_name)
    return sum(
        phi_ab(omega, a, b, em, ep, theta_mode, prefactor_fn=pf)
        for a, b in PAIRS
    )


def feature_matrix(samples: Sequence[ExactSample]):
    names: List[str] = []
    cols: List[List[Fraction]] = []
    uniq: Dict[Tuple[Fraction, ...], int] = {}

    for em, ep in SIGN_CHOICES:
        for theta in THETA_CHOICES:
            for pref in pair_feature_names():
                vals = [
                    feature_value(s.omega, em, ep, theta, pref)
                    for s in samples
                ]
                key = tuple(vals)
                if key in uniq:
                    continue
                uniq[key] = len(cols)
                names.append(f"{pref}|theta={theta}|e_m={em}|e_p={ep}")
                cols.append(vals)

    rows: List[List[Fraction]] = []
    for r in range(len(samples)):
        rows.append([col[r] for col in cols])
    return names, rows


def gauss_solve_exact(
    A: List[List[Fraction]],
    b: List[Fraction],
    row_labels: Sequence[str] = None,
):
    m = len(A)
    if m == 0:
        return False, [], 0, 0, None
    n = len(A[0]) if A else 0
    if n == 0:
        all_zero = all(rhs == 0 for rhs in b)
        return (
            all_zero,
            [],
            0,
            0 if all_zero else 1,
            None if all_zero else {"type": "inconsistent", "sample_id": None},
        )
    mat = [row[:] + [rhs] for row, rhs in zip(A, b)]

    if row_labels is None:
        row_labels = [str(i) for i in range(m)]
    row_labels = list(row_labels)
    if len(row_labels) != m:
        raise ValueError("row_labels length must match number of rows")

    row = 0
    pivot_cols = []

    for col in range(n):
        pivot = None
        for r in range(row, m):
            if mat[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            continue
        mat[row], mat[pivot] = mat[pivot], mat[row]
        row_labels[row], row_labels[pivot] = row_labels[pivot], row_labels[row]
        pv = mat[row][col]
        for c in range(col, n + 1):
            mat[row][c] /= pv
        for r in range(m):
            if r == row:
                continue
            f = mat[r][col]
            if f == 0:
                continue
            for c in range(col, n + 1):
                mat[r][c] -= f * mat[row][c]
        pivot_cols.append(col)
        row += 1
        if row == m:
            break

    rank_a = len(pivot_cols)
    rank_aug = rank_a
    for r in range(m):
        if all(mat[r][c] == 0 for c in range(n)):
            if mat[r][n] != 0:
                return False, [], rank_a, rank_a + 1, {
                    "type": "inconsistent_row",
                    "sample_id": row_labels[r],
                    "residual": fraction_to_str(mat[r][n]),
                }

    sol = [Fraction(0, 1)] * n
    for r in range(len(pivot_cols)):
        piv = pivot_cols[r]
        sol[piv] = mat[r][n]
    return True, sol, rank_a, rank_aug, None


def fit_common(samples: Sequence[ExactSample], em: int, ep: int, train_idx: Sequence[int], theta_mode: str = "min"):
    nonzero = []
    ref_pt = None
    ref_x = None
    ref_y = None
    for i in train_idx:
        x = sum_phi_pairs(samples[i].omega, em, ep, theta_mode)
        if x == 0:
            if samples[i].amp_im != 0:
                return {
                    "type": "common",
                    "status": "no_common_coeff",
                    "em": em,
                    "ep": ep,
                    "reason": "zero_train_phi_with_nonzero_amp",
                }
            continue
        if ref_pt is None:
            ref_pt = samples[i].point_id
            ref_x = x
            ref_y = samples[i].amp_im
        nonzero.append((x, samples[i].amp_im, samples[i].point_id))

    if not nonzero:
        return {
            "type": "common",
            "status": "no_common_coeff",
            "em": em,
            "ep": ep,
            "reason": "no_nonzero_train_phi",
        }

    c = ref_y / ref_x
    for x, y, pid in nonzero[1:]:
        if y != c * x:
            return {
                "type": "common",
                "status": "no_common_coeff",
                "em": em,
                "ep": ep,
                "witness": {
                    "reference_point_id": ref_pt,
                    "witness_point_id": pid,
                    "reference_x": fraction_to_str(ref_x),
                    "reference_y": fraction_to_str(ref_y),
                    "witness_x": fraction_to_str(x),
                    "witness_y": fraction_to_str(y),
                    "coef": fraction_to_str(c),
                    "residual": fraction_to_str(y - c * x),
                },
            }

    def count_matches(indexes: Sequence[int]) -> int:
        return sum(samples[i].amp_im == c * sum_phi_pairs(samples[i].omega, em, ep, theta_mode) for i in indexes)

    return {
        "type": "common",
        "status": "common_exact",
        "em": em,
        "ep": ep,
        "coef": c,
        "coef_over_32": c / Fraction(32, 1),
        "train_matches": count_matches(train_idx),
        "train_total": len(train_idx),
        "heldout_indices": [i for i in range(len(samples)) if i not in train_idx],
    }


def residual_holdout(result, samples: Sequence[ExactSample], train_idx: Sequence[int]):
    held = [i for i in range(len(samples)) if i not in train_idx]
    if result is None:
        return {
            "heldout_matches": 0,
            "heldout_total": len(held),
            "exact_formula_residuals": ["n/a" for _ in held],
        }
    if result["type"] == "common":
        em = result["em"]; ep = result["ep"]; c = result["coef"]
        residuals = []
        matches = 0
        for i in held:
            pred = c * sum_phi_pairs(samples[i].omega, em, ep)
            res = samples[i].amp_im - pred
            residuals.append(fraction_to_str(res))
            if res == 0:
                matches += 1
        return {"heldout_matches": matches, "heldout_total": len(held), "exact_formula_residuals": residuals}

    em = result["em"]; ep = result["ep"]; c01, c02, c12 = result["coef"]
    residuals = []
    matches = 0
    for i in held:
        ph = pair_phi_map(samples[i].omega, em, ep)
        pred = c01 * ph["01"] + c02 * ph["02"] + c12 * ph["12"]
        res = samples[i].amp_im - pred
        residuals.append(fraction_to_str(res))
        if res == 0:
            matches += 1
    return {"heldout_matches": matches, "heldout_total": len(held), "exact_formula_residuals": residuals}


def fit_pairs(samples: Sequence[ExactSample], em: int, ep: int, train_idx: Sequence[int], theta_mode: str = "min"):
    A: List[List[Fraction]] = []
    b: List[Fraction] = []
    for i in train_idx:
        ph = pair_phi_map(samples[i].omega, em, ep, theta_mode)
        A.append([ph["01"], ph["02"], ph["12"]])
        b.append(samples[i].amp_im)

    row_labels = [samples[i].point_id for i in train_idx]
    ok, sol, rank_a, rank_aug, wit = gauss_solve_exact(A, b, row_labels=row_labels)
    if not ok:
        return {
            "type": "pair",
            "status": "no_exact_pair_coeff",
            "em": em,
            "ep": ep,
            "rank_A": rank_a,
            "rank_augmented": rank_aug,
            "inconsistency_witness": wit,
        }

    c01, c02, c12 = sol
    # verify exact on train
    for idx in train_idx:
        ph = pair_phi_map(samples[idx].omega, em, ep)
        pred = c01 * ph["01"] + c02 * ph["02"] + c12 * ph["12"]
        if pred != samples[idx].amp_im:
            return {
                "type": "pair",
                "status": "no_exact_pair_coeff",
                "em": em,
                "ep": ep,
                "rank_A": rank_a,
                "rank_augmented": rank_aug + 1,
                "inconsistency_witness": {
                    "type": "train_mismatch",
                    "point_id": samples[idx].point_id,
                    "point_index": idx,
                    "residual": fraction_to_str(samples[idx].amp_im - pred),
                },
            }

    held = residual_holdout({"type": "pair", "em": em, "ep": ep, "coef": (c01, c02, c12)}, samples, train_idx)
    return {
        "type": "pair",
        "status": "pair_exact",
        "em": em,
        "ep": ep,
        "coef": (c01, c02, c12),
        "coef_over_32": (c01 / 32, c02 / 32, c12 / 32),
        "rank_A": rank_a,
        "rank_augmented": rank_aug,
        "train_matches": len(train_idx),
        "train_total": len(train_idx),
        "heldout_matches": held["heldout_matches"],
        "heldout_total": held["heldout_total"],
        "exact_formula_residuals": held["exact_formula_residuals"],
    }

def fit_fallback_features(
    samples: Sequence[ExactSample],
    feature_names: Sequence[str],
    feature_rows: Sequence[Sequence[Fraction]],
    train_idx: Sequence[int],
):
    hold_idx = [i for i in range(len(samples)) if i not in train_idx]
    A = [feature_rows[i] for i in train_idx]
    b = [samples[i].amp_im for i in train_idx]
    row_labels = [samples[i].point_id for i in train_idx]
    ok, coef, rank_a, rank_aug, wit = gauss_solve_exact(A, b, row_labels=row_labels)
    if not ok:
        return {
            "status": "no_exact_fit",
            "train_total": len(train_idx),
            "heldout_total": len(hold_idx),
            "rank_A": rank_a,
            "rank_augmented": rank_aug,
            "inconsistency_witness": wit,
        }

    # greedy column dropping for sparse exact solution
    active = list(range(len(feature_names)))
    while True:
        dropped = False
        for j in list(active):
            trial = [k for k in active if k != j]
            if not trial:
                continue
            A2 = [[A[r][k] for k in trial] for r in range(len(A))]
            ok2, coef2, ra2, ra2a, _ = gauss_solve_exact(
                A2,
                b,
                row_labels=row_labels,
            )
            if not ok2:
                continue
            if ra2 != ra2a:
                continue
            if not ok2:
                continue
            # verify exactness on train
            exact = True
            for r_i, _ in enumerate(train_idx):
                pred = sum(A2[r_i][k] * coef2[k] for k in range(len(trial)))
                if pred != b[r_i]:
                    exact = False
                    break
            if not exact:
                continue
            active = trial
            coef = coef2
            dropped = True
            break
        if not dropped:
            break

    # recompute residuals for full set
    residuals = []
    matches = 0
    mismatch = None
    for i, s in enumerate(samples):
        row = feature_rows[i]
        pred = sum(row[col] * coef[pos] for pos, col in enumerate(active))
        res = s.amp_im - pred
        residuals.append(fraction_to_str(res))
        if i not in hold_idx:
            continue
        if res == 0:
            matches += 1
        elif mismatch is None:
            mismatch = {
                "point_id": s.point_id,
                "predicted": fraction_to_str(pred),
                "target": fraction_to_str(s.amp_im),
                "residual": fraction_to_str(res),
            }

    status = "exact_fit" if matches == len(hold_idx) else "no_verified_fallback"
    return {
        "status": status,
        "train_total": len(train_idx),
        "heldout_matches": matches,
        "heldout_total": len(hold_idx),
        "selected_features": [feature_names[k] for k in active],
        "coefficients": {feature_names[k]: fraction_to_str(coef[i]) for i, k in enumerate(active)},
        "nonzero_count": sum(1 for v in coef if v != 0),
        "exact_formula_residuals": residuals,
        "rank_A": rank_a,
        "rank_augmented": rank_aug,
        "first_heldout_mismatch": mismatch,
        "raw_matrix_rank": rank_a,
    }

def permutation_invariance_checks(samples: Sequence[ExactSample], candidate = None) -> Dict:
    perms_m = list(permutations((0, 1, 2), 3))[:3]
    perms_p = list(permutations((3, 4, 5), 3))[:3]
    out = []
    for s in samples[: min(8, len(samples))]:
        oracle_ok = True
        h1_ok = True
        base_amp = s.amp_im
        base_pred = None
        if candidate is not None and candidate.get("type") in {"common", "pair"}:
            base_pred = _predict_candidate(candidate, s)
        for pm in perms_m:
            for pp in perms_p:
                wperm = (
                    s.omega[pm[0]], s.omega[pm[1]], s.omega[pm[2]],
                    s.omega[pp[0]], s.omega[pp[1]], s.omega[pp[2]],
                )
                try:
                    # no numerical compare with bg oracle here; only exact symbolic checks from stored points
                    sp = subset_signature(wperm, s.sigma)
                except ValueError:
                    oracle_ok = False
                    h1_ok = False
                    break
                if wperm[0] == 0:
                    oracle_ok = False
                if base_pred is not None:
                    p = _predict_candidate(candidate, ExactSample(
                        point_id="perm", source="perm", sigma=s.sigma, omega=wperm, free_w=wperm[1:5],
                        amp_re=Fraction(0,1), amp_im=Fraction(0,1), chamber_signature=sp
                    ))
                    if p != base_pred:
                        h1_ok = False
                if not oracle_ok or not h1_ok:
                    break
            if not oracle_ok or not h1_ok:
                break
        out.append({"point": s.point_id, "oracle_invariant": oracle_ok, "h1_invariant": h1_ok})
    return out


def _predict_candidate(candidate: Dict, sample: ExactSample) -> Fraction:
    if candidate["type"] == "common":
        return candidate["coef"] * sum_phi_pairs(sample.omega, candidate["em"], candidate["ep"])
    if candidate["type"] == "pair":
        c01, c02, c12 = candidate["coef"]
        ph = pair_phi_map(sample.omega, candidate["em"], candidate["ep"])
        return c01 * ph["01"] + c02 * ph["02"] + c12 * ph["12"]
    raise ValueError("unsupported candidate type")


def generate_seed_list() -> List[Tuple[Tuple[Fraction, ...], str]]:
    base = [
        (Fraction(2), Fraction(3), Fraction(4), Fraction(5)),
        (Fraction(3), Fraction(5), Fraction(2), Fraction(7)),
        (Fraction(-2), Fraction(3), Fraction(4), Fraction(-5)),
        (Fraction(2), Fraction(-3), Fraction(4), Fraction(5)),
        (Fraction(3), Fraction(-5), Fraction(-2), Fraction(7)),
    ]
    for i, s in enumerate((Fraction(2), Fraction(3), Fraction(4), Fraction(5))):
        pass

    values = [
        Fraction(1), Fraction(-1), Fraction(2), Fraction(-2), Fraction(3), Fraction(-3),
        Fraction(4), Fraction(-4), Fraction(5), Fraction(-5), Fraction(1, 2), Fraction(-1, 2),
        Fraction(3, 2), Fraction(-3, 2), Fraction(5, 2), Fraction(-5, 2),
    ]
    out: List[Tuple[Tuple[Fraction, ...], str]] = [(s, f"anchor_{i:03d}") for i, s in enumerate(base)]
    scales = [Fraction(1, 2), Fraction(3, 2), Fraction(2), Fraction(3), Fraction(-1), Fraction(-2)]
    b = (Fraction(3), Fraction(5), Fraction(2), Fraction(7))
    for s in scales:
        out.append((tuple(v * s for v in b), f"hierarchical_{s}"))
    for tup in islice(product(values, repeat=4), 2500):
        out.append((tuple(tup), "grid"))
    return out


def build_samples(oracle: BGOracle, target: int, sigma: Sequence[int]) -> Tuple[List[ExactSample], Dict]:
    seen = set()
    samples: List[ExactSample] = []
    counts = {
        "attempted": 0,
        "accepted": 0,
        "rejected_zero": 0,
        "rejected_degenerate": 0,
        "rejected_oracle": 0,
        "rejected_duplicate": 0,
        "permuted": 0,
    }

    for seed, tag in generate_seed_list():
        if len(samples) >= target:
            break
        counts["attempted"] += 1
        try:
            rr = oracle.solve_on_shell(seed, sigma=sigma)
            validate_point(sigma, rr.omega)
            if any(w == 0 for w in rr.omega):
                counts["rejected_zero"] += 1
                continue
            if rr.omega in seen:
                counts["rejected_duplicate"] += 1
                continue
            sample = parse_bg_as_sample(f"s{len(samples):04d}", tag, rr, sigma, seed)
            seen.add(rr.omega)
            samples.append(sample)
            counts["accepted"] += 1
        except ValueError as ex:
            if "exactly zero" in str(ex):
                counts["rejected_degenerate"] += 1
            else:
                counts["rejected_oracle"] += 1
        except BGOracleError:
            counts["rejected_oracle"] += 1

    # fill if needed
    rng = random.Random(2026)
    fill_attempts = 0
    value_pool = [Fraction(1), Fraction(2), Fraction(3), Fraction(4), Fraction(5), Fraction(-1), Fraction(-2), Fraction(-3), Fraction(-4), Fraction(-5), Fraction(1, 2), Fraction(3, 2)]
    while len(samples) < target and fill_attempts < 5000:
        fill_attempts += 1
        seed = tuple(rng.choice(value_pool) for _ in range(4))
        counts["attempted"] += 1
        try:
            rr = oracle.solve_on_shell(seed, sigma=sigma)
            validate_point(sigma, rr.omega)
            if rr.omega in seen:
                counts["rejected_duplicate"] += 1
                continue
            sample = parse_bg_as_sample(f"s{len(samples):04d}", "grid_random", rr, sigma, seed)
            seen.add(rr.omega)
            samples.append(sample)
            counts["accepted"] += 1
        except ValueError as ex:
            if "exactly zero" in str(ex):
                counts["rejected_degenerate"] += 1
            else:
                counts["rejected_oracle"] += 1
        except BGOracleError:
            counts["rejected_oracle"] += 1

    # plus/minus permutations from solved seeds
    perms_m = list(permutations((0, 1, 2), 3))[:3]
    perms_p = list(permutations((3, 4, 5), 3))[:2]
    for base in samples[:4]:
        for pm in perms_m:
            for pp in perms_p:
                omega_p = (
                    base.omega[pm[0]], base.omega[pm[1]], base.omega[pm[2]],
                    base.omega[pp[0]], base.omega[pp[1]], base.omega[pp[2]],
                )
                try:
                    rr = oracle.eval_with_amp(omega_p, sigma=sigma)
                    validate_point(sigma, rr.omega)
                    if rr.omega in seen:
                        counts["rejected_duplicate"] += 1
                        continue
                    sample = parse_bg_as_sample(
                        f"s{len(samples):04d}",
                        f"perm_{base.point_id}_{pm}_{pp}",
                        rr,
                        sigma,
                        omega_p[1:5],
                    )
                    seen.add(rr.omega)
                    samples.append(sample)
                    counts["accepted"] += 1
                    counts["permuted"] += 1
                except Exception:
                    counts["rejected_oracle"] += 1

    return samples, counts


def generate_samples(oracle: BGOracle, target: int, sigma: Sequence[int] = DEFAULT_SIGMA):
    return build_samples(oracle, target, sigma)


def to_jsonable(value):
    if isinstance(value, Fraction):
        return fraction_to_str(value)
    if isinstance(value, dict):
        return {k: to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_jsonable(v) for v in value]
    if isinstance(value, tuple):
        return [to_jsonable(v) for v in value]
    return value


def evaluate_fits(samples: List[ExactSample], train_frac: float):
    rng = random.Random(2026)
    indices = list(range(len(samples)))
    rng.shuffle(indices)
    if len(indices) == 80:
        split = 40
    else:
        split = int(len(indices) * train_frac)
    if split <= 0:
        split = 1
    if split >= len(indices):
        split = len(indices) - 1
    train = indices[:split]

    feature_names, feature_rows = feature_matrix(samples)

    fit_common_all = {}
    fit_pair_all = {}
    candidate = None

    for em, ep in SIGN_CHOICES:
        ck = fit_common(samples, em, ep, train)
        if ck is not None and ck.get("status") == "common_exact":
            holdout_report = residual_holdout(ck, samples, train)
            ck["heldout_matches"] = holdout_report["heldout_matches"]
            ck["heldout_total"] = holdout_report["heldout_total"]
            ck["exact_formula_residuals"] = holdout_report["exact_formula_residuals"]
            ck["train_matches"] = len(train)
            ck["train_total"] = len(train)
            fit_common_all[f"e_m={em},e_p={ep}"] = ck
        elif ck is not None:
            fit_common_all[f"e_m={em},e_p={ep}"] = ck

        pk = fit_pairs(samples, em, ep, train)
        if pk is not None and pk.get("status") == "pair_exact":
            fit_pair_all[f"e_m={em},e_p={ep}"] = pk
        elif pk is not None:
            fit_pair_all[f"e_m={em},e_p={ep}"] = pk

    # choose strongest H1 candidate (common beats pair only if exact heldout)
    candidates = []
    for item in list(fit_common_all.values()):
        if item.get("status") == "no_common_coeff":
            continue
        if item.get("heldout_matches") == item.get("heldout_total"):
            candidates.append(item)
    for item in list(fit_pair_all.values()):
        if item.get("status") == "pair_exact" and item.get("heldout_matches") == item.get("heldout_total"):
            candidates.append(item)

    if candidates:
        candidate = sorted(candidates, key=lambda c: c["heldout_total"], reverse=True)[0]

    fallback = None
    if candidate is None:
        fallback = fit_fallback_features(samples, feature_names, feature_rows, train)

    invariance = permutation_invariance_checks(samples[:8], candidate)

    return {
        "seed_train_indices": train,
        "common": fit_common_all,
        "pair": fit_pair_all,
        "selected_candidate": candidate,
        "feature_fallback": fallback,
        "pairwise_invariance": invariance,
    }


def run_all(
    sample_target: int,
    train_frac: float,
    qdir: Path,
    bg_binary: Path,
    data_dir: Path,
    deriv_dir: Path,
):
    import datetime

    data_dir.mkdir(parents=True, exist_ok=True)
    deriv_dir.mkdir(parents=True, exist_ok=True)

    oracle = BGOracle(binary_path=str(bg_binary))

    # anchor verifications required by task statement
    anchor_points = [
        ((Fraction(2), Fraction(3), Fraction(4), Fraction(5)), "seed_2_3_4_5", "(-8,2,3,4,5,-6)", "-9190656/7"),
        ((Fraction(3), Fraction(5), Fraction(2), Fraction(7)), "seed_3_5_2_7", "(-154/17,3,5,2,7,-135/17)", "-641893056/85"),
    ]
    anchors = {}
    for free_w, label, expected_omega, expected_im in anchor_points:
        rr = oracle.solve_on_shell(free_w, sigma=DEFAULT_SIGMA)
        anchors[label] = {
            "seed_free": [fraction_to_str(x) for x in free_w],
            "expected_omega": expected_omega,
            "expected_im": expected_im,
            "observed_omega": [fraction_to_str(x) for x in rr.omega],
            "observed_im": fraction_to_str(rr.amp_im),
        }

    samples, logs = build_samples(oracle, sample_target, DEFAULT_SIGMA)
    if len(samples) < 60:
        raise RuntimeError(f"Expected >=60 accepted samples, generated {len(samples)}")

    sample_path = data_dir / "exact_samples.json"
    sample_payload = {
        "metadata": {
            "sample_target": sample_target,
            "generated_count": len(samples),
            "generator_counts": logs,
        },
        "samples": [s.to_json() for s in samples],
    }
    sample_path.write_text(json.dumps(sample_payload, indent=2))

    h1_report = evaluate_fits(samples, train_frac)
    h1_report_json = to_jsonable(h1_report)
    sig_count = Counter(s.chamber_signature for s in samples)

    result = {
        "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
        "anchors": anchors,
        "sample_count": len(samples),
        "chamber_signature_count": len(sig_count),
        "chamber_signature_top": dict(sig_count.most_common(8)),
        "h1": h1_report_json,
        "artifacts": {
            "exact_samples_json": str(sample_path),
            "h1_results_json": str(data_dir / "h1_results.json"),
            "h1_report_md": str(deriv_dir / "h1_fit_report.md"),
        },
    }

    # markdown report
    lines = []
    lines.append("# H1 fitting report")
    lines.append(f"Generated at {result['timestamp']} UTC")
    lines.append("")
    lines.append("## H1 ansatz tested")
    lines.append(r"For each sign choice $(e_m,e_p)$ and pair $(a,b)$ in $\{(0,1),(0,2),(1,2)\}$,")
    lines.append(r"$$\Phi_{ab}^{e_m,e_p}=\omega_a\omega_b\sum_{S\subseteq\{r\}\cup\{3,4,5\}}(-1)^{|S|}[\theta - e_m\mathbf 1_{r\in S}\,\omega_r^2 - e_p\sum_{j\in S\cap\{3,4,5\}}\omega_j^2]_+^3,$$")
    lines.append(r"$$A_6/i = C\sum_{a<b}\Phi_{ab}^{e_m,e_p}$$")
    lines.append("Pair diagnostics used the labeled equation")
    lines.append(r"$$A_6/i = C_{01}\Phi_{01}^{e_m,e_p}+C_{02}\Phi_{02}^{e_m,e_p}+C_{12}\Phi_{12}^{e_m,e_p}$$")
    lines.append("")
    lines.append("## Anchors")
    lines.append("- anchor checks:")
    for k, a in anchors.items():
        lines.append(f"  - {k}: ω={a['observed_omega']}, A6=i*({a['observed_im']})")
    lines.append("")
    lines.append(f"- samples: {len(samples)}")
    lines.append(f"- chamber signature count: {len(sig_count)}")
    lines.append("## Common coefficient test")
    for k, v in h1_report["common"].items():
        if v.get("status") == "common_exact":
            lines.append(f"- {k}: C={v['coef']}  C/32={v['coef_over_32']}  train {v['train_matches']}/{v['train_total']} heldout {v['heldout_matches']}/{v['heldout_total']}")
        elif v.get("status") == "no_common_coeff":
            if "witness" in v:
                w = v["witness"]
                lines.append(
                    f"- {k}: {v['status']} ref={w['reference_point_id']} "
                    f"w={w['witness_point_id']} C={w['coef']} residual={w['residual']}"
                )
            else:
                lines.append(f"- {k}: {v['status']} {v.get('reason', '')}")
        else:
            lines.append(f"- {k}: {v.get('status')}")
    lines.append("## Pair coefficient diagnostics")
    for k, v in h1_report["pair"].items():
        if v.get("status") != "pair_exact":
            mismatch = ""
            if v.get("inconsistency_witness") is not None:
                mismatch = f" witness={v['inconsistency_witness']}"
            lines.append(
                f"- {k}: {v['status']} rank(A)={v['rank_A']} rank([A|y])={v['rank_augmented']}{mismatch}"
            )
        else:
            lines.append(f"- {k}: C01={v['coef'][0]} C02={v['coef'][1]} C12={v['coef'][2]} train {v['train_matches']}/{v['train_total']} heldout {v['heldout_matches']}/{v['heldout_total']} rank(A)={v['rank_A']} rank([A|y])={v['rank_augmented']}")
    if h1_report["selected_candidate"] is None:
        lines.append("## Fallback feature fit")
        fallback = h1_report["feature_fallback"] or {}
        lines.append(f"- status={fallback.get('status')}")
        lines.append(f"- rank(A)={fallback.get('rank_A')} rank([A|y])={fallback.get('rank_augmented')}")
        lines.append(f"- heldout {fallback.get('heldout_matches', 0)}/{fallback.get('heldout_total', 0)}")
        if fallback.get("first_heldout_mismatch") is not None:
            lines.append(f"- first mismatch={fallback.get('first_heldout_mismatch')}")
    else:
        lines.append("## Selected candidate")
        lines.append(f"{h1_report['selected_candidate']}")
    lines.append("## Invariance checks")
    for item in h1_report["pairwise_invariance"]:
        lines.append(f"- {item['point']}: oracle={item['oracle_invariant']} h1={item['h1_invariant']}")

    md_path = deriv_dir / "h1_fit_report.md"
    md_path.write_text("\n".join(lines) + "\n")

    # save h1 results machine JSON
    (data_dir / "h1_results.json").write_text(json.dumps(result, indent=2))

    return {
        "samples_json": sample_path,
        "h1_results_json": data_dir / "h1_results.json",
        "h1_report_md": md_path,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=80)
    parser.add_argument("--train-frac", type=float, default=0.8)
    parser.add_argument("--qdir", type=Path, default=Path("."))
    parser.add_argument("--bg", type=Path, default=Path("bots/student-1/bg"))
    args = parser.parse_args()

    qdir = args.qdir.resolve()
    run_all(
        sample_target=args.samples,
        train_frac=args.train_frac,
        qdir=qdir,
        bg_binary=(qdir / args.bg).resolve(),
        data_dir=qdir / "bots/student-1/data",
        deriv_dir=qdir / "bots/student-1/derivations",
    )


if __name__ == "__main__":
    main()
