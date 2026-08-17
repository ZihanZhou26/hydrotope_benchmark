#!/usr/bin/env python3
"""Test the hypothesis  C_6 = e2(plus) * P(omega_i^2)  on a single chamber, and
extract P exactly. P is degree-6 in omega = degree-3 in x_i=omega_i^2.

Fit P over degree-<=3 monomials in x_1..x_6, eliminating x_6 = x1+x2+x3-x4-x5
(the resonance), within one chamber (fixed signs of all mixed k_S). Solve exactly
over Q, then validate on held-out in-chamber points.
"""
import itertools, random
from fractions import Fraction as F
import sympy as sp
import harness as h
from cand_test import e_sym

MINUS = [1, 2, 3]; PLUS = [4, 5, 6]
SIG6 = [-1, -1, -1, 1, 1, 1]
random.seed(2026)


def mixed_subsets():
    subs = []
    for rm in range(1, 4):
        for Sm in itertools.combinations(MINUS, rm):
            for rp in range(1, 4):
                for Sp in itertools.combinations(PLUS, rp):
                    S = tuple(Sm) + tuple(Sp)
                    if len(S) == 6:
                        continue  # full set: k_S=0 identically (momentum cons.)
                    subs.append(S)
    return subs


MIX = mixed_subsets()


def chamber_sig(om):
    sig = []
    for S in MIX:
        ks = sum(F(SIG6[i-1]) * om[i-1]**2 for i in S)
        sig.append(1 if ks > 0 else (-1 if ks < 0 else 0))
    return tuple(sig)


def e2_plus(om):
    return e_sym([om[i-1] for i in PLUS], 2)


def gen_inchamber(reffree, refsig, ntarget):
    """Perturb the reference free-freqs by small rationals; keep same chamber."""
    pts = []
    tries = 0
    while len(pts) < ntarget and tries < ntarget * 300:
        tries += 1
        free = [reffree[i] + F(random.randint(-40, 40), 100)
                for i in range(4)]
        try:
            om = h.solve_legs_1n(free, SIG6)
        except Exception:
            continue
        if any(o == 0 for o in om):
            continue
        cs = chamber_sig(om)
        if 0 in cs or cs != refsig:
            continue
        pts.append((free, om))
    return pts


# monomial basis: degree<=3 in x1..x5 (x6 eliminated)
def monomials():
    mons = []
    for total in range(0, 4):
        for combo in itertools.combinations_with_replacement(range(5), total):
            exps = [0]*5
            for c in combo:
                exps[c]+=1
            mons.append(tuple(exps))
    return mons


MONS = monomials()


def xvec(om):
    # x_i = omega_i^2 ; x6 = x1+x2+x3-x4-x5 (resonance), so vars are x1..x5
    return [om[i]**2 for i in range(5)]  # x1..x5


def design_row(om):
    x = xvec(om)
    row = []
    for e in MONS:
        v = F(1)
        for i in range(5):
            v *= x[i]**e[i]
        row.append(v)
    return row


if __name__ == "__main__":
    # reference chamber: pick a generic OFF-WALL reference (no zero in signature)
    candidates = [[F(2), F(5), F(3), F(11)], [F(3), F(7), F(2), F(13)],
                  [F(13,5), F(17,3), F(7,2), F(23,4)], [F(2), F(9), F(4), F(7)],
                  [F(5), F(2), F(13), F(3)]]
    ref_free = None; refsig = None
    for cf in candidates:
        om = h.solve_legs_1n(cf, SIG6)
        cs = chamber_sig(om)
        if 0 not in cs and all(o != 0 for o in om):
            ref_free, refsig = cf, cs
            ref_om = om
            break
    print("reference free:", [str(o) for o in ref_free])
    print("reference omega:", [str(o) for o in ref_om])
    print("num mixed walls:", len(MIX), " basis size:", len(MONS))
    pts = gen_inchamber(ref_free, refsig, len(MONS) + 40)
    print(f"in-chamber points: {len(pts)}")
    if len(pts) < len(MONS) + 5:
        print("NOT ENOUGH POINTS"); raise SystemExit

    def yval(free, om):
        im, _, _ = h.on_shell(free, SIG6)
        C = F(im, 32)
        y = C / e2_plus(om)
        return sp.Rational(y.numerator, y.denominator)

    rows = [design_row(om) for _, om in pts]
    rows = [[sp.Rational(v.numerator, v.denominator) for v in r] for r in rows]
    ys = [yval(free, om) for free, om in pts]

    # pick a full-rank square subsystem
    Aall = sp.Matrix(rows)
    nM = len(MONS)
    # use first nM rows; if singular, sympy solve will error -> add more
    A = sp.Matrix(rows[:nM])
    bvec = sp.Matrix(ys[:nM])
    try:
        c = A.LUsolve(bvec)
    except Exception as e:
        print("LU failed, trrying solve_least_squares:", e)
        c = Aall.solve_least_squares(sp.Matrix(ys))
    # validate on the held-out points
    ok = 0; tot = 0
    for k in range(nM, len(pts)):
        tot += 1
        pred = sum(c[i] * rows[k][i] for i in range(nM))
        if sp.simplify(pred - ys[k]) == 0:
            ok += 1
    print(f"VALIDATION (held-out): {ok}/{tot} exact")
    if ok == tot and tot > 0:
        print("\n*** CONFIRMED: C_6 = e2(plus) * P(x) on this chamber. ***")
        xs = sp.symbols("x1 x2 x3 x4 x5")
        P = 0
        for i, e in enumerate(MONS):
            if c[i] != 0:
                term = c[i]
                for j in range(5):
                    term *= xs[j] ** e[j]
                P += term
        print("P(x1..x5; x6=x1+x2+x3-x4-x5) =", sp.expand(P))
    else:
        print("\nHypothesis C_6=e2*P(omega^2) FAILED on this chamber (residual odd part).")
