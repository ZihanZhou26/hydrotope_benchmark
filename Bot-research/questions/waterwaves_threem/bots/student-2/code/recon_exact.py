#!/usr/bin/env python3
"""EXACT reduced denominator of A_6 on the in-chamber F-const slice.
Chamber shift-range ~ (-1.4, 3.4); use shift=p/10, integer param p in -13..33
(small integers -> cheap exact arithmetic).  Reconstruct A_6(p)=N(p)/D(p):
for each denom-degree b, fit N(deg a=b+M) & D(deg b) through a+b+1 nodes
(nullspace) and verify on the rest; smallest consistent b = deg D.  Factor D,
identify factors via |k_S|(shift), e2(shift), S_F(shift)."""
from fractions import Fraction as Fr
from itertools import combinations
import sympy as sp
import harness as h

SIG=[-1,-1,-1,1,1,1]; H=10
def mixsig(oms):
    w=[None]+[Fr(x) for x in oms]; s=[]
    for r in range(1,6):
        for S in combinations(range(1,7),r):
            mns=[i for i in S if SIG[i-1]<0]; pls=[i for i in S if SIG[i-1]>0]
            if mns and pls:
                v=sum(Fr(SIG[i-1])*w[i]**2 for i in S)
                s.append(0 if v==0 else (1 if v>0 else -1))
    return tuple(s)

nodes=[]; ref=None
for p in list(range(1,34))+list(range(-1,-14,-1)):
    sh=Fr(p,H)
    try:
        oim,oms,_=h.on_shell([Fr(2),Fr(3),Fr(5)+sh,Fr(7)-sh],SIG)
    except Exception:
        continue
    if ref is None:
        ref=mixsig(h.on_shell([Fr(2),Fr(3),Fr(5),Fr(7)],SIG)[1])
    if mixsig(oms)!=ref: continue
    nodes.append((sp.Integer(p), sp.Rational(oim.numerator,oim.denominator)))
print("nodes:", len(nodes), flush=True)
xs=[x for x,_ in nodes]; ys=[y for _,y in nodes]; NP=len(nodes)

def reconstruct(b, M=18):
    a=b+M
    need=a+b+1
    if need+3>NP: return None
    rows=[[xs[k]**i for i in range(a+1)]+[-ys[k]*xs[k]**j for j in range(b+1)] for k in range(need)]
    ns=sp.Matrix(rows).nullspace()
    if not ns: return None
    vec=ns[0]
    nco=[vec[i] for i in range(a+1)]; dco=[vec[a+1+j] for j in range(b+1)]
    if all(c==0 for c in dco): return None
    # verify on all nodes
    for k in range(NP):
        N=sum(nco[i]*xs[k]**i for i in range(a+1))
        D=sum(dco[j]*xs[k]**j for j in range(b+1))
        if N!=ys[k]*D: return None
    return nco,dco,a

t=sp.Symbol('t')
found=None
for b in range(0,16):
    r=reconstruct(b)
    print(f"  b={b}: {'CONSISTENT' if r else 'no'}", flush=True)
    if r: found=(b,)+r; break

if not found:
    print("no consistent denom degree <=15", flush=True)
else:
    b,nco,dco,a=found
    D=sp.expand(sum(dco[j]*t**j for j in range(b+1)))
    N=sp.expand(sum(nco[i]*t**i for i in range(a+1)))
    g=sp.gcd(N,D); D=sp.cancel(D/g); N=sp.cancel(N/g)
    print(f"\nMINIMAL degD={sp.degree(D,t)} degN={sp.degree(N,t)}", flush=True)
    print("D(param t) factored:", sp.factor(D), flush=True)
    # identify: shift = t/H
    sh=t/H
    w2,w3=sp.Integer(2),sp.Integer(3); w4=sp.Integer(5)+sh; w5=sp.Integer(7)-sh
    F=w2+w3+w4+w5; R=-w2**2-w3**2+w4**2+w5**2
    w1=-(F**2+R)/(2*F); w6=-(F**2-R)/(2*F)
    W={1:w1,2:w2,3:w3,4:w4,5:w5,6:w6}
    cand={}
    for r in range(1,6):
        for S in combinations(range(1,7),r):
            cand[('k',S)]=sp.expand(sp.numer(sp.together(sum(sp.Integer(SIG[i-1])*W[i]**2 for i in S))))
    cand[('e2+',0)]=sp.expand(sp.numer(sp.together(w4*w5+w4*w6+w5*w6)))
    cand[('e2-',0)]=sp.expand(sp.numer(sp.together(w1*w2+w1*w3+w2*w3)))
    cand[('Sf',0)]=sp.expand(w2+w3+w4+w5)
    print("--- factor identification ---", flush=True)
    for fac,mult in sp.factor_list(D)[1]:
        if sp.degree(sp.Poly(sp.expand(fac),t))==0: continue
        hit=[]
        for key,expr in cand.items():
            if sp.expand(expr)==0: continue
            q=sp.cancel(expr/fac)
            if getattr(q,'free_symbols',set())==set() and q!=0: hit.append(f"{key}(x{q})")
        print(f"  {sp.factor(fac)} (m{mult}) -> {hit if hit else '??? unknown'}", flush=True)
