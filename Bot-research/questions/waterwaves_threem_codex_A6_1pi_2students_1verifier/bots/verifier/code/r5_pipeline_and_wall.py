#!/usr/bin/env python3
"""(1) Validate my R_spline/P_pole pipeline vs the INDEPENDENTLY verified order-1
q-brick anchor (12622720/27).  (2) For several isolated Q-wall crossings, compare
the exact jump cofactor quot(t) to -16 w_m^2(t) BOTH globally and AT the wall t0."""
import itertools
from fractions import Fraction as F
from r5_lines import Q_poly, wall_ts, q_mp
from r5_core import (line, Q_T_val, R_spline, R_Q, G_brick, solve_onshell,
                     poly_interp, poly_eval, poly_sub, poly_divmod, collect,
                     gen_ts, M, P, _fmt)
import numpy as np

def pr(*a): print(*a, flush=True)

# ---------------- (1) order-1 q-brick anchor validation ----------------
pr("="*70); pr("PIPELINE VALIDATION: order-1 q_{24}=0 brick anchor -> 12622720/27")
# anchor def (group notes): q_24=0 at (B,c,e)=(10,2,3); lim (R_L-R_R)/q_24
# Reconstruct the slice used in round 3: omega_2=omega_4 tie region.
# Use the s2 slice: omega=(?,B/2?...). Instead build a clean line hitting q_24=0.
# Simpler: use the documented slice omega_2=omega_4=5, omega_3=u, omega_5=6-u
# (from F12) which is a q_35 study; for q_24 use a line where only q_24 crosses.
# We just need an INDEPENDENT check that R_spline's order-1 jump matches a known #.
# Take a line through the F12 slice base and confirm the H_24 anchor via q_24.
# Construct: hold minus legs 1,3 and plus leg 6 to enforce on-shell, vary to cross q24.
# Use param: free (w2,w3,w4,w5) with w2 near w4 (q_24 ~ w4^2-w2^2).
def line_from_free(f2,f3,f4,f5, d2,d3,d4,d5):
    """on-shell line via solve_onshell at each t (free legs 2,3,4,5)."""
    def pt(t):
        return solve_onshell(F(f2)+F(d2)*t, F(f3)+F(d3)*t, F(f4)+F(d4)*t, F(f5)+F(d5)*t)
    return pt

# cross q_24 = w4^2 - w2^2 = 0 near w2=w4. Vary w2 with everything else fixed-ish.
pt = line_from_free(2, 3, 4, 5, 1, 0, 0, 0)   # vary w2 => w2 passes through w4=4 at t=2
# q_24=0 when w2=+-w4=+-4 -> t=2 (w2=4). window around t=2, isolate.
t0q = F(2)
# check only q_24 crosses near t0q on this free-line by scanning q's/Q's
def qcheck(t):
    om=pt(t); return om
om0=pt(t0q)
pr("  at t0q=2: w=",[ _fmt(x) for x in om0])
pr("  q_24=",_fmt(om0[3]**2-om0[1]**2)," (expect 0)")
# reconstruct R_spline on both sides of t=2 in a small window, order-1 jump
Ls=gen_ts(F(17,10),F(198,100),14,den=7919); Rs=gen_ts(F(202,100),F(23,10),14,den=7919)
xL,yL=[],[]
for t in Ls:
    try: yL.append(R_spline(pt(t))); xL.append(t)
    except Exception: pass
xR,yR=[],[]
for t in Rs:
    try: yR.append(R_spline(pt(t))); xR.append(t)
    except Exception: pass
if len(xL)>=9 and len(xR)>=9:
    cL=poly_interp(xL[:9],yL[:9]); cR=poly_interp(xR[:9],yR[:9])
    badL=sum(1 for x,y in zip(xL[9:],yL[9:]) if poly_eval(cL,x)!=y)
    badR=sum(1 for x,y in zip(xR[9:],yR[9:]) if poly_eval(cR,x)!=y)
    pr(f"  branch fits badL={badL} badR={badR}")
    # order-1 jump: (R_L - R_R)/q_24 at the wall. q_24(t) as poly:
    # w2=2+t, w4=4 -> q24 = 16-(2+t)^2 = 16-(4+4t+t^2)=12-4t-t^2; zero at t=2
    q24p=[F(12),F(-4),F(-1)]
    dRq=poly_sub(cL,cR)   # R_L - R_R (left is w2<4 => q24>0)
    quotq,remq=poly_divmod(dRq,q24p)
    pr(f"  (R_L-R_R)/q_24 remainder zero? {all(c==0 for c in remq)}; value at t0=2: {_fmt(poly_eval(quotq,t0q))}")
    pr(f"  expected anchor 12622720/27 = {_fmt(F(12622720,27))}")
else:
    pr("  insufficient points for q-anchor check", len(xL), len(xR))

# ---------------- (2) quot vs -16 w_m^2 globally and at wall ----------------
pr("="*70); pr("Q-BRICK: quot(t) vs -16 w_m^2(t) globally and at wall t0")

