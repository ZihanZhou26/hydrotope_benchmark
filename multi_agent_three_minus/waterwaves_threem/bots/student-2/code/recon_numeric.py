#!/usr/bin/env python3
"""!!! CAUTIONARY / DO NOT TRUST THE OUTPUT OF THIS SCRIPT !!!
This FLOAT (mpmath, normal-equations) reconstruction SPURIOUSLY reports A_6 as a
degree-10 POLYNOMIAL (residual ~1e-22) at clustered nodes -- a numerical
artifact.  The EXACT test (settle.py) proves A_6 is NOT polynomial.  Kept as a
documented example that poly-vs-rational MUST be decided with exact arithmetic.

Fast NUMERIC rational reconstruction of A_6(t) on an in-chamber F-const slice,
to find deg(denominator) and the roots of D(t); then match roots to candidate
loci |k_S|=0 / e2=0 (in t).  Uses mpmath for precision; confirm exactly after.
"""
import mpmath as mp
from fractions import Fraction as Fr
from itertools import combinations
import harness as h
mp.mp.dps=60

SIG=[-1,-1,-1,1,1,1]
def w_of_t(tv):
    return [Fr(2),Fr(3),Fr(5)+tv,Fr(7)-tv]
def mixsig(oms):
    w=[None]+[Fr(x) for x in oms]; s=[]
    for r in range(1,6):
        for S in combinations(range(1,7),r):
            mns=[i for i in S if SIG[i-1]<0]; pls=[i for i in S if SIG[i-1]>0]
            if mns and pls:
                v=sum(Fr(SIG[i-1])*w[i]**2 for i in S)
                s.append(0 if v==0 else (1 if v>0 else -1))
    return tuple(s)

# in-chamber exact samples (use exact oracle, convert to mpf)
nodes=[]; ref=None
for k in range(1,260):
    tv=Fr(k,400)   # t in (0.0025, 0.65)
    try:
        oim,oms,_=h.on_shell(w_of_t(tv),SIG)
    except Exception:
        continue
    sg=mixsig(oms)
    if ref is None: ref=sg
    if sg!=ref: break
    nodes.append((mp.mpf(tv.numerator)/tv.denominator, mp.mpf(oim.numerator)/oim.denominator))
    if len(nodes)>=140: break
print("in-chamber nodes:", len(nodes), flush=True)

def fit(a,b):
    """N deg a, D deg b (monic). linear: sum n_i t^i - A t^j d_j = A t^b. lstsq."""
    rows=[]; rhs=[]
    for x,A in nodes:
        row=[x**i for i in range(a+1)]+[-A*x**j for j in range(b)]
        rows.append(row); rhs.append(A*x**b)
    M=mp.matrix(rows); r=mp.matrix(rhs)
    # normal equations (least squares): (M^T M) v = M^T r
    MT=M.T
    try:
        v=mp.lu_solve(MT*M, MT*r)
    except Exception:
        return None
    # residual
    res=M*v-r
    nr=mp.norm(res)/ (mp.norm(r)+mp.mpf(1))
    return v,nr

print("sweep denominator degree b (a=b+10):", flush=True)
best=None
for b in range(0,22):
    a=b+10
    out=fit(a,b)
    if out is None:
        print(f"  b={b}: solve fail"); continue
    v,nr=out
    print(f"  b={b} a={a}: rel residual = {mp.nstr(nr,4)}", flush=True)
    if nr<mp.mpf(10)**(-20) and best is None:
        best=(a,b,v)
        break

if best:
    a,b,v=best
    dcoef=[v[a+1+j] for j in range(b)]+[mp.mpf(1)]
    print(f"\nDETECTED denominator degree b={b}", flush=True)
    # roots of D
    poly=[dcoef[b-i] for i in range(b+1)]  # highest first
    roots=mp.polyroots([complex(c) for c in poly], maxsteps=200, extraprec=200) if b>0 else []
    print("roots of D(t):", [mp.nstr(r,8) for r in roots], flush=True)
    # candidate loci: t where named(t)=0
    t=mp.mpf  # placeholder
    import sympy as sp
    ts=sp.Symbol('t')
    w2,w3=sp.Integer(2),sp.Integer(3); w4=sp.Integer(5)+ts; w5=sp.Integer(7)-ts
    F=w2+w3+w4+w5; R=-w2**2-w3**2+w4**2+w5**2
    w1=-(F**2+R)/(2*F); w6=-(F**2-R)/(2*F)
    W={1:w1,2:w2,3:w3,4:w4,5:w5,6:w6}
    cand={}
    for r in range(1,6):
        for S in combinations(range(1,7),r):
            cand[('k',S)]=sp.expand(sum(sp.Integer(SIG[i-1])*W[i]**2 for i in S))
    cand[('e2+',0)]=sp.expand(w4*w5+w4*w6+w5*w6)
    cand[('e2-',0)]=sp.expand(w1*w2+w1*w3+w2*w3)
    # for each root, find which candidate vanishes there
    print("--- match roots ---", flush=True)
    for rt in roots:
        rc=complex(rt)
        hits=[]
        for key,expr in cand.items():
            val=complex(sp.N(expr.subs(ts, sp.nsimplify(rc.real)+sp.I*sp.nsimplify(rc.imag)) if abs(rc.imag)>1e-9 else expr.subs(ts,rc.real)))
            if abs(val)<1e-6: hits.append(key)
        print(f"  root {mp.nstr(rt,6)} -> {hits}", flush=True)
else:
    print("no clean denominator degree found up to 21", flush=True)
