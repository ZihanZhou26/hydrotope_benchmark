#!/usr/bin/env python3
"""Map ALL wall crossings (q_{mp}=0, Q_{m;pq}=0), magnitude-order changes, and
BG poles along a given on-shell line, and print the wall-free window around a
target t0."""
import sys, itertools
from fractions import Fraction as F
from r5_core import line, Q_T_val, amp_from_omega, SingularError, M, P, _fmt

def q_mp(om,m,p): return om[p]**2 - om[m]**2   # 2-leg wall

def analyze(Pvec, dvec, t0, lo=-3, hi=3, steps=6000):
    print(f"line P={Pvec} d={dvec}, target t0={_fmt(t0)}")
    # collect sign-change locations for each wall on a fine float grid
    import numpy as np
    ts = [F(lo) + (F(hi)-F(lo))*F(2*i+1,2*steps) for i in range(steps)]  # offset: avoid exact zeros
    def sgn(x): return (x>0)-(x<0)
    walls = {}
    for m in M:
        for p in P:
            walls[f"q_{m+1}{p+1}"] = ("q",m,p)
    for m in M:
        for p,q in itertools.combinations(P,2):
            walls[f"Q_{m+1};{p+1}{q+1}"] = ("Q",m,p,q)
    crossings = []  # (t_approx, name)
    prev = {}
    magprev = None
    for t in ts:
        om = line(Pvec,dvec,t)
        for name,spec in walls.items():
            if spec[0]=="q": v = q_mp(om,spec[1],spec[2])
            else: v = Q_T_val(om,spec[1],spec[2],spec[3])
            s = sgn(v)
            if name in prev and prev[name]!=0 and s!=0 and s!=prev[name]:
                crossings.append((float(t), name))
            prev[name]=s
        magorder = tuple(sorted(range(6), key=lambda i: abs(om[i])))
        if magprev is not None and magorder!=magprev:
            crossings.append((float(t), f"MAGORDER->{tuple(x+1 for x in magorder)}"))
        magprev = magorder
    crossings.sort()
    print("crossings (approx t, wall):")
    for tt,nm in crossings:
        print(f"   t={tt:+.4f}  {nm}")
    # nearest crossings around t0
    t0f = float(t0)
    left = max([c for c in crossings if c[0] < t0f-1e-9], default=None, key=lambda c:c[0])
    right= min([c for c in crossings if c[0] > t0f+1e-9], default=None, key=lambda c:c[0])
    print(f"\n t0={t0f:+.4f}")
    print(f"  nearest crossing LEFT : {left}")
    print(f"  nearest crossing RIGHT: {right}")

if __name__=="__main__":
    analyze([8,2,-3,-5,4,-6],[-2,1,0,2,-1,0], F(1,4))
