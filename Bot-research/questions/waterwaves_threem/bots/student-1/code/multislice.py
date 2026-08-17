#!/usr/bin/env python3
"""For ONE reference chamber, reconstruct the exact in-chamber rational form of
A_6 along each free leg (2,3,4,5) in turn, and read off the denominator factors.

Each varied leg w_v = base_v + t.  Reconstruct A_6(t)*sumFree(t)^8 = N(t)/D(t)
(exact Pade).  Factor D(t).  Match each root to the frequency condition it
represents (which (w_i +/- w_j) or sumFree vanishes there), to identify the
6-frequency denominator factors of this chamber.
"""
from fractions import Fraction as F
import sympy as sp
import harness as h
import chambers_n6 as cn
from rat_denom import reconstruct

SIG = [-1, -1, -1, 1, 1, 1]
BASE = {2: F(1), 3: F(-27, 10), 4: F(43, 10), 5: F(12, 5)}  # free legs 2,3,4,5


def full_sig(oms):
    sq = [w * w for w in oms]
    ws = cn.wall_signs(sq)
    if ws is None:
        return None
    a, b = sq[0:3], sq[3:6]
    if 0 in [a[0]-a[1], a[0]-a[2], a[1]-a[2], b[0]-b[1], b[0]-b[2], b[1]-b[2]]:
        return None
    sa = tuple(1 if a[i] > a[j] else -1 for i, j in [(0,1),(0,2),(1,2)])
    sb = tuple(1 if b[i] > b[j] else -1 for i, j in [(0,1),(0,2),(1,2)])
    return ws + (sa, sb)


def slice_denom(vary, half=90, dt=F(1, 120)):
    """Vary free leg `vary` (in {2,3,4,5}) around BASE; reconstruct A_6 rational
    form, return (dN, dD, Dfactored, root->omega map)."""
    pts = []
    s0 = full_sig(cn.solve_squares([BASE[2], BASE[3], BASE[4], BASE[5]]))
    for k in range(-half, half + 1):
        t = k * dt
        free = [BASE[2], BASE[3], BASE[4], BASE[5]]
        free[vary - 2] = BASE[vary] + t
        oms = cn.solve_squares(free)
        if oms is None or any(w == 0 for w in oms):
            continue
        if full_sig(oms) != s0:
            continue
        try:
            im, _, _ = h.on_shell(free, SIG)
        except Exception:
            continue
        sumF = sum(free)
        pts.append((t, im * sumF ** 8))
    res = reconstruct(pts)
    if res is None:
        return None
    dN, dD, Nc, Dc = res
    t = sp.Symbol('t')
    Dpoly = sum(sp.Rational(c.numerator, c.denominator) * t ** k for k, c in enumerate(Dc))
    return dN, dD, sp.factor(Dpoly), len(pts)


def interpret_root(vary, troot):
    """Given a rational root t* of D on the `vary` slice, find which omega
    relations (w_i +/- w_j = 0 or sumFree = 0) hold at w_vary = BASE[vary]+t*."""
    free = [BASE[2], BASE[3], BASE[4], BASE[5]]
    free[vary - 2] = BASE[vary] + troot
    oms = cn.solve_squares(free)
    if oms is None:
        return ["(degenerate)"]
    w = {i + 1: oms[i] for i in range(6)}     # 1-indexed frequencies
    hits = []
    sumF = free[0] + free[1] + free[2] + free[3]
    if sumF == 0:
        hits.append("sumFree=0 (=w1+w6=0)")
    for i in range(1, 7):
        for j in range(i + 1, 7):
            if w[i] + w[j] == 0:
                hits.append(f"w{i}+w{j}=0")
            if w[i] - w[j] == 0:
                hits.append(f"w{i}-w{j}=0")
    return hits or ["(no simple linear relation)"]


if __name__ == "__main__":
    print(f"reference chamber base free (w2,w3,w4,w5) = "
          f"{[str(BASE[i]) for i in (2,3,4,5)]}")
    oms0 = cn.solve_squares([BASE[2], BASE[3], BASE[4], BASE[5]])
    print(f"  full omega = {[str(x) for x in oms0]}")
    print(f"  sumFree = {sum(BASE.values())} (=-(w1+w6))\n")
    t = sp.Symbol('t')
    for vary in (2, 3, 4, 5):
        out = slice_denom(vary)
        if out is None:
            print(f"vary w{vary}: reconstruction failed"); continue
        dN, dD, Dfac, npts = out
        print(f"vary w{vary} ({npts} in-chamber pts): degN={dN} degD={dD}")
        print(f"   D(t) = {Dfac}")
        # roots
        for r in sp.Poly(sp.fraction(sp.together(Dfac))[0], t).all_roots():
            if r.is_rational:
                rr = F(int(sp.numer(r)), int(sp.denom(r)))
                print(f"     root t={rr} -> {interpret_root(vary, rr)}")
            else:
                print(f"     root t={r} (irrational; not a w_i+/-w_j wall)")
        print()
