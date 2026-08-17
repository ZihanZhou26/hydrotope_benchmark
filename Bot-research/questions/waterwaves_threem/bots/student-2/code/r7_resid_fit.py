#!/usr/bin/env python3
"""Reconstruct Res_{25}(merged scale w2) as an EXACT rational function of w2,
at FIXED surviving config (w3,w4,w6target). Identify its pole structure
(predicted: sub-collision loci = the recursive matching structure)."""
import sympy as sp
from fractions import Fraction as F
from r7_resid_scale3 import residue_25_fconst
u=sp.Symbol('u')

w3,w4,w6t=F(3),F(5),F(11)
# cluster of merged scales in one chamber-interval (avoid w2=3 collision)
w2list=[F(7,4),F(2),F(9,4),F(5,2),F(11,4),F(3,2),F(5,4),F(1),F(3,4),F(1,2),F(13,4),F(7,2),F(15,4),F(4)]
pts=[]
surv0=None
for w2 in w2list:
    try:
        out,npts=residue_25_fconst(w2,w3,w4,w6t)
    except Exception as e:
        print(f"  w2={w2}: exception {e}"); continue
    if out is None: print(f"  w2={w2}: bad (code {npts})"); continue
    res,w=out
    surv=(w[1],w[3],w[4],w[6],w[7])
    if surv0 is None: surv0=surv
    same = surv==surv0
    pts.append((sp.Rational(w2.numerator,w2.denominator),sp.Rational(res)))
    print(f"  w2={w2}: Res/i={res}  surv_same={same}")

print(f"\nCollected {len(pts)} clean residue points. Surviving config = {surv0}")
if len(pts)>=4:
    # group into the largest set sharing one rational-function fit
    xs=[x for x,_ in pts]; ys=[y for _,y in pts]
    # Try rational reconstruction: Res(u) = Pnum(u)/Pden(u). Scan degrees.
    n=len(pts)
    found=False
    for dd in range(0,6):
        for nd in range(0,8):
            if nd+dd+2>n: continue
            # solve sum a_k u^k - Res * sum b_l u^l = 0, b_0=1
            A=[]; b=[]
            import itertools
            rows=[]
            for x,y in pts:
                row=[x**k for k in range(nd+1)]+[-y*x**l for l in range(1,dd+1)]
                rows.append((row,y))  # rhs = y*b_0 = y
            Mrows=sp.Matrix([r for r,_ in rows])
            rhs=sp.Matrix([yy for _,yy in rows])
            try:
                sol,params=Mrows.gauss_jordan_solve(rhs)
            except Exception:
                continue
            if params.shape[1]!=0: continue
            num=sum(sol[k]*u**k for k in range(nd+1))
            den=1+sum(sol[nd+1+l]*u**(l+1) for l in range(dd))  if dd>0 else sp.Integer(1)
            # verify on all points
            ok=all(sp.simplify(num.subs(u,x)/den.subs(u,x)-y)==0 for x,y in pts)
            if ok:
                print(f"\nRATIONAL FIT degree num={nd} den={dd}:")
                print(f"  Res(w2) = [{sp.factor(num)}] / [{sp.factor(den)}]")
                found=True; break
        if found: break
    if not found:
        print("\nNo low-degree rational fit found in scanned range; printing values:")
        for x,y in pts: print(f"  w2={x}: {y}  = {float(y):.4e}")
