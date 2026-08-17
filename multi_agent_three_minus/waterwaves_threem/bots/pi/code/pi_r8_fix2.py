#!/usr/bin/env python3
"""PI round-8: clean n=7 (1=2) exponent via a tiny single-wall window.
Strategy: scan t around t*=3 in --double to find the nearest OTHER wall, shrink
the window below that gap, verify exactly one wall flips, then reconstruct N_7."""
import subprocess, sys, itertools
from fractions import Fraction as F
HERE=sys.path[0] or "."; BATCH=HERE+"/pi_batch"
SIG=lambda n:[-1,-1,-1]+[1]*(n-3)
def solve_full(freeW,n,signs):
    s1=signs[0]; sF=sum(freeW,F(0)); sS=sum(signs[i+1]*freeW[i]*freeW[i] for i in range(n-2))
    wn=-(s1*sF*sF+sS)/(F(2)*s1*sF); w1=-(sF+wn)
    W=[w1]+list(freeW)+[wn]; return W,[signs[i]*W[i]*W[i] for i in range(n)]
def amp_batch(points):
    lines=[",".join(str(x) for x in W)+"|"+",".join(str(x) for x in K) for W,K in points]
    out=subprocess.run([BATCH],input="\n".join(lines),stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True).stdout.strip().split("\n")
    return [o if o.strip() in("SIGFPE","ERR") else F(o.strip()) for o in out]
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
def adaptive(vd,order,ret=False):
    pts=list(order)
    for d in range(1,len(pts)-2):
        xs=pts[:d+1]; ys=[vd[t] for t in xs]; c=lagrange(xs,ys); held=pts[d+1:]
        if all(peval(c,t)==vd[t] for t in held) and len(held)>=2: return (trim(c),d) if ret else trim(c)
    raise RuntimeError(f"deg up to {len(pts)-3}")
def root_mult(c,t0):
    c=trim(c); m=0
    while len(c)>1 and peval(c,t0)==0:
        n=len(c); q=[F(0)]*(n-1); rem=c[-1]
        for k in range(n-2,-1,-1): q[k]=rem; rem=c[k]+rem*t0
        assert rem==0
        c=trim(q); m+=1
    return m+1 if (len(c)==1 and c[0]==0) else m
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

n=7; sig=SIG(7)
fn=lambda t:[F(2)+t,F(10)-t,F(3),F(4),F(29,5)]   # (1=2): w2^2=w4^2+w5^2, t*=3
tstar=F(3)
# find nearest OTHER wall to t*: sample signature on a grid, locate sign changes
print("scanning for nearest other wall to t*=3 ...")
grid=[tstar+F(k,2000) for k in range(-400,401) if k!=0]   # t in [2.8,3.2]
prev=None; changes=[]
for t in grid:
    W,_=solve_full(fn(t),n,sig)
    s={k:(v>0) for k,v in wallfns(W,n).items()}
    if prev is not None:
        for k in s:
            if s[k]!=prev[k]: changes.append((t,k))
    prev=s
# nearest change that is NOT the target wall family near t*=3
target_keys={"12_0_3_4"}  # minus idx0=leg2? careful: minus indices 0,1,2 = legs1,2,3; leg2=index1
# wall w2^2=w4^2+w5^2 -> minus index1 (leg2), plus 3,4 (legs4,5): key 12_1_3_4
target_keys={"12_1_3_4"}
others=[(t,k) for (t,k) in changes if k not in target_keys]
near=sorted(others,key=lambda x:abs(x[0]-tstar))[:6]
print("nearest non-target sign-changes:",[(float(t),k) for t,k in near[:6]])
gap=min((abs(t-tstar) for t,k in others), default=F(1,10))
print("gap to nearest other wall ~",float(gap))
delta=min(gap/F(20), F(1,2000))
print("using delta=",float(delta))
# reconstruct
for npts in (50,70,90):
    ts=[tstar-delta*k for k in range(1,npts+1)]+[tstar+delta*k for k in range(1,npts+1)]
    pts=[solve_full(fn(t),n,sig) for t in ts]; amps=amp_batch(pts)
    NL={};NR={};bad=False
    for t,(W,K),a in zip(ts,pts,amps):
        if a in('SIGFPE','ERR'): bad=True; break
        (NL if t<tstar else NR)[t]=a*D_full(W,n)
    if bad: print(f"  npts={npts}: SIGFPE"); continue
    WL,_=solve_full(fn(tstar-delta),n,sig); WR,_=solve_full(fn(tstar+delta),n,sig)
    fL=wallfns(WL,n); fR=wallfns(WR,n)
    flip=[k for k in fL if (fL[k]>0)!=(fR[k]>0)]
    try:
        cL,dL=adaptive(NL,sorted(NL,reverse=True),True); cR,dR=adaptive(NR,sorted(NR),True)
    except Exception as ex:
        print(f"  npts={npts}: {ex}"); continue
    contin=peval(cL,tstar)==peval(cR,tstar)
    diff=[(cR[i] if i<len(cR) else F(0))-(cL[i] if i<len(cL) else F(0)) for i in range(max(len(cL),len(cR)))]
    m=root_mult(diff,tstar)
    ok=(m==2 and contin and len(flip)==1)
    print(f"  npts={npts}: exponent={m}(expect 2) continuous={contin} flips={flip} deg={ (dL,dR)} -> {'OK' if ok else 'CHECK'}")
    if m and contin: break
print("DONE.")
