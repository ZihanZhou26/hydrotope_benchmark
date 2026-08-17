#!/usr/bin/env python3
"""Discover the per-chamber polynomial of A_6/i by fitting.
We fit A_6/i (exact via oracle, then float) as a homogeneous degree-8 polynomial
in the four free frequencies (w2,w3,w4,w5).  Float least-squares reveals which
monomials are present; we then re-express / verify exactly elsewhere.
"""
import itertools, sys, random
import numpy as np
from fractions import Fraction as F
import harness as h
import chambers_n6 as cn

SIG = [-1, -1, -1, 1, 1, 1]


def chamber_sig_of(free):
    oms = cn.solve_squares(free)
    sq = [w * w for w in oms]
    return cn.canonical(sq)


def sample_in_chamber(target_sig, npts, seed, lo=-3.0, hi=3.0):
    rnd = random.Random(seed)
    pts = []
    while len(pts) < npts:
        free = tuple(F(rnd.randint(-300, 300), 100) for _ in range(4))
        if any(x == 0 for x in free):
            continue
        oms = cn.solve_squares(free)
        if oms is None or any(w == 0 for w in oms):
            continue
        sq = [w * w for w in oms]
        ws = cn.wall_signs(sq)
        if ws is None:
            continue
        if cn.canonical(sq) != target_sig:
            continue
        pts.append(free)
    return pts


def monos(deg=8, nv=4):
    out = []
    for e in itertools.product(range(deg + 1), repeat=nv):
        if sum(e) == deg:
            out.append(e)
    return out


def fit_float(target_sig, label):
    pts = sample_in_chamber(target_sig, 260, seed=11)
    M = monos()
    A = []; y = []
    for free in pts:
        im, oms, _ = h.on_shell(list(free), SIG)
        x = [float(free[0]), float(free[1]), float(free[2]), float(free[3])]
        row = [x[0]**e[0]*x[1]**e[1]*x[2]**e[2]*x[3]**e[3] for e in M]
        A.append(row); y.append(float(im))
    A = np.array(A); y = np.array(y)
    coef, res, rank, sv = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    relerr = np.max(np.abs(pred - y) / (np.abs(y) + 1e-9))
    print(f"[{label}] fit deg-8 in free vars: rank={rank}/{len(M)}  max rel resid={relerr:.2e}")
    # show significant monomials
    scale = np.max(np.abs(coef))
    terms = [(M[i], coef[i]) for i in range(len(M)) if abs(coef[i]) > 1e-6*scale]
    print(f"  #significant monomials: {len(terms)} (of {len(M)})")
    for e, c in sorted(terms, key=lambda t: -abs(t[1]))[:40]:
        print(f"    w2^{e[0]} w3^{e[1]} w4^{e[2]} w5^{e[3]} : {c:.4f}")
    return relerr


if __name__ == "__main__":
    T0free = (F(11, 12), F(11, 4), F(4, 3), F(5, 12))
    sig = chamber_sig_of(T0free)
    fit_float(sig, "T0")
