#!/usr/bin/env python3
"""Minimal denominator of A_7 (all-n: currently OPEN for n!=6).
Reconstruct A_7/i(t) rationally on an F-const single-chamber slice; report deg(den).
Compare to D_12 = prod_{i in M, j in P}(w_i+w_j) (degree 12) and Res(p_-,Q_7).
Also test: is A_7 * (candidate) polynomial on the slice?
"""
from fractions import Fraction as F
import sympy as sp
from residue_fact import reconstruct
import harness as h

SIG7 = [-1, -1, -1, 1, 1, 1, 1]
MINUS = (1, 2, 3); PLUS = (4, 5, 6, 7)
t = sp.Symbol('t')


def sig(oms):
    w = {i + 1: oms[i] for i in range(7)}
    tg = []
    for i in MINUS:
        for j in PLUS:
            tg.append(1 if w[j] ** 2 - w[i] ** 2 > 0 else -1)
    return tuple(tg)


def collect(w2, w3, w4, a, b, step=F(1, 30), maxk=60, double=False):
    """F-const slice: free legs 2,3,4 (w2,w3 minus; w4 plus), w5=a+t, w6=b-t (plus),
    leg 7 free? No: free legs are 2..6 (5 of them); legs 1,7 solved. So vary w5,w6."""
    pts, s0 = [], None
    for direction in (1, -1):
        for k in range(0 if direction == 1 else 1, maxk):
            tv = direction * step * k
            free = [F(w2), F(w3), F(w4), F(a) + tv, F(b) - tv]
            if sum(free) == 0:
                continue
            try:
                im, oms, re_p = h.on_shell(free, SIG7, double=double)
            except Exception:
                break
            if re_p != 0 and not double:
                continue
            oms = [F(o) if not double else o for o in oms]
            s = sig(oms)
            if s0 is None:
                s0 = s
            if s != s0:
                break
            pts.append((F(tv), F(im)))
    return pts


if __name__ == "__main__":
    print("Reconstructing A_7/i on an F-const slice ...")
    pts = collect(2, 3, 5, 7, 11)
    print(f"  collected {len(pts)} contiguous in-chamber exact points")
    rec = reconstruct(pts, cap=30)
    if rec is None:
        print("  reconstruct failed (need more pts / higher cap)")
    else:
        dN, dD, Nc, Dc = rec
        Den = sum(sp.Rational(c.numerator, c.denominator) * t ** k for k, c in enumerate(Dc))
        print(f"  A_7/i = Num/Den : deg(Num)={dN}, deg(Den)={dD}")
        print(f"  reduced Den(t) factored: {sp.factor(Den)}")
        print(f"  (compare: D_12 has 12 mixed pairs; on an F-const slice with 2 free-free")
        print(f"   plus legs, the slice-visible matching factors number 2*3=6 linear in t.)")
