#!/usr/bin/env python3
"""Driver for round-3 independent verification. Prints a structured report."""
import sys, os, itertools
from fractions import Fraction as F
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from oracle import amp_from_omega_sigma
from pole_verify import (P_pole, C_of, Delta_of, SIGMA, MINUS, PLUS,
                         solve_onshell, word_of, Lscale)
from round3_verify import (A6_over_i, R_spline, reconstruct_H24,
                           compact_same_energy_H, P_s1, fit_poly, peval)

def line(): print("-"*70)

# =====================================================================
# V1: FRESH-BUILD FOUNDATION -- R = A6/i - P_pole denominator-free, all 8 words
# =====================================================================
print("="*70); print("V1  Foundation on fresh build: R=A6/i-P_pole is denom-free (deg-8)")
line()
# scan integer + rational free coords, cover as many of the 8 words as possible
seeds = []
for b in range(1, 7):
    for c in range(1, 7):
        for d in range(1, 7):
            for e in range(1, 7):
                seeds.append((F(b), F(c), F(d), F(e)))
# add some rational coords
rat = [(F(3,2),F(5),F(7,3),F(4)),(F(11,4),F(2),F(9,5),F(13,3)),
       (F(1,2),F(6),F(13,4),F(5,3)),(F(7),F(2,3),F(11,5),F(3,2)),
       (F(8,3),F(5,2),F(1),F(9,4)),(F(2),F(11,3),F(4),F(7,6))]
seeds += rat
words = {}
tested_int = 0; ok_int = 0; tested_rat = 0; ok_rat = 0; skipped = 0
seen = set()
for (b,c,d,e) in seeds:
    w = solve_onshell(b,c,d,e)
    if w is None: continue
    if any(x==0 for x in w) or C_of(w)==0 or Delta_of(w)==0:
        skipped+=1; continue
    aw=[abs(x) for x in w]
    if len(set(aw))<6: skipped+=1; continue  # skip on walls
    key = tuple(sorted(str(x) for x in w))
    if key in seen: continue
    seen.add(key)
    wd = word_of(w)
    try:
        R = R_spline(w)
    except Exception as ex:
        skipped+=1; continue
    L = Lscale(w)
    scaled = R * F(L)**8
    integral = (scaled.denominator == 1)
    words.setdefault(wd, 0); words[wd]+=1
    if L==1:
        tested_int+=1; ok_int += 1 if (R.denominator==1) else 0
    else:
        tested_rat+=1; ok_rat += 1 if integral else 0
print(f"integer-omega points: {ok_int}/{tested_int} have R integral")
print(f"rational-omega points: {ok_rat}/{tested_rat} have L^8*R integral")
print(f"skipped (walls/degenerate): {skipped}")
print(f"distinct 8-word chambers hit: {len(words)} -> {sorted(words)}")
print("V1 PASS" if (ok_int==tested_int and ok_rat==tested_rat and len(words)>=8) else "V1 CHECK")

# =====================================================================
# V2: anchor wall H24 = 12622720/27, order 1, continuity
# =====================================================================
print(); print("="*70); print("V2  Anchor pair-wall jump: order-1, H24(anchor)=12622720/27")
line()
r = reconstruct_H24(F(10), F(2), F(3))
print("wall omega:", r.get('wall_omega'))
print("left cell ok:", r.get('left_ok'), "holdouts:", r.get('left_holdouts'))
print("right cell ok:", r.get('right_ok'), "holdouts:", r.get('right_holdouts'))
print("continuity R_L(t0)-R_R(t0):", r.get('continuity'), "(expect 0 => order>=1)")
print("reconstructed H24:", r.get('H24'), " expected 12622720/27 =", F(12622720,27))
print("V2 PASS" if r.get('H24')==F(12622720,27) and r.get('continuity')==0 else "V2 CHECK")

