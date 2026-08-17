#!/usr/bin/env python3
"""Fast 1-D symbolic slice on a chamber via a POLYNOMIAL parametrization.

Vary w2 = a+x, w3 = b-x (sum fixed) and keep w4=c, w5=d fixed rationals. Then
SF = w2+w3+w4+w5 is CONSTANT in x, so the on-shell solves
  w6 = (SF^2 - SS)/(2 SF),  w1 = -SF - w6,   SS = -w2^2-w3^2+w4^2+w5^2
are POLYNOMIALS in x (no denominators). The engine then returns C(x) as a
rational function whose denominators (propagators D_S) cancel on-shell -> a
polynomial. We cancel and print it.
"""
import sympy as sp
import symbolic_bg as S

x = sp.Symbol("x", real=True)


def build_W(a, b, c, d):
    w2 = sp.Integer(a) + x
    w3 = sp.Integer(b) - x
    w4 = sp.Integer(c)
    w5 = sp.Integer(d)
    SF = w2 + w3 + w4 + w5
    SS = -w2**2 - w3**2 + w4**2 + w5**2
    w6 = (SF**2 - SS) / (2 * SF)
    w1 = -SF - w6
    return {1: sp.expand(w1), 2: w2, 3: w3, 4: w4, 5: w5, 6: sp.expand(w6)}


def core_on_chamber(a, b, c, d, xref):
    signs = [-1, -1, -1, 1, 1, 1]
    W = build_W(a, b, c, d)
    K = {i: sp.Integer(signs[i-1]) * W[i]**2 for i in W}
    eng = S.SymEngine(K, W, {x: sp.Rational(xref)})
    re, im = eng.BGAmplitude()
    C = sp.cancel(im / sp.Integer(32))   # A/(i 2^5), g=1
    return sp.expand(C), W


if __name__ == "__main__":
    # chamber reference x=0 -> w2=a, w3=b
    a, b, c, d, xref = 2, 3, 5, 7, 0
    C, W = core_on_chamber(a, b, c, d, xref)
    print("W(x):", {i: W[i] for i in W})
    print("\nC(x) =", C)
    print("\ndegree in x:", sp.degree(sp.Poly(C, x)))
    # numeric check vs oracle at x=0 (point a,b,c,d = 2,3,5,7) -> known A6 = -29948208/17
    import harness as h
    val0 = C.subs(x, 0)
    im0, _, _ = h.on_shell([2, 3, 5, 7], [-1,-1,-1,1,1,1])
    print("\nC(0)*32 =", val0*32, " oracle A6 =", im0, " match:", sp.Rational(im0.numerator, im0.denominator) == val0*32)
