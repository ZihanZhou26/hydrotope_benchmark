#!/usr/bin/env python3
"""Decisive simple-vs-box test on M=N-corr12 (only (1=1) kinks left).
Fit M = base(12) + sum_{9 (1=1) walls} |k_ij| * P_ij  (S3xS3 orbit-sum, NO Z2 collapse).
Columns: base + {Phi_m = sum_{i in M,j in P} |w_j^2-w_i^2| * m(relabel_11(i,j) o) : m deg-9 H-inv}."""
from fractions import Fraction as F
import random, itertools
import chambers_n6 as cn, r5lib as L, r5_group as Gp, r5_basis as B, r5_corr as C, fastbg as FB, inv
PR=2**61-1
def minv(a): return pow(a%PR,PR-2,PR)
def fm(fr): return (fr.numerator%PR)*minv(fr.denominator%PR)%PR
M=[0,1,2]; P=[3,4,5]
gdeg=(1,1,1,2,1,2)
monsP,_=B.independent_subset(B.hinv_mons(9,gdeg),'P')   # 125 independent templates
baseC=__import__('r5_global').base_classes()
import r5_global as G2
W11=[(i,j) for i in M for j in P]
PERM11={(i,j):Gp.relabel_11_to_ref(i,j) for (i,j) in W11}

def phi11(m, o):
    s=F(0)
    for (i,j) in W11:
        k=abs(o[j]**2-o[i]**2)
        if k!=0:
            ro=Gp.apply_perm(PERM11[(i,j)],o)
            s+= k*B.eval_h(m,ro,'P')
    return s

def cols(o):
    c=[G2.eval_base(cl,o) for cl in baseC]
    for m in monsP: c.append(phi11(m,o))
    return c

if __name__=="__main__":
    ncol=len(baseC)+len(monsP); print("columns:",ncol,"(base",len(baseC),"+ (1=1)",len(monsP),")",flush=True)
    npts=ncol+50; rnd=random.Random(7); data=[]
    # collect oracle N in batches
    pending=[]
    while len(data)<npts:
        free=[F(rnd.randint(-90,90),10) for _ in range(4)]
        if 0 in free: continue
        o=cn.solve_squares(free)
        if o is None or any(w==0 for w in o): continue
        pending.append((free,o))
        if len(pending)>=60 or len(data)+len(pending)>=npts:
            res=FB.batch_onshell([(6,fr,[-1,-1,-1,1,1,1]) for (fr,_) in pending])
            for (fr,o),r in zip(pending,res):
                if r is None: continue
                e=inv.invariants(o); Nv=F(r[1]*(e[2]+e[3]),32)
                Mv=Nv - C.corr12(o)
                data.append((o,Mv))
            pending=[]
        if len(data)%60<2: print("  data",len(data),flush=True)
    print("collected",len(data),flush=True)
    rows=[[fm(x) for x in cols(o)] for (o,_) in data]
    rhs=[fm(mv) for (_,mv) in data]
    nrow=len(rows)
    def rref(rws,rh,nr):
        Mx=[rws[i][:]+[rh[i]] for i in range(nr)]; piv=[]; r=0
        for c in range(ncol):
            p=next((i for i in range(r,nr) if Mx[i][c]%PR!=0),None)
            if p is None: continue
            Mx[r],Mx[p]=Mx[p],Mx[r]; iv=minv(Mx[r][c]); Mx[r]=[(x*iv)%PR for x in Mx[r]]
            for i in range(nr):
                if i!=r and Mx[i][c]%PR!=0:
                    f=Mx[i][c]; Mx[i]=[(Mx[i][k]-f*Mx[r][k])%PR for k in range(ncol+1)]
            piv.append(c); r+=1
            if r==nr: break
        incons=any(Mx[i][ncol]%PR!=0 and all(Mx[i][k]%PR==0 for k in range(ncol)) for i in range(r,nr))
        return Mx,piv,r,incons
    _,piv,r,incons=rref(rows,rhs,nrow)
    print("rank",r,"CONSISTENT(all)=",not incons,flush=True)
    ntr=int(nrow*0.8)
    M2,piv2,r2,_=rref(rows[:ntr],rhs[:ntr],ntr)
    sol={piv2[i]:M2[i][ncol] for i in range(len(piv2))}
    ok=all(sum(sol.get(c,0)*rows[j][c] for c in range(ncol))%PR==rhs[j] for j in range(ntr,nrow))
    print("HELD-OUT consistent:",ok," train rank",r2,flush=True)
