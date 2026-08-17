#!/usr/bin/env python3
"""Decisive polynomial-vs-rational test for A_6 (three-minus), done SYMBOLICALLY
with my own validated BG engine (symbolic_bg.py).

Idea: pick a chamber-interior base point, a generic rational direction, and
parametrize the 4 free frequencies as omega_i(t)=base_i + t*dir_i.  Solve legs
1,6 on-shell as rational functions of t.  Freeze every |k_S| sign at t=0 (so the
whole line stays in ONE chamber's analytic piece).  Then A_6(t) is an exact
univariate rational function in t.  cancel() + factor the denominator:
  - constant denominator  -> A_6 is polynomial on the chamber  (student-2 r1)
  - nontrivial denominator -> A_6 is rational                  (student-1 r2)
and the factored denominator tells us EXACTLY which kernel magnitudes survive.
"""
import sympy as sp
from symbolic_bg import SymEngine

t = sp.Symbol('t')

def onshell_legs(free, signs):
    """free: dict {2,3,4,5}->expr(t). returns W dict 1..6 with legs1,6 solved.
    signs 0-indexed; legs1,6 are minus(-1),plus(+1)."""
    F = free[2] + free[3] + free[4] + free[5]
    # R = sum over free of sigma_i*omega_i^2 ; sigma: legs2,3 minus(-1), legs4,5 plus(+1)
    R = -free[2]**2 - free[3]**2 + free[4]**2 + free[5]**2
    w1 = -(F**2 + R) / (2*F)
    w6 = -(F**2 - R) / (2*F)
    W = {1: w1, 2: free[2], 3: free[3], 4: free[4], 5: free[5], 6: w6}
    return W, F, R

def run(base, direction, label):
    free = {i: sp.Rational(base[i]) + t*sp.Rational(direction[i]) for i in (2,3,4,5)}
    signs = [-1,-1,-1,1,1,1]
    W, F, R = onshell_legs(free, signs)
    # reference point t=0 for sign-freezing (must be a clean chamber interior)
    ref = {t: sp.Integer(0)}
    # sanity: confirm conservation laws hold symbolically
    s_w = sum(W[i] for i in range(1,7))
    s_k = sum(sp.Integer(signs[i-1])*W[i]**2 for i in range(1,7))
    assert sp.simplify(s_w) == 0, sp.simplify(s_w)
    assert sp.simplify(s_k) == 0, sp.simplify(s_k)
    E = SymEngine(W, W, ref, G=1)  # K built inside? no: build manually
    # build K with frozen-able signs (g=1): k_i = sigma_i * w_i^2
    E.K = {i: sp.Integer(signs[i-1]) * W[i]**2 for i in range(1,7)}
    E.W = W
    re, im = E.BGAmplitude()
    im = sp.cancel(sp.together(im))
    num, den = sp.fraction(im)
    num = sp.expand(num); den = sp.expand(den)
    g = sp.gcd(num, den)
    print(f"\n===== {label} =====")
    print("denominator (after cancel):", sp.factor(den))
    print("denominator degree in t:", sp.degree(den, t))
    print("numerator degree in t:", sp.degree(num, t))
    print("is polynomial in t?:", sp.degree(den, t) == 0)
    # numeric check at t=0 base point against direct engine value
    return im

if __name__ == "__main__":
    # base point ~ free=(2,3,5,7); generic small direction to stay in chamber
    run({2:2,3:3,4:5,5:7}, {2:sp.Rational(1,10),3:sp.Rational(-1,7),4:sp.Rational(1,5),5:sp.Rational(-1,3)},
        "chamber @ free=(2,3,5,7)")
