#!/usr/bin/env python3
"""Test whether a SINGLE global homogeneous degree-2 cofactor G_{1;46}(omega)
(channel-stabilizer symmetric, full basis incl. cross terms) reproduces the
extracted quot(t) across MANY isolated crossings through DIFFERENT base points.
Fit exactly on part, validate on held-out lines."""
import itertools
from fractions import Fraction as F
from r5_lines import Q_poly, wall_ts
from r5_core import (line, Q_T_val, R_spline, poly_interp, poly_eval, poly_sub,
                     poly_divmod, collect, gen_ts, M, P, _fmt)
import numpy as np

def pr(*a): print(*a, flush=True)
SIGv=[-1,-1,-1,1,1,1]
CH=(0,3,5); m,p,q=CH; tleg=4  # (1;4,6), omitted plus leg5; m',m'' = legs 2,3

BASES=[[8,2,-3,-5,4,-6],[9,-7,1,-8,6,-1],[7,-5,-2,-6,3,3],[10,-1,-6,-9,7,-1],
       [11,-4,-2,-9,-1,5],[12,-3,-4,-11,2,4],[6,6,-3,-2,-8,1],[5,-5,4,-8,7,-3]]
BASES=[b for b in BASES if sum(b)==0 and sum(SIGv[i]*b[i]**2 for i in range(6))==0]

def null_dirs(bound=3):
    ds=[]
    for d in itertools.product(range(-bound,bound+1),repeat=6):
        if sum(d)!=0: continue
        if sum(SIGv[i]*d[i]*d[i] for i in range(6))!=0: continue
        if all(x==0 for x in d): continue
        ds.append(d)
    return ds
DIRS=null_dirs()

def line_poly_omega(Pvec,dvec,idx):
    return [F(Pvec[idx]),F(dvec[idx])]
def mul(a,b):
    r=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): r[i+j]+=x*y
    return r
def add(*ps):
    n=max(len(x) for x in ps); r=[F(0)]*n
    for x in ps:
        for i,c in enumerate(x): r[i]+=c
    return r

def basis12(Pvec,dvec):
    w=lambda i: line_poly_omega(Pvec,dvec,i)
    w1,w2,w3,w4,w5,w6=[w(i) for i in range(6)]
    B=[
      mul(w1,w1),                       # wm^2
      mul(w5,w5),                       # wt^2
      mul(w1,w5),                       # wm wt
      add(mul(w4,w4),mul(w6,w6)),       # wp^2+wq^2
      mul(w4,w6),                       # wp wq
      add(mul(w2,w2),mul(w3,w3)),       # wm'^2+wm''^2
      mul(w2,w3),                       # wm' wm''
      mul(w1,add(w4,w6)),               # wm(wp+wq)
      mul(w1,add(w2,w3)),               # wm(wm'+wm'')
      mul(w5,add(w4,w6)),               # wt(wp+wq)
      mul(w5,add(w2,w3)),               # wt(wm'+wm'')
      mul(add(w4,w6),add(w2,w3)),       # (wp+wq)(wm'+wm'')
    ]
    return [ (b+[F(0)]*3)[:3] for b in B ]

def get_quots(Pvec,dvec):
    Qp=Q_poly(Pvec,dvec,m,p,q)
    roots=[r.real for r in np.roots([float(c) for c in Qp][::-1]) if abs(r.imag)<1e-9 and -2.5<r.real<2.5]
    if not roots: return []
    cr=wall_ts(Pvec,dvec,-3,3); outs=[]
    for t0 in roots:
        others=[c for c in cr if abs(c[0]-t0)>2e-3]
        left=max([c for c in others if c[0]<t0],default=(-3,"lo"),key=lambda c:c[0])
        right=min([c for c in others if c[0]>t0],default=(3,"hi"),key=lambda c:c[0])
        om0=line(Pvec,dvec,F(t0).limit_denominator(10**7)); bad=False
        for mm in M:
            for pp in P:
                if abs(float(om0[pp]**2-om0[mm]**2))<1e-2: bad=True
        for mm in M:
            for pp,qq in itertools.combinations(P,2):
                if (mm,pp,qq)!=(m,p,q) and abs(float(Q_T_val(om0,mm,pp,qq)))<1e-2: bad=True
        if bad: continue
        Lwin=(left[0]+1e-3,t0-1e-3); Rwin=(t0+1e-3,right[0]-1e-3)
        if Lwin[1]-Lwin[0]<0.05 or Rwin[1]-Rwin[0]<0.05: continue
        Lts=gen_ts(F(Lwin[0]).limit_denominator(10**6),F(Lwin[1]).limit_denominator(10**6),13,den=7919)
        Rts=gen_ts(F(Rwin[0]).limit_denominator(10**6),F(Rwin[1]).limit_denominator(10**6),13,den=7919)
        xL,yL=collect(R_spline,Pvec,dvec,Lts); xR,yR=collect(R_spline,Pvec,dvec,Rts)
        if len(xL)<9 or len(xR)<9: continue
        cL=poly_interp(xL[:9],yL[:9]); cR=poly_interp(xR[:9],yR[:9])
        if sum(1 for x,y in zip(xL[9:],yL[9:]) if poly_eval(cL,x)!=y): continue
        if sum(1 for x,y in zip(xR[9:],yR[9:]) if poly_eval(cR,x)!=y): continue
        Qmid=poly_eval(Qp,F(xR[0])); hi_b,lo_b=(cR,cL) if Qmid>0 else (cL,cR)
        dR=poly_sub(hi_b,lo_b); Qcube=[F(1)]
        for _ in range(3): Qcube=mul(Qcube,Qp)
        quot,rem=poly_divmod(dR,Qcube)
        if not all(c==0 for c in rem): continue
        quot=(quot+[F(0)]*3)[:3]
        outs.append((Pvec,dvec,t0,quot,basis12(Pvec,dvec)))
    return outs

