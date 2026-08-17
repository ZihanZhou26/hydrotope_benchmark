#!/usr/bin/env python3
"""(A) Soft recursion n=7 both legs (own oracle, F-const slice, exact).
   (B) Geometric forcing facts underpinning the cross-term closing order at n=7."""
import sympy as sp, itertools
from fractions import Fraction as F
import r8bg, r8lib as L

e = sp.Symbol('e')
def Q(x): return sp.Rational(F(x).numerator, F(x).denominator)

def Dfull(oms):
    n=len(oms); d=F(1)
    for i in range(3):
        for j in range(3,n): d*=(oms[i]+oms[j])
    return d

def soft_limit(n, base_free, soft_idx, comp_idx, neps=34, fitdeg=24):
    """F-const slice: free[soft]=eps, free[comp]=base[soft]+base[comp]-eps.
       TINY eps -> stay in the soft chamber. Fit N_full(eps)=A*Dfull (degree<=2n-4)
       and Dfull(eps) as polynomials with HELD-OUT validation (single-piece).
       Return (lim (A/i)/eps^2, single_piece_ok)."""
    s = base_free[soft_idx] + base_free[comp_idx]
    frees=[]; epsv=[]
    for k in range(1, neps+1):
        eps = F(1,4000)*k     # tiny: single soft chamber
        fr = list(base_free); fr[soft_idx]=eps; fr[comp_idx]=s-eps
        if sum(F(x) for x in fr)==0: continue
        frees.append(fr); epsv.append(eps)
    ims = r8bg.batch(frees, n, double=False)
    pts=[]
    for eps,fr,im in zip(epsv,frees,ims):
        if im is None: continue
        oms=r8bg.solve_legs(fr,n)
        pts.append((eps, F(im)*Dfull(oms), Dfull(oms)))
    xs=[Q(p[0]) for p in pts]
    nf=[Q(p[1]) for p in pts]; df=[Q(p[2]) for p in pts]
    Nful=sp.Poly(sp.interpolate(list(zip(xs[:fitdeg],nf[:fitdeg])),e),e)
    Dful=sp.Poly(sp.interpolate(list(zip(xs[:fitdeg],df[:fitdeg])),e),e)
    ok = all(Nful.eval(xs[i])==nf[i] for i in range(fitdeg,len(pts))) and \
         all(Dful.eval(xs[i])==df[i] for i in range(fitdeg,len(pts)))
    # vanish to order 2, then lim = [eps^2] N_full / Dful(0)
    vanish = (Nful.nth(0)==0 and Nful.nth(1)==0)
    lim = sp.Rational(Nful.nth(2)) / sp.Rational(Dful.eval(0))
    return sp.nsimplify(lim), (ok and vanish)

