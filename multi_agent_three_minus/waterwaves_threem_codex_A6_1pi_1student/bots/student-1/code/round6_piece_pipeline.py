#!/usr/bin/env python3
"""Round-6 student-1 reconstruction pipeline for piecewise A6 data."""

import argparse
import hashlib
import json
import math
import os
import random
import re
import shutil
import subprocess
from fractions import Fraction as F
from itertools import combinations, combinations_with_replacement
from pathlib import Path
from time import gmtime, strftime, time

import numpy as np
import sympy as sp


def p_prod(values):
    result = 1
    for value in values:
        result *= value
    return result

SIG = (-1, -1, -1, 1, 1, 1)
P31 = (1 << 31) - 1
P61 = 2147483587
RANK_PRIMES = [P31, P61]
EXTRACT_PRIMES = [2147483647, 2147483629, 2147483587, 2147483563, 2147483399]

ROOT = Path(__file__).resolve().parent.parent.parent.parent
STUDENT_DIR = ROOT / "bots" / "student-1"
CODE_DIR = STUDENT_DIR / "code"
DATA_DIR = STUDENT_DIR / "data"
PIECE_DIR = DATA_DIR / "round6_pieces"
PIECE_DIR.mkdir(parents=True, exist_ok=True)
BG_SRC = CODE_DIR / "bg.cpp"
BG_CPP = CODE_DIR / "bg_s1_r6.cpp"
BG_BIN = CODE_DIR / "bg_s1_r6"
QP_A = ROOT / "bots" / "pi" / "code" / "round6_QP.txt"
QP_B = ROOT / "bots" / "pi" / "code" / "round6_QP_B.txt"

# Known A/B signs for excluding seeds when selecting new pieces.
# Signs are for (wall/pole signature + h2+h3 signatures) over all 53 checks.
KNOWN_AB_SIGNATURES = {
    (1, 1, -1, 1, 1, -1, 1, 1, -1, -1, -1, 1, -1, -1, 1, -1, -1, 1, -1, 1, 1, 1, -1, -1, -1, -1, 1, 1, 1, -1, 1, -1, -1, -1, -1, -1, 1, 1, 1, -1, 1, -1, -1, -1, -1, 1, -1, 1, 1, 1, -1, -1, -1),
    (1, 1, 1, -1, -1, -1, -1, -1, -1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, -1, 1, 1, -1, 1, -1, -1, -1, -1, -1, 1, -1, -1, 1, -1, 1, 1, 1, 1, -1, 1, -1, -1, 1, -1, -1, -1),
}

X, Y, Z = sp.symbols("x y z")
W2, W3, W4, W5 = sp.symbols("w2 w3 w4 w5")


