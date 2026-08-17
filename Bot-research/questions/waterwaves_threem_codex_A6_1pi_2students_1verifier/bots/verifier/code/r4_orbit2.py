#!/usr/bin/env python3
"""Confirm the Q_T=0 R_spline jump is a systematic S3xS3 orbit with a consistent
ORDER. For each on-shell line crossing a single rational Q_{m;pq}=0 root t0:
 - verify LEFT side is a clean deg-8 polynomial (control on left holdouts);
 - using only right points CLOSE to t0 (before any other wall), fit the jump
   J(u)=R_spline - leftpoly as a polynomial in u=(t-t0), VALIDATE with a
   close-right holdout, and read the lowest nonzero power (= jump order).
"""
from fractions import Fraction as F
from r4_verify import R_spline, SIG, _fmt, M, P
from r4_line_test import omega_of_t, word_of, poly_fit, poly_eval
from r4_line_test3 import gen_dirs, find_base, order_changes, qt_roots

def lowest_power(coeffs):
    for i,c in enumerate(coeffs):
        if c!=0: return i,c
    return None,None

def analyze_line(Pt,d,t0,ch,lo,hi):
    # left samples across (lo,t0); need clean deg-8 control
    NL=16
    left=[lo+(t0-lo)*F(k,NL+1) for k in range(1,NL+1)]
    if any(word_of(omega_of_t(Pt,d,t))!=word_of(omega_of_t(Pt,d,left[0])) for t in left):
        return None
    RSL={t:R_spline(omega_of_t(Pt,d,t)) for t in left}
    cL=poly_fit(left[:9],[RSL[t] for t in left[:9]],8)
    if not all(poly_eval(cL,t)==RSL[t] for t in left[9:]):    # left must be clean
        return None
    # right points VERY close to t0: geometric approach
    gap=hi-t0
    rs=[t0+gap*F(1,2**k) for k in range(1,10)]   # t0+gap/2, /4, /8, ... approaching t0
    rs=[t for t in rs if word_of(omega_of_t(Pt,d,t))==word_of(omega_of_t(Pt,d,left[0]))]
    if len(rs)<7: return None
    # J(u) at these points, u=t-t0
    us=[t-t0 for t in rs]
    Js=[R_spline(omega_of_t(Pt,d,t))-poly_eval(cL,t) for t in rs]
    # fit J as polynomial in u using closest 6, validate on the next 1
    order=None
    for deg in range(1,6):
        c=poly_fit(us[-(deg+1):],Js[-(deg+1):],deg)   # closest points
        # validate on a slightly farther close point
        val_ok=(poly_eval(c,us[-(deg+2)])==Js[-(deg+2)]) if len(us)>=deg+2 else False
        if val_ok:
            lp,lc=lowest_power(c)
            order=lp
            break
    return (ch,order)

if __name__=="__main__":
    results={}
    dirs=gen_dirs(box=5)
    for d in dirs:
        Pt=find_base(d,box=6)
        if Pt is None: continue
        oc=order_changes(Pt,d); qr=qt_roots(Pt,d)
        for (t0,ch) in qr:
            lo=max([t for t in oc if t<t0],default=None)
            hi=min([t for t in oc if t>t0],default=None)
            if lo is None or hi is None or not (lo<t0<hi): continue
            if any(lo<t<hi and t!=t0 for (t,c) in qr): continue
            key=(ch[0],ch[1])
            if key in results: continue
            r=analyze_line(Pt,d,t0,ch,lo,hi)
            if r is None: continue
            results[key]=r[1]
            print(f"Q_(m=leg{ch[0]+1}; p,q=leg{ch[1][0]+1},leg{ch[1][1]+1})=0 : "
                  f"R_spline jump order in (t-t0) = {r[1]}")
        if len(results)>=9: break
    print(f"\n{len(results)} distinct Q_(m;pq) channels tested; jump orders = {sorted(set(results.values()))}")
    if results and all(v==3 for v in results.values()):
        print("ALL channels show an order-3 jump => a uniform S3xS3 Q-wall orbit of order 3.")
