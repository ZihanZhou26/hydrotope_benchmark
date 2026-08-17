#!/usr/bin/env python3
"""Rigorously test whether a candidate location w* is a real chamber wall of A_6.

Method (exact): the symbolic engine resolves each |k_S| to a fixed sign taken
from a REFERENCE point. Freeze the signs at a point just LEFT of w*, then
evaluate that frozen-chamber formula at a point just RIGHT of w*, and compare to
the oracle's true value at the right point.
  - equal  => A_6 is the SAME analytic function across w*  => NOT a wall.
  - differ => the formula changed (some |k_S| flipped & A_6 depends on it)
              => REAL wall. The signs that differ identify the subset S.
"""
import sympy as sp
from fractions import Fraction as F
import symbolic_bg as sb
import harness as h

signs = [-1, -1, -1, 1, 1, 1]


def frozen_eval(free_eval, free_ref):
    """A_6 with chamber signs frozen at free_ref, evaluated at free_eval. Both are
    lists of 4 free freqs (legs 2,3,4,5). Returns sympy Rational (im part)."""
    oms_e = h.solve_legs_1n(free_eval, signs)
    oms_r = h.solve_legs_1n(free_ref, signs)
    Wnum = {i + 1: sp.Rational(oms_e[i].numerator, oms_e[i].denominator) for i in range(6)}
    ref = {sp.Symbol(f"w{i+1}"): sp.Rational(oms_r[i].numerator, oms_r[i].denominator)
           for i in range(6)}
    # engine needs W keyed 1..6 as sympy; but absR uses self.ref on expressions.
    # Build with symbolic-substituted numeric W but ref for the SIGN of each expr:
    # We pass W as the numeric (eval) values, and ref maps the SAME symbols. To make
    # sign() use the reference chamber while value uses eval point, we keep W as
    # symbols and substitute eval at the end.
    syms = {i + 1: sp.Symbol(f"w{i+1}") for i in range(6)}
    E = sb.build_engine(syms, signs, ref)
    re, im = E.BGAmplitude()
    subs_eval = {sp.Symbol(f"w{i+1}"): Wnum[i + 1] for i in range(6)}
    return sp.nsimplify(sp.simplify(im.subs(subs_eval)))


def check_wall(wstar, base, idx, eps=F(1, 50)):
    """base: 4 free freqs; idx: which free leg crosses the wall at value wstar."""
    left = list(base); left[idx] = F(wstar) - eps
    right = list(base); right[idx] = F(wstar) + eps
    # true oracle at right
    true_r, _, _ = h.on_shell(right, signs)
    # frozen-from-left formula evaluated at right
    frozen_r = frozen_eval(right, left)
    same = (sp.Rational(true_r.numerator, true_r.denominator) == frozen_r)
    # which k_S flips between left and right?
    oms_l = h.solve_legs_1n(left, signs); oms_r = h.solve_legs_1n(right, signs)
    flips = []
    from itertools import combinations
    for r in range(2, 5):
        for S in combinations(range(6), r):
            kl = sum(signs[i] * oms_l[i] ** 2 for i in S)
            kr = sum(signs[i] * oms_r[i] ** 2 for i in S)
            if kl * kr < 0:
                flips.append(tuple(s + 1 for s in S))
    return same, flips


if __name__ == "__main__":
    base = [F(3), F(5), F(0), F(8)]  # legs 2,3,4,5; vary leg4 (idx 2)
    for wstar in [F(3), F(5), F(28, 5), F(6, 5), F(4)]:  # 3.0,5.0,5.6(~5.83 region uses 28/5),1.2,4.0
        same, flips = check_wall(wstar, base, 2)
        tag = "NOT a wall (formula unchanged)" if same else "REAL WALL (formula changes)"
        print(f"leg4 = {float(wstar):.3f}: {tag};  k_S sign-flips across: {flips}")
