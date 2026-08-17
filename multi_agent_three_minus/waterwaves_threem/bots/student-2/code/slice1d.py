#!/usr/bin/env python3
"""Symbolic 1-D slice of the ON-SHELL three-minus amplitude on a single chamber.

Vary one free frequency symbolically (leg `var`, one of 2..n-1); fix the others
rational. Solve legs 1,n on-shell (rational functions of the symbol). Pick a
chamber by a reference point (fixes all |k_S| signs). Compute A_n symbolically
with the validated engine and simplify -> a rational function of the symbol that
collapses to a polynomial (sector is pole-free) on that chamber. Print it to read
off degree and parity.
"""
import sympy as sp
from fractions import Fraction as F
import symbolic_bg as S


def onshell_symbolic(free_syms, signs):
    """free_syms: dict pos(2..n-1)->sympy expr. signs: list len n. Returns dict 1..n->expr."""
    n = len(signs)
    s1 = sp.Integer(signs[0])
    SF = sum(free_syms[i] for i in range(2, n))
    SS = sum(sp.Integer(signs[i - 1]) * free_syms[i] ** 2 for i in range(2, n))
    wn = -(s1 * SF ** 2 + SS) / (2 * s1 * SF)
    w1 = -(SF + wn)
    W = {1: sp.together(w1)}
    for i in range(2, n):
        W[i] = free_syms[i]
    W[n] = sp.together(wn)
    return W


def slice_amp(var_leg, fixed, signs, ref_free):
    """var_leg: which middle leg is symbolic. fixed: dict pos->rational for the others.
    ref_free: dict pos->rational reference (defines the chamber)."""
    n = len(signs)
    x = sp.Symbol("x", real=True)
    free_syms = {}
    for i in range(2, n):
        free_syms[i] = x if i == var_leg else sp.Rational(fixed[i])
    W = onshell_symbolic(free_syms, signs)
    # reference point for chamber signs: substitute x = ref value
    refval = sp.Rational(ref_free[var_leg])
    Wref = {i: (W[i].subs(x, refval) if hasattr(W[i], "subs") else W[i]) for i in W}
    ref = {sp.Symbol(f"w{i}"): Wref[i] for i in W}
    # engine works with symbol dict; we pass W (in x) as the W dict and ref for signs
    K = {i: sp.Integer(signs[i - 1]) * W[i] ** 2 for i in W}
    # the engine's sgn() uses .subs(ref); but our exprs are in x, ref must map x.
    eng = S.SymEngine(K, W, {x: refval})
    re, im = eng.BGAmplitude()
    im = sp.simplify(im)
    return x, im, W


if __name__ == "__main__":
    signs = [-1, -1, -1, 1, 1, 1]
    # chamber reference: a generic interior point
    ref_free = {2: F(2), 3: F(3), 4: F(5), 5: F(7)}
    fixed = {2: F(2), 3: F(3), 4: F(5), 5: F(7)}
    for var in [2, 4]:
        x, im, W = slice_amp(var, fixed, signs, ref_free)
        core = sp.simplify(im / sp.Integer(2) ** 5)  # C = A/(i 2^5 g^-3), g=1
        core = sp.nsimplify(core)
        poly_like = sp.together(core)
        print(f"\n=== vary leg {var} (others fixed {fixed}) ===")
        print("C(x) =", sp.simplify(core))
        # parity test
        even = sp.simplify(core.subs(x, -x) - core) == 0
        odd = sp.simplify(core.subs(x, -x) + core) == 0
        print(f"parity in x: even={even} odd={odd}")
