"""Fit a_4(a,b) as a homogeneous degree-4 polynomial. a=omega_2, b=omega_3.
Full omega = (-b, a, b, -a). Minus legs {omega_1,omega_2}={-b,a}; plus {b,-a}.
"""
import sympy as sp
from fractions import Fraction as Fr
from n4_limit import a4_limit

a,b = sp.symbols('a b')

# grid of (a,b)
grid=[(1,3),(2,5),(1,2),(2,3),(3,4),(1,4),(2,7),(3,5),(4,3),(5,2),(2,1),(3,1),(5,3),(1,5),(4,7)]
data=[]
for (av,bv) in grid:
    lim,_=a4_limit(av,bv)
    data.append((av,bv,sp.Rational(int(lim))))
    print(f"a={av} b={bv} -> a_4={lim}")

# fit homogeneous degree-4
mons=[a**4, a**3*b, a**2*b**2, a*b**3, b**4]
coeffs=sp.symbols('c0 c1 c2 c3 c4')
expr=sum(c*m for c,m in zip(coeffs,mons))
eqs=[expr.subs({a:av,b:bv})-val for (av,bv,val) in data]
sol=sp.solve(eqs, coeffs, dict=True)
print("solution:", sol)
if sol:
    fit=expr.subs(sol[0])
    print("a_4(a,b) =", sp.factor(fit))
    # verify on all grid points
    ok=all(sp.simplify(fit.subs({a:av,b:bv})-val)==0 for (av,bv,val) in data)
    print("all grid points reproduced:", ok)
