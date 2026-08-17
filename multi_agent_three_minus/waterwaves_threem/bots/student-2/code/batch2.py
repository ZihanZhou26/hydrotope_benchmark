#!/usr/bin/env python3
"""Batch 2: mixed-pair prefactor candidates.
C_6 has mixed parity (even, prod6, e2 all FAILED). Inspired by n=5
(C_5 = w_a w_b * block), try sum over MIXED pairs (a in minus, b in plus):
  C_6 = kappa * sum_{a in M, b in P} w_a w_b * Block_{ab}
with Block over the remaining 4 legs R_ab = (M\{a}) U (P\{b}) (2 minus, 2 plus).
Block variants (degree 6 = exponent-3 cubic, deg-2 args):
  - truncated power over R_ab subsets with threshold theta, signs by type.
Also: sum over ALL pairs, same-type pairs with different blocks.
"""
import itertools
from fractions import Fraction as F
import harness as h
from cand_test import onshell_points, evaluate, pos

MINUS = [1, 2, 3]; PLUS = [4, 5, 6]
SIG6 = [-1, -1, -1, 1, 1, 1]


def x(om, i):
    return om[i-1]**2


def block_trunc(om, R, theta, p, signs_by_type=True):
    """sum_{S subseteq R} (-1)^|S| (theta - sum_{j in S} eps_j x_j)_+^p, eps minus=+1 plus=-1?
    Here use signed knots: for j in S, subtract sigma_j-based contribution."""
    tot = F(0)
    R = list(R)
    for r in range(len(R)+1):
        for S in itertools.combinations(R, r):
            c = F(0)
            for j in S:
                # knot value = x_j (magnitude); sign handling via theta
                c += x(om, j)
            tot += F((-1)**r) * pos(theta - c)**p
    return tot


def mixed_pairs_cand(om, theta_fn, p=3):
    tot = F(0)
    for a in MINUS:
        for b in PLUS:
            R = [i for i in MINUS if i != a] + [i for i in PLUS if i != b]
            theta = theta_fn(om, a, b)
            tot += om[a-1]*om[b-1] * block_trunc(om, R, theta, p)
    return tot


if __name__ == "__main__":
    pts = onshell_points(6, SIG6, 14)
    print(f"{len(pts)} points\n")
    Q = lambda om: sum(x(om, i) for i in MINUS)
    cands = {
        # threshold = x_a (minus energy of the pair)
        "mix w_aw_b, th=x_a, p3":  lambda om, n: mixed_pairs_cand(om, lambda o,a,b: x(o,a), 3),
        "mix w_aw_b, th=x_b, p3":  lambda om, n: mixed_pairs_cand(om, lambda o,a,b: x(o,b), 3),
        "mix w_aw_b, th=min(xa,xb)":lambda om, n: mixed_pairs_cand(om, lambda o,a,b: min(x(o,a),x(o,b)), 3),
        "mix w_aw_b, th=(xa+xb)/2": lambda om, n: mixed_pairs_cand(om, lambda o,a,b: (x(o,a)+x(o,b))/2, 3),
        "mix w_aw_b, th=Q/3, p3":   lambda om, n: mixed_pairs_cand(om, lambda o,a,b: Q(o)/3, 3),
        # exponent 2 variant (block deg 4) times... no, keep p3
        "mix w_aw_b, th=x_a, p2":  lambda om, n: mixed_pairs_cand(om, lambda o,a,b: x(o,a), 2),
    }
    for name, fn in cands.items():
        evaluate(fn, 6, SIG6, pts, name)