# collect samples across bases
samples=[]
for Pv in BASES:
    got=0
    for d in DIRS:
        if sum(SIGv[i]*Pv[i]*d[i] for i in range(6))!=0: continue
        vals=[Q_T_val(line(Pv,d,F(tt,2)),m,p,q) for tt in range(-5,6)]
        if not (any(v>0 for v in vals) and any(v<0 for v in vals)): continue
        for s in get_quots(Pv,list(d)):
            samples.append(s); got+=1
        if got>=4: break
    pr(f"base {Pv}: collected {got}")
pr(f"TOTAL samples {len(samples)}")

# split fit / holdout
fit=samples[:len(samples)*2//3]; hold=samples[len(samples)*2//3:]
rows=[]; rhs=[]
for (Pv,dv,t0,quot,B) in fit:
    for k in range(3):
        rows.append([B[j][k] for j in range(12)]); rhs.append(quot[k])

def gauss(rows,rhs,n):
    A=[r[:]+[rhs[i]] for i,r in enumerate(rows)]; piv=0; where=[-1]*n
    for col in range(n):
        sel=None
        for r in range(piv,len(A)):
            if A[r][col]!=0: sel=r; break
        if sel is None: continue
        A[piv],A[sel]=A[sel],A[piv]; f=A[piv][col]; A[piv]=[x/f for x in A[piv]]
        for r in range(len(A)):
            if r!=piv and A[r][col]!=0:
                g=A[r][col]; A[r]=[A[r][j]-g*A[piv][j] for j in range(n+1)]
        where[col]=piv; piv+=1
    sol=[F(0)]*n
    for col in range(n):
        if where[col]!=-1: sol[col]=A[where[col]][n]
    resid=sum(1 for i,r in enumerate(rows) if sum(r[j]*sol[j] for j in range(n))!=rhs[i])
    return sol,resid,piv

sol,resid,rank=gauss(rows,rhs,12)
names=["wm^2","wt^2","wm*wt","wp^2+wq^2","wp*wq","wm'^2+wm''^2","wm'*wm''",
       "wm(wp+wq)","wm(wm'+wm'')","wt(wp+wq)","wt(wm'+wm'')","(wp+wq)(wm'+wm'')"]
pr(f"\nfit rank={rank}/12, inconsistent fit rows={resid}/{len(rows)}")
if resid==0:
    pr("solution (one representative; basis is on-shell-degenerate so not unique):")
    for nm,c in zip(names,sol):
        if c!=0: pr(f"   {nm}: {_fmt(c)}")
    # validate on holdouts
    hbad=0; htot=0
    for (Pv,dv,t0,quot,B) in hold:
        for k in range(3):
            pred=sum(B[j][k]*sol[j] for j in range(12)); htot+=1
            if pred!=quot[k]: hbad+=1
    pr(f"HOLDOUT: {hbad}/{htot} mismatches over {len(hold)} held-out lines")
    if hbad==0:
        pr("=> a SINGLE global degree-2 cofactor G_{1;46} EXISTS and reproduces all jumps.")
        pr("   student-2's -16 w_m^2 is a DIFFERENT deg-2 form (agrees only on the wall variety / special cells).")
else:
    pr("=> even the full 12-dim symmetric deg-2 basis is INCONSISTENT: no global deg-2 cofactor.")
