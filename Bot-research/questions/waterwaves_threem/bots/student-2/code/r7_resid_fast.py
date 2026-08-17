#!/usr/bin/env python3
"""FAST (parallel) residue characterization: confirm Res_{25}(w2) at fixed survivors
is rational in the merged scale w2 with poles ONLY at the 5 sub-collision loci, i.e.
P(w2) := Res*(w1-w2)(w3-w2)(w2+w4)(w2+w6)(w2+w7) is POLYNOMIAL in w2."""
import sympy as sp, itertools
from fractions import Fraction as F
from par import on_shell_batch
t=sp.Symbol('t'); u=sp.Symbol('u')
def Qr(x): return sp.Rational(x.numerator,x.denominator)
M=(1,2,3);P=(4,5,6,7);n=7;SIG=[-1,-1,-1,1,1,1,1]
MS=[S for r in range(1,n) for S in itertools.combinations(range(1,n+1),r)
    if any(i in M for i in S) and any(i in P for i in S)]
def csig(oms):
    w={i+1:oms[i] for i in range(n)}
    out=[]
    for S in MS:
        k=sum((-1 if i in M else 1)*w[i]**2 for i in S)
        out.append(1 if k>0 else(-1 if k<0 else 0))
    return tuple(out)
def Dfree(oms):
    w={i+1:Qr(oms[i]) for i in range(n)}; D=sp.Integer(1)
    for i in M:
        for j in P: D*=(w[i]+w[j])
    return D

w3,w4,w6t=F(3),F(5),F(11)
step=F(1,40); maxk=46
w2list=[F(7,4),F(15,8),F(2),F(17,8),F(9,4),F(19,8),F(5,2),F(21,8),F(11,4),F(23,8),F(25,8),F(13,4)]
# build all queries
jobs=[]  # (w2_index, tv, free)
for wi,w2 in enumerate(w2list):
    w5base=-w2+F(6,10); w6base=w6t-F(6,10)
    for d in (1,-1):
        for k in range(0 if d==1 else 1,maxk):
            tv=d*step*k
            free=[w2,w3,w4,w5base+tv,w6base-tv]
            if sum(free)==0: continue
            jobs.append((wi,tv,free))
print(f"running {len(jobs)} oracle queries in parallel...")
res=on_shell_batch([(j[2],SIG) for j in jobs],workers=56)
# group by w2
from collections import defaultdict
by=defaultdict(list)
for (wi,tv,free),(im,oms) in zip(jobs,res):
    if im is None: continue
    s=csig(oms)
    if 0 in s: continue
    by[wi].append((tv,im,oms,s))

pts=[]; surv0=None
for wi,w2 in enumerate(w2list):
    raw=sorted(by[wi])
    if not raw: continue
    # take the maximal contiguous-in-tv run sharing the chamber of the smallest |tv| (near wall)
    # group by chamber along sorted tv, then pick the run adjacent to the wall t0=-w2
    s0=min(raw,key=lambda r:abs(r[0]))[3]
    run=[r for r in raw if r[3]==s0]
    if len(run)<30: continue
    xs=[Qr(tv) for tv,_,_,_ in run]
    Nv=[Qr(im)*Dfree(oms) for _,im,oms,_ in run]
    half=len(run)*2//3
    Np=sp.Poly(sp.interpolate(list(zip(xs[:half],Nv[:half])),t),t)
    if not all(Np.eval(xs[i])==Nv[i] for i in range(half,len(run))): continue
    OM={a:sp.Poly(sp.interpolate(list(zip(xs,[Qr(o[a-1]) for _,_,o,_ in run])),t),t) for a in range(1,8)}
    pf=sp.Poly(OM[2].as_expr()+OM[5].as_expr(),t)
    if pf.degree()<1: continue
    t0=sp.Rational(-pf.nth(0),pf.nth(1))
    R=sp.Integer(1)
    for a in M:
        for b in P:
            if (a,b)!=(2,5): R*=sp.Poly(OM[a].as_expr()+OM[b].as_expr(),t).eval(t0)
    Res=sp.Rational(Np.eval(t0))/R
    w={a:F(OM[a].eval(t0)) for a in range(1,8)}
    surv=(w[1],w[3],w[4],w[6],w[7])
    if surv0 is None: surv0=surv
    if surv!=surv0: print(f"  w2={w2}: survivor changed {surv}"); continue
    w1,_,_,w6v,w7=surv
    w2r=Qr(w2)
    fac=(Qr(w1)-w2r)*(sp.Integer(3)-w2r)*(w2r+5)*(w2r+11)*(w2r+Qr(w7))
    Pval=Res*fac
    pts.append((w2r,Pval,Res))
    print(f"  w2={w2}: Res/i={Res}  P={Pval}")

print(f"\nSurvivors (w1,w3,w4,w6,w7)={surv0};  {len(pts)} clean points")
if len(pts)>=6:
    xs=[x for x,_,_ in pts]; ys=[y for _,y,_ in pts]
    half=len(pts)*3//4
    poly=sp.interpolate(list(zip(xs[:half],ys[:half])),u)
    pp=sp.Poly(poly,u)
    ok=all(sp.simplify(pp.eval(xs[i])-ys[i])==0 for i in range(half,len(pts)))
    print(f"\nP(w2) polynomial in merged scale? held-out OK={ok}; degree={pp.degree()}")
    if ok:
        print("=> Res(w2) poles are EXACTLY the 5 sub-collision loci (recursive matching). P(w2):")
        print("  ",sp.factor(poly))
        # also: A5 two-minus of survivors (w2-independent); is Res/A5 clean?
        from r7_residue import two_minus
        wsurv={1:surv0[0],3:surv0[1],4:surv0[2],6:surv0[3],7:surv0[4]}
        A5=F(16)*two_minus((1,3),wsurv,2)
        print(f"\n  A5_2minus(survivors)/i = {A5}")
        print(f"  P(w2)/A5 = {sp.factor(poly/sp.Rational(A5))}")
    else:
        print("held-out FAILED -> chamber changed across w2 range (residue piecewise in w2)")
        for x,y,r in pts: print(f"   w2={x}: P={y}")
