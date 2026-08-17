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
def vanish_order(expr, var, pt):
    e=sp.together(expr); n,d=sp.fraction(e)
    def mult(poly_):
        m=0; P=sp.Poly(sp.expand(poly_),var)
        while True:
            q,r=sp.div(P, sp.Poly(var-pt,var))
            if r==0: m+=1; P=q
            else: break
        return m
    return mult(n)-mult(d)

# search clean (1=2) crossings: vary w4 through a value w4c where w4c^2+w5^2=w2^2 OR
# more generally any (1=2). Require sign-diff==1 across the crossing.
import random
rnd=random.Random(123)
found=0
for _ in range(40000):
    if found>=3: break
    w2=F(rnd.randint(20,90),10); w3=F(rnd.randint(-90,90),10); w5=F(rnd.randint(5,60),10)
    val=w2*w2-w5*w5
    if val<=0: continue
    # need rational sqrt for exact wall location? not necessary; just need crossing.
    import math
    w4c=F(round(float(val)**0.5*30),30)
    if w4c<=0: continue
    base=[w2,w3,w4c,w5]
    d=F(1,10)
    okA=cn.solve_squares([w2,w3,w4c+d,w5]); okB=cn.solve_squares([w2,w3,w4c-d,w5])
    if okA is None or okB is None or any(w==0 for w in okA+okB): continue
    sA=full_sig(okA); sB=full_sig(okB)
    if sA is None or sB is None or sA==sB: continue
    diff=sum(1 for x,y in zip(sA[0]+sA[1]+sA[2]+sA[3], sB[0]+sB[1]+sB[2]+sB[3]) if x!=y)
    # which wall flipped? identify W2 index flip
    flippedW1=[(i//3+1, i%3+4) for i in range(9) if sA[0][i]!=sB[0][i]]
    flippedW2=[(i//3+1,[(4,5),(4,6),(5,6)][i%3]) for i in range(9) if sA[1][i]!=sB[1][i]]
    if diff!=1: continue
    if not flippedW2 or flippedW1: continue   # want a pure (1=2) flip
    # reconstruct jump
    ptsA,_=side(base,4,+1,F(1,200),160,Nval); ptsB,_=side(base,4,-1,F(1,200),160,Nval)
    if len(ptsA)<30 or len(ptsB)<30: continue
    rA=reconstruct(ptsA); rB=reconstruct(ptsB)
    if rA is None or rB is None: continue
    NA=poly(rA[2])/poly(rA[3]); NB=poly(rB[2])/poly(rB[3])
    jump=sp.cancel(NA-NB)
    # wall location t* on slice: where (1=2) function vanishes. Find via sign of that W2.
    # the wall fn is a_i - b_j - b_k for flippedW2[0]
    (im_,(jp,kp))=flippedW2[0]
    # compute that fn on slice as function of t, find its root near 0
    ws=[sp.Rational(base[i].numerator,base[i].denominator) for i in range(4)]
    ws[2]=ws[2]+t; w2_,w3_,w4_,w5_=ws
    sF=w2_+w3_+w4_+w5_; sSig=-w2_**2-w3_**2+w4_**2+w5_**2
    w6_=-(-sF**2+sSig)/(-2*sF); w1_=-(sF+w6_)
    wsq={1:sp.cancel(w1_**2),2:w2_**2,3:w3_**2,4:w4_**2,5:w5_**2,6:sp.cancel(w6_**2)}
    wallfn=sp.cancel(wsq[im_]-wsq[jp]-wsq[kp]); wn,_=sp.fraction(wallfn)
    roots=[r for r in sp.solve(wn,t) if r.is_real and abs(float(r))<0.6]
    if not roots: continue
    tw=min(roots, key=lambda r: abs(float(r)))
    o=vanish_order(jump,t,tw)
    pr(f"(1=2) base w2={w2} w3={w3} w4={w4c} w5={w5}: flip {flippedW2}; wall t*={tw}; jump order={o}  (A={len(ptsA)},B={len(ptsB)})")
    found+=1
if found==0: pr("no clean (1=2) crossing found")
