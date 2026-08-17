#!/usr/bin/env python3
"""Exact candidate tester for three-minus A_n.

A candidate is a function cand(om, n) -> Fraction giving the imaginary
coefficient A_n/i. We compare to the oracle (exact rational) at many on-shell
points spanning multiple chambers and several n, and report exact-match counts
and (if not matching) the ratio A_oracle/cand to expose constant-vs-nonconstant.
"""
import os, itertools, random
from fractions import Fraction as F
import harness as h

random.seed(12345)


def pos(x):
    return x if x > 0 else F(0)


def trunc_sum(knots_sq, t, p):
    """sum_{S subseteq knots} (-1)^|S| (t - sum_S)_+^p ; knots_sq = list of squared freqs."""
    s = F(0)
    K = list(knots_sq)
    for r in range(len(K) + 1):
        for S in itertools.combinations(range(len(K)), r):
            c = sum(K[i] for i in S)
            s += F((-1) ** r) * pos(t - c) ** p
    return s


def e_sym(vals, k):
    """elementary symmetric polynomial e_k of vals (list)."""
    s = F(0)
    for S in itertools.combinations(range(len(vals)), k):
        prod = F(1)
        for i in S:
            prod *= vals[i]
        s += prod
    return s


def onshell_points(n, signs, nfree, chambers_filter=None, rng_lo=1, rng_hi=9):
    """Generate (free, omegas) exact on-shell points. nfree controls count."""
    pts = []
    tries = 0
    while len(pts) < nfree and tries < nfree * 40:
        tries += 1
        free = [F(random.randint(rng_lo, rng_hi), random.randint(1, 3)) for _ in range(n - 2)]
        # avoid trivial degeneracies
        try:
            om = h.solve_legs_1n(free, signs)
        except Exception:
            continue
        if any(o == 0 for o in om):
            continue
        # avoid landing exactly on |k_S|=0 walls (oracle SIGFPE) by a quick check
        ok = True
        sig = signs
        # check mixed subset sums k_S != 0
        for r in range(2, n):
            for Ssub in itertools.combinations(range(n), r):
                ks = sum(F(sig[i]) * om[i] ** 2 for i in Ssub)
                if ks == 0:
                    ok = False; break
            if not ok:
                break
        if not ok:
            continue
        pts.append((free, om))
    return pts


def evaluate(cand, n, signs, pts, label="cand"):
    nmatch = 0
    ratios = []
    details = []
    for free, om in pts:
        try:
            im, _, _ = h.on_shell(free, signs)
        except Exception:
            continue
        c = cand(om, n)
        ok = (F(c) == im)
        nmatch += ok
        if c != 0:
            ratios.append(im / F(c))
        details.append((free, im, c, ok))
    # constancy of ratio
    rset = set(ratios)
    const = (len(rset) == 1)
    print(f"  [{label}] n={n}: {nmatch}/{len(pts)} exact;  ratio constant={const}"
          + (f" ratio={ratios[0]}" if const and ratios else "")
          + (f"  sample ratios={[str(r) for r in ratios[:4]]}" if not const else ""))
    return nmatch, len(pts), const, ratios


if __name__ == "__main__":
    sig6 = [-1, -1, -1, 1, 1, 1]
    pts6 = onshell_points(6, sig6, 12)
    print(f"generated {len(pts6)} n=6 points")
    # quick self-test: the trivial "0" candidate
    evaluate(lambda om, n: F(0), 6, sig6, pts6, "zero")
