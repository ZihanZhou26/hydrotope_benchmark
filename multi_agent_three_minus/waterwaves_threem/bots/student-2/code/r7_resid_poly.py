#!/usr/bin/env python3
"""The n>=7 single-pair residue's ONLY merged-scale poles are the SUB-COLLISIONS
(loci where a SECOND mixed pair also vanishes) -- the recursive matching structure.

At wall {w2+w5=0} with survivors {1,3,4,6,7} fixed, the residue Res(w2) has
denominator = the OTHER 11 mixed pairs evaluated at w5=-w2.  Six of them are
w2-independent (survivor-only pairs); five DEPEND on w2:
   (w1-w2),(w3-w2)  [merged minus 2 colliding with survivor minus 1,3 -> pair (1,5),(3,5) also ->0]
   (w2+w4),(w2+w6),(w2+w7)  [merged minus 2 + survivor plus -> new pair (2,4),(2,6),(2,7) ->0]
So P(w2) := Res(w2)*(w1-w2)(w3-w2)(w2+w4)(w2+w6)(w2+w7) should be POLYNOMIAL in w2
(= N7|_wall / const).  Confirm + read off its degree."""
import sympy as sp
from fractions import Fraction as F
from r7_resid_scale3 import residue_25_fconst
u=sp.Symbol('u')

w3,w4,w6t=F(3),F(5),F(11)
# tight cluster to stay in one chamber
w2list=[F(7,4),F(15,8),F(2),F(17,8),F(9,4),F(19,8),F(5,2),F(21,8),F(11,4),F(23,8),F(3),F(25,8)]
pts=[]; surv0=None
for w2 in w2list:
    if w2==w3: continue  # skip degenerate w2=w3
    try: out,npts=residue_25_fconst(w2,w3,w4,w6t)
    except Exception as ex: print(f"  w2={w2}: exc {ex}"); continue
    if out is None: print(f"  w2={w2}: bad ({npts})"); continue
    res,w=out
    surv=(w[1],w[3],w[4],w[6],w[7])
    if surv0 is None: surv0=surv
    if surv!=surv0: print(f"  w2={w2}: survivor changed!"); continue
    w1,_,_,w6v,w7=surv
    w2r=sp.Rational(w2.numerator,w2.denominator)
    fac=(sp.Rational(w1.numerator,w1.denominator)-w2r)*(sp.Integer(3)-w2r)*(w2r+5)*(w2r+sp.Integer(11))*(w2r+sp.Rational(w7.numerator,w7.denominator))
    P=sp.Rational(res)*fac
    pts.append((w2r,P,sp.Rational(res)))
    print(f"  w2={w2}: Res/i={res}  P={P}")

print(f"\nSurvivors (w1,w3,w4,w6,w7) = {surv0}")
print(f"Collected {len(pts)} points.")
if len(pts)>=5:
    xs=[x for x,_,_ in pts]; ys=[y for _,y,_ in pts]
    half=len(pts)*2//3
    poly=sp.interpolate(list(zip(xs[:half],ys[:half])),u)
    pp=sp.Poly(poly,u)
    ok=all(sp.simplify(pp.eval(xs[i])-ys[i])==0 for i in range(half,len(pts)))
    print(f"\nP(w2) polynomial? held-out OK = {ok}; degree = {pp.degree()}")
    if ok:
        print(f"P(w2) = N7|wall/const, as poly in merged scale w2:")
        print(f"   {sp.factor(poly)}")
        print(f"\n=> the residue Res(w2) = P(w2) / [(w1-w2)(w3-w2)(w2+w4)(w2+w6)(w2+w7) * const]")
        print(f"   i.e. its ONLY merged-scale poles are the 5 SUB-COLLISION loci. QED recursive matching.")
    else:
        print("Held-out failed -> chamber changed across this w2 range; residue is PIECEWISE in w2 too.")
        for x,y,r in pts: print(f"   w2={x}: P={y}")
