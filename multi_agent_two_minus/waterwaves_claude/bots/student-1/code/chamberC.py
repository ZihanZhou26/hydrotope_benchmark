"""Generate many random on-shell points, compute C_n = a_n/(2^(n-1) w1 w2),
classify by chamber = tag-pattern (M/P) of the sorted squares, and fit C_n as a
polynomial in the sorted squares within each chamber."""
import sympy as sp, random, itertools
import bgio

def gen(n, npts, seed=0, double=False):
    random.seed(seed)
    vals=[sp.Rational(a) for a in range(1,13)]+[sp.Rational(a,2) for a in range(1,16,2)]+[sp.Rational(a,3) for a in range(1,20)]
    out=[]; tries=0
    while len(out)<npts and tries<200*npts:
        tries+=1
        fw=[random.choice(vals) for _ in range(n-2)]
        if len(set(fw))<len(fw): continue
        r=bgio.onshell(n, fw, double=double)
        if not r["ok"]: continue
        if double:
            om=[sp.Float(x,30) for x in r["omega"]]; a=sp.Float(r["im"],30)
        else:
            om=[sp.Rational(x.numerator,x.denominator) for x in r["omega"]]; a=sp.Rational(r["a"].numerator,r["a"].denominator)
        if len(set([abs(x) for x in om]))<n: continue
        out.append((om,a))
    return out

def C_and_pattern(n, om, a):
    w1,w2=om[0],om[1]
    C=a/(2**(n-1)*w1*w2)
    sq=sorted([(om[i]**2, ('M' if i in (0,1) else 'P')) for i in range(n)], key=lambda z:z[0])
    pat=tuple(t for _,t in sq)
    squares=[s for s,_ in sq]
    return C, pat, squares

def fit_poly_in_squares(pts_CS, nvars, deg, verbose=False):
    """pts_CS: list of (C, [u1..]) with u sorted squares. Fit C = poly(u1..u_nvars) homog deg."""
    us=sp.symbols(f'u1:{nvars+1}')
    # weighted homogeneous (each u has weight 1) degree=deg monomials
    monos=[]
    def rec(i,rem,cur):
        if i==nvars-1: monos.append(tuple(cur+[rem])); return
        for e in range(rem+1): rec(i+1,rem-e,cur+[e])
    rec(0,deg,[])
    rows=[]; rhs=[]
    for C,U in pts_CS:
        rows.append([sp.prod(U[j]**m[j] for j in range(nvars)) for m in monos]); rhs.append(C)
    M=sp.Matrix(rows); b=sp.Matrix(rhs)
    aug=M.row_join(b)
    if M.rank()!=aug.rank():
        return None, None
    sol=M.solve_least_squares(b) if M.rank()<len(monos) else M.solve(b)
    expr=sum(sol[i]*sp.prod(us[j]**monos[i][j] for j in range(nvars)) for i in range(len(monos)))
    return sp.expand(expr), us

if __name__=="__main__":
    n=6
    pts=gen(n, 300, seed=5)
    from collections import defaultdict
    groups=defaultdict(list)
    for om,a in pts:
        C,pat,sq=C_and_pattern(n,om,a)
        groups[pat].append((C,sq))
    print(f"n={n}: {len(pts)} points, {len(groups)} chamber-patterns")
    nrel=n-3  # 3 for n=6; fit in the (n-3) or (n-2) smallest squares
    for pat,lst in sorted(groups.items(), key=lambda kv:-len(kv[1])):
        if len(lst)<8: continue
        # try fitting C as polynomial in the (nrel) and (nrel+1) smallest squares
        done=False
        for nv in (nrel, nrel+1, nrel+2):
            data=[(C,sq[:nv]) for C,sq in lst]
            expr,us=fit_poly_in_squares(data, nv, nrel)
            if expr is not None:
                # verify
                ok=all(sp.nsimplify(C-expr.subs({us[j]:sq[j] for j in range(nv)}))==0 for C,sq in lst)
                if ok:
                    print(f"  pattern {pat} (count {len(lst)}): C_6 = {expr}   [in {nv} smallest squares]")
                    done=True; break
        if not done:
            print(f"  pattern {pat} (count {len(lst)}): NO polynomial fit in up to {nrel+2} smallest squares")
