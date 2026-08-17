#!/usr/bin/env python3
"""Sanity check the chamber-fit machinery on n=5, where C_5 = omega4*omega5 * P(omega^2)
is KNOWN. The hypothesis F=omega4*omega5 should HOLD (validate fully); F=1 should FAIL.
"""
import itertools, random
from fractions import Fraction as F
import sympy as sp
import harness as h

SIG5 = [-1, -1, -1, 1, 1]
MINUS5 = [1, 2, 3]; PLUS5 = [4, 5]
random.seed(5)


def mixed_subsets5():
    subs = []
    for rm in range(1, 4):
        for Sm in itertools.combinations(MINUS5, rm):
            for rp in range(1, 3):
                for Sp in itertools.combinations(PLUS5, rp):
                    S = tuple(Sm) + tuple(Sp)
                    if len(S) < 5:
                        subs.append(S)
    return subs


MIX5 = mixed_subsets5()


def chamber_sig5(om):
    return tuple(1 if sum(F(SIG5[i-1])*om[i-1]**2 for i in S) > 0 else -1 for S in MIX5)


def gen5(reffree, refsig, ntarget, spread=20):
    pts = []; tries = 0
    while len(pts) < ntarget and tries < ntarget*400:
        tries += 1
        free = [reffree[i] + F(random.randint(-spread, spread), 100) for i in range(3)]
        try:
            om = h.solve_legs_1n(free, SIG5)
        except Exception:
            continue
        if any(o == 0 for o in om):
            continue
        if chamber_sig5(om) != refsig:
            continue
        pts.append((free, om))
    return pts


def monomials(maxdeg, nv):
    mons = []
    for total in range(maxdeg+1):
        for combo in itertools.combinations_with_replacement(range(nv), total):
            e = [0]*nv
            for c in combo:
                e[c] += 1
            mons.append(tuple(e))
    return mons


def design_row(om, mons, nv):
    # x1..x_{nv} ; for n=5 use x1,x2,x3,x4 (x5 from resonance x5=x1+x2+x3-x4)
    x = [om[i]**2 for i in range(nv)]
    row = []
    for e in mons:
        v = F(1)
        for i in range(nv):
            v *= x[i]**e[i]
        row.append(sp.Rational(v.numerator, v.denominator))
    return row


def test(hyp, deg, Ffun):
    ref_free = [F(2), F(5), F(3)]
    om = h.solve_legs_1n(ref_free, SIG5)
    refsig = chamber_sig5(om)
    nv = 4  # x1..x4
    mons = monomials(deg, nv)
    pts = gen5(ref_free, refsig, len(mons)+20)
    rows = [design_row(o, mons, nv) for _, o in pts]
    ys = []
    for free, o in pts:
        im, _, _ = h.on_shell(free, SIG5)
        C = F(im, 16)  # n=5 prefactor 2^{n-1}=2^4=16
        y = C / Ffun(o)
        ys.append(sp.Rational(y.numerator, y.denominator))
    M = sp.Matrix(rows[:len(mons)]); b = sp.Matrix(ys[:len(mons)])
    try:
        c = M.LUsolve(b)
    except Exception:
        print(f"  [{hyp}] singular"); return
    ok = sum(1 for k in range(len(mons), len(pts)) if sp.simplify(sum(c[i]*rows[k][i] for i in range(len(mons)))-ys[k]) == 0)
    tot = len(pts)-len(mons)
    print(f"  [{hyp}] basis={len(mons)} validate={ok}/{tot}  {'HOLDS' if ok==tot and tot>0 else 'fails'}")


if __name__ == "__main__":
    print("n=5 sanity (C_5 = w4 w5 * P(omega^2) is KNOWN true):")
    test("w4w5", 4, lambda om: om[3]*om[4])     # deg 8 -> P deg 4 in x  (KNOWN: should HOLD)
    test("even", 4, lambda om: F(1))            # should FAIL (C_5 odd in 4,5)
