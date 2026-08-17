#!/usr/bin/env python3
"""Determine the TRUE order-3 Q-brick cofactor for channel (1;4,6).
For many isolated clean crossings, extract quot(t)=dR/Q^3 (deg-2 poly in t).
Fit G_{1;46} = A w_m^2 + B (w_p^2+w_q^2) + C w_t^2 + D (w_m'^2+w_m''^2)
(homogeneous deg-2, channel-stabilizer symmetric). Solve exactly, validate."""
import itertools
from fractions import Fraction as F
from r5_lines import gen_int_lines, Q_poly, wall_ts, q_mp
from r5_core import (line, Q_T_val, R_spline, poly_interp, poly_eval, poly_sub,
                     poly_divmod, collect, gen_ts, M, P, _fmt)
import numpy as np

def pr(*a): print(*a, flush=True)

CH=(0,3,5)   # (m=1;p=4,q=6)
m,p,q=CH; tleg=4  # omitted plus leg idx4 (leg5); m'=1,2 -> idx1,2

def basis_polys(Pvec,dvec):
    def sqp(idx):
        a,b=F(Pvec[idx]),F(dvec[idx]); return [a*a,2*a*b,b*b]
    def add(*ps):
        n=max(len(x) for x in ps); r=[F(0)]*n
        for x in ps:
            for i,c in enumerate(x): r[i]+=c
        return r
    b1=sqp(m)
    b2=add(sqp(p),sqp(q))
    b3=sqp(tleg)
    b4=add(sqp(1),sqp(2))   # other two minus legs idx1,idx2
    return [b1,b2,b3,b4]

def get_quot(Pvec,dvec):
    """Return list of (t0, quot_coeffs, basis_polys) for isolated clean (1;46) crossings."""
    Qp=Q_poly(Pvec,dvec,m,p,q)
    roots=[r.real for r in np.roots([float(c) for c in Qp][::-1]) if abs(r.imag)<1e-9 and -3<r.real<3]
    if not roots: return []
    cr=wall_ts(Pvec,dvec,-3,3)
    outs=[]
    for t0 in roots:
        others=[c for c in cr if abs(c[0]-t0)>2e-3]
        left=max([c for c in others if c[0]<t0],default=(-3,"lo"),key=lambda c:c[0])
        right=min([c for c in others if c[0]>t0],default=(3,"hi"),key=lambda c:c[0])
        om0=line(Pvec,dvec,F(t0).limit_denominator(10**7))
        # isolation
        bad=False
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
        dR=poly_sub(hi_b,lo_b)
        Qcube=[F(1)]
        for _ in range(3):
            nw=[F(0)]*(len(Qcube)+len(Qp)-1)
            for i,ci in enumerate(Qcube):
                for j,cj in enumerate(Qp): nw[i+j]+=ci*cj
            Qcube=nw
        quot,rem=poly_divmod(dR,Qcube)
        if not all(c==0 for c in rem): continue
        # pad quot to deg2
        quot=(quot+[F(0)]*3)[:3]
        # also record chamber signs at t0 for correlation
        signs=tuple(1 if om0[i]>0 else -1 for i in range(6))
        outs.append((t0, quot, basis_polys(Pvec,dvec), signs, (Pvec,dvec)))
    return outs

# gather samples
lines,_=gen_int_lines()
seen=set(); samples=[]
for Pv,dv in lines:
    k=(tuple(Pv),tuple(dv))
    if k in seen: continue
    seen.add(k)
    # quick: does Q_{1;46} cross zero?
    vals=[Q_T_val(line(Pv,dv,F(tt,2)),m,p,q) for tt in range(-6,7)]
    if not (any(v>0 for v in vals) and any(v<0 for v in vals)): continue
    for s in get_quot(Pv,dv):
        samples.append(s)
    if len(samples)>=10: break

pr(f"collected {len(samples)} isolated clean (1;46) crossings")

# Build exact linear system: A b1 + B b2 + C b3 + D b4 = quot, matching t^0,t^1,t^2
rows=[]; rhs=[]
for (t0,quot,bp,signs,line_) in samples:
    b1,b2,b3,b4=[(x+[F(0)]*3)[:3] for x in bp]
    for k in range(3):
        rows.append([b1[k],b2[k],b3[k],b4[k]]); rhs.append(quot[k])

# exact least-squares via normal equations won't be exact if inconsistent; instead
# solve first 4 independent rows then validate all.
import fractions
def solve_exact(rows,rhs):
    # Gaussian elimination to find a solution of the (overdetermined) system if consistent
    A=[r[:]+[rhs[i]] for i,r in enumerate(rows)]
    n=4; piv=0; where=[-1]*n
    for col in range(n):
        sel=None
        for r in range(piv,len(A)):
            if A[r][col]!=0: sel=r; break
        if sel is None: continue
        A[piv],A[sel]=A[sel],A[piv]
        f=A[piv][col]
        A[piv]=[x/f for x in A[piv]]
        for r in range(len(A)):
            if r!=piv and A[r][col]!=0:
                g=A[r][col]; A[r]=[A[r][j]-g*A[piv][j] for j in range(n+1)]
        where[col]=piv; piv+=1
    sol=[F(0)]*n
    for col in range(n):
        if where[col]!=-1: sol[col]=A[where[col]][n]
    # check consistency
    resid=0
    for i,r in enumerate(rows):
        if sum(r[j]*sol[j] for j in range(n))!=rhs[i]: resid+=1
    return sol,resid

sol,resid=solve_exact(rows,rhs)
pr("fit G = A*wm^2 + B*(wp^2+wq^2) + C*wt^2 + D*(wm'^2+wm''^2)")
pr("  A,B,C,D =", [ _fmt(x) for x in sol])
pr(f"  inconsistent rows (nonzero residual): {resid} / {len(rows)}")
pr("  student-2 claims A=-16, B=C=D=0 (i.e. -16 w_m^2)")
if resid==0:
    pr("  => a SINGLE global cofactor fits ALL sampled chambers.")
else:
    pr("  => NO single stabilizer-symmetric deg-2 cofactor fits: chamber-dependent or richer.")

# report per-sample whether student-2 -16wm^2 matches, and what the true quot is
pr("\nper-sample: quot vs -16 w_m^2 (global):")
for (t0,quot,bp,signs,line_) in samples:
    b1=(bp[0]+[F(0)]*3)[:3]
    match = all(quot[k]==-16*b1[k] for k in range(3))
    pr(f"  P={line_[0]} d={line_[1]} t0={t0:+.3f} signs={signs} quot={[_fmt(c) for c in quot]} "
       f"-16wm2={[_fmt(-16*c) for c in b1]}  s2_match={match}")
