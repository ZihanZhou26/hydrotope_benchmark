"""Fast exact symmetric rational fit of A_n in plus-frequencies x=(w3..wn).
Uses hand-rolled Fraction Gaussian elimination (sympy matrices too slow)."""
from bg import amp_two_minus
from fractions import Fraction as Q
from itertools import product as iproduct, permutations, combinations
from functools import lru_cache
import sys, itertools

# ---------- exact linear solve ----------
def solve_exact(rows, rhs):
    """Solve square system rows x = rhs over Q. rows: list of lists of Q. Returns list or None."""
    n=len(rows)
    A=[list(r)+[v] for r,v in zip(rows,rhs)]
    for c in range(n):
        piv=None
        for r in range(c,n):
            if A[r][c]!=0: piv=r;break
        if piv is None: return None
        A[c],A[piv]=A[piv],A[c]
        pv=A[c][c]
        A[c]=[a/pv for a in A[c]]
        for r in range(n):
            if r!=c and A[r][c]!=0:
                f=A[r][c]
                A[r]=[a-f*b for a,b in zip(A[r],A[c])]
    return [A[i][n] for i in range(n)]

def find_indep_rows(allrows, nb):
    """greedily pick nb rows forming invertible nb x nb (first nb cols)."""
    chosen=[]; basis=[]  # basis: reduced rows for rank check
    import copy
    red=[]
    for idx,row in enumerate(allrows):
        v=[Q(x) for x in row]
        # reduce against current basis
        for b in red:
            # b has leading 1 at position b_lead
            lead=b[0]
            if v[lead[1]]!=0:
                f=v[lead[1]]
                v=[a-f*c for a,c in zip(v,lead[0])]
        # find first nonzero
        nz=None
        for j in range(nb):
            if v[j]!=0: nz=j;break
        if nz is not None:
            vv=[a/v[nz] for a in v]
            red.append([(vv,nz)])
            # store as (vector, leadcol)
            red[-1]=[(vv,nz)]
            chosen.append(idx)
        if len(chosen)==nb: break
    # fix structure of red usage above (rewrite cleanly below)
    return chosen

# simpler: just try first nb rows, if singular try random offsets
def pick_and_solve(allrows, rhs, nb):
    import random
    N=len(allrows)
    tries=[list(range(nb))]
    rng=random.Random(12345)
    for _ in range(40):
        tries.append(rng.sample(range(N), nb))
    for sub in tries:
        rows=[[Q(x) for x in allrows[i]] for i in sub]
        b=[Q(rhs[i]) for i in sub]
        sol=solve_exact(rows,b)
        if sol is not None:
            return sol, sub
    return None, None

# ---------- symmetric polynomial basis ----------
@lru_cache(maxsize=None)
def partitions_into_parts(d, maxparts):
    res=[]
    def rec(rem,maxp,cur):
        if rem==0: res.append(tuple(cur)); return
        if len(cur)==maxparts: return
        for p in range(min(maxp,rem),0,-1):
            rec(rem-p,p,cur+[p])
    rec(d,d,[])
    return res

@lru_cache(maxsize=None)
def distinct_perms(exps):
    return tuple(set(permutations(exps)))

def msym(lam, xvals):
    m=len(xvals)
    exps=tuple(list(lam)+[0]*(m-len(lam)))
    tot=Q(0)
    for perm in distinct_perms(exps):
        t=Q(1)
        for xi,e in zip(xvals,perm):
            if e: t*=xi**e
        tot+=t
    return tot

def e_k(k, xvals):
    if k==0: return Q(1)
    s=Q(0)
    for c in combinations(range(len(xvals)),k):
        t=Q(1)
        for i in c: t*=xvals[i]
        s+=t
    return s

def Dval(Dspec, xvals):
    v=Q(1)
    for k,p in Dspec.items():
        v*=e_k(k,xvals)**p
    return v

def degD(Dspec):
    return sum(k*p for k,p in Dspec.items())

# ---------- collect points ----------
def collect_points(n, grid, target=240):
    pts=[]; seen=set()
    for combo in itertools.product(grid, repeat=n-2):
        free=[Q(c) for c in combo]
        try:
            A,kL,wL=amp_two_minus(n,free)
        except Exception:
            continue
        x=tuple(wL[2:])
        key=tuple(sorted(x))
        if key in seen: continue
        # avoid degenerate zero plus-freqs / zero e-values
        if any(xi==0 for xi in x): continue
        seen.add(key); pts.append((x,A.im))
        if len(pts)>=target: break
    return pts

def fit_with_D(n, pts, Dspec):
    m=n-2
    dN=2*(n-2)+degD(Dspec)
    lams=partitions_into_parts(dN,m)
    nb=len(lams)
    if len(pts) < nb+10:
        return ('few',nb,None)
    allrows=[]; rhs=[]
    for (x,Aim) in pts:
        D=Dval(Dspec,x)
        allrows.append([msym(lam,x) for lam in lams])
        rhs.append(Aim*D)
    sol,sub=pick_and_solve(allrows,rhs,nb)
    if sol is None:
        return ('singular',nb,None)
    # verify all
    bad=0
    for (x,Aim) in pts:
        D=Dval(Dspec,x)
        N=Aim*D
        val=sum(sol[j]*msym(lams[j],x) for j in range(nb))
        if val!=N: bad+=1
    coeffs={lams[j]:sol[j] for j in range(nb) if sol[j]!=0}
    return ('ok' if bad==0 else f'fail({bad}/{len(pts)})', nb, coeffs)

if __name__=="__main__":
    n=int(sys.argv[1]) if len(sys.argv)>1 else 5
    grid=[Q(1),Q(2),Q(3),Q(5,2),Q(7,2),Q(4),Q(5),Q(3,2),Q(7,3),Q(11,5),Q(-1),Q(-2),Q(6),Q(-3),Q(8,3)]
    pts=collect_points(n,grid)
    print(f"n={n}: {len(pts)} points",flush=True)
    cands=[{},{2:1},{3:1},{2:1,3:1},{3:2},{2:2},{2:1,3:2},{2:2,3:1},{3:3},{2:1,3:3},{2:3}]
    if n>=6:
        cands += [{4:1},{2:1,4:1},{3:1,4:1},{2:1,3:1,4:1},{4:2},{3:2,4:1},{2:1,3:1,4:2}]
    for D in cands:
        st,nb,info=fit_with_D(n,pts,D)
        print(f"  D(e_k powers)={D} degD={degD(D)} basis={nb} -> {st}",flush=True)
        if st=='ok':
            for lam,c in sorted(info.items()):
                print(f"      m_{lam}: {c}",flush=True)
