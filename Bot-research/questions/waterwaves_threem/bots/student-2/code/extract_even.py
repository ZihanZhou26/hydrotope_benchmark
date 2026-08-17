#!/usr/bin/env python3
"""Test 'even' (C_6 polynomial in omega^2) with HOMOGENEOUS deg-4 x-monomials
(C_6 homogeneous deg 8 in omega = deg 4 in x_i=omega_i^2). 70 monomials.
If it holds, extract P on the chamber and print, plus its value table for matching.
"""
import itertools, random
from fractions import Fraction as F
import sympy as sp
import harness as h

MINUS = [1, 2, 3]; PLUS = [4, 5, 6]
SIG6 = [-1, -1, -1, 1, 1, 1]
random.seed(7)


def mixed_subsets():
    subs = []
    for rm in range(1, 4):
        for Sm in itertools.combinations(MINUS, rm):
            for rp in range(1, 4):
                for Sp in itertools.combinations(PLUS, rp):
                    S = tuple(Sm) + tuple(Sp)
                    if len(S) < 6:
                        subs.append(S)
    return subs


MIX = mixed_subsets()


def chamber_sig(om):
    return tuple(1 if sum(F(SIG6[i-1])*om[i-1]**2 for i in S) > 0 else -1 for S in MIX)


def gen(reffree, refsig, ntarget, spread=25):
    pts = []; tries = 0
    while len(pts) < ntarget and tries < ntarget*500:
        tries += 1
        free = [reffree[i] + F(random.randint(-spread, spread), 100) for i in range(4)]
        try:
            om = h.solve_legs_1n(free, SIG6)
        except Exception:
            continue
        if any(o == 0 for o in om) or chamber_sig(om) != refsig:
            continue
        pts.append((free, om))
    return pts


# homogeneous degree-4 monomials in x1..x5 (x6 = x1+x2+x3-x4-x5)
def hom_monomials(deg=4, nv=5):
    mons = []
    for combo in itertools.combinations_with_replacement(range(nv), deg):
        e = [0]*nv
        for c in combo:
            e[c] += 1
        mons.append(tuple(e))
    return mons


MONS = hom_monomials()


def row(om):
    x = [om[i]**2 for i in range(5)]
    r = []
    for e in MONS:
        v = F(1)
        for i in range(5):
            v *= x[i]**e[i]
        r.append(sp.Rational(v.numerator, v.denominator))
    return r


if __name__ == "__main__":
    ref_free = [F(2), F(5), F(3), F(11)]
    om = h.solve_legs_1n(ref_free, SIG6)
    refsig = chamber_sig(om)
    print("basis (hom deg4):", len(MONS))
    pts = gen(ref_free, refsig, len(MONS)+30)
    print("in-chamber pts:", len(pts))
    rows = [row(o) for _, o in pts]
    ys = []
    for free, o in pts:
        im, _, _ = h.on_shell(free, SIG6)
        ys.append(sp.Rational(F(im, 32).numerator, F(im, 32).denominator))
    M = sp.Matrix(rows[:len(MONS)]); b = sp.Matrix(ys[:len(MONS)])
    c = M.LUsolve(b)
    ok = sum(1 for k in range(len(MONS), len(pts))
             if sp.simplify(sum(c[i]*rows[k][i] for i in range(len(MONS)))-ys[k]) == 0)
    tot = len(pts)-len(MONS)
    print(f"VALIDATION: {ok}/{tot}  {'*** EVEN HOLDS ***' if ok==tot and tot>0 else 'even FAILS'}")
    if ok == tot and tot > 0:
        xs = sp.symbols("x1 x2 x3 x4 x5")
        P = 0
        for i, e in enumerate(MONS):
            if c[i] != 0:
                t = c[i]
                for j in range(5):
                    t *= xs[j]**e[j]
                P += t
        print("\nP (chamber, x6=x1+x2+x3-x4-x5) =")
        sp.pprint(sp.expand(P))
        print("\nnonzero coeffs:", sum(1 for ci in c if ci != 0), "/", len(MONS))
