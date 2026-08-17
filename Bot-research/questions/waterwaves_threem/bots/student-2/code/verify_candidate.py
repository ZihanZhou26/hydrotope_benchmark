#!/usr/bin/env python3
"""Reusable EXACT verification harness for a three-minus closed-form candidate.

A candidate is a python callable  cand(omega, sigma, g) -> Fraction*1j coefficient
(we work with the imaginary coefficient as an exact Fraction), taking the full
length-n frequency list `omega` (Fractions), the sign list `sigma`, and g.

verify_at(cand, free_points, signs, g) builds the on-shell omega via the SAME
solve as the oracle (harness.solve_legs_1n), evaluates the oracle (exact) and the
candidate, and reports the exact residual cand-oracle (0 == exact agreement).

Run as a script with a built-in candidate placeholder for smoke-testing the
machinery on the KNOWN n=5 law (which must pass).
"""
from fractions import Fraction as F
import harness as h


def verify_at(cand, free_points, signs, g=1, label=""):
    n = len(signs)
    n_pass = 0; n_tot = 0; fails = []
    for free in free_points:
        n_tot += 1
        try:
            oim, oms, _ = h.on_shell([F(x) for x in free], signs, g=g)
        except Exception:
            n_tot -= 1
            continue  # SIGFPE on a wall -> skip (sample interior only)
        omega = oms  # exact Fractions, full length-n
        cval = cand(omega, signs, g)
        resid = cval - oim
        if resid == 0:
            n_pass += 1
        else:
            rel = float(resid) / float(oim) if oim != 0 else float(resid)
            fails.append((free, oim, cval, rel))
    print(f"[{label}] n={n}: EXACT {n_pass}/{n_tot}")
    for free, o, c, rel in fails[:6]:
        print(f"    FAIL free={free}: oracle={o} cand={c} rel={rel:.3e}")
    return n_pass, n_tot


def wall_limit(cand, free_of_eps, signs, eps_seq, g=1, label=""):
    """free_of_eps: callable eps->free list. Approach a wall from both sides;
    report oracle vs candidate at shrinking eps (exact)."""
    print(f"[{label}] two-sided wall limit:")
    for eps in eps_seq:
        free = free_of_eps(eps)
        try:
            oim, oms, _ = h.on_shell([F(x) for x in free], signs, g=g)
        except Exception:
            print(f"    eps={eps}: oracle SIGFPE (on wall)"); continue
        cval = cand(oms, signs, g)
        resid = cval - oim
        print(f"    eps={eps}: oracle={oim}  cand-oracle={resid}  ({'OK' if resid==0 else 'DIFF'})")


# ---- known n=5 three-minus law, as a self-test of the harness ----
def n5_law(omega, sigma, g=1):
    """A_5 = i 2^4 g^-2 w4 w5 sum_{S subseteq {1,2,3}} (-1)^|S| (beta^2-sum_S w^2)_+^2,
    beta = min(|w4|,|w5|).  Returns the imaginary coeff (Fraction)."""
    from itertools import combinations
    w = {i+1: F(omega[i]) for i in range(5)}
    beta2 = min(w[4]**2, w[5]**2)
    tot = F(0)
    minus = [1,2,3]
    for r in range(0,4):
        for S in combinations(minus, r):
            thr = beta2 - sum(w[j]**2 for j in S)
            if thr > 0:
                tot += F((-1)**r) * thr**2
    return F(16) * F(g)**(-2) * w[4]*w[5] * tot


if __name__ == "__main__":
    signs5 = [-1,-1,-1,1,1]
    pts = [[2,3,5],[1,2,4],[3,1,5],[5,2,3],[F(7,2),F(1,3),5],
           [10,1,2],[1,1,F(5,2)],[2,3,F(9,2)],[4,5,1],[6,1,3]]
    verify_at(n5_law, pts, signs5, label="n5 self-test")