def study(Pvec,dvec,m,p,q,label):
    tleg=[x for x in P if x not in (p,q)][0]
    Qp=Q_poly(Pvec,dvec,m,p,q)
    roots=[r.real for r in np.roots([float(c) for c in Qp][::-1]) if abs(r.imag)<1e-9 and -3<r.real<3]
    cr=wall_ts(Pvec,dvec,-3,3)
    for t0 in roots:
        others=[c for c in cr if abs(c[0]-t0)>2e-3]
        left=max([c for c in others if c[0]<t0],default=(-3,"lo"),key=lambda c:c[0])
        right=min([c for c in others if c[0]>t0],default=(3,"hi"),key=lambda c:c[0])
        # ISOLATION at t0: no other q/Q within 1e-3 in value
        om0=line(Pvec,dvec,F(t0).limit_denominator(10**7))
        others_zero=[]
        for mm in M:
            for pp in P:
                if abs(float(om0[pp]**2-om0[mm]**2))<1e-2: others_zero.append(f"q{mm+1}{pp+1}")
        for mm in M:
            for pp,qq in itertools.combinations(P,2):
                if (mm,pp,qq)!=(m,p,q) and abs(float(Q_T_val(om0,mm,pp,qq)))<1e-2:
                    others_zero.append(f"Q{mm+1};{pp+1}{qq+1}")
        Lwin=(left[0]+1e-3,t0-1e-3); Rwin=(t0+1e-3,right[0]-1e-3)
        if Lwin[1]-Lwin[0]<0.03 or Rwin[1]-Rwin[0]<0.03:
            pr(f"  [{label}] t0={t0:+.4f}: window too small, skip"); continue
        Lts=gen_ts(F(Lwin[0]).limit_denominator(10**6),F(Lwin[1]).limit_denominator(10**6),14,den=7919)
        Rts=gen_ts(F(Rwin[0]).limit_denominator(10**6),F(Rwin[1]).limit_denominator(10**6),14,den=7919)
        xL,yL=collect(R_spline,Pvec,dvec,Lts); xR,yR=collect(R_spline,Pvec,dvec,Rts)
        if len(xL)<9 or len(xR)<9:
            pr(f"  [{label}] t0={t0:+.4f}: few pts"); continue
        cL=poly_interp(xL[:9],yL[:9]); cR=poly_interp(xR[:9],yR[:9])
        badL=sum(1 for x,y in zip(xL[9:],yL[9:]) if poly_eval(cL,x)!=y)
        badR=sum(1 for x,y in zip(xR[9:],yR[9:]) if poly_eval(cR,x)!=y)
        Qmid=poly_eval(Qp,F(xR[0]))
        hi_b,lo_b=(cR,cL) if Qmid>0 else (cL,cR)
        dR=poly_sub(hi_b,lo_b)
        Qcube=[F(1)]
        for _ in range(3):
            nw=[F(0)]*(len(Qcube)+len(Qp)-1)
            for i,ci in enumerate(Qcube):
                for j,cj in enumerate(Qp): nw[i+j]+=ci*cj
            Qcube=nw
        quot,rem=poly_divmod(dR,Qcube)
        remz=all(c==0 for c in rem)
        # -16 w_m^2 and -16 w_t^2 as poly in t
        def sqp(idx):
            a,b=F(Pvec[idx]),F(dvec[idx]); return [-16*a*a,-32*a*b,-16*b*b]
        wm2=sqp(m); wt2=sqp(tleg)
        eqm_glob=all(c==0 for c in poly_sub(quot,wm2))
        eqt_glob=all(c==0 for c in poly_sub(quot,wt2))
        # AT the wall t0
        t0F=F(t0).limit_denominator(10**7)
        qv=poly_eval(quot,t0F); gm=poly_eval(wm2,t0F); gt=poly_eval(wt2,t0F)
        om=line(Pvec,dvec,t0F)
        gmax=-16*max(om[m]**2,om[tleg]**2)
        # difference of quot from -16wm2 (to see structure)
        diff=poly_sub(quot,wm2)
        pr(f"  [{label}] t0={t0:+.4f} Qdeg={len(Qp)-1} badL={badL} badR={badR} remQ3={remz} "
           f"qdeg={len(quot)-1} isol_others={others_zero}")
        pr(f"      quot==-16wm2(glob)? {eqm_glob}   quot==-16wt2(glob)? {eqt_glob}")
        pr(f"      AT WALL: quot(t0)={_fmt(qv)}  -16max(t0)={_fmt(gmax)}  match={qv==gmax}")
        pr(f"      quot - (-16wm2) coeffs: {[_fmt(c) for c in diff]}")

study([8,2,-3,-5,4,-6],[-2,1,0,2,-1,0],0,3,5,"CANON(1;46) linQ")
study([8,2,-3,-5,4,-6],[-3,-2,1,3,-1,2],0,3,5,"LINE2(1;46) quadQ")
study([8,2,-3,-5,4,-6],[-3,-3,-3,3,3,3],0,4,5,"LINE1(1;56) quadQ")
