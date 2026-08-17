#!/usr/bin/env python3
"""Decisive test: is the pole residue rho = N_6|_{matching point} a single GLOBAL
polynomial in the invariants (e1,e2,e3m) on the locus e3p=-e3m, or chamber-dependent?

Collect many (e1,e2,e3m,rho) locus points from clean single-chamber slices, fit a
degree-11 polynomial in (e1,e2,e3m), hold out points, report residual. Consistent
fit + zero held-out residual => global polynomial residue. Failure => chamber-spline.
"""
import sympy as sp
from fractions import Fraction as F
from itertools import product
import harness as h
import residue_global as rg

e1, e2, e3 = sp.symbols('e1 e2 e3')


def monomials(maxdeg=11):
    """all e1^a e2^b e3^c with weighted deg a+2b+3c <= maxdeg (weights 1,2,3)."""
    monos = []
    for a in range(maxdeg + 1):
        for b in range((maxdeg - a) // 2 + 1):
            for c in range((maxdeg - a - 2 * b) // 3 + 1):
                if a + 2 * b + 3 * c <= maxdeg:
                    monos.append((a, b, c))
    return monos


def collect_many():
    slices = []
    vals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 13]
    # build assorted F-const slices (w2,w3 minus; w4=a, w5=b centers)
    combos = [(2,3,5,7),(2,3,4,9),(1,4,5,8),(3,5,6,10),(1,6,7,9),(2,5,4,11),
              (3,4,6,8),(1,2,7,10),(4,5,3,12),(2,7,5,9),(3,2,8,6),(1,3,9,7),
              (5,6,2,11),(2,4,7,8),(3,7,4,10),(1,5,8,9)]
    return rg.collect(combos)


def main():
    data = collect_many()
    # dedup by invariants
    seen = {}
    for (E1, E2, E3m, E3p, rho) in data:
        key = (E1, E2, E3m)
        if key in seen and seen[key] != rho:
            print(f"  *** INVARIANT COLLISION with DIFFERENT rho: {key} -> {seen[key]} vs {rho}")
        seen[key] = rho
    pts = [(k[0], k[1], k[2], v) for k, v in seen.items()]
    print(f"\n{len(pts)} distinct invariant points.")
    monos = monomials(11)
    print(f"{len(monos)} monomials (weighted deg <=11).")
    if len(pts) < len(monos) + 5:
        print("  not enough points for a held-out fit; collecting more would be needed.")
    # build linear system A c = b over Q
    import sympy
    rows = []
    bs = []
    for (E1, E2, E3m, v) in pts:
        row = [sp.Rational(E1)**a * sp.Rational(E2)**b * sp.Rational(E3m)**c for (a, b, c) in monos]
        rows.append(row); bs.append(sp.Rational(v))
    Amat = sp.Matrix(rows)
    bvec = sp.Matrix(bs)
    ntrain = min(len(pts) - 3, len(monos))
    Atr = Amat[:ntrain, :]
    btr = bvec[:ntrain, :]
    # least squares / solve
    try:
        sol, params = Atr.gauss_jordan_solve(btr)
        nfree = len(params)
        print(f"solved with {nfree} free params (rank-deficient if >0).")
        # validate on held-out
        coeffs = sol.subs({p: 0 for p in params}) if nfree else sol
        ok = bad = 0
        for i in range(ntrain, len(pts)):
            pred = sum(coeffs[j] * Amat[i, j] for j in range(len(monos)))
            if sp.simplify(pred - bvec[i]) == 0:
                ok += 1
            else:
                bad += 1
                if bad <= 3:
                    print(f"   held-out FAIL: pred={pred} actual={bvec[i]}")
        print(f"held-out: {ok} ok, {bad} fail  (of {len(pts)-ntrain})")
        if bad == 0 and ok > 0:
            print("=> residue IS a global polynomial in invariants. Nonzero monomials:")
            for (mono, cf) in zip(monos, coeffs):
                if cf != 0:
                    print(f"     e1^{mono[0]} e2^{mono[1]} e3m^{mono[2]} : {cf}")
    except Exception as ex:
        print("solve failed / inconsistent:", ex)
        print("=> residue is NOT a global polynomial in invariants (chamber-dependent).")


if __name__ == "__main__":
    main()
