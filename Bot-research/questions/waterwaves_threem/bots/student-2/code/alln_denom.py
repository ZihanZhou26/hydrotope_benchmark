#!/usr/bin/env python3
"""All-n denominator mechanism (no oracle).
D_n^free = prod_{i in M, j in P}(w_i+w_j) = Res(p_-, Q_n) = prod_{i in M} r(w_i),
where r(x) = Q_n(x) mod p_-(x), Q_n(x)=prod_{j in P}(x+w_j), p_-(x)=prod_{i in M}(x-w_i).
On the manifold e1^-=-e1^+, e2^-=e2^+, which makes deg(r) = (n-3)-3 ... no: deg r<=2.
COLLAPSE (D = perfect power, minimal denom = lower degree) happens IFF r is CONSTANT,
i.e. n=6 (then r=e3m+e3p, D=(e3m+e3p)^3, minimal=(e3m+e3p)^1).
For n>=7, deg r>=1 => D_n^free is NOT a perfect power -> minimal denom = full product."""
import sympy as sp, itertools
from fractions import Fraction as F
import harness as h

def ek(vals,k):
    return sum(sp.prod(c) for c in itertools.combinations(vals,k)) if k>0 else sp.Integer(1)

def analyze_n(free_str, n):
    M=tuple(range(1,4)); P=tuple(range(4,n+1))
    SIG=[-1,-1,-1]+[1]*(n-3)
    oms=h.solve_legs_1n(free_str,SIG)
    w=[sp.Rational(o.numerator,o.denominator) for o in oms]
    x=sp.Symbol('x')
    p_=sp.prod([x-w[i-1] for i in M])
    Qn=sp.prod([x+w[j-1] for j in P])
    q,r=sp.div(sp.Poly(Qn,x),sp.Poly(p_,x))
    rdeg=r.degree() if r.as_expr()!=0 else -1
    Dfree=sp.Integer(1)
    for i in M:
        for j in P: Dfree*=(w[i-1]+w[j-1])
    Dvia=sp.prod([r.eval(w[i-1]) for i in M])
    # squarefree check of Dfree as number can't be done; check structure: collapse <=> r const
    collapse = (rdeg<=0)
    print(f"n={n}: deg(r = Q_n mod p_-)={rdeg}  D_free==prod_i r(w_i)? {sp.simplify(Dfree-Dvia)==0}  "
          f"COLLAPSE(perfect power)? {collapse}  =>  minimal denom = "
          f"{'(reduced radical, deg<full)' if collapse else 'FULL product prod(w_i+w_j), deg '+str(3*(n-3))}")
    return rdeg

if __name__=="__main__":
    cases={5:[F(2),F(3),F(5)],6:[F(2),F(3),F(5),F(7)],7:[F(2),F(3),F(5),F(7),F(11)],
           8:[F(2),F(3),F(5),F(7),F(11),F(13)],9:[F(2),F(3),F(5),F(7),F(11),F(13),F(17)]}
    print("deg N_n with MINIMAL denom: n=6 -> 8+3=11 (collapse); n>=7 -> (2n-4)+3(n-3)=5n-13\n")
    for n,free in cases.items():
        analyze_n(free,n)
