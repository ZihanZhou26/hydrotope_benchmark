#!/usr/bin/env python3
"""PI round-6 phase 2 (fast): extract & FACTOR in-piece Q via multi-prime numpy
null space + CRT + rational reconstruction, then EXACT holdout validation.

h = H/omega2^2 = P(x,y,z)/Q(x,y,z), deg P=12, deg Q=10 (from the rank scan).
Usage: round6_extract_np.py <d> [rows]
"""
import json, sys
from fractions import Fraction as F
import numpy as np
import sympy as sp

PRIMES = [2147483647, 2147483629, 2147483587, 2147483563, 2147483399]


def monos_upto(d):
    out = []
    for a in range(d + 1):
        for b in range(d + 1 - a):
            for c in range(d + 1 - a - b):
                out.append((a, b, c))
    return out


def to_mod(fr, p):
    return (fr.numerator % p) * pow(fr.denominator % p, p - 2, p) % p


def build_X(fit_pts, mon, p):
    nm = len(mon)
    X = np.zeros((len(fit_pts), 2 * nm), dtype=np.int64)
    amax = max(m[0] for m in mon); bmax = max(m[1] for m in mon); cmax = max(m[2] for m in mon)
    for r, (x, y, z, h) in enumerate(fit_pts):
        xm, ym, zm, hm = to_mod(x, p), to_mod(y, p), to_mod(z, p), to_mod(h, p)
        xp = [1] * (amax + 1); yp = [1] * (bmax + 1); zp = [1] * (cmax + 1)
        for e in range(1, amax + 1): xp[e] = xp[e - 1] * xm % p
        for e in range(1, bmax + 1): yp[e] = yp[e - 1] * ym % p
        for e in range(1, cmax + 1): zp[e] = zp[e - 1] * zm % p
        mv = np.array([xp[a] * yp[b] % p * zp[c] % p for (a, b, c) in mon], dtype=np.int64)
        X[r, :nm] = mv
        X[r, nm:] = (p - hm) * mv % p
    return X


def rref_np(X, p):
    A = (X % p).astype(np.int64)
    m, ncol = A.shape
    pivots = []
    rank = 0
    for col in range(ncol):
        nz = np.nonzero(A[rank:, col] % p)[0]
        if len(nz) == 0:
            continue
        pr = rank + int(nz[0])
        A[[rank, pr]] = A[[pr, rank]]
        inv = pow(int(A[rank, col]), p - 2, p)
        A[rank] = A[rank] * inv % p
        cv = A[:, col].copy()
        for r in range(m):
            if r != rank and cv[r] % p:
                A[r] = (A[r] - cv[r] * A[rank]) % p
        pivots.append(col); rank += 1
        if rank == m: break
    return A, pivots, rank


def nullvec(X, p):
    A, pivots, rank = rref_np(X, p)
    ncol = X.shape[1]
    free = [c for c in range(ncol) if c not in set(pivots)]
    if len(free) != 1:
        return None, len(free)
    fc = free[0]
    v = np.zeros(ncol, dtype=np.int64)
    v[fc] = 1
    for i, col in enumerate(pivots):
        v[col] = (p - int(A[i, fc])) % p
    return v, 1


def crt_pair(r1, m1, r2, m2):
    from math import gcd
    g = gcd(m1, m2)
    assert g == 1
    inv = pow(m1 % m2, -1, m2)
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
    if s1 == 0 or abs(r1) > bound or s1 > bound:
        return None
    return F(int(r1), int(s1))


