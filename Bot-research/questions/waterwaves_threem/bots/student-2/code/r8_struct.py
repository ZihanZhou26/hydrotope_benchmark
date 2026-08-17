#!/usr/bin/env python3
"""Examine per-chamber rational structure of C_n = A_n/(i 2^{n-1}) on 1-D slices.
Uses my own ./bg --batch (exact). Factors numerator & denominator on each slice."""
import sympy as sp, itertools
from fractions import Fraction as F
import r8bg

t = sp.Symbol('t')
def Q(x): return sp.Rational(F(x).numerator, F(x).denominator)

def chamber_sig(oms):
    n = len(oms); M=list(range(3)); P=list(range(3,n)); sq=[w*w for w in oms]
    s=[]
    for i in M:
        for r in range(1,len(P)+1):
            for T in itertools.combinations(P,r):
                v=sum(sq[j] for j in T)-sq[i]
                if v==0: return None
                s.append(1 if v>0 else -1)
    # same-type orderings (analytic but track to stay in one analytic piece)
    for i,j in itertools.combinations(M,2):
        if sq[i]==sq[j]: return None
        s.append(1 if sq[i]>sq[j] else -1)
    for i,j in itertools.combinations(P,2):
        if sq[i]==sq[j]: return None
        s.append(1 if sq[i]>sq[j] else -1)
    return tuple(s)

def Dn(oms):
    n=len(oms); d=F(1)
    for i in range(3):
        for j in range(3,n): d*=(oms[i]+oms[j])
    return d

def slice_rational(n, base_free, idx, vals):
    """Collect (t, C_n, oms) staying in ONE chamber; reconstruct C_n=Num/Den exact."""
    pts=[]; sig0=None
    # exact batch
    frees=[]
    keep=[]
    for v in vals:
        fr=list(base_free); fr[idx]=v
        if sum(F(x) for x in fr)==0: continue
        frees.append(fr); keep.append(v)
    ims=r8bg.batch(frees, n, double=False)
    for v,fr,im in zip(keep,frees,ims):
        if im is None: continue
        oms=r8bg.solve_legs(fr,n)
        sig=chamber_sig(oms)
        if sig is None: continue
        if sig0 is None: sig0=sig
        if sig!=sig0: continue
        pts.append((F(v), F(im,2**(n-1)), oms))
    if len(pts)<12: return None
    xs=[Q(p[0]) for p in pts]
    num=[Q(p[1]*Dn(p[2])) for p in pts]
    den=[Q(Dn(p[2])) for p in pts]
    Nexpr=sp.interpolate(list(zip(xs,num)),t)
    Dexpr=sp.interpolate(list(zip(xs,den)),t)
    return sp.factor(Nexpr), sp.factor(Dexpr), pts[0][2], len(pts)

if __name__=="__main__":
    print("="*70)
    print("C_6 on slices (Num=C*Dfull, Den=Dfull); look at factorization")
    print("="*70)
    # fine grid over regions with long single-chamber runs
    cases=[([F(2),F(3),F(5),F(7)],3,[F(k,40) for k in range(201,266)],"w5 in [5.0,6.6]"),
           ([F(2),F(3),F(5),F(7)],3,[F(k,40) for k in range(133*2,400)],"w5 in [6.65,10]"),
           ([F(2),F(3),F(5),F(7)],3,[F(k,40) for k in range(81,120)],"w5 in [2.0,3.0]")]
    for base,idx,vals,desc in cases:
        r=slice_rational(6,base,idx,vals)
        if r is None: print(desc,": no clean slice"); continue
        N,D,om0,npts=r
        print(f"\n--- {desc}  ({npts} pts, chamber-fixed) ---")
        print("  om0 =",[str(x) for x in om0])
        print("  Num =",N)
        print("  Den =",D)
        print("  C_6 =", sp.factor(N/D))
