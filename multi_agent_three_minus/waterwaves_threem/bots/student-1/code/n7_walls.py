#!/usr/bin/env python3
"""n=7 wall map + single-wall jump EXPONENTS (student-1, round 7), EXACT.

Three mixed-wall orbit types under S_3(minus) x S_4(plus): (1=1),(1=2),(1=3).
For each, construct a base point exactly ON the wall at t=0, scan an F-const slice
on each side STAYING IN ONE CHAMBER, fit N_7(t) as a polynomial each side, and read
off the order of vanishing of the jump N_R-N_L at t=0 (= the truncated-power exponent).

CLEAN single-wall discipline: between the two sides exactly ONE wall function flips
sign (sign-diff = 1) and no same-type tie occurs.
"""
from fractions import Fraction as F
import sympy as sp, itertools
import n7lib as L, r5lib as RL

t = sp.Symbol('t')

def sig_nowall(oms):
    return L.signature(oms, with_orderings=True)

def chamber_sig(free):
    o = L.solve_squares(free)
    if o is None or any(w == 0 for w in o):
        return None
    return sig_nowall(o)

def collect_side(base_free, p, q, A, B, direction, step, maxn, ref_sig):
    """contiguous in-chamber points on one side; returns [(t, N7)]."""
    tvals = []; omsl = []; frees = []
    for k in range(1, maxn+1):
        tt = direction*step*k
        fr = L.fc_free(base_free, p, q, A, B, tt)
        o = L.solve_squares(fr)
        if o is None or any(w == 0 for w in o):
            break
        s = sig_nowall(o)
        if s is None or s != ref_sig:
            break
        tvals.append(tt); omsl.append(o); frees.append(fr)
    if not frees:
        return []
    ims = L.batch_amp(frees)
    out = []
    for tt, o, im in zip(tvals, omsl, ims):
        if im is None:
            continue
        out.append((tt, L.N7_from_im(o, im)))
    return out

def signdiff(sigL, sigR):
    """number of wall functions (first 42) that differ in sign."""
    return sum(1 for a, b in zip(sigL[:42], sigR[:42]) if a != b)

def measure(name, base_free, p, q, A, B, step=F(1,60), maxn=70, dmax=46):
    """base_free has free[p]=A, free[q]=B nominally; t=0 is ON the wall."""
    # signatures just off the wall
    frL = L.fc_free(base_free, p, q, A, B, -step/3)
    frR = L.fc_free(base_free, p, q, A, B, +step/3)
    sL = chamber_sig(frL); sR = chamber_sig(frR)
    if sL is None or sR is None:
        print(f"[{name}] degenerate near wall"); return None
    sd = signdiff(sL, sR)
    print(f"[{name}] sign-diff across wall = {sd}  (want 1 for clean single-wall)")
    ptsL = collect_side(base_free, p, q, A, B, -1, step, maxn, sL)
    ptsR = collect_side(base_free, p, q, A, B, +1, step, maxn, sR)
    cL = RL.fit_poly(ptsL, dmax); cR = RL.fit_poly(ptsR, dmax)
    if cL is None or cR is None:
        print(f"[{name}] fit fail: nL={len(ptsL)} nR={len(ptsR)} polyL={cL is not None} polyR={cR is not None}")
        return None
    NL = sum(sp.Rational(c.numerator, c.denominator)*t**j for j, c in enumerate(cL))
    NR = sum(sp.Rational(c.numerator, c.denominator)*t**j for j, c in enumerate(cR))
    d = sp.expand(NR - NL)
    degL = len(cL)-1; degR = len(cR)-1
    if d == 0:
        print(f"[{name}] sd={sd} nL={len(ptsL)} nR={len(ptsR)} degs=({degL},{degR}) -> JUMP SMOOTH (0) [not a wall of N_7]")
        return (sd, 0)
    P = sp.Poly(d, t)
    order = 0; nn = P
    while nn.eval(0) == 0 and nn.degree() > 0:
        nn = nn.diff(t); order += 1
    print(f"[{name}] sd={sd} nL={len(ptsL)} nR={len(ptsR)} degs=({degL},{degR}) -> JUMP ORDER (exponent) = {order}")
    return (sd, order)

if __name__ == "__main__":
    print("=== n=7 wall map ===")
    cnt = {'11':0, '12':0, '13':0}
    for w in L.WALLS:
        cnt[w[0]] += 1
    print(f"  (1=1) a_i=b_j        : {cnt['11']} walls")
    print(f"  (1=2) a_i=b_j+b_k     : {cnt['12']} walls")
    print(f"  (1=3) a_i=b_j+b_k+b_l : {cnt['13']} walls")
    print(f"  TOTAL mixed walls    : {sum(cnt.values())}")
    print("  (the (2=1) walls a_p+a_q=b_j are the SAME loci as (1=3) by complement)\n")

    print("=== single-wall jump exponents (EXACT) ===")
    # free = [w2,w3,w4,w5,w6]; idx: 0=w2(minus), 1=w3(minus), 2=w4(plus), 3=w5(plus), 4=w6(plus)

    # (1=1): a_2 = b_4  i.e. w2^2 = w4^2.  vary w4 (idx2) around A=w2=3; compensate w5 (idx3).
    # base chosen generic to avoid other walls at t=0.
    measure("(1=1) a2=b4", [F(3), F(5), F(3), F(8), F(11,2)], 2, 3, F(3), F(8))

    # (1=2): a_2 = b_4 + b_5 i.e. w2^2 = w4^2 + w5^2.  Want w2^2 = w4^2+w5^2 at t=0.
    # set w4=3,w5=4 -> w4^2+w5^2=25; need w2=5. vary w4 (idx2) around 3; compensate w6 (idx4).
    measure("(1=2) a2=b4+b5", [F(5), F(11,3), F(3), F(4), F(15,2)], 2, 4, F(3), F(15,2))

    # (1=3): a_2 = b_4+b_5+b_6 i.e. w2^2 = w4^2+w5^2+w6^2 (the three FREE plus legs).
    # pick w4=2,w5=3,w6=6 -> sum sq=4+9+36=49 -> w2=7. vary w2 (idx0) around 7; compensate w6 (idx4).
    measure("(1=3) a2=b4+b5+b6", [F(7), F(9,2), F(2), F(3), F(6)], 0, 4, F(7), F(6))
