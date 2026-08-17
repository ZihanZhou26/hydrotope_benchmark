#!/usr/bin/env python3
"""Exact-rational fit utilities: given (point, value) data and a monomial basis,
find rank/pivots modularly, then solve the square pivot-system exactly for the
unique pivot-solution (free monomials = 0)."""
from fractions import Fraction as F
PR=2**61-1
def minv(a): return pow(a%PR,PR-2,PR)
def fm(fr): return (fr.numerator%PR)*minv(fr.denominator%PR)%PR
def mod_pivots(rows,rhs,ncol):
    nrow=len(rows); Mx=[[fm(x) for x in rows[i]]+[fm(rhs[i])] for i in range(nrow)]; piv=[]; r=0
    for c in range(ncol):
        p=next((i for i in range(r,nrow) if Mx[i][c]!=0),None)
        if p is None: continue
        Mx[r],Mx[p]=Mx[p],Mx[r]; iv=minv(Mx[r][c]); Mx[r]=[(x*iv)%PR for x in Mx[r]]
        for i in range(nrow):
            if i!=r and Mx[i][c]!=0:
                f=Mx[i][c]; Mx[i]=[(Mx[i][k]-f*Mx[r][k])%PR for k in range(ncol+1)]
        piv.append(c); r+=1
    return piv
def exact_solve_square(rows,rhs):
    """exact rational solve of square system (len(rows)=len(cols)); rows are Fractions."""
    n=len(rows); Mx=[[F(rows[i][j]) for j in range(n)]+[F(rhs[i])] for i in range(n)]
    for c in range(n):
        p=next((i for i in range(c,n) if Mx[i][c]!=0),None)
        if p is None: return None
        Mx[c],Mx[p]=Mx[p],Mx[c]; pv=Mx[c][c]; Mx[c]=[x/pv for x in Mx[c]]
        for i in range(n):
            if i!=c and Mx[i][c]!=0:
                f=Mx[i][c]; Mx[i]=[Mx[i][k]-f*Mx[c][k] for k in range(n+1)]
    return [Mx[i][n] for i in range(n)]
def fit_exact(data, mons, evalf):
    """data=[(point,val)], mons=basis, evalf(mon,point)->Fraction. Returns dict pivot->coef (exact)."""
    rows=[[evalf(m,o) for m in mons] for (o,_) in data]
    rhs=[v for (_,v) in data]
    piv=mod_pivots(rows,rhs,len(mons))
    # exact solve using pivot columns and the first len(piv) independent rows
    # choose rows that are independent (use first rows giving full rank on pivot cols)
    sub_rows=[]; sub_rhs=[]; used=0
    # greedily pick rows until we have len(piv) independent (mod PR) on pivot cols
    chosen=[]
    Mx=[]; 
    import itertools
    # pick rows by modular independence on pivot columns
    basis_mod=[]
    for idx,(o,v) in enumerate(data):
        r=[fm(rows[idx][c]) for c in piv]
        # reduce against basis_mod
        rr=r[:]; 
        for (bp,brow) in basis_mod:
            if rr[bp]!=0:
                f=rr[bp]; rr=[(rr[k]-f*brow[k])%PR for k in range(len(piv))]
        nz=next((k for k in range(len(piv)) if rr[k]!=0),None)
        if nz is not None:
            iv=minv(rr[nz]); rr=[(x*iv)%PR for x in rr]
            basis_mod.append((nz,rr)); chosen.append(idx)
        if len(chosen)==len(piv): break
    sub=[[rows[idx][c] for c in piv] for idx in chosen]
    subrhs=[rhs[idx] for idx in chosen]
    sol=exact_solve_square(sub,subrhs)
    return dict(zip(piv,sol)) if sol else None
