#!/usr/bin/env python3
"""Dense scan of the (1=1) jump coefficient P(0) across {a2=b4} as a function of w5,
to (a) LOCATE the matching sub-walls (kinks) and (b) measure the cross-term EXPONENT
by exact per-side rational reconstruction.

P(w5) is rational in w5 (solved legs w1,w6 ~ 1/sumFree); fit each side as N(w5)/sumFree^d
and compare across a kink: (P_R - P_L) should vanish like (w5 - w5c)^r at the sub-wall.
"""
from fractions import Fraction as F
import sympy as sp
import r6_xt2 as X, chambers_n6 as cn, r5_walls as W
w5=sp.Symbol('w5')

def Pvals(w2,w3,w5_list):
    out=[]
    for v in w5_list:
        r=X.jumpP(F(w2),F(w3),F(v))
        if isinstance(r,F): out.append((F(v),r))
    return out

def rat_reconstruct(pts, dmax=12):
    """fit P(w5) = num(s)/den(s), s=w5, as rational with den a power of sumFree=(11+w5).
    Try P*(11+w5)^d == polynomial(deg<=dmax)."""
    S=sp.Symbol('S')
    for d in range(0,8):
        scaled=[(v, p*F((11+v)**d)) for (v,p) in pts]
        # polynomial interpolation check
        n=len(scaled)
        for deg in range(0,min(dmax,n-2)+1):
            if n<deg+1+2: continue
            xs=[sp.Rational(v.numerator,v.denominator) for (v,_) in scaled[:deg+1]]
            ys=[sp.Rational(p.numerator,p.denominator) for (_,p) in scaled[:deg+1]]
            poly=sp.interpolate(list(zip(xs,ys)),S)
            ok=all(sp.Rational(p.numerator,p.denominator)==poly.subs(S,sp.Rational(v.numerator,v.denominator)) for (v,p) in scaled[deg+1:])
            if ok:
                return sp.cancel(poly/(11+S)**d), d, deg
    return None,None,None

if __name__=="__main__":
    w2,w3=3,5
    # 1) coarse scan to see kinks
    grid=[F(x,4) for x in range(8,49) if F(x,4) not in (F(w2),F(w3))]  # 2.0 .. 12.0 step .25
    print("coarse P(0) vs w5 (looking for kinks):",flush=True)
    pv=Pvals(w2,w3,grid)
    print(f"got {len(pv)} values",flush=True)
    # second differences to spot kinks
    for i in range(1,len(pv)-1):
        (v0,p0),(v1,p1),(v2,p2)=pv[i-1],pv[i],pv[i+1]
        # only if equally spaced
        if v1-v0==v2-v1:
            d2=p0-2*p1+p2
            flag="  <== large 2nd diff" if abs(float(d2))>1e6 else ""
            # print only near suspected walls
    # print the raw table compactly
    for (v,p) in pv:
        print(f"  w5={float(v):6.2f}  P={float(p): .6e}")
