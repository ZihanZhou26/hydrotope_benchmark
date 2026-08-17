#!/usr/bin/env python3
"""Determine the pole order k of C_6 = A_6/(i 2^5 g^-3) at (e3m+e3p)=0,
by exact rational reconstruction along a 1-parameter chamber-interior family.

Also count invariant-monomial basis sizes for the numerator fit.
"""
from fractions import Fraction as F
import sympy as sp
import harness as h
import chambers_n6 as cn
import inv

SIG = [-1,-1,-1,1,1,1]

def full_sig(oms):
    sq = [w*w for w in oms]
    ws = cn.wall_signs(sq)
    if ws is None: return None
    a,b = sq[0:3], sq[3:6]
    if 0 in [a[0]-a[1],a[0]-a[2],a[1]-a[2],b[0]-b[1],b[0]-b[2],b[1]-b[2]]:
        return None
    sa = tuple(1 if a[i]>a[j] else -1 for i,j in [(0,1),(0,2),(1,2)])
    sb = tuple(1 if b[i]>b[j] else -1 for i,j in [(0,1),(0,2),(1,2)])
    return ws + (sa,sb)

# monomial counts
def count_monos(deg):
    cnt=0
    for c in range(deg//3+1):
        for d in range(deg//3+1):
            rem = deg-3*(c+d)
            if rem<0: continue
            for b in range(rem//2+1):
                a = rem-2*b
                if a>=0: cnt+=1
    return cnt

for k in (1,2,3):
    print(f"k={k}: numerator deg {8+3*k}, # invariant monomials = {count_monos(8+3*k)}")

# Reconstruct C_6 * (e3m+e3p)^? along a slice; see what power makes it finite.
# pick a chamber-interior base; vary w4 = a+t in a single chamber.
base = [F(2),F(3),F(5),F(7)]   # free w2,w3,w4,w5
s0 = full_sig(cn.solve_squares(base))
pts=[]
for j in range(-60,61):
    tt=F(j,40)
    free=[base[0],base[1],base[2]+tt,base[3]]
    oms=cn.solve_squares(free)
    if oms is None or any(w==0 for w in oms): continue
    if full_sig(oms)!=s0: continue
    e1,e2,e3m,e3p = inv.invariants(oms)
    denom = e3m+e3p
    if denom==0: continue
    try:
        im,_,_=h.on_shell(free,SIG)
    except Exception: continue
    pts.append((tt, im, denom))
print(f"\nin-chamber pts: {len(pts)}")

# C_6 = A_6/i  (im IS the A_6/i value already, since on_shell returns im coeff)
# Actually im = A_6/i. C_6 = A_6/(i 2^5 g^-3) = im / 32  (g=1).
# Reconstruct im as rational function of t and inspect pole at denom(t)=0.
# Simpler: test polynomiality of im*denom^k in t.
t=sp.Symbol('t')
def is_poly_in_t(xy, cap=30):
    # xy: list of (t_value(Fraction), value(Fraction)); fit polynomial exactly
    import functools
    n=len(xy)
    for deg in range(0,cap):
        if n < deg+1+3: continue
        # Vandermonde solve on first deg+1 pts, check rest
        A=[[xy[i][0]**j for j in range(deg+1)] for i in range(deg+1)]
        bvec=[xy[i][1] for i in range(deg+1)]
        sol = solve_exact(A,bvec)
        if sol is None: continue
        ok=all(sum(sol[j]*x**j for j in range(deg+1))==y for (x,y) in xy[deg+1:])
        if ok: return deg
    return None

def solve_exact(A,b):
    n=len(A); M=[[F(A[i][j]) for j in range(n)]+[F(b[i])] for i in range(n)]
    for col in range(n):
        piv=next((r for r in range(col,n) if M[r][col]!=0),None)
        if piv is None: return None
        M[col],M[piv]=M[piv],M[col]; pv=M[col][col]
        M[col]=[x/pv for x in M[col]]
        for r in range(n):
            if r!=col and M[r][col]!=0:
                f=M[r][col]; M[r]=[M[r][kk]-f*M[col][kk] for kk in range(n+1)]
    return [M[i][n] for i in range(n)]

for k in (0,1,2,3):
    xy=[(tt, im*denom**k) for (tt,im,denom) in pts]
    deg=is_poly_in_t(xy)
    print(f"  im*(e3m+e3p)^{k} polynomial in t?  deg = {deg}")
