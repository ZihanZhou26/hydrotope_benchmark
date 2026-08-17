#!/usr/bin/env python3
"""Generate exact integer on-shell lines w(t)=P+t d and a GENERAL per-channel
brick extractor. All independent of any student code."""
import itertools
from fractions import Fraction as F
from r5_core import (line, Q_T_val, R_spline, R_Q, G_brick, amp_from_omega,
                     poly_interp, poly_eval, poly_sub, poly_divmod, collect,
                     gen_ts, SingularError, M, P, _fmt)

SIGv = [-1,-1,-1,1,1,1]

def onshell_pt(v):
    return sum(v)==0 and sum(SIGv[i]*v[i]**2 for i in range(6))==0

def gen_int_lines(bound_P=8, bound_d=3, want=6, seed_scan=200000):
    """Yield integer (P,d) with P,d on the on-shell line variety.
    P: sum=0, sum sigma P^2=0.  d: sum=0, sum sigma d^2=0, sum sigma P d=0."""
    # a small stock of integer on-shell base points (found by structure:
    #   minus-squares == plus-squares, signed, zero sum)
    bases = [
        [8,2,-3,-5,4,-6],[ -8,2,3,4,5,-6],[9,-7,1,-8,6,-1],
        [7,-5,-2,-6,3,3],[10,-1,-6,-9,7,-1],[6,6,-3,-2,-8,1],
        [11,-4,-2,-9,-1,5],[5,-5,4,-8,7,-3],[12,-3,-4,-11,2,4],
    ]
    bases = [b for b in bases if onshell_pt([F(x) for x in b])]
    lines=[]
    # integer directions in a box that are null and sum-zero
    dirs=[]
    rng=range(-bound_d,bound_d+1)
    for d in itertools.product(rng,repeat=6):
        if sum(d)!=0: continue
        if sum(SIGv[i]*d[i]*d[i] for i in range(6))!=0: continue
        if all(x==0 for x in d): continue
        dirs.append(d)
    for Pv in bases:
        Pf=[F(x) for x in Pv]
        for d in dirs:
            if sum(SIGv[i]*Pf[i]*d[i] for i in range(6))!=0: continue
            lines.append((Pv, list(d)))
            if len(lines)>=want*40: break
    return lines, dirs

def Q_poly(Pvec,dvec,m,p,q):
    def sq(idx):
        a,b=F(Pvec[idx]),F(dvec[idx]); return [a*a,2*a*b,b*b]
    def addp(x,y):
        n=max(len(x),len(y)); x=x+[F(0)]*(n-len(x)); y=y+[F(0)]*(n-len(y))
        return [x[i]+y[i] for i in range(n)]
    return addp(addp(sq(p),sq(q)),[-c for c in sq(m)])

def q_mp(om,m,p): return om[p]**2-om[m]**2

def wall_ts(Pvec,dvec,lo,hi,steps=4000):
    """approx t of every q/Q crossing and magnitude-order change in (lo,hi)."""
    def sgn(x): return (x>0)-(x<0)
    walls={}
    for m in M:
        for p in P: walls[f"q_{m+1}{p+1}"]=("q",m,p)
    for m in M:
        for p,qq in itertools.combinations(P,2): walls[f"Q_{m+1};{p+1}{qq+1}"]=("Q",m,p,qq)
    prev={}; magprev=None; cr=[]
    for i in range(steps):
        t=F(lo)+(F(hi)-F(lo))*F(2*i+1,2*steps)
        om=line(Pvec,dvec,t)
        for nm,sp in walls.items():
            v=q_mp(om,sp[1],sp[2]) if sp[0]=="q" else Q_T_val(om,sp[1],sp[2],sp[3])
            s=sgn(v)
            if nm in prev and prev[nm] and s and s!=prev[nm]: cr.append((float(t),nm))
            prev[nm]=s
        mo=tuple(sorted(range(6),key=lambda j:abs(om[j])))
        if magprev is not None and mo!=magprev: cr.append((float(t),"MAG"))
        magprev=mo
    cr.sort()
    return cr

