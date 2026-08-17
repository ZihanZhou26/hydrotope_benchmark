#!/usr/bin/env python3
"""Verify pole order of A_6 at (e3m+e3p)=0 is exactly 1, across several chambers
and slice directions. Reconstruct A_6(t), factor denominator, identify the
(e3m+e3p) numerator factor and its multiplicity (after removing sumFree artifact)."""
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
def reconstruct(pts,cap=45):
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

def ee_num_on_slice(base, vary):
    """symbolic numerator of (e3m+e3p)(t) along slice base, varying leg `vary` (2..5)."""
    ws=[sp.Integer(base[i].numerator)/sp.Integer(base[i].denominator) for i in range(4)]
    ws[vary-2]=ws[vary-2]+t
    w2,w3,w4,w5=ws
    sF=w2+w3+w4+w5; sSig=-w2**2-w3**2+w4**2+w5**2
    w6=-(-sF**2+sSig)/(-2*sF); w1=-(sF+w6)
    ee=sp.cancel(w1*w2*w3+w4*w5*w6)
    return sp.fraction(ee), sp.cancel(sF)

def run(base, vary):
    s0=full_sig(cn.solve_squares(base)); pts=[]
    for j in range(-70,71):
        tt=F(j,50); free=list(base); free[vary-2]=base[vary-2]+tt
        oms=cn.solve_squares(free)
        if oms is None or any(w==0 for w in oms): continue
        if full_sig(oms)!=s0: continue
        try: im,_,_=h.on_shell(free,SIG)
        except Exception: continue
        pts.append((tt,im))
    res=reconstruct(pts)
    if res is None: return None
    dN,dD,Nc,Dc=res
    Dpoly=sp.Poly(sum(sp.Rational(c.numerator,c.denominator)*t**k for k,c in enumerate(Dc)),t)
    (ee_n,ee_d),sF=ee_num_on_slice(base,vary)
    ee_np=sp.Poly(ee_n,t)
    # remove sumFree^? from Dpoly, then test ee_num multiplicity
    mult=0; D=Dpoly
    while True:
        q,r=sp.div(D, ee_np)
        if r==0: mult+=1; D=q
        else: break
    return dN,dD,sp.factor(Dpoly.as_expr()),sp.factor(ee_n),mult,len(pts)

if __name__=="__main__":
    chambers,*_=cn.scan(300000, seed=11)
    items=sorted(chambers.items(), key=lambda kv:-kv[1][0])[:6]
    print("Pole-order test: multiplicity of (e3m+e3p) numerator in reduced A_6(t) denom\n")
    for idx,(sig,(cnt,free,sq)) in enumerate(items):
        base=[F(x) for x in free]
        for vary in (4,5,2):
            r=run(base,vary)
            if r is None: print(f"  T{idx} vary w{vary}: reconstruct failed"); continue
            dN,dD,Df,eef,mult,npts=r
            print(f"  T{idx} vary w{vary}: degN={dN} degD={dD}  (e3m+e3p)-multiplicity={mult}  [npts={npts}]")
