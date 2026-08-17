#!/usr/bin/env python3
"""DECISIVE cross-term test (corrected partner identification).

The (1=2) wall {a2=b4+b5} is FORCED by either disjoint (1=1) edge pair
  P1 = {a1=b6, a3=b7}   or   P2 = {a1=b7, a3=b6}
(since a1+a3=b6+b7  <=>  a2=b4+b5 on the manifold). The (1=1)x(1=1) matching cross-term
(b6-a1)_+(b7-a3)_+ [or the P2 image] is the n=6 cross-term whose forcing now lands on a
(1=2) wall at n>=7 (s1_019). If the observed (1=2) jump order 2 = 1+1 is that cross-term,
then in a chamber where BOTH forcing pairs are INACTIVE the (1=2) jump order must RISE.

Active forcing pair P1: (b6>a1 and b7>a3). P2: (b7>a1 and b6>a3).
We search for a thick chamber on {a2=b4+b5} with BOTH pairs inactive, and measure.
Indices: 0=w1(m),1=w2(m),2=w3(m),3=w4(p),4=w5(p),5=w6(p),6=w7(p).
"""
from fractions import Fraction as F
import sympy as sp
import n7lib as L, r5lib as RL

t = sp.Symbol('t')

def csig(free):
    o = L.solve_squares(free)
    if o is None or any(w == 0 for w in o): return None
    return L.signature(o, with_orderings=False)

def collect(base, p, q, A, B, direction, step, maxn, ref):
    frees=[]; omsl=[]; tv=[]
    for k in range(1, maxn+1):
        tt=direction*step*k
        fr=list(F(x) for x in base); fr[p]=F(A)+tt; fr[q]=F(B)-tt
        o=L.solve_squares(fr)
        if o is None or any(w==0 for w in o): break
        if L.signature(o,with_orderings=False)!=ref: break
        frees.append(fr); omsl.append(o); tv.append(tt)
    if not frees: return []
    ims=L.batch_amp(frees)
    return [(tt,L.N7_from_im(o,im)) for tt,o,im in zip(tv,omsl,ims) if im is not None]

def order_jump(base, p, q, A, B, step=F(1,80), maxn=40, dmax=46):
    frL=list(F(x) for x in base); frL[p]=F(A)-step/3; frL[q]=F(B)+step/3
    frR=list(F(x) for x in base); frR[p]=F(A)+step/3; frR[q]=F(B)-step/3
    sL=csig(frL); sR=csig(frR)
    if sL is None or sR is None: return None
    sd=sum(1 for a,b in zip(sL,sR) if a!=b)
    if sd!=1: return ('sd',sd)
    ptsL=collect(base,p,q,A,B,-1,step,maxn,sL)
    ptsR=collect(base,p,q,A,B,+1,step,maxn,sR)
    if len(ptsL)<32 or len(ptsR)<32: return ('thin',len(ptsL),len(ptsR))
    cL=RL.fit_poly(ptsL,dmax); cR=RL.fit_poly(ptsR,dmax)
    if cL is None or cR is None: return ('fitfail',len(ptsL),len(ptsR))
    NL=sum(sp.Rational(c.numerator,c.denominator)*t**j for j,c in enumerate(cL))
    NR=sum(sp.Rational(c.numerator,c.denominator)*t**j for j,c in enumerate(cR))
    d=sp.expand(NR-NL)
    if d==0: return ('ORDER',0)
    P=sp.Poly(d,t); o=0; nn=P
    while nn.eval(0)==0 and nn.degree()>0: nn=nn.diff(t); o+=1
    return ('ORDER',o)

def forcing_status(o):
    sq=[w*w for w in o]
    a1,a3=sq[0],sq[2]; b6,b7=sq[5],sq[6]
    P1 = (b6>a1 and b7>a3)
    P2 = (b7>a1 and b6>a3)
    return P1, P2

TRIPLES=[(3,4,5),(6,8,10),(5,12,13),(8,15,17),(20,21,29),(9,40,41),(12,35,37)]

if __name__=="__main__":
    print("Goal: (1=2){a2=b4+b5} jump order with BOTH forcing pairs P1={a1=b6,a3=b7}, P2={a1=b7,a3=b6} INACTIVE")
    print("  (vary w4 in wall, compensate w6 not in wall)\n")
    nB=0; nA=0
    inactive_orders=[]; active_orders=[]
    for (w4,w5,w2) in TRIPLES:
        for w3n in range(1,4*w2):
            w3=F(w3n,2)
            for w6n in range(1,4*w2):
                w6=F(w6n,2)
                base=[F(w2),F(w3),F(w4),F(w5),F(w6)]
                o0=L.solve_squares(base)
                if o0 is None or any(w==0 for w in o0): continue
                P1,P2=forcing_status(o0)
                # we want samples of BOTH categories, prioritize INACTIVE
                cat_inactive = (not P1) and (not P2)
                if cat_inactive and len(inactive_orders)>=3: continue
                if (not cat_inactive) and len(active_orders)>=3: continue
                res=order_jump(base,2,4,F(w4),F(w6))
                if res is None or res[0] in ('sd','thin','fitfail'): continue
                order=res[1]
                tag = "BOTH-INACTIVE" if cat_inactive else f"P1={P1},P2={P2} (some active)"
                print(f"  w=({w2},{w3},{w4},{w5},{w6}) order={order}  [{tag}]",flush=True)
                if cat_inactive: inactive_orders.append(order)
                else: active_orders.append(order)
                if len(inactive_orders)>=3 and len(active_orders)>=3: break
            if len(inactive_orders)>=3 and len(active_orders)>=3: break
        if len(inactive_orders)>=3 and len(active_orders)>=3: break
    print("\nSUMMARY:")
    print("  forcing pairs INACTIVE -> (1=2) orders:", inactive_orders)
    print("  forcing pair(s) ACTIVE -> (1=2) orders:", active_orders)
