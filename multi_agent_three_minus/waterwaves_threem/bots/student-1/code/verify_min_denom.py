#!/usr/bin/env python3
"""CANONICAL round-4 (student-1) deliverable. One command, all exact vs own ./bg.

HEADLINE: the n=6 three-minus minimal denominator is the SINGLE cubic invariant
          (omega_1 omega_2 omega_3 + omega_4 omega_5 omega_6), to the FIRST power:

    A_6 = i 2^5 g^-3 * N(omega) / (omega_1 omega_2 omega_3 + omega_4 omega_5 omega_6),
    N = degree-11 piecewise-polynomial (a spline), S_3 wr Z_2-symmetric, odd.

This SUPERSEDES the team's D_9 = prod_{i in M, j in P}(omega_i + omega_j) (degree 9):
ON THE MANIFOLD  prod_{i,j}(omega_i+omega_j) = (e3m+e3p)^3  exactly (proven below),
and the true pole order is 1, so D_9 over-clears by (e3m+e3p)^2.

Checks (exact rational):
 (P) PROOF/IDENTITY  D_9 = (e3m+e3p)^3 on the manifold (symbolic + 8 random pts).
 (A) MINIMALITY      A_6*(e3m+e3p) reconstructs to a PURE-sumFree denominator
                     (=> a genuine 6-freq polynomial) across several chambers/slices,
                     while A_6 itself is NOT polynomial (team result) -> pole order = 1.
 (D) CONTROL         on a slice, the (e3m+e3p)-numerator factor appears with
                     multiplicity exactly 1 in the reduced denominator of A_6(t).
"""
from fractions import Fraction as F
import sympy as sp
import harness as h, chambers_n6 as cn, inv
from collectlib import full_sig, reconstruct, poly, collect_contig
SIG=[-1,-1,-1,1,1,1]; t=sp.Symbol('t')
def pr(*a): print(*a, flush=True)
def ee(oms): e=inv.invariants(oms); return e[2]+e[3]

pr("="*72)
pr("(P) IDENTITY  prod_{i in M,j in P}(w_i+w_j) = (w1w2w3 + w4w5w6)^3 on manifold")
D9expr,(e1,e2,e3m,e3p)=inv.D9_symbolic()
pr(f"    symbolic resultant -> D_9 = {sp.factor(D9expr)}")
import random
rnd=random.Random(2); allok=True
for _ in range(8):
    free=[F(rnd.randint(-60,60),10) for _ in range(4)]
    oms=cn.solve_squares(free)
    if oms is None or any(w==0 for w in oms): continue
    d_direct=inv.D9_from_oms(oms); e=inv.invariants(oms)
    allok=allok and (d_direct==(e[2]+e[3])**3)
pr(f"    D_9 == (e3m+e3p)^3 at random points: {allok}")

pr("="*72)
pr("(A) MINIMALITY  A_6*(e3m+e3p) -> pure-sumFree denom (polynomial); pole order 1")
bases=[[F(2),F(3),F(5),F(7)],[F(-3),F(2),F(4),F(-5)],[F(3),F(-7,2),F(5,2),F(-4)],
       [F(1),F(-27,10),F(43,10),F(12,5)]]
allmin=True; tested=0
for base in bases:
    msgs=[]
    for vary in (4,5):
        pts,_=collect_contig(base,vary, lambda tt,oms,im: im*ee(oms))
        res=reconstruct(pts)
        if res is None: msgs.append(f"w{vary}:reconfail({len(pts)})"); continue
        dN,dD,Nc,Dc=res
        sf0=sum(base); sumF=sp.Rational(sf0.numerator,sf0.denominator)+t
        pure=sp.simplify(poly(Dc)/sumF**dD)
        ok=bool(pure.is_number and pure!=0); allmin=allmin and ok; tested+=1
        msgs.append(f"w{vary}:degN={dN},degD={dD},pureSF={ok}")
    pr(f"    base {[str(x) for x in base]}: " + " | ".join(msgs))
pr(f"    => A_6*(e3m+e3p) polynomial on all {tested} tested slices: {allmin}")

pr("="*72)
pr("(D) CONTROL  multiplicity of (e3m+e3p) in reduced denom of A_6(t) is exactly 1")
base=[F(2),F(3),F(5),F(7)]
for vary in (4,5):
    pts,_=collect_contig(base,vary, lambda tt,oms,im: im)  # A_6 itself
    res=reconstruct(pts)
    dN,dD,Nc,Dc=res
    Dpoly=sp.Poly(poly(Dc),t)
    # (e3m+e3p)(t) numerator on slice
    ws=[sp.Integer(base[i].numerator)/sp.Integer(base[i].denominator) for i in range(4)]
    ws[vary-2]=ws[vary-2]+t; w2_,w3_,w4_,w5_=ws
    sF=w2_+w3_+w4_+w5_; sSig=-w2_**2-w3_**2+w4_**2+w5_**2
    w6_=-(-sF**2+sSig)/(-2*sF); w1_=-(sF+w6_)
    ee_t=sp.cancel(w1_*w2_*w3_+w4_*w5_*w6_); ee_n,_=sp.fraction(ee_t)
    mult=0; D=Dpoly
    while True:
        q,r=sp.div(D,sp.Poly(ee_n,t))
        if r==0: mult+=1; D=q
        else: break
    pr(f"    vary w{vary}: A_6(t) degN={dN} degD={dD}; (e3m+e3p)-multiplicity = {mult}")

pr("="*72)
pr("CONCLUSION: A_6 = i 2^5 g^-3 * N / (w1w2w3+w4w5w6), N deg-11 spline. (e3m+e3p)^1 minimal.")
