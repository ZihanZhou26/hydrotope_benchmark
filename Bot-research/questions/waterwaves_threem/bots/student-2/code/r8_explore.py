#!/usr/bin/env python3
"""Round-8 exploration (student-2): soft recursion grounding + reference-chamber
rational structure of C_n = A_n/(i 2^{n-1}) at g=1.
"""
import sympy as sp
from fractions import Fraction as F
import itertools
import fastbg
import r8lib as L

t = sp.Symbol('t')
def Q(x): return sp.Rational(F(x).numerator, F(x).denominator)

# ---------- soft recursion grounding at n=7 ----------
def soft_check():
    print("="*70)
    print("SOFT RECURSION at n=7 (own fastbg, F-const slice, exact eps->0)")
    print("="*70)
    n = 7
    # Plus-leg soft: make free plus leg (index 2 in free = w4) = eps, compensate
    # another plus leg (index 3 = w5) so sum(free) stays constant -> all polynomial.
    # free = [w2,w3,w4,w5,w6]; minus legs free idx 0,1; plus free idx 2,3,4.
    # set w4 = eps, w5 = c - eps (c chosen so base config sensible).
    base = [F(2), F(3), F(5), F(7), F(11)]   # w2,w3,w4,w5,w6
    c = base[2] + base[3]                     # keep w4+w5 = c
    # C_7(eps)/eps^2 -> ?   Build N(eps)=A_7 * (denominator-ish) polynomial? Simpler:
    # exact slice: A_7/i as rational fn of eps, take coefficient.
    pts = []
    for k in range(1, 12):
        eps = F(1, 6) * k
        fr = [base[0], base[1], eps, c - eps, base[4]]
        if sum(fr) == 0: continue
        try:
            im, oms = fastbg.A_over_i([F(x) for x in fr], L.threem_signs(n))
        except Exception:
            continue
        pts.append((eps, im))
    xs = [Q(e) for (e, _) in pts]; ys = [Q(im) for (_, im) in pts]
    expr = sp.interpolate(list(zip(xs, ys)), t)
    ser = sp.series(sp.together(expr), t, 0, 4).removeO()
    print("A_7/i  series in eps (plus-leg soft):")
    print("  ", sp.nsimplify(ser))
    coeff2 = sp.expand(expr).coeff(t, 2) if expr.is_polynomial(t) else None
    # since A_7 ~ 8 eps^2 A_6^{3-}: surviving config legs {2,3,(w4=0),5,6} -> 3m at n=6
    # surviving 6-leg three-minus: minus {1,2,3}, plus {5,6,7} with w4 removed.
    # build surviving free for n=6: free=[w2,w3,w5,w6]=[2,3,c,11]? w5->c since eps->0
    surv = [base[0], base[1], c, base[4]]
    im6, oms6 = fastbg.A_over_i([F(x) for x in surv], L.threem_signs(6))
    print(f"  [t^2] coeff of A_7/i      = {sp.nsimplify(sp.expand(expr).coeff(t,2))}")
    print(f"  8 * A_6^3m/i (surviving)  = {8*im6}")

# ---------- C_n rational structure on a line in a fixed chamber ----------
def line_struct(n, base_free, idx, lo, hi, npts=40):
    """Reconstruct C_n along free[idx] in [lo,hi]; return exact rational fn of t,
    staying in one chamber (stop at sign change of any wall)."""
    pts = []
    sig0 = None
    SIG = L.threem_signs(n)
    for k in range(npts):
        tv = lo + (hi - lo) * F(k, npts - 1)
        fr = list(base_free); fr[idx] = tv
        if sum(fr) == 0: continue
        try:
            im, oms = fastbg.A_over_i([F(x) for x in fr], SIG)
        except Exception:
            continue
        sig = chamber_sig(oms)
        if sig is None: continue
        if sig0 is None: sig0 = sig
        if sig != sig0: continue   # skip pts in other chambers
        C = F(im, 2**(n-1))
        pts.append((tv, C, oms))
    if len(pts) < 10: return None
    xs = [Q(p[0]) for p in pts]; ys = [Q(p[1]) for p in pts]
    # rational reconstruction via sympy interpolate of C? C is rational in t.
    # Use Pade: fit numerator/denominator. Easier: fit C(t)*Dn(t) = poly, get poly,
    # and Dn(t) separately, present C = poly / Dn.
    Dexpr = sp.interpolate(list(zip(xs, [Q(L.Dn(p[2])) for p in pts])), t)
    NumExpr = sp.interpolate(list(zip(xs, [Q(p[1] * L.Dn(p[2])) for p in pts])), t)
    return sp.factor(NumExpr), sp.factor(Dexpr), pts[0][2]

def chamber_sig(oms):
    n = len(oms)
    M = list(range(3)); P = list(range(3, n))
    sq = [w*w for w in oms]
    sgn = []
    for i in M:
        for r in range(1, len(P)+1):
            for T in itertools.combinations(P, r):
                v = sum(sq[j] for j in T) - sq[i]
                if v == 0: return None
                sgn.append(1 if v > 0 else -1)
    return tuple(sgn)

if __name__ == "__main__":
    soft_check()
    print()
    print("="*70)
    print("C_6 rational structure on a line (chamber-fixed)")
    print("="*70)
    res = line_struct(6, [F(2), F(3), F(5), F(7)], 3, F(6), F(12))
    if res:
        Num, Den, om0 = res
        print("first om:", [str(x) for x in om0])
        print("Numerator (factored):", Num)
        print("Denominator (factored):", Den)
