#!/usr/bin/env python3
"""Explicit cross-term demo: mixed 2nd difference of N around (1=1)x(1=1) intersection.
Walls W1={a2=b4} (w4 near w2), W2={a3=b5} (w5 near w3). 4 corner chambers.
D(eps)=N(++)-N(+-)-N(-+)+N(--). Simple spline => D==0 identically; box spline => D ~ eps^2."""
from fractions import Fraction as F
import fastbg as FB, chambers_n6 as cn, inv
SIG=[-1,-1,-1,1,1,1]
def Nval(free):
    o=cn.solve_squares(free)
    if o is None or any(w==0 for w in o): return None
    r=FB.batch_onshell([(6,free,SIG)])[0]
    if r is None: return None
    e=inv.invariants(o); return F(r[1]*(e[2]+e[3]),32)
w2,w3=F(3),F(5)   # minus legs 2,3
ca,cb=F(3),F(5)   # w4 center=3(=w2 -> W1), w5 center=5(=w3 -> W2)
print("Mixed 2nd difference D(eps) around (1=1)x(1=1) intersection {a2=b4} & {a3=b5}:")
for eps in [F(1,10),F(1,20),F(1,40),F(1,80)]:
    pp=Nval([w2,w3,ca+eps,cb+eps]); pm=Nval([w2,w3,ca+eps,cb-eps])
    mp=Nval([w2,w3,ca-eps,cb+eps]); mm=Nval([w2,w3,ca-eps,cb-eps])
    if None in (pp,pm,mp,mm): print(f"  eps={eps}: oracle err"); continue
    D=pp-pm-mp+mm
    print(f"  eps={eps}: D={D}   D/eps^2={F(D, eps*eps)}   (D/eps^3={float(F(D,eps**3)):.4g})")
