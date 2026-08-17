#!/usr/bin/env python3
"""Test the all-n denominator conjecture at n=7 (three-minus: minus {1,2,3},
plus {4,5,6,7}).  Conjecture:
    A_7 = i 2^6 g^{-4} N_7 / D12,   D12 = prod_{i in 1,2,3} prod_{j in 4,5,6,7} (w_i + w_j).
Signature (exact): on a one-piece slice, A_7 * D12 reconstructs to a PURE power of
sumFree (the leg-1,7 solve artifact), with no other (w_i +/- w_j) factor.
Also reports A_7 alone (should be rational: residual NOT pure sumFree).
"""
from fractions import Fraction as F
import sympy as sp
import harness as h
from verify_denominator import reconstruct

SIG7 = [-1, -1, -1, 1, 1, 1, 1]
MINUS, PLUS = [1, 2, 3], [4, 5, 6, 7]
t = sp.Symbol('t')


def solve7(free):
    """free = (w2,w3,w4,w5,w6) -> full 7 omegas, legs 1,7 solved (sigma_1=-1)."""
    free = [F(x) for x in free]
    s1 = F(-1)
    sumFree = sum(free)
    if sumFree == 0:
        return None
    sgn = [-1, 1, 1, 1]   # legs 3? -> actually legs 2,3 minus; 4,5,6 plus
    # signs of legs 2..6 = (-1,-1,1,1,1)
    sigs = [-1, -1, 1, 1, 1]
    sumSig = sum(sigs[i] * free[i] ** 2 for i in range(5))
    w7 = -(s1 * sumFree ** 2 + sumSig) / (2 * s1 * sumFree)
    w1 = -(sumFree + w7)
    return [w1, free[0], free[1], free[2], free[3], free[4], w7]


def D12(oms):
    w = {i + 1: oms[i] for i in range(7)}
    p = F(1)
    for i in MINUS:
        for j in PLUS:
            p *= (w[i] + w[j])
    return p


def collect(base, vary, half=40, dt=F(1, 240), mult=True):
    pts = []
    for k in range(-half, half + 1):
        tt = k * dt
        free = list(base)
        free[vary - 2] = base[vary - 2] + tt
        oms = solve7(free)
        if oms is None or any(w == 0 for w in oms):
            continue
        d = D12(oms) if mult else F(1)
        if d == 0:
            continue
        try:
            im, _, _ = h.on_shell(free, SIG7)
        except Exception:
            continue
        pts.append((tt, im * d))
    return pts


if __name__ == "__main__":
    # generic interior free point (w2,w3,w4,w5,w6); legs 1,7 solved
    base = [F(7, 5), F(-23, 10), F(31, 10), F(9, 5), F(-13, 5)]
    oms0 = solve7(base)
    print(f"n=7 base omega = {[str(x) for x in oms0]}")
    print(f"  (minus 1,2,3 ; plus 4,5,6,7)\n")
    sf0 = sum(base)

    print("A_7 * D12 (vary w4):")
    pts = collect(base, 4, mult=True)
    res = reconstruct(pts, cap=44)
    if res is None:
        print(f"   reconstruct failed ({len(pts)} pts)")
    else:
        dN, dD, _, Dc = res
        Dpoly = sum(sp.Rational(c.numerator, c.denominator) * t ** k for k, c in enumerate(Dc))
        pure = sp.simplify(Dpoly / (sp.Rational(sf0.numerator, sf0.denominator) + t) ** dD)
        print(f"   {len(pts)} pts: deg N={dN} deg D={dD}; residual=sumFree^{dD} pure? "
              f"{bool(pure.is_number) and pure != 0}")
        print(f"   D(t) = {sp.factor(Dpoly)}")
