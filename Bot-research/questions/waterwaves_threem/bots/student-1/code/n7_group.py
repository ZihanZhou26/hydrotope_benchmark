#!/usr/bin/env python3
"""n=7 symmetry group: S_3(minus legs 0,1,2) x S_4(plus legs 3,4,5,6). NO Z_2 swap (n>=7).
Leg perms as tuples: perm[k] = image position of leg k. Act on omega by relabeling:
newoms[perm[j]] = oms[j].  |G| = 6*24 = 144.
"""
import itertools
from fractions import Fraction as F

MINUS = [0, 1, 2]
PLUS = [3, 4, 5, 6]

def full_group():
    els = []
    for pm in itertools.permutations([0, 1, 2]):
        for pp in itertools.permutations([3, 4, 5, 6]):
            els.append(tuple(list(pm) + list(pp)))
    return els  # 144

def apply_perm(perm, oms):
    new = [None]*7
    for j in range(7):
        new[perm[j]] = oms[j]
    return new

def relabel_to_ref_minus(i):
    """perm sending minus leg i -> 0, the other two minus -> 1,2 (order fixed)."""
    others = [x for x in MINUS if x != i]
    pm = [None, None, None]; pm[i] = 0; pm[others[0]] = 1; pm[others[1]] = 2
    return pm  # length-3 list for minus block

def relabel_11(i, j):
    """(1=1) wall a_i=b_j -> ref minus0,plus3."""
    pm = relabel_to_ref_minus(i)
    others_p = [x for x in PLUS if x != j]
    pp = {j: 3}
    for idx, x in enumerate(others_p): pp[x] = 4+idx
    return tuple(pm + [pp[3] if 3 in pp else None,  # placeholder fix below
                       ])
def perm_11(i, j):
    """proper perm for (1=1): minus i->0, plus j->3, rest fixed order."""
    pm = relabel_to_ref_minus(i)
    others_p = [x for x in PLUS if x != j]
    img = {j: 3}
    for idx, x in enumerate(others_p): img[x] = 4+idx
    return tuple(pm + [img[3], img[4], img[5], img[6]] if False else
                 pm + [img[k] for k in PLUS])

def perm_12(i, pair):
    """(1=2) wall a_i = b_{pair0}+b_{pair1}: minus i->0, pair->{3,4}, other two plus->{5,6}."""
    pm = relabel_to_ref_minus(i)
    j, k = pair
    rest_p = [x for x in PLUS if x not in pair]
    img = {j: 3, k: 4, rest_p[0]: 5, rest_p[1]: 6}
    return tuple(pm + [img[x] for x in PLUS])

def perm_13(i, triple):
    """(1=3) wall a_i = b_j+b_k+b_l: minus i->0, triple->{3,4,5}, excluded plus->6."""
    pm = relabel_to_ref_minus(i)
    rest_p = [x for x in PLUS if x not in triple]
    img = {}
    for idx, x in enumerate(triple): img[x] = 3+idx
    img[rest_p[0]] = 6
    return tuple(pm + [img[x] for x in PLUS])

if __name__ == "__main__":
    G = full_group(); print("|G| =", len(G))
    oms = [F(-13,7), F(2), F(3), F(5), F(7), F(11,2), F(-83,9)]
    print("perm_11(1,4):", perm_11(1, 4), "->", apply_perm(perm_11(1, 4), oms))
    print("perm_12(0,(3,4)):", perm_12(0, (3, 4)))
    print("perm_13(0,(3,4,5)):", perm_13(0, (3, 4, 5)))
    # sanity: apply_perm with identity
    idp = tuple(range(7))
    assert apply_perm(idp, oms) == oms
    print("identity ok")
