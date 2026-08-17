#!/usr/bin/env python3
"""PI round-8 follow-up (self-contained): (a) soft MINUS leg via small-eps
convergence in the eps->0 chamber; (b) n=7 (1=2) exponent with a larger pool.
Own ./bg + own ./pi_batch; no student code."""
import subprocess, sys, itertools
from fractions import Fraction as F
HERE=sys.path[0] or "."; BATCH=HERE+"/pi_batch"
SIG=lambda n:[-1,-1,-1]+[1]*(n-3)

def solve_full(freeW,n,signs):
    s1=signs[0]; sF=sum(freeW,F(0))
    sS=sum(signs[i+1]*freeW[i]*freeW[i] for i in range(n-2))
    wn=-(s1*sF*sF+sS)/(F(2)*s1*sF); w1=-(sF+wn)
    W=[w1]+list(freeW)+[wn]; K=[signs[i]*W[i]*W[i] for i in range(n)]
    return W,K
def amp_batch(points):
    lines=[",".join(str(x) for x in W)+"|"+",".join(str(x) for x in K) for W,K in points]
    out=subprocess.run([BATCH],input="\n".join(lines),stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True).stdout.strip().split("\n")
    return [o if o.strip() in("SIGFPE","ERR") else F(o.strip()) for o in out]
def Wamp(W,signs):
    K=[signs[i]*W[i]*W[i] for i in range(len(W))]; return amp_batch([(W,K)])[0]
def lagrange(xs,ys):
    n=len(xs); c=[F(0)]*n
    for i in range(n):
        num=[F(1)]; den=F(1)
        for j in range(n):
            if j==i: continue
            new=[F(0)]*(len(num)+1)
            for k,a in enumerate(num): new[k]+=a*(-xs[j]); new[k+1]+=a
            num=new; den*=(xs[i]-xs[j])
        sc=ys[i]/den
        for k in range(len(num)): c[k]+=num[k]*sc
    return c
def peval(c,x):
    r=F(0)
    for a in reversed(c): r=r*x+a
    return r
def trim(c):
    c=list(c)
    while len(c)>1 and c[-1]==0: c=c[:-1]
    return c
def adaptive(vd,order,ret_deg=False):
    pts=list(order)
    for d in range(1,len(pts)-2):
        xs=pts[:d+1]; ys=[vd[t] for t in xs]; c=lagrange(xs,ys); held=pts[d+1:]
        if all(peval(c,t)==vd[t] for t in held) and len(held)>=2:
            return (trim(c),d) if ret_deg else trim(c)
    raise RuntimeError(f"did not settle (deg up to {len(pts)-3})")
def root_mult(c,t0):
    c=trim(c); m=0
    while len(c)>1 and peval(c,t0)==0:
        n=len(c); q=[F(0)]*(n-1); rem=c[-1]
        for k in range(n-2,-1,-1): q[k]=rem; rem=c[k]+rem*t0
        assert rem==0
        c=trim(q); m+=1
    if len(c)==1 and c[0]==0: return m+1
    return m
def D_full(W,n):
    p=F(1)
    for i in (0,1,2):
        for j in range(3,n): p*=(W[i]+W[j])
    return p
def wallfns(W,n):
    d={}; mi=[0,1,2]; pj=list(range(3,n))
    for i in mi:
        for j in pj: d[f"11_{i}_{j}"]=W[i]**2-W[j]**2
    for i in mi:
        for jk in itertools.combinations(pj,2): d[f"12_{i}_{jk[0]}_{jk[1]}"]=W[i]**2-W[jk[0]]**2-W[jk[1]]**2
    for i in mi:
        for jkl in itertools.combinations(pj,3): d[f"13_{i}_"+"_".join(map(str,jkl))]=W[i]**2-sum(W[x]**2 for x in jkl)
    return d
