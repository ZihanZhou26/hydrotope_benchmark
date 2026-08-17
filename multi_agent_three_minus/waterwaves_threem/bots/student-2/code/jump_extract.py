#!/usr/bin/env python3
"""Extract the (1=2) jump COEFFICIENT of the spline N_6 across a clean single wall.

Across w4^2 = w2^2 + w3^2 (plus leg 4, minus legs 2,3; k_S = w4^2-w2^2-w3^2):
   N_6^{>} - N_6^{<}  =  (k_S)^3 * Q   near the wall.
Method: F-const slice w4=a+t, w5=b-t crossing the wall at t=t*. Reconstruct A_6/i(t)
rationally on each side (contiguous in-chamber). N_6 = (A_6/i)*(e3m+e3p)(t). Jump =
diff, factored; coefficient Q at the wall = jump/(k_S)^3 |_wall. Repeat over several
(w3,b) to see Q's dependence and try to recognize it.
"""
from fractions import Fraction as F
import sympy as sp
from residue_fact import reconstruct
from residue_global import slice_legs
import harness as h

SIG = [-1, -1, -1, 1, 1, 1]
MINUS, PLUS = (1, 2, 3), (4, 5, 6)
t = sp.Symbol('t')


def sig11(oms):
    w = {i + 1: oms[i] for i in range(6)}
    tg = []
    for i in MINUS:
        for j in PLUS:
            tg.append(1 if w[j] ** 2 - w[i] ** 2 > 0 else -1)
    for j in PLUS:
        for x in range(3):
            for y in range(x + 1, 3):
                tg.append(1 if w[j] ** 2 - w[MINUS[x]] ** 2 - w[MINUS[y]] ** 2 > 0 else -1)
    for i in MINUS:
        for x in range(3):
            for y in range(x + 1, 3):
                tg.append(1 if w[i] ** 2 - w[PLUS[x]] ** 2 - w[PLUS[y]] ** 2 > 0 else -1)
    return tuple(tg)


def side_recon(w2, w3, a, b, direction, t_star, step=F(1, 200), maxk=80, gap=F(1, 400)):
    pts = []
    s0 = None
    for k in range(1, maxk):
        tv = t_star + direction * (gap + step * k)
        free = [F(w2), F(w3), F(a) + tv, F(b) - tv]
        if sum(free) == 0:
            continue
        try:
            im, oms, re_p = h.on_shell(free, SIG)
        except Exception:
            break
        oms = [F(o) for o in oms]
        s = sig11(oms)
        if s0 is None:
            s0 = s
        if s != s0:
            break
        pts.append((tv - t_star, F(im)))   # recon around the wall (shift so wall at 0)
    if len(pts) < 12:
        return None
    rec = reconstruct(pts, cap=20)
    if rec is None:
        return None
    dN, dD, Nc, Dc = rec
    u = sp.Symbol('u')
    Num = sum(sp.Rational(c.numerator, c.denominator) * u ** j for j, c in enumerate(Nc))
    Den = sum(sp.Rational(c.numerator, c.denominator) * u ** k for k, c in enumerate(Dc))
    return Num, Den, u


def extract(w2, w3, a, b, t_star, kS_label):
    R = side_recon(w2, w3, a, b, +1, F(t_star))
    L = side_recon(w2, w3, a, b, -1, F(t_star))
    if R is None or L is None:
        return None
    (Nr, Dr, u) = R
    (Nl, Dl, _) = L
    _, e3sum = slice_legs(w2, w3, a, b)
    e3u = e3sum.subs(t, sp.Rational(F(t_star).numerator, F(t_star).denominator) + u)
    A_diff = sp.cancel(Nr / Dr - Nl / Dl)      # (A_6/i)_R - (A_6/i)_L as fn of u=t-t*
    jumpN = sp.cancel(A_diff * e3u)            # N_6 jump
    jumpN = sp.together(jumpN)
    num, den = sp.fraction(jumpN)
    num = sp.expand(num)
    # order of u in num/den
    def mult(P):
        P = sp.Poly(P, u)
        m = 0
        while P.eval(0) == 0 and P.degree() >= 0 and P != 0:
            P = sp.Poly(sp.quo(P.as_expr(), u, u), u); m += 1
        return m
    order = mult(num) - mult(sp.expand(den))
    coeff = sp.simplify(sp.cancel(jumpN / u ** order)).subs(u, 0) if order else None
    return order, coeff, sp.factor(sp.cancel(jumpN))


if __name__ == "__main__":
    # (1=2) wall w4^2=w2^2+w3^2, Pythagorean crossings at w4=5 (t*=0 with a=5)
    print("=== (1=2) wall w4^2 = w2^2+w3^2 ; jump order & coefficient ===")
    for (w2, w3, b) in [(3, 4, 15), (3, 4, 16), (3, 4, 18), (6, 8, 22), (5, 12, 30)]:
        # wall at w4 = sqrt(w2^2+w3^2). pick a so that t*=0 -> a = sqrt(..)
        import math
        ww = (w2 * w2 + w3 * w3) ** 0.5
        if ww != int(ww):
            continue
        a = int(ww)
        res = extract(w2, w3, a, b, 0, f"k_234")
        if res is None:
            print(f"  w2={w2},w3={w3},b={b}: recon failed"); continue
        order, coeff, jf = res
        print(f"  w2={w2},w3={w3},w4*={a},b={b}: jump ORDER={order}, coeff@wall={coeff}")
