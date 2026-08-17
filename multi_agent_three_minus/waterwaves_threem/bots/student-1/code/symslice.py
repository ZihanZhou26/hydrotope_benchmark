#!/usr/bin/env python3
"""Exact symbolic A_6(t) along a 1D slice (vary w4) inside RAW0, via the verified
symbolic BG engine.  Reduce to lowest terms and read off the TRUE denominator
(poles).  Authoritative: no fitting."""
import sympy as sp
from fractions import Fraction as F
import symbolic_bg as sb
import harness as h

SIG = [-1, -1, -1, 1, 1, 1]
base = (F(-4, 5), F(-13, 5), F(-47, 10), F(47, 10))
t = sp.Symbol('t')
fr = [sp.Rational(base[0].numerator, base[0].denominator),
      sp.Rational(base[1].numerator, base[1].denominator),
      sp.Rational(base[2].numerator, base[2].denominator) + t,
      sp.Rational(base[3].numerator, base[3].denominator)]
s1 = sp.Integer(-1)
sumF = sum(fr)
sumSig = -fr[0]**2 - fr[1]**2 + fr[2]**2 + fr[3]**2
w6 = -(s1 * sumF**2 + sumSig) / (2 * s1 * sumF)
w1 = -(sumF + w6)
W = {1: w1, 2: fr[0], 3: fr[1], 4: fr[2], 5: fr[3], 6: w6}
ref = {t: sp.Integer(0)}
E = sb.build_engine(W, SIG, ref)
re, im = E.BGAmplitude()
print("raw computed; together...", flush=True)
im = sp.together(im)
num, den = sp.fraction(im)
print("together done; factoring den (uncancelled)...", flush=True)
print("DEN (uncancelled) factored:", sp.factor(den), flush=True)
g = sp.gcd(sp.expand(num), sp.expand(den))
denR = sp.cancel(den / g)
numR = sp.cancel(num / g)
print("REDUCED denominator factored:", sp.factor(denR), flush=True)
print("REDUCED numerator degree in t:", sp.degree(sp.expand(numR), t), flush=True)
# verify vs oracle
R = numR / denR
for tv in [F(1, 3), F(7, 5), F(-2, 3), F(9, 4)]:
    val = sp.nsimplify(R.subs(t, sp.Rational(tv.numerator, tv.denominator)))
    free = (base[0], base[1], base[2] + tv, base[3])
    try:
        oim, _, _ = h.on_shell(list(free), SIG)
        print(f"  t={tv}: match={sp.Rational(oim.numerator,oim.denominator)==val}", flush=True)
    except Exception as e:
        print(f"  t={tv}: oracle err", flush=True)
