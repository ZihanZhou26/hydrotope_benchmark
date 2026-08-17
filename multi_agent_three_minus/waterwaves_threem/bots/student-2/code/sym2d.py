#!/usr/bin/env python3
"""Per-chamber A_6 as an exact rational function of TWO free frequencies
(omega_4, omega_5 symbolic; omega_2, omega_3 fixed numeric; omega_1, omega_6
solved on-shell, rational in the symbols). Factor numerator & denominator to
read the per-chamber rational structure and confirm the D_9 denominator.
"""
import sympy as sp
import symbolic_bg as S
from fractions import Fraction as F
import harness as h

SIG = [-1, -1, -1, 1, 1, 1]
w4, w5 = sp.symbols('w4 w5')

# fixed minus legs 2,3
w2v, w3v = sp.Integer(2), sp.Integer(3)
# free legs (2,3,4,5) -> solve legs 1,6. sumFree = w2+w3+w4+w5
SF = w2v + w3v + w4 + w5
sumSig = (-1) * w2v**2 + (-1) * w3v**2 + 1 * w4**2 + 1 * w5**2   # sigma_i w_i^2 for legs 2,3,4,5
s1 = sp.Integer(-1)
w6 = -(s1 * SF**2 + sumSig) / (2 * s1 * SF)
w1 = -(SF + w6)
w6 = sp.simplify(w6); w1 = sp.simplify(w1)
print("w1 =", w1)
print("w6 =", w6)

W = {1: w1, 2: w2v, 3: w3v, 4: w4, 5: w5, 6: w6}

# reference point in a chamber: pick numeric w4,w5 (generic), eval signs there
ref_free = [F(2), F(3), F(5), F(7)]
oms = h.solve_legs_1n(ref_free, SIG)
ref = {w4: sp.Integer(5), w5: sp.Integer(7)}

E = S.build_engine(W, SIG, ref)
re_, im_ = E.BGAmplitude()
print("building rational function ...")
imc = sp.cancel(im_)
num, den = sp.fraction(imc)
print("\nDEN (factored):", sp.factor(den))
print("\nNUM (factored):", sp.factor(num))
# numeric check at reference
val = imc.subs(ref)
oim, _, _ = h.on_shell(ref_free, SIG)
print("\ncheck sym(ref)=", sp.nsimplify(val), " oracle=", oim,
      " match=", sp.simplify(val - sp.Rational(oim.numerator, oim.denominator)) == 0)
