#!/usr/bin/env python3
"""Candidate lead (deliverable 4): the n=5 prefactor is omega_4 omega_5 = e_2(plus).
Test whether the swap-symmetric e_2 (= e_2(plus) = e_2(minus) on-shell) divides the
per-chamber numerator N_6 = A_6*D_9, i.e. whether A_6 = i 2^5 g^-3 e_2 * (rational with
denominator D_9). Done on F-const slices (exact polynomial division in t).
"""
import sympy as sp
from fractions import Fraction as F
import harness as h, r4lib

t = sp.Symbol('t')
SIG = [-1, -1, -1, 1, 1, 1]


def slice_polys(w2, w3, a, b, npts=40, step=F(1, 60)):
    ts, Nv, e2v = [], [], []
    for k in range(1, npts + 1):
        tv = step * k
        free = [F(w2), F(w3), F(a) + tv, F(b) - tv]
        try:
            im, oms, _ = h.on_shell(free, SIG)
        except Exception:
            continue
        o = [F(x) for x in oms]
        e2p = o[3] * o[4] + o[3] * o[5] + o[4] * o[5]    # e_2(plus): legs 4,5,6
        ts.append(tv); Nv.append(F(im) * r4lib.Dn(oms)); e2v.append(e2p)
    def ip(vals):
        return sp.expand(sp.interpolate(
            [(sp.Rational(x.numerator, x.denominator), sp.Rational(v.numerator, v.denominator))
             for x, v in zip(ts, vals)], t))
    return ip(Nv), ip(e2v)


def test(w2, w3, a, b, label):
    N, e2 = slice_polys(w2, w3, a, b)
    q, r = sp.div(N, e2, t)
    print(f"{label}: deg N={sp.degree(N,t)}, deg e2={sp.degree(e2,t)}; "
          f"e2 | N ? {sp.expand(r)==0}")
    if sp.expand(r) != 0:
        # how far off: gcd degree
        g = sp.gcd(N, e2)
        print(f"    gcd(N,e2) deg = {sp.degree(g,t) if g!=0 else 'NA'} (e2 deg {sp.degree(e2,t)})")


if __name__ == "__main__":
    test(2, 3, 5, 7, "chamber-1")
    test(2, 3, 4, 9, "chamber-2")
    test(1, 4, 6, 8, "chamber-3")
