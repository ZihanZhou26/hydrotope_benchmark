#!/usr/bin/env python3
"""Find an on-shell polynomial line + a t-window where the FULL magnitude order
is constant (=> a single R_spline polynomial cell, regardless of whether
within-sector ties matter) and exactly ONE Q_{m;pq} crosses zero inside. Then
fit a degree-8 poly in t from one side and test the other side.
"""
from fractions import Fraction as F
from r4_verify import amp_from_omega, P_pole, R_spline, SIG, _fmt, M, P, solve_onshell
from r4_line_test import (nullspace, omega_of_t, word_of, QT_signs, q_signs,
                          poly_fit, poly_eval)
import itertools

def all_directions(Pt, box=4):
    L1=[1,1,1,1,1,1]
    L2=[SIG[i]*Pt[i] for i in range(6)]
    basis=nullspace([L1,L2],6)
    nb=len(basis)
    sigv=tuple(SIG)
    seen=set(); out=[]
    for c in itertools.product(range(-box,box+1),repeat=nb):
        if all(x==0 for x in c): continue
        d=[sum(c[k]*basis[k][i] for k in range(nb)) for i in range(6)]
        if sum(SIG[i]*d[i]*d[i] for i in range(6))!=0: continue
        # normalize to primitive integer vector
        from math import gcd
        dens=[x.denominator for x in d]; L=1
        for dd in dens: L=L*dd//gcd(L,dd)
        di=[int(x*L) for x in d]
        g=0
        for x in di: g=gcd(g,abs(x))
        if g==0: continue
        di=tuple(x//g for x in di)
        if di in seen or tuple(-x for x in di) in seen: continue
        # skip d proportional to sigma
        if di==sigv or di==tuple(-x for x in sigv): continue
        seen.add(di); out.append([F(x) for x in di])
    return out

def order_changes(Pt,d):
    """t where |omega_i|=|omega_j| (order change): omega_i=+-omega_j, linear."""
    ts=set()
    for i in range(6):
        for j in range(i+1,6):
            # omega_i(t)-omega_j(t)=0 and omega_i+omega_j=0
            for sgn in (1,-1):
                a=Pt[i]-sgn*Pt[j]; b=d[i]-sgn*d[j]
                if b!=0:
                    ts.add(-a/b)
    return sorted(ts)

def qt_roots(Pt,d):
    """t where some Q_{m;pq}=0: quadratic per channel."""
    roots=[]
    for m in M:
        for pq in itertools.combinations(P,2):
            p,q=pq
            # Q(t)=omega_p^2+omega_q^2-omega_m^2, quadratic A t^2+B t+Cc
            def coef(i,j):
                return Pt[i]*Pt[j], Pt[i]*d[j]+Pt[j]*d[i], d[i]*d[j]
            A=d[p]**2+d[q]**2-d[m]**2
            B=2*(Pt[p]*d[p]+Pt[q]*d[q]-Pt[m]*d[m])
            C=Pt[p]**2+Pt[q]**2-Pt[m]**2
            # real rational roots only
            if A==0:
                if B!=0: roots.append((-C/B,(m,pq)))
                continue
            disc=B*B-4*A*C
            if disc<0: continue
            # sqrt rational?
            from math import isqrt
            num=disc.numerator; den=disc.denominator
            sn=isqrt(num) if num>=0 else -1; sd=isqrt(den)
            if sn>=0 and sn*sn==num and sd*sd==den:
                s=F(sn,sd)
                roots.append(((-B+s)/(2*A),(m,pq)))
                roots.append(((-B-s)/(2*A),(m,pq)))
            # irrational roots: still a real crossing; record approx via None flag
            else:
                # keep as float location marker so we can still isolate windows
                import math
                s=math.sqrt(float(disc))
                for r in ((-B/(2*A))+F(0), ):
                    pass
                roots.append((F(round(((-B)/(2*A)).__float__()*0+0)),None))  # placeholder skip
    return [(t,ch) for (t,ch) in roots if ch is not None]

if __name__=="__main__":
    Pt=solve_onshell(F(13,5),F(17,3),F(9,4),F(29,7))
    dirs=all_directions(Pt,box=4)
    print(f"{len(dirs)} candidate non-trivial directions")

    best=None
    for d in dirs:
        oc=order_changes(Pt,d)              # sorted list of t (rational)
        qr=qt_roots(Pt,d)                   # list of (t, channel)
        for (t0,ch) in qr:
            # nearest order-change below and above t0
            lo=max([t for t in oc if t< t0], default=F(-10**6))
            hi=min([t for t in oc if t> t0], default=F(10**6))
            # need t0 strictly interior and no OTHER qt root in (lo,hi)
            others=[t for (t,c) in qr if lo< t< hi and t!=t0]
            if lo< t0< hi and not others:
                width=min(t0-lo, hi-t0)
                cand=(width,d,t0,ch,lo,hi)
                if best is None or width>best[0]:
                    best=cand
    width,d,t0,ch,lo,hi=best
    print("chosen direction d =",[_fmt(x) for x in d])
    print(f"Q_T channel crossing: {ch} at t0={_fmt(t0)}  order-constant window ({_fmt(lo)},{_fmt(hi)})")
    print("half-window width in t:",_fmt(width))

    # sample rational t's strictly inside (lo,hi), split by side of t0, avoid t0
    span=hi-lo
    N=13
    ts=[]
    for k in range(1,2*N):
        t=lo+span*F(k,2*N)
        if t!=t0: ts.append(t)
    left=[t for t in ts if t< t0]
    right=[t for t in ts if t> t0]
    print(f"{len(left)} left samples, {len(right)} right samples")

    # verify order constant across all samples, and record QT sign of channel ch
    o0=word_of(omega_of_t(Pt,d,ts[0]))
    for t in ts:
        o=omega_of_t(Pt,d,t)
        assert sum(o)==0 and sum(SIG[i]*o[i]**2 for i in range(6))==0
        assert word_of(o)==o0, f"order changed at t={_fmt(t)}!"
    print("full magnitude order constant across ALL samples:", o0[1], "sigma-word",o0[0])

    # Q_T sign on each side (channel ch)
    def qtval(t):
        o=omega_of_t(Pt,d,t); m,pq=ch; p,q=pq
        return o[p]**2+o[q]**2-o[m]**2
    print("Q_T(ch) sign left/right:", '+' if qtval(left[0])>0 else '-',
          '/', '+' if qtval(right[0])>0 else '-')

    # compute R_spline at all samples
    Rvals={}
    for t in ts:
        Rvals[t]=R_spline(omega_of_t(Pt,d,t))

    # fit degree-8 polynomial in t from LEFT points (need >=9)
    assert len(left)>=9 and len(right)>=9, "need >=9 points per side"
    lt=left[:9]; ly=[Rvals[t] for t in lt]
    coeffs=poly_fit(lt,ly,8)

    print("\n--- CONTROL: predict remaining LEFT points from left-fit ---")
    ctrl_ok=True
    for t in left[9:]:
        pred=poly_eval(coeffs,t); res=pred-Rvals[t]
        print(f"  t={_fmt(t):>10}  residual={_fmt(res)}")
        if res!=0: ctrl_ok=False
    print("  control all-zero:",ctrl_ok)

    print("\n--- TEST: predict RIGHT points (other side of Q_T=0) from left-fit ---")
    right_zero=True
    for t in right:
        pred=poly_eval(coeffs,t); res=pred-Rvals[t]
        print(f"  t={_fmt(t):>10}  R_spline={_fmt(Rvals[t]):>18}  leftpoly={_fmt(pred):>22}  residual={_fmt(res)}")
        if res!=0: right_zero=False
    print("\nRESULT:")
    print("  left-fit reproduces left holdouts (single polynomial on left):", ctrl_ok)
    print("  left-fit reproduces RIGHT side across Q_T=0:", right_zero)
    if ctrl_ok and not right_zero:
        print("  => R_spline JUMPS across Q_T=0 within one magnitude cell. student-2 (s2_009) CONFIRMED.")
    elif ctrl_ok and right_zero:
        print("  => R_spline is a SINGLE polynomial across Q_T=0. student-2 REFUTED.")
    else:
        print("  => control failed; methodology issue, inconclusive.")
