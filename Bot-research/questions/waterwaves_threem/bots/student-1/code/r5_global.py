#!/usr/bin/env python3
"""GLOBAL truncated-power fit:  N = Base + sum_(1=1)|k_ij| Pi + sum_(1=2)|k_ijk|^3 Xi.
Columns = G-orbit-sums of |k_ref|^p * template; base = G-sym odd deg-11 invariants.
Test: is N in the column span? (consistent + held-out) -> simple form holds; then fit exact."""
from fractions import Fraction as F
import itertools, random, sys
import chambers_n6 as cn, r5lib as L, r5_group as Gp, harness as h, r5_basis as B
SIG=[-1,-1,-1,1,1,1]
PR=2**61-1
def minv(a): return pow(a%PR,PR-2,PR)
def fm(fr): return (fr.numerator%PR)*minv(fr.denominator%PR)%PR
G=Gp.full_group()

# ---- base: G-sym odd weighted-deg-11 invariant classes in (e1,e2,e3m,e3p) ----
def base_classes():
    cl=[]
    for a in range(0,12):
     for b in range(0,7):
      for c in range(0,4):
       for d in range(0,4):
        if a+2*b+3*c+3*d==11 and (a+c+d)%2==1:
         cl.append((a,b,c,d))
    seen=set(); out=[]
    for m in cl:
        a,b,c,d=m; mm=(a,b,d,c); key=tuple(sorted([m,mm]))
        if key in seen: continue
        seen.add(key)
        if mm==m and a%2==1: continue
        out.append(m)
    return out
def eval_base(cls, oms):
    e1=oms[3]+oms[4]+oms[5]
    e2=oms[3]*oms[4]+oms[3]*oms[5]+oms[4]*oms[5]
    e3m=oms[0]*oms[1]*oms[2]; e3p=oms[3]*oms[4]*oms[5]
    a,b,c,d=cls
    # Z2-symmetrized: e1^a e2^b (e3m^c e3p^d + (-1)^a e3m^d e3p^c)
    v1=(e1**a)*(e2**b)*(e3m**c)*(e3p**d)
    v2=((-1)**a)*(e1**a)*(e2**b)*(e3m**d)*(e3p**c)
    return v1+v2

# reference wall functions
def kref1(oms): return abs(oms[3]**2-oms[0]**2)          # |b3-a0|, (1=1) ref minus0,plus3
def kref2(oms): return abs(oms[0]**2-oms[3]**2-oms[4]**2) # |a0-b3-b4|, (1=2) ref minus0,plus{3,4}

def precompute_point(oms):
    """return list over G of (relabeled oms, kref1 val, kref2^3 val) all mod PR-ready (Fractions)."""
    out=[]
    for perm in G:
        ro=Gp.apply_perm(perm,oms)
        out.append((ro, kref1(ro), kref2(ro)**3))
    return out

def columns_for_point(oms, baseC, tmplP, tmplQ):
    gp=precompute_point(oms)
    cols=[]
    # base
    for cl in baseC: cols.append(eval_base(cl,oms))
    # (1=1)
    for m in tmplP:
        s=F(0)
        for (ro,w1,w2) in gp: s+= w1*B.eval_h(m,ro,'P')
        cols.append(s)
    # (1=2)
    for m in tmplQ:
        s=F(0)
        for (ro,w1,w2) in gp: s+= w2*B.eval_h(m,ro,'Q')
        cols.append(s)
    return cols

def Nval_oracle(oms, free):
    im,_,_=h.on_shell(free,SIG)
    e1=oms[3]+oms[4]+oms[5]  # not used
    from inv import invariants
    e=invariants(oms)
    return F(im*(e[2]+e[3]),32)

if __name__=="__main__":
    baseC=base_classes(); print("base classes:",len(baseC),flush=True)
    gdeg=(1,1,1,2,1,2)
    monsP=B.hinv_mons(9,gdeg); monsQ=B.hinv_mons(5,gdeg)
    tmplP,_=B.independent_subset(monsP,'P'); tmplQ,_=B.independent_subset(monsQ,'Q')
    print("templates: P",len(tmplP)," Q",len(tmplQ),flush=True)
    ncol=len(baseC)+len(tmplP)+len(tmplQ); print("total columns:",ncol,flush=True)
    # sample oracle points
    npts=ncol+60; rnd=random.Random(99); data=[]
    while len(data)<npts:
        free=[F(rnd.randint(-90,90),10) for _ in range(4)]
        if 0 in free: continue
        oms=cn.solve_squares(free)
        if oms is None or any(w==0 for w in oms): continue
        try: nv=Nval_oracle(oms,free)
        except Exception: continue
        data.append((oms,free,nv))
        if len(data)%50==0: print("  collected",len(data),flush=True)
    print("collected oracle points:",len(data),flush=True)
    # build modular system
    rows=[]; rhs=[]
    for (oms,free,nv) in data:
        cols=columns_for_point(oms,baseC,tmplP,tmplQ)
        rows.append([fm(c) for c in cols]); rhs.append(fm(nv))
    # RREF mod PR, consistency
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
    print("rank=",r," #pivots=",len(piv)," CONSISTENT=",not incons,flush=True)
    # held-out 75/25
    n=len(data); ntr=int(n*0.78)
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
    ok=True
    for j in range(ntr,n):
        pred=sum(sol.get(c,0)*rows[j][c] for c in range(ncol))%PR
        if pred!=rhs[j]: ok=False; break
    print("HELD-OUT consistent:",ok," (train rank",r2,")",flush=True)
