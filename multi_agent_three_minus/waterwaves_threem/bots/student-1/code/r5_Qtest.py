#!/usr/bin/env python3
"""Decisive (1=2) jump consistency test with RELIABLE extraction (span 24, oriented).
Harvest many (ref_oms, Qval) by evaluating coef(t) at many t per crossing; fit deg-5 H'-sym."""
from fractions import Fraction as F
import itertools, sympy as sp, random
import r5lib as L, r5_walls as W, r5_group as Gp, chambers_n6 as cn, r5_basis as B
t=W.t
PR=2**61-1
def minv(a): return pow(a%PR,PR-2,PR)
def fm(fr): return (fr.numerator%PR)*minv(fr.denominator%PR)%PR
gdeg=(1,1,1,2,1,2); monsQ=B.hinv_mons(5,gdeg)
def harvest(target=120, seed=5):
    rnd=random.Random(seed); data=[]; tries=0
    while len(data)<target and tries<400:
        tries+=1
        vals=[F(rnd.randint(-70,70),10) for _ in range(4)]; w2,w3,a,b=vals
        if 0 in vals or len(set(vals))<4: continue
        crs=W.find_crossings(w2,w3,a,b,F(1,40),F(6))
        for (lo,hi,key) in crs:
            if key[0]!='2': continue
            r=W.extract_bracket(w2,w3,a,b,lo,hi,key,F(1,120),24)
            if r[0]=='fitfail' or not r[4]: continue
            kk,jump,kp,coef,isp=r
            i=key[1]; pair=key[2]; perm=Gp.relabel_12_to_ref(i,pair)
            cf=sp.Poly(coef,t)
            for tt in [F(rnd.randint(-60,60),10) for _ in range(10)]:
                oms=cn.solve_squares(L.fc_free(w2,w3,a,b,tt))
                if oms is None or any(w==0 for w in oms): continue
                val=cf.eval(sp.Rational(tt.numerator,tt.denominator))
                qv=F(sp.Rational(val).p,sp.Rational(val).q)
                data.append((tuple(Gp.apply_perm(perm,oms)),qv))
                if len(data)>=target: break
            if len(data)>=target: break
    return data
if __name__=="__main__":
    print("basis deg-5 H'-inv:",len(monsQ),flush=True)
    data=harvest()
    print("harvested:",len(data),flush=True)
    rows=[[fm(B.eval_h(m,list(o),'Q')) for m in monsQ] for (o,_) in data]
    rhs=[fm(q) for (_,q) in data]
    ncol=len(monsQ); nrow=len(rows)
    # full consistency
    Mx=[rows[i][:]+[rhs[i]] for i in range(nrow)]; piv=[]; r=0
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
    print("rank=",r," CONSISTENT(all data)=",not incons,flush=True)
    # held-out
    ntr=int(nrow*0.7)
    M2=[rows[i][:]+[rhs[i]] for i in range(ntr)]; piv2=[]; r2=0
    for c in range(ncol):
        p=next((i for i in range(r2,ntr) if M2[i][c]%PR!=0),None)
        if p is None: continue
        M2[r2],M2[p]=M2[p],M2[r2]; iv=minv(M2[r2][c]); M2[r2]=[(x*iv)%PR for x in M2[r2]]
        for i in range(ntr):
            if i!=r2 and M2[i][c]%PR!=0:
                f=M2[i][c]; M2[i]=[(M2[i][k]-f*M2[r2][k])%PR for k in range(ncol+1)]
        piv2.append(c); r2+=1
        if r2==ntr: break
    sol={piv2[i]:M2[i][ncol] for i in range(len(piv2))}
    ok=all(sum(sol.get(c,0)*rows[j][c] for c in range(ncol))%PR==rhs[j] for j in range(ntr,nrow))
    print("HELD-OUT consistent:",ok," train rank",r2,flush=True)
