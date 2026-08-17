#!/usr/bin/env python3
"""Bulletproof R_spline: (a) P_pole second (single-cubic) form must agree with
form 1; (b) R_spline dual-S_3 symmetric; both at line-2 points where the Q-brick
seemed to fail. If both pass, R_spline (hence the line-2 jump) is trustworthy."""
import itertools
from fractions import Fraction as F
from r5_core import (amp_from_omega, P_pole, R_spline, Hblock, pos, line, M, P, _fmt)

def C_val(om): return om[0]*om[1]*om[2] + om[3]*om[4]*om[5]

def P_pole_form2(omega):
    """Single-cubic form (F9 equivalent): -32/C sum_{Q_T>0} w_m w_pbar (w_m+w_pbar) Q^2 H H."""
    omega=[F(w) for w in omega]
    C=C_val(omega); tot=F(0)
    for m in M:
        mp=[x for x in M if x!=m]
        for pq in itertools.combinations(P,2):
            p,q=pq; pbar=[x for x in P if x not in pq][0]
            Q=omega[p]**2+omega[q]**2-omega[m]**2
            if Q<=0: continue
            H1=Hblock(min(omega[m]**2,Q),p,q,omega)
            H2=Hblock(min(omega[pbar]**2,Q),mp[0],mp[1],omega)
            tot+=omega[m]*omega[pbar]*(omega[m]+omega[pbar])*Q*Q*H1*H2
    return -32*tot/C

def check_point(om,label):
    p1=P_pole(om); p2=P_pole_form2(om)
    r=R_spline(om)
    # dual-S3 symmetry: permute minus legs (0,1,2) and plus legs (3,4,5)
    import itertools as it
    sym_ok=True
    base=amp_from_omega(om)-P_pole(om)
    for pm in it.permutations([0,1,2]):
        for pp in it.permutations([3,4,5]):
            perm=[om[pm[0]],om[pm[1]],om[pm[2]],om[pp[0]],om[pp[1]],om[pp[2]]]
            if R_spline(perm)!=base: sym_ok=False
    print(f"[{label}] P_pole form1==form2? {p1==p2}  R_spline denom={F(r).denominator}  dualS3_sym? {sym_ok}")

# line 2 right-side points (t in (-0.3956,0.5)); pick a couple on-shell
Pv=[8,2,-3,-5,4,-6]; dv=[-3,-2,1,3,-1,2]
for t in [F(1,10), F(3,10), F(-2,10)]:
    om=line(Pv,dv,t)
    check_point(om, f"line2 t={_fmt(t)}")
# canonical right point
Pc=[8,2,-3,-5,4,-6]; dc=[-2,1,0,2,-1,0]
check_point(line(Pc,dc,F(4,10)), "canon t=2/5")
