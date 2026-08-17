#!/usr/bin/env python3
"""Can the symbolic engine produce A_6 symbolically (6 free symbols, chamber
signs frozen)? Time it; then verify it reproduces the oracle at the reference
point, and check A_6*D_9 reduces to a polynomial on the manifold."""
import time, sympy as sp
from fractions import Fraction as F
import symbolic_bg as S
import harness as h

SIG = [-1, -1, -1, 1, 1, 1]
w = sp.symbols('w1 w2 w3 w4 w5 w6')
W = {i + 1: w[i] for i in range(6)}

# reference point: on-manifold generic (legs 1,6 solved from free 2,3,5,7)
free = [F(2), F(3), F(5), F(7)]
oms = h.solve_legs_1n(free, SIG)
ref = {w[i]: sp.Rational(oms[i].numerator, oms[i].denominator) for i in range(6)}

t0 = time.time()
E = S.build_engine(W, SIG, ref)
re_, im_ = E.BGAmplitude()
t1 = time.time()
print(f"BGAmplitude built in {t1-t0:.1f}s; im is {'number' if im_.is_number else 'expression'}")

# numeric check at reference
val = im_.subs(ref)
oim, _, _ = h.on_shell(free, SIG)
print("sym(ref) =", sp.nsimplify(val), " oracle =", oim,
      " match =", sp.simplify(val - sp.Rational(oim.numerator, oim.denominator)) == 0)

t2 = time.time()
# Try to cancel into a single rational function
imc = sp.cancel(im_)
t3 = time.time()
print(f"cancel done in {t3-t2:.1f}s")
num, den = sp.fraction(imc)
print("den (factored):", sp.factor(den))
