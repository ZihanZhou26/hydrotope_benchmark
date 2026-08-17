#!/usr/bin/env python3
"""Round-5 shared lib: F-CONSTANT slices (vary w4=a+t, w5=b-t so sumFree fixed ->
   w1,w6 polynomial in t -> N(t) polynomial), exact reconstruction, jump coeffs.
   N := A_6/i * (e3m+e3p)/32   (g=1).  A_6 = i 32 N/(e3m+e3p).
"""
from fractions import Fraction as F
import sympy as sp
import harness as h, chambers_n6 as cn, inv
SIG=[-1,-1,-1,1,1,1]; t=sp.Symbol('t')

def full_sig(oms):
    """signature = (W1 signs, W2 signs, same-type orderings). None if on any wall/tie."""
    sq=[w*w for w in oms]; ws=cn.wall_signs(sq)
    if ws is None: return None
    a,b=sq[0:3],sq[3:6]
    if 0 in [a[0]-a[1],a[0]-a[2],a[1]-a[2],b[0]-b[1],b[0]-b[2],b[1]-b[2]]: return None
    sa=tuple(1 if a[i]>a[j] else -1 for i,j in [(0,1),(0,2),(1,2)])
    sb=tuple(1 if b[i]>b[j] else -1 for i,j in [(0,1),(0,2),(1,2)])
    return ws+(sa,sb)

def Nval(oms,im):
    e=inv.invariants(oms); return F(im*(e[2]+e[3]),32)

def fc_free(w2,w3,a,b,tt):
    """F-const slice: free=(w2,w3, a+tt, b-tt). sumFree=w2+w3+a+b fixed."""
    return [F(w2),F(w3),F(a)+tt,F(b)-tt]

def fc_point(w2,w3,a,b,tt):
    free=fc_free(w2,w3,a,b,tt)
    oms=cn.solve_squares(free)
    return free,oms

def solve_exact(A,bb):
    n=len(A); M=[[F(A[i][j]) for j in range(n)]+[F(bb[i])] for i in range(n)]
    for col in range(n):
        piv=next((r for r in range(col,n) if M[r][col]!=0),None)
        if piv is None: return None
        M[col],M[piv]=M[piv],M[col]; pv=M[col][col]; M[col]=[x/pv for x in M[col]]
        for r in range(n):
            if r!=col and M[r][col]!=0:
                f=M[r][col]; M[r]=[M[r][k]-f*M[col][k] for k in range(n+1)]
    return [M[i][n] for i in range(n)]

def fit_poly(pts, dmax=20):
    """pts=[(tt,val)] -> coeffs (low->high) in ORIGINAL var tt if val is a polynomial
    of deg<=dmax, else None. Fits in SHIFTED s=tt-t0 (small numbers, fast), then unshifts."""
    if not pts: return None
    t0=pts[0][0]
    sp_pts=[(x-t0, v) for (x,v) in pts]
    sol_s=None
    for d in range(0,dmax+1):
        if len(sp_pts)<d+1+3: continue
        rows=[[s**j for j in range(d+1)] for (s,_) in sp_pts[:d+1]]
        rhs=[v for (_,v) in sp_pts[:d+1]]
        sol=solve_exact(rows,rhs)
        if sol is None: continue
        if all(sum(c*s**j for j,c in enumerate(sol))==v for (s,v) in sp_pts[d+1:]):
            sol_s=sol; break
    if sol_s is None: return None
    tt=sp.Symbol('tt')
    expr=sp.expand(sum(sp.Rational(c.numerator,c.denominator)*(tt-sp.Rational(t0.numerator,t0.denominator))**j for j,c in enumerate(sol_s)))
    Pp=sp.Poly(expr,tt); deg=Pp.degree()
    co=[F(0)]*(deg+1)
    for (m,c) in Pp.terms(): co[m[0]]=F(int(sp.Rational(c).p),int(sp.Rational(c).q))
    return co

def poly(coeffs): return sum(sp.Rational(c.numerator,c.denominator)*t**j for j,c in enumerate(coeffs))

def collect_fc_side(w2,w3,a,b, t0, direction, step, maxn, ref_sig):
    """Collect contiguous in-chamber F-const points on one side of t0."""
    pts=[]
    for k in range(1,maxn+1):
        tt=t0+direction*step*k
        free=fc_free(w2,w3,a,b,tt)
        oms=cn.solve_squares(free)
        if oms is None or any(w==0 for w in oms): break
        if full_sig(oms)!=ref_sig: break
        try: im,_,_=h.on_shell(free,SIG)
        except Exception: break
        pts.append((tt, Nval(oms,im)))
    return pts
