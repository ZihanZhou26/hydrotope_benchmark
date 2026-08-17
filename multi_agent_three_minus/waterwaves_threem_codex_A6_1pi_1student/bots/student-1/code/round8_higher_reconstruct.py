#!/usr/bin/env python3
"""Round-8 higher-chamber reconstruction for signature 12ea165a03.

Workflow:
  1) scan d = 12, 13 (and d = 14 on top-up) by modular nullity on
     P(x,y,z)/Q(x,y,z), where deg(P)=d and deg(Q)=d-2 in x,y,z.
  2) scan equal-bound mode separately: deg(P)=deg(Q)=d for d=13,14.
  3) if a unique modular null vector exists at a degree, reconstruct with CRT
     over multiple 31-bit primes, exact-rational reconstruct coefficients,
     validate on all points used in that mode.
  4) factor/analyse Q and run fixed candidate-factor divisibility checks.

The script writes:
  - result JSON: bots/student-1/data/round8_higher_reconstruct.json
  - dense P/Q (expanded + factorized): bots/student-1/data/round8_higher_QP.txt
  - short log: bots/student-1/data/round8_higher_reconstruct.log
  - equal-bound result JSON: bots/student-1/data/round8_higher_equal_reconstruct.json
  - equal-bound dense P/Q (expanded + factorized):
        bots/student-1/data/round8_higher_equal_reconstruct_QP.txt
"""

import argparse
import hashlib
import json
import random
import re
import shlex
import shutil
import os
import subprocess
import sys
from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from time import gmtime, strftime, time
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import sympy as sp

SIG = [-1, -1, -1, 1, 1, 1]
P31 = (1 << 31) - 1
PRIMES_31 = [
    2147483647,
    2147483629,
    2147483587,
    2147483563,
    2147483399,
]

ROOT = Path(__file__).resolve().parent.parent.parent.parent
STUDENT_DIR = ROOT / "bots" / "student-1"
CODE_DIR = STUDENT_DIR / "code"
DATA_DIR = STUDENT_DIR / "data"
QUESTION_BG_SRC = ROOT / "bg.cpp"
LOCAL_BG_CPP = CODE_DIR / "bg_s1_r8.cpp"
LOCAL_BG_BIN = CODE_DIR / "bg_s1_r8"

POINTS_DEFAULT = ROOT / "round7_pts_12ea165a03.json"
DEFAULT_RESULT = DATA_DIR / "round8_higher_reconstruct.json"
DEFAULT_QP = DATA_DIR / "round8_higher_QP.txt"
DEFAULT_LOG = DATA_DIR / "round8_higher_reconstruct.log"
TOPUP_POINTS = DATA_DIR / "round8_pts_12ea165a03_1250.json"
TOPUP_POINTS_1450 = DATA_DIR / "round8_pts_12ea165a03_1450.json"
DEFAULT_EQUAL_RESULT = DATA_DIR / "round8_higher_equal_reconstruct.json"
DEFAULT_EQUAL_QP = DATA_DIR / "round8_higher_equal_reconstruct_QP.txt"
DEFAULT_EQUAL_LOG = DATA_DIR / "round8_higher_equal_reconstruct.log"


def utc_timestamp() -> str:
    return subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%S"], universal_newlines=True).strip()


def frac_from_json(v) -> Fraction:
    if isinstance(v, Fraction):
        return v
    return Fraction(str(v))


