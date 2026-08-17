#!/usr/bin/env python3
"""Exact reduced A_6(t) on an F-constant slice, with AGGRESSIVE cancellation at
every intermediate (so expressions stay small and the reduction is fast).
Reads off the TRUE denominator and factors it; identifies factors as kernel /
propagator structures.  Single analytic piece (signs frozen at t=0)."""
import sympy as sp
from symbolic_bg import SymEngine
from itertools import combinations

t = sp.Symbol('t')
SIG = [-1,-1,-1,1,1,1]

class FastEngine(SymEngine):
    def _c(self, e):
        return sp.cancel(e)
    def EKernel(self, n, ps):
        return self._c(super().EKernel(n, ps))
    def FKernel(self, n, ps):
        return self._c(super().FKernel(n, ps))
    @staticmethod
    def cmul(a, b):
        return (sp.cancel(a[0]*b[0]-a[1]*b[1]), sp.cancel(a[0]*b[1]+a[1]*b[0]))
    @staticmethod
    def cadd(a, b):
        return (sp.cancel(a[0]+b[0]), sp.cancel(a[1]+b[1]))
    def BGCurrent(self, S):
        r = super().BGCurrent(S)
        return (sp.cancel(r[0]), sp.cancel(r[1]))

# F-constant slice: w4=5+t, w5=7-t ; w2=2,w3=3
w2,w3 = sp.Integer(2),sp.Integer(3)
w4 = sp.Integer(5)+t; w5 = sp.Integer(7)-t
F = w2+w3+w4+w5; R = -w2**2-w3**2+w4**2+w5**2
w1 = -(F**2+R)/(2*F); w6 = -(F**2-R)/(2*F)
W = {1:w1,2:w2,3:w3,4:w4,5:w5,6:w6}
ref = {t: sp.Integer(0)}
E = FastEngine(W, W, ref, G=1)
E.K = {i: sp.Integer(SIG[i-1])*W[i]**2 for i in range(1,7)}
re, im = E.BGAmplitude()
im = sp.cancel(im)
num, den = sp.fraction(im)
print("REDUCED denominator factored:", sp.factor(den), flush=True)
print("den degree:", sp.degree(sp.expand(den), t), " num degree:", sp.degree(sp.expand(num), t), flush=True)

# identify each denominator factor
print("\n--- identify denominator factors ---", flush=True)
named = {}
for r in range(1,6):
    for S in combinations(range(1,7), r):
        named[('k',S)] = sp.expand(sum(sp.Integer(SIG[i-1])*W[i]**2 for i in S))   # |k_S| up to sign
# products w_i*w_j (from same-type propagators) and (w_i+w_j) etc
for i in range(1,7):
    named[('w',i)] = W[i]
for fac, mult in sp.factor_list(den)[1]:
    if sp.degree(sp.Poly(sp.expand(fac), t)) == 0: continue
    hit=[]
    for key, expr in named.items():
        e=sp.expand(expr)
        if e==0: continue
        q=sp.cancel(e/fac)
        if q.free_symbols==set() and q!=0:
            hit.append(f"{key} (x{q})")
    print(f"  factor {sp.factor(fac)} (mult {mult}) -> {hit if hit else '??? not a single k_S/w'}", flush=True)

# oracle cross-check
import harness as h
from fractions import Fraction as Fr
Rrat = num/den
for tv in [Fr(1,3),Fr(-2,5),Fr(4,7)]:
    val=sp.nsimplify(Rrat.subs(t, sp.Rational(tv.numerator,tv.denominator)))
    oim,_,_=h.on_shell([Fr(2),Fr(3),Fr(5)+tv,Fr(7)-tv], SIG)
    print(f"  t={tv}: match={sp.Rational(oim.numerator,oim.denominator)==val}", flush=True)
