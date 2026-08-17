#!/usr/bin/env python3
"""Decisive cross-term test: measure the (1=2) wall {a2=b4+b5} jump order in a THICK
chamber where the candidate partner (1=1) walls a2=b6 and a2=b7 are INACTIVE
(b6<a2 and b7<a2). If the order rises to 4 there (vs 2 where partners active), the
pure single-(1=2) exponent is n-3=4 and a (1=2)x(1=1) cross-term lowers it to 2.

Wall a2=b4+b5: keep w2^2=w4^2+w5^2 by Pythagorean (w4,w5,w2). Vary w4 (idx2) on a
slice, compensate w6 (idx4, plus, not in wall). Search w3,w6 (and w4,w5,w2 triple)
for a point with b6=w6^2<a2 and b7=w7^2<a2 and >=30 in-chamber points each side.
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

def order_jump(ptsL, ptsR, dmax=46):
    cL=RL.fit_poly(ptsL,dmax); cR=RL.fit_poly(ptsR,dmax)
    if cL is None or cR is None: return None,(len(ptsL),len(ptsR))
    NL=sum(sp.Rational(c.numerator,c.denominator)*t**j for j,c in enumerate(cL))
    NR=sum(sp.Rational(c.numerator,c.denominator)*t**j for j,c in enumerate(cR))
    d=sp.expand(NR-NL)
    if d==0: return 0,(len(ptsL),len(ptsR))
    P=sp.Poly(d,t); o=0; nn=P
    while nn.eval(0)==0 and nn.degree()>0: nn=nn.diff(t); o+=1
    return o,(len(ptsL),len(ptsR))

# Pythagorean triples (w4,w5,w2) with w2^2=w4^2+w5^2:
TRIPLES=[(3,4,5),(6,8,10),(5,12,13),(8,15,17),(9,12,15),(20,21,29),(12,16,20)]

def try_point(w4,w5,w2,w3,w6,step=F(1,80),maxn=40):
    base=[F(w2),F(w3),F(w4),F(w5),F(w6)]
    o0=L.solve_squares(base)
    if o0 is None or any(w==0 for w in o0): return None
    sq=[w*w for w in o0]
    a2=sq[1]; b6=sq[5]; b7=sq[6]
    inact = (b6<a2 and b7<a2)
    # check on-wall: a2 == b4+b5
    if sq[1]!=sq[3]+sq[4]:  # not exactly on wall (w4 shifted) -- we set base at wall via w4=w4
        pass
    frL=list(base); frL[2]=F(w4)-step/3
    frR=list(base); frR[2]=F(w4)+step/3
    sL=csig(frL); sR=csig(frR)
    if sL is None or sR is None: return None
    sd=sum(1 for a,b in zip(sL,sR) if a!=b)
    if sd!=1: return ('sd',sd,inact,b6,b7,a2)
    ptsL=collect(base,2,4,F(w4),F(w6),-1,step,maxn,sL)
    ptsR=collect(base,2,4,F(w4),F(w6),+1,step,maxn,sR)
    if len(ptsL)<32 or len(ptsR)<32: return ('thin',len(ptsL),len(ptsR),inact,b6<a2,b7<a2)
    o,_=order_jump(ptsL,ptsR)
    return ('ORDER',o,inact,(b6<a2),(b7<a2),len(ptsL),len(ptsR))

if __name__=="__main__":
    print("Searching for (1=2) crossings with a2=b6 and a2=b7 INACTIVE (thick chamber)...")
    # scan w3, w6 over a grid for each triple; report first good inactive-partner point
    found=[]; nmeas=0; ninact=0
    for (w4,w5,w2) in TRIPLES:
        for w6n in range(1,2*w2):
            w6=F(w6n,2)
            for w3n in list(range(1,3*w2)):
                w3=F(w3n,2)
                r=try_point(w4,w5,w2,w3,w6)
                if r is None: continue
                if r[0]=='ORDER':
                    nmeas+=1
                    inact=r[2]; b6i=r[3]; b7i=r[4]
                    tag = "PARTNERS-INACTIVE" if (b6i and b7i) else (("a2>b6 " if b6i else "")+("a2>b7" if b7i else "") or "partner(s) ACTIVE")
                    print(f"  w=({w2},{w3},{w4},{w5},{w6}) -> ORDER={r[1]}  a2>b6:{b6i} a2>b7:{b7i}  nL,nR={r[5]},{r[6]}  [{tag}]",flush=True)
                    found.append((b6i and b7i, r[1]))
                    if (b6i and b7i): ninact+=1
                    if ninact>=3 and nmeas>=8: break
            if ninact>=3 and nmeas>=8: break
        if ninact>=3 and nmeas>=8: break
        if nmeas>=24: break
    print("\nSUMMARY: orders when partners INACTIVE vs ACTIVE:")
    inact_orders=sorted({r for (k,r) in found if k})
    act_orders=sorted({r for (k,r) in found if not k})
    print("  partners INACTIVE (a2>b6 & a2>b7): orders =", inact_orders)
    print("  partners (some) ACTIVE          : orders =", act_orders)
