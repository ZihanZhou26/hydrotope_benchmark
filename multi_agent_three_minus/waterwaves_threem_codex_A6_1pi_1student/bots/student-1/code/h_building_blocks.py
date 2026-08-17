#!/usr/bin/env python3
"""Orbit basis generation and exact fit helper for `h_rational_probe.py`."""

from fractions import Fraction
from itertools import permutations
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import sympy as sp

# Group variables:
# a0,a1,a2 are minus-sector squares; b0,b1,b2 are plus-sector squares.
GroupAction = Tuple[Tuple[int, int, int], Tuple[int, int, int], bool]


def _all_group_actions() -> List[GroupAction]:
    out: List[GroupAction] = []
    for p_m in permutations((0, 1, 2)):
        for p_b in permutations((0, 1, 2)):
            for swap in (False, True):
                out.append((p_m, p_b, swap))
    return out


_ACTIONS: List[GroupAction] = _all_group_actions()


class Term:
    __slots__ = ("kind", "exp", "i", "j", "diff_swapped")

    kind: str  # "base", "D", "S"
    exp: Tuple[int, int, int, int, int, int]
    i: int = -1
    j: int = -1
    diff_swapped: bool = False

    def __init__(self, kind, exp, i=-1, j=-1, diff_swapped=False):
        self.kind = kind
        self.exp = exp
        self.i = i
        self.j = j
        self.diff_swapped = diff_swapped

    def key(self) -> Tuple[str, Tuple[int, int, int, int, int, int], int, int, bool]:
        return (self.kind, self.exp, self.i, self.j, self.diff_swapped)


def _permute_exp(exp: Tuple[int, int, int, int, int, int], action: GroupAction) -> Tuple[int, int, int, int, int, int]:
    p_m, p_b, swap = action
    out = [0] * 6
    for idx, e in enumerate(exp):
        if not swap:
            ni = p_m[idx] if idx < 3 else 3 + p_b[idx - 3]
        else:
            ni = 3 + p_m[idx] if idx < 3 else p_b[idx - 3]
        out[ni] = e
    return tuple(out)


def _transform_wall(i: int, j: int, diff_swapped: bool, action: GroupAction) -> Tuple[int, int, bool]:
    p_m, p_b, swap = action
    if not swap:
        return p_m[i], p_b[j], diff_swapped
    return p_b[j], p_m[i], not diff_swapped


def monomials_degree(d: int, nvar: int = 6) -> List[Tuple[int, ...]]:
    out: List[Tuple[int, ...]] = []
    exps = [0] * nvar

    def rec(pos: int, rem: int) -> None:
        if pos == nvar:
            if rem == 0:
                out.append(tuple(exps))
            return
        if pos == nvar - 1:
            exps[pos] = rem
            out.append(tuple(exps))
            return
        for e in range(rem + 1):
            exps[pos] = e
            rec(pos + 1, rem - e)

    rec(0, d)
    return out


def _orbit_terms_base(seed: Tuple[int, int, int, int, int, int]) -> List[Tuple[int, int, int, int, int, int]]:
    return sorted({_permute_exp(seed, action) for action in _ACTIONS})


def _orbit_terms_wall(
    seed: Tuple[int, int, int, int, int, int],
    kind: str,
    i: int,
    j: int,
    diff_swapped: bool,
) -> List[Term]:
    terms: List[Term] = []
    for action in _ACTIONS:
        ni, nj, nw = _transform_wall(i, j, diff_swapped, action)
        terms.append(Term(kind=kind, exp=_permute_exp(seed, action), i=ni, j=nj, diff_swapped=nw))

    uniq: Dict[Tuple[str, Tuple[int, int, int, int, int, int], int, int, bool], Term] = {}
    for t in terms:
        uniq[t.key()] = t
    return sorted(uniq.values(), key=lambda t: (t.kind, t.i, t.j, t.exp, t.diff_swapped))


def _positive(v: Fraction) -> Fraction:
    return v if v > 0 else Fraction(0, 1)


def _eval_monom(exp: Sequence[int], a: Sequence[Fraction], b: Sequence[Fraction]) -> Fraction:
    vals = list(a) + list(b)
    out = Fraction(1, 1)
    for idx, e in enumerate(exp):
        if e:
            out *= vals[idx] ** e
    return out


def _eval_monomial(omega: Sequence[Fraction], exp: Sequence[int]) -> Fraction:
    out = Fraction(1, 1)
    for v, e in zip(omega, exp):
        if e:
            out *= v ** e
    return out


