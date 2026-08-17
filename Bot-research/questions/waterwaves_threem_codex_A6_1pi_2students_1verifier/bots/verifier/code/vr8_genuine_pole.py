#!/usr/bin/env python3
"""Characterise GENUINE internal-line on-shell crossings D_S=0 and verify the
formula tracks BG on both sides as eps->0.  Locate a crossing by bisection in a
free-frequency parameter, then sample rational points ever closer on each side.
"""
from fractions import Fraction as F
from itertools import combinations
import vr8_core as V
SIG=[-1,-1,-1,1,1,1]

def DS(w,S):
    wS=sum(w[i] for i in S); kS=sum(SIG[i]*w[i]*w[i] for i in S)
    if kS==0: return None
    return wS*wS/abs(kS)-1

def ev(free):
    try:
        omega,a6i=V.bg_amp_free(free)
    except Exception:
        return None
    w=list(omega); x2=[z*z for z in w]
    if len(set(x2))<6: return None
    try: me=V.stripped(w)
    except ZeroDivisionError: return None
    return w,a6i,me

# scan a family for a D_S sign change, S given
def find_and_probe(base, slot, S):
    grid=[F(g,8) for g in range(-80,81)]
    prev=None
    for g in grid:
        free=list(base); free[slot]=g
        r=ev(free)
        if r is None: prev=None; continue
        w,a6i,me=r
        d=DS(w,S)
        if prev is not None:
            pg,pd=prev
            if pd is not None and d is not None and pd!=0 and d!=0 and (pd>0)!=(d>0):
                kS=sum(SIG[i]*w[i]*w[i] for i in S)
                if abs(kS)>F(1,50):
                    return pg,g   # bracket [pg,g]
        prev=(g,d)
    return None

def probe(base, slot, S, lo, hi):
    # bisect to shrink bracket around D_S root, then sample both sides finely
    for _ in range(30):
        mid=(lo+hi)/2
        free=list(base); free[slot]=mid
        r=ev(free)
        if r is None:
            # perturb mid slightly
            mid=mid+F(1,10**6)
            free=list(base); free[slot]=mid
            r=ev(free)
            if r is None: break
        w,a6i,me=r
        d=DS(w,S)
        free_lo=list(base); free_lo[slot]=lo; rlo=ev(free_lo)
        if rlo is None: break
        dlo=DS(rlo[0],S)
        if d is None or dlo is None: break
        if (dlo>0)==(d>0): lo=mid
        else: hi=mid
    print(f"  bracket lo={float(lo):.8f} hi={float(hi):.8f}")
    results=[]
    for x in [lo, hi]:
        free=list(base); free[slot]=x
        r=ev(free)
        if r is None: continue
        w,a6i,me=r
        results.append((x, DS(w,S), a6i, me, me==a6i))
    for x,d,a6i,me,ok in results:
        print(f"    slot={float(x):.8f}  D_S={float(d):.3e}  |A6/i|={float(abs(a6i)):.6e}  formula==BG:{ok}")
    return results

tests=[
    ([F(2),F(3),F(4),F(5)], 3, (0,3,4)),
    ([F(-3),F(5),F(2),F(7)], 2, (1,2,5)),
    ([F(2),F(9),F(-4),F(5)], 0, (0,1,2)),
]
allok=True
for base,slot,S in tests:
    print(f"family base={base} vary slot {slot}, subset S={S}:")
    br=find_and_probe(base,slot,S)
    if br is None:
        print("  no genuine D_S crossing found in range"); continue
    res=probe(base,slot,S,br[0],br[1])
    for x,d,a6i,me,ok in res:
        if not ok: allok=False
print("\nALL near-genuine-pole points formula==BG:", allok)
