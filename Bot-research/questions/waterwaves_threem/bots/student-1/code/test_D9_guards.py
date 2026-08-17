#!/usr/bin/env python3
"""Two guards for the claim  A_6 * D9 = polynomial(6 freqs),
   D9 = prod_{i in {1,2,3}, j in {4,5,6}} (w_i + w_j):

GUARD 1 (diagonal): vary TWO free legs together (w4 = a4 + t, w5 = a5 + 2t) so the
  slice is not axis-aligned.  A_6*D9 must still reconstruct to a pure power of the
  (now linear-in-t) sumFree -- i.e. polynomiality is not an axis artifact.

GUARD 2 (minimality): on the reference chamber, multiply A_6 by D9 with ONE factor
  removed (drop (w2+w4)).  The reconstruction must then expose (w2+w4) as a genuine
  residual denominator factor -> every mixed pair is necessary.
"""
from fractions import Fraction as F
import sympy as sp
import harness as h
import chambers_n6 as cn
from test_D9_global import reconstruct, full_sig, D9

SIG = [-1, -1, -1, 1, 1, 1]
MINUS, PLUS = [1, 2, 3], [4, 5, 6]
t = sp.Symbol('t')
BASE = [F(1), F(-27, 10), F(43, 10), F(12, 5)]   # free w2,w3,w4,w5 (reference chamber)


def D9_drop(oms, drop):
    w = {i + 1: oms[i] for i in range(6)}
    p = F(1)
    for i in MINUS:
        for j in PLUS:
            if (i, j) == drop:
                continue
            p *= (w[i] + w[j])
    return p


def diagonal():
    print("GUARD 1: diagonal slice  w4 = 43/10 + t,  w5 = 12/5 + 2t")
    pts = []
    s0 = full_sig(cn.solve_squares(BASE))
    for k in range(-70, 71):
        tt = F(k, 160)
        free = [BASE[0], BASE[1], BASE[2] + tt, BASE[3] + 2 * tt]
        oms = cn.solve_squares(free)
        if oms is None or any(w == 0 for w in oms):
            continue
        if full_sig(oms) != s0:
            continue
        d9 = D9(oms)
        if d9 == 0:
            continue
        try:
            im, _, _ = h.on_shell(free, SIG)
        except Exception:
            continue
        pts.append((tt, im * d9))
    res = reconstruct(pts)
    if res is None:
        print(f"   reconstruct failed ({len(pts)} pts)"); return
    dN, dD, Nc, Dc = res
    Dpoly = sum(sp.Rational(c.numerator, c.denominator) * t ** k for k, c in enumerate(Dc))
    print(f"   {len(pts)} pts: degN={dN} degD={dD}  D(t)={sp.factor(Dpoly)}")
    # sumFree(t) = w2+w3 + (w4+t) + (w5+2t) = const + 3t
    sf = sp.Rational((BASE[0]+BASE[1]+BASE[2]+BASE[3]).numerator,
                     (BASE[0]+BASE[1]+BASE[2]+BASE[3]).denominator) + 3 * t
    pure = sp.simplify(Dpoly / sf ** dD)
    print(f"   D(t)/sumFree^{dD} = {pure}  -> pure sumFree power? {pure.is_number}")


def minimality():
    print("\nGUARD 2: drop (w2+w4) from D9 on the reference chamber, vary w4")
    pts = []
    s0 = full_sig(cn.solve_squares(BASE))
    for k in range(-90, 91):
        tt = F(k, 120)
        free = [BASE[0], BASE[1], BASE[2] + tt, BASE[3]]
        oms = cn.solve_squares(free)
        if oms is None or any(w == 0 for w in oms):
            continue
        if full_sig(oms) != s0:
            continue
        d = D9_drop(oms, (2, 4))
        if d == 0:
            continue
        try:
            im, _, _ = h.on_shell(free, SIG)
        except Exception:
            continue
        pts.append((tt, im * d))
    res = reconstruct(pts)
    if res is None:
        print(f"   reconstruct failed ({len(pts)} pts)"); return
    dN, dD, Nc, Dc = res
    Dpoly = sum(sp.Rational(c.numerator, c.denominator) * t ** k for k, c in enumerate(Dc))
    print(f"   {len(pts)} pts: degN={dN} degD={dD}  D(t)={sp.factor(Dpoly)}")
    # (w2+w4)=0 at w4=-w2=-1 -> t = -1 - 43/10 = -53/10
    print("   expect a factor vanishing at t=-53/10 (w2+w4=0) -> 10*t+53")


if __name__ == "__main__":
    diagonal()
    minimality()
