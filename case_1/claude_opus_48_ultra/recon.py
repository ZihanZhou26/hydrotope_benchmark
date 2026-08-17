"""Reconstruct A_n as N/D with general SYMMETRIC polynomials N,D in plus-freqs.
Homogeneous linear algebra: A*D - N = 0 over many exact points. Find minimal deg D."""
from bg import amp_two_minus
from fractions import Fraction as Q
from itertools import product as iproduct, permutations, combinations
from functools import lru_cache
import sys, itertools

@lru_cache(maxsize=None)
def parts(d, maxparts):
    res=[]
    def rec(rem,maxp,cur):
        if rem==0: res.append(tuple(cur)); return
        if len(cur)==maxparts: return
        for p in range(min(maxp,rem),0,-1):
            rec(rem-p,p,cur+[p])
    rec(d,d,[]); return res

@lru_cache(maxsize=None)
def dperms(exps):
    return tuple(set(permutations(exps)))

def msym(lam, xvals):
    m=len(xvals); exps=tuple(list(lam)+[0]*(m-len(lam))); tot=Q(0)
    for perm in dperms(exps):
        t=Q(1)
        for xi,e in zip(xvals,perm):
            if e: t*=xi**e
        tot+=t
    return tot

def collect(n, grid, target=400):
    pts=[]; seen=set()
    for combo in itertools.product(grid, repeat=n-2):
        free=[Q(c) for c in combo]
        try: A,kL,wL=amp_two_minus(n,free)
        except Exception: continue
        x=tuple(wL[2:]); key=tuple(sorted(x))
        if key in seen: continue
        if any(xi==0 for xi in x): continue
        seen.add(key); pts.append((x,A.im))
        if len(pts)>=target: break
    return pts

def rref_nullspace(M):
    """M: list of rows (lists of Q). Return list of nullspace basis vectors (lists of Q)."""
    M=[row[:] for row in M]
    rows=len(M); cols=len(M[0])
    pivots=[]; r=0
    for c in range(cols):
        piv=None
        for rr in range(r,rows):
            if M[rr][c]!=0: piv=rr;break
        if piv is None: continue
        M[r],M[piv]=M[piv],M[r]
        pv=M[r][c]; M[r]=[a/pv for a in M[r]]
        for rr in range(rows):
            if rr!=r and M[rr][c]!=0:
                f=M[rr][c]; M[rr]=[a-f*b for a,b in zip(M[rr],M[r])]
        pivots.append(c); r+=1
        if r==rows: break
    pivset=set(pivots)
    free=[c for c in range(cols) if c not in pivset]
    basis=[]
    for fc in free:
        vec=[Q(0)]*cols; vec[fc]=Q(1)
        for ri,pc in enumerate(pivots):
            vec[pc]=-M[ri][fc]
        basis.append(vec)
    return basis, pivots

def reconstruct(n, pts, maxdD=12):
    m=n-2; dA=2*(n-2)
    for dD in range(0, maxdD+1, 1):
        DB=parts(dD, m); NB=parts(dD+dA, m)
        nv=len(DB)+len(NB)
        if len(pts) < nv+5:
            print(f"  dD={dD}: need {nv} vars, have {len(pts)} pts -> skip"); continue
        rows=[]
        for (x,Aim) in pts:
            row=[]
            # D-part coeffs: A*DB_j(x)
            for lam in DB: row.append(Aim*msym(lam,x))
            # N-part coeffs: -NB_i(x)
            for lam in NB: row.append(-msym(lam,x))
            rows.append(row)
        basis,piv=rref_nullspace(rows)
        dim=len(basis)
        print(f"  dD={dD}: vars={nv} (|D|={len(DB)},|N|={len(NB)}) nullspace dim={dim}",flush=True)
        if dim>=1:
            return dD, DB, NB, basis
    return None

if __name__=="__main__":
    n=int(sys.argv[1]) if len(sys.argv)>1 else 5
    grid=[Q(1),Q(2),Q(3),Q(5,2),Q(7,2),Q(4),Q(5),Q(3,2),Q(7,3),Q(11,5),Q(-1),Q(-2),Q(6),Q(-3),Q(8,3),Q(9,2),Q(-5,2)]
    pts=collect(n,grid, target=400)
    print(f"n={n}: {len(pts)} points",flush=True)
    res=reconstruct(n,pts)
    if res:
        dD,DB,NB,basis=res
        print(f"\n>>> minimal denominator degree dD={dD}, nullspace dim={len(basis)}")
        vec=basis[0]
        Dc=vec[:len(DB)]; Nc=vec[len(DB):]
        print("Denominator D (m_lambda coeffs):")
        for lam,c in zip(DB,Dc):
            if c!=0: print(f"   D m_{lam}: {c}")
        print("Numerator N (m_lambda coeffs):")
        for lam,c in zip(NB,Nc):
            if c!=0: print(f"   N m_{lam}: {c}")