def forcing_check():
    print("="*70); print("(B) n=7 geometric forcing (exact)"); print("="*70)
    # two disjoint (1=1) edges a1=b4, a2=b5  => check a3 = b6+b7 (a (1=2) relation)
    # Build a point with w1^2=w4^2 and w2^2=w5^2 on the manifold, check w3^2 vs w6^2+w7^2.
    # Param: choose w4,w5,w6 plus, set w1=-w4 (=> a1=b4 via w1^2=w4^2), w2=-w5.
    # Then need on-shell: solve remaining. Use free=(w2,w3,w4,w5,w6); we want w1^2=w4^2.
    # w1 is solved, so instead pick a slice and find crossing numerically->exact rational.
    # Simpler: directly construct on-shell point with the two coincidences.
    # Unknowns: w3,w6,w7 (3) with 2 constraints (sum, sumsig) => 1-param; impose nothing else.
    # Let w4=5,w5=3 (plus), w1=-5,w2=-3 (minus) [=> a1=b4, a2=b5]. Free: w3(minus),w6,w7(plus).
    # sum: -5-3+w3+5+3+w6+w7=0 => w3+w6+w7=0
    # sumsig: -(25+9+w3^2)+(25+9+w6^2+w7^2)=0 => w6^2+w7^2 = w3^2  (== a3=b6+b7!)  AUTOMATIC.
    print("Set w1=-5,w2=-3,w4=5,w5=3 (=> a1=b4, a2=b5). On-shell forces:")
    print("  sum=0 : w3+w6+w7=0 ;  sumsig=0 : w6^2+w7^2 = w3^2  <=> a3 = b6+b7  (a (1=2) wall)")
    print("  => two disjoint (1=1) edges FORCE the complementary (1=2) wall. CONFIRMED (algebra).")
    # numeric instance
    w3=sp.Symbol('w3'); w6=sp.Symbol('w6'); w7=sp.Symbol('w7')
    # pick w6=2,w7? from w3+2+w7=0 and 4+w7^2=w3^2 => w3=-(2+w7), (2+w7)^2-w7^2=4 =>4+4w7=4=>w7=0 -> degenerate
    # pick w6=2,w3 free: w7=-w3-2; w6^2+w7^2=w3^2 => 4+(w3+2)^2=w3^2 =>4+4w3+4=0=>w3=-2 -> w7=0 degenerate again
    print("  (note: fixing a1=b4,a2=b5 AND a third pair tends to force a vanishing leg)")
    print()
    print("Three disjoint (1=1) edges a1=b4,a2=b5,a3=b6 (=> w_i^2=w_j^2):")
    print("  sum a = b4+b5+b6 ; sum b = b4+b5+b6+b7 ; resonance sum a=sum b => b7=0 => w7=0.")
    print("  => THREE disjoint (1=1) edges FORCE a leg to vanish (DEGENERATE).")
    print("  => no transversal triple (1=1) intersection => NO pure triple-(1=1) cross-term.")

if __name__=="__main__":
    print("="*70); print("(A) SOFT RECURSION n=7 (own oracle, exact)"); print("="*70)
    base=[F(2),F(3),F(5),F(7),F(11)]   # w2,w3,w4,w5,w6  (legs 2,3 minus; 4,5,6 plus)
    # PLUS-leg soft (uncompensated): w4=eps, others fixed -> surviving 6-leg = drop w4.
    print("PLUS-leg soft (w4=eps->0): A7i/eps^2 should -> 8*A6^3m(surviving)")
    for k in [4,2,1]:
        eps=F(1,2000)*k; fr=[base[0],base[1],eps,base[3],base[4]]
        im=r8bg.amp_one(fr,7); print(f"   eps={float(eps):.5f}  A7i/eps^2 = {float(F(im)/eps**2):.3f}")
    oms7=r8bg.solve_legs([base[0],base[1],F(1,10**9),base[3],base[4]],7)
    oms6=[oms7[0],oms7[1],oms7[2],oms7[4],oms7[5],oms7[6]]  # drop w4 -> minus{w1,w2,w3} plus{w5,w6,w7}
    A6_3m=L.A2m_over_i  # placeholder
    im6,_=L.A_over_i_3m([base[0],base[1],base[3],base[4]],6)  # 6-leg 3m free [w2,w3,w5,w6]
    print(f"   8*A6^3m([2,3,7,11]) = {float(8*im6):.3f}   (exact 8*A6 = {8*im6})")
    # MINUS-leg soft (uncompensated): w2=eps, others fixed -> surviving 6-leg two-minus.
    print("MINUS-leg soft (w2=eps->0): A7i/eps^2 should -> 8*A6^2m(surviving)")
    for k in [4,2,1]:
        eps=F(1,2000)*k; fr=[eps,base[1],base[2],base[3],base[4]]
        im=r8bg.amp_one(fr,7); print(f"   eps={float(eps):.5f}  A7i/eps^2 = {float(F(im)/eps**2):.3f}")
    oms7=r8bg.solve_legs([F(1,10**9),base[1],base[2],base[3],base[4]],7)
    oms6m=[oms7[0],oms7[2],oms7[3],oms7[4],oms7[5],oms7[6]]  # drop w2 -> minus{w1,w3} plus{w4..w7}
    A6_2m=L.A2m_over_i(oms6m,0,1)
    print(f"   8*A6^2m(surviving) = {float(8*A6_2m):.3f}")
    print()
    forcing_check()
