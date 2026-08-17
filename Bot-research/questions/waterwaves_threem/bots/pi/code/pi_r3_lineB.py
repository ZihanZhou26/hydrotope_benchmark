#!/usr/bin/env python3
"""Factor the generic line-B denominator of A_6 and identify each root's
vanishing omega-forms (no false positives: we look at actual roots)."""
import subprocess, re
from fractions import Fraction as F
from itertools import combinations
BG="./bg"; SIG=[-1,-1,-1,1,1,1]
def onshell(fw):
    s0=SIG[0]; sF=sum(fw); sS=sum(SIG[i+1]*fw[i]**2 for i in range(4))
    wn=-(s0*sF**2+sS)/(2*s0*sF); w1=-(sF+wn)
    W=[w1]+list(fw)+[wn]; K=[SIG[i]*W[i]**2 for i in range(6)]; return W,K
def amp(K,W):
    Ks=",".join(str(F(k)) for k in K); Ws=",".join(str(F(w)) for w in W)
    o=subprocess.run([BG,"--amp","-K",Ks,"-W",Ws,"-g","1"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    if o.returncode!=0: return None
    m=re.search(r"A_\d+ = i \* \(([-0-9/]+)\)", o.stdout)
    if m: return F(m.group(1))
    m=re.search(r"A_\d+ = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)", o.stdout)
    if m: assert F(m.group(1))==0; return F(m.group(2))
    raise RuntimeError(o.stdout)
def nullvec(rows):
    M=[r[:] for r in rows]; nr=len(M); nc=len(M[0]); piv=[]; r=0
    for c in range(nc):
        pr=next((i for i in range(r,nr) if M[i][c]!=0),None)
        if pr is None: continue
        M[r],M[pr]=M[pr],M[r]; inv=M[r][c]; M[r]=[x/inv for x in M[r]]
        for i in range(nr):
            if i!=r and M[i][c]!=0:
                f=M[i][c]; M[i]=[a-f*b for a,b in zip(M[i],M[r])]
        piv.append(c); r+=1
        if r==nr: break
    fc=[c for c in range(nc) if c not in piv]
    if not fc: return None
    x=[F(0)]*nc; x[fc[0]]=F(1)
    for idx,c in enumerate(piv): x[c]=-M[idx][fc[0]]
    return x
def peval(c,t): return sum(ci*t**i for i,ci in enumerate(c))
def ptrim(c):
    c=c[:]
    while len(c)>1 and c[-1]==0: c.pop()
    return c
def pdivlin(c,root):
    """divide poly c(t) by (t-root), return quotient (assumes exact)."""
    n=len(c)-1; q=[F(0)]*n; rem=c[n]
    for i in range(n-1,-1,-1):
        q[i]=rem; rem=c[i]+rem*root
    return q,rem
base=[F(2),F(3),F(5),F(7)]; direction=[F(2),F(-1),F(-1),F(0)]
pts=[]; sig0=None
for k in range(-90,91):
    t=F(k,240); free=[base[i]+t*direction[i] for i in range(4)]
    W,K=onshell(free)
    if any(w==0 for w in W): continue
    if any(sum(K[i] for i in S)==0 for r in range(1,6) for S in combinations(range(6),r)): continue
    cs=tuple(1 if sum(K[i] for i in S)>0 else -1 for r in range(1,6) for S in combinations(range(6),r))+tuple(1 if w>0 else -1 for w in W)
    if sig0 is None: sig0=cs
    if cs!=sig0: continue
    a=amp(K,W)
    if a is None: continue
    pts.append((t,a))
ts=[p[0] for p in pts]; ys=[p[1] for p in pts]
print(f"line B in-chamber pts: {len(pts)}")
model=None
for dD in range(0,8):
    dN=dD+18; need=dN+dD+2
    if len(pts)<need+4: break
    rows=[[t**i for i in range(dN+1)]+[-y*t**j for j in range(dD+1)] for t,y in zip(ts[:need],ys[:need])]
    x=nullvec(rows)
    if x is None: continue
    N,D=x[:dN+1],x[dN+1:]
    if all(d==0 for d in D): continue
    if all(peval(N,t)==y*peval(D,t) for t,y in zip(ts[need:],ys[need:])):
        model=(N,D,dD); break
N,D,dD=model
Dt=ptrim(D); lead=Dt[-1]; Dt=[c/lead for c in Dt]
print(f"minimal dD={dD}; D(t) monic coeffs = {[str(c) for c in Dt]}")
# find rational roots by scanning a wide set of candidate rationals
roots=[]
rem=Dt[:]
# try rational roots p/q with small p,q
cands=set()
for p in range(-200,201):
    for q in range(1,13):
        cands.add(F(p,q))
changed=True
while changed and len(rem)>1:
    changed=False
    for r in sorted(cands):
        if peval(rem,r)==0:
            q,rr=pdivlin(rem,r)
            if rr==0:
                roots.append(r); rem=ptrim(q); changed=True; break
print(f"rational roots found: {[str(r) for r in roots]}; residual deg after factoring = {len(ptrim(rem))-1}")
for r in roots:
    free=[base[i]+r*direction[i] for i in range(4)]; W,K=onshell(free)
    zer=[]
    for i in range(3):
        for j in range(3,6):
            if W[i]+W[j]==0: zer.append(f"w{i+1}+w{j+1}")
    for rr in range(2,5):
        for S in combinations(range(6),rr):
            wS=sum(W[s] for s in S); kS=sum(K[s] for s in S)
            if kS!=0 and wS**2-abs(kS)==0: zer.append("D_"+"".join(str(s+1) for s in S))
    print(f"  root t*={r}: omega={[str(w) for w in W]}  vanishing: {zer}")
