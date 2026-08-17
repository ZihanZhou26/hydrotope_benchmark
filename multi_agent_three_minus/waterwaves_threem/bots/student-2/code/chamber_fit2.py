#!/usr/bin/env python3
"""Fit C_6 on ONE chamber under several structural hypotheses, exactly.

Hypotheses for the odd prefactor F (so that C_6 = F * P(omega^2), P poly in x_i):
  - 'even'  : F=1                      -> P degree 4 in x   (C_6 even in each leg)
  - 'prod6' : F=prod_i omega_i (deg6)  -> P degree 1 in x   (fully-odd factor)
  - 'e2'    : F=e2(plus) (deg2)        -> P degree 3 in x
Within one chamber, fit P over x-monomials, solve a full-rank exact system,
validate on held-out in-chamber points. Reports which hypothesis holds.
"""
import itertools, random
from fractions import Fraction as F
import sympy as sp
import harness as h
from cand_test import e_sym

MINUS = [1, 2, 3]; PLUS = [4, 5, 6]
SIG6 = [-1, -1, -1, 1, 1, 1]
random.seed(99)


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


def gen_inchamber(reffree, refsig, ntarget, spread=40):
    pts = []; tries = 0
    while len(pts) < ntarget and tries < ntarget * 400:
        tries += 1
        free = [reffree[i] + F(random.randint(-spread, spread), 100) for i in range(4)]
        try:
            om = h.solve_legs_1n(free, SIG6)
        except Exception:
            continue
        if any(o == 0 for o in om):
            continue
        cs = chamber_sig(om)
        if cs != refsig:
            continue
        pts.append((free, om))
    return pts


def monomials(maxdeg, nv=5):
    mons = []
    for total in range(maxdeg + 1):
        for combo in itertools.combinations_with_replacement(range(nv), total):
            e = [0]*nv
            for c in combo:
                e[c] += 1
            mons.append(tuple(e))
    return mons


def design_row(om, mons):
    x = [om[i]**2 for i in range(5)]   # x1..x5 ; x6=x1+x2+x3-x4-x5
    row = []
    for e in mons:
        v = F(1)
        for i in range(5):
            v *= x[i]**e[i]
        row.append(sp.Rational(v.numerator, v.denominator))
    return row


HYP = {
    'prod6': (1, lambda om: prod_all(om)),                       # F deg6 -> P deg1 (6 mons)
    'e2':    (3, lambda om: e_sym([om[i-1] for i in PLUS], 2)),  # F deg2 -> P deg3 (56)
    'e3m':   (sp.Rational(5, 2), None),                          # placeholder, see below
    'even':  (4, lambda om: F(1)),                               # F=1   -> P deg4 (126)
}
# e3m needs integer degree; remove placeholder
HYP.pop('e3m', None)


def prod_all(om):
    p = F(1)
    for o in om:
        p *= o
    return p


def run(name, ref_free):
    om = h.solve_legs_1n(ref_free, SIG6)
    refsig = chamber_sig(om)
    print(f"\n=== chamber ref free={[str(x) for x in ref_free]} ===")
    for hyp, (deg, Ffun) in HYP.items():
        mons = monomials(deg)
        pts = gen_inchamber(ref_free, refsig, len(mons) + 25)
        if len(pts) < len(mons) + 10:
            print(f"  [{hyp}] not enough points ({len(pts)} / need {len(mons)})"); continue
        rows = [design_row(o, mons) for _, o in pts]
        ys = []
        for free, o in pts:
            im, _, _ = h.on_shell(free, SIG6)
            C = F(im, 32)
            Fv = Ffun(o)
            y = C / Fv
            ys.append(sp.Rational(y.numerator, y.denominator))
        M = sp.Matrix(rows[:len(mons)])
        bvec = sp.Matrix(ys[:len(mons)])
        try:
            c = M.LUsolve(bvec)
        except Exception:
            print(f"  [{hyp}] singular design (rank-deficient), skipping"); continue
        ok = 0; tot = 0
        for k in range(len(mons), len(pts)):
            tot += 1
            pred = sum(c[i]*rows[k][i] for i in range(len(mons)))
            if sp.simplify(pred - ys[k]) == 0:
                ok += 1
        verdict = "*** HOLDS ***" if (ok == tot and tot > 0) else "fails"
        print(f"  [{hyp}] basis={len(mons)} pts={len(pts)} validate={ok}/{tot}  {verdict}")
        if ok == tot and tot > 0:
            xs = sp.symbols("x1 x2 x3 x4 x5")
            P = 0
            for i, e in enumerate(mons):
                if c[i] != 0:
                    term = c[i]
                    for j in range(5):
                        term *= xs[j]**e[j]
                    P += term
            print("       P =", sp.expand(P))
            return hyp, c, mons
    return None


if __name__ == "__main__":
    run("c1", [F(2), F(5), F(3), F(11)])
