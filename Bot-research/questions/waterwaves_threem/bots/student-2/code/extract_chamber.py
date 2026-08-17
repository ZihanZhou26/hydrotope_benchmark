#!/usr/bin/env python3
"""Extract the EXACT symbolic per-chamber core C_6 = A_6/(i 2^5 g^-3) as a rational
function of the free legs, then N_6 = C_6 * (e3m+e3p).

Strategy: keep the n-2 free frequencies as sympy symbols; solve legs 1,n on-shell
(rational in the free symbols, sumFree denominator); pick a chamber by a reference
point; run the faithful symbolic BG engine (signs frozen at the reference).

This is for STRUCTURE RECOGNITION (top-down). Times each piece.
"""
import sympy as sp
import time
from symbolic_bg import SymEngine

SIG = [-1, -1, -1, 1, 1, 1]   # legs 1,2,3 minus; 4,5,6 plus


def solve_full(free_syms, signs):
    """free_syms: list of n-2 sympy exprs (legs 2..n-1). Return dict 1..n -> W expr."""
    n = len(signs)
    s1 = sp.Integer(signs[0])
    sumFree = sum(free_syms)
    sumSig = sum(sp.Integer(signs[i + 1]) * free_syms[i] ** 2 for i in range(n - 2))
    wn = -(s1 * sumFree ** 2 + sumSig) / (2 * s1 * sumFree)
    w1 = -(sumFree + wn)
    W = {1: sp.together(w1)}
    for i in range(n - 2):
        W[i + 2] = free_syms[i]
    W[n] = sp.together(wn)
    return W


def run(ref_free, label, free_idx=(0, 1, 2, 3)):
    """ref_free: 4 rationals (reference free legs 2,3,4,5) selecting the chamber.
    free_idx: which of the 4 free legs to keep symbolic (default all)."""
    n = 6
    syms = [sp.Symbol(f"f{i}") for i in range(n - 2)]
    # mix: symbolic where in free_idx, numeric (reference) otherwise
    free = []
    for i in range(n - 2):
        free.append(syms[i] if i in free_idx else sp.Rational(ref_free[i]))
    W = solve_full(free, SIG)
    # reference dict for sign evaluation (all numeric)
    refW = solve_full([sp.Rational(x) for x in ref_free], SIG)
    ref = {syms[i]: sp.Rational(ref_free[i]) for i in range(n - 2)}
    # also need numeric values of W1,W6 in ref (they are numbers already)
    K = {i: sp.Integer(SIG[i - 1]) * W[i] ** 2 for i in W}
    E = SymEngine(K, W, ref)
    t0 = time.time()
    re, im = E.BGAmplitude()
    t1 = time.time()
    print(f"\n=== {label}  (BG took {t1-t0:.1f}s) ===")
    im = sp.cancel(im)
    # C_6 = A_6/(i 2^5) = im/2^5
    C6 = sp.cancel(im / sp.Integer(2 ** 5))
    e3m = W[1] * W[2] * W[3]
    e3p = W[4] * W[5] * W[6]
    P3 = sp.cancel(e3m + e3p)
    N6 = sp.cancel(C6 * P3)
    t2 = time.time()
    print(f"simplify took {t2-t1:.1f}s")
    nC, dC = sp.fraction(C6)
    print("C6 numerator (factored):")
    sp.pprint(sp.factor(nC))
    print("C6 denominator (factored):")
    sp.pprint(sp.factor(dC))
    print("N6 = C6*(e3m+e3p) (factored):")
    sp.pprint(sp.factor(N6))
    return C6, N6, W


if __name__ == "__main__":
    # one clean reference chamber; keep just w4 symbolic first (fast 1-var sanity),
    # then all 4.
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "1var"
    ref = [2, 3, 5, 7]   # generic reference (chamber-1 above)
    if mode == "1var":
        run(ref, "ref chamber, w4 symbolic", free_idx=(2,))
    elif mode == "2var":
        run(ref, "ref chamber, w4,w5 symbolic", free_idx=(2, 3))
    elif mode == "all":
        run(ref, "ref chamber, all 4 free symbolic", free_idx=(0, 1, 2, 3))
