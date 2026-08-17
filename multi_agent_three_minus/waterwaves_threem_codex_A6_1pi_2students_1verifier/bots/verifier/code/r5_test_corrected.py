#!/usr/bin/env python3
"""Decisive: compare student-2's R_Q (G=-16max) against the corrected hypothesis
R_Q2 (G=-32 w_m w_t) via smoothness of R_spline - R_Q across isolated Q walls,
over many channels/chambers/lines. Also verify per-channel cofactor = -32 w_m w_t."""
import itertools
from fractions import Fraction as F
from r5_lines import gen_int_lines, Q_poly, wall_ts
from r5_core import (line, Q_T_val, R_spline, R_Q, pos, poly_interp, poly_eval,
                     poly_sub, poly_divmod, collect, gen_ts, M, P, _fmt)
import numpy as np

def pr(*a): print(*a, flush=True)
SIGv=[-1,-1,-1,1,1,1]

def R_Q2(omega):
    """corrected orbit: -32 sum_{m,p<q} (Q_{m;pq})_+^3 * w_m * w_t (t=omitted plus)."""
    omega=[F(w) for w in omega]; tot=F(0)
    for m in M:
        for p,q in itertools.combinations(P,2):
            t=[x for x in P if x not in (p,q)][0]
            Q=omega[p]**2+omega[q]**2-omega[m]**2
            if Q>0: tot+=Q**3*omega[m]*omega[t]
    return -32*tot

def clean_windows(Pvec,dvec,m,p,q):
    Qp=Q_poly(Pvec,dvec,m,p,q)
    roots=[r.real for r in np.roots([float(c) for c in Qp][::-1]) if abs(r.imag)<1e-9 and -2.5<r.real<2.5]
    if not roots: return []
    cr=wall_ts(Pvec,dvec,-3,3); out=[]
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
        out.append((t0,Lwin,Rwin,om0))
    return out

def smooth_bad(func,Pvec,dvec,Lwin,Rwin):
    Lts=gen_ts(F(Lwin[0]).limit_denominator(10**6),F(Lwin[1]).limit_denominator(10**6),10,den=7919)
    Rts=gen_ts(F(Rwin[0]).limit_denominator(10**6),F(Rwin[1]).limit_denominator(10**6),10,den=7919)
    xA,yA=collect(func,Pvec,dvec,Lts+Rts)
    if len(xA)<12: return None
    c=poly_interp(xA[:9],yA[:9])
    return sum(1 for x,y in zip(xA,yA) if poly_eval(c,x)!=y)

lines,_=gen_int_lines()
seen=set()
tested=0; s2_fail=0; v_fail=0; chambers=set(); channels=set()
def RmQ_s2(om): return R_spline(om)-R_Q(om)
def RmQ_v(om):  return R_spline(om)-R_Q2(om)

for Pv,dv in lines:
    k=(tuple(Pv),tuple(dv))
    if k in seen: continue
    seen.add(k)
    if tested>=24: break
    for m in M:
        for p,q in itertools.combinations(P,2):
            vals=[Q_T_val(line(Pv,dv,F(tt,2)),m,p,q) for tt in range(-5,6)]
            if not (any(v>0 for v in vals) and any(v<0 for v in vals)): continue
            for (t0,Lwin,Rwin,om0) in clean_windows(Pv,dv,m,p,q):
                b_s2=smooth_bad(RmQ_s2,Pv,dv,Lwin,Rwin)
                b_v =smooth_bad(RmQ_v ,Pv,dv,Lwin,Rwin)
                if b_s2 is None or b_v is None: continue
                tested+=1
                sg=tuple(1 if om0[i]>0 else -1 for i in range(6)); chambers.add(sg); channels.add((m,p,q))
                if b_s2!=0: s2_fail+=1
                if b_v!=0:  v_fail+=1
                if tested<=16 or b_v!=0:
                    pr(f"  ch({m+1};{p+1},{q+1}) t0={t0:+.3f} signs={sg}: "
                       f"R-R_Q(s2)_bad={b_s2}  R-R_Q2(corr)_bad={b_v}")
    tested_line=True

pr("\n================ SUMMARY ================")
pr(f"isolated Q-wall smoothness tests: {tested}")
pr(f"distinct channels: {len(channels)}  distinct energy-sign chambers: {len(chambers)}")
pr(f"student-2 R_Q (G=-16max):   NON-smooth across {s2_fail}/{tested}")
pr(f"corrected R_Q2 (G=-32 wm wt): NON-smooth across {v_fail}/{tested}")
