#!/usr/bin/env python3
"""On an F-constant slice, A_6/i = sextic(t) / prod_k (t - r_k), where each r_k is
a perfect-matching locus omega_i = -omega_sigma(i). Extract the residue c_k at
each pole and try to recognize it in terms of the frequencies at t=r_k (which are
3 opposite pairs). Look for: product of freqs, two-minus blocks, simple symmetric
functions.
"""
import sympy as sp
from fractions import Fraction as F
import harness as h, r4lib

SIG = [-1, -1, -1, 1, 1, 1]
t = sp.Symbol('t')


def slice_rational(w2, w3, a, b, npts=40, step=F(1, 50)):
    ts = [step * (k + 1) for k in range(npts)]
    good_t, A_vals = [], []
    for tv in ts:
        free = [F(w2), F(w3), F(a) + tv, F(b) - tv]
        try:
            im, oms, _ = h.on_shell(free, SIG)
            good_t.append(tv); A_vals.append(F(im))
        except Exception:
            pass
    pts = [(sp.Rational(tv.numerator, tv.denominator), sp.Rational(v.numerator, v.denominator))
           for tv, v in zip(good_t, A_vals)]
    # interpolate as polynomial won't work (rational). Reconstruct rational via cancel of
    # A*D9 (poly) over D9 (poly). Build both then cancel.
    D_vals = []
    for tv in good_t:
        free = [F(w2), F(w3), F(a) + tv, F(b) - tv]
        im, oms, _ = h.on_shell(free, SIG)
        D_vals.append(r4lib.Dn(oms))
    Npts = [(sp.Rational(tv.numerator, tv.denominator),
             sp.Rational((v * d).numerator, (v * d).denominator))
            for tv, v, d in zip(good_t, A_vals, D_vals)]
    Dpts = [(sp.Rational(tv.numerator, tv.denominator),
             sp.Rational(d.numerator, d.denominator)) for tv, d in zip(good_t, D_vals)]
    Npoly = sp.expand(sp.interpolate(Npts, t))
    Dpoly = sp.expand(sp.interpolate(Dpts, t))
    return sp.cancel(Npoly / Dpoly)   # = A_6/i on slice


def omegas_at(w2, w3, a, b, tv):
    free = [F(w2), F(w3), F(a) + tv, F(b) - tv]
    _, oms, _ = h.on_shell(free, SIG)
    return [F(o) for o in oms]


def analyze(w2, w3, a, b, label):
    A = slice_rational(w2, w3, a, b)
    num, den = sp.fraction(A)
    print(f"\n=== {label}: w2={w2},w3={w3}, w4={a}+t, w5={b}-t ===")
    print("A_6/i =", sp.factor(A))
    roots = sp.roots(sp.Poly(den, t))
    print("poles (t):", roots)
    for r in roots:
        rr = sp.nsimplify(r)
        c = sp.limit((t - rr) * A, t, rr)   # residue
        # frequencies at the pole (analytic continuation, may be off-chamber)
        try:
            oms = omegas_at(w2, w3, a, b, F(int(rr.p), int(rr.q)) if rr.is_Rational else None)
        except Exception:
            oms = None
        print(f"  pole t={rr}: residue c={c}  (={float(c):.4g})")
        if oms:
            print(f"     omegas at pole = {[str(o) for o in oms]}")
            # check which matching: omega_i = -omega_j pairs
            pairs = []
            for i in (0, 1, 2):
                for j in (3, 4, 5):
                    if oms[i] + oms[j] == 0:
                        pairs.append((i + 1, j + 1))
            print(f"     vanishing mixed pairs (omega_i+omega_j=0): {pairs}")
            prod_all = 1
            for o in oms:
                prod_all *= o
            print(f"     prod(all omega)={prod_all}, prod_minus={oms[0]*oms[1]*oms[2]}, "
                  f"prod_plus={oms[3]*oms[4]*oms[5]}")


if __name__ == "__main__":
    analyze(2, 3, 5, 7, "chamber-1")
    analyze(2, 3, 4, 9, "chamber-2")
