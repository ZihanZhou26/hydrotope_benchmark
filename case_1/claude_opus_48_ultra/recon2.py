"""Group sector points by chamber signature (signs of k_S over all multi-leg S),
then reconstruct A_n = N/D (general symmetric polys in plus-freqs) within each chamber."""
from bg import amp_two_minus, two_minus_sigma
from fractions import Fraction as Q
from recon import parts, msym, rref_nullspace
from itertools import product as iproduct, combinations
import itertools, sys

def chamber_sig(kL):
    n=len(kL)
    sig=[]
    for r in range(2,n):  # multi-leg subsets size 2..n-1
        for S in combinations(range(n), r):
            ks=sum(kL[i] for i in S)
            sig.append(1 if ks>0 else (-1 if ks<0 else 0))
    return tuple(sig)

def collect_by_chamber(n, grid, target=4000):
    groups={}
    for combo in itertools.product(grid, repeat=n-2):
        free=[Q(c) for c in combo]
        try: A,kL,wL=amp_two_minus(n,free)
        except Exception: continue
        x=tuple(wL[2:])
        if any(xi==0 for xi in x): continue
        if 0 in chamber_sig(kL):  # on a chamber wall; skip
            continue
        sig=chamber_sig(kL)
        key=tuple(sorted(x))
        g=groups.setdefault(sig, {})
        if key in g: continue
        g[key]=(x,A.im)
        if sum(len(v) for v in groups.values())>=target: break
    return groups

def reconstruct(n, pts, maxdD=10, verbose=True):
    m=n-2; dA=2*(n-2)
    for dD in range(0, maxdD+1):
        DB=parts(dD, m); NB=parts(dD+dA, m)
        nv=len(DB)+len(NB)
        if len(pts) < nv+5:
            if verbose: print(f"    dD={dD}: need {nv}, have {len(pts)} -> skip")
            continue
        rows=[[Aim*msym(l,x) for l in DB]+[-msym(l,x) for l in NB] for (x,Aim) in pts]
        basis,_=rref_nullspace(rows)
        if verbose: print(f"    dD={dD}: vars={nv} nullspace dim={len(basis)}",flush=True)
        if len(basis)>=1:
            return dD, DB, NB, basis
    return None

if __name__=="__main__":
    n=int(sys.argv[1]) if len(sys.argv)>1 else 5
    grid=[Q(1),Q(2),Q(3),Q(5,2),Q(7,2),Q(4),Q(5),Q(3,2),Q(7,3),Q(11,5),Q(-1),Q(-2),Q(6),
          Q(-3),Q(8,3),Q(9,2),Q(-5,2),Q(13,3),Q(-4),Q(5,3)]
    groups=collect_by_chamber(n,grid)
    sizes=sorted(((len(v),sig) for sig,v in groups.items()), reverse=True)
    print(f"n={n}: {len(groups)} chambers; sizes: {[s for s,_ in sizes[:8]]}",flush=True)
    # reconstruct in the largest few chambers
    for cnt,sig in sizes[:3]:
        if cnt < 30: continue
        pts=list(groups[sig].values())
        print(f"\n--- chamber size {cnt} ---",flush=True)
        res=reconstruct(n, pts, maxdD=8)
        if res:
            dD,DB,NB,basis=res
            print(f"  >>> dD={dD}, nullspace dim={len(basis)}")
            vec=basis[0]; Dc=vec[:len(DB)]; Nc=vec[len(DB):]
            print("  D coeffs:")
            for lam,c in zip(DB,Dc):
                if c!=0: print(f"     D m_{lam}: {c}")
            print("  N coeffs:")
            for lam,c in zip(NB,Nc):
                if c!=0: print(f"     N m_{lam}: {c}")
