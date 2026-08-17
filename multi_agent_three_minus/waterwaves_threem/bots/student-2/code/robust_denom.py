#!/usr/bin/env python3
"""Robust EXACT determination of A_6(t)'s denominator on an F-constant slice,
within ONE chamber, WITHOUT slow symbolic BG.

Method: P(t) = generous product of all plausibly-present factors (every same-type
|k_S| = sum of squares: singletons, pairs, Q; plus e2(plus), e2(minus)).  Sample
A_6(t) exactly at small in-chamber nodes (oracle), interpolate the polynomial
N(t) = A_6(t)*P(t) (verify it IS polynomial via holdout), then reduce:
D(t) = P(t)/gcd(N(t),P(t)).  Factor D and name its factors.
If A_6*P is NOT polynomial, the denominator has a factor outside this set.
"""
from fractions import Fraction as Fr
from itertools import combinations
import sympy as sp
import harness as h

t=sp.Symbol('t')
SIG=[-1,-1,-1,1,1,1]

# F-constant slice w4=5+t, w5=7-t, w2=2,w3=3 (symbolic w_i(t))
w2,w3=sp.Integer(2),sp.Integer(3)
w4=sp.Integer(5)+t; w5=sp.Integer(7)-t
F=w2+w3+w4+w5; R=-w2**2-w3**2+w4**2+w5**2
w1=-(F**2+R)/(2*F); w6=-(F**2-R)/(2*F)
Wt={1:w1,2:w2,3:w3,4:w4,5:w5,6:w6}

# generous P(t): all same-type sums of squares + e2(plus),e2(minus)
factors=[]
for i in range(1,7):
    factors.append(sp.expand(Wt[i]**2))                       # singletons
for trip in ([1,2,3],[4,5,6]):
    for i,j in combinations(trip,2):
        factors.append(sp.expand(Wt[i]**2+Wt[j]**2))          # same-type pairs
factors.append(sp.expand(Wt[1]**2+Wt[2]**2+Wt[3]**2))         # Q
factors.append(sp.expand(Wt[4]*Wt[5]+Wt[4]*Wt[6]+Wt[5]*Wt[6]))# e2 plus
factors.append(sp.expand(Wt[1]*Wt[2]+Wt[1]*Wt[3]+Wt[2]*Wt[3]))# e2 minus
P=sp.Integer(1)
for f in factors:
    P=P*f
P=sp.expand(P)
degP=sp.degree(P,t)
print("deg P(t) =", degP, flush=True)

# sample A_6 at in-chamber nodes
def mixed_sig(oms):
    w=[None]+[Fr(x) for x in oms]; s=[]
    for r in range(1,6):
        for S in combinations(range(1,7),r):
            mns=[i for i in S if SIG[i-1]<0]; pls=[i for i in S if SIG[i-1]>0]
            if mns and pls:
                v=sum(Fr(SIG[i-1])*w[i]**2 for i in S)
                s.append(0 if v==0 else (1 if v>0 else -1))
    return tuple(s)

nodes=[]; sigref=None
for k in range(1,degP+200):
    tv=Fr(k,500)
    try:
        oim,oms,_=h.on_shell([Fr(2),Fr(3),Fr(5)+tv,Fr(7)-tv],SIG)
    except Exception:
        continue
    sg=mixed_sig(oms)
    if sigref is None: sigref=sg
    if sg!=sigref: continue
    nodes.append((tv,oim))
    if len(nodes)>=degP+60: break
print("in-chamber nodes:", len(nodes), flush=True)

# build N(t_k)=A_6(t_k)*P(t_k); interpolate degree degN
need=degP+40
xs=[sp.Rational(tv.numerator,tv.denominator) for tv,_ in nodes[:need]]
Pvals=[P.subs(t,x) for x in xs]
ys=[sp.Rational(o.numerator,o.denominator)*Pv for (_,o),Pv in zip(nodes[:need],Pvals)]
d=need-20
Vm=sp.Matrix([[xs[k]**p for p in range(d+1)] for k in range(d+1)])
Yv=sp.Matrix(ys[:d+1])
c=Vm.LUsolve(Yv)
# holdout check
ok=True
for k in range(d+1,len(xs)):
    pred=sum(c[p]*xs[k]**p for p in range(d+1))
    if sp.simplify(pred-ys[k])!=0: ok=False;break
print("A_6*P polynomial?:", ok, flush=True)
if ok:
    N=sum(c[p]*t**p for p in range(d+1))
    N=sp.expand(N)
    g=sp.gcd(N,P)
    D=sp.cancel(P/g)
    print("REDUCED denominator D(t) factored:", sp.factor(D), flush=True)
    print("deg D:", sp.degree(sp.expand(D),t), flush=True)
    # name factors
    named={}
    for r in range(1,6):
        for S in combinations(range(1,7),r):
            named[('k',S)]=sp.expand(sum(sp.Integer(SIG[i-1])*Wt[i]**2 for i in S))
    named[('e2+',0)]=sp.expand(Wt[4]*Wt[5]+Wt[4]*Wt[6]+Wt[5]*Wt[6])
    named[('e2-',0)]=sp.expand(Wt[1]*Wt[2]+Wt[1]*Wt[3]+Wt[2]*Wt[3])
    for fac,mult in sp.factor_list(D)[1]:
        if sp.degree(sp.Poly(sp.expand(fac),t))==0: continue
        hit=[]
        for key,expr in named.items():
            if sp.expand(expr)==0: continue
            q=sp.cancel(sp.expand(expr)/fac)
            if q.free_symbols==set() and q!=0: hit.append(f"{key}(x{q})")
        print(f"  {sp.factor(fac)} (mult {mult}) -> {hit if hit else '???'}", flush=True)
else:
    print("=> denominator has a factor OUTSIDE {same-type sums of squares, e2}.", flush=True)
