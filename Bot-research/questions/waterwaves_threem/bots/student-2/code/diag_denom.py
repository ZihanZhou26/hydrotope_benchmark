#!/usr/bin/env python3
"""Diagnostics for the denominator machinery.
(1) n=5 control: A_5 is polynomial -> slice test must report POLYNOMIAL.
(2) n=6 full-divisor test: A_6 times the product of ALL BG divisors
    ( |k_S| for every subset, and (w_S^2-|k_S|) for every subset ) MUST be
    polynomial.  If this fails, the test machinery (chamber/degree) is at fault.
"""
from fractions import Fraction as Fr
from itertools import combinations
import sympy as sp
import harness as h

def in_chamber_nodes(signs, basefree, vary, denom, count, scale_lo=1):
    """vary=(legpos_i,legpos_j) among the free legs (0-indexed in basefree),
    held-sum slice.  Returns list of (t, free, omega)."""
    n=len(signs)
    def mixsig(oms):
        w=[None]+[Fr(x) for x in oms]; s=[]
        for r in range(1,n):
            for S in combinations(range(1,n+1),r):
                mns=[i for i in S if signs[i-1]<0]; pls=[i for i in S if signs[i-1]>0]
                if mns and pls:
                    v=sum(Fr(signs[i-1])*w[i]**2 for i in S)
                    s.append(0 if v==0 else (1 if v>0 else -1))
        return tuple(s)
    out=[]; ref=None
    i,j=vary
    for k in range(1,count+200):
        t=Fr(k,denom)
        free=list(basefree)
        free[i]=Fr(basefree[i])+t; free[j]=Fr(basefree[j])-t
        try:
            oim,oms,_=h.on_shell(free,signs)
        except Exception:
            continue
        sg=mixsig(oms)
        if ref is None: ref=sg
        if sg!=ref: continue
        out.append((t,free,oms,oim))
        if len(out)>=count: break
    return out

def poly_test(nodes, Dfun, label, dmax=80):
    xs=[sp.Rational(t.numerator,t.denominator) for t,_,_,_ in nodes]
    ys=[sp.Rational((oim*Dfun(oms)).numerator,(oim*Dfun(oms)).denominator)
        for _,_,oms,oim in nodes]
    d=min(dmax,len(xs)-8)
    Vm=sp.Matrix([[xs[k]**p for p in range(d+1)] for k in range(d+1)])
    c=Vm.LUsolve(sp.Matrix(ys[:d+1]))
    ok=all(sp.simplify(sum(c[p]*xs[k]**p for p in range(d+1))-ys[k])==0
           for k in range(d+1,len(xs)))
    truedeg=max([p for p in range(d+1) if c[p]!=0],default=0) if ok else None
    print(f"  [{label}] polynomial?={ok} deg={truedeg} (fit {d}, {len(xs)} pts)")
    return ok

# (1) n=5 control
print("=== n=5 control (A_5 is polynomial) ===")
s5=[-1,-1,-1,1,1]
nodes5=in_chamber_nodes(s5,[Fr(2),Fr(3),Fr(5)],(1,2),300,90)  # vary legs 3,4 (free idx1,2)
poly_test(nodes5, lambda o: Fr(1), "n5 D=1")

# (2) n=6 full-divisor test
print("=== n=6 full-divisor product (must be polynomial) ===")
s6=[-1,-1,-1,1,1,1]
nodes6=in_chamber_nodes(s6,[Fr(2),Fr(3),Fr(5),Fr(7)],(2,3),300,90) # vary legs4,5
def Dfull(o):
    w=[None]+[Fr(x) for x in o]
    prod=Fr(1)
    for r in range(1,6):
        for S in combinations(range(1,7),r):
            kS=sum(Fr(s6[i-1])*w[i]**2 for i in S)
            wS=sum(w[i] for i in S)
            absk=abs(kS)
            if absk!=0: prod*=absk
            propden=wS**2-absk    # w_S^2 - |k_S|
            if propden!=0: prod*=propden
    return prod
poly_test(nodes6, Dfull, "n6 Dfull", dmax=80)
