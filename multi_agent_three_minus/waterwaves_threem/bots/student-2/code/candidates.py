#!/usr/bin/env python3
"""Test truncated-power ansatz candidates for A_6 three-minus against the oracle.
A_6 is degree-8 homogeneous, pole-free (piecewise polynomial), symmetric under
S_3 (minus legs) x S_3 (plus legs) x Z_2 (swap of the two triples).

Building block (two-minus law applied to a designated 'minus-role' pair {a,b}
with the remaining legs R as 'plus-role'), exponent p=n-3=3 at n=6:
   B({a,b};R) = w_a w_b * sum_{S subseteq R} (-1)^{|S|}
                 ( min(w_a^2,w_b^2) - sum_{j in S} w_j^2 )_+^3
"""
from fractions import Fraction as F
from itertools import combinations
import harness as h


def trunc_block(pair, R, w):
    """w: dict leg->Fraction (1-indexed). pair=(a,b) minus-role legs; R list plus-role."""
    a, b = pair
    beta2 = min(w[a] ** 2, w[b] ** 2)
    tot = F(0)
    R = list(R)
    for r in range(len(R) + 1):
        for S in combinations(R, r):
            v = beta2 - sum(w[j] ** 2 for j in S)
            if v > 0:
                tot += F((-1) ** len(S)) * v ** 3
    return w[a] * w[b] * tot


def oracle_A6(free):
    im, oms, _ = h.on_shell(free, [-1, -1, -1, 1, 1, 1])
    w = {i + 1: oms[i] for i in range(6)}
    return im, w


MINUS = [1, 2, 3]
PLUS = [4, 5, 6]


def G_plus(w):  # sum over plus-leg pairs as minus-role
    tot = F(0)
    for pair in combinations(PLUS, 2):
        R = MINUS + [x for x in PLUS if x not in pair]
        tot += trunc_block(pair, R, w)
    return tot


def G_minus(w):  # sum over minus-leg pairs as minus-role
    tot = F(0)
    for pair in combinations(MINUS, 2):
        R = PLUS + [x for x in MINUS if x not in pair]
        tot += trunc_block(pair, R, w)
    return tot


CANDS = {
    "16*G_plus": lambda w: 16 * G_plus(w),
    "16*G_minus": lambda w: 16 * G_minus(w),
    "16*(G_plus+G_minus)": lambda w: 16 * (G_plus(w) + G_minus(w)),
    "32*G_plus": lambda w: 32 * G_plus(w),
    "8*(G_plus+G_minus)": lambda w: 8 * (G_plus(w) + G_minus(w)),
}

PTS = [[2, 3, 5, 7], [1, 4, 6, 9], [2, 2, 7, 3], [1, 1, 10, 4],
       [F(1, 2), 3, 9, 5], [7, 1, 2, 8], [3, 3, 3, 4], [5, 5, F(1, 3), 6],
       [9, 2, 1, 11], [F(3, 7), F(11, 5), 6, 4]]

if __name__ == "__main__":
    print(f"Testing candidates vs oracle at {len(PTS)} points (g=1, coeff 2^5=32 baseline):\n")
    for name, fn in CANDS.items():
        nmatch = 0; ratios = []
        for free in PTS:
            try:
                A, w = oracle_A6(free)
            except Exception:
                continue
            cand = fn(w)
            ok = (cand == A)
            nmatch += ok
            ratios.append(float(A / cand) if cand != 0 else None)
        print(f"  {name:>22}: {nmatch}/{len(PTS)} exact;  A/cand ratios (first 5): "
              f"{[round(r,4) if r else r for r in ratios[:5]]}")
