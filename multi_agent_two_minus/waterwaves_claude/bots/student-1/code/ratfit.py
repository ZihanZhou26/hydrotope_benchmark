"""Fit a_n as a weighted-homogeneous RATIONAL function N/D of the plus-leg
elementary symmetric polynomials e1..e_{n-2} (weights 1..n-2), within a
single chamber (smallest |omega| is a minus leg, like the PI reference pts).

a_n * D(e) = N(e), linear & homogeneous in unknown coeffs -> nullspace.
"""
import sympy as sp, itertools, random
import bgio

def esym_plus(omega):
    plus=omega[2:]
    es=[]
    for k in range(1,len(plus)+1):
        es.append(sum(sp.prod(c) for c in itertools.combinations(plus,k)))
    return es  # e1..e_{n-2}

def wmonos(nvars, weights, total):
    res=[]
    def rec(i,rem,cur):
        if i==nvars:
            if rem==0: res.append(tuple(cur))
            return
        for e in range(rem//weights[i]+1):
            rec(i+1,rem-e*weights[i],cur+[e])
    rec(0,total,[])
    return res

def chamber_ok(omega):
    """smallest magnitude leg is a minus leg (index 0 or 1)."""
    mags=[abs(x) for x in omega]
    return mags.index(min(mags)) in (0,1)

def gen_points(n, npts, seed=0, want_chamber=True):
    random.seed(seed)
    vals=[sp.Rational(x) for x in range(1,13)]+[sp.Rational(1,2),sp.Rational(3,2),sp.Rational(5,2),sp.Rational(7,2)]
    pts=[]; tries=0
    while len(pts)<npts and tries<200*npts:
        tries+=1
        # bias: small omega_2 (a minus free leg) to land in reference chamber
        fw=[random.choice(vals) for _ in range(n-2)]
        if len(set(fw))<len(fw): continue
        r=bgio.onshell(n, fw)
        if not r["ok"]: continue
        om=[sp.Rational(x.numerator,x.denominator) for x in r["omega"]]
        if len(set([abs(x) for x in om]))<n: continue
        if want_chamber and not chamber_ok(om): continue
        a=sp.Rational(r["a"].numerator,r["a"].denominator)
        pts.append((om,a))
    return pts

def fit(n, pts, dmax=4, verbose=True):
    ne=n-2; weights=list(range(1,ne+1)); tot=2*n-4
    esyms=sp.symbols(f'e1:{ne+1}')
    for d in range(0,dmax+1):
        Nmon=wmonos(ne,weights,tot+d); Dmon=wmonos(ne,weights,d)
        nN,nD=len(Nmon),len(Dmon)
        # unknowns: c (numerator), e (denominator). Build homogeneous system.
        rows=[]
        for om,a in pts:
            es=esym_plus(om)
            Nrow=[sp.prod(es[j]**m[j] for j in range(ne)) for m in Nmon]
            Drow=[a*sp.prod(es[j]**m[j] for j in range(ne)) for m in Dmon]
            rows.append([-x for x in Nrow]+Drow)   # -N + a*D = 0
        M=sp.Matrix(rows)
        ns=M.nullspace()
        if verbose: print(f"  d={d}: nN={nN} nD={nD} unknown={nN+nD} points={len(pts)} nullity={len(ns)}")
        if len(ns)==1:
            v=ns[0]
            cN=v[:nN]; cD=v[nN:]
            N=sum(cN[i]*sp.prod(esyms[j]**Nmon[i][j] for j in range(ne)) for i in range(nN))
            D=sum(cD[i]*sp.prod(esyms[j]**Dmon[i][j] for j in range(ne)) for i in range(nD))
            expr=sp.cancel(N/D)
            return expr, d, esyms
    return None, None, esyms

if __name__=="__main__":
    n=5
    pts=gen_points(n, 40, seed=3)
    print(f"n={n}: {len(pts)} reference-chamber points")
    expr,d,esyms=fit(n,pts)
    if expr is None:
        print("no unique rational fit up to dmax")
    else:
        print(f"FOUND at denom weighted-deg d={d}:")
        print("  a_5 =", expr)
        print("  factored:", sp.factor(expr))
        # verify on fresh points
        test=gen_points(n, 15, seed=99)
        ne=n-2
        ok=all(sp.simplify(expr.subs({esyms[j]:esym_plus(om)[j] for j in range(ne)})-a)==0 for om,a in test)
        print("  verify on 15 fresh reference-chamber points:", ok)
