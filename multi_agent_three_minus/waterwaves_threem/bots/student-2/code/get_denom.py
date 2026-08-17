#!/usr/bin/env python3
"""Exact reconstruction of A_6(t)=N(t)/D(t) on the F-const slice with the now-known
degrees (degN=6, degD=4).  Factor D over Q and identify its factors by evaluating
candidate omega-expressions; also print N, D explicitly and the net structure."""
from fractions import Fraction as Fr
from itertools import combinations
import sympy as sp
import harness as h

SIG=[-1,-1,-1,1,1,1]; H=20
def mixsig(oms):
    w=[None]+[Fr(x) for x in oms]; s=[]
    for r in range(1,6):
        for S in combinations(range(1,7),r):
            mns=[i for i in S if SIG[i-1]<0]; pls=[i for i in S if SIG[i-1]>0]
            if mns and pls:
                v=sum(Fr(SIG[i-1])*w[i]**2 for i in S)
                s.append(0 if v==0 else (1 if v>0 else -1))
    return tuple(s)
ref=mixsig(h.on_shell([Fr(2),Fr(3),Fr(5),Fr(7)],SIG)[1])
nodes=[]
for p in list(range(1,40))+list(range(-1,-14,-1)):
    sh=Fr(p,H)
    try: oim,oms,_=h.on_shell([Fr(2),Fr(3),Fr(5)+sh,Fr(7)-sh],SIG)
    except Exception: continue
    if mixsig(oms)!=ref: continue
    nodes.append((sp.Rational(p), sp.Rational(oim.numerator,oim.denominator)))
a,b=6,4
need=a+b+1
xs=[x for x,_ in nodes[:need]]; ys=[y for _,y in nodes[:need]]
# N(t)-A_6 D(t)=0, D monic (d_b=1): sum n_i t^i - A sum_{j<b} d_j t^j = A t^b
M=sp.Matrix([[xs[k]**i for i in range(a+1)]+[-ys[k]*xs[k]**j for j in range(b)] for k in range(need)])
rhs=sp.Matrix([ys[k]*xs[k]**b for k in range(need)])
sol=M.LUsolve(rhs)
t=sp.Symbol('t')
N=sum(sol[i]*t**i for i in range(a+1))
D=sum(sol[a+1+j]*t**j for j in range(b))+t**b
N=sp.expand(N); D=sp.expand(D)
# verify remaining nodes
ok=all(sp.simplify(N.subs(t,x)-y*D.subs(t,x))==0 for x,y in nodes[need:])
print("verify holdout:", ok, " (nodes", len(nodes),")")
print("D(t) =", D)
print("D factored:", sp.factor(D))
print("N(t) =", N)
print("N factored:", sp.factor(N))

# identify D factors: shift = t/H
sh=t/H
w2,w3=sp.Integer(2),sp.Integer(3); w4=sp.Integer(5)+sh; w5=sp.Integer(7)-sh
F=w2+w3+w4+w5; R=-w2**2-w3**2+w4**2+w5**2
w1=-(F**2+R)/(2*F); w6=-(F**2-R)/(2*F)
W={1:w1,2:w2,3:w3,4:w4,5:w5,6:w6}
print("\n-- on this slice (shift=t/20): w1=",sp.expand(w1)," w6=",sp.expand(w6))
cands={}
for r in range(1,6):
    for S in combinations(range(1,7),r):
        cands[('|k|',S)]=sp.expand(sp.numer(sp.together(sum(sp.Integer(SIG[i-1])*W[i]**2 for i in S))))
cands[('e2+',0)]=sp.expand(sp.numer(sp.together(w4*w5+w4*w6+w5*w6)))
cands[('e2-',0)]=sp.expand(sp.numer(sp.together(w1*w2+w1*w3+w2*w3)))
print("--- match each D-factor ---")
for fac,mult in sp.factor_list(D)[1]:
    if sp.degree(sp.Poly(sp.expand(fac),t))==0: continue
    hits=[]
    for key,expr in cands.items():
        if sp.expand(expr)==0: continue
        q=sp.cancel(expr/fac)
        if getattr(q,'free_symbols',set())==set() and q!=0: hits.append(f"{key}(x{q})")
    print(f"  {sp.factor(fac)} (m{mult}) -> {hits if hits else 'NONE'}")