# =====================================================================
# V3: compact same-energy brick + FOUR-LEG beta selector
# =====================================================================
print(); print("="*70)
print("V3  Compact same-energy H24 with four-leg beta; discriminate vs minus-only")
line()
# environments (B,c,e). Choose so the minimizing non-primary leg is a MINUS leg
# in some, a PLUS leg in others.
envs = [
    ("A minus-min", F(10), F(2), F(3)),
    ("B plus-min ", F(10), F(4), F(1)),
    ("C plus-min ", F(12), F(5), F(1)),
    ("D minus-min", F(14), F(2), F(5)),
    ("E plus-min ", F(16), F(6), F(1)),
]
v3_all_four = True; v3_discriminated = False
for name,B,c,e in envs:
    r = reconstruct_H24(B,c,e)
    w = r.get('wall_omega')
    if w is None or not (r.get('left_ok') and r.get('right_ok')):
        print(f"[{name}] reconstruction FAILED cell_ok L={r.get('left_ok')} R={r.get('right_ok')}")
        continue
    Hbg = r['H24']
    Hfour = compact_same_energy_H(w, 1, 3, 'four')   # m=leg2 idx1, p=leg4 idx3
    Hminus = compact_same_energy_H(w, 1, 3, 'minus')
    # which leg is the four-leg minimizer?
    nonprim = {1:'w1(min)',2:'w3(min)',4:'w5(plus)',5:'w6(plus)'}
    mags = {i:abs(w[i]) for i in (0,2,4,5)}
    argmin = min(mags, key=lambda i:mags[i])
    minlabel = {0:'w1(minus)',2:'w3(minus)',4:'w5(plus)',5:'w6(plus)'}[argmin]
    ok_four = (Hbg==Hfour)
    ok_minus = (Hbg==Hminus)
    v3_all_four = v3_all_four and ok_four
    if Hfour != Hminus:
        v3_discriminated = True
    print(f"[{name}] wall={w}")
    print(f"    beta-argmin = {minlabel}   H_BG={Hbg}")
    print(f"    four-leg   ={Hfour}  match={ok_four}")
    print(f"    minus-only ={Hminus}  match={ok_minus}  (differ from four: {Hfour!=Hminus})")
print("V3 four-leg matches all:", v3_all_four, "| discriminating env present:", v3_discriminated)

# =====================================================================
# V4: H_mp is a spline -- P(u) <-> P(6-u) exchange across Q_{3;45}=61-12u
# =====================================================================
print(); print("="*70)
print("V4  Nested-spline verdict: H24(u) = P(u) then P(6-u) after Q_{3;45} flips")
line()
# slice B=10, c=u, e=6-u. Q_{3;45}=61-12u flips at u=61/12~5.083
tests = [("left ", F(7,6)), ("left ", F(2)),
         ("right", F(7)), ("right", F(9)), ("right", F(11,2))]
v4_ok = True
for side,u in tests:
    r = reconstruct_H24(F(10), u, F(6)-u)
    w = r.get('wall_omega')
    if w is None or not (r.get('left_ok') and r.get('right_ok')):
        print(f"u={u}: reconstruction FAILED  L={r.get('left_ok')} R={r.get('right_ok')}")
        v4_ok=False; continue
    Hbg = r['H24']
    Pu = P_s1(u); P6u = P_s1(F(6)-u)
    Hfour = compact_same_energy_H(w, 1, 3, 'four')
    match_side = 'P(u)' if Hbg==Pu else ('P(6-u)' if Hbg==P6u else 'NEITHER')
    print(f"u={str(u):>6} [{side}] H_BG={Hbg}")
    print(f"        H_BG-P(u)  ={Hbg-Pu}")
    print(f"        H_BG-P(6-u)={Hbg-P6u}   -> matches {match_side}; four-leg-formula match={Hbg==Hfour}")
    # expectation: left -> P(u); right -> P(6-u); four-leg formula always matches
    exp = Pu if side=='left ' else P6u
    if Hbg!=exp or Hbg!=Hfour:
        v4_ok=False
print("V4 PASS" if v4_ok else "V4 CHECK")
print(); print("="*70); print("done")
