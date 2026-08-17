#!/usr/bin/env python3
"""Round-5 exact Q-wall brick reconstruction for student-2.

Builds fresh bg binary, scans exact affine walls, reconstructs the
Q_wall jump quotient and the representative degree-2 quadratic
brick G in homogeneous on-shell basis, then validates transport across
all 9 channels from relabeling the representative line.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import sympy as sp

from round3_bottomup import (
    BOT,
    DATA,
    R2,
    ROOT,
    fstr,
    homogeneous_basis,
)

PAIR_KEYS = [
    "q_1_4",
    "q_1_5",
    "q_1_6",
    "q_2_4",
    "q_2_5",
    "q_2_6",
    "q_3_4",
    "q_3_5",
    "q_3_6",
]
TRIPLE_KEYS = [
    "q_1_45",
    "q_1_46",
    "q_1_56",
    "q_2_45",
    "q_2_46",
    "q_2_56",
    "q_3_45",
    "q_3_46",
    "q_3_56",
]
CHANNEL_KEYS = [
    "q_1_45",
    "q_1_46",
    "q_1_56",
    "q_2_45",
    "q_2_46",
    "q_2_56",
    "q_3_45",
    "q_3_46",
    "q_3_56",
]
REPR_CHANNEL = "q_1_46"
W = sp.symbols("w1:6")
W6 = sp.symbols("w1:7")
T = sp.Symbol("t")


def frac_to_q(r: sp.Rational) -> Fraction:
    return Fraction(int(r.p), int(r.q))


def sign_char(v: Fraction) -> str:
    if v > 0:
        return "+"
    if v < 0:
        return "-"
    return "0"


def parse_channel(key: str) -> Tuple[int, int, int]:
    if not key.startswith("q_"):
        raise ValueError("invalid channel key %r" % key)
    parts = key.split("_")
    if len(parts) != 3:
        raise ValueError("invalid channel key %r" % key)
    m = int(parts[1])
    pair = parts[2]
    if len(pair) != 2:
        raise ValueError("invalid channel pair %r in key %r" % (pair, key))
    p = int(pair[0])
    q = int(pair[1])
    if p > q:
        p, q = q, p
    return m - 1, p - 1, q - 1


def key_from_indices(m: int, p: int, q: int) -> str:
    a, b, c = m + 1, p + 1, q + 1
    if b > c:
        b, c = c, b
    return "q_%d_%d%d" % (a, b, c)


def to_fraction(v: int | Fraction | str) -> Fraction:
    return v if isinstance(v, Fraction) else Fraction(str(v))


def fraction_from_sympy(value: sp.Expr) -> Fraction:
    num, den = sp.together(value).as_numer_denom()
    return Fraction(int(num), int(den))


def q_polynomial(P: Sequence[Fraction], D: Sequence[Fraction], key: str):
    m, p, q = parse_channel(key)
    tm = sp.Rational(P[m].numerator, P[m].denominator)
    tp = sp.Rational(P[p].numerator, P[p].denominator)
    tq = sp.Rational(P[q].numerator, P[q].denominator)
    dm = sp.Rational(D[m].numerator, D[m].denominator)
    dp = sp.Rational(D[p].numerator, D[p].denominator)
    dq = sp.Rational(D[q].numerator, D[q].denominator)
    return sp.expand((tp + T * dp) ** 2 + (tq + T * dq) ** 2 - (tm + T * dm) ** 2)


def square_root_rational(x: Fraction) -> Optional[Fraction]:
    if x < 0:
        return None
    n = x.numerator
    d = x.denominator
    rn = int(math.isqrt(abs(n)))
    if rn * rn != n:
        return None
    rd = int(math.isqrt(d))
    if rd * rd != d:
        return None
    if x < 0:
        return None
    return Fraction(rn, rd)


def q_roots(P: Sequence[Fraction], D: Sequence[Fraction], key: str) -> List[Fraction]:
    expr = q_polynomial(P, D, key)
    poly = sp.Poly(expr, T)
    if poly.degree() == 0:
        return []
    if poly.degree() == 1:
        coeffs = poly.all_coeffs()
        a = frac_to_q(coeffs[0])
        b = frac_to_q(coeffs[1])
        if a == 0:
            return []
        r = -b / a
        return [r] if r != 0 else [r]
    a = frac_to_q(poly.all_coeffs()[0])
    b = frac_to_q(poly.all_coeffs()[1])
    c = frac_to_q(poly.all_coeffs()[2])
    if a == 0:
        if b == 0:
            return []
        return [-c / b]
    disc = b * b - 4 * a * c
    sr = square_root_rational(disc)
    if sr is None:
        return []
    num1 = -b + sr
    num2 = -b - sr
    den = 2 * a
    roots = []
    for r in (Fraction(num1, den), Fraction(num2, den)):
        if r not in roots:
            roots.append(r)
    return roots


def eval_rational(expr: sp.Expr, value: Fraction) -> Fraction:
    return fraction_from_sympy(expr.subs(T, sp.Rational(value.numerator, value.denominator)))


def sixpoint_from_omega(w: Sequence[Fraction]) -> R2.SixPoint:
    point = R2.SixPoint(w[1], w[2], w[3], w[4])
    if point.omega[0] != w[0] or point.omega[5] != w[5]:
        raise ValueError("line point not in sixpoint chart")
    return point


def w_at(P: Sequence[Fraction], D: Sequence[Fraction], t: Fraction) -> List[Fraction]:
    return [w_i + t * d_i for w_i, d_i in zip(P, D)]


def point_signature(point: R2.SixPoint) -> Dict[str, object]:
    word, strict, order = point.sorted_word()
    pair_sign = {k: sign_char(point.pair_q[k]) for k in PAIR_KEYS}
    triple_sign = {k: sign_char(point.triple_q[k]) for k in TRIPLE_KEYS}
    return {
        "word": word,
        "strict": strict,
        "order": [i + 1 for i in order],
        "energy_sign": ["+" if w > 0 else "-" if w < 0 else "0" for w in point.omega],
        "pair_sign": pair_sign,
        "triple_sign": triple_sign,
        "pair_q": {k: fstr(point.pair_q[k]) for k in PAIR_KEYS},
        "triple_q": {k: fstr(point.triple_q[k]) for k in TRIPLE_KEYS},
    }


def line_environment_key(signature: Dict[str, object], exclude_key: str) -> Tuple[Tuple[str, str], Tuple[str, str]]:
    pair = tuple((k, signature["pair_sign"][k]) for k in PAIR_KEYS if k != exclude_key)
    triple = tuple((k, signature["triple_sign"][k]) for k in TRIPLE_KEYS if k != exclude_key)
    return pair, triple


@dataclass
class Line:
    name: str
    P: Tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction]
    D: Tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction]

    def at(self, t: Fraction) -> Tuple[Fraction, ...]:
        return tuple(w_at(self.P, self.D, t))

    def conservation_report(self) -> Dict[str, bool]:
        s = sum(self.P)
        sq = sum(sg * (x * x) for sg, x in zip(R2.SIGMA, self.P))
        md = sum(sg * (w * d) for sg, (w, d) in zip(R2.SIGMA, zip(self.P, self.D)))
        dq = sum(sg * (d * d) for sg, d in zip(R2.SIGMA, self.D))
        return {
            "sumP0": s == 0,
            "sumP_sq0": sq == 0,
            "sumd0": sum(self.D) == 0,
            "sumPd0": md == 0,
            "sumD_sq0": dq == 0,
            "sumP": fstr(s),
            "sumP_sq": fstr(sq),
            "sumd": fstr(sum(self.D)),
            "sumPd": fstr(md),
            "sumD_sq": fstr(dq),
        }


def mapping_for_channel(target_key: str, swap_nonprimary_minus: bool = False, swap_pair_plus: bool = False) -> Dict[int, int]:
    m, p, q = parse_channel(target_key)
    old_to_new = {}
    # Primary minus goes to requested minus label.
    old_to_new[0] = m
    rem_new_minus = [x for x in (0, 1, 2) if x != m]
    rem_old_minus = [1, 2]
    if swap_nonprimary_minus:
        rem_old_minus = rem_old_minus[::-1]
    old_to_new[rem_old_minus[0]] = rem_new_minus[0]
    old_to_new[rem_old_minus[1]] = rem_new_minus[1]

    # plus-wall legs map to requested pair (plus labels sorted).
    pair = sorted((p, q))
    if swap_pair_plus:
        pair = list(pair)
        pair[0], pair[1] = pair[1], pair[0]
    old_to_new[3] = pair[0]
    old_to_new[5] = pair[1]
    old_to_new[4] = next(x for x in (3, 4, 5) if x not in pair)

    for i in (0, 1, 2, 3, 4, 5):
        if i not in old_to_new:
            raise RuntimeError("incomplete mapping")
    for _, v in old_to_new.items():
        if not (0 <= v < 6):
            raise RuntimeError("invalid map image")
    return old_to_new


def relabel_line(line: Line, target_key: str, **kwargs) -> Line:
    perm = mapping_for_channel(target_key, **kwargs)
    inv = [None] * 6
    for old, new in perm.items():
        inv[new] = old
    P2 = tuple(line.P[i] for i in inv)
    D2 = tuple(line.D[i] for i in inv)
    return Line(f"{line.name}->{target_key}", P2, D2)


def evaluate_remainder(oracle: R2.BGOracle, point: R2.SixPoint) -> Fraction:
    k = [sg * (x * x) for sg, x in zip(R2.SIGMA, point.omega)]
    result, err = R2.safe_raw(oracle, k, point.omega)
    if result is None:
        raise RuntimeError(err)
    _, re_part, im_part = result
    if re_part != 0:
        raise RuntimeError("non-imaginary A6 at sample")
    return R2.wall_pole_subtracted(point, im_part)[0]


def interpolate_and_fit(samples: Sequence[Tuple[Fraction, Fraction]], degree: int):
    return R2.rational_poly_fit(samples, T, degree)


def nodes_around(root: Fraction, denom: int = 1200, count: int = 12):
    return [
        [root - Fraction(k, denom) for k in range(1, count + 1)],
        [root + Fraction(k, denom) for k in range(1, count + 1)],
    ]


def wall_case(
    oracle: R2.BGOracle,
    line: Line,
    target_key: str,
    root: Fraction,
    denom: int,
    min_nodes_per_side: int = 12,
):
    left_nodes = [root - Fraction(k, denom) for k in range(1, min_nodes_per_side + 1)]
    right_nodes = [root + Fraction(k, denom) for k in range(1, min_nodes_per_side + 1)]

    records = []
    baseline = None
    target_signs = set()

    def sign_info(t: Fraction):
        w = line.at(t)
        point = sixpoint_from_omega(w)
        sig = point_signature(point)
        qv = point.pair_q if target_key in point.pair_q else point.triple_q
        qkey = target_key
        qval = qv[qkey]
        sig["t"] = t
        sig["w"] = [fstr(x) for x in point.omega]
        sig["w1to5"] = [fstr(x) for x in point.omega[:5]]
        sig["q_target"] = fstr(qval)
        sig["q_target_sign"] = sign_char(qval)
        return sig, point, qval

    for t in left_nodes + right_nodes:
        try:
            sig, point, qval = sign_info(t)
        except Exception:
            return None
        side = "L" if t < root else "R"

        # exact signs, no accidental degeneracies on the cell.
        if sig["word"] == "" or not sig["strict"]:
            return None
        if sig["strict"] is False:
            return None
        if "0" in sig["energy_sign"]:
            return None
        if any(v == "0" for v in sig["pair_sign"].values()):
            return None
        if any(v == "0" for v in sig["triple_sign"].values()):
            return None

        if qval == 0:
            return None

        if baseline is None:
            baseline = sig
            target_signs.add(sign_char(qval))
        else:
            for k in PAIR_KEYS:
                if k == target_key:
                    continue
                if sig["pair_sign"][k] != baseline["pair_sign"][k]:
                    return None
            for k in TRIPLE_KEYS:
                if k == target_key:
                    continue
                if sig["triple_sign"][k] != baseline["triple_sign"][k]:
                    return None
            if sig["energy_sign"] != baseline["energy_sign"]:
                return None
            if sig["order"] != baseline["order"]:
                return None
            if sig["word"] != baseline["word"]:
                return None
            target_signs.add(sign_char(qval))

        records.append({"side": side, "node": sig, "point": point, "q": qval})

    if len(target_signs) != 2:
        return None
    if len(records) != 2 * min_nodes_per_side:
        return None

    left_records = [r for r in records if r["q"] < 0]
    right_records = [r for r in records if r["q"] > 0]
    if len(left_records) != min_nodes_per_side or len(right_records) != min_nodes_per_side:
        return None

    for rec in records:
        try:
            rem = evaluate_remainder(oracle, rec["point"])
        except Exception as exc:
            raise RuntimeError(f"bg failure at t={fstr(rec['node']['t'])}: {exc}")
        rec["R"] = rem

    left_fit_pts = [(rec["node"]["t"], rec["R"]) for rec in left_records[:9]]
    right_fit_pts = [(rec["node"]["t"], rec["R"]) for rec in right_records[:9]]

    left_fit = interpolate_and_fit(left_fit_pts, 8)
    right_fit = interpolate_and_fit(right_fit_pts, 8)
    if left_fit["status"] != "ok" or right_fit["status"] != "ok":
        raise RuntimeError("interpolation")

    left_hold = [(rec["node"]["t"], rec["R"]) for rec in left_records[9:]]
    right_hold = [(rec["node"]["t"], rec["R"]) for rec in right_records[9:]]
    left_hold_res = R2.poly_residuals(left_fit["poly"], T, left_hold)
    right_hold_res = R2.poly_residuals(right_fit["poly"], T, right_hold)

    if any(h["res"] != "0" for h in left_hold_res + right_hold_res):
        raise RuntimeError("interpolation")

    q_expr = q_polynomial(line.P, line.D, target_key)
    delta_expr = sp.expand(right_fit["poly"].as_expr() - left_fit["poly"].as_expr())
    q_pow = sp.expand(q_expr ** 3)
    delta_poly = sp.Poly(delta_expr, T, domain=sp.QQ)
    q_poly = sp.Poly(q_pow, T, domain=sp.QQ)
    H_poly, H_rem = delta_poly.div(q_poly)
    if H_rem != 0:
        raise RuntimeError("division")
    H_poly = sp.Poly(sp.expand(H_poly.as_expr()), T, domain=sp.QQ)

    if H_poly.total_degree() > 2:
        return None

    # exact jump division check on held-out nodes
    for rec in left_records[9:] + right_records[9:]:
        tv = sp.Rational(rec["node"]["t"].numerator, rec["node"]["t"].denominator)
        qv = eval_rational(q_expr, rec["node"]["t"])
        delta_hat = fraction_from_sympy(H_poly.eval(tv) * (qv ** 3))
        actual = eval_rational(delta_expr, rec["node"]["t"])
        if delta_hat != actual:
            raise RuntimeError("division")

    sample_nodes = []
    for rec in left_records + right_records:
        tv = rec["node"]["t"]
        tR = sp.Rational(tv.numerator, tv.denominator)
        sample_nodes.append(
            {
                "side": rec["side"],
                "t": fstr(tv),
                "omega": rec["node"]["w"],
                "w1to5": rec["node"]["w1to5"],
                "R": fstr(rec["R"]),
                "q": rec["node"]["q_target"],
                "quotient": fstr(fraction_from_sympy(H_poly.eval(tR))),
                "q_target_sign": rec["node"]["q_target_sign"],
            }
        )

    return {
        "status": "ok",
        "line": line.name,
        "target": target_key,
        "root": fstr(root),
        "denom": denom,
        "environment": {
            "pair_sign": {k: v for k, v in baseline["pair_sign"].items()},
            "triple_sign": {k: v for k, v in baseline["triple_sign"].items()},
            "magnitude_order": baseline["order"],
            "energy_sign": baseline["energy_sign"],
            "word": baseline["word"],
        },
        "left": {
            "degree": int(left_fit["deg"]),
            "poly": str(left_fit["poly"].as_expr()),
            "holdout_residual_zero": sum(1 for x in left_hold_res if x["res"] == "0"),
            "holdout_total": len(left_hold_res),
        },
        "right": {
            "degree": int(right_fit["deg"]),
            "poly": str(right_fit["poly"].as_expr()),
            "holdout_residual_zero": sum(1 for x in right_hold_res if x["res"] == "0"),
            "holdout_total": len(right_hold_res),
        },
        "jump": {
            "q_poly": str(q_expr),
            "H_poly": str(H_poly.as_expr()),
            "H_degree": H_poly.total_degree(),
            "division_zero_remainder": True,
            "division_remainder": "0",
        },
        "sample_nodes": sample_nodes,
        "samples": len(sample_nodes),
        "signature_key": {
            "pair": [(k, v) for k, v in baseline["pair_sign"].items()],
            "triple": [(k, v) for k, v in baseline["triple_sign"].items()],
        },
    }


def wall_signature_without_target(signature: Dict[str, object], target_key: str) -> Tuple[Tuple[Tuple[str, str], ...], Tuple[Tuple[str, str], ...]]:
    if "pair_sign" in signature:
        pair_sign = signature["pair_sign"]
        triple_sign = signature["triple_sign"]
    elif "pair" in signature and isinstance(signature["pair"], dict):
        pair_sign = signature["pair"]
        triple_sign = signature["triple"]
    elif "pair" in signature and isinstance(signature["pair"], list):
        pair_sign = {k: v for k, v in signature["pair"]}
        triple_sign = {k: v for k, v in signature["triple"]}
    else:
        raise ValueError("invalid signature shape")
    return (
        tuple((k, pair_sign[k]) for k in sorted(pair_sign) if k != target_key),
        tuple((k, triple_sign[k]) for k in sorted(triple_sign) if k != target_key),
    )


def collect_walls(oracle: R2.BGOracle, lines: Sequence[Line], denom_candidates: Sequence[int] = (1200, 1600, 2000, 2400, 3000, 3600, 4200)) -> Tuple[List[Dict[str, object]], Dict[str, object]]:
    walls = []
    stats = {
        "attempted": 0,
        "certified": 0,
        "rejected_root_missing": 0,
        "rejected_geometry": 0,
        "rejected_interpolation": 0,
        "rejected_division": 0,
    }

    for line in lines:
        for target_key in CHANNEL_KEYS:
            roots = q_roots(line.P, line.D, target_key)
            if not roots:
                stats["rejected_root_missing"] += 1
                continue
            ok = False
            for root in roots:
                for denom in denom_candidates:
                    stats["attempted"] += 1
                    try:
                        rec = wall_case(oracle, line, target_key, root, denom)
                    except RuntimeError as exc:
                        msg = str(exc)
                        if msg == "interpolation":
                            stats["rejected_interpolation"] += 1
                        elif msg == "division":
                            stats["rejected_division"] += 1
                        else:
                            stats["rejected_geometry"] += 1
                        rec = None
                    if rec is None:
                        continue
                    sig_env = rec["environment"]
                    # finalize only isolated wall with exact side fits and jump.
                    rec["source_line_P"] = [fstr(x) for x in line.P]
                    rec["source_line_D"] = [fstr(x) for x in line.D]
                    rec["environment_without_target"] = {
                        "pair": [
                            [k, v]
                            for k, v in sig_env["pair_sign"].items()
                            if k != target_key
                        ],
                        "triple": [
                            [k, v]
                            for k, v in sig_env["triple_sign"].items()
                            if k != target_key
                        ],
                    }
                    # keep one certified wall per channel/line/root/denom.
                    walls.append(rec)
                    ok = True
                    stats["certified"] += 1
                    break
                if ok:
                    break
            if not ok:
                stats["rejected_geometry"] += 1

    if not walls:
        return walls, stats

    return walls, stats


def basis_row(point_w1to5: Sequence[Fraction], basis: Sequence[Tuple[int, ...]]) -> List[Fraction]:
    return [
        (point_w1to5[0] ** a)
        * (point_w1to5[1] ** b)
        * (point_w1to5[2] ** c)
        * (point_w1to5[3] ** d)
        * (point_w1to5[4] ** e)
        for (a, b, c, d, e) in basis
    ]


def modular_independent(rows: List[List[Fraction]], prime: int = 1000000007):
    cols = len(rows[0]) if rows else 0
    selected = []
    idx_selected = []

    basis = {}

    def row_mod(x: Fraction):
        den = x.denominator
        if den == 0:
            raise RuntimeError("non-invertible denominator in modular reduction")
        den_inv = pow(den % prime, prime - 2, prime)
        return (x.numerator % prime) * den_inv % prime

    def add(row):
        v = [row_mod(x) for x in row]
        for pivot in sorted(basis):
            if v[pivot] == 0:
                continue
            factor = v[pivot]
            base = basis[pivot]
            for j in range(pivot, cols):
                v[j] = (v[j] - factor * base[j]) % prime
        pivot = next((j for j in range(cols) if v[j]), None)
        if pivot is None:
            return False, None
        inv = pow(v[pivot], prime - 2, prime)
        for j in range(pivot, cols):
            v[j] = (v[j] * inv) % prime
        for old, base in list(basis.items()):
            if base[pivot] == 0:
                continue
            factor = base[pivot]
            basis[old] = [
                (base[j] - factor * v[j]) % prime if j >= old else base[j]
                for j in range(cols)
            ]
        basis[pivot] = v
        return True, pivot

    for i, row in enumerate(rows):
        ok, pivot = add(row)
        if ok:
            selected.append(row)
            idx_selected.append(i)
    return selected, idx_selected


def solve_quadratic_for_records(records: List[Dict[str, object]], basis: Sequence[Tuple[int, ...]]) -> Dict[str, object]:
    if not records:
        return {"status": "no_records"}

    all_nodes = []
    for rec in records:
        for n in rec["sample_nodes"]:
            w = [Fraction(x) for x in n["w1to5"]]
            qval = Fraction(n["quotient"])
            all_nodes.append((w, qval))

    # Deduplicate by point to reduce accidental rank loss.
    unique = {}
    for w, q in all_nodes:
        key = tuple(w)
        unique.setdefault(key, q)
    nodes = [(list(k), v) for k, v in unique.items()]

    rows = [basis_row(w, basis) for w, _ in nodes]
    vals = [v for _, v in nodes]

    sel_rows, sel_idx = modular_independent(rows)
    if len(sel_rows) < len(basis):
        return {
            "status": "insufficient_rank",
            "rows": len(rows),
            "rank": len(sel_rows),
            "needed": len(basis),
        }

    chosen_rows = [rows[i] for i in sel_idx[: len(basis)]]
    chosen_vals = [vals[i] for i in sel_idx[: len(basis)]]
    M = sp.Matrix(
        [[sp.Rational(x.numerator, x.denominator) for x in row] for row in chosen_rows]
    )
    b = sp.Matrix([sp.Rational(v.numerator, v.denominator) for v in chosen_vals])
    coeff = list(M.LUsolve(b))

    expr = 0
    for c, ex in zip(coeff, basis):
        expr += c * W[0] ** ex[0] * W[1] ** ex[1] * W[2] ** ex[2] * W[3] ** ex[3] * W[4] ** ex[4]
    poly = sp.Poly(sp.expand(expr), *W, domain=sp.QQ)

    residuals = []
    zero = 0
    for w, qv in nodes:
        pred = fraction_from_sympy(poly.as_expr().subs(dict(zip(W, w))))
        res = pred - qv
        residuals.append(str(res))
        if res == 0:
            zero += 1

    return {
        "status": "ok",
        "rank": len(sel_rows),
        "coeff": [str(sp.Rational(c)) for c in coeff],
        "poly": str(poly.as_expr()),
        "factor": str(sp.factor(poly.as_expr())),
        "residual_count": zero,
        "residual_total": len(nodes),
        "node_total": len(nodes),
        "residuals": residuals[:24],
    }


def g_expr_from_coeff(coeff: Sequence[sp.Rational], basis: Sequence[Tuple[int, ...]]) -> sp.Poly:
    expr = 0
    for c, mon in zip(coeff, basis):
        if c == 0:
            continue
        expr += c * W[0] ** mon[0] * W[1] ** mon[1] * W[2] ** mon[2] * W[3] ** mon[3] * W[4] ** mon[4]
    return sp.Poly(sp.expand(expr), *W, domain=sp.QQ)


def reduce_w5_local(expr: sp.Expr) -> sp.Poly:
    if hasattr(R2, "reduce_w5"):
        reduced = R2.reduce_w5(expr, W)
        if isinstance(reduced, sp.Poly):
            return reduced
    w1, w2, w3, w4, w5 = W
    S4 = w1 + w2 + w3 + w4
    K = -w1 ** 2 - w2 ** 2 - w3 ** 2 + w4 ** 2 + S4 ** 2
    relation = 2 * w5 ** 2 + 2 * S4 * w5 + K
    return sp.Poly(
        sp.rem(sp.Poly(sp.expand(expr), w5), sp.Poly(relation, w5)).as_expr(),
        *W,
        domain=sp.QQ,
    )


def relabel_poly_to_channel(poly: sp.Poly, target_key: str) -> sp.Poly:
    perm = mapping_for_channel(target_key)
    expr6 = poly.as_expr().xreplace({W[i]: W6[i] for i in range(5)})
    rel_map = {W6[o]: W6[n] for o, n in perm.items()}
    rel_expr = expr6.xreplace(rel_map)
    reduced = reduce_w5_local(rel_expr)
    return reduced


def check_channel_transport(repr_poly: sp.Poly, walls: List[Dict[str, object]]) -> Dict[str, object]:
    out = {}
    for key in CHANNEL_KEYS:
        rel = relabel_poly_to_channel(repr_poly, key)
        recs = [w for w in walls if w["target"] == key]
        if not recs:
            out[key] = {"status": "missing_channel"}
            continue
        total = 0
        zero = 0
        for rec in recs:
            for node in rec["sample_nodes"]:
                w = [Fraction(x) for x in node["w1to5"]]
                expected = Fraction(node["quotient"])
                val = fraction_from_sympy(rel.as_expr().subs(dict(zip(W, w))))
                total += 1
                if val == expected:
                    zero += 1
        out[key] = {
            "records": len(recs),
            "samples": total,
            "residual_zero": zero,
            "poly": str(rel.as_expr()),
        }

    return out


def check_fixed_candidate(walls: List[Dict[str, object]], poly: sp.Poly) -> Dict[str, object]:
    out = {}
    total_samples = 0
    total_zero = 0
    expr = poly.as_expr()
    for key in CHANNEL_KEYS:
        rel = relabel_poly_to_channel(poly, key)
        rel_expr = rel.as_expr()
        recs = [w for w in walls if w["target"] == key]
        if not recs:
            out[key] = {"status": "missing_channel"}
            continue
        samples = 0
        zeros = 0
        for rec in recs:
            for node in rec["sample_nodes"]:
                w = [Fraction(x) for x in node["w1to5"]]
                expected = Fraction(node["quotient"])
                val = fraction_from_sympy(rel_expr.subs(dict(zip(W, w))))
                samples += 1
                if val == expected:
                    zeros += 1
        out[key] = {
            "records": len(recs),
            "samples": samples,
            "residual_zero": zeros,
        }
        total_samples += samples
        total_zero += zeros
    out["_summary"] = {"samples": total_samples, "residual_zero": total_zero}
    return out


def check_selector_candidate(walls: List[Dict[str, object]]) -> Dict[str, object]:
    out: Dict[str, object] = {}
    global_samples = 0
    global_zero = 0
    global_branches = {"m": 0, "t": 0, "tie": 0}

    for key in CHANNEL_KEYS:
        recs = [w for w in walls if w["target"] == key]
        if not recs:
            out[key] = {"status": "missing_channel"}
            continue
        samples = 0
        zeros = 0
        branch_counts = {"m": 0, "t": 0, "tie": 0}
        signature_counts = {}
        m_idx, p_idx, q_idx = parse_channel(key)
        omitted_plus = next(x for x in (3, 4, 5) if x not in (p_idx, q_idx))
        for rec in recs:
            sig = str(rec["signature_key"])
            sig_entry = signature_counts.setdefault(
                sig, {"m": 0, "t": 0, "tie": 0, "samples": 0, "records": 0}
            )
            sig_entry["records"] += 1
            for node in rec["sample_nodes"]:
                w = [Fraction(x) for x in node["w1to5"]]
                w.append(-sum(w))
                wm2 = w[m_idx] * w[m_idx]
                wt2 = w[omitted_plus] * w[omitted_plus]
                if wm2 > wt2:
                    expected = Fraction(-16) * wm2
                    branch = "m"
                elif wm2 < wt2:
                    expected = Fraction(-16) * wt2
                    branch = "t"
                else:
                    expected = Fraction(-16) * wm2
                    branch = "m"
                samples += 1
                global_samples += 1
                sig_entry["samples"] += 1
                branch_counts[branch] += 1
                sig_entry[branch] += 1
                global_branches[branch] += 1
                if wm2 == wt2:
                    branch_counts["tie"] += 1
                    sig_entry["tie"] += 1
                    global_branches["tie"] += 1
                expected_node = Fraction(node["quotient"])
                if expected == expected_node:
                    zeros += 1
                    global_zero += 1
        out[key] = {
            "records": len(recs),
            "samples": samples,
            "residual_zero": zeros,
            "branch_counts": branch_counts,
            "signature_branch_counts": signature_counts,
        }

    out["_summary"] = {
        "samples": global_samples,
        "residual_zero": global_zero,
        "branch_counts": global_branches,
    }
    return out


def check_stabilizer(repr_poly: sp.Poly) -> Dict[str, object]:
    # swap nonprimary minus legs in Q wall: 2 <-> 3 (indices 1,2), keep primary minus 1 fixed
    perm_minus_swap = {0: 0, 1: 2, 2: 1, 3: 3, 4: 4, 5: 5}
    # swap plus legs in Q wall: 4 <-> 6 (indices 0-based 3,5)
    perm_plus_swap = {0: 0, 1: 1, 2: 2, 3: 5, 4: 4, 5: 3}

    def relabel(poly, perm):
        expr6 = poly.as_expr().xreplace({W[i]: W6[i] for i in range(5)})
        rel_expr = expr6.xreplace({W6[o]: W6[n] for o, n in perm.items()})
        return reduce_w5_local(rel_expr)

    poly_m = relabel(repr_poly, perm_minus_swap)
    poly_p = relabel(repr_poly, perm_plus_swap)

    return {
        "swap_nonprimary_minus": {
            "poly": str(poly_m.as_expr()),
            "difference_zero": (poly_m - repr_poly).as_expr() == 0,
            "difference_terms": len((poly_m - repr_poly).terms()),
            "difference_witness": str((poly_m - repr_poly).terms()[0][0]) if (poly_m - repr_poly).terms() else None,
        },
        "swap_wall_plus_legs": {
            "poly": str(poly_p.as_expr()),
            "difference_zero": (poly_p - repr_poly).as_expr() == 0,
            "difference_terms": len((poly_p - repr_poly).terms()),
            "difference_witness": str((poly_p - repr_poly).terms()[0][0]) if (poly_p - repr_poly).terms() else None,
        },
    }


def make_lines() -> List[Line]:
    base = Line(
        "worked",
        (
            to_fraction(8),
            to_fraction(2),
            to_fraction(-3),
            to_fraction(-5),
            to_fraction(4),
            to_fraction(-6),
        ),
        (
            to_fraction(-2),
            to_fraction(1),
            to_fraction(0),
            to_fraction(2),
            to_fraction(-1),
            to_fraction(0),
        ),
    )
    D3 = (
        to_fraction(0),
        to_fraction(10),
        to_fraction(-5),
        to_fraction(5),
        to_fraction(0),
        to_fraction(-10),
    )

    dirs = [0, 1, 2]
    bases = [
        Line(f"worked_n{n}", base.P, tuple(base.D[i] + n * D3[i] for i in range(6)))
        for n in dirs
    ]

    for b in bases:
        if not all(b.conservation_report().get(k) for k in ("sumP0", "sumd0", "sumP_sq0", "sumPd0", "sumD_sq0")):
            raise AssertionError(f"line {b.name} failed on-shell checks")

    out = []
    for b in bases:
        for ck in CHANNEL_KEYS:
            out.append(relabel_line(b, ck))
    return out


def wall_signature_key(rec: Dict[str, object]) -> Tuple[Tuple[Tuple[str, str], ...], Tuple[Tuple[str, str], ...]]:
    return (
        tuple((x[0], x[1]) for x in rec["environment_without_target"]["pair"]),
        tuple((x[0], x[1]) for x in rec["environment_without_target"]["triple"]),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-walls-per-channel", type=int, default=3)
    args = parser.parse_args()

    build_meta: Dict[str, object] = {}
    bg_bin = R2.build_bg(ROOT, build_meta)
    build_hash = subprocess.check_output(["sha256sum", str(bg_bin)]).decode().split()[0]
    oracle = R2.BGOracle(bg_bin)
    build_root_path = ROOT / "bg.cpp"
    build_copy_path = BOT / "bg.cpp"
    root_bg_hash = subprocess.check_output(["sha256sum", str(build_root_path)]).decode().split()[0]
    copy_bg_hash = subprocess.check_output(["sha256sum", str(build_copy_path)]).decode().split()[0]
    assert root_bg_hash == copy_bg_hash, "bg.cpp copy hash mismatch"

    all_lines = make_lines()

    lines_checked = []
    for line in all_lines:
        lines_checked.append(
            {
                "name": line.name,
                "P": [fstr(x) for x in line.P],
                "D": [fstr(x) for x in line.D],
                "conservation": line.conservation_report(),
            }
        )

    all_walls, collect_stats = collect_walls(oracle, all_lines)

    # Keep one wall per line/channel/root for deterministic compactness.
    by_id = {}
    for w in all_walls:
        key = (w["line"], w["target"], w["root"])
        if key in by_id:
            continue
        by_id[key] = w
    walls = list(by_id.values())

    # channel-wise caps for stability.
    counts = {k: 0 for k in CHANNEL_KEYS}
    filtered = []
    for w in walls:
        if counts[w["target"]] >= args.max_walls_per_channel:
            continue
        counts[w["target"]] += 1
        filtered.append(w)

    # split by target channel and pick representative for G reconstruction.
    repr_walls = [w for w in filtered if w["target"] == REPR_CHANNEL]

    basis = homogeneous_basis(2)
    g_solution = solve_quadratic_for_records(repr_walls, basis)

    # symbolic transport across all channels.
    transport = {}
    global_channel_report = {}
    if g_solution.get("status") == "ok":
        g_poly = g_expr_from_coeff([Fraction(c) for c in g_solution["coeff"]], basis)
        transport = check_channel_transport(g_poly, filtered)
        # stability checks in stabilizer subgroup.
        stabilizer = check_stabilizer(g_poly)
        g_solution["factorized"] = {
            "human": str(sp.factor(g_poly.as_expr())),
        }
        g_solution["stabilizer"] = stabilizer

        # Per-signature fallback if any channel transport fails globally.
        by_sig = {}
        for rec in repr_walls:
            by_sig.setdefault(wall_signature_key(rec), []).append(rec)
        signature_fits = {}
        for sig, recs in by_sig.items():
            if len(recs) < len(basis):
                signature_fits[str(sig)] = {"status": "insufficient_records"}
                continue
            signature_fits[str(sig)] = solve_quadratic_for_records(recs, basis)
        g_solution["signature_fits"] = signature_fits

        # one exact summary line for each channel.
        global_channel_report = {k: transport[k]["residual_zero"] for k in CHANNEL_KEYS if k in transport}

    candidate_poly = sp.Poly(-16 * W[0] ** 2, *W, domain=sp.QQ)
    candidate_transport = check_fixed_candidate(filtered, candidate_poly)
    selector_transport = check_selector_candidate(filtered)

    unique_sig_keys = [str(w["signature_key"]) for w in filtered]

    payload = {
        "meta": {
            "task": "round5_qbrick",
            "build": {
                "command": build_meta["build"]["command"],
                "binary": str(bg_bin),
                "sha256": build_hash,
                "bg_root_sha256": root_bg_hash,
                "bg_copy_sha256": copy_bg_hash,
            },
            "lines": lines_checked,
            "line_count": len(all_lines),
            "collect_stats": collect_stats,
            "filter_max_per_channel": args.max_walls_per_channel,
            "representative_channel": REPR_CHANNEL,
        },
        "basis": [
            list(item) for item in basis
        ],
        "wall_records": filtered,
        "wall_counts": {
            "total_records": len(filtered),
            "by_target": {k: sum(1 for w in filtered if w["target"] == k) for k in CHANNEL_KEYS},
            "distinct_signatures": len(set(unique_sig_keys)),
            "distinct_signature_keys": sorted(set(unique_sig_keys)),
        },
        "representative_reconstruction": {
            "basis_size": len(basis),
            "wall_count": len(repr_walls),
            "solve": g_solution,
            "transport": transport,
        },
        "candidate": {
            "poly": str(candidate_poly.as_expr()),
            "transport": candidate_transport,
            "selector": {
                "formula": "-16*max(w_m^2,w_t^2)",
                "transport": selector_transport,
            },
        },
        "signature_transport_zero_count": global_channel_report,
    }

    out_path = DATA / "round5_qbrick.json"
    DATA.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True))

    report_lines = [
        "# Round-5 Q-wall brick reconstruction",
        "",
        f"- built bg: `{payload['meta']['build']['binary']}`",
        f"- build command: `{payload['meta']['build']['command']}`",
        f"- candidate lines checked: `{payload['meta']['line_count']}`",
        f"- wall attempts: `{payload['meta']['collect_stats']['attempted']}`",
        f"- certified walls: `{payload['wall_counts']['total_records']}`",
        f"- representative walls ({REPR_CHANNEL}): `{payload['representative_reconstruction']['wall_count']}`",
        "",
        "## Channel coverage",
    ]

    for k, v in payload["wall_counts"]["by_target"].items():
        report_lines.append(f"- {k}: `{v}`")

    rec_status = payload["representative_reconstruction"]["solve"].get("status")
    report_lines.extend(
        [
            "",
            f"- representative solve status: `{rec_status}`",
            f"- representative residual pass: `{payload['representative_reconstruction']['solve'].get('residual_count', 0)}` / `{payload['representative_reconstruction']['solve'].get('residual_total', 0)}`",
            "",
            "## Channel transport checks",
        ]
    )

    for ch, val in transport.items():
        if isinstance(val, dict):
            report_lines.append(f"- {ch}: `{val.get('residual_zero', 0)}` / `{val.get('samples', 0)}`")

    report_lines.append("")
    report_lines.append("## Fixed selector candidate `-16*max(w_m^2,w_t^2)` checks")
    report_lines.append(
        f"- summary: `{payload['candidate']['selector']['transport']['_summary']['residual_zero']}` / `{payload['candidate']['selector']['transport']['_summary']['samples']}`"
    )
    report_lines.append(
        "- branch selection: "
        + ", ".join(
            f"{k}={v}"
            for k, v in payload["candidate"]["selector"]["transport"]["_summary"]["branch_counts"].items()
        )
    )
    for ch, val in payload["candidate"]["selector"]["transport"].items():
        if ch == "_summary":
            continue
        if isinstance(val, dict):
            if val.get("status") == "missing_channel":
                report_lines.append(f"- {ch}: missing channel")
            else:
                report_lines.append(
                    f"- {ch}: `{val.get('residual_zero', 0)}` / `{val.get('samples', 0)}` | "
                    + ", ".join(
                        f"{k}={val.get('branch_counts', {}).get(k, 0)}"
                        for k in ("m", "t", "tie")
                    )
                )

    report_lines.append("")
    report_lines.append("## Fixed diagnostic `-16*w_m^2` checks")
    report_lines.append(
        f"- summary: `{candidate_transport['_summary']['residual_zero']}` / `{candidate_transport['_summary']['samples']}`"
    )
    for ch, val in candidate_transport.items():
        if ch == "_summary":
            continue
        if isinstance(val, dict):
            if val.get("status") == "missing_channel":
                report_lines.append(f"- {ch}: missing channel")
            else:
                report_lines.append(f"- {ch}: `{val.get('residual_zero', 0)}` / `{val.get('samples', 0)}`")

    rpt_path = DATA / "round5_qbrick_report.md"
    rpt_path.write_text("\n".join(report_lines))

    print(str(out_path))
    print(str(rpt_path))


if __name__ == "__main__":
    main()
