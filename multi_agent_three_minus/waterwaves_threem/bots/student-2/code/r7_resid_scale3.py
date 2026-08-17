#!/usr/bin/env python3
"""Res_{25}(merged scale w2) at FIXED surviving config -- F-CONSTANT slice.

Vary (w5,w6) OPPOSITELY (sumFree const => solved legs 1,7 polynomial in t, so
A_7*Dfree is polynomial). Wall {w2+w5=0} placed near tv=0.
Surviving config {1,3,4,6,7} kept fixed across w2:
  w5 = w5base + tv,  w6 = w6base - tv ;  set w5base = -w2 + 0.6 (wall at tv=-0.6),
  w6base = w6target - 0.6  (so w6 at wall = w6target, w2-independent).
Then w1,w7 (5pt-solved from w3,w4,w6target) are w2-independent => fixed survivor."""
import sympy as sp, itertools
from fractions import Fraction as F
from n7_mindenom import collect, Dfree_val, Qr
from r7_residue import two_minus
t=sp.Symbol('t')

def residue_25_fconst(w2,w3,w4,w6target,step=F(1,40),maxk=40):
    M=(1,2,3);P=(4,5,6,7);n=7
    w5base=-w2+F(6,10); w6base=w6target-F(6,10)
    fixed=[w2,w3,w4,F(0),F(0)]   # positions 3,4 (w5,w6) overwritten by collect
    pts=collect(7,M,P,fixed,w5base,w6base,3,4,step=step,maxk=maxk)
    if len(pts)<30: return None,len(pts)
    xs=[Qr(tv) for (tv,_,_) in pts]
    Nv=[Qr(im)*Dfree_val(oms,M,P) for (_,im,oms) in pts]
    half=len(pts)*2//3
    Np=sp.Poly(sp.interpolate(list(zip(xs[:half],Nv[:half])),t),t)
    if not all(Np.eval(xs[i])==Nv[i] for i in range(half,len(pts))): return None,-1
    OM={a:sp.Poly(sp.interpolate(list(zip(xs,[Qr(o[a-1]) for (_,_,o) in pts])),t),t) for a in range(1,8)}
    pf=sp.Poly(OM[2].as_expr()+OM[5].as_expr(),t)
    if pf.degree()<1: return None,-2
    t0=sp.Rational(-pf.nth(0),pf.nth(1))
    R=sp.Integer(1)
    for a in M:
        for b in P:
            if (a,b)!=(2,5): R*=sp.Poly(OM[a].as_expr()+OM[b].as_expr(),t).eval(t0)
    res=sp.Rational(Np.eval(t0))/R
    w={a:F(OM[a].eval(t0)) for a in range(1,8)}
    return (res,w),len(pts)

if __name__=="__main__":
    w3,w4,w6t=F(3),F(5),F(11)
    print(f"Fixed survivors via (w3,w4,w6target)=({w3},{w4},{w6t})\n")
    data=[]
    for w2 in [F(2),F(3),F(4),F(5),F(6),F(7),F(8),F(5,2)]:
        out,npts=residue_25_fconst(w2,w3,w4,w6t)
        if out is None: print(f"  w2={w2}: bad (code {npts})"); continue
        res,w=out
        surv=(w[1],w[3],w[4],w[6],w[7])
        A2m=F(16)*two_minus((1,3),w,2)
        data.append((w2,sp.Rational(res),A2m,surv))
        print(f"  w2={w2}: surv(1,3,4,6,7)={[str(x) for x in surv]}  Res/i={res}")
    if len(data)>=3:
        print("\n--- merged-scale dependence (surviving config FIXED) ---")
        for w2,res,A2m,surv in data:
            print(f"  w2={w2}: Res={res}")
            print(f"        Res/w2^2 = {sp.nsimplify(res/w2**2)}")
            print(f"        Res/A5_2m = {sp.nsimplify(res/sp.Rational(A2m)) if A2m else None}")
        u=sp.Symbol('u')
        xs=[sp.Rational(w2.numerator,w2.denominator)**2 for w2,_,_,_ in data]
        ys=[res for _,res,_,_ in data]
        p=sp.interpolate(list(zip(xs,ys)),u)
        pp=sp.Poly(p,u)
        print(f"\n  Res interpolated as poly in u=w2^2: degree {pp.degree()}")
        print(f"    Res(u) = {sp.factor(p)}")
