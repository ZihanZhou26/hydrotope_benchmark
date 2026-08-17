#!/usr/bin/env python3
"""Channel / propagator-denominator bookkeeping for the three-minus sector.

A factorization channel for subset S has propagator denominator
    D_S = omega_S^2 / |k_S| - g,   omega_S = sum_{i in S} w_i,  k_S = sum_{i in S} sigma_i w_i^2 / g.
Internal line on-shell  <=>  D_S = 0  <=>  omega_S^2 = g |k_S|.

The BG amplitude (leg 1 = root) carries denominators D_S for every proper
subset S of {2,...,n} with 2<=|S|<=n-2.  By the complement identity
D_S = D_{complement} (total momentum/energy conserved), each channel can be
labelled by a subset of {1,...,n} up to complementation.
"""
from itertools import combinations
from fractions import Fraction as F


def all_channels(n):
    """Return list of frozenset channels (subsets of 1..n, 2<=|S|<=n-2),
    deduped by complement. 1-indexed legs."""
    full = frozenset(range(1, n + 1))
    seen = set()
    out = []
    for sz in range(2, n - 1):
        for c in combinations(range(1, n + 1), sz):
            S = frozenset(c)
            comp = full - S
            key = frozenset([S, comp])
            if key in seen:
                continue
            seen.add(key)
            out.append(S)
    return out


def omega_k_S(S, omegas, signs, g=1):
    """omega_S, k_S for 1-indexed subset S. omegas, signs are 0-indexed lists."""
    wS = sum(omegas[i - 1] for i in S)
    kS = sum(signs[i - 1] * omegas[i - 1] ** 2 for i in S)
    kS = kS / g
    return wS, kS


def D_S(S, omegas, signs, g=1):
    wS, kS = omega_k_S(S, omegas, signs, g)
    if kS == 0:
        return None  # |k_S|=0 wall
    return wS * wS / abs(kS) - g


def channel_label(S, n):
    """Human label: which legs, and minus/plus composition (legs 1,2,3 minus)."""
    minus = sorted(i for i in S if i <= 3)
    plus = sorted(i for i in S if i > 3)
    return f"S={sorted(S)} ({len(minus)}m+{len(plus)}p)"


if __name__ == "__main__":
    import harness as h
    free = [F(2), F(3), F(5), F(7)]
    signs = [-1, -1, -1, 1, 1, 1]
    oms = h.solve_legs_1n(free, signs)
    print("omegas:", [str(x) for x in oms])
    print(f"{'channel':>22} {'omega_S':>10} {'k_S':>12} {'D_S':>14}")
    for S in all_channels(6):
        wS, kS = omega_k_S(S, oms, signs)
        d = D_S(S, oms, signs)
        print(f"{channel_label(S,6):>22} {str(wS):>10} {str(kS):>12} "
              f"{(str(d) if d is not None else 'WALL k=0'):>14}")
