import sys, math
from fractions import Fraction as F
import sympy as sp
from collectlib import full_sig, reconstruct, poly
import harness as h, chambers_n6 as cn, inv
SIG=[-1,-1,-1,1,1,1]; t=sp.Symbol('t')
def pr(*a): print(*a, flush=True)
def ee(oms): e=inv.invariants(oms); return e[2]+e[3]
def Nval(oms,im): return im*ee(oms)
def side(base, vary, direction, step, maxn, fn):
    pts=[]; s0=None
    for k in range(1,maxn+1):
        s=direction*step*k
        free=list(base); free[vary-2]=base[vary-2]+s
        oms=cn.solve_squares(free)
        if oms is None or any(w==0 for w in oms): break
        sig=full_sig(oms)
        if sig is None: break
        if s0 is None: s0=sig
        elif sig!=s0: break
        try: im,_,_=h.on_shell(free,SIG); pts.append((s, fn(oms,im)))
        except Exception: break
    return pts,s0

# pick a base exactly on (1=2) wall w4^2+w5^2=w2^2 with a Pythagorean triple: (w4,w5,w2)=(4,3,5)
# vary w4 across 4. other legs w3 chosen for big clean chambers.
tried=[(F(5),F(-13,2),F(4),F(3)),(F(5),F(-15,2),F(4),F(3)),(F(13),F(-8),F(12),F(5)),
       (F(5),F(8),F(4),F(3)),(F(25,1),F(-20),F(24),F(7)),(F(5),F(-9),F(4),F(3))]
for (w2,w3,w4mid,w5) in tried:
    okA=cn.solve_squares([w2,w3,w4mid+F(1,10),w5]); okB=cn.solve_squares([w2,w3,w4mid-F(1,10),w5])
    if okA is None or okB is None or any(w==0 for w in okA+okB): continue
    sA=full_sig(okA); sB=full_sig(okB)
    if sA is None or sB is None or sA==sB: continue
    base=[w2,w3,w4mid,w5]
    for step in (F(1,150),F(1,300),F(1,600)):
        ptsA,_=side(base,4,+1,step,150,Nval); ptsB,_=side(base,4,-1,step,150,Nval)
        if len(ptsA)<30 or len(ptsB)<30: continue
        rA=reconstruct(ptsA); rB=reconstruct(ptsB)
        if rA is None or rB is None: continue
        NA=poly(rA[2])/poly(rA[3]); NB=poly(rB[2])/poly(rB[3])
        jump=sp.cancel(NA-NB)
        k245=sp.expand((sp.Rational(w4mid.numerator,w4mid.denominator)+t)**2
                       + sp.Rational(w5.numerator,w5.denominator)**2
                       - sp.Rational(w2.numerator,w2.denominator)**2)
        jn,_=sp.fraction(sp.together(jump))
        orders=[]
        for p in (1,2,3,4):
            q,r=sp.div(sp.Poly(jn,t), sp.Poly(sp.expand(k245**p),t))
            orders.append((p,r==0))
        pr(f"base w2={w2} w3={w3} w4={w4mid} w5={w5} step={step}: A={len(ptsA)} B={len(ptsB)} degNA={rA[0]} degNB={rB[0]}")
        pr(f"   k245={sp.factor(k245)}  divisibility: {orders}")
        # report the order = max p s.t. divisible
        maxp=max([p for p,ok in orders if ok], default=0)
        pr(f"   => (1=2) jump vanishes to order {maxp} at the wall")
        sys.exit()
pr("no clean (1=2) reconstruction obtained")
