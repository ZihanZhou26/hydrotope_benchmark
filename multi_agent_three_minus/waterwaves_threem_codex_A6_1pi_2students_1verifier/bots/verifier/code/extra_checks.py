#!/usr/bin/env python3
"""(a) H1 common-coefficient rejection for ALL four (e_m,e_p) sign choices.
   (b) 8-word chamber selector: every random on-shell point lands in the set."""
from fractions import Fraction as F
from itertools import combinations
import random, oracle

SIG=[-1,-1,-1,1,1,1]; M=[0,1,2]; P=[3,4,5]

def onshell_from_free(freeW):
    fw=[F(x) for x in freeW]; s=[F(x) for x in SIG]
    sumFree=sum(fw); sumSig=sum(s[i+1]*fw[i]*fw[i] for i in range(4))
    wn=-(s[0]*sumFree*sumFree+sumSig)/(2*s[0]*sumFree); w1=-(sumFree+wn)
    return [w1]+fw+[wn]

def Phi(w,a,b,e_m,e_p):
    r=[x for x in M if x not in (a,b)][0]
    beta2=min(w[a]**2,w[b]**2); idx=[r]+P; tot=F(0)
    for k in range(len(idx)+1):
        for S in combinations(idx,k):
            arg=beta2
            if r in S: arg-=e_m*w[r]**2
            for j in S:
                if j in P: arg-=e_p*w[j]**2
            if arg>0: tot+=((-1)**len(S))*arg**3
    return w[a]*w[b]*tot
def sumPhi(w,e_m,e_p): return sum(Phi(w,a,b,e_m,e_p) for a,b in combinations(M,2))

print("== (a) H1 common-C rejection, all four sign choices ==")
pts=[onshell_from_free(fw) for fw in
     [[1,2,4,8],[3,5,2,7],[1,3,2,9],[2,7,1,11],[1,5,6,2],[4,9,1,13]]]
amps=[oracle.amp_from_omega_sigma(p,SIG)[1] for p in pts]
for e_m in (1,-1):
  for e_p in (1,-1):
    # fit common C from first point where sumPhi!=0, test on the rest
    C=None; consistent=True; note=""
    for p,A in zip(pts,amps):
        s=sumPhi(p,e_m,e_p)
        if s==0:
            if A!=0: consistent=False; note="sumPhi=0 but A!=0"; break
            continue
        c=A/s
        if C is None: C=c
        elif c!=C: consistent=False; note="C mismatch {} vs {}".format(C,c); break
    verdict = "CONSISTENT (not rejected!)" if consistent else "REJECTED: "+note
    print("  (e_m,e_p)=({:+d},{:+d}): C={} -> {}".format(e_m,e_p,C,verdict))

print("\n== (b) 8-word selector: random on-shell points all land in the set ==")
WORDS={"+-+--+","+--++-","+--+-+","+---++","-+++--","-++-+-","-++--+","-+-++-"}
def word_of(omega):
    order=sorted(range(6), key=lambda i:-abs(omega[i]))  # descending |omega|
    return "".join("+" if SIG[i]>0 else "-" for i in order)
random.seed(1)
bad=0; total=0; seen=set()
for _ in range(4000):
    fw=[F(random.randint(1,30),random.randint(1,6)) for _ in range(4)]
    om=onshell_from_free(fw)
    mags=[abs(x) for x in om]
    if len(set(mags))<6: continue      # skip ties (walls)
    # standard sheet requires w2..w5>0 (they are) and solved w1,w6<0:
    if not (om[0]<0 and om[5]<0): continue
    w=word_of(om); total+=1; seen.add(w)
    if w not in WORDS: bad+=1
print("  sampled {} generic standard-sheet points; words outside set: {}".format(total,bad))
print("  distinct words seen ({}): {}".format(len(seen), sorted(seen)))
print("  all 8 realized:", seen==WORDS)
