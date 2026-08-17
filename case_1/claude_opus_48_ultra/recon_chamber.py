"""Reconstruct A_5 as a rational function of free vars (w2,w3,w4) within ONE chamber
(fixed sign vector of all subset-sum momenta). Non-symmetric homogeneous recon."""
from bg import amp_two_minus, two_minus_sigma
from fractions import Fraction as Q
from itertools import combinations, product as iproduct
import itertools, sys
from recon import rref_nullspace

def chamber_sig(kL):
    n=len(kL); sig=[]
    for r in range(2,n):
        for S in combinations(range(n), r):
            ks=sum(kL[i] for i in S)
            sig.append(1 if ks>0 else (-1 if ks<0 else 0))
    return tuple(sig)

def monomials(deg, nvars=3):
    res=[]
    def rec(rem, idx, cur):
        if idx==nvars-1:
            res.append(tuple(cur+[rem])); return
        for e in range(rem+1):
            rec(rem-e, idx+1, cur+[e])
    rec(deg,0,[]); return res

def monval(exps, x):
    v=Q(1)
    for xi,e in zip(x,exps):
        if e: v*=xi**e
    return v

# reference point defining the chamber
ref_free=[Q(2),Q(5,2),Q(3,2)]   # the "207" chamber (plus leg w4 smallest)
A0,k0,w0=amp_two_minus(5,ref_free)
refsig=chamber_sig(k0)
print("reference free=",ref_free," A=",A0.im," sig=",refsig)

# collect points in same chamber
grid=[Q(a,2) for a in range(1,16)]+[Q(2),Q(5,2),Q(3),Q(7,2),Q(4),Q(9,2),Q(5)]
grid=sorted(set(grid))
pts=[]; seen=set()
for combo in itertools.product(grid,repeat=3):
    free=list(combo)
    try: A,kL,wL=amp_two_minus(5,free)
    except Exception: continue
    if chamber_sig(kL)!=refsig: continue
    key=tuple(free)
    if key in seen: continue
    seen.add(key); pts.append((tuple(free),A.im))
    if len(pts)>=300: break
print("collected", len(pts),"points in chamber")

# homogeneous recon: A is degree-6 homogeneous in (w2,w3,w4)? Actually w1,w5 derived are
# degree-1 homogeneous in free vars, so A is degree-6 homogeneous. N deg 6+dD, D deg dD.
dA=6
for dD in range(0,9):
    NB=monomials(dA+dD); DB=monomials(dD)
    nv=len(NB)+len(DB)
    if len(pts)<nv+4: print(f"  dD={dD}: need {nv} have {len(pts)} skip"); continue
    rows=[]
    for (x,Aim) in pts:
        rows.append([Aim*monval(l,x) for l in DB]+[-monval(l,x) for l in NB])
    basis,_=rref_nullspace(rows)
    print(f"  dD={dD}: vars={nv} nullspace dim={len(basis)}",flush=True)
    if basis:
        import sympy as sp
        w2,w3,w4=sp.symbols('w2 w3 w4')
        vec=basis[0]; Dc=vec[:len(DB)]; Nc=vec[len(DB):]
        Dexpr=sum(sp.Rational(Dc[i])*w2**DB[i][0]*w3**DB[i][1]*w4**DB[i][2] for i in range(len(DB)))
        Nexpr=sum(sp.Rational(Nc[i])*w2**NB[i][0]*w3**NB[i][1]*w4**NB[i][2] for i in range(len(NB)))
        print("  D=",sp.factor(Dexpr))
        print("  N=",sp.factor(Nexpr))
        print("  A=N/D =",sp.factor(Nexpr/Dexpr) if Dexpr!=0 else None)
        break
