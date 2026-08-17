#!/usr/bin/env python3
"""Determine the TRUE pole order k of A_6 at (e3m+e3p)=0, via exact oracle
reconstruction on a chamber-interior slice (vary w4=a+t). Factor the reduced
denominator of A_6(t) and read off the multiplicity of the (e3m+e3p)(t) factor.
"""
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

# slice
base=[F(2),F(3),F(5),F(7)]; s0=full_sig(cn.solve_squares(base))
pts=[]; ee_t=None
for j in range(-70,71):
    tt=F(j,50)
    free=[base[0],base[1],base[2]+tt,base[3]]
    oms=cn.solve_squares(free)
    if oms is None or any(w==0 for w in oms): continue
    if full_sig(oms)!=s0: continue
    e1,e2,e3m,e3p=inv.invariants(oms)
    try: im,_,_=h.on_shell(free,SIG)
    except Exception: continue
    pts.append((tt,im))
print(f"in-chamber pts: {len(pts)}")
res=reconstruct(pts,cap=40)
if res is None:
    print("reconstruct A_6(t) failed"); raise SystemExit
dN,dD,Nc,Dc=res
print(f"A_6(t) = N/D: deg N={dN}, deg D={dD}")
Dpoly=sum(sp.Rational(c.numerator,c.denominator)*t**k for k,c in enumerate(Dc))
Npoly=sum(sp.Rational(c.numerator,c.denominator)*t**j for j,c in enumerate(Nc))
print("D(t) factored:"); sp.pprint(sp.factor(Dpoly))
# sumFree(t) and (e3m+e3p)(t) numerators:
sf0=sum(base); sumF_t=sp.Rational(sf0.numerator,sf0.denominator)+t
# (e3m+e3p)(t): compute symbolically via solve on the slice
w2,w3,w5=sp.Integer(2),sp.Integer(3),sp.Integer(7); w4=sp.Integer(5)+t
sF=w2+w3+w4+w5; sSig=-w2**2-w3**2+w4**2+w5**2
w6=-(-sF**2+sSig)/(-2*sF); w1=-(sF+w6)
e3m_t=sp.cancel(w1*w2*w3); e3p_t=sp.cancel(w4*w5*w6)
ee_t=sp.cancel(e3m_t+e3p_t)
print("\n(e3m+e3p)(t) =", ee_t)
ee_num,ee_den=sp.fraction(ee_t)
print("numerator factored:", sp.factor(ee_num))
# multiplicity of ee_num factors in Dpoly
print("\nDpoly / ee_num^k tests:")
for k in (1,2,3,4):
    q,r=sp.div(sp.Poly(Dpoly,t), sp.Poly(ee_num,t)**k)
    print(f"  Dpoly divisible by ee_num^{k}? {r==0}")
