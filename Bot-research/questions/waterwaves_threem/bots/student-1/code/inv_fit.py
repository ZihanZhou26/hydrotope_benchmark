#!/usr/bin/env python3
"""Fit C_6*(e3m+e3p)^k = N(e1,e2,e3m,e3p) [poly] within one chamber, exact over Q.
Finds the minimal pole order k and the numerator polynomial."""
from fractions import Fraction as F
import sympy as sp
import harness as h
import chambers_n6 as cn
import inv

SIG=[-1,-1,-1,1,1,1]

def full_sig(oms):
    sq=[w*w for w in oms]
    ws=cn.wall_signs(sq)
    if ws is None: return None
    a,b=sq[0:3],sq[3:6]
    if 0 in [a[0]-a[1],a[0]-a[2],a[1]-a[2],b[0]-b[1],b[0]-b[2],b[1]-b[2]]: return None
    sa=tuple(1 if a[i]>a[j] else -1 for i,j in [(0,1),(0,2),(1,2)])
    sb=tuple(1 if b[i]>b[j] else -1 for i,j in [(0,1),(0,2),(1,2)])
    return ws+(sa,sb)

def monos(deg):
    """exponent tuples (a,b,c,d) for e1^a e2^b e3m^c e3p^d, a+2b+3c+3d=deg."""
    out=[]
    for c in range(deg//3+1):
        for d in range(deg//3+1):
            rem=deg-3*(c+d)
            if rem<0: continue
            for b in range(rem//2+1):
                a=rem-2*b
                if a>=0: out.append((a,b,c,d))
    return out

def solve_exact(A,b):
    rows=len(A); cols=len(A[0])
    M=[[F(A[i][j]) for j in range(cols)]+[F(b[i])] for i in range(rows)]
    # Gaussian elimination, return one solution if consistent & determined enough
    piv_cols=[]; r=0
    for col in range(cols):
        piv=next((rr for rr in range(r,rows) if M[rr][col]!=0),None)
        if piv is None: continue
        M[r],M[piv]=M[piv],M[r]; pv=M[r][col]
        M[r]=[x/pv for x in M[r]]
        for rr in range(rows):
            if rr!=r and M[rr][col]!=0:
                f=M[rr][col]; M[rr]=[M[rr][k]-f*M[r][k] for k in range(cols+1)]
        piv_cols.append(col); r+=1
        if r==rows: break
    # check consistency for remaining rows
    for rr in range(r,rows):
        if M[rr][cols]!=0 and all(M[rr][c]==0 for c in range(cols)):
            return None  # inconsistent
    sol=[F(0)]*cols
    for i,col in enumerate(piv_cols):
        sol[col]=M[i][cols]
    return sol, len(piv_cols)

def sample_chamber(base, nmax=400):
    s0=full_sig(cn.solve_squares(base))
    pts=[]
    import random
    rnd=random.Random(12345)
    # sample near base within same chamber
    while len(pts)<nmax:
        free=[base[i]+F(rnd.randint(-40,40),50) for i in range(4)]
        oms=cn.solve_squares(free)
        if oms is None or any(w==0 for w in oms): continue
        if full_sig(oms)!=s0: continue
        e1,e2,e3m,e3p=inv.invariants(oms)
        if e3m+e3p==0: continue
        try: im,_,_=h.on_shell(free,SIG)
        except Exception: continue
        C6=im/32   # A_6/(i 2^5)= im/32 (g=1)
        pts.append((e1,e2,e3m,e3p,C6))
    return pts,s0

if __name__=="__main__":
    base=[F(2),F(3),F(5),F(7)]
    pts,s0=sample_chamber(base, 250)
    print(f"chamber sig={s0}\nsampled {len(pts)} in-chamber points")
    for k in (1,2,3):
        ms=monos(8+3*k)
        nb=len(ms)
        if len(pts)<nb+10:
            print(f"  k={k}: need more pts ({nb} basis)"); continue
        # build system: N(invariants)=C6*(e3m+e3p)^k
        A=[]; rhs=[]
        for (e1,e2,e3m,e3p,C6) in pts[:nb]:
            row=[e1**a*e2**b*e3m**c*e3p**d for (a,b,c,d) in ms]
            A.append(row); rhs.append(C6*(e3m+e3p)**k)
        res=solve_exact(A,rhs)
        if res is None:
            print(f"  k={k}: NO consistent polynomial fit"); continue
        sol,rank=res
        # validate on holdout
        ok=True
        for (e1,e2,e3m,e3p,C6) in pts[nb:]:
            val=sum(sol[i]*(e1**a*e2**b*e3m**c*e3p**d) for i,(a,b,c,d) in enumerate(ms))
            if val!=C6*(e3m+e3p)**k: ok=False; break
        print(f"  k={k}: rank={rank}/{nb}, holdout {'PASS' if ok else 'FAIL'}")
        if ok:
            nz=[(ms[i],sol[i]) for i in range(nb) if sol[i]!=0]
            print(f"        nonzero terms: {len(nz)}")
            break
