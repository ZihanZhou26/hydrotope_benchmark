#!/usr/bin/env python3
"""Soft recursion at n=7 -- EXACT (F-constant slice), extends s2_012 to n>=7.

A_n^{3-} -> 2(n-3) w_p^2 A_{n-1} as w_p->0; 2(n-3)=8 at n=7.
Make the soft leg w_p=eps and a partner plus leg = c-eps so sumFree is CONSTANT
=> all legs polynomial in eps => A_7*Dfree(eps) =: Nfull(eps) polynomial, Dfree(eps)
polynomial.  lim A_7/eps^2 = ([eps^2] Nfull)/Dfree(0)  (Nfull has a double zero at 0).
Compare to 8 * A_6(surviving config at eps->0)."""
import sympy as sp, itertools
from fractions import Fraction as F
import harness as h
e=sp.Symbol('e')
def Qr(x): return sp.Rational(x.numerator,x.denominator)

def Dfree_poly(omfns):  # omfns: dict leg->sympy poly in e ; product of mixed pairs
    M=(1,2,3);P=(4,5,6,7); D=sp.Integer(1)
    for i in M:
        for j in P: D*=(omfns[i]+omfns[j])
    return sp.expand(D)

def soft_exact(soft_leg, partner_plus, base_free, surviving_free, surv_signs):
    """soft_leg, partner_plus are positions (0-idx in the 5 free legs 2..6).
    base_free: the 5 free leg values at eps=0 (soft_leg entry is the limit, =0).
    Vary free[soft_leg]=eps, free[partner_plus]=base[partner]-eps (sumFree const)."""
    SIG7=[-1,-1,-1,1,1,1,1]
    pts=[]
    for k in range(1,46):
        eps=F(k,60)
        free=[F(x) for x in base_free]
        free[soft_leg]=eps
        free[partner_plus]=F(base_free[partner_plus])-eps
        try: im,oms,rep=h.on_shell([str(x) for x in free],SIG7)
        except Exception: continue
        if rep!=0: continue
        pts.append((Qr(eps),F(im),[F(o) for o in oms]))
    # interpolate Nfull(e)=A_7*Dfree and Dfree(e) as polynomials in e
    xs=[x for x,_,_ in pts]
    # build omega(e) polynomials
    OM={a:sp.Poly(sp.interpolate(list(zip(xs,[Qr(o[a-1]) for _,_,o in pts])),e),e) for a in range(1,8)}
    omf={a:OM[a].as_expr() for a in range(1,8)}
    Dfree=sp.expand(Dfree_poly(omf))
    Nv=[Qr(im)*sp.Poly(Dfree,e).eval(x) for (x,im,_) in pts]
    half=len(pts)*2//3
    Np=sp.Poly(sp.interpolate(list(zip(xs[:half],Nv[:half])),e),e)
    okN=all(Np.eval(xs[i])==Nv[i] for i in range(half,len(pts)))
    a2=Np.nth(2)  # coefficient of e^2
    D0=sp.Poly(Dfree,e).eval(0)
    lim=sp.Rational(a2)/sp.Rational(D0)
    # surviving 6pt amplitude (free legs = surviving_free) at eps=0
    im6,_,_=h.on_shell([str(x) for x in surviving_free],surv_signs)
    return lim, F(im6), okN, len(pts)

if __name__=="__main__":
    print("=== Soft recursion at n=7 (EXACT, F-const slice). expect lim = 8*A_6 ===\n")
    # free legs 2..6 -> (w2,w3,w4,w5,w6). PLUS leg = leg6 (pos 4) -> 0; partner = leg5 (pos 3).
    # base eps=0: (2,3,5,7,0); surviving 6pt three-minus free = (2,3,5,7).
    lim,a6,okN,npts=soft_exact(4,3,[F(2),F(3),F(5),F(7),F(0)],[F(2),F(3),F(5),F(7)],[-1,-1,-1,1,1,1])
    print(f"PLUS leg ->0 (npts {npts}, Nfull poly {okN}):")
    print(f"  lim A_7/(i eps^2) = {lim}")
    print(f"  8 * A_6^3minus    = {8*a6}")
    print(f"  EXACT match: {lim==8*a6}\n")
    # MINUS leg = leg3 (pos 1) -> 0 ; partner plus = leg6 (pos 4).
    # base eps=0: (2,0,5,7,11); surviving 6pt TWO-minus free=(2,5,7,11) signs(-1,-1,1,1,1,1)
    lim,a6,okN,npts=soft_exact(1,4,[F(2),F(0),F(5),F(7),F(11)],[F(2),F(5),F(7),F(11)],[-1,-1,1,1,1,1])
    print(f"MINUS leg ->0 (npts {npts}, Nfull poly {okN}):")
    print(f"  lim A_7/(i eps^2) = {lim}")
    print(f"  8 * A_6^2minus    = {8*a6}")
    print(f"  EXACT match: {lim==8*a6}")
