#!/usr/bin/env python3
"""PIN the n=7 MINIMAL denominator (deliverable r6-student-2 #4) -- FAST gcd method.

Method (per chamber, F-const slice, EXACT):
  N_full(t) = A_n(t)/i * D_free(t),  D_free = prod_{i in M,j in P}(w_i+w_j).
  (A) verify N_full(t) is a POLYNOMIAL (Lagrange + held-out)  -> D_free clears A_n.
  (B) reduced denominator of A_n on the slice = D_free / gcd(N_full, D_free).
      over-clearing := deg gcd(N_full, D_free).
CONTROL n=6: D_9=(e3m+e3p)^3 collapses -> minimal=(e3m+e3p)^1, so over-clearing
  = 2*deg((e3m+e3p) on slice)  (the method must DETECT this collapse).
TARGET n=7: predict NO collapse -> over-clearing = 0, reduced denom == D_free (deg 12).
"""
import sympy as sp
from fractions import Fraction as F
import itertools, harness as h
t = sp.Symbol('t')
def Qr(x): return sp.Rational(x.numerator, x.denominator)

def msubs_of(n,M,P):
    out=[]
    for r in range(1,n):
        for S in itertools.combinations(range(1,n+1),r):
            if any(i in M for i in S) and any(i in P for i in S): out.append(S)
    return out

def csig(oms,n,M,msubs):
    w={i+1:oms[i] for i in range(n)}
    out=[]
    for S in msubs:
        kk=sum((-1 if i in M else 1)*w[i]**2 for i in S)
        out.append(1 if kk>0 else (-1 if kk<0 else 0))
    return tuple(out)

def collect(n,M,P,fixed,va,vb,ia,ib,step=F(1,30),maxk=45):
    SIG=[-1 if (i+1) in M else 1 for i in range(n)]
    ms=msubs_of(n,M,P); pts=[]; s0=None
    for d in (1,-1):
        for k in range(0 if d==1 else 1,maxk):
            tv=d*step*k; free=list(fixed); free[ia]=va+tv; free[ib]=vb-tv
            if sum(free)==0: continue
            try: im,oms,rep=h.on_shell([str(x) for x in free],SIG)
            except Exception: break
            if rep!=0: continue
            oms=[F(o) for o in oms]; s=csig(oms,n,M,ms)
            if 0 in s: continue
            if s0 is None: s0=s
            if s!=s0: break
            pts.append((tv,F(im),oms))
    return pts

def Dfree_val(oms,M,P):
    w={i+1:Qr(oms[i]) for i in range(len(oms))}
    D=sp.Integer(1)
    for i in M:
        for j in P: D*=(w[i]+w[j])
    return D

def analyze(n,M,P,fixed,va,vb,ia,ib,label):
    print(f"\n===== {label} (n={n}) =====")
    pts=collect(n,M,P,fixed,va,vb,ia,ib)
    print(f"  in-chamber exact points: {len(pts)}")
    if len(pts)<25: print("  too few"); return
    xs=[Qr(tv) for (tv,_,_) in pts]
    Nv=[Qr(im)*Dfree_val(oms,M,P) for (_,im,oms) in pts]
    Dv=[Dfree_val(oms,M,P) for (_,_,oms) in pts]
    half=len(pts)*2//3
    Npoly=sp.Poly(sp.interpolate(list(zip(xs[:half],Nv[:half])),t),t)
    okN=all(Npoly.eval(xs[i])==Nv[i] for i in range(half,len(pts)))
    Dpoly=sp.Poly(sp.interpolate(list(zip(xs[:half],Dv[:half])),t),t)
    okD=all(Dpoly.eval(xs[i])==Dv[i] for i in range(half,len(pts)))
    print(f"  (A) N_full=A*D_free polynomial? {okN} (deg {Npoly.degree()});  D_free poly? {okD} (deg {Dpoly.degree()})")
    if not(okN and okD): print("  FAIL polynomial check"); return
    g=sp.gcd(Npoly,Dpoly)
    over=sp.degree(g,t)
    red_deg=Dpoly.degree()-over
    print(f"  (B) over-clearing deg gcd(N_full,D_free) = {over}")
    print(f"      => reduced denom degree on slice = {red_deg}  (D_free slice deg {Dpoly.degree()})")
    print(f"      reduced denom factored = {sp.factor(Dpoly.as_expr()/g.as_expr())}")
    return red_deg, Dpoly.degree(), over

if __name__=="__main__":
    analyze(6,(1,2,3),(4,5,6),[F(3),F(5,2),F(0),F(0)],F(53,10),F(7),2,3,
            "CONTROL n=6 (collapse known: over-clearing = 2*deg(e3m+e3p))")
    analyze(7,(1,2,3),(4,5,6,7),[F(2),F(3),F(5),F(0),F(0)],F(7),F(11),3,4,
            "TARGET n=7 (predict NO collapse: over-clearing = 0)")
