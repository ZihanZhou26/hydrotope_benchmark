#!/usr/bin/env python3
"""FAST independent poly-vs-rational test + denominator finder, via EXACT
rational-function reconstruction from oracle evaluations (no heavy sympy).

Along the F-constant slice w4=5+t, w5=7-t (w2=2,w3=3), every w_i(t) is a
polynomial in t, so A_6(t)=N(t)/D(t) with N,D polynomials in t.  Evaluate A_6 at
many exact rational t (oracle, exact), then reconstruct (N,D) by exact linear
algebra for increasing denominator degree b.  b=0 consistent  -> polynomial;
smallest b>0 consistent -> rational with that denominator degree.  Factor D(t)
and match factors to |k_S|(t).
"""
from fractions import Fraction as Fr
import sympy as sp
import harness as h

SIG = [-1,-1,-1,1,1,1]
def freeoft(t):  # t rational
    return [Fr(2), Fr(3), Fr(5)+t, Fr(7)-t]

def A6(t):
    oim, _, _ = h.on_shell(freeoft(t), SIG)
    return oim

# sample points (avoid t where slice hits a wall / SIGFPE)
ts = []
k = 0
cand = [Fr(p, q) for q in (1,2,3,5,7,11) for p in range(-30,31) if Fr(p,q) not in (Fr(0),)]
vals = {}
for tv in cand:
    try:
        vals[tv] = A6(tv)
    except Exception:
        continue
    if len(vals) >= 90:
        break
pts = sorted(vals.keys(), key=lambda x: (x.denominator, abs(x.numerator)))
print(f"collected {len(pts)} exact samples", flush=True)

def fit(a, b, pts):
    """fit N deg a, D deg b (D monic). returns (n_coeffs,d_coeffs) or None if inconsistent."""
    need = a + b + 1
    use = pts[:need]
    # unknowns: n_0..n_a (a+1), d_0..d_{b-1} (b); D=t^b+sum d_j t^j
    M = []; rhs = []
    for tk in use:
        Ak = vals[tk]
        row = [tk**i for i in range(a+1)] + [-Ak*tk**j for j in range(b)]
        M.append(row); rhs.append(Ak*tk**b)
    A = sp.Matrix([[sp.Rational(x.numerator,x.denominator) for x in row] for row in M])
    bb = sp.Matrix([sp.Rational(x.numerator,x.denominator) for x in rhs])
    try:
        sol = A.LUsolve(bb)
    except Exception:
        return None
    ncoef = [sol[i] for i in range(a+1)]
    dcoef = [sol[a+1+j] for j in range(b)] + [sp.Integer(1)]
    # verify on held-out points
    extra = pts[need:need+12]
    if len(extra) < 6:
        extra = pts[:need]  # fall back
    for tk in extra:
        tq = sp.Rational(tk.numerator, tk.denominator)
        Nv = sum(ncoef[i]*tq**i for i in range(a+1))
        Dv = sum(dcoef[j]*tq**j for j in range(b+1))
        Ak = sp.Rational(vals[tk].numerator, vals[tk].denominator)
        if Dv == 0 or sp.simplify(Nv/Dv - Ak) != 0:
            return None
    return ncoef, dcoef

# sweep: find minimal b giving a consistent fit. try a up to some bound.
t = sp.Symbol('t')
found = None
for b in range(0, 13):
    for a in range(b, b+30):
        if a+b+1 > len(pts)-6:
            break
        r = fit(a, b, pts)
        if r:
            found = (a, b, r); break
    if found:
        break

if not found:
    print("no consistent (a,b) found in range", flush=True)
else:
    a, b, (ncoef, dcoef) = found
    print(f"\nMINIMAL fit: numerator degree a={a}, DENOMINATOR degree b={b}", flush=True)
    print("POLYNOMIAL?:", b == 0, flush=True)
    D = sum(dcoef[j]*t**j for j in range(b+1))
    print("D(t) factored:", sp.factor(D), flush=True)
    # match factors to |k_S|
    from itertools import combinations
    w4=sp.Integer(5)+t; w5=sp.Integer(7)-t; w2=sp.Integer(2); w3=sp.Integer(3)
    F=w2+w3+w4+w5; R=-w2**2-w3**2+w4**2+w5**2
    w1=-(F**2+R)/(2*F); w6=-(F**2-R)/(2*F)
    W={1:w1,2:w2,3:w3,4:w4,5:w5,6:w6}
    print("--- denominator factors as |k_S| ---", flush=True)
    for fac,mult in sp.factor_list(D)[1]:
        if sp.degree(sp.Poly(sp.expand(fac),t))==0: continue
        ms=[]
        for r in range(1,6):
            for S in combinations(range(1,7),r):
                ks=sp.expand(sum(sp.Integer(SIG[i-1])*W[i]**2 for i in S))
                if ks==0: continue
                q=sp.cancel(ks/fac)
                if q.free_symbols==set() and q!=0:
                    tag=''.join(f"{'+' if SIG[i-1]>0 else '-'}w{i}^2" for i in S)
                    ms.append(f"|k_{S}|~{tag}(x{q})")
        print(f"  {sp.factor(fac)} (m{mult}) -> {ms if ms else '?'}", flush=True)
