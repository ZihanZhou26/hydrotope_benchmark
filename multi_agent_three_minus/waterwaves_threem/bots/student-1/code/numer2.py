#!/usr/bin/env python3
"""Extract & factor N(t)=A_6*(e3m+e3p) on the anchor chamber; compare to wall fns.
Also confirm pure-sumFree denom (minimal denom = (e3m+e3p)^1) on 2 chambers."""
import sys
from fractions import Fraction as F
import sympy as sp
import harness as h, chambers_n6 as cn, inv
SIG=[-1,-1,-1,1,1,1]; t=sp.Symbol('t')
def pr(*a): print(*a, flush=True)
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
def reconstruct(pts,cap=30):
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
def collect(base, vary, fn, npts=90):
    s0=full_sig(cn.solve_squares(base)); pts=[]
    j=0
    while len(pts)<npts and j<400:
        for sgn in (1,-1):
            tt=F(sgn*j,55); free=list(base); free[vary-2]=base[vary-2]+tt
            oms=cn.solve_squares(free)
            if oms is None or any(w==0 for w in oms): continue
            if full_sig(oms)!=s0: continue
            try: im,_,_=h.on_shell(free,SIG)
            except Exception: continue
            pts.append((tt, fn(tt,oms,im)))
        j+=1
    return pts,s0

pr("(A) minimal-denom confirm (A_6*(e3m+e3p) -> pure sumFree denom):")
for base in [[F(2),F(3),F(5),F(7)],[F(-3),F(2),F(4),F(-5)]]:
    for vary in (4,5):
        pts,_=collect(base,vary, lambda tt,oms,im: im*(inv.invariants(oms)[2]+inv.invariants(oms)[3]),80)
        res=reconstruct(pts)
        if res is None: pr(f"  base {base} w{vary}: recon fail ({len(pts)})"); continue
        dN,dD,Nc,Dc=res
        Dpoly=sum(sp.Rational(c.numerator,c.denominator)*t**k for k,c in enumerate(Dc))
        sf0=sum(base); sumF=sp.Rational(sf0.numerator,sf0.denominator)+t
        pure=sp.simplify(Dpoly/sumF**dD)
        pr(f"  base {base} w{vary}: degN={dN} degD={dD} pureSF={bool(pure.is_number and pure!=0)} ({len(pts)}pts)")

pr("\n(B) factor N(t)=A_6*(e3m+e3p) on anchor [2,3,5,7] vary w4:")
base=[F(2),F(3),F(5),F(7)]; vary=4
pts,_=collect(base,vary, lambda tt,oms,im: im*(inv.invariants(oms)[2]+inv.invariants(oms)[3]),100)
res=reconstruct(pts); dN,dD,Nc,Dc=res
Npoly=sum(sp.Rational(c.numerator,c.denominator)*t**j for j,c in enumerate(Nc))
Dpoly=sum(sp.Rational(c.numerator,c.denominator)*t**k for k,c in enumerate(Dc))
sf0=sum(base); sumF=sp.Rational(sf0.numerator,sf0.denominator)+t
# A_6*(e3m+e3p) = Npoly/Dpoly ; Dpoly = const*sumF^dD
Nclean=sp.factor(sp.cancel(Npoly/(Dpoly/sumF**dD)))   # remove the const, keep sumF^dD in numerator
pr(f"  degN={dN} degD={dD}")
pr(f"  N(t)*sumFree^{dD} factored:")
sp.pprint(sp.factor(Npoly))
# wall functions roots
w2,w3,w5=sp.Integer(2),sp.Integer(3),sp.Integer(7); w4=sp.Integer(5)+t
sF=w2+w3+w4+w5; sSig=-w2**2-w3**2+w4**2+w5**2
w6=-(-sF**2+sSig)/(-2*sF); w1=-(sF+w6)
wsq={1:sp.cancel(w1**2),2:w2**2,3:w3**2,4:w4**2,5:w5**2,6:sp.cancel(w6**2)}
roots={}
for i in (1,2,3):
    for j in (4,5,6):
        kij=sp.cancel(wsq[j]-wsq[i]); nn,_=sp.fraction(kij)
        rs=[r for r in sp.solve(nn,t) if r.is_real]
        roots[f"k_{i}{j}"]=rs
pr("  mixed (1=1) wall roots k_ij=w_j^2-w_i^2:")
for k,v in roots.items(): pr(f"    {k}: {v}")
