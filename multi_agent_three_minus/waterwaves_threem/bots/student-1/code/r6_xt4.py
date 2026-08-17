#!/usr/bin/env python3
"""Test whether P_{24}(w5) (jump coeff across {a2=b4}, scanning wall point by w5)
is a SINGLE rational function over a range (=> no cross-term kink crossed) or kinks
(=> cross-term). Exact rational reconstruction with held-out validation.

Also locate the matching sub-loci on the wall {a2=b4} (w2=3,w3=5,w4=3):
  matching A {2->4,3->5,1->6}: a3=b5  => w5=5
  matching B {2->4,3->6,1->5}: a3=b6  => w3^2=w6^2  (find w5)
"""
from fractions import Fraction as F
import sympy as sp
import r6_xt2 as X, chambers_n6 as cn
S=sp.Symbol('S')

def fit_single_rational(pts, sumfree_lin, dmax=14):
    """pts=[(w5,P)]. Try P*(sumfree_lin)^d == poly(deg<=dmax) consistently w/ held-out."""
    for d in range(0,10):
        scaled=[(v, p*(sumfree_lin.subs(S,sp.Rational(v.numerator,v.denominator)))**d) for (v,p) in pts]
        n=len(scaled)
        for deg in range(0,min(dmax,n-3)+1):
            if n<deg+1+3: continue
            data=[(sp.Rational(v.numerator,v.denominator), sp.nsimplify(p)) for (v,p) in scaled[:deg+1]]
            poly=sp.interpolate(data,S)
            ok=all(sp.nsimplify(p)==poly.subs(S,sp.Rational(v.numerator,v.denominator)) for (v,p) in scaled[deg+1:])
            if ok:
                return sp.cancel(poly/sumfree_lin**d), d, deg
    return None,None,None

if __name__=="__main__":
    w2,w3=3,5
    sumfree=11+S  # sumFree = 2*w2+w3+w5 = 6+5+w5
    # sample exact P on each side and overall, avoiding w5=5 and w5=w2,w3
    left=[F(x,4) for x in range(8,20)]            # 2.0 .. 4.75
    right=[F(x,4) for x in range(21,45)]          # 5.25 .. 11.0
    allpts=left+right
    print("computing exact P values...",flush=True)
    def getP(vs):
        out=[]
        for v in vs:
            r=X.jumpP(F(w2),F(w3),F(v))
            if isinstance(r,F): out.append((v,r))
        return out
    Lp=getP(left); Rp=getP(right)
    print(f"left {len(Lp)} right {len(Rp)}",flush=True)
    # 1) single rational over WHOLE range?
    fA,dA,degA=fit_single_rational(Lp+Rp, sumfree)
    print(f"\n[WHOLE range] single rational? {'YES' if fA is not None else 'NO'}  (den sumFree^{dA}, num deg {degA})",flush=True)
    # 2) per-side
    fL,dL,degL=fit_single_rational(Lp, sumfree)
    fR,dR,degR=fit_single_rational(Rp, sumfree)
    print(f"[LEFT  w5<5] rational: den sumFree^{dL}, num deg {degL}",flush=True)
    print(f"[RIGHT w5>5] rational: den sumFree^{dR}, num deg {degR}",flush=True)
    if fL is not None and fR is not None:
        diff=sp.cancel(fR-fL)
        print("\nP_R - P_L =",flush=True)
        sp.pprint(sp.factor(diff))
        # order of vanishing at w5=5
        num,den=sp.fraction(diff)
        num=sp.Poly(sp.expand(num),S)
        order=0; nn=num
        while nn.eval(5)==0 and nn.degree()>0:
            nn=nn.diff(S); order+=1
        print(f"\norder of vanishing of (P_R-P_L) at w5=5: {order}",flush=True)
