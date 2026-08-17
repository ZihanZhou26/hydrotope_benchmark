#!/usr/bin/env python3
"""Confirm the n=7 minimal denominator: (1) identify reduced-denom factors with the
nine non-constant slice mixed pairs; (2) re-run a SECOND chamber; (3) exhibit a
manifold point where ONE mixed pair vanishes alone (the geometric reason there is
no n=6-style collapse at n=7)."""
import sympy as sp
from fractions import Fraction as F
import itertools, harness as h
from n7_mindenom import collect, Dfree_val, Qr
t=sp.Symbol('t')
M=(1,2,3); P=(4,5,6,7)

def slice_pairfactors(pts):
    """Interpolate each (w_i+w_j)(t); return dict (i,j)->sympy poly (nonconstant only)."""
    xs=[Qr(tv) for (tv,_,_) in pts]
    facs={}
    for i in M:
        for j in P:
            ys=[Qr(oms[i-1])+Qr(oms[j-1]) for (_,_,oms) in pts]
            poly=sp.Poly(sp.interpolate(list(zip(xs,ys)),t),t)
            facs[(i,j)]=poly
    return facs

def reduced_denom_poly(pts):
    xs=[Qr(tv) for (tv,_,_) in pts]
    Nv=[Qr(im)*Dfree_val(oms,M,P) for (_,im,oms) in pts]
    Dv=[Dfree_val(oms,M,P) for (_,_,oms) in pts]
    h2=len(pts)*2//3
    Np=sp.Poly(sp.interpolate(list(zip(xs[:h2],Nv[:h2])),t),t)
    Dp=sp.Poly(sp.interpolate(list(zip(xs[:h2],Dv[:h2])),t),t)
    g=sp.gcd(Np,Dp)
    red=sp.Poly(sp.simplify(Dp.as_expr()/g.as_expr()),t)
    return red, sp.degree(g,t), Dp

print("=== n=7 chamber A: identify reduced-denom factors with mixed pairs ===")
ptsA=collect(7,M,P,[F(2),F(3),F(5),F(0),F(0)],F(7),F(11),3,4)
print(f"  points: {len(ptsA)}")
red,over,Dp=reduced_denom_poly(ptsA)
facs=slice_pairfactors(ptsA)
red_monic=red.monic()
# divide out each nonconstant pair factor
rem=red_monic
matched=[]
for (i,j),poly in facs.items():
    if poly.degree()>=1:
        q,r=sp.div(rem,poly.monic(),t)
        if r==0:
            matched.append((i,j,poly.degree())); rem=sp.Poly(q,t)
nonconst=[(i,j) for (i,j),pp in facs.items() if pp.degree()>=1]
const=[(i,j) for (i,j),pp in facs.items() if pp.degree()==0]
print(f"  over-clearing={over}; reduced denom deg={red.degree()}")
print(f"  nonconstant slice mixed pairs ({len(nonconst)}): {nonconst}")
print(f"  constant slice mixed pairs    ({len(const)}): {const}")
print(f"  reduced-denom factors matched to mixed pairs: {matched}")
print(f"  leftover after dividing all matched pairs (should be constant): deg={rem.degree()}")
print(f"  => reduced denom == prod of the {len(matched)} nonconstant mixed pairs, each POWER 1: {rem.degree()==0 and len(matched)==len(nonconst)}")

print("\n=== n=7 chamber B (different reference point): over-clearing must be 0 ===")
ptsB=collect(7,M,P,[F(3,2),F(5),F(2),F(0),F(0)],F(17,3),F(4),3,4)
if len(ptsB)>=25:
    redB,overB,DpB=reduced_denom_poly(ptsB)
    print(f"  points: {len(ptsB)}; over-clearing={overB}; reduced denom deg={redB.degree()} (D_free slice deg {DpB.degree()})")
    print(f"  NO collapse (over-clearing==0): {overB==0}")
else:
    print(f"  only {len(ptsB)} pts; trying another reference")

print("\n=== Geometric reason: a SINGLE mixed pair vanishes ALONE at n=7 ===")
print("  (At n=6 one pair forces a full matching -> all 9 sum-walls coincide on {e3m+e3p=0}.)")
# Build a manifold point with w1+w4=0 and NO other pair zero.
# w1=-w4; remaining 2 minus + 3 plus satisfy sum=0 and sum_+^2 = sum_-^2.
# choose w4=5(=>w1=-5), w2=3,w3=8 (minus). need w5+w6+w7=-11, w5^2+w6^2+w7^2=9+64=73.
import sympy as sp
w4=sp.Integer(5); w1=-w4; w2=sp.Integer(3); w3=sp.Integer(8)
S1=-(w2+w3); S2=w2**2+w3**2  # target sum and sumsq for plus trio
# parametrize w5=s; w6,w7 roots of z^2+(S1-s)... wait w5+w6+w7=-(w2+w3)=-11
# Let plus trio sum = -(w2+w3) = -11, sumsq = w2^2+w3^2 = 73
s=sp.symbols('s')
# pick w5 = -2 ; then w6+w7 = -9, w6^2+w7^2 = 73-4=69 -> w6w7=((-9)^2-69)/2=(81-69)/2=6
w5=sp.Integer(-2); su=sp.Integer(-9); pr=sp.Integer(6)
disc=su**2-4*pr
w6=(su+sp.sqrt(disc))/2 if disc>=0 else None
w7=(su-sp.sqrt(disc))/2
w6=sp.nsimplify(w6); w7=sp.nsimplify(w7)
oms=[w1,w2,w3,w4,w5,w6,w7]
sumc=sum(oms); sig=sum((-1 if k<3 else 1)*oms[k]**2 for k in range(7))
print(f"  point omega = {[sp.nsimplify(o) for o in oms]}")
print(f"  conservation: sum omega = {sp.simplify(sumc)}, sum sigma omega^2 = {sp.simplify(sig)}")
pairs0=[(i,j) for i in M for j in P if sp.simplify(oms[i-1]+oms[j-1])==0]
print(f"  mixed pairs that vanish: {pairs0}  (exactly one => walls are DISTINCT, no collapse)")
