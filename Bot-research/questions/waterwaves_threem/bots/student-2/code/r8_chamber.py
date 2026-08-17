#!/usr/bin/env python3
"""Per-chamber numerator of C_6 over the MINIMAL denom (e3m+e3p): degree 11.
Reconstruct on a 1-D slice within one chamber, factor, study structure."""
import sympy as sp, itertools
from fractions import Fraction as F
import r8bg

t = sp.Symbol('t')
def Q(x): return sp.Rational(F(x).numerator, F(x).denominator)

def chamber_sig(oms):
    n=len(oms); M=list(range(3)); P=list(range(3,n)); sq=[w*w for w in oms]; s=[]
    for i in M:
        for r in range(1,len(P)+1):
            for T in itertools.combinations(P,r):
                v=sum(sq[j] for j in T)-sq[i]
                if v==0: return None
                s.append(1 if v>0 else -1)
    for i,j in itertools.combinations(M,2):
        if sq[i]==sq[j]: return None
        s.append(1 if sq[i]>sq[j] else -1)
    for i,j in itertools.combinations(P,2):
        if sq[i]==sq[j]: return None
        s.append(1 if sq[i]>sq[j] else -1)
    return tuple(s)

def e3m(o): return o[0]*o[1]*o[2]
def e3p(o): return o[3]*o[4]*o[5]

def one_slice(base, idx, kgrid):
    frees=[]; keep=[]
    for k in kgrid:
        v=F(k,40); fr=list(base); fr[idx]=v
        if sum(F(x) for x in fr)==0: continue
        frees.append(fr); keep.append(v)
    ims=r8bg.batch(frees,6,double=False)
    pts=[]; sig0=None
    for v,fr,im in zip(keep,frees,ims):
        if im is None: continue
        oms=r8bg.solve_legs(fr,6); sig=chamber_sig(oms)
        if sig is None: continue
        if sig0 is None: sig0=sig
        if sig!=sig0: continue
        C=F(im,2**5)            # C_6 = A_6/(i 2^5)
        Nmin=C*(e3m(oms)+e3p(oms))
        pts.append((F(v),Nmin,oms))
    if len(pts)<14: return None
    xs=[Q(p[0]) for p in pts]; ys=[Q(p[1]) for p in pts]
    poly=sp.Poly(sp.interpolate(list(zip(xs[:14],ys[:14])),t),t)
    # verify it's degree<=11 and matches held-out
    ok=all(poly.eval(xs[i])==ys[i] for i in range(14,len(pts)))
    return poly, ok, pts[0][2], len(pts)

if __name__=="__main__":
    print("C_6 * (e3m+e3p) per-chamber numerator on a slice (degree should be <=11)")
    for base,idx,grid,desc in [([F(2),F(3),F(5),F(7)],3,range(201,266),"w5 in [5,6.6]"),
                               ([F(2),F(3),F(5),F(7)],3,range(266,400),"w5 in [6.65,10]"),
                               ([F(2),F(3),F(5),F(7)],3,range(81,120),"w5 in [2,3]")]:
        r=one_slice(base,idx,grid)
        if r is None: print(desc,"no slice"); continue
        poly,ok,om0,npts=r
        print(f"\n--- {desc}: {npts} pts, held-out ok={ok}, deg={poly.degree()} ---")
        print("  om0=",[str(x) for x in om0])
        print("  N_min(t) =", sp.factor(poly.as_expr()))
