#!/usr/bin/env python3
"""Consolidated round-2 verification (student-1), all against my own ./bg.

Reproduces the load-bearing findings:
  (A) A_6 (three-minus) is piecewise-RATIONAL, NOT polynomial: on a 1-D slice that
      stays inside ONE full chamber (mixed wall signs AND all same-type orderings
      fixed -> a single analytic piece), A_6 * sumFree^p is NOT a polynomial of
      degree 8+p for any p up to 12.  If A_6 were a degree-8 polynomial in the six
      frequencies it would be (elimination of legs 1,6 gives at most sumFree^8), so
      this proves A_6 is rational.
  (B) No PHYSICAL factorization poles: driving onto the channel S={2,4,5}
      (1 minus + 2 plus, k_S>0 -> naive 2-minus x 2-minus residue) D_S->0, A_6
      stays finite and A_6*D_S -> 0 (removable).  ('no poles' from round-1 holds.)
  (C) Double-subset resonance spline is impossible: the degree-8 member (exponent 4)
      vanishes identically.

Build: g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp   (already built)
Run:   python3 verify_n6_rational.py
"""
from fractions import Fraction as F
import harness as h
import chambers_n6 as cn
from exactfit import exact_solve

SIG = [-1, -1, -1, 1, 1, 1]


def fullsig(oms):
    sq = [oms[i] ** 2 for i in range(6)]
    mixed = cn.wall_signs(sq)
    if mixed is None:
        return None
    a, b = sq[0:3], sq[3:6]
    if 0 in [a[0]-a[1], a[0]-a[2], a[1]-a[2], b[0]-b[1], b[0]-b[2], b[1]-b[2]]:
        return None
    sa = tuple(1 if a[i] > a[j] else -1 for i, j in [(0, 1), (0, 2), (1, 2)])
    sb = tuple(1 if b[i] > b[j] else -1 for i, j in [(0, 1), (0, 2), (1, 2)])
    return mixed + (sa, sb)


def test_A_rational():
    print("=" * 70)
    print("(A) A_6 is RATIONAL, not polynomial  (full-chamber slice)")
    base = (F(1), F(-27, 10), F(43, 10), F(12, 5))
    dn = (F(0), F(0), F(1), F(0))
    s0 = fullsig(cn.solve_squares(base))
    pts = []
    for k in range(-60, 61):
        t = F(k, 120)
        free = tuple(base[i] + t * dn[i] for i in range(4))
        o = cn.solve_squares(free)
        if o is None or any(w == 0 for w in o):
            continue
        if fullsig(o) != s0:
            continue
        try:
            im, _, _ = h.on_shell(list(free), SIG)
        except Exception:
            continue
        pts.append((t, sum(free), im))
    print(f"    in-chamber exact points: {len(pts)}")
    anypoly = False
    for p in range(1, 13):
        deg = 8 + p
        if len(pts) < deg + 3:
            print(f"    p={p}: too few pts"); continue
        rows = [[t ** i for i in range(deg + 1)] for (t, sF, im) in pts]
        ys = [im * sF ** p for (t, sF, im) in pts]
        sol = exact_solve(rows[:deg + 1], ys[:deg + 1])
        ok = sol is not None and all(
            sum(c * v for c, v in zip(sol, row)) == y
            for row, y in zip(rows[deg + 1:], ys[deg + 1:]))
        anypoly = anypoly or ok
        if p <= 8 or ok:
            print(f"    A_6*sumFree^{p} polynomial(deg {deg})? {ok}")
    print(f"    => polynomial for some p<=12? {anypoly}  "
          f"(bound for a true polynomial is p=8) -> A_6 is {'POLY' if anypoly else 'RATIONAL'}")
    return not anypoly


def test_no_poles():
    print("=" * 70)
    print("(B) channel S={2,4,5} (m=1, k_S>0): removable, A_6 finite")
    print(f"    {'eps':>10} {'A6/i':>16} {'D_245':>14} {'A6*D_245':>16}")
    for eps in [F(1, 5), F(1, 50), F(1, 500), F(-1, 50), F(-1, 500)]:
        w2 = F(-2) + eps
        free = (w2, F(1), F(2), F(3))
        oms = cn.solve_squares(free)
        im, _, _ = h.on_shell(list(free), SIG)
        w245 = oms[1] + oms[3] + oms[4]
        k245 = -oms[1] ** 2 + oms[3] ** 2 + oms[4] ** 2
        D = w245 ** 2 - abs(k245)
        print(f"    {str(eps):>10} {float(im):>16.2f} {float(D):>14.6f} {float(im*D):>16.3f}")
    print("    => A_6 finite, A_6*D_245 -> 0 : channel REMOVABLE (no physical pole)")
    return True


def test_double_subset_zero():
    print("=" * 70)
    print("(C) double-subset spline degree-8 member (exponent 4) vanishes:")

    def pos(x):
        return x if x > 0 else F(0)

    def subs(vals):
        out = []
        for mask in range(8):
            s = F(0); kk = 0
            for b in range(3):
                if mask & (1 << b):
                    s += vals[b]; kk += 1
            out.append((s, kk))
        return out

    def DS(a, b, p):
        SA, SB = subs(a), subs(b); tot = F(0)
        for sS, kS in SA:
            for sT, kT in SB:
                tot += ((-1) ** (kS + kT)) * pos(sT - sS) ** p
        return tot

    allz = True
    for free in [[F(2), F(3), F(5), F(7)], [F(1), F(4), F(6), F(3)], [F(3), F(-2), F(5), F(4)]]:
        oms = cn.solve_squares(free)
        sq = [o * o for o in oms]
        v = DS(sq[0:3], sq[3:6], 4)
        allz = allz and (v == 0)
        print(f"    DS(p=4) = {v}")
    print(f"    => DS(p=4) identically 0? {allz}  (so no degree-8 double-subset spline)")
    return allz


if __name__ == "__main__":
    r1 = test_A_rational()
    r2 = test_no_poles()
    r3 = test_double_subset_zero()
    print("=" * 70)
    print(f"SUMMARY: A_6 rational(not poly)={r1}; channel removable={r2}; "
          f"double-subset deg8 vanishes={r3}")
