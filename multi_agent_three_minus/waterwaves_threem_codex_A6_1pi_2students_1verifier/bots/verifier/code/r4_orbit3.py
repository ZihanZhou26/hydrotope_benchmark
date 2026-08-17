#!/usr/bin/env python3
"""Fast orbit confirmation: several on-shell lines, each crossing a single
rational Q_{m;pq}=0. Verify left is clean deg-8, confirm R_spline JUMPS on the
right (within the same magnitude cell), and read the jump order from close-right
points with small denominators (validated by a holdout)."""
from fractions import Fraction as F
from r4_verify import R_spline, SIG, _fmt, M, P
from r4_line_test import omega_of_t, word_of, poly_fit, poly_eval
from r4_line_test3 import gen_dirs, find_base, order_changes, qt_roots

def lowest_power(c):
    for i,x in enumerate(c):
        if x!=0: return i
    return None

def analyze(Pt,d,t0,ch,lo,hi):
    w0=word_of(omega_of_t(Pt,d,lo+(t0-lo)/2))
    # left: 14 points across (lo,t0)
    left=[lo+(t0-lo)*F(k,15) for k in range(1,15)]
    if any(word_of(omega_of_t(Pt,d,t))!=w0 for t in left): return None
    RSL=[R_spline(omega_of_t(Pt,d,t)) for t in left]
    cL=poly_fit(left[:9],RSL[:9],8)
    if any(poly_eval(cL,left[i])!=RSL[i] for i in range(9,14)): return None  # left clean
    # close right points: t0 + (hi-t0)*j/32, j=1..7  (small-ish denominators)
    step=(hi-t0)*F(1,32)
    rs=[t0+step*j for j in range(1,8)]
    if any(word_of(omega_of_t(Pt,d,t))!=w0 for t in rs): return None
    us=[t-t0 for t in rs]
    Js=[R_spline(omega_of_t(Pt,d,t))-poly_eval(cL,t) for t in rs]
    if all(J==0 for J in Js): return (ch,0)          # no jump
    # fit J(u) as low-degree poly using closest 5 points, validate on 6th
    order=None
    for deg in range(1,5):
        c=poly_fit(us[:deg+1],Js[:deg+1],deg)
        if deg+1<len(us) and poly_eval(c,us[deg+1])==Js[deg+1]:
            order=lowest_power(c); break
    return (ch,order)

if __name__=="__main__":
    results={}
    for d in gen_dirs(box=5):
        if len(results)>=6: break
        Pt=find_base(d,box=6)
        if Pt is None: continue
        oc=order_changes(Pt,d); qr=qt_roots(Pt,d)
        for (t0,ch) in qr:
            key=(ch[0],ch[1])
            if key in results: continue
            lo=max([t for t in oc if t<t0],default=None)
            hi=min([t for t in oc if t>t0],default=None)
            if lo is None or hi is None or not (lo<t0<hi): continue
            if any(lo<t<hi and t!=t0 for (t,c) in qr): continue
            r=analyze(Pt,d,t0,ch,lo,hi)
            if r is None: continue
            results[key]=r[1]
            print(f"Q_(m=leg{ch[0]+1}; p,q=leg{ch[1][0]+1},leg{ch[1][1]+1})=0 : jump order = {r[1]}   (t0={_fmt(t0)})", flush=True)
    print(f"\n{len(results)} distinct channels; orders={sorted(set(results.values()))}")
