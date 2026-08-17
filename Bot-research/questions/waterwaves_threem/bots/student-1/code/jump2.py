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
    """scan outward from wall (s = direction*step*k, k=1..), stop at chamber exit."""
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

# find clean w4=w2 crossing base
import random
rnd=random.Random(11); chosen=None
for _ in range(6000):
    w2=F(3); w3=F(rnd.randint(-90,90),10); w5=F(rnd.randint(-90,90),10)
    okA=cn.solve_squares([w2,w3,F(3)+F(2,10),w5]); okB=cn.solve_squares([w2,w3,F(3)-F(2,10),w5])
    if okA is None or okB is None: continue
    if any(w==0 for w in okA) or any(w==0 for w in okB): continue
    sA=full_sig(okA); sB=full_sig(okB)
    if sA is None or sB is None or sA==sB: continue
    diff=sum(1 for x,y in zip(sA[0]+sA[1]+sA[2]+sA[3], sB[0]+sB[1]+sB[2]+sB[3]) if x!=y)
    if diff<=2: chosen=(w3,w5,diff); break
w3,w5,diff=chosen
pr(f"base w2=3 w3={w3} w5={w5}, sign-diff={diff}")
base=[F(3),w3,F(3),w5]
ptsA,sA=side(base,4,+1,F(1,90),120,Nval)
ptsB,sB=side(base,4,-1,F(1,90),120,Nval)
pr(f"A pts={len(ptsA)} B pts={len(ptsB)}")
resA=reconstruct(ptsA); resB=reconstruct(ptsB)
if resA is None or resB is None: pr("recon fail",resA is None,resB is None); sys.exit()
dNA,dDA,NcA,DcA=resA; dNB,dDB,NcB,DcB=resB
NA=poly(NcA)/poly(DcA); NB=poly(NcB)/poly(DcB)
pr(f"A: degN={dNA} degD={dDA} | B: degN={dNB} degD={dDB}")
jump=sp.cancel(NA-NB)
pr("JUMP N_A-N_B factored:"); sp.pprint(sp.factor(jump))
k24=sp.expand((3+t)**2-9)   # w4^2-w2^2
pr(f"k_24(s)=w4^2-w2^2 = {sp.factor(k24)}")
jn,jd=sp.fraction(sp.together(jump))
pr(f"jump denom factored: {sp.factor(jd)}")
for p in (1,2,3,4,5):
    q,r=sp.div(sp.Poly(jn,t), sp.Poly(sp.expand(k24**p),t))
    pr(f"  jump_num divisible by k24^{p}? {r==0}")
# show jump/k24^2
pr("jump / k24^2 ="); sp.pprint(sp.factor(sp.cancel(jump/k24**2)))
