#!/usr/bin/env python3
"""Faithful native-Python port of bg.cpp (exact Fraction arithmetic).
Validated against ./bg. Cx = (re,im) Fraction tuple. ~10-50x faster than subprocess."""
from fractions import Fraction as F
from functools import lru_cache
from math import factorial
import itertools

def setpartitions(S, k):
    S=tuple(S)
    if k==1: return [[list(S)]]
    if k>len(S): return []
    mn=min(S); X=[x for x in S if x!=mn]; xs=len(X); L=len(S); out=[]
    for mask in range(1<<xs):
        if bin(mask).count('1')> L-k: continue
        fp=[mn]+[X[b] for b in range(xs) if mask&(1<<b)]
        fps=set(fp); fp=sorted(fp)
        rem=[v for v in S if v not in fps]
        if len(rem)>=k-1:
            for sp in setpartitions(rem,k-1):
                out.append([fp]+sp)
    return out

class BG:
    def __init__(self, K, W, G=F(1)):
        # K,W 1-indexed lists length N+1 (index 0 unused)
        self.K=K; self.W=W; self.G=G
        self.Em={}; self.Fm={}; self.BGm={}
    def EKernel(self,n,ps):
        if n==3: return (F(-1)/2)*(abs(ps[0])*abs(ps[1])+ps[0]*ps[1])
        key=(n,ps); v=self.Em.get(key)
        if v is not None: return v
        p1=ps[0]; p2=ps[1]; rest=ps[2:]
        qp2=abs(p2); rs=sum(rest,F(0))
        res=qp2**(n-3)*self.EKernel(3,(p1,p2,rs))/F(factorial(n-2))
        for m in range(1,n-2):
            part=sum(rest[:m],F(0))
            nl=(p1,p2+part)+tuple(rest[m:])
            res=res-qp2**m/F(factorial(m))*self.EKernel(n-m,nl)
        self.Em[key]=res; return res
    def FKernel(self,n,ps):
        if n==3:
            return F(-1)-ps[0]*ps[1]/(abs(ps[0])*abs(ps[1]))
        key=(n,ps); v=self.Fm.get(key)
        if v is not None: return v
        p1=ps[0]; p2=ps[1]; rest=ps[2:]
        qp1=abs(p1); qp2=abs(p2)
        res=F(2)*self.EKernel(n,ps)/qp1
        for m in range(1,n-2):
            part=sum(rest[:m],F(0)); sigM=p2+part
            el=(-sigM,p2)+tuple(rest[:m])
            fl=(p1,sigM)+tuple(rest[m:])
            res=res-F(2)*self.EKernel(m+2,el)*self.FKernel(n-m,fl)
        res=res/qp2; self.Fm[key]=res; return res
    def Vertex(self,n,moms,om):
        acc=F(0)
        for p in itertools.permutations(range(n)):
            pm=tuple(moms[i] for i in p)
            acc=acc+om[p[0]]*om[p[1]]*self.FKernel(n,pm)
        return (F(0), -acc/2)
    def Propagator(self,wS,kS):
        D=wS*wS/abs(kS)-self.G
        return (F(0), F(-1)/D)
    def BGCurrent(self,S):
        if len(S)==1: return (F(1),F(0))
        mask=0
        for i in S: mask|=(1<<i)
        v=self.BGm.get(mask)
        if v is not None: return v
        wS=sum(self.W[i] for i in S); kS=sum(self.K[i] for i in S)
        res=(F(0),F(0))
        for m in range(2,len(S)+1):
            for part in setpartitions(S,m):
                vM=[-kS]; vO=[-wS]
                for blk in part:
                    vM.append(sum(self.K[i] for i in blk)); vO.append(sum(self.W[i] for i in blk))
                vx=self.Vertex(m+1,vM,vO)
                prod=(F(1),F(0))
                for blk in part:
                    bc=self.BGCurrent(blk)
                    prod=(prod[0]*bc[0]-prod[1]*bc[1], prod[0]*bc[1]+prod[1]*bc[0])
                res=(res[0]+vx[0]*prod[0]-vx[1]*prod[1], res[1]+vx[0]*prod[1]+vx[1]*prod[0])
        pr=self.Propagator(wS,kS)
        res=(res[0]*pr[0]-res[1]*pr[1], res[0]*pr[1]+res[1]*pr[0])
        self.BGm[mask]=res; return res
    def amplitude(self,N):
        self.BGm={}; self.Em={}; self.Fm={}
        rest=list(range(2,N+1))
        res=(F(0),F(0))
        for m in range(2,N):
            for part in setpartitions(rest,m):
                vM=[self.K[1]]; vO=[self.W[1]]
                for blk in part:
                    vM.append(sum(self.K[i] for i in blk)); vO.append(sum(self.W[i] for i in blk))
                vx=self.Vertex(m+1,vM,vO)
                prod=(F(1),F(0))
                for blk in part:
                    bc=self.BGCurrent(blk)
                    prod=(prod[0]*bc[0]-prod[1]*bc[1], prod[0]*bc[1]+prod[1]*bc[0])
                res=(res[0]+vx[0]*prod[0]-vx[1]*prod[1], res[1]+vx[0]*prod[1]+vx[1]*prod[0])
        return res

def amp_onshell(free, signs, g=F(1)):
    """free = n-2 free freqs (legs 2..n-1). signs length n. Returns (im, oms)."""
    free=[F(x) for x in free]; signs=[F(s) for s in signs]; N=len(signs)
    s1=signs[0]; sumFree=sum(free); 
    sumSig=sum(signs[i+1]*free[i]*free[i] for i in range(N-2))
    wn=-(s1*sumFree*sumFree+sumSig)/(2*s1*sumFree)
    w1=-(sumFree+wn)
    W=[F(0)]*(N+1); K=[F(0)]*(N+1)
    W[1]=w1
    for i in range(N-2): W[i+2]=free[i]
    W[N]=wn
    for i in range(1,N+1): K[i]=signs[i-1]*W[i]*W[i]/g
    bg=BG(K,W,g); re,im=bg.amplitude(N)
    return im, [W[i] for i in range(1,N+1)], re

def amp_raw(K,W,g=F(1)):
    K=[F(x) for x in K]; W=[F(x) for x in W]; N=len(W)
    Kf=[F(0)]+K; Wf=[F(0)]+W
    bg=BG(Kf,Wf,g); return bg.amplitude(N)

if __name__=="__main__":
    import time, harness as h
    # validate vs ./bg at several points, n=5,6,7
    tests=[([2,3,5],[-1,-1,-1,1,1]),([2,3,5,7],[-1,-1,-1,1,1,1]),
           ([F(2),F(7,2),F(5),F(13,2),F(3)],[-1,-1,-1,1,1,1,1]),
           ([F(11,3),F(-7,2),F(9,5),F(13,4)],[-1,-1,-1,1,1,1])]
    allok=True
    for free,sig in tests:
        im,oms,re=amp_onshell(free,sig)
        imo,omso,reo=h.on_shell(free,sig)
        ok=(im==imo and re==reo)
        allok=allok and ok
        print(f"n={len(sig)} free={free}: pybg im={im}  ./bg im={imo}  match={ok}")
    print("ALL MATCH:",allok)
    t0=time.time()
    for _ in range(20): amp_onshell([2,3,5,7],[-1,-1,-1,1,1,1])
    print("pybg n=6 x20:",round(time.time()-t0,3),"s")
