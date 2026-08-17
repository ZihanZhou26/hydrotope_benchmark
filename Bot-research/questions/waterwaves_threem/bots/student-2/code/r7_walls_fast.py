#!/usr/bin/env python3
"""FAST (parallel) single-wall jump exponents at n=7. Tests the unified law:
(1=1)->1; every other mixed subset-sum wall -> n-3 = 4 (incl. NEW (1=3),(2=2))."""
import sympy as sp, itertools
from fractions import Fraction as F
from par import on_shell_batch
t=sp.Symbol('t')
def Qr(x): return sp.Rational(x.numerator,x.denominator)
M=(1,2,3);P=(4,5,6,7);n=7;SIG=[-1,-1,-1,1,1,1,1]
MS=[S for r in range(1,n) for S in itertools.combinations(range(1,n+1),r)
    if any(i in M for i in S) and any(i in P for i in S)]
def csig(oms):
    out=[]
    w={i+1:oms[i] for i in range(n)}
    for S in MS:
        k=sum((-1 if i in M else 1)*w[i]**2 for i in S)
        out.append(1 if k>0 else(-1 if k<0 else 0))
    return tuple(out)
def Dfree(oms):
    w={i+1:Qr(oms[i]) for i in range(n)}; D=sp.Integer(1)
    for i in M:
        for j in P: D*=(w[i]+w[j])
    return D

SLICES=[([F(2),F(3),F(5),F(7),F(11)],F(7),F(11),3,4,"A"),
        ([F(2),F(3),F(5),F(7),F(11)],F(5),F(7),2,3,"B"),
        ([F(3),F(4),F(6),F(9),F(13)],F(9),F(13),3,4,"C"),
        ([F(2),F(5),F(6),F(8),F(15)],F(8),F(15),3,4,"D"),
        ([F(2),F(7,2),F(5),F(8),F(17,2)],F(8),F(17,2),3,4,"E")]
step=F(1,60); maxk=110
jobs=[]
for si,(fixed,va,vb,ia,ib,lab) in enumerate(SLICES):
    for k in range(-maxk,maxk+1):
        tv=step*k
        free=list(fixed); free[ia]=va+tv; free[ib]=vb-tv
        if sum(free)==0: continue
        jobs.append((si,tv,free))
print(f"running {len(jobs)} queries in parallel...")
res=on_shell_batch([(j[2],SIG) for j in jobs],workers=56)
from collections import defaultdict
by=defaultdict(list)
for (si,tv,free),(im,oms) in zip(jobs,res):
    if im is None: continue
    s=csig(oms)
    if 0 in s: continue
    by[si].append((Qr(tv),F(im),oms,s))

seen=set()
for si,(fixed,va,vb,ia,ib,lab) in enumerate(SLICES):
    pts=sorted(by[si])
    if len(pts)<60: continue
    runs=[]; cur=[pts[0]]
    for p in pts[1:]:
        if p[3]==cur[-1][3]: cur.append(p)
        else: runs.append(cur); cur=[p]
    runs.append(cur)
    for a,b in zip(runs,runs[1:]):
        diff=[idx for idx in range(len(MS)) if a[-1][3][idx]!=b[0][3][idx]]
        if len(diff)!=1 or len(a)<25 or len(b)<25: continue
        S=MS[diff[0]]; nm=sum(1 for i in S if i in M); npp=len(S)-nm
        key=(nm,npp)
        def recon(run):
            xs=[x for x,_,_,_ in run]; Nv=[Qr(im)*Dfree(oms) for _,im,oms,_ in run]
            half=len(run)*2//3
            Np=sp.Poly(sp.interpolate(list(zip(xs[:half],Nv[:half])),t),t)
            ok=all(Np.eval(xs[i])==Nv[i] for i in range(half,len(run)))
            return Np,ok
        Na,oka=recon(a); Nb,okb=recon(b)
        if not(oka and okb): continue
        allr=a+b
        OM={leg:sp.Poly(sp.interpolate(list(zip([x for x,_,_,_ in allr],
            [Qr(o[leg-1]) for _,_,o,_ in allr])),t),t) for leg in range(1,8)}
        kS=sp.Poly(sp.expand(sum((-1 if i in M else 1)*OM[i].as_expr()**2 for i in S)),t)
        tb=(a[-1][0]+b[0][0])/2
        rts=[r for r in sp.roots(kS,t,multiple=True) if r.is_real]
        if not rts: continue
        t0=min(rts,key=lambda r:abs(float(r)-float(tb)))
        J=sp.Poly(Na.as_expr()-Nb.as_expr(),t)
        if J.as_expr()==0: continue
        order=0; Jc=J.as_expr()
        while sp.Poly(Jc,t).eval(sp.Rational(t0))==0 and order<12:
            Jc=sp.div(Jc,(t-t0))[0]; order+=1
        tag=f"({nm}={npp})"
        print(f"  slice {lab}: wall S={S} {tag}  exponent = {order}")
        seen.add((key,order))
print("\nSummary (wall type -> exponent):", sorted(seen))
