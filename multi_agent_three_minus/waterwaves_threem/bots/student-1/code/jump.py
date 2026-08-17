import sys
from fractions import Fraction as F
import sympy as sp
from collectlib import full_sig, solve_exact, reconstruct, poly
import harness as h, chambers_n6 as cn, inv
SIG=[-1,-1,-1,1,1,1]; t=sp.Symbol('t')
def pr(*a): print(*a, flush=True)
def ee(oms): e=inv.invariants(oms); return e[2]+e[3]

def Nval(oms,im): return im*ee(oms)

def collect_side(base, vary, s_lo, s_hi, step, fn):
    """collect points with vary-leg = base+s for s in [s_lo,s_hi], requiring SAME
    full_sig throughout (one chamber). Returns pts and the sig."""
    pts=[]; s0=None
    s=s_lo
    while s<=s_hi:
        free=list(base); free[vary-2]=base[vary-2]+s
        oms=cn.solve_squares(free)
        if oms is not None and not any(w==0 for w in oms):
            sig=full_sig(oms)
            if sig is not None:
                if s0 is None: s0=sig
                if sig==s0:
                    try:
                        im,_,_=h.on_shell(free,SIG); pts.append((s, fn(oms,im)))
                    except Exception: pass
        s+=step
    return pts,s0

# Find a base where w2 and w4 are close (cross w4=w2 wall) with other walls far.
# Use w2=3 fixed, vary w4 around 3. Choose w3,w5 to keep it a single clean crossing.
import itertools, random
rnd=random.Random(5)
chosen=None
for _ in range(4000):
    w2=F(3); w3=F(rnd.randint(-90,90),10); w5=F(rnd.randint(-90,90),10)
    # we'll vary w4 around w2=3
    base=[w2,w3,F(3),w5]  # placeholder w4=3 (on wall) - test slightly off
    okA=cn.solve_squares([w2,w3,F(3)+F(3,10),w5]); okB=cn.solve_squares([w2,w3,F(3)-F(3,10),w5])
    if okA is None or okB is None: continue
    if any(w==0 for w in okA) or any(w==0 for w in okB): continue
    sA=full_sig(okA); sB=full_sig(okB)
    if sA is None or sB is None or sA==sB: continue
    # they should differ ONLY in the k_24 sign (w4^2 vs w2^2). check minimal difference
    diff=sum(1 for x,y in zip(sA[0]+sA[1]+sA[2]+sA[3], sB[0]+sB[1]+sB[2]+sB[3]) if x!=y)
    if diff<=2:   # ideally just k_24 (and maybe its (2=2)-complement bookkeeping)
        chosen=(w2,w3,w5,diff); break
if chosen is None:
    pr("no clean crossing base found"); sys.exit()
w2,w3,w5,diff=chosen
pr(f"crossing base: w2={w2} w3={w3} w5={w5}; sign-diff across w4=3 is {diff}")
base=[w2,w3,F(3),w5]
# side A: w4 in (3, 3+d];  side B: w4 in [3-d, 3)
ptsA,sA=collect_side(base,4, F(1,80), F(60,80), F(1,80), Nval)
ptsB,sB=collect_side(base,4, F(-60,80), F(-1,80), F(1,80), Nval)
pr(f"side A pts={len(ptsA)}, side B pts={len(ptsB)}")
resA=reconstruct(ptsA); resB=reconstruct(ptsB)
if resA is None or resB is None: pr("recon fail",resA is None,resB is None); sys.exit()
dNA,dDA,NcA,DcA=resA; dNB,dDB,NcB,DcB=resB
# N(s) = NumA(s)/DenA(s); both should have pure-sumFree denom; clear it
sf0=sum(base); sumF=sp.Rational(sf0.numerator,sf0.denominator)+t
NA=sp.cancel(poly(NcA)/poly(DcA)*sumF**dDA)   # = N(s)*sumFree^dDA / (Den/sumF^dD)... 
# safer: N as a function = poly(NcA)/poly(DcA). Evaluate jump symbolically:
NA_fn=poly(NcA)/poly(DcA); NB_fn=poly(NcB)/poly(DcB)
jump=sp.cancel(NA_fn-NB_fn)
pr(f"degA: N={dNA} D={dDA};  degB: N={dNB} D={dDB}")
pr("JUMP N_A - N_B (factored):"); sp.pprint(sp.factor(jump))
# wall function k_24(s) = w4^2-w2^2 = (3+s)^2 - 9
k24=(3+t)**2-9
pr(f"k_24(s) = {sp.expand(k24)} = {sp.factor(k24)}")
# divide jump by k24^p
jn,jd=sp.fraction(sp.together(jump))
for p in (1,2,3,4):
    q,r=sp.div(sp.Poly(jn,t), sp.Poly(k24**p,t))
    pr(f"  jump_num / k24^{p}: remainder zero? {r==0}")
