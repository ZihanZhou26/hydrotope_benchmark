#!/usr/bin/env python3
"""Dead-simple EXACT tie-breaker: is A_6(t) a polynomial on the F-constant slice?
Fit exact polynomial of degree d through d+1 in-chamber points; check it predicts
6 more EXACTLY.  Sweep d.  Unambiguous exact rational arithmetic, small degrees."""
from fractions import Fraction as Fr
from itertools import combinations
import sympy as sp
import harness as h

SIG=[-1,-1,-1,1,1,1]
def mixsig(oms):
    w=[None]+[Fr(x) for x in oms]; s=[]
    for r in range(1,6):
        for S in combinations(range(1,7),r):
            mns=[i for i in S if SIG[i-1]<0]; pls=[i for i in S if SIG[i-1]>0]
            if mns and pls:
                v=sum(Fr(SIG[i-1])*w[i]**2 for i in S)
                s.append(0 if v==0 else (1 if v>0 else -1))
    return tuple(s)

# in-chamber exact samples on F-const slice (vary w4,w5)
nodes=[]; ref=None
for k in range(1,80):
    tv=Fr(k,50)            # t in (0.02, 1.58); modest spacing
    try:
        oim,oms,_=h.on_shell([Fr(2),Fr(3),Fr(5)+tv,Fr(7)-tv],SIG)
    except Exception:
        continue
    sg=mixsig(oms)
    if ref is None: ref=sg
    if sg!=ref:
        print(f"chamber wall between t< {tv}; stopping (have {len(nodes)})"); break
    nodes.append((sp.Rational(tv.numerator,tv.denominator),
                  sp.Rational(oim.numerator,oim.denominator)))
print("in-chamber exact nodes:", len(nodes))
xs=[x for x,_ in nodes]; ys=[y for _,y in nodes]

for d in range(0, min(25, len(xs)-7)+1):
    V=sp.Matrix([[xs[k]**p for p in range(d+1)] for k in range(d+1)])
    c=V.LUsolve(sp.Matrix(ys[:d+1]))
    ok=all(sum(c[p]*xs[k]**p for p in range(d+1))==ys[k] for k in range(d+1, d+7))
    if ok:
        nz=max([p for p in range(d+1) if c[p]!=0], default=0)
        print(f"  A_6 IS polynomial on slice: degree {nz} (verified holdout)")
        break
else:
    print("  A_6 NOT polynomial up to degree", min(25,len(xs)-7))

# ALSO: check on a NON-F-const slice (vary only w4, S_F varies) -> S_F denominators
print("\n--- non-F-const slice (vary only w4; S_F varies) ---")
nodes2=[]; ref2=None
for k in range(1,80):
    tv=Fr(k,50)
    try:
        oim,oms,_=h.on_shell([Fr(2),Fr(3),Fr(5)+tv,Fr(7)],SIG)
    except Exception:
        continue
    sg=mixsig(oms)
    if ref2 is None: ref2=sg
    if sg!=ref2: break
    nodes2.append((sp.Rational(tv.numerator,tv.denominator),
                   sp.Rational(oim.numerator,oim.denominator)))
print("nodes:", len(nodes2))
xs2=[x for x,_ in nodes2]; ys2=[y for _,y in nodes2]
SF=Fr(2)+Fr(3)+Fr(7)  # +w4(t): S_F = 12 + (5+t) = 17+t  (varies!)
t=sp.Symbol('t')
for p in range(0, 9):
    # test A_6*(17+t)^p polynomial
    zs=[ys2[k]*(sp.Rational(17)+xs2[k])**p for k in range(len(xs2))]
    found=False
    for d in range(0, min(20,len(xs2)-7)+1):
        V=sp.Matrix([[xs2[k]**q for q in range(d+1)] for k in range(d+1)])
        c=V.LUsolve(sp.Matrix(zs[:d+1]))
        if all(sum(c[q]*xs2[k]**q for q in range(d+1))==zs[k] for k in range(d+1,d+7)):
            print(f"  A_6*(S_F)^{p} polynomial, degree {max([q for q in range(d+1) if c[q]!=0],default=0)}"); found=True; break
    if found: break
else:
    print("  A_6*S_F^p NOT polynomial for p=0..8")
