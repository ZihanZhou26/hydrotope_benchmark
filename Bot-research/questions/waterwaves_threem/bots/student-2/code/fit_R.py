#!/usr/bin/env python3
"""Fit the canonical pole-residue R(p,q,r) = +-rho as a SYMMETRIC homogeneous
degree-11 polynomial in the matched magnitudes (p,q,r). Reads (mags -> R) data
produced by residue_canon (pasted in DATA below or recomputed)."""
import sympy as sp
from fractions import Fraction as F
from itertools import combinations_with_replacement

p, q, r = sp.symbols('p q r', positive=True)


def sym_monomials(deg=11):
    """monomial symmetric polynomials m_lambda for partitions lambda of deg into <=3 parts."""
    monos = []
    parts = []
    for a in range(deg, -1, -1):
        for b in range(min(a, deg - a), -1, -1):
            c = deg - a - b
            if c <= b:
                parts.append((a, b, c))
    for (a, b, c) in parts:
        # symmetrize p^a q^b r^c
        seen = set()
        terms = []
        for perm in set([(a, b, c), (a, c, b), (b, a, c), (b, c, a), (c, a, b), (c, b, a)]):
            terms.append(p**perm[0] * q**perm[1] * r**perm[2])
        monos.append((a, b, c), )
        monos[-1] = ((a, b, c), sum(terms))
    return monos


def main(data):
    monos = sym_monomials(11)
    print(f"{len(monos)} symmetric monomials of degree 11")
    # build linear system
    rows, rhs = [], []
    keys = list(data.keys())
    for mags in keys:
        P, Qv, Rv = (sp.Integer(int(x)) if float(x) == int(x) else sp.Rational(F(x).numerator, F(x).denominator) for x in mags)
        row = [m.subs({p: P, q: Qv, r: Rv}) for (_, m) in monos]
        rows.append(row); rhs.append(sp.Rational(data[mags].numerator, data[mags].denominator))
    A = sp.Matrix(rows); b = sp.Matrix(rhs)
    print(f"{len(keys)} data points, {len(monos)} unknowns")
    ntrain = min(len(keys), len(monos))
    try:
        sol, params = A[:ntrain, :].gauss_jordan_solve(b[:ntrain, :])
        coeffs = sol.subs({pp: 0 for pp in params}) if len(params) else sol
        # validate
        ok = bad = 0
        for i in range(len(keys)):
            pred = sum(coeffs[j] * A[i, j] for j in range(len(monos)))
            if sp.simplify(pred - b[i]) == 0:
                ok += 1
            else:
                bad += 1
        print(f"fit: {ok} ok / {bad} bad of {len(keys)}; free params={len(params)}")
        if bad == 0:
            print("R(p,q,r) =")
            expr = sum(coeffs[j] * monos[j][1] for j in range(len(monos)))
            sp.pprint(sp.factor(expr))
    except Exception as ex:
        print("fit failed:", ex)


if __name__ == "__main__":
    print("import residue_canon table and call main(); placeholder.")
