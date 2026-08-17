#!/usr/bin/env python3
"""Recognize the residue of A_6 at each perfect-matching pole.
At t=r_k: omega_i = -omega_sigma(i) (3 opposite pairs). Extract residue c_k and
compare to candidate expressions of the 3 pair-magnitudes m1,m2,m3 (= |omega| of
the 3 pairs): products, sums of squares, two-minus-like blocks, etc.
"""
import sympy as sp
from fractions import Fraction as F
import harness as h, r4lib
import residue as R

t = sp.Symbol('t')
SIG = [-1, -1, -1, 1, 1, 1]


def omegas_at(w2, w3, a, b, tv):
    free = [F(w2), F(w3), F(a) + tv, F(b) - tv]
    return h.solve_legs_1n(free, SIG)   # algebraic solve, no oracle (no SIGFPE)


def analyze(w2, w3, a, b, label):
    A = R.slice_rational(w2, w3, a, b)
    num, den = sp.fraction(A)
    print(f"\n=== {label}: w2={w2},w3={w3}, w4={a}+t, w5={b}-t ===")
    roots = sp.roots(sp.Poly(den, t))
    for r in sorted(roots, key=lambda x: float(x)):
        rr = sp.Rational(r)
        c = sp.limit((t - rr) * A, t, rr)
        tv = F(int(rr.p), int(rr.q))
        oms = omegas_at(w2, w3, a, b, tv)
        pairs = [(i + 1, j + 1) for i in (0, 1, 2) for j in (3, 4, 5) if oms[i] + oms[j] == 0]
        mags = sorted(set(abs(oms[i]) for i in range(6)))
        cF = F(int(sp.numer(c)), int(sp.denom(c)))
        print(f"\n pole t={rr}: residue c={cF} ({float(cF):.5g})")
        print(f"   omegas={[str(o) for o in oms]}  matching={pairs}")
        print(f"   pair magnitudes={[str(m) for m in mags]}")
        # candidate ratios
        m = sorted([abs(oms[0]), abs(oms[1]), abs(oms[2])])  # but pairs share magnitude
        # the 3 distinct magnitudes:
        M = sorted(set(abs(o) for o in oms))
        if len(M) == 3:
            m1, m2, m3 = M
            cands = {
                "m1 m2 m3": m1 * m2 * m3,
                "(m1 m2 m3)^2": (m1 * m2 * m3) ** 2,
                "m1^2 m2^2 m3^2 * sum": (m1 * m2 * m3) ** 2,
                "prod * (m1^2+m2^2+m3^2)": m1 * m2 * m3 * (m1**2 + m2**2 + m3**2),
                "prod * e2(sq)": m1 * m2 * m3 * (m1**2 * m2**2 + m1**2 * m3**2 + m2**2 * m3**2),
            }
            for nm, val in cands.items():
                if val != 0:
                    print(f"     c/({nm}) = {cF/val}  ({float(cF/val):.5g})")


if __name__ == "__main__":
    analyze(2, 3, 5, 7, "chamber-1")
    analyze(2, 3, 4, 9, "chamber-2")
