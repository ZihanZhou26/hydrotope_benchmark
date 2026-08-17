#!/usr/bin/env python3
"""Exact soft coefficient: lim_{w5->0} A_6/(i w5^2), via exact rational values +
rational Richardson extrapolation, and its relation to the n=5 amplitude of the
surviving legs {1,2,3,4,6}.
"""
from fractions import Fraction as F
import sympy as sp
import harness as h
import itertools

SIG6 = [-1,-1,-1,1,1,1]; SIG5=[-1,-1,-1,1,1]


def A5_form(w1,w2,w3,w4,w5):
    m=min(w4**2,w5**2); tot=F(0); legs=[w1,w2,w3]
    for r in range(4):
        for S in itertools.combinations(range(3),r):
            v=m-sum(legs[i]**2 for i in S)
            if v>0: tot+=F((-1)**r)*v**2
    return 16*w4*w5*tot


if __name__=="__main__":
    base=[F(3),F(5),F(4)]   # legs 2,3,4
    # exact A6/w5^2 at a sequence of eps, then Richardson (eps -> 0)
    seq=[]
    for k in range(2,9):
        eps=F(1,2**k)
        im6,om6,_=h.on_shell([base[0],base[1],base[2],eps],SIG6)
        seq.append((eps, F(im6, 1)/eps**2))
    print("eps, A6/(i eps^2):")
    for e,v in seq: print(f"  {float(e):.6f}  {v}  ~ {float(v):.4f}")
    # Richardson: assume A6/eps^2 = c0 + c1 eps + c2 eps^2 + ...
    X=sp.Symbol('e'); pts=[(sp.Rational(e.numerator,e.denominator), sp.Rational(v.numerator,v.denominator)) for e,v in seq]
    poly=sp.interpolate(pts,X)
    c0=sp.expand(poly).subs(X,0)
    print("\nlim_{eps->0} A6/(i eps^2) =", c0, "=", float(c0))
    # n=5 of surviving legs at eps->0: legs 1,2,3 minus, 4 and 6(solved) plus.
    # take eps tiny, read om6 legs (1,2,3,4,6) and eval n=5 closed form with plus pair {4,6}
    im6,om6,_=h.on_shell([base[0],base[1],base[2],F(1,2**12)],SIG6)
    w=[F(o) for o in om6]
    a5=A5_form(w[0],w[1],w[2],w[3],w[5])  # plus legs 4 and 6
    print("n=5 (legs1,2,3 minus;4,6 plus) A5/i ~", float(a5), a5)
    print("ratio c0 / A5 ~", float(c0/a5))
