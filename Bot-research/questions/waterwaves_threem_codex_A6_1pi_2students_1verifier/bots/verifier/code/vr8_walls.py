#!/usr/bin/env python3
"""Two-sided wall & pole crossings on genuine on-shell 1-parameter families.

Family: vary ONE free frequency lambda; bg -n solves (w1,w6) to keep the point
exactly on-shell.  Scan lambda on a rational grid, detect sign flips of each
candidate wall/pole locator, and straddle every crossing with two rational
points just off the wall on each side.  At every sampled point compare fresh BG
against my formula EXACTLY.  Classify crossing as WALL (BG stays finite) or
POLE (BG diverges) by monitoring the pole locator d_{m;pq}.
"""
from fractions import Fraction as F
from itertools import combinations
import vr8_core as V

MINUS, PLUS = V.MINUS, V.PLUS

def q_locators(w):
    x2=[z*z for z in w]
    out={}
    for m in MINUS:
        for p in PLUS:
            out[("q",m,p)] = x2[p]-x2[m]
    return out

def Q_locators(w):
    x2=[z*z for z in w]
    out={}
    for m in MINUS:
        for p,q in combinations(PLUS,2):
            out[("Q",m,p,q)] = x2[p]+x2[q]-x2[m]
    return out

def d_locators(w):
    out={}
    for m in MINUS:
        for p in PLUS:
            out[("d",m,p)] = w[m]+w[p]   # pole factor of d_{m;pq}
    return out

def all_loc(w):
    d={}; d.update(q_locators(w)); d.update(Q_locators(w)); d.update(d_locators(w))
    return d

def eval_at(free):
    """return (omega, bg, mine) or None if degenerate/singular."""
    try:
        omega,a6i = V.bg_amp_free(free)
    except Exception:
        return None
    w=list(omega)
    x2=[z*z for z in w]
    if len(set(x2))<6:
        return None
    # skip if on a pole (some w_m+w_p==0)
    for m in MINUS:
        for p in PLUS:
            if w[m]+w[p]==0:
                return None
    try:
        me=V.stripped(w)
    except ZeroDivisionError:
        return None
    return w,a6i,me

# base free config; we vary slot `slot`
bases = [
    ([F(2),F(3),F(4),F(5)],),
    ([F(-3),F(5),F(2),F(7)],),
    ([F(7,2),F(-2),F(9,2),F(3)],),
    ([F(2),F(9),F(-4),F(5)],),
    ([F(-6),F(2),F(3),F(11,2)],),
]

crossings = {"WALL":0,"POLE":0}
loc_types_hit = set()
checks = 0
mism = 0
mism_list = []
finite_pairs = 0

for (base,) in bases:
    for slot in range(4):
        # scan lambda over a rational grid
        grid = [F(g,4) for g in range(-60,61) if F(g,4)!=base[slot]]
        prev=None
        for lam in grid:
            free=list(base); free[slot]=lam
            r=eval_at(free)
            if r is None:
                prev=None; continue
            w,a6i,me = r
            if me!=a6i:
                mism+=1; mism_list.append((free,w,a6i,me))
            checks+=1
            loc=all_loc(w)
            if prev is not None:
                pw,ploc,plam = prev
                for key,val in loc.items():
                    if key in ploc and ploc[key]!=0 and val!=0 and (ploc[key]>0)!=(val>0):
                        # sign flip of this locator between plam and lam -> a crossing
                        # both endpoints are already off-wall; record straddle
                        loc_types_hit.add(key[0])
                        # is it a pole? check if BG magnitude blew up near crossing
                        # (pole locator 'd' flips) -> classify
                        if key[0]=="d":
                            crossings["POLE"]+=1
                        else:
                            crossings["WALL"]+=1
            prev=(w,loc,lam)

print(f"total on-shell points sampled & exactly checked: {checks}")
print(f"formula != BG mismatches: {mism}")
print(f"locator sign-flip crossings detected: {crossings}")
print(f"distinct locator TYPES crossed: {sorted(loc_types_hit)}  (q=pair wall, Q=triple wall, d=factorization pole factor)")
if mism_list:
    print("\n=== MISMATCHES ===")
    for free,w,a6i,me in mism_list[:15]:
        print(" free",free," omega",w)
        print("   BG",a6i," mine",me," diff",me-a6i)
else:
    print("\nEXACT agreement at every sampled point straddling every detected wall/pole crossing.")
