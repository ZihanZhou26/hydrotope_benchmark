#!/usr/bin/env python3
"""Test the ALL-n denominator conjecture:
    A_n^{3-} * prod_{i in minus, j in plus} (w_i + w_j)  is a POLYNOMIAL,
i.e. A_n = i 2^{n-1} g^{3-n} N_n / prod_{i in minus,j in plus}(w_i+w_j).
Check at n=6 (fresh F-const slice) and n=7 (12 mixed pairs).  Exact, in-chamber.
"""
from fractions import Fraction as Fr
from itertools import combinations
import sympy as sp
import harness as h

def mixsig(oms, signs):
    n=len(signs); w=[None]+[Fr(x) for x in oms]; s=[]
    for r in range(1,n):
        for S in combinations(range(1,n+1),r):
            mns=[i for i in S if signs[i-1]<0]; pls=[i for i in S if signs[i-1]>0]
            if mns and pls:
                v=sum(Fr(signs[i-1])*w[i]**2 for i in S)
                s.append(0 if v==0 else (1 if v>0 else -1))
    return tuple(s)

def Dmix(oms, signs):
    w=[None]+[Fr(x) for x in oms]
    minus=[i for i in range(1,len(signs)+1) if signs[i-1]<0]
    plus=[i for i in range(1,len(signs)+1) if signs[i-1]>0]
    pr=Fr(1)
    for i in minus:
        for j in plus: pr*=(w[i]+w[j])
    return pr

def poly_fit(xs,ys,dmax=40):
    d=min(dmax,len(xs)-6)
    V=sp.Matrix([[xs[k]**q for q in range(d+1)] for k in range(d+1)])
    c=V.LUsolve(sp.Matrix(ys[:d+1]))
    ok=all(sum(c[q]*xs[k]**q for q in range(d+1))==ys[k] for k in range(d+1,len(xs)))
    if not ok: return None
    return max([q for q in range(d+1) if c[q]!=0],default=0)

def run(signs, basefree, vary, H, count, label):
    # F-const slice: vary[0]+=t/H, vary[1]-=t/H (positions are free-leg indices 0..len-1)
    ref=mixsig(h.on_shell([Fr(x) for x in basefree],signs)[1],signs)
    i,j=vary; data=[]
    for p in list(range(1,count))+list(range(-1,-count,-1)):
        free=[Fr(x) for x in basefree]; free[i]+=Fr(p,H); free[j]-=Fr(p,H)
        try: oim,oms,_=h.on_shell(free,signs)
        except Exception: continue
        if mixsig(oms,signs)!=ref: continue
        data.append((sp.Rational(p), sp.Rational(oim.numerator,oim.denominator), oms))
        if len(data)>=count: break
    xs=[x for x,_,_ in data]
    degAll=poly_fit(xs,[y*Dmix(o,signs) for _,y,o in data])
    degA  =poly_fit(xs,[y for _,y,_ in data])
    print(f"[{label}] nodes={len(data)}  A_n alone poly? {'deg '+str(degA) if degA is not None else 'NO(rational)'}"
          f"   A_n*prod_mixed poly? {'YES deg '+str(degAll) if degAll is not None else 'NO'}")

# n=6 fresh slice: vary plus legs 5,6 (free idx 3,4)
run([-1,-1,-1,1,1,1], [2,3,5,7], (3,2), 20, 70, "n=6 vary(5,4)")   # free legs: [w2,w3,w4,w5]; idx3=w5, idx2=w4
# n=7: minus 1,2,3 ; plus 4,5,6,7. free legs = w2..w6 (idx0..4). vary w5,w6 (idx3,4).
run([-1,-1,-1,1,1,1,1], [2,3,5,7,11], (3,4), 20, 60, "n=7 vary(w5,w6)")
