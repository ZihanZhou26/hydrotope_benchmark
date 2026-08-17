#!/usr/bin/env python3
"""Robust construction of an on-shell polynomial line crossing a single Q_T=0
wall inside one magnitude cell, then the degree-8 jump test.

Strategy: pick integer direction d (sum d=0, sum sigma d^2=0, not ~sigma), then
solve for a rational on-shell base point P with sum sigma P d = 0 and distinct
|omega_i|. Line omega(t)=P+t d is exactly on-shell for all t.
"""
from fractions import Fraction as F
from r4_verify import R_spline, SIG, _fmt, M, P
from r4_line_test import nullspace, omega_of_t, word_of, poly_fit, poly_eval
import itertools
from math import gcd, isqrt

def primitive(d):
    dens=[x.denominator for x in d]; L=1
    for dd in dens: L=L*dd//gcd(L,dd)
    di=[int(x*L) for x in d]; g=0
    for x in di: g=gcd(g,abs(x))
    if g==0: return None
    return tuple(x//g for x in di)

def gen_dirs(box=5):
    out=set(); sigv=tuple(SIG)
    for vals in itertools.product(range(-box,box+1),repeat=6):
        if sum(vals)!=0: continue
        if sum(SIG[i]*vals[i]*vals[i] for i in range(6))!=0: continue
        if all(v==0 for v in vals): continue
        p=primitive([F(v) for v in vals])
        if p is None: continue
        if p==sigv or tuple(-x for x in p)==sigv: continue
        if tuple(-x for x in p) in out: continue
        out.add(p)
    return [list(map(F,p)) for p in out]

def find_base(d, box=6):
    """rational on-shell P with sum sigma P d=0 and distinct |omega|."""
    L1=[1,1,1,1,1,1]
    L2=[SIG[i]*d[i] for i in range(6)]
    N=nullspace([L1,L2],6)            # 4-dim basis
    nb=len(N)
    for c in itertools.product(range(-box,box+1),repeat=nb):
        if all(x==0 for x in c): continue
        Pv=[sum(c[k]*N[k][i] for k in range(nb)) for i in range(6)]
        if sum(SIG[i]*Pv[i]*Pv[i] for i in range(6))!=0: continue
        mags=[abs(x) for x in Pv]
        if len(set(mags))!=6: continue          # distinct magnitudes
        if any(x==0 for x in Pv): continue
        return Pv
    return None

def order_changes(Pt,d):
    ts=set()
    for i in range(6):
        for j in range(i+1,6):
            for sgn in (1,-1):
                a=Pt[i]-sgn*Pt[j]; b=d[i]-sgn*d[j]
                if b!=0: ts.add(-a/b)
    return sorted(ts)

def qt_roots(Pt,d):
    roots=[]
    for m in M:
        for pq in itertools.combinations(P,2):
            p,q=pq
            A=d[p]**2+d[q]**2-d[m]**2
            B=2*(Pt[p]*d[p]+Pt[q]*d[q]-Pt[m]*d[m])
            C=Pt[p]**2+Pt[q]**2-Pt[m]**2
            if A==0:
                if B!=0: roots.append((-C/B,(m,pq)))
                continue
            disc=B*B-4*A*C
            if disc<0: continue
            num,den=disc.numerator,disc.denominator
            sn=isqrt(num) if num>=0 else -1; sd=isqrt(den)
            if sn>=0 and sn*sn==num and sd*sd==den:
                s=F(sn,sd)
                roots.append(((-B+s)/(2*A),(m,pq)))
                roots.append(((-B-s)/(2*A),(m,pq)))
    return roots

def try_line(Pt,d):
    oc=order_changes(Pt,d)
    qr=qt_roots(Pt,d)
    best=None
    for (t0,ch) in qr:
        lo=max([t for t in oc if t<t0], default=None)
        hi=min([t for t in oc if t>t0], default=None)
        if lo is None or hi is None: continue
        others=[t for (t,c) in qr if lo<t<hi and t!=t0]
        if lo<t0<hi and not others:
            width=min(t0-lo,hi-t0)
            if best is None or width>best[0]:
                best=(width,t0,ch,lo,hi)
    return best

if __name__=="__main__":
    dirs=gen_dirs(box=5)
    print(f"{len(dirs)} integer directions")
    chosen=None
    for d in dirs:
        Pt=find_base(d,box=6)
        if Pt is None: continue
        res=try_line(Pt,d)
        if res is None: continue
        width,t0,ch,lo,hi=res
        chosen=(d,Pt,width,t0,ch,lo,hi)
        break
    assert chosen is not None, "no usable line found"
    d,Pt,width,t0,ch,lo,hi=chosen
    print("base P     =",[_fmt(x) for x in Pt])
    print("direction d=",[_fmt(x) for x in d])
    print("on-shell:",_fmt(sum(Pt)),_fmt(sum(SIG[i]*Pt[i]**2 for i in range(6))))
    print(f"single Q_T crossing: channel {ch} at t0={_fmt(t0)}; order-constant window ({_fmt(lo)},{_fmt(hi)})")

    span=hi-lo; Ns=13
    ts=[lo+span*F(k,2*Ns) for k in range(1,2*Ns) if lo+span*F(k,2*Ns)!=t0]
    left=[t for t in ts if t<t0]; right=[t for t in ts if t>t0]
    o0=word_of(omega_of_t(Pt,d,ts[0]))
    for t in ts:
        o=omega_of_t(Pt,d,t)
        assert sum(o)==0 and sum(SIG[i]*o[i]**2 for i in range(6))==0
        assert word_of(o)==o0
    print("full magnitude order CONSTANT across all samples:", o0[1], " sigma-word", o0[0])
    m,pq=ch; p,q=pq
    def qtv(t):
        o=omega_of_t(Pt,d,t); return o[p]**2+o[q]**2-o[m]**2
    print("Q_T sign left/right:", ('+' if qtv(left[0])>0 else '-'),'/',('+' if qtv(right[0])>0 else '-'))
    print(f"{len(left)} left / {len(right)} right samples")

    Rvals={t:R_spline(omega_of_t(Pt,d,t)) for t in ts}
    assert len(left)>=9 and len(right)>=9
    lt=left[:9]; coeffs=poly_fit(lt,[Rvals[t] for t in lt],8)

    print("\nCONTROL (left holdouts, must be 0):")
    ctrl=True
    for t in left[9:]:
        r=poly_eval(coeffs,t)-Rvals[t]; ctrl&=(r==0)
        print(f"  t={_fmt(t):>12} residual={_fmt(r)}")
    print("\nTEST (right side, across Q_T=0):")
    rz=True
    for t in right:
        pred=poly_eval(coeffs,t); r=pred-Rvals[t]; rz&=(r==0)
        print(f"  t={_fmt(t):>12} R={_fmt(Rvals[t]):>16} leftpoly={_fmt(pred):>20} resid={_fmt(r)}")
    print("\n=== VERDICT ===")
    print("left single-polynomial control passed:", ctrl)
    print("left polynomial also fits right side  :", rz)
    if ctrl and not rz:
        print("R_spline JUMPS across Q_T=0 in a fixed magnitude cell -> student-2 s2_009 CONFIRMED")
    elif ctrl and rz:
        print("R_spline is one polynomial across Q_T=0 -> student-2 s2_009 REFUTED")
    else:
        print("inconclusive (control failed)")
