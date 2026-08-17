#!/usr/bin/env python3
"""FAST modular confirmation that Res_{25}(merged scale w2) at fixed survivors has
poles ONLY at the 5 sub-collision loci, i.e. P(w2)=Res*(w1-w2)(w3-w2)(w2+w4)(w2+w6)
(w2+w7) is POLYNOMIAL in w2. All slice reconstruction done mod a large prime to
avoid the huge-rational blow-up (oracle values exact, reduced mod p)."""
import itertools
from fractions import Fraction as F
from par import on_shell_batch
PMOD=(1<<61)-1
def red(fr): return (fr.numerator % PMOD)*pow(fr.denominator % PMOD,PMOD-2,PMOD)%PMOD
def lag_eval(xs,ys,xq):
    # Lagrange interpolation value at xq, mod PMOD
    s=0
    for i in range(len(xs)):
        num=ys[i]%PMOD; den=1
        for j in range(len(xs)):
            if j==i: continue
            num=num*((xq-xs[j])%PMOD)%PMOD
            den=den*((xs[i]-xs[j])%PMOD)%PMOD
        s=(s+num*pow(den,PMOD-2,PMOD))%PMOD
    return s
def poly_degree(xs,ys):
    # minimal d s.t. degree-d interpolation (first d+1 pts) predicts ALL pts
    for d in range(0,len(xs)-1):
        ok=all(lag_eval(xs[:d+1],ys[:d+1],xs[k])==ys[k]%PMOD for k in range(d+1,len(xs)))
        if ok: return d
    return None

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

w3,w4,w6t=F(3),F(5),F(11)
step=F(1,40); maxk=46
w2list=[F(7,4)+F(i,8) for i in range(0,11)]  # 1.75 .. 3.0 step 1/8 (skip exact 3)
w2list=[x for x in w2list if x!=F(3)]
jobs=[]
for wi,w2 in enumerate(w2list):
    w5base=-w2+F(6,10); w6base=w6t-F(6,10)
    for d in (1,-1):
        for k in range(0 if d==1 else 1,maxk):
            tv=d*step*k; free=[w2,w3,w4,w5base+tv,w6base-tv]
            if sum(free)==0: continue
            jobs.append((wi,tv,free))
print(f"{len(jobs)} oracle queries (parallel)...")
res=on_shell_batch([(j[2],SIG) for j in jobs],workers=56)
from collections import defaultdict
by=defaultdict(list)
for (wi,tv,free),(im,oms) in zip(jobs,res):
    if im is None: continue
    s=csig(oms)
    if 0 in s: continue
    by[wi].append((F(tv),im,oms,s))

pts=[]; surv0=None
for wi,w2 in enumerate(w2list):
    raw=sorted(by[wi],key=lambda r:r[0])
    if not raw: continue
    s0=min(raw,key=lambda r:abs(r[0]))[3]
    run=[r for r in raw if r[3]==s0]
    if len(run)<32: continue
    # mod-p reconstruct N_full(t)=A*Dfree and omega_a(t); eval at wall t0 (w2+w5=0)
    xs=[red(tv) for tv,_,_,_ in run]
    def Dfree_red(oms):
        w={i+1:oms[i] for i in range(n)}; D=1
        for i in M:
            for j in P: D=D*red(w[i]+w[j])%PMOD
        return D
    Nv=[red(im)*Dfree_red(oms)%PMOD for _,im,oms,_ in run]
    OMv={a:[red(o[a-1]) for _,_,o,_ in run] for a in range(1,8)}
    # find t0 exactly (rational): w2+w5(t)=0. w5=run's varying leg; get its exact value vs tv
    # w5 = w5base + tv ; wall at tv where w2+w5base+tv=0 -> tv0 = -(w2+w5base)= -(w2 + (-w2+0.6)) = -0.6
    tv0=F(-6,10)
    x0=red(tv0)
    N0=lag_eval(xs,Nv,x0)
    om0={a:lag_eval(xs,OMv[a],x0) for a in range(1,8)}
    # Res = N0 / prod_{(a,b)!=(2,5)}(wa+wb)  mod p
    R=1
    for a in M:
        for b in P:
            if (a,b)!=(2,5): R=R*((om0[a]+om0[b])%PMOD)%PMOD
    Res=N0*pow(R,PMOD-2,PMOD)%PMOD
    # exact survivor values (from one run point extrapolated exactly? use rational solve at tv0)
    import harness as h
    free0=[w2,w3,w4,(-w2+F(6,10))+tv0,(w6t-F(6,10))-tv0]
    oms0=h.solve_legs_1n([str(x) for x in free0],SIG)
    surv=(oms0[0],oms0[2],oms0[3],oms0[5],oms0[6])
    if surv0 is None: surv0=surv
    w1,_,_,w6v,w7=surv
    fac=red((w1-w2)*(F(3)-w2)*(w2+w4)*(w2+w6v)*(w2+w7))
    Pv=Res*fac%PMOD
    pts.append((red(w2),Pv,w2,Res))

print(f"survivors {surv0}; {len(pts)} points")
xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
d=poly_degree(xs,ys)
print(f"\nP(w2) [= Res * 5 sub-collision factors]: minimal polynomial degree (mod p) = {d}")
if d is not None and d<len(xs)-2:
    print(f"=> P(w2) is a POLYNOMIAL of degree {d} -> Res(w2)'s ONLY merged-scale poles are")
    print(f"   the 5 sub-collision loci (a 2nd mixed pair vanishes). Recursive matching CONFIRMED.")
else:
    print("=> NOT low-degree polynomial in this w2-range (chamber may change -> piecewise).")
# also show Res raw at each w2 (mod p is opaque; print w2 + that Res is finite)
for x,Pv,w2,Res in pts: print(f"   w2={w2}: Res(mod p)={Res}")
