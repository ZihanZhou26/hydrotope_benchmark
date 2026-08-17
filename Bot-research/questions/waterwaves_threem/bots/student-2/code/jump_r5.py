#!/usr/bin/env python3
"""Extract the SPLINE JUMP-COEFFICIENT polynomials of N_6 across SINGLE mixed walls.

N_6 = A_6*(e3m+e3p)/(i 2^5).  On a clean F-constant single-chamber slice N_6(t) is a
degree-6 polynomial. Across a (1=2) wall (k_S = +-(w_i^2 - w_j^2 - w_k^2) = 0) it
jumps by (k_S)^3 * Q; across a (1=1) wall (k_ij = w_j^2 - w_i^2 = 0) by (k_ij)^1 * P.

We build a slice crossing ONE wall at t=t*, verify single-wall by the chamber sign
pattern being constant on each side, fit N_6(t) deg<=6 each side, subtract, and read
the jump = (t-t*)^p * (poly). Map the coefficient as a function of the wall point.
"""
import sympy as sp
from fractions import Fraction as F
import harness as h, r4lib

SIG = [-1, -1, -1, 1, 1, 1]
M = (1, 2, 3)
P = (4, 5, 6)
t = sp.Symbol('t')


def wall_signs(w):
    """sign pattern of all (1=1) mixed pairs and (1=2) triples on the manifold."""
    tag = []
    for i in M:
        for j in P:
            tag.append(1 if w[j]**2 - w[i]**2 > 0 else -1)
    # (1=2): one plus singleton = two minus  (k = wplus^2 - wm1^2 - wm2^2)
    for j in P:
        for a in range(len(M)):
            for b in range(a + 1, len(M)):
                tag.append(1 if w[j]**2 - w[M[a]]**2 - w[M[b]]**2 > 0 else -1)
    # (1=2): one minus singleton = two plus
    for i in M:
        for a in range(len(P)):
            for b in range(a + 1, len(P)):
                tag.append(1 if w[i]**2 - w[P[a]]**2 - w[P[b]]**2 > 0 else -1)
    return tuple(tag)


def N6_and_w(free):
    N, oms, im = r4lib.Nn_value([F(x) for x in free], SIG)
    w = {i + 1: F(oms[i]) for i in range(6)}
    return N, w


def fit_poly(ts, vs):
    pts = [(sp.Rational(a.numerator, a.denominator), sp.Rational(b.numerator, b.denominator))
           for a, b in zip(ts, vs)]
    return sp.expand(sp.interpolate(pts, t))


def crossing(w2, w3, a, b, t_star, npts=14, gap=F(1, 2000), step=F(1, 2000)):
    """F-const slice w4=a+t, w5=b-t; minus legs w2,w3. Sample each side of t_star;
    require a CONSTANT chamber tag on each side (single wall). Returns (Nl,Nr,wall_w)."""
    def sample(side):
        ts, vs, tags = [], [], set()
        k = 0
        while len(ts) < npts and k < npts * 10:
            k += 1
            tv = t_star + side * (gap + step * k)
            free = [F(w2), F(w3), F(a) + tv, F(b) - tv]
            try:
                N, w = N6_and_w(free)
            except Exception:
                continue
            ts.append(tv); vs.append(N); tags.add(wall_signs(w))
        return ts, vs, tags
    tl, vl, tagl = sample(F(-1))
    tr, vr, tagr = sample(F(1))
    return tl, vl, tagl, tr, vr, tagr


def analyze(w2, w3, a, b, t_star, label):
    tl, vl, tagl, tr, vr, tagr = crossing(w2, w3, a, b, F(t_star))
    if len(tl) < 7 or len(tr) < 7:
        print(f"  {label}: insufficient points"); return None
    if len(tagl) != 1 or len(tagr) != 1:
        print(f"  {label}: NOT single-chamber (left tags={len(tagl)}, right tags={len(tagr)})"); return None
    # how many sign entries flip across the wall?
    dl, dr = next(iter(tagl)), next(iter(tagr))
    flips = sum(1 for x, y in zip(dl, dr) if x != y)
    Nl = fit_poly(tl, vl)
    Nr = fit_poly(tr, vr)
    jump = sp.expand(Nr - Nl)
    ts = sp.Rational(F(t_star).numerator, F(t_star).denominator)
    # multiplicity of (t-ts) in jump
    order = 0
    j = jump
    while order < 8 and sp.simplify(j.subs(t, ts)) == 0 and j != 0:
        j = sp.cancel(j / (t - ts)); order += 1
    free_star = [F(w2), F(w3), F(a) + F(t_star), F(b) - F(t_star)]
    cont = sp.simplify(Nl.subs(t, ts) - Nr.subs(t, ts))
    print(f"  {label}: single-wall, {flips} sign flip(s); jump order = {order}; "
          f"deg Nl={sp.degree(Nl,t)} deg Nr={sp.degree(Nr,t)}; N_L(t*)-N_R(t*)={cont}")
    if order >= 1:
        print("     jump/(t-t*)^order factored:", sp.factor(j))
    return jump, order, free_star, j if order >= 1 else None


if __name__ == "__main__":
    print("=== (1=2) wall  w4^2 = w2^2 + w3^2 (Pythagorean 3,4,5) ===")
    # w2=3,w3=4 minus; w4=5+t crosses wall at t=0; vary w5 center b
    for b in [15, 16, 20]:
        analyze(3, 4, 5, b, 0, f"w2=3,w3=4,w5c={b}")

    print("\n=== (1=1) wall  w4 = w2 (mixed pair) ===")
    # w2=3 minus, w4=3 at t=0 -> w4=3+t; need w3,w5 generic & far from other walls
    for (w3, b) in [(F(13,2), 17), (5, 19)]:
        analyze(3, w3, 3, b, 0, f"w3={w3},w5c={b}")
