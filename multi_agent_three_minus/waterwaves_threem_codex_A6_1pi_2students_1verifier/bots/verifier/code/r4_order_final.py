#!/usr/bin/env python3
"""Nail the order-3 R_spline jump on line1 with a validated holdout, and print
the exact local jump expansion J(u)=sum a_k u^k, u=t-t0 (t0=1/4)."""
from fractions import Fraction as F
from r4_verify import R_spline
from r4_line_test import omega_of_t, word_of, poly_fit, poly_eval

Pt=[F(8),F(2),F(-3),F(-5),F(4),F(-6)]; d=[F(-2),F(1),F(0),F(2),F(-1),F(0)]
t0=F(1,4); lo,hi=F(-1,2),F(1)

# clean left deg-8
left=[lo+(t0-lo)*F(k,15) for k in range(1,15)]
RSL=[R_spline(omega_of_t(Pt,d,t)) for t in left]
cL=poly_fit(left[:9],RSL[:9],8)
assert all(poly_eval(cL,left[i])==RSL[i] for i in range(9,14)), "left not clean"

# right points close to t0 with small denominators: t0 + 1/28 * j
rs=[t0+F(1,28)*j for j in range(1,9)]           # 8 close points, same magnitude cell
assert all(word_of(omega_of_t(Pt,d,t))==word_of(omega_of_t(Pt,d,left[0])) for t in rs)
us=[t-t0 for t in rs]
Js=[R_spline(omega_of_t(Pt,d,t))-poly_eval(cL,t) for t in rs]

# fit J(u) with degree 5 using 6 points, VALIDATE on remaining 2
c=poly_fit(us[:6],Js[:6],5)
val=all(poly_eval(c,us[i])==Js[i] for i in range(6,8))
print("J(u) local expansion coeffs a_0..a_5:", [str(x) for x in c])
print("holdout validation on 2 farther close points:", val)
lp=next(i for i,x in enumerate(c) if x!=0)
print(f"lowest nonzero power = {lp}  => R_spline jump across Q_T=0 is ORDER {lp} in (t-t0)~Q_T")
print(f"leading local coefficient a_{lp} = {c[lp]}")
