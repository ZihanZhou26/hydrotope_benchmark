#!/usr/bin/env python3
"""Single-wall crossing + jump-coefficient extraction on F-const slices.
Group sides by the MIXED-wall signvec only (same-type orderings are analytic).
 (1=1) wall ('1',i,j): k_ij=b_j-a_i. jump(R-L)=k_ij*P  (R = b_j>a_i side).
 (1=2) wall ('2',i,(j,k)): k_ijk=a_i-b_j-b_k. jump = k_ijk^3 * Q  (signed by k_ijk)."""
from fractions import Fraction as F
import itertools, sympy as sp
import r5lib as L, harness as h, chambers_n6 as cn, inv
t=sp.Symbol('t'); SIG=[-1,-1,-1,1,1,1]
M=[0,1,2]; P=[3,4,5]
W1KEYS=[('1',i,j) for i in M for j in P]
W2KEYS=[('2',i,(j,k)) for i in M for (j,k) in itertools.combinations(P,2)]
ALLKEYS=W1KEYS+W2KEYS

def wallvals(oms):
    sq=[w*w for w in oms]; v={}
    for key in W1KEYS: v[key]=sq[key[1]]-sq[key[2]]
    for key in W2KEYS: v[key]=sq[key[1]]-sq[key[2][0]]-sq[key[2][1]]
    return v
def msig(oms):
    v=wallvals(oms)
    if any(x==0 for x in v.values()): return None
    return tuple(1 if v[key]>0 else -1 for key in ALLKEYS)

import fastbg as FB
from inv import invariants as _invs
def collect_from(w2,w3,a,b,tstart,direction,step,maxn,ref):
    # 1) contiguous in-chamber t-values (pure python, no oracle)
    tvals=[]; omsl=[]
    for k in range(0,maxn+1):
        tt=tstart+direction*step*k
        oms=cn.solve_squares(L.fc_free(w2,w3,a,b,tt))
        if oms is None or any(w==0 for w in oms): break
        s=msig(oms)
        if s is None or s!=ref: break
        tvals.append(tt); omsl.append(oms)
    if not tvals: return []
    # 2) batch-evaluate N at all in-chamber points (one oracle call)
    res=FB.batch_onshell([(6, L.fc_free(w2,w3,a,b,tt), SIG) for tt in tvals])
    pts=[]
    for tt,oms,r in zip(tvals,omsl,res):
        if r is None: continue
        e=_invs(oms); pts.append((tt, F(r[1]*(e[2]+e[3]),32)))
    return pts

def ksym(w2,w3,a,b,key):
    w2s,w3s,As,Bs=[sp.nsimplify(x) for x in (w2,w3,a,b)]
    w4=As+t; w5=Bs-t
    sumF=w2s+w3s+w4+w5; sumSig=-w2s**2-w3s**2+w4**2+w5**2
    w6=(sumSig-sumF**2)/(2*sumF); w1=-(sumF+w6)
    sq=[w1**2,w2s**2,w3s**2,w4**2,w5**2,w6**2]
    if key[0]=='1': return sp.cancel(sq[key[2]]-sq[key[1]])  # k_ij=b_j-a_i
    else: i,(j,k)=key[1],key[2]; return sp.cancel(sq[i]-sq[j]-sq[k])

def find_crossings(w2,w3,a,b,step,tmax):
    """return list of (tlo,thi,key) for SINGLE-wall crossings (msig differs by one)."""
    out=[]; prev=None
    k=-int(tmax/step)
    while k<=int(tmax/step):
        tt=F(k)*step
        oms=cn.solve_squares(L.fc_free(w2,w3,a,b,tt))
        s=msig(oms) if (oms is not None and not any(w==0 for w in oms)) else None
        if prev is not None and prev[1] is not None and s is not None and s!=prev[1]:
            diff=[ALLKEYS[i] for i in range(len(ALLKEYS)) if prev[1][i]!=s[i]]
            if len(diff)==1: out.append((prev[0],tt,diff[0]))
        prev=(tt,s); k+=1
    return out

def extract_bracket(w2,w3,a,b,tlo,thi,key,step,span):
    """collect rightward from thi, leftward from tlo; fit each; jump & coef."""
    oLref=cn.solve_squares(L.fc_free(w2,w3,a,b,tlo)); sL=msig(oLref)
    oRref=cn.solve_squares(L.fc_free(w2,w3,a,b,thi)); sR=msig(oRref)
    ptsL=collect_from(w2,w3,a,b,tlo,-1,step,span,sL)
    ptsR=collect_from(w2,w3,a,b,thi,+1,step,span,sR)
    solL=L.fit_poly(ptsL,16); solR=L.fit_poly(ptsR,16)
    if solL is None or solR is None: return ('fitfail',key,len(ptsL),len(ptsR))
    NL=L.poly(solL); NR=L.poly(solR)
    jump=sp.expand(NR-NL)   # N(R side, larger t) - N(L side)
    k=ksym(w2,w3,a,b,key)
    # ensure jump sign convention: jump = (sign of k on R side)*|...| ; coef = jump/k^p
    p=3 if key[0]=='2' else 1
    coef=sp.cancel(jump/k**p)
    # ORIENT to the (k_S>0)-active convention: evaluate k_S at an R-side point
    tR=thi+step
    kR=k.subs(t, sp.Rational(tR.numerator,tR.denominator))
    sgn=1 if kR>0 else -1
    coef=sp.expand(coef*sgn)
    return key,jump,k,coef,coef.is_polynomial(t)
