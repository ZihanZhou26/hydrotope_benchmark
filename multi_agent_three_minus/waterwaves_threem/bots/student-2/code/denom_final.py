#!/usr/bin/env python3
"""Rock-solid confirmation that D = prod_{i in minus, j in plus}(w_i+w_j) is the
A_6 denominator, on a GENERIC slice (vary only w4 -> S_F varies).  Since
(w_1+w_6) = -S_F is itself one of the mixed pairs, A_6*prod_mixed must be
polynomial with NO extra S_F powers.  Also extract the numerator N and the
partial-fraction polynomial part."""
from fractions import Fraction as Fr
from itertools import combinations
import sympy as sp
import harness as h

S6=[-1,-1,-1,1,1,1]
def mixsig(oms):
    w=[None]+[Fr(x) for x in oms]; s=[]
    for r in range(1,6):
        for S in combinations(range(1,7),r):
            mns=[i for i in S if S6[i-1]<0]; pls=[i for i in S if S6[i-1]>0]
            if mns and pls:
                v=sum(Fr(S6[i-1])*w[i]**2 for i in S)
                s.append(0 if v==0 else (1 if v>0 else -1))
    return tuple(s)
def Dmix(oms):
    w=[None]+[Fr(x) for x in oms]; pr=Fr(1)
    for i in (1,2,3):
        for j in (4,5,6): pr*=(w[i]+w[j])
    return pr

# GENERIC slice: vary only w4 (S_F = 12 + w4 varies). base (2,3,5,7).
ref=mixsig(h.on_shell([Fr(2),Fr(3),Fr(5),Fr(7)],S6)[1])
data=[]
for p in list(range(1,60))+list(range(-1,-30,-1)):
    sh=Fr(p,20)
    try: oim,oms,_=h.on_shell([Fr(2),Fr(3),Fr(5)+sh,Fr(7)],S6)
    except Exception: continue
    if mixsig(oms)!=ref: continue
    data.append((sp.Rational(p), sp.Rational(oim.numerator,oim.denominator), oms))
    if len(data)>=80: break
print("generic-slice in-chamber nodes:", len(data))
xs=[x for x,_,_ in data]
ys_AD=[y*Dmix(o) for _,y,o in data]
def poly_fit(xs,ys,dmax=50):
    d=min(dmax,len(xs)-6)
    V=sp.Matrix([[xs[k]**q for q in range(d+1)] for k in range(d+1)])
    c=V.LUsolve(sp.Matrix(ys[:d+1]))
    ok=all(sum(c[q]*xs[k]**q for q in range(d+1))==ys[k] for k in range(d+1,len(xs)))
    if not ok: return None,None
    deg=max([q for q in range(d+1) if c[q]!=0],default=0)
    return deg,[c[q] for q in range(deg+1)]
deg,co=poly_fit(xs,ys_AD)
print(f"GENERIC slice: A_6 * prod_mixed(w_i+w_j) polynomial? deg={deg}")
# control: A_6 alone (should be rational -> not polynomial)
degA,_=poly_fit(xs,[y for _,y,_ in data])
print(f"  control A_6 alone polynomial? {'deg '+str(degA) if degA is not None else 'NO (rational)'}")
# control: A_6*S_F^8 (student-1's test) on this slice (should fail, since other mixed pairs remain)
SF=[Fr(2)+Fr(3)+(Fr(5)+Fr(x,20))+Fr(7) for x in [0]]  # placeholder
ys_SF=[y*(Fr(12)+Fr(5)+Fr(x,20))**8 for x,y,_ in data]
degSF,_=poly_fit(xs,ys_SF)
print(f"  control A_6*S_F^8 polynomial? {'deg '+str(degSF) if degSF is not None else 'NO (S_F alone insufficient)'}")
