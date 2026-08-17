#!/usr/bin/env python3
"""CROSS-TERM test: measure the (1=2) wall {a2=b4+b5} jump order in several DIFFERENT
chambers. If the order varies (2 vs higher), the jump is cross-term-affected (= the
measured local order is min over single+cross terms). Record, for each crossing, the
ACTIVE (1=1) walls so we can correlate which partner lowers the exponent.

Pure single exponent = MAX order over chambers (all cross-partners inactive).
"""
from fractions import Fraction as F
import sympy as sp, itertools
import n7lib as L, r5lib as RL

t = sp.Symbol('t')

def csig(free):
    o = L.solve_squares(free)
    if o is None or any(w == 0 for w in o): return None
    return L.signature(o, with_orderings=False)

def active_11(o):
    """list of active (1=1) walls b_j>a_i (truncated power on)."""
    sq = [w*w for w in o]; out = []
    for i in L.MINUS:
        for j in L.PLUS:
            if sq[j] > sq[i]: out.append((i, j))
    return out

def collect(base, p, q, A, B, direction, step, maxn, ref):
    frees = []; omsl = []; tv = []
    for k in range(1, maxn+1):
        tt = direction*step*k
        fr = list(F(x) for x in base); fr[p] = F(A)+tt; fr[q] = F(B)-tt
        o = L.solve_squares(fr)
        if o is None or any(w == 0 for w in o): break
        if L.signature(o, with_orderings=False) != ref: break
        frees.append(fr); omsl.append(o); tv.append(tt)
    if not frees: return []
    ims = L.batch_amp(frees)
    return [(tt, L.N7_from_im(o, im)) for tt, o, im in zip(tv, omsl, ims) if im is not None]

def order_at_chamber(name, base, p, q, A, B, step=F(1,100), maxn=34, dmax=46):
    frL = list(F(x) for x in base); frL[p]=F(A)-step/3; frL[q]=F(B)+step/3
    frR = list(F(x) for x in base); frR[p]=F(A)+step/3; frR[q]=F(B)-step/3
    sL = csig(frL); sR = csig(frR)
    if sL is None or sR is None: print(f"  [{name}] degenerate"); return
    sd = sum(1 for a, b in zip(sL, sR) if a != b)
    oL = L.solve_squares(frL)
    act = active_11(oL)
    ptsL = collect(base, p, q, A, B, -1, step, maxn, sL)
    ptsR = collect(base, p, q, A, B, +1, step, maxn, sR)
    cL = RL.fit_poly(ptsL, dmax); cR = RL.fit_poly(ptsR, dmax)
    if cL is None or cR is None:
        print(f"  [{name}] sd={sd} FIT FAIL nL={len(ptsL)} nR={len(ptsR)}"); return
    NL = sum(sp.Rational(c.numerator, c.denominator)*t**j for j, c in enumerate(cL))
    NR = sum(sp.Rational(c.numerator, c.denominator)*t**j for j, c in enumerate(cR))
    d = sp.expand(NR - NL)
    if d == 0: print(f"  [{name}] sd={sd} SMOOTH"); return
    P = sp.Poly(d, t); order = 0; nn = P
    while nn.eval(0) == 0 and nn.degree() > 0: nn = nn.diff(t); order += 1
    # active (1=1) walls involving minus 2 (the wall's minus leg) excluding j,k=3,4 (b4,b5)
    a2act = [(i, j) for (i, j) in act if i == 1 and j in (5, 6)]  # a2 vs b6(idx5),b7(idx6)
    print(f"  [{name}] sd={sd} ORDER={order}  active(a2=b6?,a2=b7?): {a2act}  #active(1=1)={len(act)}")

if __name__ == "__main__":
    # (1=2) wall a2=b4+b5 (w2^2=w4^2+w5^2). vary w4 (idx2), comp w6 (idx4, plus, NOT in wall).
    # Different chambers via different w2,w3,w6 (and hence different active (1=1) walls).
    print("=== (1=2) {a2=b4+b5} jump order across chambers ===")
    order_at_chamber("c1 w2=5,w4=3,w5=4,w6=15/2,w3=11/3", [F(5),F(11,3),F(3),F(4),F(15,2)], 2, 4, F(3), F(15,2))
    order_at_chamber("c2 w2=5,w4=3,w5=4,w6=1/2,w3=11/3",  [F(5),F(11,3),F(3),F(4),F(1,2)],  2, 4, F(3), F(1,2))
    order_at_chamber("c3 w2=5,w4=4,w5=3,w6=9,w3=7/2",     [F(5),F(7,2),F(4),F(3),F(9)],     2, 4, F(4), F(9))
    order_at_chamber("c4 w2=5,w4=4,w5=3,w6=1/3,w3=7/2",   [F(5),F(7,2),F(4),F(3),F(1,3)],   2, 4, F(4), F(1,3))
    order_at_chamber("c5 w2=10,w4=6,w5=8,w6=1/2,w3=9/2",  [F(10),F(9,2),F(6),F(8),F(1,2)],  2, 4, F(6), F(1,2))
    order_at_chamber("c6 w2=10,w4=6,w5=8,w6=12,w3=9/2",   [F(10),F(9,2),F(6),F(8),F(12)],   2, 4, F(6), F(12))
