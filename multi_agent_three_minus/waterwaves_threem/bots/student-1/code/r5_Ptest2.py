#!/usr/bin/env python3
"""(1=1) jump consistency via TARGETED slices (plus crosses minus) + batched oracle.
P = (1=1) jump coefficient (deg-9 H-sym). corr12 is (1=1)-smooth so P from N = P from M."""
from fractions import Fraction as F
import sympy as sp, random
import r5lib as L, r5_walls as W, r5_group as Gp, chambers_n6 as cn, r5_basis as B
t=W.t
PR=2**61-1
def minv(a): return pow(a%PR,PR-2,PR)
def fm(fr): return (fr.numerator%PR)*minv(fr.denominator%PR)%PR
gdeg=(1,1,1,2,1,2); monsP=B.hinv_mons(9,gdeg)

def harvest(target=200, seed=3):
    rnd=random.Random(seed); data=[]; tries=0
    while len(data)<target and tries<600:
        tries+=1
        # targeted: choose w2 (minus) and set a (=w4 center) near w2 so w4 crosses w2
        w2=F(rnd.randint(20,65),10); w3=F(rnd.randint(-60,60),10)
        a=w2+F(rnd.randint(-15,15),10)   # w4 center near w2 -> crossing in range
        b=F(rnd.randint(-60,60),10)
        if 0 in (w2,w3,a,b) or len({w2,w3,a,b})<4: continue
        crs=W.find_crossings(w2,w3,a,b,F(1,50),F(5))
        for (lo,hi,key) in crs:
            if key[0]!='1': continue
            r=W.extract_bracket(w2,w3,a,b,lo,hi,key,F(1,110),24)
            if r[0]=='fitfail' or not r[4]: continue
            kk,jump,kp,coef,isp=r
            i=key[1]; j=key[2]; perm=Gp.relabel_11_to_ref(i,j)
            cf=sp.Poly(coef,t)
            for tt in [F(rnd.randint(-55,55),10) for _ in range(9)]:
                o=cn.solve_squares(L.fc_free(w2,w3,a,b,tt))
                if o is None or any(w==0 for w in o): continue
                val=cf.eval(sp.Rational(tt.numerator,tt.denominator))
                data.append((tuple(Gp.apply_perm(perm,o)),F(sp.Rational(val).p,sp.Rational(val).q)))
                if len(data)>=target: break
            if len(data)>=target: break
        if tries%30==0: print("  tries",tries,"data",len(data),flush=True)
    return data
if __name__=="__main__":
    print("deg-9 H-inv basis:",len(monsP),flush=True)
    data=harvest()
    print("harvested:",len(data),flush=True)
    rows=[[fm(B.eval_h(m,list(o),'P')) for m in monsP] for (o,_) in data]
    rhs=[fm(p) for (_,p) in data]
    ncol=len(monsP); nrow=len(rows)
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
    print("rank=",r," CONSISTENT(all)=",not incons,flush=True)
    ntr=int(nrow*0.72)
    M2,piv2,r2,_=rref(rows[:ntr],rhs[:ntr],ntr)
    sol={piv2[i]:M2[i][ncol] for i in range(len(piv2))}
    ok=all(sum(sol.get(c,0)*rows[j][c] for c in range(ncol))%PR==rhs[j] for j in range(ntr,nrow))
    print("HELD-OUT consistent:",ok," train rank",r2,flush=True)
