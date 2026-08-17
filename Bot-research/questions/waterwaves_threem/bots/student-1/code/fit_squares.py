#!/usr/bin/env python3
"""Test whether A_6/i is, per chamber, a polynomial in the SIX squares
(a1,a2,a3,b4,b5,b6) of homogeneous degree 4 (=deg 8 in omega).
A degree-4 poly in the squares is uniquely determined on the 4-dim manifold
(the minimal square-relation, the sign resultant, has degree 16 >> 4), so the
fit is well-posed.  Float least squares first."""
import itertools, random
import numpy as np
from fractions import Fraction as F
import harness as h
import chambers_n6 as cn

SIG = [-1, -1, -1, 1, 1, 1]


def sample_in_chamber(target_sig, npts, seed):
    rnd = random.Random(seed)
    pts = []
    while len(pts) < npts:
        free = tuple(F(rnd.randint(-400, 400), 100) for _ in range(4))
        if any(x == 0 for x in free):
            continue
        oms = cn.solve_squares(free)
        if oms is None or any(w == 0 for w in oms):
            continue
        sq = [w * w for w in oms]
        ws = cn.wall_signs(sq)
        if ws is None or cn.canonical(sq) != target_sig:
            continue
        pts.append(free)
    return pts


def monos(deg, nv=6):
    return [e for e in itertools.product(range(deg + 1), repeat=nv) if sum(e) == deg]


def fit(target_sig, label, deg=4):
    pts = sample_in_chamber(target_sig, 200, seed=3)
    M = monos(deg)
    A = []; y = []
    rows_sq = []
    for free in pts:
        im, oms, _ = h.on_shell(list(free), SIG)
        sq = [float(o*o) for o in oms]
        row = [np.prod([sq[v]**e[v] for v in range(6)]) for e in M]
        A.append(row); y.append(float(im)); rows_sq.append(sq)
    A = np.array(A); y = np.array(y)
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    relerr = np.max(np.abs(pred - y) / (np.abs(y) + 1e-9))
    print(f"[{label}] A6/i as deg-{deg} poly in 6 squares: #monos={len(M)}, "
          f"max rel resid={relerr:.3e}")
    scale = np.max(np.abs(coef))
    terms = [(M[i], coef[i]) for i in range(len(M)) if abs(coef[i]) > 1e-5*scale]
    print(f"  significant monomials: {len(terms)}")
    return relerr, coef, M


if __name__ == "__main__":
    T0free = (F(11, 12), F(11, 4), F(4, 3), F(5, 12))
    sig = cn.canonical([w*w for w in cn.solve_squares(T0free)])
    fit(sig, "T0", deg=4)
