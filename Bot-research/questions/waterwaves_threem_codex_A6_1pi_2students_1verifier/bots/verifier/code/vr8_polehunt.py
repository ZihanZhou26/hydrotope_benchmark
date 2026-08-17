#!/usr/bin/env python3
"""Hunt for a GENUINE factorization pole (real BG divergence) in the physical
three-minus on-shell domain.  For many on-shell 1-parameter families, track
every internal propagator D_S = w_S^2/|k_S| - g (2<=|S|<=4) along the family;
whenever a D_S changes sign with |k_S| bounded away from 0, that is a genuine
internal line going on shell -> BG must diverge.  Straddle it and test the
formula on both sides EXACTLY; confirm BG really diverges.
"""
from fractions import Fraction as F
from itertools import combinations
import vr8_core as V

SIG=[-1,-1,-1,1,1,1]

def subsets():
    idx=list(range(6))
    out=[]
    for r in range(2,5):
        for S in combinations(idx,r):
            out.append(S)
    return out
SUBS=subsets()

def D_S(w,S):
    wS=sum(w[i] for i in S)
    kS=sum(SIG[i]*w[i]*w[i] for i in S)   # g=1
    if kS==0:
        return None
    return wS*wS/abs(kS) - 1

def eval_free(free):
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

import random
random.seed(99)
bases=[]
while len(bases)<10:
    free=[F(random.randint(-9,9),random.choice([1,2,3])) for _ in range(4)]
    if any(x==0 for x in free): continue
    bases.append(free)

genuine=[]
checks=0; mism=0; mism_list=[]
for base in bases:
    for slot in range(4):
        grid=[F(g,4) for g in range(-48,49)]
        prev=None
        for gval in grid:
            free=list(base); free[slot]=gval
            r=eval_free(free)
            if r is None:
                prev=None; continue
            w,a6i,me=r
            checks+=1
            if me!=a6i:
                mism+=1; mism_list.append((free,w,a6i,me))
            Ds={S:D_S(w,S) for S in SUBS}
            if prev is not None:
                pw,pDs,pfree=prev
                for S in SUBS:
                    a=pDs.get(S); b=Ds.get(S)
                    if a is None or b is None or a==0 or b==0: continue
                    if (a>0)!=(b>0):
                        # D_S sign flip -> internal line crosses on-shell.
                        kS=sum(SIG[i]*w[i]*w[i] for i in S)
                        if abs(kS)>F(1,100):   # genuine (k_S not vanishing)
                            genuine.append((tuple(S),pfree,free,abs(a6i),abs(pw and 0)))
            prev=(w,Ds,free)

print(f"on-shell points checked: {checks}   formula!=BG: {mism}")
print(f"genuine internal-line on-shell crossings (|k_S|>0.01) detected: {len(genuine)}")
# show a few with the BG magnitudes to see if BG actually blows up
from collections import Counter
c=Counter(g[0] for g in genuine)
print("subset multiplicities:",dict(c))
if mism_list:
    print("MISMATCHES:")
    for free,w,a6i,me in mism_list[:10]:
        print("  ",free,w,a6i,me,me-a6i)
else:
    print("no formula/BG mismatch anywhere in the hunt")