def main():
    d = int(sys.argv[1])
    extra = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    ptsfile = sys.argv[3] if len(sys.argv) > 3 else "round6_points.json"
    outfile = sys.argv[4] if len(sys.argv) > 4 else "round6_QP.txt"
    data = json.load(open(ptsfile))
    pts = [tuple(F(a) for a in row) for row in data["pts"]]
    mon = monos_upto(d); nm = len(mon); ncol = 2 * nm
    nfit = min(len(pts), ncol + extra)
    fit_pts, hold_pts = pts[:nfit], pts[nfit:]
    print(f"d={d} |mon|={nm} ncol={ncol} fit={nfit} hold={len(hold_pts)}")

    # normalization index: fix a coordinate that is nonzero across all primes.
    # We normalize the null vector so coordinate j0 == 1; choose j0 from prime0's
    # free column, verify nonzero elsewhere.
    vecs = {}
    j0 = None
    for p in PRIMES:
        X = build_X(fit_pts, mon, p)
        v, nfree = nullvec(X, p)
        if v is None:
            print(f"p={p}: nulldim={nfree} (expected 1) -> abort"); return
        vecs[p] = v
    # choose j0 = a coordinate nonzero in all vecs
    for cand in range(ncol):
        if all(vecs[p][cand] % p != 0 for p in PRIMES):
            j0 = cand; break
    # normalize each vec so vec[j0]=1
    norm = {}
    for p in PRIMES:
        inv = pow(int(vecs[p][j0]), p - 2, p)
        norm[p] = [int(vecs[p][k]) * inv % p for k in range(ncol)]

    # CRT + rational reconstruction coordinate-wise
    coeffs = []
    ok = True
    for k in range(ncol):
        r, M = norm[PRIMES[0]][k], PRIMES[0]
        for p in PRIMES[1:]:
            r, M = crt_pair(r, M, norm[p][k], p)
        fr = rat_recon(r, M)
        if fr is None:
            ok = False; coeffs.append(None)
        else:
            coeffs.append(fr)
    if not ok:
        print("rational reconstruction failed on some coords; add primes."); return

    pc = coeffs[:nm]; qc = coeffs[nm:]

    # EXACT validation over ALL points via direct Fraction polynomial evaluation
    def peval(cs, x, y, z):
        acc = F(0)
        # precompute powers
        amax = max(m[0] for m in mon); bmax = max(m[1] for m in mon); cmax = max(m[2] for m in mon)
        xp = [F(1)] * (amax + 1); yp = [F(1)] * (bmax + 1); zp = [F(1)] * (cmax + 1)
        for e in range(1, amax + 1): xp[e] = xp[e - 1] * x
        for e in range(1, bmax + 1): yp[e] = yp[e - 1] * y
        for e in range(1, cmax + 1): zp[e] = zp[e - 1] * z
        for cf, (a, b, c) in zip(cs, mon):
            if cf != 0:
                acc += cf * xp[a] * yp[b] * zp[c]
        return acc
    bad = checked = 0; first_ratio = None
    for (xx, yy, zz, hh) in pts:                      # all 1000 points
        qv = peval(qc, xx, yy, zz); pv = peval(pc, xx, yy, zz)
        if qv == 0:
            continue
        checked += 1
        if pv / qv != hh:
            bad += 1
            if first_ratio is None and hh != 0:
                first_ratio = (pv / qv) / hh
    print(f"EXACT validation over all points: {checked-bad}/{checked} pass, bad={bad}")
    if first_ratio is not None:
        print("first-mismatch (P/Q)/h ratio =", first_ratio)

    x, y, z = sp.symbols('x y z')
    def build(cs):
        e = sp.Integer(0)
        for cf, (a, b, c) in zip(cs, mon):
            if cf != 0:
                e += sp.Rational(cf.numerator, cf.denominator) * x**a * y**b * z**c
        return sp.expand(e)
    Ppoly, Qpoly = build(pc), build(qc)

    print("degQ =", sp.total_degree(Qpoly), " degP =", sp.total_degree(Ppoly))
    fQ = sp.factor(Qpoly); fP = sp.factor(Ppoly)
    print("\nfactor(Q) =", fQ)
    print("\nfactor(P) =", fP)
    with open(outfile, "w") as fh:
        fh.write("Q=" + str(Qpoly) + "\n\nfactorQ=" + str(fQ) +
                 "\n\nP=" + str(Ppoly) + "\n\nfactorP=" + str(fP) + "\n")
    print("\nwrote", outfile)


if __name__ == "__main__":
    main()
