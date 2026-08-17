#!/usr/bin/env python3
"""Soft MINUS-leg limit: as omega_2 -> 0, the n=6 three-minus config degenerates
to n=5 with minus legs {1,3} and plus {4,5,6} = the TWO-minus sector (known
exactly). Find the scaling power and the factor relating A_6^{3-} to A_5^{2-}.
"""
from fractions import Fraction as F
import sympy as sp, itertools
import harness as h

SIG6=[-1,-1,-1,1,1,1]


def A5_twominus(wa, wb, plus):
    """two-minus law n=5: minus legs a,b; plus = list of 3 plus freqs.
    A = i 2^{4} g^{-1}? prefactor 2^{n-1}=2^4=16, g=1. exponent n-3=2."""
    beta2=min(wa**2,wb**2)
    tot=F(0)
    for r in range(4):
        for S in itertools.combinations(range(3),r):
            v=beta2-sum(plus[i]**2 for i in S)
            if v>0: tot+=F((-1)**r)*v**2
    return 16*wa*wb*tot


if __name__=="__main__":
    base=[F(5),F(4),F(6)]  # legs 3,4,5 ; leg2=eps; legs1,6 solved
    seq=[]
    for k in range(2,10):
        eps=F(1,2**k)
        # free legs order: 2,3,4,5
        im6,om6,_=h.on_shell([eps,base[0],base[1],base[2]],SIG6)
        seq.append((eps, F(im6,1)))
    print("eps=w2->0:  A6/i, /eps, /eps^2")
    for e,v in seq:
        print(f"  {float(e):.6f}  A6/i={float(v):.6g}  /eps={float(v/e):.6g}  /eps^2={float(v/e**2):.6g}")
    X=sp.Symbol('e')
    for power in [1,2]:
        pts=[(sp.Rational(e.numerator,e.denominator), sp.Rational((v/e**power).numerator,(v/e**power).denominator)) for e,v in seq]
        c0=sp.expand(sp.interpolate(pts,X)).subs(X,0)
        print(f"lim A6/(i eps^{power}) =", float(c0))
    # two-minus A5 of surviving legs {1,3 minus; 4,5,6 plus} at eps tiny
    im6,om6,_=h.on_shell([F(1,2**13),base[0],base[1],base[2]],SIG6)
    w=[F(o) for o in om6]
    a5=A5_twominus(w[0],w[2],[w[3],w[4],w[5]])  # minus legs 1,3 ; plus 4,5,6
    print("two-minus A5/i (legs1,3 minus;4,5,6 plus) ~", float(a5))
