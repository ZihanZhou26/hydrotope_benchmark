#!/usr/bin/env python3
"""Univariate rational fit of A_6 on a slice: A_6(t)=P(t)/Q(t).
Find minimal (degP,degQ). Identifies whether A_6 is rational (degQ>0) and the
denominator structure."""
from fractions import Fraction as F
import harness as h, chambers_n6 as cn
from exactfit import exact_solve
import modfit as mf
SIG=[-1,-1,-1,1,1,1]
base=(F(-4,5),F(-13,5),F(-47,10),F(47,10)); dirn=(F(0),F(0),F(1),F(0))
rawsig=cn.wall_signs([w*w for w in cn.solve_squares(base)])
pts=[]
for k in range(-60,61):
    t=F(k,60); free=tuple(base[i]+t*dirn[i] for i in range(4))
    if any(x==0 for x in free): continue
    oms=cn.solve_squares(free)
    if oms is None or any(w==0 for w in oms): continue
    sq=[w*w for w in oms]; ws=cn.wall_signs(sq)
    if ws is None or ws!=rawsig: continue
    try: im,_,_=h.on_shell(list(free),SIG)
    except Exception: continue
    pts.append((t,im,oms))
print("slice pts:",len(pts))
# rational fit: P(t)=sum_{i<=dP} p_i t^i, Q(t)=1+sum_{j=1..dQ} q_j t^j ; A*Q=P
def try_fit(dP,dQ):
    rows=[];ys=[]
    for (t,im,oms) in pts:
        # unknowns: p_0..p_dP (dP+1), q_1..q_dQ (dQ); eqn: sum p_i t^i - im*sum q_j t^j = im*1
        row=[t**i for i in range(dP+1)]+[-im*t**j for j in range(1,dQ+1)]
        rows.append(row); ys.append(im)
    nun=dP+1+dQ
    if len(rows)<nun+5: return None
    sol=exact_solve(rows[:nun],ys[:nun])
    if sol is None: return None
    ok=bad=0
    for row,y in zip(rows[nun:],ys[nun:]):
        if sum(c*v for c,v in zip(sol,row))==y: ok+=1
        else: bad+=1
    return (ok,bad,sol)
for dQ in range(0,9):
    dP=8  # try numerator degree 8 first (A6 homogeneous deg 8 -> on slice <=8? maybe higher)
    for dP in [dQ+0, dQ+2, dQ+4, dQ+6, dQ+8, 8, 10, 12]:
        r=try_fit(dP,dQ)
        if r and r[1]==0 and r[0]>0:
            ok,bad,sol=r
            qs=sol[dP+1:]
            print(f"FIT: degP={dP} degQ={dQ}  held-out {ok}/0  Q coeffs(q1..)={[str(x) for x in qs]}")
            break
    else:
        continue
    break