def frac_to_str(v: Fraction) -> str:
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def sha256_hex(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def sign(v: Fraction) -> int:
    if v > 0:
        return 1
    if v < 0:
        return -1
    return 0


def solve_onshell(free: Sequence[Fraction]) -> Tuple[Fraction, ...]:
    s = sum(free)
    if s == 0:
        raise ValueError("sum free is zero")
    ss = sum(SIG[i + 1] * free[i] * free[i] for i in range(4))
    w6 = -(SIG[0] * s * s + ss) / (2 * SIG[0] * s)
    w1 = -(s + w6)
    return (w1, free[0], free[1], free[2], free[3], w6)


def full_sign_and_margin(omega: Sequence[Fraction]) -> Tuple[Tuple[int, ...], Fraction]:
    a = [omega[i] * omega[i] for i in range(3)]
    b = [omega[3 + j] * omega[3 + j] for j in range(3)]
    sv: List[int] = []
    vals: List[Fraction] = []
    for i in range(3):
        for j in range(3):
            v = a[i] - b[j]
            sv.append(sign(v))
            vals.append(abs(v))
    total = sum(a)
    for i in range(3):
        for j in range(3):
            v = a[i] + b[j] - total
            sv.append(sign(v))
            vals.append(abs(v))
    for r in (2, 3):
        for S in combinations(range(6), r):
            wS = sum(omega[i] for i in S)
            kS = sum(SIG[i] * omega[i] * omega[i] for i in S)
            h = wS * wS - (kS if kS >= 0 else -kS)
            sv.append(sign(h))
            vals.append(abs(h))
    scale = sum(w * w for w in omega)
    margin = min(vals) / scale if scale else Fraction(0)
    return tuple(sv), margin


def is_generic(omega: Sequence[Fraction]) -> bool:
    if any(x == 0 for x in omega):
        return False
    sq = sorted(x * x for x in omega)
    return all(sq[i] != sq[i + 1] for i in range(5))


def monomials_upto(total_degree: int) -> List[Tuple[int, int, int]]:
    return [
        (a, b, c)
        for a in range(total_degree + 1)
        for b in range(total_degree + 1 - a)
        for c in range(total_degree + 1 - a - b)
    ]


def mod_of(fr: Fraction, p: int) -> int:
    num = fr.numerator % p
    den = fr.denominator % p
    if den == 0:
        raise ZeroDivisionError("zero modular denominator")
    return (num * pow(den, p - 2, p)) % p


def build_matrix(pts: Sequence[Tuple[Fraction, Fraction, Fraction, Fraction]],
                 monP: Sequence[Tuple[int, int, int]],
                 monQ: Sequence[Tuple[int, int, int]],
                 p: int) -> np.ndarray:
    nrow = len(pts)
    nmP = len(monP)
    nmQ = len(monQ)
    ncol = nmP + nmQ
    if nrow == 0:
        return np.zeros((0, ncol), dtype=np.int64)

    maxa = max(max(a for a, _, _ in monP), max(a for a, _, _ in monQ)) if ncol else 0
    maxb = max(max(b for _, b, _ in monP), max(b for _, b, _ in monQ)) if ncol else 0
    maxc = max(max(c for _, _, c in monP), max(c for _, _, c in monQ)) if ncol else 0
    X = np.empty((nrow, ncol), dtype=np.int64)

    for r, (x, y, z, h) in enumerate(pts):
        xm = mod_of(x, p)
        ym = mod_of(y, p)
        zm = mod_of(z, p)
        hm = mod_of(h, p)

        xp = [1] * (maxa + 1)
        yp = [1] * (maxb + 1)
        zp = [1] * (maxc + 1)
        for e in range(1, maxa + 1):
            xp[e] = (xp[e - 1] * xm) % p
        for e in range(1, maxb + 1):
            yp[e] = (yp[e - 1] * ym) % p
        for e in range(1, maxc + 1):
            zp[e] = (zp[e - 1] * zm) % p

        rowP = np.empty(nmP, dtype=np.int64)
        for i, (a, b, c) in enumerate(monP):
            rowP[i] = (xp[a] * yp[b] % p) * zp[c] % p
        rowQ = np.empty(nmQ, dtype=np.int64)
        for i, (a, b, c) in enumerate(monQ):
            rowQ[i] = (-(hm % p) * (xp[a] * yp[b] % p) % p) * zp[c] % p
        X[r, :nmP] = rowP
        X[r, nmP:] = rowQ % p
    return X


def rref_rank_nullspace(M: np.ndarray, p: int):
    A = np.array(M, dtype=np.int64, copy=True) % p
    m, n = A.shape
    row = 0
    pivots: List[int] = []
    for col in range(n):
        nz = np.nonzero(A[row:, col] % p)[0]
        if len(nz) == 0:
            continue
        pr = row + int(nz[0])
        if pr != row:
            A[[row, pr], :] = A[[pr, row], :]
        inv = pow(int(A[row, col]), p - 2, p)
        A[row, :] = (A[row, :] * inv) % p

        cv = A[:, col].copy()
        for rr in range(m):
            if rr == row:
                continue
            fac = cv[rr]
            if fac == 0:
                continue
            A[rr, :] = (A[rr, :] - fac * A[row, :]) % p
        pivots.append(col)
        row += 1
        if row == m:
            break

    pivot_set = set(pivots)
    free = [c for c in range(n) if c not in pivot_set]
    if len(free) == 0:
        return row, []

    basis = []
    for fc in free:
        vec = [0] * n
        vec[fc] = 1
        for pr, pc in reversed(list(zip(range(len(pivots)), pivots))):
            vec[pc] = (-int(A[pr, fc])) % p
        basis.append(vec)
    return row, basis


def crt_pair(a1: int, m1: int, a2: int, m2: int) -> Tuple[int, int]:
    inv = pow(m1 % m2, m2 - 2, m2)
    x = (a1 + m1 * ((a2 - a1) * inv % m2)) % (m1 * m2)
    return x, m1 * m2


def rat_recon(u: int, M: int):
    bound = int((M // 2) ** 0.5)
    r0, r1 = M, u % M
    s0, s1 = 0, 1
    while r1 > bound:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
    if s1 < 0:
        r1, s1 = -r1, -s1
    if r1 == 0 or s1 == 0 or abs(r1) > bound or abs(s1) > bound:
        return None
    return Fraction(int(r1), int(s1))


def reconstruct_coefficients(
    monP: Sequence[Tuple[int, int, int]],
    monQ: Sequence[Tuple[int, int, int]],
    basis_by_prime: Dict[int, List[int]],
) -> Tuple[List[Fraction], Dict[str, object]]:
    ncol = len(monP) + len(monQ)
    report: Dict[str, object] = {
        "status": "pending",
        "primes_used": [],
        "nullity_per_prime": {},
        "failed_coords": [],
        "details": [],
    }

    primed = sorted(basis_by_prime.keys())
    if not primed:
        report["status"] = "no_bases"
        return [], report

    def _entry_to_vector(v):
        if not isinstance(v, Sequence) or len(v) == 0:
            raise ValueError("null-vector entry is empty")
        if isinstance(v[0], Sequence):
            if len(v) != 1:
                raise ValueError("nullspace must be one-dimensional")
            # canonical format is [vector], as returned by rref_rank_nullspace
            return 1, list(v[0])
        return 1, list(v)

    free_dims = {}
    for p, vs in basis_by_prime.items():
        free_dim, _ = _entry_to_vector(vs)
        free_dims[p] = free_dim

    if any(n != 1 for n in free_dims.values()):
        report["status"] = "non_unique_nullspace"
        report["nullity_per_prime"] = free_dims
        return [], report

    vecs = [_entry_to_vector(basis_by_prime[p])[1] for p in primed]
    j0 = None
    for c in range(ncol):
        if all(v[c] % p != 0 for p, v in zip(primed, vecs)):
            j0 = c
            break
    if j0 is None:
        report["status"] = "no_normalization_coordinate"
        return [], report

    norm: Dict[int, List[int]] = {}
    for p, v in zip(primed, vecs):
        inv = pow(v[j0], p - 2, p)
        norm[p] = [int(x) * inv % p for x in v]

    coeffs: List[Fraction] = [Fraction(0, 1)] * ncol
    M = 1
    residues = [0] * ncol
    for idx in range(ncol):
        r, Mcur = 0, 1
        for p in primed:
            r, Mcur = crt_pair(r, Mcur, norm[p][idx], p)
        residues[idx], M = r % Mcur, Mcur

    failed = []
    for k in range(ncol):
        fr = rat_recon(residues[k], M)
        if fr is None:
            failed.append(k)
        else:
            coeffs[k] = fr
    if failed:
        report["status"] = "rational_reconstruction_failed"
        report["failed_coords"] = failed[:10]
        return [], report
    report["status"] = "ok"
    report["primes_used"] = primed
    report["modulus"] = M
    return coeffs, report


def run_smoke_checks() -> Dict[str, object]:
    p1 = PRIMES_31[0]
    p2 = PRIMES_31[1]
    monP = [(0, 0, 0)]
    monQ = [(0, 0, 0)]
    vec_p1 = [1, p1 - 1]  # [1, -1] mod p1
    vec_p2 = [1, p2 - 1]  # [1, -1] mod p2

    list_entry, rr1 = reconstruct_coefficients(monP, monQ, {p1: [vec_p1], p2: [vec_p2]})
    flat_entry, rr2 = reconstruct_coefficients(monP, monQ, {p1: vec_p1, p2: vec_p2})
    ok = bool(list_entry) and bool(flat_entry)
    if ok:
        ok = (list_entry[0] == 1 and list_entry[1] == -1
              and flat_entry[0] == 1 and flat_entry[1] == -1)
    return {
        "status": "ok" if ok else "fail",
        "list_entry_ok": rr1["status"],
        "flat_entry_ok": rr2["status"],
        "list_entry_coeffs": [frac_to_str(x) for x in list_entry] if list_entry else [],
        "flat_entry_coeffs": [frac_to_str(x) for x in flat_entry] if flat_entry else [],
    }


def poly_eval(coeffs: Sequence[Fraction], mon: Sequence[Tuple[int, int, int]],
             x_pow: Sequence[Sequence[Fraction]], y_pow: Sequence[Sequence[Fraction]], z_pow: Sequence[Sequence[Fraction]]) -> List[Fraction]:
    out: List[Fraction] = []
    for xp, yp, zp in zip(x_pow, y_pow, z_pow):
        s = Fraction(0, 1)
        for c, (a, b, cexp) in zip(coeffs, mon):
            if c == 0:
                continue
            s += c * xp[a] * yp[b] * zp[cexp]
        out.append(s)
    return out


def validate_exact(pts: Sequence[Tuple[Fraction, Fraction, Fraction, Fraction]],
                  monP, monQ, cP, cQ):
    deg = max(max(a for a, _, _ in monP + monQ), max(b for _, b, _ in monP + monQ),
              max(c for _, _, c in monP + monQ))
    xp = [[Fraction(1)] for _ in pts]
    yp = [[Fraction(1)] for _ in pts]
    zp = [[Fraction(1)] for _ in pts]
    for i, (x, y, z, _) in enumerate(pts):
        xp[i] = [Fraction(1)]
        yp[i] = [Fraction(1)]
        zp[i] = [Fraction(1)]
        for e in range(1, deg + 1):
            xp[i].append(xp[i][-1] * x)
            yp[i].append(yp[i][-1] * y)
            zp[i].append(zp[i][-1] * z)

    Pvals = poly_eval(cP, monP, xp, yp, zp)
    Qvals = poly_eval(cQ, monQ, xp, yp, zp)
    bad = 0
    skipped = 0
    for (x, y, z, h), pv, qv in zip(pts, Pvals, Qvals):
        if qv == 0:
            skipped += 1
            continue
        if pv != h * qv:
            bad += 1
    return {
        "checked": len(pts) - skipped,
        "bad": bad,
        "skipped_q_zero": skipped,
    }


def build_polys(monP, monQ, coeffs, x, y, z):
    nmP = len(monP)
    cP = coeffs[:nmP]
    cQ = coeffs[nmP:]
    P = sp.Integer(0)
    Q = sp.Integer(0)
    for c, (a, b, cex) in zip(cP, monP):
        cc = sp.Rational(c.numerator, c.denominator)
        if cc != 0:
            P += cc * x ** a * y ** b * z ** cex
    for c, (a, b, cex) in zip(cQ, monQ):
        cc = sp.Rational(c.numerator, c.denominator)
        if cc != 0:
            Q += cc * x ** a * y ** b * z ** cex
    return sp.expand(P), sp.expand(Q)


def analyze_factors(Qpoly):
    x, y, z = sp.symbols("x y z")
    A_FACTORS = {
        "x": x,
        "x+y": x + y,
        "x+z": x + z,
        "y+1": y + 1,
        "z+1": z + 1,
        "BM": x ** 2 + x * y + x * z + x + y * z + y + z + 1,
        "BP": x * y + x * z + x + y ** 2 + y * z + y + z ** 2 + z,
    }
    Qfactor_list = sp.factor_list(Qpoly)
    facs = [(sp.expand(f), int(e)) for f, e in Qfactor_list[1] if not f.is_Number]
    assoc = defaultdict(int)

    def are_associate(u, v) -> bool:
        ratio = sp.cancel(sp.expand(u / v))
        return ratio.is_Number and ratio != 0

    for k, v in A_FACTORS.items():
        mult = 0
        for f, e in facs:
            try:
                if are_associate(f, v):
                    mult += e
            except Exception:
                continue
        assoc[k] = mult

    residual = []
    for f, e in facs:
        is_new = True
        for v in A_FACTORS.values():
            if are_associate(f, v):
                is_new = False
                break
        if is_new:
            residual.append({"factor": str(f), "power": e})
    return {
        "a_piece_factors": {k: assoc[k] for k in sorted(A_FACTORS)},
        "residual_factors": residual,
        "factorQ": str(sp.factor(Qpoly)),
        "factor_list": [{"factor": str(f), "power": e} for f, e in facs],
    }


def max_div_exp(poly_expr, cand_expr, x, y, z) -> int:
    expr = sp.expand(poly_expr)
    cand = sp.expand(cand_expr)
    if cand == 0:
        return 0
    e = 0
    r = expr
    while True:
        q, rem = sp.div(r, cand, x, y, z)
        if sp.expand(rem) != 0:
            break
        e += 1
        r = sp.expand(q)
    return e


def candidate_audit(Qpoly, points_om_sign=None):
    x, y, z = sp.symbols("x y z")
    w2 = sp.Integer(1)
    w3, w4, w5 = x, y, z
    s = w2 + w3 + w4 + w5
    ss = SIG[0] * w2 ** 2 + SIG[1] * w3 ** 2 + SIG[2] * w4 ** 2 + SIG[3] * w5 ** 2
    w6 = -(SIG[0] * s * s + ss) / (2 * SIG[0] * s)
    w1 = -(s + w6)
    omega = [w1, w2, w3, w4, w5, w6]

    omega_base = None
    if points_om_sign is not None and len(points_om_sign) >= 4:
        base_om = solve_onshell(points_om_sign)
        omega_base = base_om

    kS_sign = None
    w2345 = w2 + w3 + w4 + w5
    if omega_base is not None:
        # base branch of h_2345 is W^2 - sign* K where sign = sign(K) so that abs(K)=sign*K
        K2345 = sum(SIG[i] * omega_base[i] ** 2 for i in (1, 2, 3, 4))
        kS_sign = 1 if K2345 >= 0 else -1

    if kS_sign is None:
        kS_sign = 1

    out = {"triple_W": [], "triple_propagator": [], "h_2345": []}
    for S in combinations(range(6), 3):
        S_name = "".join(str(i + 1) for i in S)
        W = sum(omega[i] for i in S)
        K = sum(SIG[i] * omega[i] * omega[i] for i in S)
        # W itself as candidate
        numW = sp.fraction(sp.together(W))[0]
        numW = sp.expand(numW)
        out["triple_W"].append({
            "subset": S_name,
            "expr": str(sp.expand(W)),
            "numerator_poly": str(numW),
            "divides_Q": (sp.rem(Qpoly, numW, x, y, z) == 0),
            "multiplicity": max_div_exp(Qpoly, numW, x, y, z),
        })
        for sign_name, sign_val in (("+", 1), ("-", -1)):
            expr = W ** 2 + sign_val * K
            num = sp.expand(sp.fraction(sp.together(expr))[0])
            out["triple_propagator"].append({
                "subset": S_name,
                "branch": f"{sign_name}",
                "expr": str(sp.expand(expr)),
                "numerator_poly": str(num),
                "divides_Q": (sp.rem(Qpoly, num, x, y, z) == 0),
                "multiplicity": max_div_exp(Qpoly, num, x, y, z),
            })

    if omega_base is not None:
        # S={2,3,4,5} -> h_2345 branch used by 12ea data's h16-sign difference
        W = w2345
        K = sum(SIG[i] * omega[i] * omega[i] for i in (1, 2, 3, 4))
        expr = W ** 2 + (-kS_sign) * K
        num = sp.expand(sp.fraction(sp.together(expr))[0])
        out["h_2345"].append({
            "subset": "2345",
            "branch": f"{' - ' if kS_sign == 1 else ' + '}",
            "expr": str(sp.expand(expr)),
            "numerator_poly": str(num),
            "divides_Q": (sp.rem(Qpoly, num, x, y, z) == 0),
            "multiplicity": max_div_exp(Qpoly, num, x, y, z),
        })

    return out


def ensure_bg_copy_and_compile(force: bool = False, log_lines: List[str] = None):
    log_lines = [] if log_lines is None else log_lines
    if force or (not LOCAL_BG_CPP.exists()) or QUESTION_BG_SRC.stat().st_mtime > LOCAL_BG_CPP.stat().st_mtime:
        shutil.copy2(QUESTION_BG_SRC, LOCAL_BG_CPP)
        log_lines.append(f"copied bg.cpp -> {LOCAL_BG_CPP}")
    need_build = force or (not LOCAL_BG_BIN.exists()) or LOCAL_BG_BIN.stat().st_mtime < LOCAL_BG_CPP.stat().st_mtime
    if need_build:
        p = subprocess.run(
            ["g++", "-O2", "-std=c++17", "-o", str(LOCAL_BG_BIN), str(LOCAL_BG_CPP), "-lgmpxx", "-lgmp"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        if p.returncode != 0:
            raise RuntimeError(f"bg_s1_r8 build failed: {p.stderr.strip()}")
        log_lines.append(f"built {LOCAL_BG_BIN}")
    return {
        "bg_src": str(QUESTION_BG_SRC),
        "bg_copy": str(LOCAL_BG_CPP),
        "bg_bin": str(LOCAL_BG_BIN),
        "bg_src_sha256": sha256_hex(QUESTION_BG_SRC),
        "bg_copy_sha256": sha256_hex(LOCAL_BG_CPP),
        "build_log": log_lines,
    }


def parse_bg_output(text: str) -> Fraction:
    m = re.search(r"A_6 = i \* \(([^)]*)\)", text)
    if m:
        return frac_from_json(m.group(1))
    m2 = re.search(r"A_6 = \(([^)]*)\) \+ i \* \(([^)]*)\)", text)
    if m2 and frac_from_json(m2.group(1)) == 0:
        return frac_from_json(m2.group(2))
    raise RuntimeError("unexpected bg output format")


def persist_points_with_audit(path: Path, base_f: Sequence[Fraction], base_sg: Sequence[int],
                             pts: Sequence[Tuple[Fraction, Fraction, Fraction, Fraction]]) -> Dict[str, object]:
    path.parent.mkdir(parents=True, exist_ok=True)
    entries = [[frac_to_str(v) for v in pt] for pt in pts]
    payload = {
        "base_f": [frac_to_str(v) for v in base_f],
        "base_sg": [int(x) for x in base_sg],
        "pts": entries,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    mismatch = 0
    for x, y, z, _ in pts:
        try:
            om = solve_onshell([Fraction(1), x, y, z])
            sg, _ = full_sign_and_margin(om)
            if tuple(int(v) for v in sg) != tuple(base_sg):
                mismatch += 1
        except Exception:
            mismatch += 1
    distinct = len({(x, y, z) for x, y, z, _ in pts})
    digest = {
        "path": str(path),
        "count_points": len(pts),
        "count_distinct_xyz": distinct,
        "reaudit_total": len(pts),
        "reaudit_matched": len(pts) - mismatch,
        "reaudit_mismatch": mismatch,
        "sha256": sha256_hex(path),
    }
    return digest


def bg_h_at_free(free: Sequence[Fraction], log_cache: Dict[Tuple[str, ...], Fraction]) -> Fraction:
    key = tuple(str(x) for x in free)
    if key in log_cache:
        return log_cache[key]
    omega = solve_onshell(free)
    mom = ",".join(frac_to_str(SIG[i] * omega[i] * omega[i]) for i in range(6))
    wts = ",".join(frac_to_str(w) for w in omega)
    p = subprocess.run(
        [str(LOCAL_BG_BIN), "--amp", "-K", mom, "-W", wts],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    if p.returncode != 0:
        raise RuntimeError(p.stderr or p.stdout)
    A6 = parse_bg_output(p.stdout)
    prod = Fraction(1)
    for w in omega:
        prod *= w
    h = A6 / prod
    h = h / (free[0] * free[0])
    log_cache[key] = h
    return h


def collect_points(base_free: Sequence[Fraction], base_sg: Sequence[int], need_total: int,
                  seed: int, log: List[dict],
                  cache: Dict[Tuple[str, ...], Fraction],
                  existing_points: List[Tuple[Fraction, Fraction, Fraction, Fraction]] = None) -> List[Tuple[Fraction, Fraction, Fraction, Fraction]]:
    if existing_points is None:
        existing_points = []
    pts: List[Tuple[Fraction, Fraction, Fraction, Fraction]] = list(existing_points)
    seen = set((x, y, z) for x, y, z, _ in existing_points)
    rng = random.Random(seed)
    denoms = [3, 4, 5, 6, 7, 8, 11, 13, 17]
    attempts = 0
    while len(pts) < need_total and attempts < 6_000_000:
        attempts += 1
        den = rng.choice(denoms)
        free = [base_free[i] + Fraction(rng.randint(-11, 11), den) for i in range(4)]
        if any(x == 0 for x in free) or sum(free) == 0:
            continue
        try:
            om = solve_onshell(free)
        except Exception:
            continue
        if not is_generic(om):
            continue
        sg, margin = full_sign_and_margin(om)
        if sg != tuple(base_sg) or margin == 0:
            continue
        try:
            h = bg_h_at_free(free, cache)
        except Exception:
            continue
        x = free[1] / free[0]
        y = free[2] / free[0]
        z = free[3] / free[0]
        if (x, y, z) in seen:
            continue
        seen.add((x, y, z))
        pts.append((x, y, z, h))
        if len(pts) and len(pts) % 100 == 0:
            log.append({"event": "collect", "count": len(pts), "attempts": attempts})
    if len(pts) < need_total:
        raise RuntimeError(f"collected only {len(pts)}/{need_total} in-piece points (tries={attempts})")
    return pts


def write_log(log_path: Path, lines: List[str]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_scan(pts, d: int, prime_list: Sequence[int], *, equal_bound: bool = False):
    monP = monomials_upto(d)
    monQ = monomials_upto(d if equal_bound else d - 2)
    ncol = len(monP) + len(monQ)
    q_deg = d if equal_bound else d - 2
    fit_rows = min(len(pts), ncol + 60)
    fit_pts = pts[:fit_rows]
    row = {}
    basis = {}
    for p in prime_list:
        M = build_matrix(fit_pts, monP, monQ, p)
        rk, ns = rref_rank_nullspace(M, p)
        row[str(p)] = {
            "rank": int(rk),
            "nullity": int(ncol - rk),
            "rows": int(len(fit_pts)),
            "cols": int(ncol),
            "basis_dim": len(ns),
            "success": len(ns) > 0,
        }
        basis[p] = ns
    return {
        "d": d,
        "monP": len(monP),
        "monQ": len(monQ),
        "monQ_degree": q_deg,
        "ncols": ncol,
        "fit_rows": fit_rows,
        "holdout_rows": len(pts) - fit_rows,
        "prime_results": row,
        "unique_basis": all(entry["basis_dim"] == 1 for entry in row.values()),
        "basis_by_prime": basis,
    }


def read_points_file(path: Path):
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    base_f = [frac_from_json(x) for x in data["base_f"]]
    base_sg = tuple(int(x) for x in data["base_sg"])
    pts = [(frac_from_json(x), frac_from_json(y), frac_from_json(z), frac_from_json(h)) for x, y, z, h in data["pts"]]
    return base_f, base_sg, pts


def _job_id():
    return strftime("r8_eq_%Y%m%dT%H%M%SZ", gmtime())


def launch_detached(cmd: Sequence[str], result_path: Path, note: str, *, blocking: bool = False) -> str:
    jobs = ROOT / "jobs"
    jobs.mkdir(exist_ok=True)
    jid = _job_id()
    done = jobs / f"{jid}.done"
    fail = jobs / f"{jid}.fail"
    logp = jobs / f"{jid}.log"
    payload = {
        "id": jid,
        "launched_by": "student-1",
        "cmd": " ".join(shlex.quote(x) for x in cmd),
        "run_ref": str(os.getpid()),
        "result_path": str(result_path),
        "blocking": bool(blocking),
        "note": note,
    }
    with open(jobs / f"{jid}.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    quoted_cmd = " ".join(shlex.quote(x) for x in cmd)
    shell_cmd = (
        f"cd {shlex.quote(str(ROOT))} && {quoted_cmd} > {shlex.quote(str(logp))} 2>&1; "
        f"rc=$?; if [ $rc -eq 0 ]; then touch {shlex.quote(str(done))}; else touch {shlex.quote(str(fail))}; fi"
    )
    subprocess.Popen(["bash", "-lc", shell_cmd], preexec_fn=os.setsid)
    return jid


def run(
    points_path: Path,
    result_path: Path,
    qp_path: Path,
    log_path: Path,
    target_total: int = 1250,
    topup: bool = False,
    force_detach: bool = False,
    equal_result_path: Path = None,
    equal_qp_path: Path = None,
    equal_log_path: Path = None,
) -> Dict[str, object]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    _ = force_detach
    if equal_result_path is None:
        equal_result_path = DEFAULT_EQUAL_RESULT
    if equal_qp_path is None:
        equal_qp_path = DEFAULT_EQUAL_QP
    if equal_log_path is None:
        equal_log_path = DEFAULT_EQUAL_LOG
    log_lines: List[str] = []
    t0 = time()
    payload: Dict[str, object] = {
        "utc": utc_timestamp(),
        "points_source": str(points_path),
        "target_signature": "12ea165a03",
    }
    smoke = run_smoke_checks()
    payload["self_test"] = smoke
    if smoke["status"] != "ok":
        raise RuntimeError(f"internal smoke check failed: {smoke}")

    base_f, base_sg, pts = read_points_file(points_path)
    payload["initial_points"] = len(pts)
    payload["equal_mode"] = {
        "requested": True,
        "points_1250_source": str(TOPUP_POINTS),
        "points_1450_source": str(TOPUP_POINTS_1450),
    }
    # d12 and d13 scan
    scan12 = run_scan(pts, 12, PRIMES_31[:2])
    scan13 = run_scan(pts, 13, PRIMES_31[:2])
    payload["scan"] = {
        "d12": scan12,
        "d13": scan13,
    }
    payload["scan_order"] = ["d12", "d13"]
    payload["npoints_used"] = len(pts)
    payload["top_up_performed"] = False

    log_lines.append(f"d12: ncol={scan12['ncols']} fit={scan12['fit_rows']} null={scan12['prime_results'][str(PRIMES_31[0])]['nullity']} | {scan12['prime_results'][str(PRIMES_31[1])]['nullity']}")
    log_lines.append(f"d13: ncol={scan13['ncols']} fit={scan13['fit_rows']} null={scan13['prime_results'][str(PRIMES_31[0])]['nullity']} | {scan13['prime_results'][str(PRIMES_31[1])]['nullity']}")

    rec_degree = None
    coeffs: List[Fraction] = []
    monP: List[Tuple[int, int, int]] = []
    monQ: List[Tuple[int, int, int]] = []
    recon_report = {"status": "not_found"}
    def try_reconstruct(scan_entry, d: int, monQ_degree: int, validate_pts, prime_label: str = None):
        monP_ = monomials_upto(d)
        monQ_ = monomials_upto(monQ_degree)
        basis_by_prime: Dict[int, List[int]] = {}
        for p in sorted(scan_entry["basis_by_prime"].keys()):
            ns = scan_entry["basis_by_prime"].get(p, [])
            if not ns:
                return None, {"status": "no_nonzero_nullvec", "d": d, "prime": p}
            if len(ns) != 1:
                return None, {"status": "non_unique", "d": d, "nullity": scan_entry["prime_results"][str(p)]["nullity"]}
            basis_by_prime[p] = ns
        c, rr = reconstruct_coefficients(monP_, monQ_, basis_by_prime)
        if not c:
            return None, rr
        stats = validate_exact(validate_pts, monP_, monQ_, c[:len(monP_)], c[len(monP_):])
        rr["prime_set"] = prime_label or str(sorted(scan_entry["basis_by_prime"].keys()))
        return (c, monP_, monQ_, stats), rr

    if scan13["prime_results"][str(PRIMES_31[0])]["nullity"] > 0 and scan13["prime_results"][str(PRIMES_31[1])]["nullity"] > 0:
        scan13_full = run_scan(pts, 13, PRIMES_31)
        payload["scan"]["d13_all5"] = scan13_full
        rec, rr = try_reconstruct(scan13_full, 13, 11, pts, prime_label="all5")
        if rec is not None:
            coeffs, monP, monQ, stats = rec
            rec_degree = 13
            recon_report = {
                "status": "found",
                "degree": 13,
                "rank_scan": scan13,
                "rank_scan_all5": scan13_full,
                "coeff_recon": rr,
                "validation": stats,
            }
        else:
            payload.setdefault("reconstruction_notes", []).append({
                "stage": "d13",
                "status": "all5_reconstruction_failed",
                "detail": rr,
            })
    if rec_degree is None and scan12["prime_results"][str(PRIMES_31[0])]["nullity"] > 0 and scan12["prime_results"][str(PRIMES_31[1])]["nullity"] > 0:
        rec, rr = try_reconstruct(scan12, 12, 10, pts, prime_label="scan2")
        if rec is not None:
            coeffs, monP, monQ, stats = rec
            rec_degree = 12
            recon_report = {
                "status": "found",
                "degree": 12,
                "rank_scan": scan12,
                "coeff_recon": rr,
                "validation": stats,
            }

    if rec_degree is None and topup and len(pts) < target_total:
        bg_meta = ensure_bg_copy_and_compile(force=False, log_lines=log_lines)
        payload["bg_build"] = bg_meta
        payload["topup_requested"] = {
            "target_points": target_total,
            "existing_points": len(pts),
        }
        log_lines.append(f"collecting in-piece points to {target_total} (base points={len(pts)})")
        payload["scan_order"] = ["d12", "d13", "d14_topup"]
        payload["top_up_performed"] = True
        bg_cache: Dict[Tuple[str, ...], Fraction] = {}
        pts = collect_points(
            base_f,
            base_sg,
            target_total,
            4242,
            [],
            bg_cache,
            existing_points=[(x, y, z, h) for x, y, z, h in pts],
        )
        topup_audit = persist_points_with_audit(TOPUP_POINTS, base_f, base_sg, pts)
        payload["topup_points_audit"] = topup_audit
        payload["topped_up_points"] = len(pts)
        payload["npoints_used"] = len(pts)
        scan14_3 = run_scan(pts, 14, PRIMES_31[:3])
        payload["scan"]["d14_topup"] = scan14_3
        null2_14 = scan14_3["prime_results"][str(PRIMES_31[0])]["nullity"] > 0 and scan14_3["prime_results"][str(PRIMES_31[1])]["nullity"] > 0
        log_lines.append(f"d14_topup: ncol={scan14_3['ncols']} fit={scan14_3['fit_rows']} null_p0={scan14_3['prime_results'][str(PRIMES_31[0])]['nullity']} null_p1={scan14_3['prime_results'][str(PRIMES_31[1])]['nullity']} null_p2={scan14_3['prime_results'][str(PRIMES_31[2])]['nullity']}")
        if null2_14:
            scan14_full = run_scan(pts, 14, PRIMES_31)
            payload["scan"]["d14_all5"] = scan14_full
            rec, rr = try_reconstruct(scan14_full, 14, 12, pts, prime_label="all5")
            if rec is not None:
                coeffs, monP, monQ, stats = rec
                rec_degree = 14
                recon_report = {
                    "status": "found",
                    "degree": 14,
                    "rank_scan": scan14_3,
                    "rank_scan_all5": scan14_full,
                    "coeff_recon": rr,
                    "validation": stats,
                }
            else:
                payload.setdefault("reconstruction_notes", []).append({
                    "stage": "d14",
                    "status": "all5_reconstruction_failed",
                    "detail": rr,
                    "scan_all5": scan14_full,
                })
        else:
            payload.setdefault("reconstruction_notes", []).append({
                "stage": "d14",
                "status": "nullity_zero_on_topup_3primes",
                "scan_topup_3primes": {
                    "prime0": scan14_3["prime_results"][str(PRIMES_31[0])]["nullity"],
                    "prime1": scan14_3["prime_results"][str(PRIMES_31[1])]["nullity"],
                    "prime2": scan14_3["prime_results"][str(PRIMES_31[2])]["nullity"],
                    "rank0": scan14_3["prime_results"][str(PRIMES_31[0])]["rank"],
                    "rank1": scan14_3["prime_results"][str(PRIMES_31[1])]["rank"],
                    "rank2": scan14_3["prime_results"][str(PRIMES_31[2])]["rank"],
                    "rows": scan14_3["fit_rows"],
                    "cols": scan14_3["ncols"],
                    "points": len(pts),
                },
                "lower_degree_bound": 15,
            })

    if rec_degree is None and payload.get("top_up_performed", False):
        payload["degree_lower_bound"] = {
            "min_numerator_degree": 15,
            "min_denominator_degree": 13,
            "reason": "excluded by d14-topup scan; excluded rectangle degP<=14, degQ<=12, homogeneous form bound applies",
        }

    payload["reconstruction"] = recon_report

    def write_reconstruction_payload(target_payload: Dict[str, object], coeffs: Sequence[Fraction],
                                   monP: Sequence[Tuple[int, int, int]],
                                   monQ: Sequence[Tuple[int, int, int]],
                                   validation_points: Sequence[Tuple[Fraction, Fraction, Fraction, Fraction]],
                                   qp_out: Path, result_note: str,
                                   base_ref: Sequence[Fraction]):
        if not coeffs:
            return
        x, y, z = sp.symbols("x y z")
        Ppoly, Qpoly = build_polys(monP, monQ, coeffs, x, y, z)
        Pc = sp.Poly(Ppoly, x, y, z)
        Qc = sp.Poly(Qpoly, x, y, z)
        gcd_poly = sp.expand(sp.gcd(Ppoly, Qpoly))
        factor_report = analyze_factors(Qpoly)
        target_payload["degrees"] = {
            "degP": int(Pc.total_degree()),
            "degQ": int(Qc.total_degree()),
            "gcd_degree": int(sp.Poly(gcd_poly, x, y, z).total_degree()) if gcd_poly != 0 else 0,
            "gcd_expr": str(gcd_poly),
        }
        target_payload["factor"] = factor_report
        target_payload["a_factor_audit"] = factor_report["a_piece_factors"]
        target_payload["candidate_factor_audit"] = candidate_audit(Qpoly, base_ref)
        validate = validate_exact(validation_points, monP, monQ, coeffs[:len(monP)], coeffs[len(monP):])
        target_payload["validation_full"] = validate

        qp_lines = [
            "Q=" + str(Qpoly),
            "\nfactorQ=" + factor_report["factorQ"],
            "\nP=" + str(Ppoly),
            "\nfactorP=" + str(sp.factor(Ppoly)),
        ]
        qp_out.parent.mkdir(parents=True, exist_ok=True)
        qp_out.write_text("".join(qp_lines), encoding="utf-8")

        target_payload["result_note"] = result_note

    if coeffs:
        write_reconstruction_payload(payload["reconstruction"], coeffs, monP, monQ, pts, qp_path, "asymmetric_homogeneous_scan", base_f)

    # Equal-bound branch (dehomogeneous mode with deg(P)=deg(Q)).
    equal_payload = {
        "status": "not_found",
        "mode": "equal_deg",
        "scan": {},
    }
    payload["equal_reconstruction"] = equal_payload

    equal_points_path = TOPUP_POINTS
    equal_loaded_from_default = False
    if equal_points_path.exists():
        equal_base_f, equal_base_sg, equal_pts = read_points_file(equal_points_path)
        if len(equal_pts) >= 1250:
            equal_loaded_from_default = True
        else:
            payload.setdefault("equal_notes", []).append({
                "stage": "equal_source",
                "status": "insufficient_points_in_default",
                "path": str(equal_points_path),
                "count": len(equal_pts),
            })
            equal_base_f, equal_base_sg, equal_pts = base_f, base_sg, pts
    else:
        equal_base_f, equal_base_sg, equal_pts = base_f, base_sg, pts

    if len(equal_pts) < 1250:
        if topup:
            bg_meta = ensure_bg_copy_and_compile(force=False, log_lines=log_lines)
            payload["bg_build_equal"] = bg_meta
            payload["equal_source"] = {
                "used_default_1250": False,
                "existing_points": len(equal_pts),
                "target_points": 1250,
            }
            bg_cache: Dict[Tuple[str, ...], Fraction] = {}
            equal_pts = collect_points(
                equal_base_f,
                equal_base_sg,
                1250,
                4242,
                [],
                bg_cache,
                existing_points=[(x, y, z, h) for x, y, z, h in equal_pts],
            )
            equal_topup_audit = persist_points_with_audit(TOPUP_POINTS, equal_base_f, equal_base_sg, equal_pts)
            payload["equal_topup_1250"] = equal_topup_audit
            log_lines.append(f"equal-mode collected to 1250 points: {len(equal_pts)}")
            equal_loaded_from_default = True
        else:
            equal_payload["status"] = "aborted"
            equal_payload["abort_reason"] = "insufficient_points_for_equal_d13 (need 1250)"
            payload["equal_reconstruction"] = equal_payload

    if equal_payload.get("status") != "aborted":
        equal_payload["scan"]["d13"] = run_scan(equal_pts, 13, PRIMES_31[:2], equal_bound=True)
        scan13_eq = equal_payload["scan"]["d13"]
        equal_payload["scan_order"] = ["d13_eq"]
        log_lines.append(f"d13_equal: ncol={scan13_eq['ncols']} fit={scan13_eq['fit_rows']} null={scan13_eq['prime_results'][str(PRIMES_31[0])]['nullity']} | {scan13_eq['prime_results'][str(PRIMES_31[1])]['nullity']}")
        equal_payload["points_source"] = str(equal_points_path)
        equal_payload["points_count"] = len(equal_pts)
        if equal_loaded_from_default:
            if "equal_topup_1250" in payload:
                equal_payload["points_audit_1250"] = payload["equal_topup_1250"]
            else:
                equal_payload["points_audit_1250"] = persist_points_with_audit(
                    equal_points_path,
                    equal_base_f,
                    equal_base_sg,
                    [(x, y, z, h) for x, y, z, h in equal_pts[:1250]],
                )

        d13_nullity = (
            scan13_eq["prime_results"][str(PRIMES_31[0])]["nullity"] > 0
            and scan13_eq["prime_results"][str(PRIMES_31[1])]["nullity"] > 0
            and scan13_eq["unique_basis"]
        )
        if d13_nullity:
            rec_eq_full = None
            try:
                scan13_eq_all5 = run_scan(equal_pts, 13, PRIMES_31, equal_bound=True)
                equal_payload["scan"]["d13_all5"] = scan13_eq_all5
                rec, rr = try_reconstruct(scan13_eq_all5, 13, 13, equal_pts, prime_label="all5")
                if rec is not None:
                    rec_eq_full = rec
                    eq_coeffs, eq_monP, eq_monQ, eq_stats = rec_eq_full
                    equal_payload["status"] = "found"
                    equal_payload["degree"] = 13
                    equal_payload["rank_scan"] = scan13_eq
                    equal_payload["rank_scan_all5"] = scan13_eq_all5
                    equal_payload["coeff_recon"] = rr
                    equal_payload["validation"] = eq_stats
                    write_reconstruction_payload(
                        equal_payload,
                        eq_coeffs,
                        eq_monP,
                        eq_monQ,
                        equal_pts[:1250],
                        equal_qp_path,
                        "equal_bound_d13",
                        equal_base_f,
                    )
                    payload["equal_reconstruction"] = equal_payload
                else:
                    payload.setdefault("equal_reconstruction_notes", []).append({
                        "stage": "d13_equal",
                        "status": "all5_reconstruction_failed",
                        "detail": rr,
                    })
            except Exception as e:
                payload.setdefault("equal_reconstruction_notes", []).append({
                    "stage": "d13_equal",
                    "status": "exception",
                    "detail": str(e),
                })
        else:
            # d13 equal nullity is zero: top-up to 1450 and try d14
            if len(equal_pts) < 1450 and topup:
                bg_meta = ensure_bg_copy_and_compile(force=True, log_lines=log_lines)
                payload["bg_build_equal"] = bg_meta
                bg_cache = {}
                equal_pts_1450 = collect_points(
                    equal_base_f,
                    equal_base_sg,
                    1450,
                    4242,
                    [],
                    bg_cache,
                    existing_points=[(x, y, z, h) for x, y, z, h in equal_pts],
                )
                equal_payload["points_count_1450"] = len(equal_pts_1450)
                equal_payload["scan_order"] = ["d13_eq", "d14_eq_topup"]
                d14_source_audit = persist_points_with_audit(TOPUP_POINTS_1450, equal_base_f, equal_base_sg, equal_pts_1450)
                payload["equal_topup_1450"] = d14_source_audit
                equal_payload["points_audit_1450"] = d14_source_audit
                log_lines.append(f"equal-mode collected to 1450 points: {len(equal_pts_1450)}")
                equal_pts_14 = equal_pts_1450
            else:
                equal_pts_14 = equal_pts[:1450] if len(equal_pts) >= 1450 else equal_pts

            if len(equal_pts_14) >= 1450:
                scan14_eq = run_scan(equal_pts_14, 14, PRIMES_31[:3], equal_bound=True)
                equal_payload["scan"]["d14_eq_topup"] = scan14_eq
                log_lines.append(f"d14_equal_topup: ncol={scan14_eq['ncols']} fit={scan14_eq['fit_rows']} null_p0={scan14_eq['prime_results'][str(PRIMES_31[0])]['nullity']} null_p1={scan14_eq['prime_results'][str(PRIMES_31[1])]['nullity']} null_p2={scan14_eq['prime_results'][str(PRIMES_31[2])]['nullity']}")
                null2_14 = (
                    scan14_eq["prime_results"][str(PRIMES_31[0])]["nullity"] > 0
                    and scan14_eq["prime_results"][str(PRIMES_31[1])]["nullity"] > 0
                    and scan14_eq["unique_basis"]
                )
                if null2_14:
                    scan14_eq_all5 = run_scan(equal_pts_14, 14, PRIMES_31, equal_bound=True)
                    equal_payload["scan"]["d14_equal_all5"] = scan14_eq_all5
                    rec, rr = try_reconstruct(scan14_eq_all5, 14, 14, equal_pts_14, prime_label="all5")
                    if rec is not None:
                        eq_coeffs, eq_monP, eq_monQ, eq_stats = rec
                        equal_payload["status"] = "found"
                        equal_payload["degree"] = 14
                        equal_payload["rank_scan"] = scan14_eq
                        equal_payload["rank_scan_all5"] = scan14_eq_all5
                        equal_payload["coeff_recon"] = rr
                        equal_payload["validation"] = eq_stats
                        write_reconstruction_payload(
                            equal_payload,
                            eq_coeffs,
                            eq_monP,
                            eq_monQ,
                            equal_pts_14,
                            equal_qp_path,
                            "equal_bound_d14",
                            equal_base_f,
                        )
                    else:
                        payload.setdefault("equal_reconstruction_notes", []).append({
                            "stage": "d14_equal",
                            "status": "all5_reconstruction_failed",
                            "detail": rr,
                        })
                else:
                    payload.setdefault("equal_reconstruction_notes", []).append({
                        "stage": "d14_equal",
                        "status": "nullity_zero_on_topup_3primes",
                        "scan_topup_3primes": {
                            "prime0": scan14_eq["prime_results"][str(PRIMES_31[0])]["nullity"],
                            "prime1": scan14_eq["prime_results"][str(PRIMES_31[1])]["nullity"],
                            "prime2": scan14_eq["prime_results"][str(PRIMES_31[2])]["nullity"],
                            "rank0": scan14_eq["prime_results"][str(PRIMES_31[0])]["rank"],
                            "rank1": scan14_eq["prime_results"][str(PRIMES_31[1])]["rank"],
                            "rank2": scan14_eq["prime_results"][str(PRIMES_31[2])]["rank"],
                            "rows": scan14_eq["fit_rows"],
                            "cols": scan14_eq["ncols"],
                            "points": len(equal_pts_14),
                        },
                        "lower_degree_bound": 15,
                    })
                    equal_payload["degree_lower_bound"] = {
                        "min_max_degree": 15,
                        "mode": "equal_bound",
                        "reason": "no representation with degP<=14 and degQ<=14",
                    }
            else:
                payload.setdefault("equal_reconstruction_notes", []).append({
                    "stage": "d14_equal",
                    "status": "insufficient_points",
                    "needed": 1450,
                    "provided": len(equal_pts_14),
                })

    payload["timing_sec"] = round(time() - t0, 3)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    with result_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    if rec_degree is not None:
        log_lines.append(f"reconstruction degree={rec_degree} succeeded")
        log_lines.append(
            f"degP={payload['reconstruction']['degrees']['degP']} degQ={payload['reconstruction']['degrees']['degQ']} "
            f"gcd={payload['reconstruction']['degrees']['gcd_expr']}"
        )
    else:
        log_lines.append(
            "no reconstruction relation found up to "
            + ("d14_topup" if payload.get("top_up_performed", False) else "d13")
            + " with available points"
        )
        log_lines.append(f"asymmetric_status={recon_report.get('status', 'not_found')}")

    equal_log_lines = list(log_lines)
    if equal_payload.get("status") == "found":
        equal_log_lines.append(
            f"equal_mode_degree={equal_payload.get('degree')} "
            f"status={equal_payload.get('status')}"
        )
    elif equal_payload.get("status") == "aborted":
        equal_log_lines.append(
            f"equal_mode_aborted: {equal_payload.get('abort_reason', 'unknown')}"
        )
    else:
        equal_log_lines.append(f"equal_mode_status={equal_payload.get('status', 'not_found')}")

    equal_result_payload = {
        "utc": utc_timestamp(),
        "target_signature": "12ea165a03",
        "source_points": str(equal_points_path) if "equal_points_path" in locals() else None,
        "equal_reconstruction": equal_payload,
    }
    if "d13_all5" in equal_payload.get("scan", {}):
        equal_result_payload["scan_d13_all5"] = equal_payload["scan"]["d13_all5"]
    if "d14_equal_all5" in equal_payload.get("scan", {}):
        equal_result_payload["scan_d14_all5"] = equal_payload["scan"]["d14_equal_all5"]
    equal_result_payload["timing_sec"] = payload["timing_sec"]
    with equal_result_path.open("w", encoding="utf-8") as f:
        json.dump(equal_result_payload, f, indent=2)

    write_log(log_path, log_lines)
    write_log(equal_log_path, equal_log_lines)
    return payload


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--points", default=str(POINTS_DEFAULT))
    p.add_argument("--result", default=str(DEFAULT_RESULT))
    p.add_argument("--qp", default=str(DEFAULT_QP))
    p.add_argument("--log", default=str(DEFAULT_LOG))
    p.add_argument("--equal-result", default=str(DEFAULT_EQUAL_RESULT))
    p.add_argument("--equal-qp", default=str(DEFAULT_EQUAL_QP))
    p.add_argument("--equal-log", default=str(DEFAULT_EQUAL_LOG))
    p.add_argument("--topup", action="store_true")
    p.add_argument("--topup-target", type=int, default=1250)
    p.add_argument("--force-detach", action="store_true", help="launch this scan as a detached non-blocking job")
    p.add_argument("--detached", action="store_true", help=argparse.SUPPRESS)
    args = p.parse_args()

    if args.force_detach and not args.detached:
        cmd = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--points", args.points,
            "--result", args.result,
            "--qp", args.qp,
            "--log", args.log,
            "--equal-result", args.equal_result,
            "--equal-qp", args.equal_qp,
            "--equal-log", args.equal_log,
            "--topup-target", str(args.topup_target),
            "--detached",
        ]
        if args.topup:
            cmd.append("--topup")
        if args.force_detach:
            cmd.append("--force-detach")
        jid = launch_detached(cmd, Path(args.result), "round8 higher-chamber reconstruction (asymmetric + equal scans)")
        print(f"launched job {jid} (non-blocking)")
        return

    run(Path(args.points), Path(args.result), Path(args.qp), Path(args.log),
        args.topup_target, args.topup, args.force_detach,
        equal_result_path=Path(args.equal_result),
        equal_qp_path=Path(args.equal_qp),
        equal_log_path=Path(args.equal_log))


if __name__ == "__main__":
    main()
