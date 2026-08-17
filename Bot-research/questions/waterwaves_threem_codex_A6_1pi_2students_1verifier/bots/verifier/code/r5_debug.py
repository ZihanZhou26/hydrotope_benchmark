#!/usr/bin/env python3
"""Deep debug of one 'failing' extraction: is it my windowing/selector check
or a genuine refutation? Print window, q_{mt} crossing, quotient vs both pieces."""
from fractions import Fraction as F
from r5_lines import Q_poly, wall_ts, q_mp
from r5_core import (line, Q_T_val, R_spline, R_Q, G_brick, poly_interp, poly_eval,
                     poly_sub, poly_divmod, collect, gen_ts, M, P, _fmt)
import numpy as np

def dbg(Pvec,dvec,m,p,q):
    tleg=[x for x in P if x not in (p,q)][0]
    print("="*70)
    print(f"line P={Pvec} d={dvec}  channel (m={m+1};p={p+1},q={q+1}) omitted t={tleg+1}")
    Qp=Q_poly(Pvec,dvec,m,p,q)
    print("Q(t) coeffs:", [_fmt(c) for c in Qp])
    roots=[r.real for r in np.roots([float(c) for c in Qp][::-1]) if abs(r.imag)<1e-9]
    print("Q roots:", roots)
    cr=wall_ts(Pvec,dvec,-3,3)
    for t0 in roots:
        if not (-3<t0<3): continue
        print(f"\n--- t0={t0:+.4f} ---")
        others=[c for c in cr if abs(c[0]-t0)>1e-3]
        left=max([c for c in others if c[0]<t0],default=(-3,"lo"),key=lambda c:c[0])
        right=min([c for c in others if c[0]>t0],default=(3,"hi"),key=lambda c:c[0])
        print("nearest other crossings: left",left," right",right)
        # is q_{mt}=0 crossing inside [left,right]?
        # q_{mt}(t)=w_t^2-w_m^2
        for tt in [left[0], t0, right[0]]:
            om=line(Pvec,dvec,F(tt).limit_denominator(10**6))
            print(f"   t={tt:+.4f}: wm^2={float(om[m]**2):.3f} wt^2={float(om[tleg]**2):.3f} "
                  f"q_mt={float(om[tleg]**2-om[m]**2):+.3f}  -> selector picks "
                  f"{'wm2' if om[m]**2>=om[tleg]**2 else 'wt2'}")
        Lwin=(left[0]+1e-3,t0-1e-3); Rwin=(t0+1e-3,right[0]-1e-3)
        Lts=gen_ts(F(Lwin[0]).limit_denominator(10**6),F(Lwin[1]).limit_denominator(10**6),16,den=7919)
        Rts=gen_ts(F(Rwin[0]).limit_denominator(10**6),F(Rwin[1]).limit_denominator(10**6),16,den=7919)
        xL,yL=collect(R_spline,Pvec,dvec,Lts); xR,yR=collect(R_spline,Pvec,dvec,Rts)
        print(f"   usable L={len(xL)} R={len(xR)}")
        if len(xL)<9 or len(xR)<9:
            print("   too few pts"); continue
        cL=poly_interp(xL[:9],yL[:9]); cR=poly_interp(xR[:9],yR[:9])
        Qmid_R=poly_eval(Qp,F(xR[0]))
        hi_b,lo_b=(cR,cL) if Qmid_R>0 else (cL,cR)
        dR=poly_sub(hi_b,lo_b)
        Qcube=[F(1)]
        for _ in range(3):
            nw=[F(0)]*(len(Qcube)+len(Qp)-1)
            for i,ci in enumerate(Qcube):
                for j,cj in enumerate(Qp): nw[i+j]+=ci*cj
            Qcube=nw
        quot,rem=poly_divmod(dR,Qcube)
        print("   remQ3=0?",all(c==0 for c in rem)," quot deg",len(quot)-1)
        print("   quot(t):",[_fmt(c) for c in quot])
        # compare quot to -16 wm^2 and -16 wt^2 as polynomials in t
        def sq_poly(idx):
            a,b=F(Pvec[idx]),F(dvec[idx]); return [-16*a*a,-32*a*b,-16*b*b]
        wm2p=sq_poly(m); wt2p=sq_poly(tleg)
        print("   -16 wm^2(t):",[_fmt(c) for c in wm2p])
        print("   -16 wt^2(t):",[_fmt(c) for c in wt2p])
        eqm = poly_sub(quot,wm2p)==[F(0)] or all(c==0 for c in poly_sub(quot,wm2p))
        eqt = all(c==0 for c in poly_sub(quot,wt2p))
        print(f"   quot == -16 wm^2 ? {eqm} ;  quot == -16 wt^2 ? {eqt}")

if __name__=="__main__":
    # the failing ch(1;5,6) on the all-scaling line
    dbg([8,2,-3,-5,4,-6],[-3,-3,-3,3,3,3], 0,4,5)
    # failing ch(1;4,6) on a different line (canonical channel, new line)
    dbg([8,2,-3,-5,4,-6],[-3,-2,1,3,-1,2], 0,3,5)
