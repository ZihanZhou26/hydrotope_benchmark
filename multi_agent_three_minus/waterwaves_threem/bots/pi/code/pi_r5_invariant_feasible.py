#!/usr/bin/env python3
"""
PI round-5 FEASIBILITY test (modular, fast) for the proposed round-5 attack:
  Is the GLOBAL symmetric N = A_6*(e3m+e3p)/(i 2^5 g^-3), restricted to a single
  invariant-REGION (constant sign of every mixed wall), a POLYNOMIAL in the 4
  invariants (e1=e1+, e2=e2+, e3m=w1w2w3, e3p=w4w5p6), weighted degree 11
  (weights 1,2,3,3)?   Linear algebra over GF(p) with held-out verification.
  (A non-polynomial fitting 40 held-out points mod p has prob ~ p^-40.)
"""
import subprocess, re, itertools, random
from fractions import Fraction as F
BG="./bg"; P=(1<<61)-1; random.seed(2026)

def oracle(fw):
    ws=",".join(str(x) for x in fw)
    o=subprocess.run([BG,"-n","6","-w",ws,"-s","-1,-1,-1,1,1,1","-g","1"],
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    if o.returncode!=0: return None
    m=re.search(r"omega = \{([^}]*)\}",o.stdout)
    if not m: return None
    omg=[F(s) for s in m.group(1).split(",")]
    m=re.search(r"A_6 = i \* \(([^)]*)\)",o.stdout)
    if not m: return None
    return F(m.group(1)),omg

SIG=[-1,-1,-1,1,1,1]
def mixed_subsets():
    legs=set(range(6)); subs=[]; seen=set()
    for r in range(2,6):
        for S in itertools.combinations(range(6),r):
            sg=[SIG[i] for i in S]
            if not(-1 in sg and 1 in sg): continue
            comp=frozenset(legs-set(S))
            if frozenset(S) in seen or comp in seen: continue
            seen.add(frozenset(S)); subs.append(S)
    return subs
MIX=mixed_subsets()
def signvec(omg):
    out=[]
    for S in MIX:
        kS=sum(SIG[i]*omg[i]**2 for i in S)
        out.append(0 if kS==0 else (1 if kS>0 else -1))
    return tuple(out)
def fmod(x): return (x.numerator % P)*pow(x.denominator,P-2,P) % P
def invariants(omg):
    w1,w2,w3,w4,w5,w6=omg
    return (w4+w5+w6, w4*w5+w4*w6+w5*w6, w1*w2*w3, w4*w5*w6)

# monomials weighted deg 11, weights (1,2,3,3)
monos=[(a,b,c,d) for a in range(12) for b in range(7) for c in range(4) for d in range(4)
       if a+2*b+3*c+3*d==11]
K=len(monos)
def rowmod(inv):
    e1,e2,e3m,e3p=[fmod(x) for x in inv]
    return [ pow(e1,a,P)*pow(e2,b,P)%P*pow(e3m,c,P)%P*pow(e3p,d,P)%P for (a,b,c,d) in monos]

def solve_mod(M,v):
    n=len(M); A=[row[:]+[v[i]] for i,row in enumerate(M)]
    col=0; piv=[]
    for r in range(n):
        # find pivot
        pr=None
        for rr in range(r,n):
            if A[rr][r]%P!=0: pr=rr; break
        if pr is None: return None
        A[r],A[pr]=A[pr],A[r]
        inv=pow(A[r][r],P-2,P)
        A[r]=[(x*inv)%P for x in A[r]]
        for rr in range(n):
            if rr!=r and A[rr][r]!=0:
                f=A[rr][r]; A[rr]=[(A[rr][k]-f*A[r][k])%P for k in range(n+1)]
    return [A[i][n]%P for i in range(n)]

print("generating samples...")
groups={}; trials=0
while trials<5000 and sum(len(v) for v in groups.values())<3000:
    trials+=1
    fw=[F(random.randint(-90,90),random.randint(1,9)) for _ in range(4)]
    r=oracle(fw)
    if r is None: continue
    A,omg=r
    sv=signvec(omg)
    if 0 in sv: continue
    inv=invariants(omg); N=A*(inv[2]+inv[3])
    groups.setdefault(sv,[]).append((inv,N))
sv_best=max(groups,key=lambda k:len(groups[k])); data=groups[sv_best]
print("regions:",len(groups)," largest region pts:",len(data)," monomials:",K)
if len(data)<K+40:
    print("not enough points in one region; got",len(data)); raise SystemExit
fit=data[:K]; test=data[K:K+40]
M=[rowmod(inv) for (inv,_) in fit]; v=[fmod(N) for (_,N) in fit]
sol=solve_mod(M,v)
if sol is None:
    print("singular system (region too thin / monomials dependent on slice)")
else:
    bad=0
    for (inv,N) in test:
        pred=sum(sol[j]*rowmod(inv)[j] for j in range(K))%P
        if pred!=fmod(N): bad+=1
    print("HELD-OUT (40 pts): bad=%d"%bad)
    nz=sum(1 for s in sol if s!=0)
    if bad==0:
        print(">>> SUCCESS: N is a weighted-deg-11 polynomial in (e1,e2,e3m,e3p) on this region.")
        print("    nonzero monomials: %d / %d"%(nz,K))
    else:
        print(">>> FAIL: not a single deg-11 invariant polynomial on this region.")

# also test: is N a SINGLE global invariant polynomial (NO spline)? fit across ALL regions
allpts=[(inv,N) for g in groups.values() for (inv,N) in g]
random.shuffle(allpts)
fit=allpts[:K]; test=allpts[K:K+60]
M=[rowmod(inv) for (inv,_) in fit]; v=[fmod(N) for (_,N) in fit]
sol=solve_mod(M,v)
if sol is None:
    print("global: singular")
else:
    bad=sum(1 for (inv,N) in test if sum(sol[j]*rowmod(inv)[j] for j in range(K))%P!=fmod(N))
    print("GLOBAL (all regions mixed) held-out bad=%d  -> %s"%(bad,
          "N is ONE global invariant polynomial (no spline!)" if bad==0 else "N is a genuine SPLINE (multiple pieces), as expected"))
