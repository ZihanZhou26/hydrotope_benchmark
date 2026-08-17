#!/usr/bin/env python3
"""Numerators (over D_9) of Cauchy/matching objects, computed WITHOUT cancel:
  perm[f/(wi+wj)] = (1/D9) * sum_sigma  prod_i f(w_i,w_sigma(i)) * prod_{(i,j) not in sigma}(w_i+w_j).
"""
import sympy as sp
from itertools import permutations

w = sp.symbols('w1 w2 w3 w4 w5 w6')
M = [0, 1, 2]
P = [3, 4, 5]
allpairs = [(i, j) for i in M for j in P]


def perm_num(f):
    """numerator of sum_sigma prod_i f(w_i,w_sigma(i))/(w_i+w_sigma(i)), over D9."""
    tot = sp.Integer(0)
    for sigma in permutations(P):
        used = set((M[a], sigma[a]) for a in range(3))
        fac = sp.Integer(1)
        for a in range(3):
            fac *= f(w[M[a]], w[sigma[a]])
        for (i, j) in allpairs:
            if (i, j) not in used:
                fac *= (w[i] + w[j])
        tot += fac
    return sp.expand(tot)


for name, f in [
    ("perm[1/(wi+wj)]", lambda x, y: sp.Integer(1)),
    ("perm[wi*wj/(wi+wj)]", lambda x, y: x * y),
    ("perm[(wi^2+wj^2)/(wi+wj)]", lambda x, y: x ** 2 + y ** 2),
    ("perm[wi^2*wj^2/(wi+wj)]", lambda x, y: x ** 2 * y ** 2),
]:
    num = perm_num(f)
    print(f"\n{name}: numerator deg =", sp.total_degree(num))
    print("  =", sp.factor(num))