def frac_to_str(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def to_fraction(x) -> F:
    if isinstance(x, F):
        return x
    if isinstance(x, sp.Rational):
        return F(x.p, x.q)
    if isinstance(x, int):
        return F(x, 1)
    if isinstance(x, np.integer):
        return F(int(x), 1)
    if isinstance(x, float):
        return F(str(x))
    if isinstance(x, str):
        return F(x)
    if hasattr(x, "p") and hasattr(x, "q"):
        try:
            return F(int(x.p), int(x.q))
        except Exception:
            pass
    if hasattr(x, "as_numer_denom"):
        n, d = x.as_numer_denom()
        return to_fraction(n) / to_fraction(d)
    return F(x)


def sign_of(x: F) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def solve_from_free(free):
    free = [F(v) for v in free]
    s = sum(free)
    if s == 0:
        raise ValueError("free sum is zero")
    ss = sum(SIG[i + 1] * free[i] * free[i] for i in range(4))
    w6 = -(SIG[0] * s * s + ss) / (2 * SIG[0] * s)
    w1 = -(s + w6)
    return (w1, free[0], free[1], free[2], free[3], w6)


def is_generic(omega):
    if any(w == 0 for w in omega):
        return False
    sq = sorted(w * w for w in omega)
    return all(sq[i] != sq[i + 1] for i in range(5))


def build_signatures(omega):
    a = [omega[i] * omega[i] for i in range(3)]
    b = [omega[3 + i] * omega[3 + i] for i in range(3)]

    wall_labels = []
    wall_values = []
    scales = []
    for i in range(3):
        for j in range(3):
            v = a[i] - b[j]
            wall_labels.append(f"wall_diff_a{i+1}_b{j+1}")
            wall_values.append(sign_of(v))
            scales.append(abs(v))

    s_minus = a[0] + a[1] + a[2]
    for i in range(3):
        for j in range(3):
            v = a[i] + b[j] - s_minus
            wall_labels.append(f"wall_sum_a{i+1}_b{j+1}")
            wall_values.append(sign_of(v))
            scales.append(abs(v))

    h_labels = []
    h_signs = []
    for r in (2, 3):
        for comb in combinations(range(6), r):
            wsum = F(0)
            ksum = F(0)
            for i in comb:
                wsum += omega[i]
                ksum += SIG[i] * omega[i] * omega[i]
            h = wsum * wsum - (ksum if ksum >= 0 else -ksum)
            h_signs.append(sign_of(h))
            h_labels.append(f"h_r{r}_{''.join(str(i+1) for i in comb)}")

    scale = sum(w * w for w in omega)
    margin = min(scales) / scale if scale else F(0)
    all_signs = tuple(wall_values) + tuple(h_signs)
    all_labels = tuple(wall_labels) + tuple(h_labels)
    return all_signs, all_labels, wall_values, wall_labels, h_signs, h_labels, margin


def matrix_23_45(omega):
    return [
        [
            sign_of(omega[1] * omega[1] - omega[3] * omega[3]),
            sign_of(omega[1] * omega[1] - omega[4] * omega[4]),
        ],
        [
            sign_of(omega[2] * omega[2] - omega[3] * omega[3]),
            sign_of(omega[2] * omega[2] - omega[4] * omega[4]),
        ],
    ]


def branch_16_record(omega):
    wsum = omega[0] + omega[5]
    k = SIG[0] * omega[0] * omega[0] + SIG[5] * omega[5] * omega[5]
    h = wsum * wsum - (k if k >= 0 else -k)
    return {
        "subset": "{1,6}",
        "h_value": frac_to_str(h),
        "h_sign": sign_of(h),
        "k_sign": 1 if k >= 0 else -1,
    }


def build_binary(force=False):
    if not BG_CPP.exists() or BG_CPP.stat().st_mtime < BG_SRC.stat().st_mtime:
        shutil.copy2(BG_SRC, BG_CPP)
    need = force or not BG_BIN.exists() or BG_BIN.stat().st_mtime < BG_CPP.stat().st_mtime
    if need:
        subprocess.run(["g++", "-O2", "-std=c++17", "-o", str(BG_BIN), str(BG_CPP), "-lgmpxx", "-lgmp"], check=True)


def parse_bg(stdout):
    m1 = re.search(r"A_6 = i \* \(([^)]*)\)", stdout)
    if m1:
        return F(m1.group(1))
    m2 = re.search(r"A_6 = \(([^)]*)\) \+ i \* \(([^)]*)\)", stdout)
    if m2 and F(m2.group(1)) == 0:
        return F(m2.group(2))
    raise ValueError("Unexpected BG output")


def bg_eval(omega, cache):
    key = tuple(str(w) for w in omega)
    if key in cache:
        return cache[key]
    moms = [frac_to_str(SIG[i] * omega[i] * omega[i]) for i in range(6)]
    cmd = [
        str(BG_BIN),
        "--amp",
        "-K",
        ",".join(moms),
        "-W",
        ",".join(frac_to_str(w) for w in omega),
    ]
    p = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    if p.returncode != 0:
        raise RuntimeError(p.stderr)
    a = parse_bg(p.stdout)
    prod = F(1)
    for w in omega:
        prod *= w
    h = a / prod
    h = h / (omega[1] * omega[1])
    cache[key] = h
    return h


def monomials_upto(d):
    return [(a, b, c) for a in range(d + 1) for b in range(d + 1 - a) for c in range(d + 1 - a - b)]


def mod_of(fr, p):
    return (fr.numerator % p) * pow(fr.denominator % p, p - 2, p) % p


def crt_pair(r1, m1, r2, m2):
    inv = pow(m1 % m2, m2 - 2, m2)
    x = (r1 + m1 * ((r2 - r1) * inv % m2)) % (m1 * m2)
    return x, m1 * m2


def rat_recon(u, M):
    bound = int((M // 2) ** 0.5)
    r0, r1 = M, u % M
    s0, s1 = 0, 1
    while r1 > bound:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
    if s1 < 0:
        r1, s1 = -r1, -s1
    if s1 == 0 or abs(r1) > bound or abs(s1) > bound:
        return None
    return F(int(r1), int(s1))


def _build_power_table(x: int, deg: int, p: int):
    out = np.ones(deg + 1, dtype=np.int64)
    for e in range(1, deg + 1):
        out[e] = (out[e - 1] * x) % p
    return out


def build_rows_rhs(pts, mon, p, g_scale_func=None):
    nm = len(mon)
    n = len(pts)
    if n == 0:
        return np.zeros((0, nm), dtype=np.int64), np.zeros((0,), dtype=np.int64)
    maxa = max(m[0] for m in mon)
    maxb = max(m[1] for m in mon)
    maxc = max(m[2] for m in mon)

    mat = np.zeros((n, nm), dtype=np.int64)
    rhs = np.zeros((n,), dtype=np.int64)

    for r, (x, y, z, h) in enumerate(pts):
        xm = mod_of(x, p)
        ym = mod_of(y, p)
        zm = mod_of(z, p)
        hm = mod_of(h, p)
        px = _build_power_table(xm, maxa, p)
        py = _build_power_table(ym, maxb, p)
        pz = _build_power_table(zm, maxc, p)

        row = np.empty(nm, dtype=np.int64)
        for k, (a, b, c) in enumerate(mon):
            row[k] = (px[a] * py[b] % p) * pz[c] % p
        mat[r, :] = row

        gv = h
        if g_scale_func is not None:
            gv = g_scale_func(x, y, z, h)
        rhs[r] = mod_of(gv, p)

    return mat, rhs


def rank_mod(M, p):
    A = np.array(M, dtype=np.int64, copy=True) % p
    m, n = A.shape
    rank = 0
    for col in range(n):
        rows = np.nonzero(A[rank:, col] % p)[0]
        if len(rows) == 0:
            continue
        pr = rank + rows[0]
        if pr != rank:
            A[[rank, pr], :] = A[[pr, rank], :]
        inv = pow(int(A[rank, col]), p - 2, p)
        A[rank, :] = (A[rank, :] * inv) % p
        nz = np.where(A[:, col] != 0)[0]
        nz = nz[nz != rank]
        if len(nz):
            A[nz, :] = (A[nz, :] - (A[nz, col][:, None] * A[rank, :])) % p
        A[rank, :] = A[rank, :]
        rank += 1
        if rank == m:
            break
    return rank


def solve_linear_mod(mat, rhs, p):
    M = np.array(mat, dtype=np.int64, copy=True) % p
    b = np.array(rhs, dtype=np.int64, copy=True) % p
    m, n = M.shape

    A = np.concatenate((M, b.reshape(-1, 1)), axis=1)
    rank = 0
    pivots = []
    for col in range(n):
        rows = np.nonzero(A[rank:, col] % p)[0]
        if len(rows) == 0:
            continue
        pr = rank + rows[0]
        if pr != rank:
            A[[rank, pr], :] = A[[pr, rank], :]
        inv = pow(int(A[rank, col]), p - 2, p)
        A[rank, :] = (A[rank, :] * inv) % p
        nz = np.where(A[:, col] != 0)[0]
        if len(nz):
            keep = nz != rank
            nz = nz[keep]
            if len(nz):
                A[nz, :] = (A[nz, :] - (A[nz, col][:, None] * A[rank, :])) % p
        pivots.append(col)
        rank += 1
        if rank == n:
            break

    if rank < n:
        # underdetermined
        return None, rank

    # inconsistency check
    if rank < m:
        if np.any(A[rank:, -1] % p != 0):
            return None, rank
    return [int(A[i, -1]) % p for i in range(n)], rank


def test_poly_fit(pts, mon, subset_v, holdout, dmax=12):
    U = (X + Y) * (X + Z) * (1 + Y) * (1 + Z) * (X**2 + X * Y + X * Z + X + Y * Z + Y + Z + 1) * (X * Y + X * Z + X + Y**2 + Y * Z + Y + Z**2 + Z)

    def gv_factor(x, y, z, h):
        v = h * U.subs({X: x, Y: y, Z: z})
        for var in subset_v:
            v *= {"x": x, "y": y, "z": z}[var]
        return F(v)

    def eval_poly(c, monoms, x, y, z):
        out = F(0)
        for coeff, (a, b, cexp) in zip(c, monoms):
            if coeff == 0:
                continue
            term = coeff
            if a:
                term *= x ** a
            if b:
                term *= y ** b
            if cexp:
                term *= z ** cexp
            out += term
        return out

    if len(pts) < holdout + 1:
        return None, {
            "status": "insufficient_total",
            "need_total": holdout + 1,
            "got": len(pts),
            "best": None,
            "checks": {},
        }

    hold = min(holdout, max(0, len(pts) // 5))
    fit_pts = pts[: max(0, len(pts) - hold)]
    hold_pts = pts[len(pts) - hold :]

    scan = []
    for d in range(0, dmax + 1):
        mon = monomials_upto(d)
        nm = len(mon)
        fit_n = max(nm + 2, len(pts))
        # require at least nm equations from fit points
        if len(fit_pts) < nm:
            scan.append({"d": d, "nm": nm, "status": "insufficient_fit"})
            continue

        pass_all = True
        for p in RANK_PRIMES:
            M, b = build_rows_rhs(fit_pts, mon, p, g_scale_func=gv_factor)
            rM = rank_mod(M, p)
            M2 = np.concatenate((M, b.reshape(-1, 1)), axis=1)
            rA = rank_mod(M2, p)
            if rM != rA or rM != nm:
                pass_all = False
                break
        scan.append({
            "d": d,
            "nm": nm,
            "npts": len(fit_pts),
            "r31": rank_mod(
                np.array(build_rows_rhs(fit_pts, mon, P31, g_scale_func=gv_factor)[0], dtype=np.int64), P31
            ),
            "r61": rank_mod(
                np.array(build_rows_rhs(fit_pts, mon, P61, g_scale_func=gv_factor)[0], dtype=np.int64), P61
            ),
            "status": "rank_match" if pass_all else "rank_mismatch",
        })
        if not pass_all:
            continue

        # reconstruct coefficients from the five extraction primes (no projective normalization)
        coeffs = {}
        for p in EXTRACT_PRIMES:
            M, b = build_rows_rhs(fit_pts, mon, p, g_scale_func=gv_factor)
            sol, rk = solve_linear_mod(M, b, p)
            if sol is None or rk != nm:
                pass_all = False
                break
            coeffs[p] = sol
        if not pass_all:
            continue

        solved = []
        for k in range(nm):
            r = coeffs[EXTRACT_PRIMES[0]][k] % EXTRACT_PRIMES[0]
            mod = EXTRACT_PRIMES[0]
            for p in EXTRACT_PRIMES[1:]:
                r, mod = crt_pair(r, mod, coeffs[p][k], p)
            fr = rat_recon(r, mod)
            if fr is None:
                pass_all = False
                break
            solved.append(fr)
        if not pass_all:
            continue

        P = sum(coeff * (X ** a * Y ** b * Z ** cexp) for coeff, (a, b, cexp) in zip(solved, mon))
        Q = U * p_prod({"x": X, "y": Y, "z": Z}.get(v, F(1)) for v in subset_v)
        expr = sp.together(P / Q)

        num, den = expr.as_numer_denom()
        num = sp.expand(num)
        den = sp.expand(den)

        # exact full-point checks
        check_total = 0
        check_bad = 0
        hold_total = 0
        hold_bad = 0
        hold_set = set(hold_pts)
        for x, y, z, h in pts:
            numv = eval_poly(solved, mon, x, y, z)
            denv = U.subs({X: x, Y: y, Z: z})
            for var in subset_v:
                denv = denv * {"x": x, "y": y, "z": z}[var]
            gv = to_fraction(h)
            denv = to_fraction(denv)
            if denv == 0:
                continue
            recon = numv / denv
            check_total += 1
            if recon != gv:
                check_bad += 1
            if len(pts) > hold and (x, y, z, h) in hold_set:
                hold_total += 1
                if recon != gv:
                    hold_bad += 1
        if check_bad or hold_bad:
            continue

        gcd_num_den = sp.gcd(num, den)
        num_red = sp.expand(num / gcd_num_den)
        den_red = sp.expand(den / gcd_num_den)
        all_gcd_single = []
        for v in subset_v:
            fs = sp.expand({"x": X, "y": Y, "z": Z}[v])
            all_gcd_single.append({"factor": str(fs), "gcd_with_num": str(sp.gcd(num_red, fs)), "neutral": str(sp.gcd(num_red, fs) == 1)})

        return {
            "status": "reconstructed",
            "method": "fast_fixed_den",
            "scan": scan,
            "degree": d,
            "num": str(num),
            "den": str(den),
            "P": str(sp.expand(P)),
            "Q": str(sp.expand(Q)),
            "factorP": str(sp.factor(num_red)),
            "factorQ": str(sp.factor(den_red)),
            "degP": int(sp.Poly(sp.expand(num), X, Y, Z).total_degree() if num != 0 else 0),
            "degQ": int(sp.Poly(sp.expand(den), X, Y, Z).total_degree() if den != 0 else 0),
            "check_total": check_total,
            "check_bad": check_bad,
            "hold_total": hold_total,
            "hold_bad": hold_bad,
            "check_ok": max(0, check_total - check_bad),
            "hold_ok": max(0, hold_total - hold_bad),
            "gcd_num_den": str(gcd_num_den),
            "gcd_singles": all_gcd_single,
            "selected_V": list(subset_v),
            "U": str(U),
            "V_product": str(p_prod({"x": X, "y": Y, "z": Z}.get(v, F(1)) for v in subset_v)),
            "monomials": nm,
        }, scan

    return None, {"status": "not_found", "scan": scan, "dmax": dmax}


def ordered_subsets():
    vars3 = ["x", "y", "z"]
    out = [tuple()]
    for k in range(1, 4):
        from itertools import combinations
        for comb in combinations(vars3, k):
            out.append(comb)
    return out


def pick_bases(target=3, rng_seed=2026, need=4):
    rng = random.Random(rng_seed)
    candidates = {}
    seen_matrices = set()

    # deterministic seed samples to start away from known A/B signatures
    seed_bases = [
        (F(9), F(8), F(2), F(-5)),
        (F(-4), F(9), F(6), F(-7)),
        (F(7), F(2), F(-3), F(-5)),
        (F(3), F(5), F(7), F(-9)),
    ]

    def push_if_good(free):
        try:
            omega = solve_from_free(free)
        except Exception:
            return
        if not is_generic(omega):
            return
        all_signs = build_signatures(omega)[0]
        if 0 in all_signs or all_signs in KNOWN_AB_SIGNATURES:
            return
        if all_signs in candidates:
            return
        mat = tuple(map(tuple, matrix_23_45(omega)))
        # prioritize interleaved distinct matrices when possible
        if mat in seen_matrices and len(candidates) + 1 < target:
            return
        candidates[all_signs] = {
            "free": free,
            "matrix": mat,
            "omega": tuple(omega),
        }
        seen_matrices.add(mat)

    for free in seed_bases:
        if all(x == 0 for x in free) or sum(free) == 0:
            continue
        push_if_good(free)

    tries = 0
    denoms = [2, 3, 4, 5, 6, 7, 8, 11, 13]
    while len(candidates) < target and tries < 300000:
        tries += 1
        den = rng.choice(denoms)
        free = tuple(F(rng.randint(-13, 13), den) for _ in range(4))
        if any(x == 0 for x in free) or sum(free) == 0:
            continue
        if all(abs(v) <= 1 for v in free):
            continue
        _, _, _, _, _, _, margin = build_signatures(solve_from_free(free)) if is_generic(solve_from_free(free)) else (None, None, None, None, None, None, F(0))
        if margin == 0 or margin < F(1, 20000):
            continue
        push_if_good(free)

    # if we fail on matrix-unique requirement, relax matrix constraint.
    if len(candidates) < target:
        tries = 0
        while len(candidates) < target and tries < 300000:
            tries += 1
            den = rng.choice(denoms)
            free = tuple(F(rng.randint(-17, 17), den) for _ in range(4))
            if any(x == 0 for x in free) or sum(free) == 0:
                continue
            try:
                omega = solve_from_free(free)
            except Exception:
                continue
            if not is_generic(omega):
                continue
            all_signs = build_signatures(omega)[0]
            if 0 in all_signs or all_signs in KNOWN_AB_SIGNATURES or all_signs in candidates:
                continue
            candidates[all_signs] = {
                "free": free,
                "matrix": tuple(map(tuple, matrix_23_45(omega))),
                "omega": tuple(omega),
            }

    return [v["free"] for v in list(candidates.values())[:max(need, target)][:target]]


def persist_points(points_path, base_omega, all_signs, labels, pts, status):
    payload = {
        "base_omega": [frac_to_str(x) for x in base_omega],
        "all_signs": list(all_signs),
        "labels": list(labels),
        "status": status,
        "points": [[frac_to_str(x), frac_to_str(y), frac_to_str(z), frac_to_str(h)] for x, y, z, h in pts],
        "npoints": len(pts),
    }
    with open(points_path, "w") as f:
        json.dump(payload, f, indent=2)


def collect_points(base_free, target_signs, need=570, seed=2026, target_path=None, labels=(), checkpoint_every=50):
    rng = random.Random(seed)
    pts = []
    tries = 0
    cache = {}
    need_total = need
    if checkpoint_every < 1:
        checkpoint_every = 50

    base_omega = solve_from_free(base_free)
    if target_path is not None:
        persist_points(target_path, base_omega, target_signs, labels, pts, "collecting")

    while len(pts) < need_total and tries < 4_000_000:
        tries += 1
        den = rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13])
        ff = tuple(base_free[i] + F(rng.randint(-9, 9), den) for i in range(4))
        if any(x == 0 for x in ff):
            continue
        try:
            omega = solve_from_free(ff)
        except Exception:
            continue
        if not is_generic(omega):
            continue
        if build_signatures(omega)[0] != target_signs:
            continue
        try:
            h = bg_eval(omega, cache)
        except Exception:
            continue
        w2 = omega[1]
        if w2 == 0:
            continue
        x = omega[2] / w2
        y = omega[3] / w2
        z = omega[4] / w2
        if x == 0 or y == 0 or z == 0:
            continue
        pts.append((x, y, z, h))
        if target_path is not None and len(pts) % checkpoint_every == 0:
            persist_points(target_path, base_omega, target_signs, labels, pts, "collecting")

    return pts, tries


def build_piece_points_path(sig_hash):
    return PIECE_DIR / f"piece_{sig_hash}_points.json"


def build_piece_detail_path(sig_hash):
    return PIECE_DIR / f"piece_{sig_hash}_detail.json"


def build_piece_md_path(sig_hash):
    return PIECE_DIR / f"piece_{sig_hash}_detail.md"


def _eval_poly(coeffs, mon, x, y, z):
    xp = {}
    yp = {}
    zp = {}
    for i, j, k in mon:
        if i not in xp:
            xp[i] = x ** i
        if j not in yp:
            yp[j] = y ** j
        if k not in zp:
            zp[k] = z ** k
    out = F(0)
    for c, (i, j, k) in zip(coeffs, mon):
        if c == 0:
            continue
        out += c * xp[i] * yp[j] * zp[k]
    return out


def U_factor(x, y, z):
    return (x + y) * (x + z) * (1 + y) * (1 + z) * (x**2 + x * y + x * z + x + y * z + y + z + 1) * (x * y + x * z + x + y**2 + y * z + y + z**2 + z)


def write_piece_files(sig_hash, base_omega, all_signs, labels, wall_signs, h_signs, matrix, pts, extract, scans):
    points_path = build_piece_points_path(sig_hash)
    persist_points(points_path, base_omega, all_signs, labels, pts, extract.get("status", "partial"))

    detail = {
        "signature_hash": sig_hash,
        "base_omega": [frac_to_str(x) for x in base_omega],
        "signature_labels": list(labels),
        "signature_values": list(all_signs),
        "wall_signs": list(wall_signs),
        "h_signs": h_signs,
        "compare_matrix_23_45": matrix,
        "h16_branch": branch_16_record(base_omega),
        "scan": scans,
        "dmin": extract.get("degree"),
        "selected_V": extract.get("selected_V"),
        "fixed_denominator": {
            "U": extract.get("U", str(0)),
            "V": extract.get("selected_V", []),
            "Q": extract.get("Q", ""),
            "V_product": extract.get("V_product", "1"),
        },
        "P": extract.get("P", ""),
        "Q": extract.get("Q", ""),
        "factorP": extract.get("factorP", ""),
        "factorQ": extract.get("factorQ", ""),
        "degP": extract.get("degP", -1),
        "degQ": extract.get("degQ", -1),
        "gcd_num_den": extract.get("gcd_num_den", "1"),
        "gcd_singles": extract.get("gcd_singles", []),
        "check": {
            "ok": extract.get("check_ok", 0),
            "total": extract.get("check_total", 0),
            "bad": extract.get("check_bad", 0),
            "hold_ok": extract.get("hold_ok", 0),
            "hold_total": extract.get("hold_total", 0),
            "hold_bad": extract.get("hold_bad", 0),
        },
        "status": extract.get("status", "insufficient_points"),
        "point_file": str(points_path),
        "detail_file": str(build_piece_detail_path(sig_hash)),
    }
    detail_path = build_piece_detail_path(sig_hash)
    with open(detail_path, "w") as f:
        json.dump(detail, f, indent=2)

    with open(build_piece_md_path(sig_hash), "w") as f:
        f.write(f"# Piece {sig_hash}\n")
        f.write(f"base omega: {[frac_to_str(x) for x in base_omega]}\n")
        f.write(f"compare matrix: {matrix}\n")
        f.write(f"status: {detail['status']}\n")
        f.write(f"selected V: {detail['selected_V']}\n")
        f.write(f"points: {len(pts)}\n")
        if detail["status"] == "reconstructed":
            f.write(f"d = {extract.get('degree')}\n")
            f.write(f"check ok={extract.get('check_ok', 0)} total={extract.get('check_total', 0)} hold_ok={extract.get('hold_ok', 0)} hold_total={extract.get('hold_total', 0)}\n")
    return str(points_path), str(detail_path)


def run_one(base_free, need_points, holdout, dmax, seed):
    base_omega = solve_from_free(base_free)
    all_signs, all_labels, wall_signs, wall_labels, h_signs, h_labels, _ = build_signatures(base_omega)
    sig_hash = hashlib.sha1("".join(str(v) for v in all_signs).encode()).hexdigest()[:10]

    print(f"piece {sig_hash}: collect target={need_points}")
    points_path = build_piece_points_path(sig_hash)
    pts, tries = collect_points(
        base_free, all_signs, need=need_points, seed=seed, target_path=points_path, labels=all_labels
    )
    print(f"piece {sig_hash}: tries={tries} collected={len(pts)}")

    detail_item = {
        "signature_hash": sig_hash,
        "status": "insufficient_points",
        "collected_points": len(pts),
        "collect_tries": tries,
        "base_omega": [frac_to_str(x) for x in base_omega],
        "matrix": matrix_23_45(base_omega),
        "h16_branch": branch_16_record(base_omega),
        "elapsed_sec": 0,
        "progress": {
            "points": len(pts),
            "target": need_points,
            "holds": holdout,
        },
    }

    extract = {
        "status": "insufficient_points",
    }
    scans = []

    if len(pts) >= max(need_points - 1, 1):
        for subset in ordered_subsets():
            print(f"piece {sig_hash}: test V={subset}")
            extracted, scans_subset = test_poly_fit(pts, None, subset, holdout=holdout, dmax=dmax)
            scans.append({"V": list(subset), "scan": scans_subset, "status": scans_subset.get("status", "") if isinstance(scans_subset, dict) else "ok"})
            if extracted is not None and extracted.get("status") == "reconstructed":
                detail_item["status"] = "reconstructed"
                extract = extracted
                break
        else:
            detail_item["status"] = "no_fixed_den_fit"
            scans = scans or []
    else:
        detail_item["status"] = "insufficient_points"

    write_piece_files(
        sig_hash,
        base_omega,
        all_signs,
        all_labels,
        wall_signs,
        h_signs,
        matrix_23_45(base_omega),
        pts,
        extract,
        scans,
    )

    if extract.get("status") == "reconstructed":
        detail_item.update({
            "degree": {"P": extract.get("degP", -1), "Q": extract.get("degQ", -1)},
            "selected_V": extract.get("selected_V", []),
            "check": {
                "ok": extract.get("check_ok", 0),
                "total": extract.get("check_total", 0),
                "bad": extract.get("check_bad", 0),
                "hold_ok": extract.get("hold_ok", 0),
                "hold_total": extract.get("hold_total", 0),
                "hold_bad": extract.get("hold_bad", 0),
            },
            "factorP": extract.get("factorP", ""),
            "factorQ": extract.get("factorQ", ""),
            "point_file": str(build_piece_points_path(sig_hash)),
            "detail_file": str(build_piece_detail_path(sig_hash)),
            "scan": scans,
            "base_omega": [frac_to_str(x) for x in base_omega],
        })

    return detail_item


def parse_factorP(path):
    if not path.exists():
        return None
    txt = path.read_text()
    m = re.search(r"\n\nfactorP=(.*?)\n\nP=", txt, re.S)
    if not m:
        m = re.search(r"\n\nfactorP=(.*)", txt, re.S)
    if not m:
        return None
    return m.group(1).strip()


def strip_obvious(expr):
    x, y, z = sp.symbols("x y z")
    expr = sp.expand(expr)
    poly = sp.Poly(expr, x, y, z, domain="QQ")
    coeffs = poly.coeffs() if poly is not None else [F(1)]
    if coeffs:
        num_g = 0
        den_lcm = 1
        for c in coeffs:
            rc = sp.Rational(c)
            num_g = rc.p if num_g == 0 else math.gcd(num_g, abs(rc.p))
            den_lcm = int(p_prod([den_lcm, rc.q]) / math.gcd(den_lcm, rc.q))
        if num_g != 0:
            expr = expr / sp.Rational(num_g, den_lcm)
            expr = sp.expand(expr)

    factors = sp.factor_list(expr)[1]
    remain = expr
    singles = []
    for f, e in factors:
        f_exp = sp.expand(f)
        if f_exp in (x, y, z):
            remain = sp.expand(sp.cancel(remain / (f ** e)))
            singles.append(str(f_exp))
            continue
        if f_exp == x + y + z + 1:
            remain = sp.expand(sp.cancel(remain / (f ** e)))
            singles.append("x+y+z+1")
    return remain, singles


def _weighted_monomials(deg, weights=(1, 1, 2, 2)):
    w1, w2, w3, w4 = weights
    out = []
    for a in range(deg + 1):
        for b in range(deg + 1):
            for c in range(deg + 1):
                for d in range(deg + 1):
                    if a * w1 + b * w2 + c * w3 + d * w4 == deg:
                        out.append((a, b, c, d))
    return out


def coeffs_in_basis(expr, basis_gens, vars=(W2, W3, W4, W5), degree=0, weights=(1, 1, 2, 2), generator_names=None):
    expr = sp.expand(expr)
    target_poly = sp.Poly(expr, *vars, domain="QQ")
    mon_dict_target = dict(target_poly.terms())
    nmon = len(mon_dict_target)

    if generator_names is None:
        generator_names = [f"e{i}" for i in range(1, len(basis_gens) + 1)]
    gen_syms = sp.symbols(" ".join(generator_names))
    if len(gen_syms) != len(basis_gens):
        gen_syms = sp.symbols(" ".join(generator_names[: len(basis_gens)]))

    basis_powers = _weighted_monomials(degree, weights)
    basis_terms_w = []
    basis_terms_g = []
    mon_set = set(mon_dict_target.keys())

    for pw in basis_powers:
        term_w = sp.Integer(1)
        term_g = sp.Integer(1)
        for e, gen_expr, gen_sym in zip(pw, basis_gens, gen_syms):
            if e == 0:
                continue
            term_w *= sp.expand(gen_expr ** e)
            term_g *= gen_sym ** e
        basis_terms_w.append(sp.expand(term_w))
        basis_terms_g.append(sp.expand(term_g))

    # if no candidate basis terms, return immediately.
    if not basis_terms_w:
        return {
            "status": "empty_basis",
            "basis_terms": 0,
            "target_terms": nmon,
            "terms": 0,
            "exact": False,
            "expression": "",
            "factor": "",
        }

    for basis_expr in basis_terms_w:
        p = sp.Poly(sp.expand(basis_expr), *vars, domain="QQ")
        mon_set |= set(p.as_dict().keys())

    mon_list = sorted(mon_set)
    idx = {m: i for i, m in enumerate(mon_list)}
    n_basis = len(basis_terms_w)

    rhs = sp.Matrix([F(0) for _ in range(len(mon_list))])
    for m, c in mon_dict_target.items():
        rhs[idx[m], 0] = sp.Rational(c)

    A = sp.zeros(len(mon_set), n_basis)
    for j, basis_expr in enumerate(basis_terms_w):
        p = sp.Poly(sp.expand(basis_expr), *vars, domain="QQ")
        mon_to_c = p.as_dict()
        for m, c in mon_to_c.items():
            A[idx[m], j] = sp.Rational(c)

    A_aug = A.row_join(rhs)

    rank_A = int(A.rank())
    rank_aug = int(A_aug.rank())
    if rank_A != rank_aug:
        return {
            "status": "mismatch",
            "basis_terms": n_basis,
            "target_terms": nmon,
            "rankA": rank_A,
            "rankAug": rank_aug,
            "terms": 0,
            "expression": "",
            "exact": False,
        }

    if rank_A != n_basis:
        # underdetermined in this basis
        # solve least with symbolic params then reject.
        return {
            "status": "rank_deficient",
            "basis_terms": n_basis,
            "target_terms": nmon,
            "rankA": rank_A,
            "rankAug": rank_aug,
            "terms": 0,
            "expression": "",
            "exact": False,
        }

    sol = A.LUsolve(rhs)
    poly_expr_w = sp.Integer(0)
    poly_expr_g = sp.Integer(0)
    for c, base_expr_w, base_expr_g in zip(sol, basis_terms_w, basis_terms_g):
        cc = sp.expand(sp.Rational(c))
        if cc != 0:
            poly_expr_w += cc * sp.expand(base_expr_w)
            poly_expr_g += cc * sp.expand(base_expr_g)
    ok = sp.expand(sp.expand(poly_expr_w - expr)) == 0

    pp = sp.Poly(sp.expand(poly_expr_w), *vars)
    return {
        "status": "ok" if ok else "mismatch",
        "basis_terms": n_basis,
        "target_degree": int(target_poly.total_degree()) if expr != 0 else 0,
        "candidate_terms": len(basis_terms_w),
        "target_terms": nmon,
        "terms": len(pp.terms()) if ok else 0,
        "expression": str(sp.expand(poly_expr_g)) if ok else "",
        "expression_expanded": str(sp.expand(poly_expr_w)) if ok else "",
        "exact": bool(ok),
        "factor": str(sp.factor(sp.expand(poly_expr_g))) if ok else "",
    }


def compute_numerator_invariants():
    x, y, z = sp.symbols("x y z")
    w2, w3, w4, w5 = sp.symbols("w2 w3 w4 w5")

    m1 = w2 + w3
    m2 = w2 * w3
    p1 = w4 + w5
    p2 = w4 * w5
    basis_alpha = (m1, p1, m2, p2)
    basis_beta = (m1 + p1, m1 - p1, m2, p2)
    basis_gamma = (m1 + p1, m2 + p2, m1 * p1, m2 * p2)
    basis_delta = (m1 - p1, m2 - p2, m1 * p1, m2 * p2)

    def compare_sym(expr, transformed):
        d0 = sp.expand(expr - transformed)
        d1 = sp.expand(expr + transformed)
        if d0 == 0:
            return {"relation": "equal", "difference": "0"}
        if d1 == 0:
            return {"relation": "negative", "difference": "0"}
        return {
            "relation": "different",
            "difference": str(sp.expand(d0)),
        }

    entries = []
    for src, qpath in [("piece_A", QP_A), ("piece_B", QP_B)]:
        f = parse_factorP(qpath)
        if f is None:
            continue
        P = sp.sympify(f)
        core, singles = strip_obvious(P)
        deg = int(sp.Poly(core, x, y, z).total_degree()) if core != 0 else 0
        C = sp.expand(core.subs({x: w3 / w2, y: w4 / w2, z: w5 / w2}) * (w2 ** deg))

        # weighted exact basis fits
        basis_defs = {
            "m1_p1_m2_p2": (basis_alpha, (1, 1, 2, 2)),
            "Omega_d_m2_p2": (basis_beta, (1, 1, 2, 2)),
            "e1_e2_e2cross_e4": (basis_gamma, (1, 2, 2, 4)),
            "swap_sym_e1_e2_ecross_e4": (basis_delta, (1, 2, 2, 4)),
        }
        basis_rows = {}
        for name, (bvec, weights) in basis_defs.items():
            basis_rows[name] = coeffs_in_basis(
                C,
                bvec,
                vars=(w2, w3, w4, w5),
                degree=deg,
                weights=weights,
                generator_names=["e1", "e2", "e3", "e4"],
            )

        entry = {
            "source": src,
            "stripped_singles": singles,
            "C_homogeneous": str(sp.expand(C)),
            "degree": deg,
            "bases": basis_rows,
            "symmetry": {
                "swap_23": compare_sym(C, C.subs({w2: w3, w3: w2})),
                "swap_45": compare_sym(C, C.subs({w4: w5, w5: w4})),
                "swap_sides": compare_sym(C, C.subs({w2: w4, w3: w5, w4: w2, w5: w3})),
            },
            "raw_factorP": str(P),
        }
        entries.append(entry)
        with open(PIECE_DIR / f"invariants_{src}.json", "w") as jf:
            json.dump(entry, jf, indent=2)

    return entries


def _job_id():
    return strftime("r6_piece_%Y%m%dT%H%M%SZ", gmtime())


def launch_detached_job(cmd, result_path, note, blocking=False):
    jid = _job_id()
    JOBS = ROOT / "jobs"
    JOBS.mkdir(exist_ok=True)
    done = JOBS / f"{jid}.done"
    fail = JOBS / f"{jid}.fail"
    logp = JOBS / f"{jid}.log"

    job = {
        "id": jid,
        "launched_by": "student-1",
        "cmd": cmd,
        "run_ref": str(os.getpid()),
        "result_path": str(result_path),
        "blocking": bool(blocking),
        "note": note,
    }
    with open(JOBS / f"{jid}.json", "w") as f:
        json.dump(job, f, indent=2)

    # detach without polling. touch completion marker deterministically.
    shell_cmd = f"cd {ROOT} && {cmd} > {logp} 2>&1; rc=$?; if [ $rc -eq 0 ]; then touch {done}; else touch {fail}; fi"
    subprocess.Popen(["bash", "-lc", shell_cmd], preexec_fn=os.setsid)
    return jid, str(logp), str(done), str(fail), str(JOBS / f"{jid}.json")


def estimate_runtime_seconds(bases, need_points, dmax):
    # conservative cost model for modular elimination and reconstruction.
    # this is intentionally over-estimate-first.
    import math as _m

    est_per_piece = 0.0
    for d in range(0, min(dmax, 12) + 1):
        nm = (d + 1) * (d + 2) * (d + 3) // 6
        # rank checks for two test primes, 8 subsets, sparse overhead
        est_per_piece += 0.12 * 2 * min(need_points, 600) * nm * 0.003
    # point collection dominates quickly.
    est_per_piece += need_points * 0.015
    # 4 V-subset scans with rebuild overhead
    est_per_piece *= 2.0
    est_total = max(1.0, bases) * est_per_piece
    # clamp floor/ceil to keep behavior deterministic
    return int(_m.ceil(est_total))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bases", type=int, default=3)
    p.add_argument("--points", type=int, default=520)
    p.add_argument("--dmax", type=int, default=12)
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--holdout", type=int, default=50)
    p.add_argument("--fast-fixed-den", action="store_true", default=True)
    p.add_argument("--run-mode", choices=["block", "auto_detach", "force_detach"], default="auto_detach")
    p.add_argument("--detach-threshold", type=float, default=600.0)
    args = p.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    start = time()

    # 1) numerator invariants first (BG-agnostic)
    invs = compute_numerator_invariants()
    with open(DATA_DIR / "round6_numerator_invariants.json", "w") as f:
        json.dump({"entries": invs}, f, indent=2)

    with open(DATA_DIR / "round6_numerator_invariants.md", "w") as f:
        f.write("# Round-6 numerator invariant rewriting\n")
        for ent in invs:
            f.write(f"\n## {ent['source']}\n")
            f.write(f"- stripped singles: {ent['stripped_singles']}\n")
            f.write(f"- degree: {ent['degree']}\n")
            for k, v in ent["bases"].items():
                f.write(f"- {k}: status={v['status']} terms={v['terms']} exact={v['exact']}\n")

    # 2) fresh BG build smoke
    build_binary(force=True)

    run_ref_cmd = "python3 bots/student-1/code/round6_piece_pipeline.py --fast-fixed-den --bases {} --points {} --dmax {} --seed {} --holdout {} --run-mode block".format(
        args.bases, args.points, args.dmax, args.seed + 997, args.holdout
    )
    # smoke run with a tiny local point can optionally be added by human if needed.

    # 3) base selection and run
    total_needed = args.points + args.holdout
    bases = pick_bases(args.bases, args.seed, need=args.bases)
    if len(bases) < max(1, args.bases):
        raise RuntimeError(f"only found {len(bases)} distinct sign bases")

    detail_mode = args.run_mode
    est = estimate_runtime_seconds(len(bases), total_needed, args.dmax)
    piece_reports = []

    if detail_mode == "force_detach" or (detail_mode == "auto_detach" and est > args.detach_threshold):
        cmd = "python3 bots/student-1/code/round6_piece_pipeline.py --fast-fixed-den --bases {} --points {} --dmax {} --seed {} --holdout {} --run-mode block".format(
            args.bases, args.points, args.dmax, args.seed, args.holdout
        )
        jid, logp, donep, failp, _ = launch_detached_job(
            cmd,
            DATA_DIR / "round6_piece_report.json",
            f"detached fast-fixed-den piece run ({args.bases} bases, points={args.points})",
            blocking=False,
        )
        elapsed = time() - start
        out = {
            "utc": strftime("%Y-%m-%dT%H:%M:%SZ", gmtime()),
            "elapsed_sec": elapsed,
            "targets": args.__dict__,
            "mode": "detached",
            "detached_job": {
                "id": jid,
                "log": logp,
                "done": donep,
                "fail": failp,
                "result_path": str(DATA_DIR / "round6_piece_report.json"),
            },
            "piece_reports": [],
            "invariant_sources": [x["source"] for x in invs],
            "estimate_sec": est,
        }
        with open(DATA_DIR / "round6_piece_report.json", "w") as f:
            json.dump(out, f, indent=2)
        with open(DATA_DIR / "round6_piece_report.md", "w") as f:
            f.write("# Round-6 Piece Report\n")
            f.write(f"- elapsed: {elapsed:.3f} sec\n")
            f.write(f"- utc: {out['utc']}\n")
            f.write(f"- status: detached\n")
            f.write(f"- job_id: {jid}\n")
            f.write(f"- log: {logp}\n")
            f.write(f"- estimate_sec: {est}\n")
        return

    for i, free in enumerate(bases):
        report = run_one(free, total_needed, args.holdout, args.dmax, args.seed + 31 * (i + 1))
        piece_reports.append(report)

    elapsed = time() - start
    out = {
        "utc": strftime("%Y-%m-%dT%H:%M:%SZ", gmtime()),
        "elapsed_sec": elapsed,
        "targets": args.__dict__,
        "mode": "block",
        "piece_reports": piece_reports,
        "invariant_sources": [x["source"] for x in invs],
        "estimate_sec": est,
    }
    with open(DATA_DIR / "round6_piece_report.json", "w") as f:
        json.dump(out, f, indent=2)

    with open(DATA_DIR / "round6_piece_report.md", "w") as f:
        f.write("# Round-6 Piece Report\n")
        f.write(f"- elapsed: {elapsed:.3f} sec\n")
        f.write(f"- utc: {out['utc']}\n")
        f.write(f"- estimated_sec: {est}\n")
        for it in piece_reports:
            f.write(f"\n- {it['signature_hash']} : {it['status']} points={it.get('collected_points', 0)} matrix={it.get('matrix', '')}\n")


if __name__ == "__main__":
    main()
