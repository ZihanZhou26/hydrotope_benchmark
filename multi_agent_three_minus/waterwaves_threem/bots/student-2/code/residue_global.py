#!/usr/bin/env python3
"""Test whether the residue of A_6 at its SIMPLE pole {e3m+e3p=0} is a GLOBAL
(chamber-independent) symmetric polynomial.

A_6/i = N_6 / (e3m+e3p),  N_6 a per-chamber polynomial (spline).
On an F-const slice, N_6(t) is an exact polynomial; (e3m+e3p)(t) is an explicit
polynomial whose real roots r_k are the matching/pole points (outside the chamber,
reached by analytic continuation of the chamber form).

residue value  rho(point) := N_6(r_k)  [the numerator at the locus point].
If rho is the SAME symmetric function evaluated at omega(r_k) regardless of which
chamber/slice we continue from, then A_6 = i 2^5 [ rho/(e3m+e3p) + W ] with rho a
GLOBAL polynomial and W a (lower-degree) polynomial spline.

We collect (invariants, rho) over several slices and fit rho as a symmetric
polynomial in (e1, e2, e3m) on the locus e3p=-e3m.
"""
import sympy as sp
from fractions import Fraction as F
import harness as h

SIG = [-1, -1, -1, 1, 1, 1]
t = sp.Symbol('t')


def slice_legs(w2, w3, a, b):
    """F-const slice; return W dict (1..6) as sympy polys in t, and (e3m+e3p)(t)."""
    w2, w3, a, b = map(sp.Rational, (w2, w3, a, b))
    w4 = a + t; w5 = b - t
    sF = w2 + w3 + w4 + w5
    sumSig = -w2**2 - w3**2 + w4**2 + w5**2
    w6 = sp.expand(-(-sF**2 + sumSig) / (-2 * sF))   # s1=-1
    w1 = sp.expand(-(sF + w6))
    W = {1: w1, 2: w2, 3: w3, 4: w4, 5: w5, 6: w6}
    e3m = sp.expand(w1 * w2 * w3)
    e3p = sp.expand(w4 * w5 * w6)
    return W, sp.expand(e3m + e3p)


def tag(wv):
    """chamber sign tag from numeric omega dict."""
    tg = []
    for i in (1, 2, 3):
        for j in (4, 5, 6):
            tg.append(1 if wv[j]**2 - wv[i]**2 > 0 else -1)
    for j in (4, 5, 6):
        mm = (1, 2, 3)
        for x in range(3):
            for y in range(x + 1, 3):
                tg.append(1 if wv[j]**2 - wv[mm[x]]**2 - wv[mm[y]]**2 > 0 else -1)
    for i in (1, 2, 3):
        pp = (4, 5, 6)
        for x in range(3):
            for y in range(x + 1, 3):
                tg.append(1 if wv[i]**2 - wv[pp[x]]**2 - wv[pp[y]]**2 > 0 else -1)
    return tuple(tg)


def fit_N6_slice(w2, w3, a, b, t0=F(0), step=F(1, 30), maxn=40):
    """Sample N_6(t) at in-chamber points around t0; fit exact polynomial.
    Returns (N6poly(t), e3sum(t), chamber-tag)."""
    W, e3sum = slice_legs(w2, w3, a, b)
    pts = []
    base_tag = None
    for k in list(range(0, maxn)) + [-x for x in range(1, maxn)]:
        tv = t0 + step * k
        free = [F(w2), F(w3), F(a) + tv, F(b) - tv]
        if sum(free) == 0:
            continue
        try:
            im, oms, re_p = h.on_shell(free, SIG)
        except Exception:
            continue
        if re_p != 0:
            continue
        wv = {i + 1: F(oms[i]) for i in range(6)}
        tg = tag(wv)
        if base_tag is None:
            base_tag = tg
        if tg != base_tag:
            continue
        e3v = e3sum.subs(t, sp.Rational(tv.numerator, tv.denominator))
        N6v = F(im) * F(int(e3v.p), int(e3v.q)) if e3v.is_Rational else None
        pts.append((sp.Rational(tv.numerator, tv.denominator), sp.Rational(N6v.numerator, N6v.denominator)))
        if len(pts) >= 30:
            break
    # fit minimal-degree polynomial: increase #points until top coeff stabilizes to a poly
    # use all pts; interpolation through m points = degree m-1; check it's actually lower
    poly = sp.interpolate(pts, t)
    poly = sp.expand(poly)
    return poly, e3sum, base_tag, len(pts)


def invariants_at(W, tv):
    wv = {i: W[i].subs(t, tv) if hasattr(W[i], 'subs') else W[i] for i in W}
    e1 = wv[4] + wv[5] + wv[6]              # e1 plus
    e2 = wv[4]*wv[5] + wv[4]*wv[6] + wv[5]*wv[6]
    e3m = wv[1]*wv[2]*wv[3]
    e3p = wv[4]*wv[5]*wv[6]
    return sp.Rational(e1), sp.Rational(e2), sp.Rational(e3m), sp.Rational(e3p)


def collect(slices):
    data = []   # (e1,e2,e3m,e3p, rho)
    for (w2, w3, a, b) in slices:
        try:
            N6, e3sum, tg, npts = fit_N6_slice(w2, w3, a, b)
        except Exception as ex:
            print(f"  slice {(w2,w3,a,b)}: fit fail {ex}"); continue
        W, _ = slice_legs(w2, w3, a, b)
        roots = sp.roots(sp.Poly(e3sum, t))
        deg = sp.degree(N6, t)
        print(f"  slice {(w2,w3,a,b)}: npts={npts}, deg N6(t)={deg}, "
              f"#real roots of (e3m+e3p)={sum(1 for r in roots if r.is_real)}")
        for r, mult in roots.items():
            if not r.is_real:
                continue
            rho = N6.subs(t, r)
            e1, e2, e3m, e3p = invariants_at(W, r)
            data.append((e1, e2, e3m, e3p, sp.Rational(rho)))
    return data


if __name__ == "__main__":
    slices = [(2, 3, 5, 7), (2, 3, 4, 9), (1, 4, 5, 8), (3, 5, 6, 10),
              (2, 5, 4, 11), (1, 6, 7, 9)]
    data = collect(slices)
    print(f"\nCollected {len(data)} locus points. Sample (e1,e2,e3m,e3p,rho):")
    for d in data[:12]:
        print("  ", [str(x) for x in d])
