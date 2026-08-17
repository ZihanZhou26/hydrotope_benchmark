#!/usr/bin/env python3
"""Invariant-coordinate machinery for n=6 three-minus.

A_6 is S_3(minus 1,2,3) x S_3(plus 4,5,6) x Z_2(swap) symmetric and lives on the
2-codim resonant manifold (sum w = 0, sum sigma w^2 = 0). On the manifold the
S_3xS_3 invariants reduce to FOUR:
    e1  := e1plus = -e1minus     (sum w = 0)
    e2  := e2plus =  e2minus     (sum sigma w^2 = 0  <=>  e2minus = e2plus)
    e3m := e3minus = w1 w2 w3
    e3p := e3plus  = w4 w5 w6
Z_2 swap acts as (e1,e2,e3m,e3p) -> (-e1, e2, e3p, e3m).
Degrees: e1:1, e2:2, e3m:3, e3p:3.  A_6/(i 2^5 g^-3) is homogeneous degree 8.
Denominator D9 = prod_{i in M, j in P}(w_i + w_j) is a polynomial in the invariants.
"""
from fractions import Fraction as F
import sympy as sp
import chambers_n6 as cn

MINUS = [0, 1, 2]
PLUS = [3, 4, 5]


def invariants(oms):
    """oms = 6 Fractions [w1..w6]. Return (e1,e2,e3m,e3p) as Fractions."""
    m = [oms[i] for i in MINUS]
    p = [oms[j] for j in PLUS]
    e1p = p[0] + p[1] + p[2]
    e2p = p[0]*p[1] + p[0]*p[2] + p[1]*p[2]
    e3p = p[0]*p[1]*p[2]
    e3m = m[0]*m[1]*m[2]
    return (e1p, e2p, e3m, e3p)


def D9_from_oms(oms):
    w = {i+1: oms[i] for i in range(6)}
    d = F(1)
    for i in (1, 2, 3):
        for j in (4, 5, 6):
            d *= (w[i] + w[j])
    return d


# ---- D9 as an explicit polynomial in (e1,e2,e3m,e3p) ----
def D9_symbolic():
    """Return D9 expressed in symbols e1,e2,e3m,e3p (on the manifold)."""
    w1,w2,w3,w4,w5,w6 = sp.symbols('w1 w2 w3 w4 w5 w6')
    D9 = sp.prod([(wi+wj) for wi in (w1,w2,w3) for wj in (w4,w5,w6)])
    # elementary symmetric of each triple
    e1m_,e2m_,e3m_ = w1+w2+w3, w1*w2+w1*w3+w2*w3, w1*w2*w3
    e1p_,e2p_,e3p_ = w4+w5+w6, w4*w5+w4*w6+w5*w6, w4*w5*w6
    E1m,E2m,E3m,E1p,E2p,E3p = sp.symbols('E1m E2m E3m E1p E2p E3p')
    # write D9 in terms of the 6 elementaries via resultant structure:
    # D9 = prod_i (wi^3 + E1p wi^2 + E2p wi + E3p) evaluated over minus roots,
    # which is Res of minus-cubic and (x^3+E1p x^2+E2p x+E3p). Use sympy resultant.
    x = sp.symbols('x')
    pm = x**3 - E1m*x**2 + E2m*x - E3m      # monic cubic with minus roots
    Q  = x**3 + E1p*x**2 + E2p*x + E3p      # prod_j (x + wj)
    R = sp.resultant(pm, Q, x)              # = prod_i Q(wi) = D9  (leading coeffs 1)
    R = sp.expand(R)
    # substitute manifold relations: E1m=-E1p=-e1, E2m=E2p=e2, E3m=e3m, E3p=e3p
    e1,e2,e3m,e3p = sp.symbols('e1 e2 e3m e3p')
    R = R.subs({E1m:-e1, E1p:e1, E2m:e2, E2p:e2, E3m:e3m, E3p:e3p})
    return sp.expand(R), (e1,e2,e3m,e3p)


if __name__ == "__main__":
    import harness as h
    SIG = [-1,-1,-1,1,1,1]
    # (1) verify D9 polynomial-in-invariants matches direct product at random pts
    D9expr, syms = D9_symbolic()
    e1,e2,e3m,e3p = syms
    print("D9 as polynomial in (e1,e2,e3m,e3p):")
    sp.pprint(sp.factor(D9expr))
    print()
    import random
    rnd = random.Random(1)
    ok = True
    for _ in range(8):
        free = [F(rnd.randint(-50,50),10) for _ in range(4)]
        oms = cn.solve_squares(free)
        if oms is None or any(w==0 for w in oms): continue
        inv = invariants(oms)
        d_direct = D9_from_oms(oms)
        d_poly = D9expr.subs({e1:sp.Rational(inv[0].numerator,inv[0].denominator),
                              e2:sp.Rational(inv[1].numerator,inv[1].denominator),
                              e3m:sp.Rational(inv[2].numerator,inv[2].denominator),
                              e3p:sp.Rational(inv[3].numerator,inv[3].denominator)})
        match = sp.Rational(d_direct.numerator,d_direct.denominator) == d_poly
        ok = ok and match
        print(f"  D9 direct={d_direct}  poly-match={match}")
    print("D9 invariant-polynomial OK:", ok)

    # (2) verify A_6 depends only on invariants: two DIFFERENT free points with the
    # SAME (e1,e2,e3m,e3p) must give the same A_6.  Build one by permuting legs.
    free = [F(2),F(3),F(5),F(7)]
    oms = cn.solve_squares(free); inv = invariants(oms)
    im,_,_ = h.on_shell(free, SIG)
    print(f"\nA_6 at free {free}: {im};  invariants {inv}")
