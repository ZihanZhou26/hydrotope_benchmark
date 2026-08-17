#!/usr/bin/env python3
"""Walk omega_4 along the slice toward t=-8/5 (where the reconstructed in-chamber
rational form has a denominator root) and watch A_6 and the chamber signature.
Question: does A_6 actually diverge there (genuine pole of the in-chamber form),
or is t=-8/5 a chamber wall where a *different* analytic piece takes over and the
physical A_6 stays finite?"""
from fractions import Fraction as F
import harness as h
import chambers_n6 as cn

SIG = [-1, -1, -1, 1, 1, 1]
w2, w3, w5, a4 = F(1), F(-27, 10), F(12, 5), F(43, 10)


def sig(oms):
    sq = [w * w for w in oms]
    ws = cn.wall_signs(sq)
    if ws is None:
        return 'MIXED-WALL'
    a, b = sq[0:3], sq[3:6]
    if 0 in [a[0]-a[1], a[0]-a[2], a[1]-a[2], b[0]-b[1], b[0]-b[2], b[1]-b[2]]:
        return 'ORD-WALL'
    sa = tuple(1 if a[i] > a[j] else -1 for i, j in [(0,1),(0,2),(1,2)])
    sb = tuple(1 if b[i] > b[j] else -1 for i, j in [(0,1),(0,2),(1,2)])
    return ws + (sa, sb)


s0 = None
for k in [0, -50, -100, -150, -180, -189, -191, -195, -200, -210, -230, -250]:
    t = F(k, 120)
    free = (w2, w3, a4 + t, w5)
    oms = cn.solve_squares(free)
    if oms is None or any(w == 0 for w in oms):
        print(f"t={float(t):+.4f}: degenerate")
        continue
    sg = sig(oms)
    same = (sg == s0)
    if s0 is None:
        s0 = sg
        label = "(reference chamber)"
    else:
        label = "SAME" if same else f"DIFFERENT {sg}"
    try:
        im, _, _ = h.on_shell(list(free), SIG)
        print(f"t={float(t):+.4f} w4={float(a4+t):+.4f}: A6/i={float(im):+.6g}   {label}")
    except Exception:
        print(f"t={float(t):+.4f} w4={float(a4+t):+.4f}: ORACLE SIGFPE (exactly on wall)   {label}")

print("\nt=-8/5 = -1.600 -> k=-192/120;  t=-53/10=-5.3 (far).")
print("k_{3,4}=0 at w4=2.7 (w4^2=w3^2);  reconstructed pole at t=-8/5 i.e. w4=2.7.")
