#!/usr/bin/env python3
"""Measure single-wall JUMP EXPONENTS at n=7, testing the unified exponent law:
  (1=1) wall a_i=b_j  ->  exponent 1   (anomalous, |k_ij| difference branch)
  every OTHER mixed subset-sum wall  ->  exponent n-3 = 4.
NEW walls available only at n>=7: (1=3) a_i=b_j+b_k+b_l ; (2=2) a_i+a_k=b_j+b_l.

Method: F-const slice (vary two plus legs oppositely, sumFree const => legs 1,7
polynomial). Walk t; detect a CLEAN single-wall crossing (exactly ONE mixed-subset
sign flips). Reconstruct N(t)=A_7*Dfree as a polynomial on EACH side; the jump
J(t)=N_+(t)-N_-(t) vanishes at t0 to order = the exponent. Report order."""
import sympy as sp, itertools
from fractions import Fraction as F
import harness as h
t=sp.Symbol('t')
def Qr(x): return sp.Rational(x.numerator,x.denominator)
M=(1,2,3); P=(4,5,6,7); n=7; SIG=[-1,-1,-1,1,1,1,1]

def msubs():
    out=[]
    for r in range(1,n):
        for S in itertools.combinations(range(1,n+1),r):
            if any(i in M for i in S) and any(i in P for i in S): out.append(S)
    return out
MS=msubs()

def csig(oms):
    w={i+1:oms[i] for i in range(n)}
    return tuple(1 if sum((-1 if i in M else 1)*w[i]**2 for i in S)>0 else
                 (-1 if sum((-1 if i in M else 1)*w[i]**2 for i in S)<0 else 0) for S in MS)

def Dfree(oms):
    w={i+1:Qr(oms[i]) for i in range(n)}
    D=sp.Integer(1)
    for i in M:
        for j in P: D*=(w[i]+w[j])
    return D

def walk(fixed,va,vb,ia,ib,step=F(1,60),maxk=120):
    """fixed: 5 free-leg template; vary free[ia]=va+t, free[ib]=vb-t. Return list of
    (t, im, oms, sig)."""
    pts=[]
    for k in range(-maxk,maxk+1):
        tv=step*k
        free=list(fixed); free[ia]=va+tv; free[ib]=vb-tv
        if sum(free)==0: continue
        try: im,oms,rep=h.on_shell([str(x) for x in free],SIG)
        except Exception: continue
        if rep!=0: continue
        oms=[F(o) for o in oms]; s=csig(oms)
        if 0 in s: continue
        pts.append((tv,F(im),oms,s))
    return pts

def measure_exponents(fixed,va,vb,ia,ib,label):
    print(f"\n=== {label} ===")
    pts=walk(fixed,va,vb,ia,ib)
    # find clean single-wall crossings: adjacent in-chamber runs differing in exactly 1 sign
    # group into maximal constant-sig runs
    runs=[]; cur=[pts[0]]
    for p in pts[1:]:
        if p[3]==cur[-1][3]: cur.append(p)
        else: runs.append(cur); cur=[p]
    runs.append(cur)
    for a,b in zip(runs,runs[1:]):
        sa,sb=a[-1][3],b[0][3]
        diff=[idx for idx in range(len(MS)) if sa[idx]!=sb[idx]]
        if len(diff)!=1: continue
        if len(a)<30 or len(b)<30: continue
        S=MS[diff[0]]
        nm=sum(1 for i in S if i in M); npp=len(S)-nm
        # reconstruct N on each side as poly in t
        def recon(run):
            xs=[Qr(tv) for tv,_,_,_ in run]
            Nv=[Qr(im)*Dfree(oms) for _,im,oms,_ in run]
            half=len(run)*2//3
            Np=sp.Poly(sp.interpolate(list(zip(xs[:half],Nv[:half])),t),t)
            ok=all(Np.eval(xs[i])==Nv[i] for i in range(half,len(run)))
            return Np,ok
        Na,oka=recon(a); Nb,okb=recon(b)
        if not(oka and okb): continue
        # wall function k_S(t)
        OM={leg:sp.Poly(sp.interpolate(list(zip([Qr(tv) for tv,_,_,_ in a+b],
            [Qr(o[leg-1]) for _,_,o,_ in a+b])),t),t) for leg in range(1,8)}
        kS=sum((-1 if i in M else 1)*OM[i].as_expr()**2 for i in S)
        kSp=sp.Poly(sp.expand(kS),t)
        # t0 = root of kS in the crossing interval
        roots=[r for r in sp.roots(kSp,t,multiple=True)]
        # jump
        J=sp.Poly(Na.as_expr()-Nb.as_expr(),t)
        if J.as_expr()==0:
            print(f"  wall S={S} ({nm}={npp}): jump identically 0 (smooth)"); continue
        # find real root of kS nearest the run boundary
        tb=(a[-1][0]+b[0][0])/2
        cand=[r for r in roots if r.is_real]
        if not cand: continue
        t0=min(cand,key=lambda r: abs(float(r)-float(tb)))
        # order of vanishing of J at t0
        order=0; Jc=J
        while sp.Poly(Jc,t).eval(sp.Rational(t0))==0 and order<12:
            Jc=sp.Poly(sp.div(Jc.as_expr(),(t-t0))[0],t); order+=1
        print(f"  wall S={S}  ({nm} minus = {npp} plus)  t0={t0}: JUMP EXPONENT = {order}")

if __name__=="__main__":
    # several slices to hit different wall types; vary plus legs 5,6 (idx 3,4) oppositely
    measure_exponents([F(2),F(3),F(5),F(7),F(11)],F(7),F(11),3,4,"slice A (vary w5,w6)")
    measure_exponents([F(2),F(3),F(5),F(7),F(11)],F(5),F(7),2,3,"slice B (vary w4,w5)")
    measure_exponents([F(3),F(4),F(6),F(9),F(13)],F(9),F(13),3,4,"slice C (vary w5,w6)")
    measure_exponents([F(2),F(5),F(6),F(8),F(15)],F(8),F(15),3,4,"slice D (vary w5,w6)")
