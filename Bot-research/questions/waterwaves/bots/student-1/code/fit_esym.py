"""Test whether a_n is a polynomial in the plus-leg elementary symmetric
polynomials e1,e2,...,e_{n-2}, homogeneous of weighted degree 2n-4
(deg e_k = k). On-shell the minus pair satisfies sum=-e1, prod=e2.

Generates on-shell points via -w, extracts full omega, computes e_k from
plus legs (omega_3..omega_n), and solves for the polynomial coefficients
by exact linear algebra over many points.
"""
import sympy as sp, itertools, random
import bgio

def esym_plus(omega):
    """elementary symmetric polys of plus legs omega[2:] (0-indexed)."""
    plus=omega[2:]
    n=len(plus)
    es=[sp.Integer(1)]
    for k in range(1,n+1):
        es.append(sum(sp.prod(c) for c in itertools.combinations(plus,k)))
    return es[1:]  # e1..e_{n-2}

def gen_points(n, npts, lo=-6, hi=8, seed=0):
    random.seed(seed)
    pts=[]
    tries=0
    vals=[sp.Rational(x) for x in range(lo,hi+1) if x!=0]+[sp.Rational(1,2),sp.Rational(3,2),sp.Rational(5,2),sp.Rational(-3,2)]
    while len(pts)<npts and tries<60*npts:
        tries+=1
        fw=[random.choice(vals) for _ in range(n-2)]
        if len(set(fw))<len(fw): continue
        r=bgio.onshell(n, fw)
        if not r["ok"]: continue
        om=[sp.Rational(x.numerator,x.denominator) for x in r["omega"]]
        if len(set(om))<n: continue
        a=sp.Rational(r["a"].numerator,r["a"].denominator)
        pts.append((om,a))
    return pts

def weighted_monomials(nvars, weights, total):
    """all exponent tuples (a1..) with sum a_i*w_i == total."""
    res=[]
    def rec(i, rem, cur):
        if i==nvars:
            if rem==0: res.append(tuple(cur))
            return
        w=weights[i]
        for e in range(0, rem//w+1):
            rec(i+1, rem-e*w, cur+[e])
    rec(0, total, [])
    return res

def fit_poly_in_e(n, pts):
    ne=n-2
    weights=list(range(1,ne+1))
    total=2*n-4
    mons=weighted_monomials(ne, weights, total)
    esyms=sp.symbols(f'e1:{ne+1}')
    coeffs=sp.symbols(f'C0:{len(mons)}')
    expr=sum(c*sp.prod(esyms[i]**m[i] for i in range(ne)) for c,m in zip(coeffs,mons))
    rows=[]; rhs=[]
    for om,a in pts:
        es=esym_plus(om)
        sub={esyms[i]:es[i] for i in range(ne)}
        row=[sp.prod(es[i]**m[i] for i in range(ne)) for m in mons]
        rows.append(row); rhs.append(a)
    M=sp.Matrix(rows); b=sp.Matrix(rhs)
    print(f"  #monomials={len(mons)}, #points={len(pts)}, rank={M.rank()}")
    sol,params=M.gauss_jordan_solve(b) if M.rank()<len(mons) else (M.solve(b),None)
    return mons, esyms, sol, M, b

if __name__=="__main__":
    n=5
    pts=gen_points(n, 30, seed=1)
    print(f"n={n}: generated {len(pts)} points")
    ne=n-2; weights=list(range(1,ne+1)); total=2*n-4
    mons=weighted_monomials(ne,weights,total)
    esyms=sp.symbols(f'e1:{ne+1}')
    rows=[]; rhs=[]
    for om,a in pts:
        es=esym_plus(om)
        rows.append([sp.prod(es[i]**m[i] for i in range(ne)) for m in mons]); rhs.append(a)
    M=sp.Matrix(rows); b=sp.Matrix(rhs)
    print("  monomials (exponents of e1..):", mons)
    print("  matrix rank:", M.rank(), " unknowns:", len(mons))
    aug=M.row_join(b)
    print("  augmented rank:", aug.rank())
    if M.rank()==aug.rank():
        # consistent -> solve least-norm / particular
        try:
            sol=M.solve_least_squares(b)
        except Exception:
            sol,_=M.gauss_jordan_solve(b)
        expr=sum(sol[i]*sp.prod(esyms[j]**mons[i][j] for j in range(ne)) for i in range(len(mons)))
        print("  CONSISTENT. a_5 =", sp.nsimplify(sp.expand(expr)))
        # verify
        ok=all(sp.simplify(expr.subs({esyms[j]:esym_plus(om)[j] for j in range(ne)})-a)==0 for om,a in pts)
        print("  verify all points:", ok)
    else:
        print("  INCONSISTENT: a_n is NOT a polynomial in (e1..e_{n-2}) alone.")
