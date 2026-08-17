#!/usr/bin/env python3
"""Independent symbolic determination of the A_6 (three-minus) denominator.

Trick to keep it FAST: vary TWO plus legs with opposite increments so that
sumFree = w2+w3+w4+w5 stays CONSTANT.  Then the on-shell-solved legs w1,w6
(= -(F^2 +- R)/(2F)) are POLYNOMIAL in t (no sumFree denominators), every w_i(t)
is a low-degree polynomial, and the ONLY denominators of A_6(t) are the kernel
magnitudes |k_S|(t) and propagators D_S(t).  Reduce to lowest terms and factor
the denominator; identify each factor as a momentum subset sum k_S.

Base point t=0 is free=(2,3,5,7) (a clean generic chamber interior, A_6=-29948208/17).
Independent of student-1's symslice.py (different base, different slice, F const).
"""
import sympy as sp
from itertools import combinations
from symbolic_bg import SymEngine

t = sp.Symbol('t')
SIG = [-1,-1,-1,1,1,1]

# F-constant slice: w4 -> 5+t, w5 -> 7-t ; w2=2,w3=3 fixed.  F=17 always.
w2, w3 = sp.Integer(2), sp.Integer(3)
w4 = sp.Integer(5) + t
w5 = sp.Integer(7) - t
F = w2 + w3 + w4 + w5            # = 17
R = -w2**2 - w3**2 + w4**2 + w5**2
w1 = -(F**2 + R)/(2*F)
w6 = -(F**2 - R)/(2*F)
W = {1: w1, 2: w2, 3: w3, 4: w4, 5: w5, 6: w6}
print("w1(t) =", sp.expand(w1), " w6(t) =", sp.expand(w6), flush=True)
assert sp.simplify(sum(W[i] for i in range(1,7))) == 0
assert sp.simplify(sum(sp.Integer(SIG[i-1])*W[i]**2 for i in range(1,7))) == 0

ref = {t: sp.Integer(0)}
E = SymEngine(W, W, ref, G=1)
E.K = {i: sp.Integer(SIG[i-1])*W[i]**2 for i in range(1,7)}
re, im = E.BGAmplitude()
print("amplitude computed; together...", flush=True)
im = sp.together(im)
num, den = sp.fraction(im)
print("together done; reducing via gcd...", flush=True)
num = sp.expand(num); den = sp.expand(den)
g = sp.gcd(num, den)
numR = sp.simplify(num/g); denR = sp.simplify(den/g)
print("REDUCED denominator (factored):", sp.factor(denR), flush=True)
print("denominator degree in t:", sp.degree(sp.expand(denR), t), flush=True)
print("numerator degree in t:", sp.degree(sp.expand(numR), t), flush=True)
print("POLYNOMIAL in t?:", sp.degree(sp.expand(denR), t) == 0, flush=True)

# identify denominator factors as k_S (same-type subsets give sums of squares)
print("\n--- match reduced-denominator factors to |k_S|(t) ---", flush=True)
kS = {}
for r in range(1,6):
    for S in combinations(range(1,7), r):
        kS[S] = sp.expand(sum(sp.Integer(SIG[i-1])*W[i]**2 for i in S))
for fac, mult in sp.factor_list(denR)[1]:
    if sp.degree(sp.Poly(sp.expand(fac), t)) == 0:
        continue
    matches = []
    for S, expr in kS.items():
        if sp.expand(expr) == 0: continue
        q = sp.cancel(sp.expand(expr)/fac)
        if q.free_symbols == set() and q != 0:
            tag = ''.join(f"{'+' if SIG[i-1]>0 else '-'}w{i}^2" for i in S)
            matches.append(f"|k_{S}| ~ {tag} (x{q})")
    print(f"  factor {sp.factor(fac)} (mult {mult}) -> {matches if matches else 'NO single-k_S match'}", flush=True)

# oracle cross-check
print("\n--- oracle cross-check ---", flush=True)
import harness as h
from fractions import Fraction as Fr
Rrat = numR/denR
for tv in [Fr(1,3), Fr(-2,5), Fr(4,7), Fr(-9,8)]:
    val = sp.nsimplify(Rrat.subs(t, sp.Rational(tv.numerator, tv.denominator)))
    freev = [Fr(2), Fr(3), Fr(5)+tv, Fr(7)-tv]
    oim, _, _ = h.on_shell(freev, SIG)
    ok = sp.Rational(oim.numerator, oim.denominator) == val
    print(f"  t={tv}: match={ok}", flush=True)
