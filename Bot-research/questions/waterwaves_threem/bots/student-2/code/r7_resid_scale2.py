#!/usr/bin/env python3
"""Isolate Res_{25}(merged scale w2) at FIXED surviving 5pt config.

Fix (w3,w4,w6); the surviving config {1,3,4,6,7} (legs 1,7 solved) is then
INDEPENDENT of w2 (the merged pair (2,5) drops out of both conservation laws at
the wall w2+w5=0). Vary w2; slice w5 near -w2; extract Res = lim (w2+w5) A_7.
"""
import sympy as sp, itertools
from fractions import Fraction as F
import harness as h
t=sp.Symbol('t')
def Qr(x): return sp.Rational(x.numerator,x.denominator)
from r7_residue import msubs_of,csig,Dfree,two_minus

def slice_toward(n,M,P,fixed_w2,w3,w4,w6,t0_w5,step=F(1,50),maxk=70):
    """free=[w2,w3,w4,w5,w6]; vary w5 starting just above t0_w5 (= -w2), one chamber."""
    SIG=[-1,-1,-1,1,1,1,1]; ms=msubs_of(n,M,P); pts=[]; s0=None
    base=t0_w5+F(6,10)
    for k in range(maxk):   # drive downward toward the wall t0_w5
        w5=base-step*k
        free=[fixed_w2,w3,w4,w5,w6]
        if sum(free)==0: continue
        try: im,oms,rep=h.on_shell([str(x) for x in free],SIG)
        except Exception: break
        if rep!=0: continue
        oms=[F(o) for o in oms]; s=csig(oms,n,M,ms)
        if 0 in s: continue
        if s0 is None: s0=s
        if s!=s0: break
        pts.append((w5,F(im),oms))
    return pts,s0

def residue_25(w2,w3,w4,w6):
    n=7;M=(1,2,3);P=(4,5,6,7)
    t0=-w2
    pts,s0=slice_toward(n,M,P,w2,w3,w4,w6,t0)
    if len(pts)<30: return None,len(pts)
    xs=[Qr(w5) for (w5,_,_) in pts]
    Nv=[Qr(im)*Dfree(oms,M,P) for (_,im,oms) in pts]
    half=len(pts)*2//3
    Np=sp.Poly(sp.interpolate(list(zip(xs[:half],Nv[:half])),t),t)
    if not all(Np.eval(xs[i])==Nv[i] for i in range(half,len(pts))): return None,-1
    OM={a:sp.Poly(sp.interpolate(list(zip(xs,[Qr(o[a-1]) for (_,_,o) in pts])),t),t) for a in range(1,8)}
    t0v=sp.Rational(t0.numerator,t0.denominator)
    R=sp.Integer(1)
    for a in M:
        for b in P:
            if (a,b)!=(2,5): R*=sp.Poly(OM[a].as_expr()+OM[b].as_expr(),t).eval(t0v)
    res=sp.Rational(Np.eval(t0v))/R
    w={a:F(OM[a].eval(t0v)) for a in range(1,8)}
    return (res,w),len(pts)

if __name__=="__main__":
    w3,w4,w6=F(3),F(5),F(11)
    print(f"Fixed (w3,w4,w6)=({w3},{w4},{w6}). Surviving config {{1,3,4,6,7}} should be w2-independent.\n")
    data=[]
    for w2 in [F(2),F(3),F(4),F(5),F(6),F(7),F(5,2),F(7,2)]:
        out,npts=residue_25(w2,w3,w4,w6)
        if out is None: print(f"  w2={w2}: bad slice (npts={npts})"); continue
        res,w=out
        surv=(w[1],w[3],w[4],w[6],w[7])
        A2m=F(16)*two_minus((1,3),w,2)
        data.append((w2,res,A2m,surv))
        print(f"  w2={w2}: surviving(1,3,4,6,7)={[str(x) for x in surv]}")
        print(f"     Res/i={res}")
        print(f"     16*A5_2m(min13)={A2m}   ratio={sp.nsimplify(sp.Rational(res)/sp.Rational(A2m)) if A2m else None}")
    if len(data)>=3:
        print("\n--- Res(w2) at fixed surviving config: fit vs w2 ---")
        A2m0=data[0][2]
        for w2,res,A2m,surv in data:
            r=sp.Rational(res)
            print(f"  w2={w2}: Res={r};  Res/w2^2={sp.nsimplify(r/w2**2)};  Res/A5={sp.nsimplify(r/sp.Rational(A2m)) if A2m else None}")