def build_features(degree: int) -> List[Dict]:
    features: List[Dict] = []
    if degree % 2 != 0:
        return features

    half = degree // 2
    seen = set()

    for exp in monomials_degree(half, 6):
        orbit = tuple(_orbit_terms_base(exp))
        if orbit in seen:
            continue
        seen.add(orbit)
        features.append({"kind": "base", "terms": [tuple(e) for e in orbit]})

    if half >= 1:
        for exp in monomials_degree(half - 1, 6):
            for i in range(3):
                for j in range(3):
                    orbit = _orbit_terms_wall(exp, "D", i, j, False)
                    key = ("D", tuple(t.key() for t in orbit))
                    if key in seen:
                        continue
                    seen.add(key)
                    features.append({
                        "kind": "D",
                        "terms": [
                            {
                                "exp": t.exp,
                                "i": t.i,
                                "j": t.j,
                                "diff_swapped": t.diff_swapped,
                            }
                            for t in orbit
                        ],
                    })

    if half >= 3:
        for exp in monomials_degree(half - 3, 6):
            for i in range(3):
                for j in range(3):
                    orbit = _orbit_terms_wall(exp, "S", i, j, False)
                    key = ("S", tuple(t.key() for t in orbit))
                    if key in seen:
                        continue
                    seen.add(key)
                    features.append({
                        "kind": "S",
                        "terms": [
                            {
                                "exp": t.exp,
                                "i": t.i,
                                "j": t.j,
                                "diff_swapped": t.diff_swapped,
                            }
                            for t in orbit
                        ],
                    })

    return features


def _eval_feature(feature: Dict, omega: Sequence[Fraction]) -> Fraction:
    a = [omega[0] ** 2, omega[1] ** 2, omega[2] ** 2]
    b = [omega[3] ** 2, omega[4] ** 2, omega[5] ** 2]
    T = a[0] + a[1] + a[2]

    if feature["kind"] == "base":
        total = Fraction(0, 1)
        for exp in feature["terms"]:
            total += _eval_monom(exp, a, b)
        return total

    total = Fraction(0, 1)
    for term in feature["terms"]:
        exp = term["exp"]
        i = int(term["i"])
        j = int(term["j"])
        base = _eval_monom(exp, a, b)
        if feature["kind"] == "D":
            wall = _positive(b[j] - a[i]) if bool(term["diff_swapped"]) else _positive(a[i] - b[j])
            total += base * wall
        else:
            wall = _positive(a[i] + b[j] - T)
            total += base * (wall ** 3)
    return total


def _target_P(
    row,
    coeffP: Sequence[Fraction],
    monP: Sequence[Sequence[int]],
    coeffQ: Sequence[Fraction],
    monQ: Sequence[Sequence[int]],
) -> Fraction:
    # coeffQ kept for API symmetry with caller
    P = Fraction(0, 1)
    for c, ex in zip(coeffP, monP):
        P += c * _eval_monomial(row.omega, ex)
    return P


def _sympy_to_fraction(v: object) -> Fraction:
    if isinstance(v, sp.Rational):
        return Fraction(int(v.p), int(v.q))
    if isinstance(v, int):
        return Fraction(v, 1)
    return Fraction(v)


def _poly_rows(
    rows: Sequence,
    features: Sequence[Dict],
    coeffP: Sequence[Fraction],
    coeffQ: Sequence[Fraction],
    monP: Sequence[Sequence[int]],
    monQ: Sequence[Sequence[int]],
):
    X: List[List[Fraction]] = []
    y: List[Fraction] = []
    for row in rows:
        X.append([_eval_feature(f, row.omega) for f in features])
        y.append(_target_P(row, coeffP, monP, coeffQ, monQ))
    return X, y


def evaluate_p_from_features(omega: Sequence[Fraction], features: Sequence[Dict], coeffs: Sequence[Fraction]) -> Fraction:
    value = Fraction(0, 1)
    for c, feature in zip(coeffs, features):
        value += c * _eval_feature(feature, omega)
    return value


