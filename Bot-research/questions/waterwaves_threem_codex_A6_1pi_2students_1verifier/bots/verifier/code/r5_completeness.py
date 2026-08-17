#!/usr/bin/env python3
"""Corroborate student-1's 18-wall completeness: on several on-shell lines, the
ONLY loci where R_spline changes polynomial are q_{mp}=0 and Q_{m;pq}=0.
Test: between two consecutive q/Q crossings (which may contain magnitude-order
changes), R_spline is a SINGLE degree-8 polynomial (0 holdout residual)."""
import itertools
from fractions import Fraction as F
from r5_lines import gen_int_lines, q_mp
from r5_core import (line, Q_T_val, R_spline, poly_interp, poly_eval, collect,
                     gen_ts, M, P, _fmt)
import numpy as np

def pr(*a): print(*a, flush=True)

def qQ_crossings(Pvec,dvec,lo=-3,hi=3,steps=6000):
    def sgn(x): return (x>0)-(x<0)
    prev={}; cr=[]
    for i in range(steps):
        t=F(lo)+(F(hi)-F(lo))*F(2*i+1,2*steps)
        om=line(Pvec,dvec,t)
        for mm in M:
            for pp in P:
                v=sgn(om[pp]**2-om[mm]**2); nm=f"q{mm+1}{pp+1}"
                if nm in prev and prev[nm] and v and v!=prev[nm]: cr.append(float(t))
                prev[nm]=v
        for mm in M:
            for pp,qq in itertools.combinations(P,2):
                v=sgn(Q_T_val(om,mm,pp,qq)); nm=f"Q{mm+1};{pp+1}{qq+1}"
                if nm in prev and prev[nm] and v and v!=prev[nm]: cr.append(float(t))
                prev[nm]=v
    return sorted(cr)

def mag_changes(Pvec,dvec,lo,hi,steps=4000):
    prev=None; mc=[]
    for i in range(steps):
        t=F(lo)+(F(hi)-F(lo))*F(2*i+1,2*steps)
        om=line(Pvec,dvec,t)
        mo=tuple(sorted(range(6),key=lambda j:abs(om[j])))
        if prev is not None and mo!=prev: mc.append(float(t))
        prev=mo
    return mc

lines,_=gen_int_lines()
seen=set(); nline=0; total=0; passed=0; interesting=0
for Pv,dv in lines:
    k=(tuple(Pv),tuple(dv))
    if k in seen: continue
    seen.add(k)
    if nline>=6: break
    cr=qQ_crossings(Pv,dv)
    # add segment endpoints
    pts=[-2.8]+cr+[2.8]
    used=False
    for a,b in zip(pts,pts[1:]):
        if b-a<0.25: continue
        # count magnitude-order changes strictly inside (a,b)
        mc=[t for t in mag_changes(Pv,dv,a+0.02,b-0.02) if a+0.02<t<b-0.02]
        if not mc:  # only test segments that DO contain a MAG change (the nontrivial case)
            continue
        Ts=gen_ts(F(a+0.03).limit_denominator(10**6),F(b-0.03).limit_denominator(10**6),16,den=7919)
        xs,ys=collect(R_spline,Pv,dv,Ts)
        if len(xs)<12: continue
        c=poly_interp(xs[:9],ys[:9])
        bad=sum(1 for x,y in zip(xs,ys) if poly_eval(c,x)!=y)
        total+=1; interesting+=1
        if bad==0: passed+=1
        used=True
        pr(f"  P={Pv} d={dv} seg({a:+.2f},{b:+.2f}) MAGchanges_inside={len(mc)} "
           f"pts={len(xs)} single-poly_bad={bad} -> {'smooth (no hidden wall)' if bad==0 else 'HIDDEN WALL!'}")
    if used: nline+=1

pr("\n================ SUMMARY ================")
pr(f"segments with an interior magnitude-order change tested: {total}")
pr(f"R_spline single-polynomial across them: {passed}/{total}")
pr("=> magnitude-order changes (same-sector) are NOT walls; supports 18-wall (9 q + 9 Q) completeness."
   if passed==total else "=> FOUND a segment with a hidden wall not at q/Q!")
