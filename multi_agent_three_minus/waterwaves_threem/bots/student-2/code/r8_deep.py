#!/usr/bin/env python3
"""C_6 per-chamber rational function on an F-CONST slice (legs polynomial in t).
Vary w4=A+t, w5=B-t (sum fixed). C_6 = N_ref(t)/(e3m+e3p)(t), both polynomial.
Factor to expose structure across several chambers."""
import sympy as sp, itertools
from fractions import Fraction as F
import r8bg

t=sp.Symbol('t')
def Q(x): return sp.Rational(F(x).numerator,F(x).denominator)
def e3m(o): return o[0]*o[1]*o[2]
def e3p(o): return o[3]*o[4]*o[5]

def chamber_sig(oms):
    M=[0,1,2];P=[3,4,5];sq=[w*w for w in oms];s=[]
    for i in M:
        for r in range(1,4):
            for T in itertools.combinations(P,r):
                v=sum(sq[j] for j in T)-sq[i]
                if v==0: return None
                s.append(1 if v>0 else -1)
    for i,j in itertools.combinations(range(6),2):
        if sq[i]==sq[j] and ((i<3)==(j<3)): return None
    return tuple(s)

def recon(base, A, B, t_lo, t_hi, npts=40):
    """base=[w2,w3,_,_]; w4=A+t, w5=B-t. Reconstruct C_6=N/D per chamber."""
    frees=[];tvs=[]
    for k in range(npts+1):
        tv=t_lo+(t_hi-t_lo)*F(k,npts)
        fr=[base[0],base[1],A+tv,B-tv]
        if sum(F(x) for x in fr)==0: continue
        frees.append(fr);tvs.append(tv)
    ims=r8bg.batch(frees,6)
    by={}
    for tv,fr,im in zip(tvs,frees,ims):
        if im is None: continue
        oms=r8bg.solve_legs(fr,6); s=chamber_sig(oms)
        if s is None: continue
        by.setdefault(s,[]).append((tv,F(im,2**5),oms))
    out=[]
    for s,pts in by.items():
        if len(pts)<16: continue
        xs=[Q(p[0]) for p in pts]
        Nv=[Q(p[1]*(e3m(p[2])+e3p(p[2]))) for p in pts]
        Dv=[Q(e3m(p[2])+e3p(p[2])) for p in pts]
        Np=sp.Poly(sp.interpolate(list(zip(xs[:14],Nv[:14])),t),t)
        if not all(Np.eval(xs[i])==Nv[i] for i in range(14,len(pts))): continue
        Dp=sp.Poly(sp.interpolate(list(zip(xs[:6],Dv[:6])),t),t)
        out.append((s,pts[0][2],sp.factor(Np.as_expr()),sp.factor(Dp.as_expr()),len(pts)))
    return out

if __name__=="__main__":
    print("C_6 = N_ref(t)/(e3m+e3p)(t) on F-const slices (w4=A+t,w5=B-t).")
    print("Looking at numerator factorization per chamber.\n")
    for base,A,B,lo,hi in [([F(2),F(3),0,0],F(5),F(7),F(-9,2),F(9,2)),
                            ([F(2),F(3),0,0],F(4),F(6),F(-7,2),F(7,2))]:
        print(f"=== base w2,w3={base[0]},{base[1]}; w4={A}+t, w5={B}-t ===")
        for s,om0,N,D,npts in recon(base,A,B,lo,hi):
            print(f"  chamber {s[:6]}... ({npts}pts) om0={[str(x) for x in om0]}")
            print(f"    N_ref(t) = {N}")
            print(f"    D(t)=e3m+e3p = {D}")
