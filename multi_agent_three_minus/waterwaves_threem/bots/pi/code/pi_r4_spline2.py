#!/usr/bin/env python3
"""Clean spline test on an F-CONSTANT slice that crosses the plus-ordering wall
   omega_4 = omega_5 (D_9 != 0 there). If N_6=(A_6/i)*D_9 is a different polynomial
   on each side but A_6 stays finite/continuous, then N_6 is a genuine SPLINE and
   A_6 is NOT a single global rational function (it is rational per-chamber)."""
import subprocess, re, sys
from fractions import Fraction as Fr
from itertools import combinations

BG = "./bg"
def run_bg(n, free_w, signs):
    def fmt(x):
        x=Fr(x); return f"{x.numerator}/{x.denominator}" if x.denominator!=1 else str(x.numerator)
    cmd=[BG,"-n",str(n),"-w",",".join(fmt(w) for w in free_w),"-s",",".join(str(s) for s in signs)]
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    if r.returncode!=0 or "omega" not in r.stdout: return None
    om=re.search(r"omega = \{([^}]*)\}",r.stdout).group(1)
    omega=tuple(Fr(s.strip()) for s in om.split(","))
    m=re.search(r"A_\d+ = i \* \(([^)]*)\)",r.stdout)
    if m: return omega,Fr(m.group(1))
    m=re.search(r"A_\d+ = \(([^)]*)\) \+ i \* \(([^)]*)\)",r.stdout)
    if m: assert Fr(m.group(1))==0; return omega,Fr(m.group(2))
    raise RuntimeError(r.stdout)
def lag(pts,xq):
    s=Fr(0)
    for i,(xi,yi) in enumerate(pts):
        t=yi
        for j,(xj,_) in enumerate(pts):
            if j!=i: t*=(xq-xj)/(xi-xj)
        s+=t
    return s
def fits(samples,deg):
    if len(samples)<=deg+1: return None
    return all(lag(samples[:deg+1],x)==y for (x,y) in samples[deg+1:])
def pdeg(samples,maxdeg):
    for d in range(maxdeg+1):
        v=fits(samples,d)
        if v: return d
        if v is None: return "INCONCLUSIVE"
    return None
def csign(omega,signs):
    n=len(omega);k=[signs[i]*omega[i]**2 for i in range(n)];b=[]
    for r in range(1,n):
        for S in combinations(range(n),r):
            ks=sum(k[i] for i in S);b.append(0 if ks==0 else(1 if ks>0 else -1))
    return tuple(b)
def D9(omega,pairs):
    p=Fr(1)
    for (i,j) in pairs: p*=(omega[i]+omega[j])
    return p

n=6; minus=[0,1,2]; plus=[3,4,5]; signs=[-1,-1,-1,1,1,1]
pairs=[(i,j) for i in minus for j in plus]
# F-const slice: w4=5+t, w5=5-t (sumFree const); wall w4=w5 at t=0. w2,w3 minus fixed generic.
w2,w3=Fr(7,2),Fr(13,3)
def s(t):
    res=run_bg(n,[w2,w3,Fr(5)+t,Fr(5)-t],signs)
    return None if res is None else (t,res[0],res[1])
left =[x for x in (s(-Fr(k,80)) for k in range(1,24)) if x]   # t<0 -> w4<w5
right=[x for x in (s( Fr(k,80)) for k in range(1,24)) if x]   # t>0 -> w4>w5
def clean(side):
    if not side: return []
    ref=csign(side[len(side)//2][1],signs)
    return [(t,o,A) for (t,o,A) in side if csign(o,signs)==ref]
L,R=clean(left),clean(right)
print(f"left (w4<w5) clean: {len(L)}  right (w4>w5) clean: {len(R)}")
if len(L)>=14 and len(R)>=14:
    NL=[(t,A*D9(o,pairs)) for (t,o,A) in L]; NR=[(t,A*D9(o,pairs)) for (t,o,A) in R]
    dL=pdeg(NL,len(NL)-3); dR=pdeg(NR,len(NR)-3)
    print(f"N_6 left poly deg {dL}, right poly deg {dR}")
    if isinstance(dL,int) and isinstance(dR,int):
        # are the two polynomials the same function? test on a fresh probe in each domain
        probe=Fr(1,7)  # right-side value of t
        pL=lag(NL[:dL+1],probe); pR=lag(NR[:dR+1],probe)
        same=(pL==pR)
        vL=lag(NL[:dL+1],Fr(0)); vR=lag(NR[:dR+1],Fr(0))   # extrapolate N_6 to wall t=0
        aL=lag([(t,A) for (t,o,A) in L][:dL+1],Fr(0)); aR=lag([(t,A) for (t,o,A) in R][:dR+1],Fr(0))
        print(f"N_6 polynomials identical as functions? {same}   (expect False -> SPLINE)")
        print(f"N_6 at wall: left={vL} right={vR} equal? {vL==vR}")
        print(f"A_6/i at wall: left={aL} right={aR} continuous? {aL==aR}")
        verdict = (not same) and (aL==aR)
        print("VERDICT:", "N_6 is a genuine SPLINE; A_6 finite (kink, not pole) -> A_6 rational PER-CHAMBER, "
              "not one global rational function" if verdict else "inconclusive/unexpected")
else:
    print("insufficient clean samples")
