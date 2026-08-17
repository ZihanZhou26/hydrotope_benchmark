#!/usr/bin/env python3
"""ROUND 8: confirm the (1=3) single-wall exponent at n=7 is 4 (=n-3) and CLEAN
(J/v^4 is an exact polynomial => a chamber-independent (1=3) coefficient exists, the
n=7 analog of the n=6 (1=2) coefficient Q). EXACT ./bg --batch.

Also re-confirm (1=2)->2 / (1=1)->1 with the SAME J/v^e divisibility test, and check
the (1=3) cross-term cleanliness: unlike (1=2), NO disjoint-(1=1)-pair forces a (1=3)
wall (a pair forces a (1=2)), so (1=3) should be uncontaminated.
"""
from fractions import Fraction as F
import sympy as sp
import n7lib as L, r5lib as RL

SIG = L.SIG7
t = sp.Symbol('t')

def sig_at(bf, p, q, A, B, tt):
    o = L.solve_squares(L.fc_free(bf, p, q, A, B, tt))
    if o is None or any(w == 0 for w in o): return None
    return L.signature(o, with_orderings=True)

def collect_side(bf, p, q, A, B, direction, step, maxn, refsig):
    tvals, frees, omsl = [], [], []
    for k in range(1, maxn+1):
        tt = direction*step*k
        fr = L.fc_free(bf, p, q, A, B, tt)
        o = L.solve_squares(fr)
        if o is None or any(w == 0 for w in o): break
        s = L.signature(o, with_orderings=True)
        if s is None or s != refsig: break
        tvals.append(tt); frees.append(fr); omsl.append(o)
    if not frees: return []
    ims = L.batch_amp(frees)
    return [(tt, L.N7_from_im(o, im), o) for tt, o, im in zip(tvals, omsl, ims) if im is not None]

def measure(name, bf, p, q, A, B, wall_sm, wall_sp, exp_guess, step=F(1,120), maxn=120, dmax=48):
    """wall fn v = sum_{sp} b - sum_{sm} a ; sm minus indices, sp plus indices (n7lib idx)."""
    sL = sig_at(bf, p, q, A, B, -step/3); sR = sig_at(bf, p, q, A, B, +step/3)
    if sL is None or sR is None: print(f"[{name}] degenerate near wall"); return None
    sd = sum(1 for a, b in zip(sL[:42], sR[:42]) if a != b)
    ptsL = collect_side(bf, p, q, A, B, -1, step, maxn, sL)
    ptsR = collect_side(bf, p, q, A, B, +1, step, maxn, sR)
    cL = RL.fit_poly([(x, y) for (x, y, _) in ptsL], dmax)
    cR = RL.fit_poly([(x, y) for (x, y, _) in ptsR], dmax)
    if cL is None or cR is None:
        print(f"[{name}] sd={sd} FIT FAIL nL={len(ptsL)} nR={len(ptsR)} L={cL is not None} R={cR is not None}")
        return None
    NL = sum(sp.Rational(c.numerator, c.denominator)*t**j for j, c in enumerate(cL))
    NR = sum(sp.Rational(c.numerator, c.denominator)*t**j for j, c in enumerate(cR))
    J = sp.expand(NR - NL)
    if J == 0:
        print(f"[{name}] sd={sd} JUMP=0 (not a wall)"); return None
    Pj = sp.Poly(J, t); order = min(m for (m,), _ in Pj.terms())
    # wall fn v(t) exact (low degree) from a few points
    side = ptsR if len(ptsR) >= len(ptsL) else ptsL
    vpts = [(tt, sum([w*w for w in o][j] for j in wall_sp) - sum([w*w for w in o][i] for i in wall_sm))
            for (tt, _, o) in side[:10]]
    cv = RL.fit_poly(vpts, 8)
    vt = sum(sp.Rational(c.numerator, c.denominator)*t**j for j, c in enumerate(cv))
    quo, rem = sp.div(J, sp.expand(vt**exp_guess), t)
    ok = sp.simplify(rem) == 0
    print(f"[{name}] sd={sd} nL={len(ptsL)} nR={len(ptsR)} JUMP ORDER={order}; "
          f"J/v^{exp_guess} exact-divides={ok}; coeff-at-wall S(0)={sp.nsimplify(quo.subs(t,0)) if ok else 'n/a'}")
    return order, ok

if __name__ == "__main__":
    print("=== (1=3) a2 = b4+b5+b6 : exponent 4 + clean coefficient (J/v^4 poly) ===")
    # wall: w2^2 = w4^2+w5^2+w6^2. idx: minus w2=1; plus w4,w5,w6 = 3,4,5. excluded plus w7=6.
    # cross by varying w4 (idx2), compensate w7?? w7 is solved. compensate w3 (idx1, minus, not in wall).
    # Pick base so ONLY this (1=3) wall is crossed. vary the MINUS leg w2 (idx0) across, comp w3 (idx1).
    # near-equal plus triple => the (1=2) pair-walls sit far from the (1=3) wall (more chamber room).
    cfgs13 = [
        ("(1=3) #1", [F(9), F(7,2), F(6), F(6), F(3)], 0, 1, F(9), F(7,2)),   # 36+36+9=81 -> w2=9
        ("(1=3) #2", [F(7), F(9,2), F(6), F(3), F(2)], 0, 1, F(7), F(9,2)),   # 36+9+4=49 -> w2=7
        ("(1=3) #3", [F(11), F(7,2), F(9), F(6), F(2)], 0, 1, F(11), F(7,2)), # 81+36+4=121 -> w2=11
    ]
    for (nm, bf, p, q, A, B) in cfgs13:
        # wall fn v = b4+b5+b6 - a2 = (sq[3]+sq[4]+sq[5]) - sq[1]
        measure(nm, bf, p, q, A, B, wall_sm=[1], wall_sp=[3, 4, 5], exp_guess=4)

    print("\n=== controls: (1=1)->1 and (1=2)->2 with same J/v^e test ===")
    measure("(1=1) a2=b4", [F(3), F(5), F(3), F(8), F(11,2)], 2, 3, F(3), F(8),
            wall_sm=[1], wall_sp=[3], exp_guess=1)
    measure("(1=2) a2=b4+b5", [F(5), F(11,3), F(3), F(4), F(15,2)], 2, 4, F(3), F(15,2),
            wall_sm=[1], wall_sp=[3, 4], exp_guess=2)