def sigtuple(W,n): return tuple(val>0 for key,val in sorted(wallfns(W,n).items()))
def measure_exponent(n,fn,tstar,delta,npts):
    sig=SIG(n)
    ts=[tstar-delta*k for k in range(1,npts+1)]+[tstar+delta*k for k in range(1,npts+1)]
    pts=[solve_full(fn(t),n,sig) for t in ts]; amps=amp_batch(pts)
    NL={};NR={}
    for t,(W,K),a in zip(ts,pts,amps):
        if a in('SIGFPE','ERR'): raise RuntimeError(f"SIGFPE t={t}")
        (NL if t<tstar else NR)[t]=a*D_full(W,n)
    WL,_=solve_full(fn(tstar-delta),n,sig); WR,_=solve_full(fn(tstar+delta),n,sig)
    fL=wallfns(WL,n); fR=wallfns(WR,n)
    flip=[k for k in fL if (fL[k]>0)!=(fR[k]>0)]
    cL,dL=adaptive(NL,sorted(NL,reverse=True),True); cR,dR=adaptive(NR,sorted(NR),True)
    contin=peval(cL,tstar)==peval(cR,tstar)
    diff=[(cR[i] if i<len(cR) else F(0))-(cL[i] if i<len(cL) else F(0)) for i in range(max(len(cL),len(cR)))]
    return root_mult(diff,tstar),flip,contin,(dL,dR)

print("="*72); print("PI ROUND-8 FOLLOW-UP (own oracle, no student code)"); print("="*72)

# (a) soft MINUS leg
print("\n--- soft MINUS leg: A_7/(i eps^2) -> 8*A_6^(2-) as eps->0 ---")
a=F(9); sig=SIG(7); fw=lambda e:[a-e,e,F(5),F(7),F(11)]
W0,_=solve_full(fw(F(0)),7,sig); W6=[W0[i] for i in [0,1,3,4,5,6]]
A6=Wamp(W6,[-1,-1,1,1,1,1]); target=F(8)*A6
print(f"  surviving 6pt TWO-minus A_6/i={A6}; 8*A_6={target}")
eps=[F(1,10**k) for k in range(2,8)]
s0=None;ck=True
for e in eps:
    Wf,_=solve_full(fw(e),7,sig); s=sigtuple(Wf,7)
    if s0 is None:s0=s
    elif s!=s0:ck=False
print(f"  eps in 1e-2..1e-7 single-chamber: {ck}")
amps=amp_batch([solve_full(fw(e),7,sig) for e in eps])
print("   eps        A_7/(i eps^2)/(8 A_6) [->1]")
for e,am in zip(eps,amps):
    print(f"   {float(e):.0e}  "+("SIGFPE" if am in('SIGFPE','ERR') else f"{float(am/(e*e)/target):.12f}"))
# exact via small-eps reconstruction
epsP=[F(1,k) for k in range(300,430)]
ptsP=[solve_full(fw(e),7,sig) for e in epsP]; ampsP=amp_batch(ptsP)
N7={e:am*D_full(solve_full(fw(e),7,sig)[0],7) for e,am in zip(epsP,ampsP) if am not in('SIGFPE','ERR')}
sP=sigtuple(solve_full(fw(F(1,10000)),7,sig)[0],7)
try:
    c,deg=adaptive(N7,[e for e in epsP if e in N7],True); L=c[2]/D_full(W0,7)
    print(f"  EXACT small-eps limit (deg {deg}): {L}   matches 8*A_6: {L==target}  c0={c[0]},c1={c[1]}")
except Exception as ex: print(f"  exact: {ex}")

# (b) n=7 (1=2)
print("\n--- n=7 (1=2) w2^2=w4^2+w5^2 exponent (expect 2) ---")
for npts in (60,76):
    try:
        m,flip,ct,degs=measure_exponent(7, lambda t:[F(2)+t,F(10)-t,F(3),F(4),F(29,5)], F(3), F(1,500), npts)
        print(f"  npts={npts}: exponent={m}(expect 2) continuous={ct} flips={flip} slicedeg={degs} -> {'OK' if (m==2 and ct and len(flip)==1) else 'CHECK'}")
        break
    except Exception as ex: print(f"  npts={npts}: {ex}")
print("\nDONE.")
