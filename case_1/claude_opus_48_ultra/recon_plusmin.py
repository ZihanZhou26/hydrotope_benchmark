"""Reconstruct A_5 as a SYMMETRIC rational function of plus-freqs, restricted to the
region where the smallest-magnitude leg is a PLUS leg (the generic region)."""
from bg import amp_two_minus
from fractions import Fraction as Q
from recon import parts, msym, rref_nullspace
import itertools, sys

def collect_plusmin(n, grid, target=400):
    pts=[]; seen=set()
    for combo in itertools.product(grid, repeat=n-2):
        free=[Q(c) for c in combo]
        try: A,kL,wL=amp_two_minus(n,free)
        except Exception: continue
        w=wL
        x=tuple(w[2:])
        if any(xi==0 for xi in x): continue
        mags=[abs(v) for v in w]
        mn=min(mags)
        # smallest leg index
        argmin=mags.index(mn)
        if argmin<2:  # smallest is a minus leg -> skip; we want plus smallest
            continue
        # ensure unique smallest among plus and smaller than both minus
        key=tuple(sorted(x))
        if key in seen: continue
        seen.add(key); pts.append((x,A.im))
        if len(pts)>=target: break
    return pts

def reconstruct(n, pts, maxdD=10):
    m=n-2; dA=2*(n-2)
    for dD in range(0, maxdD+1):
        DB=parts(dD, m); NB=parts(dD+dA, m); nv=len(DB)+len(NB)
        if len(pts) < nv+5:
            print(f"  dD={dD}: need {nv} have {len(pts)} skip"); continue
        rows=[[Aim*msym(l,x) for l in DB]+[-msym(l,x) for l in NB] for (x,Aim) in pts]
        basis,_=rref_nullspace(rows)
        print(f"  dD={dD}: vars={nv} nullspace dim={len(basis)}",flush=True)
        if basis:
            return dD,DB,NB,basis
    return None

if __name__=="__main__":
    n=int(sys.argv[1]) if len(sys.argv)>1 else 5
    grid=[Q(1),Q(3,2),Q(2),Q(5,2),Q(3),Q(7,2),Q(4),Q(9,2),Q(5),Q(11,2),Q(6),
          Q(1,2),Q(5,4),Q(7,4),Q(9,4),Q(11,4),Q(13,4)]
    pts=collect_plusmin(n,grid,target=450)
    print(f"n={n}: {len(pts)} points (smallest leg is a plus leg)",flush=True)
    res=reconstruct(n,pts,maxdD=9)
    if res:
        import sympy as sp
        dD,DB,NB,basis=res
        print(f">>> dD={dD} dim={len(basis)}")
        x=sp.symbols(f'x1:{n-1}')
        def msym_sym(lam):
            from itertools import permutations
            exps=list(lam)+[0]*((n-2)-len(lam))
            terms=set(permutations(exps))
            return sum(sp.prod(x[i]**e[i] for i in range(n-2)) for e in terms)
        vec=basis[0]; Dc=vec[:len(DB)]; Nc=vec[len(DB):]
        D=sum(sp.Rational(Dc[i])*msym_sym(DB[i]) for i in range(len(DB)))
        N=sum(sp.Rational(Nc[i])*msym_sym(NB[i]) for i in range(len(NB)))
        print("D=",sp.factor(D))
        print("N=",sp.factor(N))
