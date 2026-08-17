#!/usr/bin/env python3
"""Manifold-reduce the H/H'-invariant monomial template bases (no oracle needed).
Find a maximal subset of monomials that are linearly INDEPENDENT on the manifold."""
from fractions import Fraction as F
import itertools, random
import chambers_n6 as cn, r5lib as L
PR=2**61-1
def minv(a): return pow(a%PR,PR-2,PR)
def fm(fr): return (fr.numerator%PR)*minv(fr.denominator%PR)%PR

def hinv_mons(deg, gdeg):
    out=[]
    for e in itertools.product(*[range(deg+1) for _ in gdeg]):
        if sum(e[i]*gdeg[i] for i in range(len(gdeg)))==deg: out.append(e)
    return out

def eval_h(e, oms, mode):
    # mode 'P' (1=1): x=om0,y=om3,A1=om1+om2,A2=om1om2,B1=om4+om5,B2=om4om5
    # mode 'Q' (1=2): x=om0,y=om5,A1=om1+om2,A2=om1om2,B1=om3+om4,B2=om3om4
    if mode=='P': v=[oms[0],oms[3],oms[1]+oms[2],oms[1]*oms[2],oms[4]+oms[5],oms[4]*oms[5]]
    else:         v=[oms[0],oms[5],oms[1]+oms[2],oms[1]*oms[2],oms[3]+oms[4],oms[3]*oms[4]]
    r=F(1)
    for i,ex in enumerate(e):
        if ex: r*=v[i]**ex
    return r

def manifold_points(npts, seed):
    rnd=random.Random(seed); pts=[]
    while len(pts)<npts:
        free=[F(rnd.randint(-80,80),10) for _ in range(4)]
        if 0 in free: continue
        oms=cn.solve_squares(free)
        if oms is None or any(w==0 for w in oms): continue
        pts.append(oms)
    return pts

def independent_subset(mons, mode, npts=900, seed=3):
    pts=manifold_points(npts,seed)
    # build matrix points x monomials mod PR, find independent columns greedily by row-reduction
    cols=len(mons)
    rows=[[fm(eval_h(m,o,mode)) for m in mons] for o in pts]
    # column rank: do RREF tracking pivot columns
    nrow=len(rows); Mx=[row[:] for row in rows]; piv=[]; r=0
    for c in range(cols):
        p=next((i for i in range(r,nrow) if Mx[i][c]%PR!=0),None)
        if p is None: continue
        Mx[r],Mx[p]=Mx[p],Mx[r]; iv=minv(Mx[r][c]); Mx[r]=[(x*iv)%PR for x in Mx[r]]
        for i in range(nrow):
            if i!=r and Mx[i][c]%PR!=0:
                f=Mx[i][c]; Mx[i]=[(Mx[i][k]-f*Mx[r][k])%PR for k in range(cols)]
        piv.append(c); r+=1
        if r==nrow: break
    return [mons[c] for c in piv], len(piv)

if __name__=="__main__":
    gdeg=(1,1,1,2,1,2)
    monsP=hinv_mons(9,gdeg); monsQ=hinv_mons(5,gdeg)
    print("raw H-inv deg9:",len(monsP)," H'-inv deg5:",len(monsQ),flush=True)
    indP,rP=independent_subset(monsP,'P'); print("(1=1) template indep dim on manifold:",rP,flush=True)
    indQ,rQ=independent_subset(monsQ,'Q'); print("(1=2) template indep dim on manifold:",rQ,flush=True)
