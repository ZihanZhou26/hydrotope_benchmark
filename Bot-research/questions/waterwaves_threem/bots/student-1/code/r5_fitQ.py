#!/usr/bin/env python3
"""Harvest reference (1=2) jump-coefficient Q and fit it (deg5, H'-sym).
Reference (1=2) wall: minus idx0, plus pair {idx3,idx4}, excluded plus idx5.
H' = swap(idx1,idx2) x swap(idx3,idx4); distinguished idx0,idx5.
Basis gens: x=om0, y=om5, A1=om1+om2,A2=om1 om2, B1=om3+om4,B2=om3 om4 (deg 1,1,1,2,1,2)."""
from fractions import Fraction as F
import itertools, sympy as sp, random, sys
import r5lib as L, r5_walls as W, r5_group as Gp, chambers_n6 as cn
t=W.t

def hp_mons(deg, gdeg=(1,1,1,2,1,2)):
    out=[]
    for e in itertools.product(*[range(deg+1) for _ in gdeg]):
        if sum(e[i]*gdeg[i] for i in range(len(gdeg)))==deg: out.append(e)
    return out
def eval_mon(e, oms):
    x=oms[0]; y=oms[5]; A1=oms[1]+oms[2]; A2=oms[1]*oms[2]; B1=oms[3]+oms[4]; B2=oms[3]*oms[4]
    v=[x,y,A1,A2,B1,B2]; r=F(1)
    for i,ex in enumerate(e):
        if ex: r*=v[i]**ex
    return r

def harvest(target=130, seed=7):
    rnd=random.Random(seed); data=[]; tries=0
    while len(data)<target and tries<2000:
        tries+=1
        vals=[F(rnd.randint(-70,70),10) for _ in range(4)]
        w2,w3,a,b=vals
        if 0 in vals or w2==w3 or a==b: continue
        crs=W.find_crossings(w2,w3,a,b,F(1,40),F(6))
        for (lo,hi,key) in crs:
            if key[0]!='2': continue
            r=W.extract_bracket(w2,w3,a,b,lo,hi,key,F(1,120),14)
            if r[0] in ('fitfail',): continue
            kk,jump,kpoly,coef,isp=r
            if not isp: continue
            i=key[1]; pair=key[2]; perm=Gp.relabel_12_to_ref(i,pair)
            cf=sp.Poly(sp.expand(coef),t)
            for tt in [F(rnd.randint(-55,55),10) for _ in range(5)]:
                oms=cn.solve_squares(L.fc_free(w2,w3,a,b,tt))
                if oms is None or any(w==0 for w in oms): continue
                val=cf.eval(sp.Rational(tt.numerator,tt.denominator))
                qv=F(sp.Rational(val).p,sp.Rational(val).q)
                data.append((tuple(Gp.apply_perm(perm,oms)), qv))
                if len(data)>=target: break
            if len(data)>=target: break
    return data

PR=2**61-1
def minv(a): return pow(a%PR,PR-2,PR)
def fm(fr): return (fr.numerator%PR)*minv(fr.denominator%PR)%PR

def modrref(rows,rhs,ncol):
    nrow=len(rows); Mx=[rows[i][:]+[rhs[i]] for i in range(nrow)]; piv=[]; r=0
    for c in range(ncol):
        p=next((i for i in range(r,nrow) if Mx[i][c]%PR!=0),None)
        if p is None: continue
        Mx[r],Mx[p]=Mx[p],Mx[r]; iv=minv(Mx[r][c]); Mx[r]=[(x*iv)%PR for x in Mx[r]]
        for i in range(nrow):
            if i!=r and Mx[i][c]%PR!=0:
                f=Mx[i][c]; Mx[i]=[(Mx[i][k]-f*Mx[r][k])%PR for k in range(ncol+1)]
        piv.append(c); r+=1
        if r==nrow: break
    incons=any(Mx[i][ncol]%PR!=0 and all(Mx[i][k]%PR==0 for k in range(ncol)) for i in range(r,nrow))
    return Mx,piv,r,incons

if __name__=="__main__":
    mons=hp_mons(5)
    print("H'-inv deg-5 basis:",len(mons))
    data=harvest()
    print("harvested:",len(data),flush=True)
    rows=[[fm(eval_mon(m,list(o))) for m in mons] for (o,_) in data]
    rhs=[fm(q) for (_,q) in data]
    Mx,piv,rank,incons=modrref(rows,rhs,len(mons))
    print("rank=",rank," #pivots=",len(piv)," CONSISTENT=",not incons)
    # held-out validation: refit on first 80% check last 20%
    n=len(data); ntr=int(n*0.7)
    Mx2,piv2,rank2,inc2=modrref(rows[:ntr],rhs[:ntr],len(mons))
    # build solution vector (pivot cols), eval on held-out
    sol={piv2[i]:Mx2[i][len(mons)] for i in range(len(piv2))}
    ok=True
    for j in range(ntr,n):
        pred=sum(sol.get(c,0)*rows[j][c] for c in range(len(mons)))%PR
        if pred!=rhs[j]: ok=False;break
    print("held-out (70/30) consistent:",ok," train rank",rank2)
