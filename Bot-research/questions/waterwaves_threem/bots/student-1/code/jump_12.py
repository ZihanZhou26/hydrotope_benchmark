import sys
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

# cross (1=2) wall k_{245} = w4^2+w5^2-w2^2 = 0 by varying w4.
# need a base where this is the ONLY sign change at the crossing.
import random
rnd=random.Random(7); chosen=None
for _ in range(20000):
    w2=F(rnd.randint(30,90),10); w3=F(rnd.randint(-90,90),10); w5=F(rnd.randint(5,40),10)
    val=w2*w2-w5*w5
    if val<=0: continue
    w4c=val.numerator/val.denominator
    import math
    w4mid=F(round(math.sqrt(float(val))*10),10)  # approx sqrt
    # test crossing around w4 where w4^2 ~ w2^2-w5^2
    base=[w2,w3,w4mid,w5]
    okA=cn.solve_squares([w2,w3,w4mid+F(3,10),w5]); okB=cn.solve_squares([w2,w3,w4mid-F(3,10),w5])
    if okA is None or okB is None: continue
    if any(w==0 for w in okA) or any(w==0 for w in okB): continue
    sA=full_sig(okA); sB=full_sig(okB)
    if sA is None or sB is None or sA==sB: continue
    diff=sum(1 for x,y in zip(sA[0]+sA[1]+sA[2]+sA[3], sB[0]+sB[1]+sB[2]+sB[3]) if x!=y)
    if diff<=2:
        chosen=(w2,w3,w4mid,w5,diff); break
if chosen is None: pr("no clean (1=2) crossing"); sys.exit()
w2,w3,w4mid,w5,diff=chosen
pr(f"(1=2) base w2={w2} w3={w3} w4~{w4mid} w5={w5}, sign-diff={diff}")
base=[w2,w3,w4mid,w5]
ptsA,_=side(base,4,+1,F(1,90),120,Nval)
ptsB,_=side(base,4,-1,F(1,90),120,Nval)
pr(f"A={len(ptsA)} B={len(ptsB)}")
rA=reconstruct(ptsA); rB=reconstruct(ptsB)
if rA is None or rB is None: pr("recon fail",rA is None,rB is None); sys.exit()
NA=poly(rA[2])/poly(rA[3]); NB=poly(rB[2])/poly(rB[3])
pr(f"A degN={rA[0]} degD={rA[1]} | B degN={rB[0]} degD={rB[1]}")
jump=sp.cancel(NA-NB)
# wall fn on slice: k245(s)=(w4mid+s)^2 + w5^2 - w2^2
k245=sp.expand((sp.Rational(w4mid.numerator,w4mid.denominator)+t)**2
               + sp.Rational(w5.numerator,w5.denominator)**2
               - sp.Rational(w2.numerator,w2.denominator)**2)
pr(f"k_245(s) factored: {sp.factor(k245)}")
jn,jd=sp.fraction(sp.together(jump))
# find the wall root s* (where k245=0 and it's the crossing)
roots=[r for r in sp.solve(k245,t) if r.is_real]
pr(f"k_245 real roots: {roots}")
for p in (1,2,3,4):
    q,r=sp.div(sp.Poly(jn,t), sp.Poly(sp.expand(k245**p),t))
    pr(f"  jump_num divisible by k245^{p}? {r==0}")
