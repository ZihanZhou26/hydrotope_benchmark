#!/usr/bin/env python3
"""ROUND 6: directly characterize the (1=1) CROSS-TERM.

Extract the (1=1) jump coefficient P across wall {a2=b4} (legs 2,4 both FREE) as a
function of a sub-wall parameter w5, scanning across the matching sub-wall {a3=b5}
(at w5 = +-w3). If P is chamber-independent (simple sum), P(w5) is one smooth
polynomial; if there is a cross-term, P kinks at w5=+-w3, with some exponent.

Slice trick: fix w2,w3; set base (a=w2, b=w5star) so that at t=0, w4=w2 (ON the wall
{a2=b4}) and w5=w5star. F-const (sumFree=2 w2+w3+w5star fixed) => N(t) polynomial in
t per side. k(t)=w4^2-w2^2=(w2+t)^2-w2^2 = t(2 w2 + t). jump=N_R(t)-N_L(t)=k(t) P(t);
P(0) is the jump coefficient at the wall point (w2,w3,w4=w2,w5=w5star).
"""
from fractions import Fraction as F
import sympy as sp
import r5lib as L, r5_walls as W, chambers_n6 as cn, inv, fastbg as FB
SIG=[-1,-1,-1,1,1,1]; t=sp.Symbol('tt')

def Nval(o,im):
    e=inv.invariants(o); return F(im*(e[2]+e[3]),32)

def collect_side(w2,w3,w5s,direction,step,maxn):
    """contiguous in-chamber pts on one side of t=0 (single wall {a2=b4} at t=0)."""
    a=F(w2); b=F(w5s)
    tvals=[]; omsl=[]
    ref=None
    for k in range(1,maxn+1):
        tt=direction*step*k
        free=[F(w2),F(w3),a+tt,b-tt]   # w4=w2+tt, w5=w5s-tt
        o=cn.solve_squares(free)
        if o is None or any(w==0 for w in o): break
        s=W.msig(o)
        if s is None: break
        if ref is None: ref=s
        elif s!=ref: break
        tvals.append(tt); omsl.append(o)
    if not tvals: return None
    res=FB.batch_onshell([(6,[F(w2),F(w3),a+tt,b-tt],SIG) for tt in tvals])
    pts=[]
    for tt,o,r in zip(tvals,omsl,res):
        if r is None: continue
        pts.append((tt, Nval(o,r[1])))
    return pts

def jumpP(w2,w3,w5s,step=F(1,100),maxn=30):
    """Return P(0) = jump coefficient across {a2=b4} at wall point w4=w2,w5=w5s."""
    pR=collect_side(w2,w3,w5s,+1,step,maxn)
    pL=collect_side(w2,w3,w5s,-1,step,maxn)
    if not pR or not pL or len(pR)<8 or len(pL)<8: return None
    cR=L.fit_poly(pR,16); cL=L.fit_poly(pL,16)
    if cR is None or cL is None: return None
    NR=sum(sp.Rational(c.numerator,c.denominator)*t**j for j,c in enumerate(cR))
    NL=sum(sp.Rational(c.numerator,c.denominator)*t**j for j,c in enumerate(cL))
    jump=sp.expand(NR-NL)
    w2s=sp.Rational(F(w2).numerator,F(w2).denominator)
    kpoly=t*(2*w2s+t)
    P=sp.cancel(jump/kpoly)
    if not P.is_polynomial(t): return ('notpoly',sp.simplify(jump))
    return F(sp.Rational(P.subs(t,0)).p, sp.Rational(P.subs(t,0)).q)

if __name__=="__main__":
    w2,w3=F(3),F(5)
    print(f"Wall {{a2=b4}} jump coefficient P(0) vs w5 (sub-wall {{a3=b5}} at w5=+-{w3}):")
    print("(w2,w3 fixed = 3,5)")
    for w5s in [F(2),F(3),F(4),F(45,10),F(49,10),F(5,1),F(51,10),F(6),F(7),F(9),F(11)]:
        if w5s in (w2,w3): continue
        r=jumpP(w2,w3,w5s)
        print(f"  w5={str(w5s):>5}  (w5-w3={float(w5s-w3):+.2f})  P(0)={r}")
