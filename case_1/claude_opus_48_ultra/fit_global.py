"""Test the hint's global ansatz: A_n = N(omega) / prod_channels (omega_S^2 - |k_S|),
with N a SINGLE symmetric polynomial valid across ALL chambers.
Channels: subsets S with 1 in S, 2<=|S|<=n-2 (one per complementary pair)."""
from bg import amp_two_minus
from fractions import Fraction as Q
from itertools import combinations, permutations, product as iproduct
from functools import lru_cache
import itertools, sys
from recon import rref_nullspace  # not used; we solve inhomogeneous

def solve_exact(rows, rhs):
    n=len(rows); A=[list(r)+[v] for r,v in zip(rows,rhs)]
    for c in range(n):
        piv=None
        for r in range(c,n):
            if A[r][c]!=0: piv=r;break
        if piv is None: return None
        A[c],A[piv]=A[piv],A[c]; pv=A[c][c]; A[c]=[a/pv for a in A[c]]
        for r in range(n):
            if r!=c and A[r][c]!=0:
                f=A[r][c]; A[r]=[a-f*b for a,b in zip(A[r],A[c])]
    return [A[i][n] for i in range(n)]

def pick_and_solve(allrows, rhs, nb):
    import random
    N=len(allrows); rng=random.Random(7)
    tries=[list(range(nb))]+[rng.sample(range(N),nb) for _ in range(60)]
    for sub in tries:
        sol=solve_exact([[Q(x) for x in allrows[i]] for i in sub],[Q(rhs[i]) for i in sub])
        if sol is not None: return sol,sub
    return None,None

def channels(n):
    reps=[]
    for r in range(2,n-1):  # |S| from 2 to n-2
        for S in combinations(range(1,n), r-1):  # other elements from {1..n-1} (0-based 1..n-1)
            full=(0,)+S  # include leg 0 (=leg1)
            reps.append(full)
    return reps

def Dval(n, w, sig, reps):
    # w: tuple freqs (0-based); k_i = sig_i*w_i^2 ; factor = wS^2 - |kS|
    D=Q(1)
    for S in reps:
        wS=sum(w[i] for i in S)
        kS=sum(sig[i]*w[i]**2 for i in S)
        D*= wS*wS - (kS if kS>=0 else -kS)
    return D

# symmetric basis: sym in (w1,w2) [minus] x sym in (w3..wn) [plus]
@lru_cache(maxsize=None)
def parts_le(d, maxparts):
    res=[]
    def rec(rem,maxp,cur):
        if rem==0: res.append(tuple(cur)); return
        if len(cur)==maxparts: return
        for p in range(min(maxp,rem),0,-1): rec(rem-p,p,cur+[p])
    rec(d,d,[]); return res

@lru_cache(maxsize=None)
def dperms(exps): return tuple(set(permutations(exps)))

def msym_vars(lam, xs):
    m=len(xs); exps=tuple(list(lam)+[0]*(m-len(lam))); tot=Q(0)
    for perm in dperms(exps):
        t=Q(1)
        for xi,e in zip(xs,perm):
            if e: t*=xi**e
        tot+=t
    return tot

def basis_eval(n, w, dN):
    # return list of basis monomial values: sym(w1,w2)_{d1} * sym(plus)_{d2}, d1+d2=dN
    minus=w[:2]; plus=w[2:]
    vals=[]; labels=[]
    for d1 in range(0,dN+1):
        d2=dN-d1
        for lam1 in parts_le(d1,2) if d1>0 else [()]:
            v1=msym_vars(lam1, minus) if d1>0 else Q(1)
            for lam2 in parts_le(d2,n-2) if d2>0 else [()]:
                v2=msym_vars(lam2, plus) if d2>0 else Q(1)
                vals.append(v1*v2); labels.append((lam1,lam2))
    return vals, labels

def collect(n, grid, target=600):
    pts=[]; seen=set()
    for combo in itertools.product(grid, repeat=n-2):
        free=[Q(c) for c in combo]
        try: A,kL,wL=amp_two_minus(n,free)
        except Exception: continue
        x=tuple(wL[2:])
        if any(xi==0 for xi in x): continue
        key=tuple(wL)
        if key in seen: continue
        seen.add(key); pts.append((tuple(wL),A.im))
        if len(pts)>=target: break
    return pts

if __name__=="__main__":
    n=int(sys.argv[1]) if len(sys.argv)>1 else 5
    sig=tuple([-1,-1]+[1]*(n-2))
    reps=channels(n)
    degD=2*len(reps); dN=2*(n-2)+degD
    print(f"n={n}: {len(reps)} channels, degD={degD}, degN={dN}",flush=True)
    grid=[Q(1),Q(3,2),Q(2),Q(5,2),Q(3),Q(7,2),Q(4),Q(9,2),Q(5),Q(-1),Q(-2),Q(-3),
          Q(1,2),Q(5,4),Q(11,4),Q(-3,2),Q(-5,2),Q(13,4),Q(6),Q(-4)]
    pts=collect(n,grid,target=700)
    # basis size
    _,labels=basis_eval(n, pts[0][0], dN)
    nb=len(labels)
    print(f"collected {len(pts)} pts, symmetric basis size {nb}",flush=True)
    if len(pts)<nb+10:
        print("NOT ENOUGH POINTS"); sys.exit()
    allrows=[]; rhs=[]
    for (w,Aim) in pts:
        D=Dval(n,w,sig,reps)
        vals,_=basis_eval(n,w,dN)
        allrows.append(vals); rhs.append(Aim*D)
    sol,sub=pick_and_solve(allrows,rhs,nb)
    if sol is None: print("singular"); sys.exit()
    bad=0
    for (w,Aim) in pts:
        D=Dval(n,w,sig,reps); vals,_=basis_eval(n,w,dN)
        if sum(sol[j]*vals[j] for j in range(nb))!=Aim*D: bad+=1
    print(f"FIT: {'CONSISTENT (single polynomial N exists!)' if bad==0 else f'INCONSISTENT ({bad}/{len(pts)} bad)'}",flush=True)
    if bad==0:
        nz=[(labels[j],sol[j]) for j in range(nb) if sol[j]!=0]
        print(f"N has {len(nz)} nonzero terms")
