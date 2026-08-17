#!/usr/bin/env python3
"""Explicit two-sided factorization-pole crossings d_{m;pq}=2(w_m+w_p)(w_m+w_q)=0.

Vary a free plus-leg so that (w_m + w_p) sweeps through 0 while the channel is
active.  Confirm (a) BG actually diverges at the locus (genuine pole), and
(b) my formula == fresh BG EXACTLY at rational points arbitrarily close on
BOTH sides.  This is the real pole-prescription test (the 1/d in P_pole).
"""
from fractions import Fraction as F
from itertools import combinations
import vr8_core as V

MINUS,PLUS=V.MINUS,V.PLUS

def eval_at(free):
    try:
        omega,a6i=V.bg_amp_free(free)
    except Exception:
        return None
    w=list(omega); x2=[z*z for z in w]
    if len(set(x2))<6: return None
    try:
        me=V.stripped(w)
    except ZeroDivisionError:
        return None
    return w,a6i,me

def pole_factors(w):
    out={}
    for m in MINUS:
        for p in PLUS:
            out[(m,p)]=w[m]+w[p]
    return out

# We approach several distinct pole loci by varying slot 2 (=w_4) toward -w_2, etc.
# free slots: 0->w2, 1->w3, 2->w4, 3->w5.  w1,w6 solved by bg.
targets = [
    # (base free, slot to vary, target value where a pole factor -> 0, label)
    ([F(3),F(5),None,F(4)], 2, F(-3), "w2+w4=0"),
    ([F(3),F(5),None,F(4)], 2, F(-5), "w3+w4=0"),
    ([F(3),F(7),F(4),None], 3, F(-3), "w2+w5=0"),
    ([F(3),F(7),F(4),None], 3, F(-7), "w3+w5=0"),
    ([F(5),F(2),None,F(6)], 2, F(-5), "w2+w4=0 (b)"),
]

eps_list=[F(1,10),F(1,50),F(1,500),F(1,5000)]
checks=0; mism=0; mism_list=[]
genuine_poles=0
tested_loci=0
for base,slot,tgt,label in targets:
    # magnitude of BG on each side, and exact match
    side_mag={}
    ok_here=True
    diverges=True
    prev_absL=prev_absR=None
    seq=[]
    for eps in eps_list:
        for sign in (-1,1):
            free=list(base); free[slot]=tgt+sign*eps
            r=eval_at(free)
            if r is None:
                continue
            w,a6i,me=r
            checks+=1
            if me!=a6i:
                mism+=1; mism_list.append((label,free,w,a6i,me)); ok_here=False
            seq.append((sign,eps,abs(a6i)))
    # check divergence: |A6| should grow as eps shrinks on at least one side
    left=sorted([(e,mag) for s,e,mag in seq if s<0])
    right=sorted([(e,mag) for s,e,mag in seq if s>0])
    def growing(lst):
        vals=[m for e,m in lst]
        return len(vals)>=2 and vals[0]>vals[-1]*10  # smallest eps has >=10x larger |A6|
    tested_loci+=1
    div = growing(left) or growing(right)
    if div: genuine_poles+=1
    print(f"[{label}] exact-match both sides: {ok_here}   BG diverges at locus: {div}")
    if left:  print(f"    left  |A6|: "+", ".join(f"eps={e} ->{float(m):.3e}" for e,m in left))
    if right: print(f"    right |A6|: "+", ".join(f"eps={e} ->{float(m):.3e}" for e,m in right))

print(f"\ntotal near-pole points exactly checked: {checks}")
print(f"formula != BG mismatches: {mism}")
print(f"loci where BG genuinely diverges (real factorization pole): {genuine_poles}/{tested_loci}")
if mism_list:
    print("\n=== MISMATCHES ===")
    for label,free,w,a6i,me in mism_list[:15]:
        print(" ",label,free,w); print("    BG",a6i,"mine",me,"diff",me-a6i)
else:
    print("EXACT agreement at every near-pole point on both sides.")
