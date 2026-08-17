#!/usr/bin/env python3
"""Cross-wall JUMP of the numerator N_6 across a (1=2) wall omega_4^2=omega_2^2+omega_3^2
(k_{234}=0). Reconstruct N_6(t)=A_6(t)*D_9(t) as a polynomial on each SIDE of the
wall (each side = one chamber), take the difference, and verify it factors as
const * (k_S)^p (a truncated power), confirming the box-spline / spline structure
of the numerator. On the F-const slice omega_4=5+t, omega_5=b-t (omega_2=3,omega_3=4),
the wall is at omega_4=5 i.e. t=0, and k_{234} = omega_4^2-omega_2^2-omega_3^2
= (5+t)^2-25 = t^2+10t = t(t+10) ~ 10 t near t=0.
"""
import sympy as sp
from fractions import Fraction as F
import harness as h, r4lib

t = sp.Symbol('t')
SIG = [-1, -1, -1, 1, 1, 1]


def N6_poly_on_side(w2, w3, a, b, ts):
    """Interpolate N_6(t)=A_6*D_9 from points ts (all one side of wall)."""
    good, vals = [], []
    for tv in ts:
        free = [F(w2), F(w3), F(a) + tv, F(b) - tv]
        try:
            im, oms, _ = h.on_shell(free, SIG)
        except Exception:
            continue
        good.append(tv); vals.append(F(im) * r4lib.Dn(oms))
    return sp.expand(sp.interpolate(
        [(sp.Rational(x.numerator, x.denominator), sp.Rational(v.numerator, v.denominator))
         for x, v in zip(good, vals)], t))


if __name__ == "__main__":
    w2, w3, a, b = 3, 4, 5, 12   # wall omega_4^2=9+16=25 -> omega_4=5 -> t=0
    # right side t>0 (15 points), left side t<0 (15 points)
    right_ts = [F(k, 200) for k in range(1, 16)]
    left_ts = [F(-k, 200) for k in range(1, 16)]
    NR = N6_poly_on_side(w2, w3, a, b, right_ts)
    NL = N6_poly_on_side(w2, w3, a, b, left_ts)
    print("deg NR =", sp.degree(NR, t), " deg NL =", sp.degree(NL, t))
    print("NR == NL ?", sp.expand(NR - NL) == 0)
    jump = sp.expand(NR - NL)
    print("\nJUMP NR - NL factored:", sp.factor(jump))
    # k_{234} on slice = omega_4^2-omega_2^2-omega_3^2 = (5+t)^2-25 = t(t+10)
    kS = t * (t + 10)
    for p in (1, 2, 3, 4):
        q, r = sp.div(jump, kS ** p, t)
        if r == 0:
            print(f"  jump divisible by k_S^{p};  jump/k_S^{p} =", sp.factor(q))
    # also confirm wall is crossed: sign of k_{234} flips? on slice k_S=t(t+10): t>0 -> +, t<0 -> -
    print("\n(k_{234}=t(t+10): >0 for t in (0,.075], <0 for t in [-.075,0) -> wall crossed at t=0)")
