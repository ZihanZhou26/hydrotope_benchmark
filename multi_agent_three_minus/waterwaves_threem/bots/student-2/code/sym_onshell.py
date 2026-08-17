#!/usr/bin/env python3
"""Compute the symbolic on-shell three-minus amplitude on a chosen chamber, as a
function of the free frequencies (legs 2..n-1), with legs 1,n solved like bg.cpp.
The propagator denominators cancel (pole-free sector) leaving a rational function
whose value on the manifold is the physical amplitude."""
import sympy as sp
from fractions import Fraction as F
import symbolic_bg as sb
import harness as h


def solved_W(free_syms, signs):
    """Mirror bg.cpp on-shell solve symbolically. free_syms: list of n-2 sympy
    symbols (legs 2..n-1). Returns dict 1..n -> sympy expr for W."""
    n = len(signs)
    s1 = sp.Integer(signs[0])
    sumFree = sum(free_syms)
    sumSig = sum(sp.Integer(signs[i + 1]) * free_syms[i] ** 2 for i in range(n - 2))
    wn = -(s1 * sumFree ** 2 + sumSig) / (2 * s1 * sumFree)
    w1 = -(sumFree + wn)
    W = {1: w1}
    for i in range(n - 2):
        W[i + 2] = free_syms[i]
    W[n] = wn
    return W


def amp_onshell(free_vals, signs, simplify=True):
    """free_vals: list of n-2 rationals (chamber reference). Build symbolic W in
    free symbols, fix chamber signs from free_vals, return simplified A (im part)
    as a sympy expr in the free symbols."""
    n = len(signs)
    syms = [sp.Symbol(f"x{i}") for i in range(n - 2)]
    W = solved_W(syms, signs)
    # reference dict for sign resolution (interior chamber point)
    ref = {syms[i]: sp.Rational(F(free_vals[i]).numerator, F(free_vals[i]).denominator)
           for i in range(n - 2)}
    E = sb.build_engine(W, signs, ref)
    re, im = E.BGAmplitude()
    if simplify:
        im = sp.cancel(sp.together(im))
    return im, syms, ref


if __name__ == "__main__":
    import time
    for free, signs, label in [
        ([F(2), F(3), F(5)], [-1, -1, -1, 1, 1], "n=5"),
    ]:
        t = time.time()
        im, syms, ref = amp_onshell(free, signs)
        dt = time.time() - t
        # numeric check
        val = im.subs(ref)
        oim, _, _ = h.on_shell(free, signs)
        print(f"{label}: ({dt:.1f}s) numeric match={sp.Rational(oim.numerator,oim.denominator)==sp.nsimplify(val)}")
        print(f"  A_{len(signs)} (im) on this chamber =")
        sp.pprint(sp.factor(im))
