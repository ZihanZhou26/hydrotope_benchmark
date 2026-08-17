#!/usr/bin/env python3
"""Reconstruct N_6(t) = A_6(t)*D_9(t) on an F-constant slice (omega_4=a+t,
omega_5=b-t; omega_2,omega_3 fixed; legs 1,6 solved -> polynomial in t since
S_F constant). N_6 is an exact polynomial in t per chamber; interpolate & FACTOR
to read its structure. Also print the per-chamber A_6 = N_6/D_9 and factor both.
"""
import sympy as sp
from fractions import Fraction as F
import harness as h, r4lib

SIG = [-1, -1, -1, 1, 1, 1]
t = sp.Symbol('t')


def slice_points(w2, w3, a, b, ts):
    """For each t: free=(w2,w3,a+t,b-t), solve legs 1,6, return (omegas, A6/i)."""
    out = []
    for tv in ts:
        free = [F(w2), F(w3), F(a) + tv, F(b) - tv]
        try:
            im, oms, _ = h.on_shell(free, SIG)
            out.append((tv, [F(o) for o in oms], F(im)))
        except Exception:
            pass
    return out


def interp_poly(ts, vs):
    pts = [(sp.Rational(tv.numerator, tv.denominator), sp.Rational(v.numerator, v.denominator))
           for tv, v in zip(ts, vs)]
    return sp.expand(sp.interpolate(pts, t))


def run(w2, w3, a, b, label, npts=40, step=F(1, 50), t0=F(0)):
    ts = [t0 + step * k for k in range(npts)]
    data = slice_points(w2, w3, a, b, ts)
    # build N_6(t) and D_9(t) symbolic-in-t via interpolation of values
    good_t, N_vals, D_vals = [], [], []
    for tv, oms, im in data:
        d9 = r4lib.Dn(oms)
        good_t.append(tv)
        N_vals.append(im * d9 / F(2 ** 5))   # N_6 value
        D_vals.append(d9)
    # interpolate N_6(t) and D_9(t)
    Npoly = interp_poly(good_t, N_vals)
    Dpoly = interp_poly(good_t, D_vals)
    print(f"\n=== {label}: w2={w2},w3={w3}, slice w4={a}+t, w5={b}-t ===")
    print("deg N_6(t) =", sp.degree(Npoly, t), "  deg D_9(t) =", sp.degree(Dpoly, t))
    print("D_9(t) factored:", sp.factor(Dpoly))
    print("N_6(t) factored:", sp.factor(Npoly))
    A = sp.cancel(Npoly / Dpoly)
    print("A_6/i = N/D simplified, factored:", sp.factor(A))
    return Npoly, Dpoly


if __name__ == "__main__":
    # a few chambers (vary the fixed minus legs and slice center)
    run(2, 3, 5, 7, "chamber-1 (generic)")
    run(2, 3, 4, 9, "chamber-2")
    run(1, 6, 5, 8, "chamber-3")
