"""
CHECK B -- is S = R_spline - R_Q a genuine dual-S3 degree-8 spline over the 9
pair walls q_{mp}=0 only?

B1: S is dual-S3-symmetric and degree-8 homogeneous.
B2: within a fixed q-sign chamber, S is a SINGLE polynomial in the on-shell
    dual-symmetric degree-8 basis {u^i v^j a^k b^l : i+2j+3k+3l=8} (17 dim),
    verified by exact rational fit + holdouts.
B3: the per-chamber polynomials DIFFER between chambers (=> genuine spline).

Invariants (on shell e1p=-u, e2p=v):
  u = w0+w1+w2   (deg 1)      a = w0*w1*w2   (deg 3, e3 minus)
  v = w0w1+w0w2+w1w2 (deg 2)  b = w3*w4*w5   (deg 3, e3 plus)
"""
from fractions import Fraction as Fr
from itertools import product
import random
import r6_core as C
from r5_core import solve_onshell

M, P = [0,1,2],[3,4,5]

def invariants(om):
    u = om[0]+om[1]+om[2]
    v = om[0]*om[1]+om[0]*om[2]+om[1]*om[2]
    a = om[0]*om[1]*om[2]
    b = om[3]*om[4]*om[5]
    return u,v,a,b

def basis_exps():
    out=[]
    for i,j,k,l in product(range(9),repeat=4):
        if i+2*j+3*k+3*l==8:
            out.append((i,j,k,l))
    return out

BEXP = basis_exps()   # 17

def basis_row(om):
    u,v,a,b = invariants(om)
    return [ (u**i)*(v**j)*(a**k)*(b**l) for (i,j,k,l) in BEXP ]

# ---- exact rational linear algebra ----
def rref_solve(A, y):
    """Solve A x = y over Fractions. Return (rankA, rank_aug, solution_or_None)."""
    A=[row[:] for row in A]; y=y[:]
    m=len(A); n=len(A[0])
    # augmented
    aug=[A[i]+[y[i]] for i in range(m)]
    row=0; pivots=[]
    for col in range(n):
        piv=None
        for r in range(row,m):
            if aug[r][col]!=0: piv=r; break
        if piv is None: continue
        aug[row],aug[piv]=aug[piv],aug[row]
        pv=aug[row][col]
        aug[row]=[x/pv for x in aug[row]]
        for r in range(m):
            if r!=row and aug[r][col]!=0:
                f=aug[r][col]
                aug[r]=[aug[r][c]-f*aug[row][c] for c in range(n+1)]
        pivots.append(col); row+=1
        if row==m: break
    rankA=len(pivots)
    # rank of augmented: count nonzero rows overall
    rank_aug=0
    for r in range(m):
        if any(aug[r][c]!=0 for c in range(n+1)):
            rank_aug+=1
    # consistency: any row with all-zero A part but nonzero y => inconsistent
    consistent=True
    for r in range(m):
        if all(aug[r][c]==0 for c in range(n)) and aug[r][n]!=0:
            consistent=False; break
    sol=None
    if consistent and rankA==n:
        sol=[Fr(0)]*n
        # back-substitute from pivots
        for idx,col in enumerate(pivots):
            sol[col]=aug[idx][n]
    return rankA, (rankA if consistent else rankA+1), sol, consistent

def rand_onshell(rng):
    while True:
        fr=[Fr(rng.randint(-40,40), rng.randint(1,7)) for _ in range(4)]
        if len({abs(x) for x in fr})<4: continue
        try: om=solve_onshell(*fr)
        except ZeroDivisionError: continue
        if any(x==0 for x in om): continue
        # nondegenerate magnitudes
        mags={abs(x) for x in om}
        if len(mags)<6: continue
        return [Fr(x) for x in om]

def qsig(om):
    return tuple(1 if (om[p]**2-om[m]**2)>0 else -1 for m in M for p in P)

def main():
    import json
    rng=random.Random(20260726)
    buckets={}
    N=900
    for _ in range(N):
        om=rand_onshell(rng)
        try:
            s=C.S_resid(om)
        except Exception:
            continue
        key=qsig(om)
        buckets.setdefault(key,[]).append((om,s))
    # B2: fit each big-enough bucket
    fitted={}
    report=[]
    big=sorted(buckets.items(), key=lambda kv:-len(kv[1]))
    ncons=0; ntested=0
    for key,pts in big:
        if len(pts) < 30:   # need > 17 + holdouts
            continue
        fitpts=pts[:20]; holds=pts[20:]
        A=[basis_row(om) for om,_ in fitpts]
        yv=[s for _,s in fitpts]
        rankA, rankAug, sol, consistent = rref_solve(A,yv)
        ntested+=1
        if sol is None:
            report.append((key,len(pts),rankA,rankAug,consistent,"NO_UNIQUE_SOL"))
            continue
        # holdout check
        maxr=Fr(0)
        for om,s in holds:
            val=sum(c*b for c,b in zip(sol,basis_row(om)))
            r=abs(val-s)
            if r>maxr: maxr=r
        ok = (maxr==0)
        if ok: ncons+=1
        fitted[key]=sol
        report.append((key,len(pts),rankA,rankAug,consistent,"holdout_max="+str(maxr)))
    print(f"q-sign chambers with >=30 pts fitted: {ntested}")
    print(f"  chambers where S is a SINGLE dual-sym deg-8 poly (holdouts exact 0): {ncons}/{ntested}")
    qs=[ "".join('+' if x>0 else '-' for x in k) for k,_ in big if len(_)>=30]
    print(f"  chamber q-signatures: {qs[:ntested]}")
    for r in report:
        ksig="".join('+' if x>0 else '-' for x in r[0])
        print(f"   {ksig}  n={r[1]:3d}  rankA={r[2]}  rankAug={r[3]}  {r[5]}")
    # B3: are the fitted chamber-polynomials distinct?
    distinct = len({tuple(v) for v in fitted.values()})
    print(f"  distinct per-chamber polynomials among fitted: {distinct} (spline if >1)")
    json.dump({"ntested":ntested,"nconsistent":ncons,"distinct_polys":distinct,
               "report":[[('+' if x>0 else '-') for x in r[0]]+[r[1],r[2],r[3],r[5]] for r in report]},
              open("../data/r6_checkB.json","w"),indent=1)

if __name__=="__main__":
    main()
