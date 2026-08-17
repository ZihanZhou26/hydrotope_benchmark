"""Fit a_5 as a homogeneous-degree-6 RATIONAL function of the free freqs
(x,y,z)=(omega_2,omega_3,omega_4), within ONE fine chamber (tiny local steps).
Then study its structure (factor numerator & denominator)."""
import sympy as sp, itertools
import bgio

x,y,z = sp.symbols('x y z')

def homog_monos(vars_, deg):
    res=[]
    n=len(vars_)
    def rec(i,rem,cur):
        if i==n-1:
            res.append(tuple(cur+[rem])); return
        for e in range(rem+1):
            rec(i+1,rem-e,cur+[e])
    rec(0,deg,[])
    return res

def local_free_points(n, base, steps):
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

def fit(pts, dmax=5):
    for d in range(0,dmax+1):
        Nmon=homog_monos((x,y,z),6+d); Dmon=homog_monos((x,y,z),d)
        nN,nD=len(Nmon),len(Dmon)
        if nN+nD>len(pts):
            print(f"  d={d}: unknowns {nN+nD}>pts {len(pts)}; skip"); continue
        rows=[]
        for fw,om,a in pts:
            xv,yv,zv=fw
            Nrow=[xv**m[0]*yv**m[1]*zv**m[2] for m in Nmon]
            Drow=[a*xv**m[0]*yv**m[1]*zv**m[2] for m in Dmon]
            rows.append([-q for q in Nrow]+Drow)
        M=sp.Matrix(rows); ns=M.nullspace()
        print(f"  d={d}: nN={nN} nD={nD} pts={len(pts)} nullity={len(ns)}")
        if len(ns)==1:
            v=ns[0]; cN=v[:nN]; cD=v[nN:]
            N=sum(cN[i]*x**Nmon[i][0]*y**Nmon[i][1]*z**Nmon[i][2] for i in range(nN))
            D=sum(cD[i]*x**Dmon[i][0]*y**Dmon[i][1]*z**Dmon[i][2] for i in range(nD))
            return sp.cancel(N/D), d, N, D
    return None,None,None,None

if __name__=="__main__":
    st=[sp.Rational(0),sp.Rational(1,50),sp.Rational(2,50),sp.Rational(3,50),sp.Rational(-1,50)]
    pts=local_free_points(5,[2,3,5],st)
    print(f"{len(pts)} local points around free=(2,3,5)")
    expr,d,N,D=fit(pts)
    if expr is None: print("no fit up to dmax")
    else:
        print(f"FOUND d={d}:")
        print("  a_5(x=om2,y=om3,z=om4) =", expr)
        print("  numerator factored:", sp.factor(N))
        print("  denominator factored:", sp.factor(D))
        # verify on the base reference point exactly
        for fw,exp in [([2,3,5],-3328),([1,2,4],sp.Rational(-544,7))]:
            val=expr.subs({x:fw[0],y:fw[1],z:fw[2]})
            print(f"  check free={fw}: {sp.nsimplify(val)} (expect {exp})", "OK" if sp.nsimplify(val)==exp else "NO")
