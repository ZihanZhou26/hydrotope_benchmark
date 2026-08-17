"""General local free-fit of a_n as homogeneous-degree-(2n-4) rational function
of the n-2 free freqs, within one fine chamber. Returns numerator/denominator."""
import sympy as sp, itertools
import bgio

def homog_monos(nv, deg):
    res=[]
    def rec(i,rem,cur):
        if i==nv-1:
            res.append(tuple(cur+[rem])); return
        for e in range(rem+1):
            rec(i+1,rem-e,cur+[e])
    rec(0,deg,[])
    return res

def local_points(n, base, steps):
    pts=[]; seen=set()
    base=[sp.Rational(v) for v in base]
    grids=[[b+s for s in steps] for b in base]
    for combo in itertools.product(*grids):
        if len(set(combo))<len(combo): continue
        fw=list(combo); key=tuple(fw)
        if key in seen: continue
        seen.add(key)
        r=bgio.onshell(n,fw)
        if not r["ok"]: continue
        om=[sp.Rational(q.numerator,q.denominator) for q in r["omega"]]
        if len(set([abs(v) for v in om]))<n: continue
        a=sp.Rational(r["a"].numerator,r["a"].denominator)
        pts.append((fw,om,a))
    return pts

def fit(n, pts, dmax=3):
    nv=n-2
    vs=sp.symbols(f'v0:{nv}')
    deg=2*n-4
    for d in range(0,dmax+1):
        Nmon=homog_monos(nv,deg+d); Dmon=homog_monos(nv,d)
        nN,nD=len(Nmon),len(Dmon)
        if nN+nD>len(pts):
            continue
        rows=[]
        for fw,om,a in pts:
            Nrow=[sp.prod(fw[i]**m[i] for i in range(nv)) for m in Nmon]
            Drow=[a*sp.prod(fw[i]**m[i] for i in range(nv)) for m in Dmon]
            rows.append([-q for q in Nrow]+Drow)
        M=sp.Matrix(rows); ns=M.nullspace()
        if len(ns)==1:
            v=ns[0]; cN=v[:nN]; cD=v[nN:]
            N=sum(cN[i]*sp.prod(vs[j]**Nmon[i][j] for j in range(nv)) for i in range(nN))
            D=sum(cD[i]*sp.prod(vs[j]**Dmon[i][j] for j in range(nv)) for i in range(nD))
            return sp.cancel(N/D), d, sp.factor(N), sp.factor(D), vs
    return None,None,None,None,vs

def find_chamber(n, ksmall, seed=0, maxtry=40000):
    """find a base free-vec where exactly ksmall plus legs lie below the smaller-minus magnitude."""
    import random; random.seed(seed)
    vals=[sp.Rational(a,2) for a in range(2,40)]+[sp.Rational(a,3) for a in range(2,50)]
    for _ in range(maxtry):
        fw=[random.choice(vals) for _ in range(n-2)]
        if len(set(fw))<len(fw): continue
        r=bgio.onshell(n,fw)
        if not r["ok"]: continue
        om=[sp.Rational(q.numerator,q.denominator) for q in r["omega"]]
        if len(set([abs(v) for v in om]))<n: continue
        m=min(abs(om[0]),abs(om[1]))
        kk=sum(1 for j in range(2,n) if abs(om[j])<m)
        if kk==ksmall:
            return fw, om
    return None,None
