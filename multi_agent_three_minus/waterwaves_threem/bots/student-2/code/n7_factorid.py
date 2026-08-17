#!/usr/bin/env python3
"""Light: identify reduced-denom factors with slice mixed pairs (capped points);
re-confirm over-clearing=0 on a SECOND n=7 chamber."""
import sympy as sp
from fractions import Fraction as F
import harness as h
t=sp.Symbol('t'); M=(1,2,3); P=(4,5,6,7)
def Qr(x): return sp.Rational(x.numerator,x.denominator)
def msubs():
    import itertools; out=[]
    for r in range(1,7):
        for S in itertools.combinations(range(1,8),r):
            if any(i in M for i in S) and any(i in P for i in S): out.append(S)
    return out
MS=msubs()
def csig(oms):
    w={i+1:oms[i] for i in range(7)}; out=[]
    for S in MS:
        k=sum((-1 if i in M else 1)*w[i]**2 for i in S); out.append(1 if k>0 else(-1 if k<0 else 0))
    return tuple(out)
def collect(fixed,va,vb,ia,ib,step=F(1,24),cap=38):
    SIG=[-1,-1,-1,1,1,1,1]; pts=[]; s0=None
    for d in(1,-1):
        for k in range(0 if d==1 else 1,60):
            if len(pts)>=cap: break
            tv=d*step*k; free=list(fixed); free[ia]=va+tv; free[ib]=vb-tv
            if sum(free)==0: continue
            try: im,oms,rep=h.on_shell([str(x) for x in free],SIG)
            except Exception: break
            if rep!=0: continue
            oms=[F(o) for o in oms]; s=csig(oms)
            if 0 in s: continue
            if s0 is None: s0=s
            if s!=s0: break
            pts.append((tv,F(im),oms))
    return pts
def Dfree(oms):
    w={i+1:Qr(oms[i]) for i in range(7)}; D=sp.Integer(1)
    for i in M:
        for j in P: D*=(w[i]+w[j])
    return D
def analyze(pts,tag):
    xs=[Qr(tv) for(tv,_,_)in pts]
    Nv=[Qr(im)*Dfree(oms) for(_,im,oms)in pts]; Dv=[Dfree(oms) for(_,_,oms)in pts]
    h2=len(pts)*2//3
    Np=sp.Poly(sp.interpolate(list(zip(xs[:h2],Nv[:h2])),t),t)
    Dp=sp.Poly(sp.interpolate(list(zip(xs[:h2],Dv[:h2])),t),t)
    okN=all(Np.eval(xs[i])==Nv[i] for i in range(h2,len(pts)))
    g=sp.gcd(Np,Dp); over=sp.degree(g,t)
    red=sp.Poly(sp.cancel(Dp.as_expr()/g.as_expr()),t)
    print(f"  [{tag}] pts={len(pts)} N_full poly?{okN} over-clearing={over} reduced_deg={red.degree()} Dfree_deg={Dp.degree()}")
    return red
print("=== chamber A: factor identification ===")
ptsA=collect([F(2),F(3),F(5),F(0),F(0)],F(7),F(11),3,4)
redA=analyze(ptsA,"A")
# pair factors
xs=[Qr(tv) for(tv,_,_)in ptsA]; facs={}
for i in M:
    for j in P:
        ys=[Qr(o[i-1])+Qr(o[j-1]) for(_,_,o)in ptsA]
        facs[(i,j)]=sp.Poly(sp.interpolate(list(zip(xs,ys)),t),t)
nonc=[(i,j) for(i,j),p in facs.items() if p.degree()>=1]
rem=redA.monic(); matched=[]
for (i,j) in nonc:
    q,r=sp.div(rem,facs[(i,j)].monic(),t)
    if r==0: matched.append((i,j,facs[(i,j)].degree())); rem=sp.Poly(q,t)
print(f"  nonconstant mixed pairs ({len(nonc)}): {sorted(nonc)}")
print(f"  matched to reduced-denom (i,j,deg): {sorted(matched)}")
print(f"  leftover deg after dividing all matched: {rem.degree()} (0 => exact)")
print(f"  => reduced denom = prod of all {len(nonc)} nonconstant mixed pairs, POWER 1: {rem.degree()==0 and len(matched)==len(nonc)}")
print("=== chamber B: independent over-clearing check ===")
ptsB=collect([F(3,2),F(5),F(2),F(0),F(0)],F(17,3),F(4),3,4)
if len(ptsB)>=26: analyze(ptsB,"B")
else:
    ptsB=collect([F(1),F(4),F(7),F(0),F(0)],F(3),F(13,2),3,4)
    analyze(ptsB,"B'") if len(ptsB)>=26 else print(f"  B fallback pts={len(ptsB)}")
