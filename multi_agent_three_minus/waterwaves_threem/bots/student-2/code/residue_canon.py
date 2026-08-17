#!/usr/bin/env python3
"""Canonical pole-residue numerator rho = N_6(matching point), tabulated by the three
matched magnitudes {p,q,r} (each matched pair has w_minus=-w_plus=+-value) and the
matching sign. Goal: recognize rho as +- R(p,q,r), R a symmetric polynomial.

N_6 = A_6/i * (e3m+e3p). On an F-const slice both are functions of t; A_6/i is
reconstructed (rational), (e3m+e3p)(t) is exact; rho = N_6(matching root r) =
Res_t(A_6/i) * (e3m+e3p)'(r)  (canonical: independent of the slice parametrization
up to the well-defined polynomial N_6).
"""
from fractions import Fraction as F
import sympy as sp
import harness as h
from residue_fact import reconstruct, slice_data
from residue_global import slice_legs

SIG = [-1, -1, -1, 1, 1, 1]
MINUS = (1, 2, 3); PLUS = (4, 5, 6)
t = sp.Symbol('t')


def matching_of(w):
    m = {}; used = set()
    for i in MINUS:
        for j in PLUS:
            if j not in used and w[i] + w[j] == 0:
                m[i] = j; used.add(j); break
    return m if len(m) == 3 else None


def perm_sign(m):
    """sign of the matching as a permutation MINUS->PLUS (relative to identity 1->4,2->5,3->6)."""
    target = {1: 4, 2: 5, 3: 6}
    # express as permutation of {0,1,2}
    perm = [m[i] - 4 for i in MINUS]  # values in 0..2
    # count inversions
    inv = sum(1 for a in range(3) for b in range(a + 1, 3) if perm[a] > perm[b])
    return -1 if inv % 2 else 1


def analyze(w2, w3, a, b):
    pts = slice_data(w2, w3, a, b)
    if len(pts) < 14:
        return []
    rec = reconstruct(pts)
    if rec is None:
        return []
    dN, dD, Nc, Dc = rec
    Npoly = sum(sp.Rational(c.numerator, c.denominator) * t ** j for j, c in enumerate(Nc))
    Dpoly = sum(sp.Rational(c.numerator, c.denominator) * t ** k for k, c in enumerate(Dc))
    Dprime = sp.diff(Dpoly, t)
    _, e3sum = slice_legs(w2, w3, a, b)
    e3prime = sp.diff(e3sum, t)
    out = []
    for r, mult in sp.roots(Dpoly).items():
        if not r.is_rational:
            continue
        rr = F(int(sp.fraction(r)[0]), int(sp.fraction(r)[1]))
        from harness import solve_legs_1n
        omv = solve_legs_1n([F(w2), F(w3), F(a) + rr, F(b) - rr], SIG)
        w = {i + 1: F(omv[i]) for i in range(6)}
        match = matching_of(w)
        if match is None:
            continue
        res_t = Npoly.subs(t, r) / Dprime.subs(t, r)
        rho = sp.Rational(res_t * e3prime.subs(t, r))
        rho = F(int(sp.fraction(rho)[0]), int(sp.fraction(rho)[1]))
        mags = tuple(sorted(abs(w[i]) for i in MINUS))
        sgn = perm_sign(match)
        out.append((mags, sgn, rho, w))
    return out


if __name__ == "__main__":
    slices = [(2, 3, 5, 7), (2, 3, 4, 9), (1, 4, 5, 8), (3, 5, 6, 10), (1, 6, 7, 9),
              (2, 5, 6, 11), (3, 4, 7, 8), (1, 2, 8, 9), (4, 5, 2, 12), (2, 7, 3, 10),
              (1, 3, 6, 11), (5, 6, 3, 13), (2, 4, 5, 14), (1, 5, 7, 12)]
    table = {}
    for sl in slices:
        try:
            for (mags, sgn, rho, w) in analyze(*sl):
                key = mags
                table.setdefault(key, [])
                table[key].append((sgn, rho))
        except Exception as ex:
            pass
    print(f"{'magnitudes {p,q,r}':22} {'sign':>5} {'rho = N_6(matching pt)':>26}  rho/sign")
    clean = {}
    for mags in sorted(table, key=lambda m: (float(m[0]), float(m[1]), float(m[2]))):
        for (sgn, rho) in table[mags]:
            rs = rho * sgn
            print(f"{str(tuple(str(x) for x in mags)):34} {sgn:>5} {str(rho):>26}  {rs}")
            clean.setdefault(mags, set()).add(rs)
    print("\n=== rho/sign per magnitude-set (should be single-valued = R(p,q,r)) ===")
    for mags in sorted(clean, key=lambda m: (float(m[0]), float(m[1]), float(m[2]))):
        vals = clean[mags]
        ok = "OK" if len(vals) == 1 else "MULTI!"
        print(f"  {tuple(str(x) for x in mags)}: {[str(v) for v in vals]}  {ok}")