def run_orbit_feature_fit(
    rows: Sequence,
    coeffP: Sequence[Fraction],
    coeffQ: Sequence[Fraction],
    monP: Sequence[Sequence[int]],
    monQ: Sequence[Sequence[int]],
    degree: int,
    data_dir: Path,
) -> Dict:
    if degree % 2 != 0:
        return {"status": "skip", "reason": "odd_degree"}

    features = build_features(degree)
    if not features:
        return {"status": "skip", "reason": "no_features"}

    train_rows = [r for r in rows if getattr(r, "split", "") == "train"]
    hold_rows = [r for r in rows if getattr(r, "split", "") == "holdout"]
    if not train_rows:
        return {"status": "skip", "reason": "no_train_rows"}

    X, y = _poly_rows(train_rows, features, coeffP, coeffQ, monP, monQ)
    m = len(features)
    if m == 0:
        return {"status": "skip", "reason": "no_features"}
    if len(X) < m:
        return {"status": "skip", "reason": f"insufficient_rows_{len(X)}<{m}"}

    Xi = sp.Matrix([[sp.Rational(v.numerator, v.denominator) for v in row] for row in X])
    yi = sp.Matrix([sp.Rational(v.numerator, v.denominator) for v in y])
    G = Xi.T * Xi
    b = Xi.T * yi
    try:
        coeff_vec = G.LUsolve(b)
    except Exception:
        return {"status": "fail", "reason": "singular_normal_matrix"}

    coeff = [_sympy_to_fraction(c) for c in coeff_vec]
    if len(coeff) != m:
        return {"status": "fail", "reason": "coefficient_count_mismatch"}

    bad: List[str] = []
    for row in hold_rows:
        pred = evaluate_p_from_features(row.omega, features, coeff)
        target = _target_P(row, coeffP, monP, coeffQ, monQ)
        if pred != target:
            bad.append(getattr(row, "sample_id", ""))
            if len(bad) >= 10:
                break

    result: Dict = {
        "feature_count": m,
        "train_rows": len(train_rows),
        "holdout_rows": len(hold_rows),
        "rank": int(Xi.rank()),
        "coeff_count": len(coeff),
        "status": "pass" if not bad else "fail",
    }
    if bad:
        result["reason"] = "holdout_residuals"
        result["fail_ids"] = bad
        return result

    # Write a minimal standalone evaluator for later inspection.
    data_dir.mkdir(parents=True, exist_ok=True)
    eval_path = data_dir / "h_building_blocks_evaluator.py"
    payload = {
        "coeffs": [(c.numerator, c.denominator) for c in coeff],
        "features": features,
    }
    code = _build_evaluator_code(payload, degree)
    eval_path.write_text(code, encoding="utf-8")

    return {
        **result,
        "status": "pass",
        "evaluator_path": str(eval_path),
    }


def _build_evaluator_code(payload: Dict, degree: int) -> str:
    return f"""#!/usr/bin/env python3
\"\"\"Autogenerated orbit-feature evaluator.\"\"\"

from fractions import Fraction
from typing import Dict, List, Sequence

DEGREE = {degree}
FEATURES = {payload['features']!r}
COEFFS = {payload['coeffs']!r}


def _positive(v: Fraction) -> Fraction:
    return v if v > 0 else Fraction(0, 1)


def _eval_monom(exp, a, b):
    vals = list(a) + list(b)
    out = Fraction(1, 1)
    for e, x in zip(exp, vals):
        if e:
            out *= x ** e
    return out


def _eval_feature(feature: Dict, omega: Sequence[Fraction]) -> Fraction:
    a = [omega[0] ** 2, omega[1] ** 2, omega[2] ** 2]
    b = [omega[3] ** 2, omega[4] ** 2, omega[5] ** 2]
    T = a[0] + a[1] + a[2]

    if feature['kind'] == 'base':
        total = Fraction(0, 1)
        for exp in feature['terms']:
            total += _eval_monom(exp, a, b)
        return total

    total = Fraction(0, 1)
    for term in feature['terms']:
        exp = tuple(term['exp'])
        i = int(term['i'])
        j = int(term['j'])
        base = _eval_monom(exp, a, b)
        if feature['kind'] == 'D':
            if bool(term['diff_swapped']):
                wall = _positive(b[j] - a[i])
            else:
                wall = _positive(a[i] - b[j])
            total += base * wall
        else:
            wall = _positive(a[i] + b[j] - T)
            total += base * (wall ** 3)
    return total


def evaluate_p_from_features(omega: Sequence[Fraction], coeffs: Sequence[Fraction]) -> Fraction:
    return sum(c * _eval_feature(f, omega) for c, f in zip(coeffs, FEATURES))


def evaluate_P(omega: Sequence[Fraction]) -> Fraction:
    coeffs = [Fraction(num, den) for num, den in COEFFS]
    return evaluate_p_from_features(omega, coeffs)
"""