def extract(Pvec,dvec,m,p,q,lo=-3,hi=3,verbose=True):
    """Extract order-3 Q-brick for channel (m;p,q) on line P+td. Returns dict."""
    tleg=[x for x in P if x not in (p,q)][0]
    Qp=Q_poly(Pvec,dvec,m,p,q)
    # find real root(s) of Q(t) in (lo,hi)
    import numpy as np
    coeffs=[float(c) for c in Qp]
    roots=[r.real for r in np.roots(coeffs[::-1]) if abs(r.imag)<1e-9 and lo<r.real<hi] if len(coeffs)>1 else []
    if not roots: return {"ok":False,"reason":"no Q root in range"}
    cr=wall_ts(Pvec,dvec,lo,hi)
    res=[]
    for t0 in roots:
        # nearest OTHER crossing on each side (exclude this Q root itself ~ t0)
        others=[c for c in cr if abs(c[0]-t0)>1e-3]
        left=max([c for c in others if c[0]<t0],default=(lo,"lo"),key=lambda c:c[0])
        right=min([c for c in others if c[0]>t0],default=(hi,"hi"),key=lambda c:c[0])
        Lwin=(left[0]+1e-3, t0-1e-3); Rwin=(t0+1e-3, right[0]-1e-3)
        if Lwin[1]-Lwin[0]<0.02 or Rwin[1]-Rwin[0]<0.02:
            res.append({"t0":t0,"ok":False,"reason":"window too small","L":left,"R":right}); continue
        Lts=gen_ts(F(Lwin[0]).limit_denominator(10**6),F(Lwin[1]).limit_denominator(10**6),16,den=7919)
        Rts=gen_ts(F(Rwin[0]).limit_denominator(10**6),F(Rwin[1]).limit_denominator(10**6),16,den=7919)
        xL,yL=collect(R_spline,Pvec,dvec,Lts); xR,yR=collect(R_spline,Pvec,dvec,Rts)
        if len(xL)<9 or len(xR)<9:
            res.append({"t0":t0,"ok":False,"reason":f"few pts L{len(xL)} R{len(xR)}"}); continue
        cL=poly_interp(xL[:9],yL[:9]); cR=poly_interp(xR[:9],yR[:9])
        badL=sum(1 for x,y in zip(xL[9:],yL[9:]) if poly_eval(cL,x)!=y)
        badR=sum(1 for x,y in zip(xR[9:],yR[9:]) if poly_eval(cR,x)!=y)
        # which side is Q>0 ?
        Qmid_R=poly_eval(Qp,F(xR[0]))
        hi_branch,lo_branch=(cR,cL) if Qmid_R>0 else (cL,cR)
        dR=poly_sub(hi_branch,lo_branch)      # R|_{Q>0} - R|_{Q<0}
        # Q^3
        Qcube=[F(1)]
        for _ in range(3):
            nw=[F(0)]*(len(Qcube)+len(Qp)-1)
            for i,ci in enumerate(Qcube):
                for j,cj in enumerate(Qp): nw[i+j]+=ci*cj
            Qcube=nw
        quot,rem=poly_divmod(dR,Qcube)
        rem_zero=all(c==0 for c in rem)
        # G along line (selector) as poly? compare quotient to G_brick at sample pts
        selector_ok=True; sel_kind=set()
        for t in (xR[:3]+xL[:3]):
            om=line(Pvec,dvec,t)
            g=G_brick(om,m,p,q)
            if poly_eval(quot,t)!=g: selector_ok=False
            sel_kind.add("wm2" if om[m]**2>=om[tleg]**2 else "wt2")
        # divisible by Q^4?  (should NOT be, for order exactly 3)
        Q4=Qcube[:]
        nw=[F(0)]*(len(Q4)+len(Qp)-1)
        for i,ci in enumerate(Q4):
            for j,cj in enumerate(Qp): nw[i+j]+=ci*cj
        Q4=nw
        _,rem4=poly_divmod(dR,Q4)
        div_by_Q4=all(c==0 for c in rem4)
        # DECISIVE global: R_spline - R_Q smooth across wall
        def RmQ(om): return R_spline(om)-R_Q(om)
        xA,yA=collect(RmQ,Pvec,dvec,Lts+Rts)
        cA=poly_interp(xA[:9],yA[:9])
        badA=sum(1 for x,y in zip(xA,yA) if poly_eval(cA,x)!=y)
        res.append({"t0":t0,"ok":True,"badL":badL,"badR":badR,"rem_zero":rem_zero,
                    "quot_deg":len(quot)-1,"selector_ok":selector_ok,"sel_kind":sorted(sel_kind),
                    "div_by_Q4":div_by_Q4,"badA":badA,"nL":len(xL),"nR":len(xR),
                    "quot":[_fmt(c) for c in quot]})
        if verbose:
            print(f"  ch(m={m+1};{p+1},{q+1}) t0={t0:+.4f}: badL={badL} badR={badR} "
                  f"remQ3=0?{rem_zero} qdeg={len(quot)-1} selOK?{selector_ok} sel={sorted(sel_kind)} "
                  f"divQ4?{div_by_Q4} RmQ_smooth_bad={badA}")
    return {"ok":True,"channel":(m,p,q),"results":res}
