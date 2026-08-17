"""Fit a_n as a rational function of (e1..e_{n-2}) within ONE fine chamber, by
perturbing the free frequencies locally around a base config (small rational
steps that don't cross any |kS|=0 boundary). The fitted rational function is
the analytic form on that chamber."""
import sympy as sp, itertools
import bgio
from ratfit import esym_plus, wmonos

def local_points(n, base_free, steps):
    """base_free: list of n-2 free freqs. steps: list of small rational deltas
    applied to each coordinate combinatorially (a small grid)."""
    pts=[]; seen=set()
    import itertools as it
    base=[sp.Rational(x) for x in base_free]
    # vary each coordinate over base+step for a few steps; take a sparse grid
    grids=[[b+s for s in steps] for b in base]
    for combo in it.product(*grids):
        if len(set(combo))<len(combo): continue
        fw=list(combo)
        key=tuple(fw)
        if key in seen: continue
        seen.add(key)
        r=bgio.onshell(n, fw)
        if not r["ok"]: continue
        om=[sp.Rational(x.numerator,x.denominator) for x in r["omega"]]
        if len(set([abs(x) for x in om]))<n: continue
        a=sp.Rational(r["a"].numerator,r["a"].denominator)
        pts.append((om,a))
    return pts

def fit_local(n, pts, dmax=6, verbose=True):
    ne=n-2; weights=list(range(1,ne+1)); tot=2*n-4
    esyms=sp.symbols(f'e1:{ne+1}')
    for d in range(0,dmax+1):
        Nmon=wmonos(ne,weights,tot+d); Dmon=wmonos(ne,weights,d)
        nN,nD=len(Nmon),len(Dmon)
        if nN+nD>len(pts):
            if verbose: print(f"  d={d}: need {nN+nD} unknowns > {len(pts)} pts; skip");
            continue
        rows=[]
        for om,a in pts:
            es=esym_plus(om)
            Nrow=[sp.prod(es[j]**m[j] for j in range(ne)) for m in Nmon]
            Drow=[a*sp.prod(es[j]**m[j] for j in range(ne)) for m in Dmon]
            rows.append([-x for x in Nrow]+Drow)
        M=sp.Matrix(rows); ns=M.nullspace()
        if verbose: print(f"  d={d}: nN={nN} nD={nD} pts={len(pts)} nullity={len(ns)}")
        if len(ns)>=1:
            v=ns[0]; cN=v[:nN]; cD=v[nN:]
            N=sum(cN[i]*sp.prod(esyms[j]**Nmon[i][j] for j in range(ne)) for i in range(nN))
            D=sum(cD[i]*sp.prod(esyms[j]**Dmon[i][j] for j in range(ne)) for i in range(nD))
            return sp.cancel(N/D), d, esyms, len(ns)
    return None,None,esyms,0

if __name__=="__main__":
    n=5
    steps=[sp.Rational(0),sp.Rational(1,7),sp.Rational(2,7),sp.Rational(3,7),sp.Rational(-1,11)]
    pts=local_points(n,[2,3,5],steps)
    print(f"n={n}: {len(pts)} local points around (2,3,5)")
    expr,d,esyms,nullity=fit_local(n,pts)
    if expr is None:
        print("no fit")
    else:
        print(f"FOUND d={d} nullity={nullity}:")
        print("  a_5 =", expr)
        print("  factored:", sp.factor(expr))
        ne=n-2
        ok=all(sp.simplify(expr.subs({esyms[j]:esym_plus(om)[j] for j in range(ne)})-a)==0 for om,a in pts)
        print("  reproduces all local points:", ok)
