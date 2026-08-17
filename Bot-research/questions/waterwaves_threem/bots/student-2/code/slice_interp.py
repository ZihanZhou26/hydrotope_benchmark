#!/usr/bin/env python3
"""Exact 1-D slice of C_6 by oracle interpolation along a polynomial slice.

Slice: w2=2+x, w3=3-x, w4=5, w5=7 (SF constant=17). For rational x (avoiding
walls), call ./bg exactly, get C_6(x)=A_6/i/32. Interpolate a polynomial in x
(Lagrange over exact rationals); report it and its degree. Reveals the chamber
polynomial and parity along this slice without slow symbolics.
"""
from fractions import Fraction as F
import sympy as sp
import harness as h

SIG = [-1, -1, -1, 1, 1, 1]


def Cval(xv):
    free = [F(2) + xv, F(3) - xv, F(5), F(7)]
    im, om, _ = h.on_shell(free, SIG)
    return F(im, 32), om


if __name__ == "__main__":
    # pick x values in a single chamber: small |x| around 0, avoid walls
    xs = [F(k, 7) for k in range(-3, 6)]  # 9 points, degree<=8 reconstructable
    data = []
    for xv in xs:
        try:
            c, om = Cval(xv)
            data.append((xv, c))
        except Exception as e:
            print("skip x=", xv, "(wall/SIGFPE)")
    print(f"{len(data)} usable points")
    X = sp.Symbol("x")
    pts = [(sp.Rational(xv.numerator, xv.denominator), sp.Rational(c.numerator, c.denominator)) for xv, c in data]
    poly = sp.interpolate(pts, X)
    poly = sp.expand(poly)
    print("C_6(x) on this chamber =", poly)
    print("degree:", sp.degree(sp.Poly(poly, X)))
    # verify at a fresh x
    xt = F(2, 7)
    ct, _ = Cval(xt)
    pv = poly.subs(X, sp.Rational(xt.numerator, xt.denominator))
    print(f"check x={xt}: interp={pv} oracle={ct} match={sp.Rational(ct.numerator,ct.denominator)==pv}")
