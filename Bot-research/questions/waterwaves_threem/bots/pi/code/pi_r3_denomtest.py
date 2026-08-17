#!/usr/bin/env python3
"""PI round-3: test explicit GLOBAL denominator hypotheses for A_6.

On sumFree-constant on-shell lines (all omega_i polynomial in t), test whether
A_6(t) * Dcand(t) is a POLYNOMIAL in t (degree <= 8 + deg Dcand), for candidate
global denominators Dcand built from the mixed-pair structure discovered:
  H1: prod_{i in M, j in P} (w_i + w_j)               [9 linear factors]
  H2: prod_{mixed pairs} D_{ij} = w_{ij}^2 - |k_{ij}|  [9 propagator factors]
  H3: prod over mixed pairs of (w_i + w_j) but only the 'active branch'
Method: if A*Dcand is a polynomial of degree d, fit it on d+1 pts, verify on rest.
Run on several lines / chambers; a TRUE denominator must work on every chamber.
"""
import subprocess, re
from fractions import Fraction as F
from itertools import combinations

BG = "./bg"; SIG = [-1, -1, -1, 1, 1, 1]
M = [0, 1, 2]; P = [3, 4, 5]

def onshell(freeW):
    s0=SIG[0]; sF=sum(freeW); sS=sum(SIG[i+1]*freeW[i]**2 for i in range(4))
    wn=-(s0*sF**2+sS)/(2*s0*sF); w1=-(sF+wn)
    W=[w1]+list(freeW)+[wn]; K=[SIG[i]*W[i]**2 for i in range(6)]
    return W,K

def amp(K,W):
    Ks=",".join(str(F(k)) for k in K); Ws=",".join(str(F(w)) for w in W)
    o=subprocess.run([BG,"--amp","-K",Ks,"-W",Ws,"-g","1"],stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE,universal_newlines=True)
    if o.returncode!=0: return None
    m=re.search(r"A_\d+ = i \* \(([-0-9/]+)\)", o.stdout)
    if m: return F(m.group(1))
    m=re.search(r"A_\d+ = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)", o.stdout)
    if m: assert F(m.group(1))==0; return F(m.group(2))
    raise RuntimeError(o.stdout)

def solve_lin(A,b):
    n=len(A); M_=[A[i][:]+[b[i]] for i in range(n)]
    for c in range(n):
        pr=next((i for i in range(c,n) if M_[i][c]!=0),None)
        if pr is None: return None
        M_[c],M_[pr]=M_[pr],M_[c]; inv=M_[c][c]; M_[c]=[x/inv for x in M_[c]]
        for i in range(n):
            if i!=c and M_[i][c]!=0:
                f=M_[i][c]; M_[i]=[a-f*bb for a,bb in zip(M_[i],M_[c])]
    return [M_[i][n] for i in range(n)]

def is_poly(ts,ys,deg):
    if len(ts)<deg+1: return None
    A=[[t**i for i in range(deg+1)] for t in ts[:deg+1]]; b=ys[:deg+1]
    sol=solve_lin(A,b)
    if sol is None: return False
    return all(sum(c*t**i for i,c in enumerate(sol))==y for t,y in zip(ts[deg+1:],ys[deg+1:]))

def gather(base,direction,npts=80,denom=240):
    pts=[]; sig0=None
    for k in range(-npts,npts+1):
        t=F(k,denom); free=[base[i]+t*direction[i] for i in range(4)]
        W,K=onshell(free)
        if any(w==0 for w in W): continue
        if any(sum(K[i] for i in S)==0 for r in range(1,6) for S in combinations(range(6),r)): continue
        cs=tuple(1 if sum(K[i] for i in S)>0 else -1 for r in range(1,6) for S in combinations(range(6),r))+tuple(1 if w>0 else -1 for w in W)
        if sig0 is None: sig0=cs
        if cs!=sig0: continue
        a=amp(K,W)
        if a is None: continue
        pts.append((t,W,K,a))
    return pts

def Dcand_value(name,W,K):
    if name=="H1_prod_wi+wj":
        v=F(1)
        for i in M:
            for j in P: v*= (W[i]+W[j])
        return v, 9
    if name=="H2_prod_Dij":
        v=F(1)
        for i in M:
            for j in P:
                wS=W[i]+W[j]; kS=K[i]+K[j]; v*=(wS**2-abs(kS))
        return v, 18  # each Dij is degree 2 -> total deg 18
    if name=="H1b_prod_(wi+wj)_only_pairs_signed":
        # |w_i+w_j| variant
        v=F(1)
        for i in M:
            for j in P: v*= abs(W[i]+W[j])
        return v, 9
    raise ValueError(name)

def test_line(base,direction,tag):
    pts=gather(base,direction)
    print(f"--- line {tag}: {len(pts)} in-chamber pts, sumFree={sum(base)}")
    if len(pts)<40:
        print("    too few"); return
    ts=[p[0] for p in pts]
    for name in ["H1_prod_wi+wj","H2_prod_Dij"]:
        ys=[]; degD=None
        ok_build=True
        for (t,W,K,a) in pts:
            val,degD=Dcand_value(name,W,K)
            ys.append(a*val)
        # A*Dcand should be polynomial of degree <= 8 + degD ; search smallest working degree
        worked=None
        for d in range(0, 8+degD+1):
            if is_poly(ts,ys,d):
                worked=d; break
        print(f"    {name}: A_6*Dcand polynomial? {'YES at deg '+str(worked) if worked is not None else 'NO (up to deg '+str(8+degD)+')'}")

if __name__=="__main__":
    lines=[
        ([F(2),F(3),F(5),F(7)],[F(2),F(-1),F(-1),F(0)],"B(generic)"),
        ([F(2),F(3),F(5),F(7)],[F(1),F(-1),F(1),F(-1)],"A"),
        ([F(1),F(6),F(4),F(2)],[F(0),F(1),F(0),F(-1)],"D"),
        ([F(3),F(11,2),F(4),F(9,2)],[F(1),F(1),F(-1),F(-1)],"C"),
    ]
    for b,d,t in lines:
        test_line(b,d,t)
