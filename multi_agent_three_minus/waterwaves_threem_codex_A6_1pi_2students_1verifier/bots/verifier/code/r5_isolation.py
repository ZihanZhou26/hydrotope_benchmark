#!/usr/bin/env python3
"""Check wall isolation at t0: are OTHER q_{mp}/Q_{m;pq} walls also ~0 at the
crossing? If so, dR mixes jumps and dR/Q^3 is contaminated."""
import itertools
from fractions import Fraction as F
from r5_lines import Q_poly, q_mp
from r5_core import line, Q_T_val, M, P
import numpy as np

def walls_at(Pvec,dvec,t0):
    om=line(Pvec,dvec,F(t0).limit_denominator(10**7))
    print(f" t0={t0:+.5f}")
    for m in M:
        for p in P:
            v=float(q_mp(om,m,p))
            if abs(v)<1e-2: print(f"   q_{m+1}{p+1} = {v:+.4f}  <-- near zero")
    for m in M:
        for p,q in itertools.combinations(P,2):
            v=float(Q_T_val(om,m,p,q))
            if abs(v)<1e-2: print(f"   Q_{m+1};{p+1}{q+1} = {v:+.4f}  <-- near zero")

def target_root(Pvec,dvec,m,p,q,near):
    Qp=Q_poly(Pvec,dvec,m,p,q)
    roots=[r.real for r in np.roots([float(c) for c in Qp][::-1]) if abs(r.imag)<1e-9]
    return min(roots,key=lambda r:abs(r-near))

print("CANONICAL line (worked): ch(1;4,6) t0=0.25")
walls_at([8,2,-3,-5,4,-6],[-2,1,0,2,-1,0], 0.25)

print("\nLINE2 ch(1;4,6) t0=-0.3956 (failed):")
walls_at([8,2,-3,-5,4,-6],[-3,-2,1,3,-1,2], -0.39564392373896)

print("\nLINE1 ch(1;5,6) t0=0.3094 (failed):")
walls_at([8,2,-3,-5,4,-6],[-3,-3,-3,3,3,3], 0.30940107675850304)
