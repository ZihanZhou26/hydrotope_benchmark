#!/usr/bin/env python3
"""Batch 1 of three-minus A_6 candidates (exact, oracle-validated).

Key facts used:
 - prefactor lead: on-shell e2(plus)=e2(minus)=:E2 (degree 2, Z_2-symmetric),
   generalizing the n=5 prefactor omega4*omega5 = e2(plus).
 - walls at k_R=0 (mixed R): sum_{j in T} w_j^2 = sum_{i in S} w_i^2.
 - degree 8, exponent in cubic block expected n-3 = 3 (or no-prefactor p=4).

Candidates: double-subset resonance spline
   J_pm(p) = sum_{S subseteq minus, T subseteq plus} (-1)^{|S|+|T|} (sum_T w^2 - sum_S w^2)_+^p
   J_abs(p)= sum ... |sum_T w^2 - sum_S w^2|^p
tested with prefactor E2 (p=3) and bare (p=4), scanning overall constant.
"""
import itertools
from fractions import Fraction as F
import harness as h
from cand_test import onshell_points, evaluate, pos, e_sym

MINUS = [1, 2, 3]; PLUS = [4, 5, 6]
SIG6 = [-1, -1, -1, 1, 1, 1]


def sq(om, legs):
    return [om[i - 1] ** 2 for i in legs]


def E2_plus(om):
    return e_sym([om[i - 1] for i in PLUS], 2)


def E2_minus(om):
    return e_sym([om[i - 1] for i in MINUS], 2)


def double_subset(om, p, absval=False):
    ms = sq(om, MINUS); ps = sq(om, PLUS)
    tot = F(0)
    for rs in range(4):
        for S in itertools.combinations(range(3), rs):
            sumS = sum(ms[i] for i in S)
            for rt in range(4):
                for T in itertools.combinations(range(3), rt):
                    sumT = sum(ps[i] for i in T)
                    arg = sumT - sumS
                    sgn = (-1) ** (rs + rt)
                    if absval:
                        tot += F(sgn) * abs(arg) ** p
                    else:
                        tot += F(sgn) * pos(arg) ** p
    return tot


if __name__ == "__main__":
    pts = onshell_points(6, SIG6, 14)
    print(f"{len(pts)} points\n")

    # First verify the e2(plus)==e2(minus) on-shell identity
    bad = 0
    for free, om in pts:
        if E2_plus(om) != E2_minus(om):
            bad += 1
    print(f"e2(plus)==e2(minus) on-shell: {len(pts)-bad}/{len(pts)} hold\n")

    cands = {
        "E2*J_+(3)":   lambda om, n: E2_plus(om) * double_subset(om, 3, False),
        "E2*J_abs(3)": lambda om, n: E2_plus(om) * double_subset(om, 3, True),
        "J_+(4)":      lambda om, n: double_subset(om, 4, False),
        "J_abs(4)":    lambda om, n: double_subset(om, 4, True),
        "E2*J_+(2)":   lambda om, n: E2_plus(om) * double_subset(om, 2, False),
        "E2*J_abs(2)": lambda om, n: E2_plus(om) * double_subset(om, 2, True),
    }
    for name, fn in cands.items():
        evaluate(fn, 6, SIG6, pts, name)
