#!/usr/bin/env python3
"""Extract the EXACT (1=2) jump coefficient Q (deg-5, H'-sym, reference wall minus0+plus{3,4}).
Q is defined by: across wall a_1=b_4+b_5, jump N_+ - N_- = (a_1-b_4-b_5)^3 * Q  (k>0 active)."""
from fractions import Fraction as F
import itertools, sympy as sp, random
import r5lib as L, r5_walls as W, r5_group as Gp, chambers_n6 as cn, r5_basis as B
t=W.t
PR=2**61-1
def minv(a): return pow(a%PR,PR-2,PR)
def fm(fr): return (fr.numerator%PR)*minv(fr.denominator%PR)%PR
gdeg=(1,1,1,2,1,2); monsQ=B.hinv_mons(5,gdeg)

def harvest(target=55, seed=21):
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
            for tt in [F(rnd.randint(-60,60),10) for _ in range(8)]:
                oms=cn.solve_squares(L.fc_free(w2,w3,a,b,tt))
                if oms is None or any(w==0 for w in oms): continue
                val=cf.eval(sp.Rational(tt.numerator,tt.denominator))
                data.append((tuple(Gp.apply_perm(perm,oms)),F(sp.Rational(val).p,sp.Rational(val).q)))
                if len(data)>=target: break
            if len(data)>=target: break
    return data

def exact_square_solve(rows,rhs):
    n=len(rows); M=[[F(rows[i][j]) for j in range(n)]+[F(rhs[i])] for i in range(n)]
    for c in range(n):
        p=next((i for i in range(c,n) if M[i][c]!=0),None)
        if p is None: return None
        M[c],M[p]=M[p],M[c]; pv=M[c][c]; M[c]=[x/pv for x in M[c]]
        for i in range(n):
            if i!=c and M[i][c]!=0:
                f=M[i][c]; M[i]=[M[i][k]-f*M[c][k] for k in range(n+1)]
    return [M[i][n] for i in range(n)]

if __name__=="__main__":
    data=harvest(); print("harvested",len(data),flush=True)
    # find pivot columns mod p
    rows=[[fm(B.eval_h(m,list(o),'Q')) for m in monsQ] for (o,_) in data]
    rhs=[fm(q) for (_,q) in data]
    ncol=len(monsQ); nrow=len(rows)
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
    print("rank",r,"pivots",len(piv),flush=True)
    # pick r independent rows (first r that are independent on pivot cols)
    chosen=[]; bm=[]
    for idx in range(nrow):
        rr=[fm(rows[idx][c]) for c in piv]
        for (bp,brow) in bm:
            if rr[bp]!=0:
                f=rr[bp]; rr=[(rr[k]-f*brow[k])%PR for k in range(len(piv))]
        nz=next((k for k in range(len(piv)) if rr[k]!=0),None)
        if nz is not None:
            iv=minv(rr[nz]); rr=[(x*iv)%PR for x in rr]; bm.append((nz,rr)); chosen.append(idx)
        if len(chosen)==len(piv): break
    sub=[[F(rows_orig) for rows_orig in [B.eval_h(monsQ[c],list(data[idx][0]),'Q') for c in piv]] for idx in chosen]
    subrhs=[data[idx][1] for idx in chosen]
    sol=exact_square_solve(sub,subrhs)
    coefs=dict(zip(piv,sol))
    # build Q as sympy in named gens
    x,y,A1,A2,B1,B2=sp.symbols('x y A1 A2 B1 B2')
    gens=[x,y,A1,A2,B1,B2]
    Qexpr=sum(coefs[c]*sp.prod([gens[i]**monsQ[c][i] for i in range(6)]) for c in piv)
    Qexpr=sp.nsimplify(Qexpr)
    print("Q (in x=w1,y=w6,A1=w2+w3,A2=w2w3,B1=w4+w5,B2=w4w5):")
    sp.pprint(sp.expand(Qexpr))
    print()
    print("factored:")
    sp.pprint(sp.factor(Qexpr))
    # verify exactly on held-out data
    def evalQ(o):
        subs={x:o[0],y:o[5],A1:o[1]+o[2],A2:o[1]*o[2],B1:o[3]+o[4],B2:o[3]*o[4]}
        return Qexpr.subs(subs)
    bad=0
    for (o,q) in data:
        if sp.nsimplify(evalQ(o))!=sp.Rational(q.numerator,q.denominator): bad+=1
    print("exact mismatches over",len(data),"harvested pts:",bad)
