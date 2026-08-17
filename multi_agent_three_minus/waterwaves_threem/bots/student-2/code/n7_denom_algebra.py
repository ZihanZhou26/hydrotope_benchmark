#!/usr/bin/env python3
"""ALGEBRAIC reduction of the n=7 free denominator on the manifold.
Claim: D_12 = prod_{i in M, j in P}(w_i+w_j) = prod_{i in M}(c w_i + d) on-shell,
with c = e3^- + e3^+, d = e4^+ (e_k = elementary symmetric polys).
Mechanism: Q_7(x)=prod_{j in P}(x+w_j) = x*p_-(x) + (c x + d) since e1^-=-e1^+, e2^-=e2^+.
So Q_7(w_i) = c w_i + d at each minus root, and D_12 = prod_i Q_7(w_i).
NO oracle needed -- pure algebra on the resonance manifold.
"""
import sympy as sp
from fractions import Fraction as F
import harness as h

MINUS=(1,2,3); PLUS=(4,5,6,7)
SIG7=[-1,-1,-1,1,1,1,1]

def ek(vals,k):
    return sum(sp.prod(c) for c in __import__('itertools').combinations(vals,k)) if k>0 else sp.Integer(1)

def check_point(free):
    oms=h.solve_legs_1n(free,SIG7)            # exact Fractions, full 7 omegas
    w={i+1: sp.Rational(oms[i].numerator,oms[i].denominator) for i in range(7)}
    m=[w[i] for i in MINUS]; p=[w[j] for j in PLUS]
    # manifold sanity
    assert sum(w.values())==0
    assert sum((1 if i in MINUS else -1)*0 for i in range(1))==0
    sig=sum((-1 if (i+1) in MINUS else 1)*w[i+1]**2 for i in range(7))
    assert sig==0, sig
    # invariants
    e3m=ek(m,3); e2m=ek(m,2); e1m=ek(m,1)
    e1p=ek(p,1); e2p=ek(p,2); e3p=ek(p,3); e4p=ek(p,4)
    c=e3m+e3p; d=e4p
    # D_12 directly
    D12=sp.Integer(1)
    for i in MINUS:
        for j in PLUS:
            D12*= (w[i]+w[j])
    # reduction 1: prod_i Q7(w_i), Q7(x)=prod_j(x+w_j)
    red1=sp.Integer(1)
    for i in MINUS:
        Q=sp.Integer(1)
        for j in PLUS: Q*=(w[i]+w[j])
        red1*=Q
    # reduction 2: prod_i (c w_i + d)
    red2=sp.prod([c*w[i]+d for i in MINUS])
    # reduction 3: invariant closed form  c^3 e3m + c^2 d e2 - c d^2 e1p + d^3
    red3= c**3*e3m + c**2*d*e2m - c*d**2*e1p + d**3
    # also check Q7(w_i)=c w_i + d individually
    okQ=all( sp.prod([w[i]+w[j] for j in PLUS]) == c*w[i]+d for i in MINUS )
    return D12, red1, red2, red3, okQ, (e1m,e1p,e2m,e2p)

if __name__=="__main__":
    pts=[[2,3,5,7,11],[3,sp.Rational(5,2),4,sp.Rational(13,3),7],
         [1,2,4,6,9],[5,-3,2,7,-4],[sp.Rational(7,5),3,sp.Rational(11,4),6,2]]
    allok=True
    for free in pts:
        D12,r1,r2,r3,okQ,(e1m,e1p,e2m,e2p)=check_point([F(str(x)) if not isinstance(x,sp.Rational) else F(x.p,x.q) for x in free])
        ok = (D12==r1==r2==r3) and okQ and (e1m==-e1p) and (e2m==e2p)
        allok&=ok
        print(f"free={free}: D12={D12}  =prod_i(c w_i+d)? {D12==r2}  =invform? {D12==r3}  Q7(w_i)=cw_i+d? {okQ}  e1m=-e1p:{e1m==-e1p} e2m=e2p:{e2m==e2p}  ALL:{ok}")
    print("\nALL POINTS CONSISTENT:", allok)
