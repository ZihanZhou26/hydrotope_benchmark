"""n=4 two-minus amplitude via delta->0 limit.
On-shell forces omega=(-b, a, b, -a) with a=omega_2, b=omega_3, but that point is 0/0.
Relax: omega_4=-a+delta, omega_1=-(b+delta) (keeps sum=0; breaks square-constraint by -2 delta (a+b)).
Extrapolate delta->0.

Exact-rational extrapolation: evaluate a_4(delta) at several exact rational delta,
fit a polynomial in delta through them (sympy, exact), read constant term.
"""
import sys
from fractions import Fraction as Fr
import sympy as sp
import bgio

def a4_limit(a, b, deltas=None, deg=None, verbose=False):
    a=Fr(a); b=Fr(b)
    if deltas is None:
        deltas=[Fr(1,d) for d in (2,3,4,5,6,7,8)]
    pts=[]
    for d in deltas:
        w2=a; w3=b; w4=-a+d; w1=-(b+d)
        omega=[w1,w2,w3,w4]
        r=bgio.amp_twominus(omega, double=False)
        if not r["ok"]:
            if verbose: print("  fail at delta",d, r.get("rc"))
            continue
        assert r["re_zero"], f"Re!=0 at delta={d}"
        pts.append((d, r["a"]))
    if len(pts)<4:
        raise RuntimeError(f"only {len(pts)} good delta points for a={a},b={b} (singular config?)")
    if deg is None:
        deg=len(pts)-1
    x=sp.symbols('x')
    # exact polynomial interpolation through (delta, a) points
    xs=[sp.Rational(d.numerator, d.denominator) for d,_ in pts]
    ys=[sp.Rational(v.numerator, v.denominator) for _,v in pts]
    poly=sp.interpolate(list(zip(xs,ys)), x)
    lim=sp.simplify(poly.subs(x,0))
    if verbose:
        print(f"  a={a} b={b}: {len(pts)} pts, limit={lim}")
    return sp.nsimplify(lim), pts

if __name__=="__main__":
    for (a,b,exp) in [(1,3,-24),(2,5,-320)]:
        lim,pts=a4_limit(a,b,verbose=True)
        print(f"(a={a},b={b}) -> a_4={lim}   expected {exp}   {'OK' if sp.Rational(exp)==lim else 'MISMATCH'}")
