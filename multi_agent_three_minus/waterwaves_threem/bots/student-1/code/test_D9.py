#!/usr/bin/env python3
"""Test: is the denominator of A_6 exactly the product of the 9 mixed-pair linear
forms (w_i + w_j), i in minus {1,2,3}, j in plus {4,5,6}?

D9(w) = prod_{i in {1,2,3}, j in {4,5,6}} (w_i + w_j)  (degree 9).
Note (w_1+w_6) etc. include the solved legs.  On a w4-slice, (w_1+w_6)=-sumFree
and several factors involve the solved legs 1,6 (rational in t).  We compute
A_6(t)*D9(t) on a chamber slice and reconstruct it as a rational function.

If the 9 mixed-pair linear forms are the COMPLETE denominator (up to the leg-1,6
solve artifact, a pure power of sumFree), then A_6*D9 reconstructs to
N(t)/sumFree(t)^m  -- denominator a pure power of (t - t_sumFree).  Any OTHER
denominator factor would signal a missing/extra piece.
"""
from fractions import Fraction as F
import sympy as sp
import harness as h
import chambers_n6 as cn
from rat_denom import reconstruct

SIG = [-1, -1, -1, 1, 1, 1]
MINUS = [1, 2, 3]
PLUS = [4, 5, 6]


def full_sig(oms):
    sq = [w * w for w in oms]
    ws = cn.wall_signs(sq)
    if ws is None:
        return None
    a, b = sq[0:3], sq[3:6]
    if 0 in [a[0]-a[1], a[0]-a[2], a[1]-a[2], b[0]-b[1], b[0]-b[2], b[1]-b[2]]:
        return None
    sa = tuple(1 if a[i] > a[j] else -1 for i, j in [(0,1),(0,2),(1,2)])
    sb = tuple(1 if b[i] > b[j] else -1 for i, j in [(0,1),(0,2),(1,2)])
    return ws + (sa, sb)


def D9(oms):
    w = {i + 1: oms[i] for i in range(6)}
    p = F(1)
    for i in MINUS:
        for j in PLUS:
            p *= (w[i] + w[j])
    return p


def run(vary, base, half=90):
    pts = []
    s0 = full_sig(cn.solve_squares([base[2], base[3], base[4], base[5]]))
    for k in range(-half, half + 1):
        t = F(k, 120)
        free = [base[2], base[3], base[4], base[5]]
        free[vary - 2] = base[vary] + t
        oms = cn.solve_squares(free)
        if oms is None or any(w == 0 for w in oms):
            continue
        if full_sig(oms) != s0:
            continue
        try:
            im, _, _ = h.on_shell(free, SIG)
        except Exception:
            continue
        pts.append((t, im * D9(oms)))
    res = reconstruct(pts)
    return res, len(pts)


if __name__ == "__main__":
    base = {2: F(1), 3: F(-27, 10), 4: F(43, 10), 5: F(12, 5)}
    t = sp.Symbol('t')
    for vary in (2, 3, 4, 5):
        res, npts = run(vary, base)
        if res is None:
            print(f"vary w{vary}: reconstruction failed (raise cap)"); continue
        dN, dD, Nc, Dc = res
        Dpoly = sum(sp.Rational(c.numerator, c.denominator) * t ** k for k, c in enumerate(Dc))
        print(f"vary w{vary} ({npts} pts): A_6*D9 has degN={dN} degD={dD}")
        print(f"   residual denom D(t) = {sp.factor(Dpoly)}")
        # sumFree(t) for this slice
        b = dict(base)
        sumF0 = sum(base.values())   # at t=0
        print(f"   (sumFree at t=0 = {sumF0}; pure-power-of-sumFree denom => 9 mixed pairs are complete)")
