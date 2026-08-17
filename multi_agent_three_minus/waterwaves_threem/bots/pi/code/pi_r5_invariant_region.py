#!/usr/bin/env python3
"""
PI round-5 feasibility, take 2: group leg-points by SYMMETRIC region labels and
test whether the global symmetric N = A_6*(e3m+e3p) is a weighted-deg-11
polynomial in (e1,e2,e3m,e3p) within each symmetric region.

Symmetric region labels tried:
  (A) canonical mixed-wall sign type (orbit under S3 x S3 x Z2) -- student-1's 12 types
  (B) (sign W1, sign W2, sign e1) where
        W1 = prod_{i in M,j in P}(wi - wj)     [(1=1) difference branch]
        W2 = prod over (1=2) walls (wi^2-wj^2-wk^2)
Modular linear algebra over GF(P), held-out verification.
"""
import subprocess, re, itertools, random
from fractions import Fraction as F
BG="./bg"; P=(1<<61)-1; random.seed(7)

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

MINUS=[0,1,2]; PLUS=[3,4,5]; SIG=[-1,-1,-1,1,1,1]
def W1(omg):
    p=F(1)
    for i in MINUS:
        for j in PLUS: p*=(omg[i]-omg[j])
    return p
def W2(omg):
    p=F(1)
    for i in MINUS:
        for j,k in itertools.combinations(PLUS,2): p*=(omg[i]**2-omg[j]**2-omg[k]**2)
    for i in PLUS:
        for j,k in itertools.combinations(MINUS,2): p*=(omg[i]**2-omg[j]**2-omg[k]**2)
    return p
def sgn(x): return 0 if x==0 else (1 if x>0 else -1)

# canonical mixed-wall type (orbit under S3xS3xZ2)
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
import itertools as it
PERMS=[]
for pm in it.permutations(MINUS):
    for pp in it.permutations(PLUS):
        for sw in (False,True):
            PERMS.append((pm,pp,sw))
def relabel(omg,perm):
    pm,pp,sw=perm
    new=[None]*6
    for a,i in enumerate(MINUS): new[i]=omg[pm[a]]
    for a,j in enumerate(PLUS):  new[j]=omg[pp[a]]
    if sw:
        new=[new[3],new[4],new[5],new[0],new[1],new[2]]
    return new
def signvec(omg):
    out=[]
    for S in MIX:
        kS=sum(SIG[i]*omg[i]**2 for i in S); out.append(sgn(kS))
    return tuple(out)
def canon_type(omg):
    best=None
    for perm in PERMS:
        sv=signvec(relabel(omg,perm))
        if best is None or sv<best: best=sv
    return best

def fmod(x): return (x.numerator % P)*pow(x.denominator,P-2,P) % P
def invariants(omg):
    w1,w2,w3,w4,w5,w6=omg
    return (w4+w5+w6, w4*w5+w4*w6+w5*w6, w1*w2*w3, w4*w5*w6)
monos=[(a,b,c,d) for a in range(12) for b in range(7) for c in range(4) for d in range(4)
       if a+2*b+3*c+3*d==11]
K=len(monos)
def rowmod(inv):
    e1,e2,e3m,e3p=[fmod(x) for x in inv]
    return [pow(e1,a,P)*pow(e2,b,P)%P*pow(e3m,c,P)%P*pow(e3p,d,P)%P for (a,b,c,d) in monos]
def solve_mod(M,v):
    n=len(M); A=[row[:]+[v[i]] for i,row in enumerate(M)]
    for r in range(n):
        pr=None
        for rr in range(r,n):
            if A[rr][r]%P!=0: pr=rr; break
        if pr is None: return None
        A[r],A[pr]=A[pr],A[r]
        inv=pow(A[r][r],P-2,P); A[r]=[(x*inv)%P for x in A[r]]
        for rr in range(n):
            if rr!=r and A[rr][r]!=0:
                f=A[rr][r]; A[rr]=[(A[rr][k]-f*A[r][k])%P for k in range(n+1)]
    return [A[i][n]%P for i in range(n)]
def test_group(data,label):
    if len(data)<K+30: return "  %-28s pts=%d (too few)"%(label,len(data))
    fit=data[:K]; test=data[K:K+30]
    M=[rowmod(inv) for (inv,_) in fit]; v=[fmod(N) for (_,N) in fit]
    sol=solve_mod(M,v)
    if sol is None: return "  %-28s pts=%d SINGULAR"%(label,len(data))
    bad=sum(1 for (inv,N) in test if sum(sol[j]*rowmod(inv)[j] for j in range(K))%P!=fmod(N))
    nz=sum(1 for s in sol if s!=0)
    return "  %-28s pts=%d held-out-bad=%d  nz-monos=%d  %s"%(label,len(data),bad,nz,
            "<= INVARIANT-POLYNOMIAL!" if bad==0 else "(not inv-poly)")

print("sampling...");
gtype={}; gWW={}; tot=0; trials=0
while trials<5000 and tot<3500:
    trials+=1
    fw=[F(random.randint(-90,90),random.randint(1,9)) for _ in range(4)]
    r=oracle(fw)
    if r is None: continue
    A,omg=r
    if 0 in signvec(omg): continue
    inv=invariants(omg); N=A*(inv[2]+inv[3])
    gWW.setdefault((sgn(W1(omg)),sgn(W2(omg))),[]).append((inv,N))
    ct=canon_type(omg)
    gtype.setdefault(ct,[]).append((inv,N))
    tot+=1
print("total pts:",tot," canonical types:",len(gtype)," (signW1,signW2) groups:",len(gWW))
print("\n[B] grouped by (sign W1, sign W2):")
for k in sorted(gWW,key=lambda k:-len(gWW[k]))[:8]:
    print(test_group(gWW[k],str(k)))
print("\n[A] grouped by canonical mixed-wall type (largest 6):")
for k in sorted(gtype,key=lambda k:-len(gtype[k]))[:6]:
    print(test_group(gtype[k],"type#"+str(hash(k)%10000)))
