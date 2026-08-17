#!/usr/bin/env python3
"""Confirm minimal denominator of A_6 is (e3m+e3p)^1 (NOT D_9=(e3m+e3p)^3).
Per chamber slice: reconstruct A_6*(e3m+e3p) and confirm the reduced denominator
is a PURE power of sumFree (the leg-1,6 solve artifact) -- no (e3m+e3p) factor.
That certifies N := A_6*(e3m+e3p) is a polynomial in the 6 freqs (per chamber)."""
from fractions import Fraction as F
import sympy as sp
import harness as h, chambers_n6 as cn, inv
SIG=[-1,-1,-1,1,1,1]; t=sp.Symbol('t')

def full_sig(oms):
    sq=[w*w for w in oms]; ws=cn.wall_signs(sq)
    if ws is None: return None
    a,b=sq[0:3],sq[3:6]
    if 0 in [a[0]-a[1],a[0]-a[2],a[1]-a[2],b[0]-b[1],b[0]-b[2],b[1]-b[2]]: return None
    sa=tuple(1 if a[i]>a[j] else -1 for i,j in [(0,1),(0,2),(1,2)])
    sb=tuple(1 if b[i]>b[j] else -1 for i,j in [(0,1),(0,2),(1,2)])
    return ws+(sa,sb)
def solve_exact(A,b):
    n=len(A); M=[[F(A[i][j]) for j in range(n)]+[F(b[i])] for i in range(n)]
    for col in range(n):
        piv=next((r for r in range(col,n) if M[r][col]!=0),None)
        if piv is None: return None
        M[col],M[piv]=M[piv],M[col]; pv=M[col][col]; M[col]=[x/pv for x in M[col]]
        for r in range(n):
            if r!=col and M[r][col]!=0:
                f=M[r][col]; M[r]=[M[r][k]-f*M[col][k] for k in range(n+1)]
    return [M[i][n] for i in range(n)]
def reconstruct(pts,cap=40):
    nP=len(pts)
    for total in range(0,cap):
        for dD in range(0,total+1):
            dN=total-dD; nun=(dN+1)+dD
            if nP<nun+5: continue
            rows,rhs=[],[]
            for (x,G) in pts[:nun]:
                rows.append([x**j for j in range(dN+1)]+[-G*x**k for k in range(1,dD+1)]); rhs.append(G)
            sol=solve_exact(rows,rhs)
            if sol is None: continue
            Nc=sol[:dN+1]; Dc=[F(1)]+sol[dN+1:]
            if all((sum(c*x**k for k,c in enumerate(Dc))!=0 and
                    sum(c*x**j for j,c in enumerate(Nc))==G*sum(c*x**k for k,c in enumerate(Dc)))
                   for (x,G) in pts[nun:]):
                return dN,dD,Nc,Dc
    return None

def run(base, vary, mult_ee=1):
    s0=full_sig(cn.solve_squares(base)); pts=[]
    for j in range(-95,96):
        tt=F(j,60); free=list(base); free[vary-2]=base[vary-2]+tt
        oms=cn.solve_squares(free)
        if oms is None or any(w==0 for w in oms): continue
        if full_sig(oms)!=s0: continue
        e1,e2,e3m,e3p=inv.invariants(oms)
        try: im,_,_=h.on_shell(free,SIG)
        except Exception: continue
        pts.append((tt, im*(e3m+e3p)**mult_ee))
    if len(pts)<25: return ("few pts",len(pts))
    res=reconstruct(pts)
    if res is None: return ("recon fail",len(pts))
    dN,dD,Nc,Dc=res
    Dpoly=sum(sp.Rational(c.numerator,c.denominator)*t**k for k,c in enumerate(Dc))
    sf0=sum(base); sumF=sp.Rational(sf0.numerator,sf0.denominator)+t
    pure = sp.simplify(Dpoly/sumF**dD)
    return (dN,dD,bool(pure.is_number and pure!=0),len(pts))

if __name__=="__main__":
    chambers,*_=cn.scan(400000, seed=3)
    items=sorted(chambers.items(), key=lambda kv:-kv[1][0])
    print(f"{len(items)} chamber types found. Testing A_6*(e3m+e3p): is reduced denom pure-sumFree?\n")
    allok=True; tested=0
    for idx,(sig,(cnt,free,sq)) in enumerate(items):
        base=[F(x) for x in free]
        msgs=[]
        for vary in (4,5,2,3):
            r=run(base,vary,mult_ee=1)
            if isinstance(r[0],str):
                msgs.append(f"w{vary}:{r[0]}({r[1]})"); continue
            dN,dD,pure,npts=r
            tested+=1; allok=allok and pure
            msgs.append(f"w{vary}:degN={dN},degD={dD},pureSF={pure}")
        print(f"  T{idx} (cnt {cnt}): " + " | ".join(msgs))
    print(f"\nAll tested slices give pure-sumFree denom (=> minimal denom (e3m+e3p)^1): {allok}  [{tested} slices]")
