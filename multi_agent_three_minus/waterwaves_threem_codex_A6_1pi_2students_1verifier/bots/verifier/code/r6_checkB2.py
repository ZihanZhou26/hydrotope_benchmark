"""
Pinpoint the chamber granularity at which S = R_spline - R_Q becomes a single
dual-S3 degree-8 polynomial. Also directly verify S is dual-symmetric and
degree-8 homogeneous.
"""
from fractions import Fraction as Fr
from itertools import combinations, permutations
import random
import r6_core as C
import r6_checkB as B
from r5_core import solve_onshell

M,P=[0,1,2],[3,4,5]

def qsig(om):
    return tuple(1 if (om[p]**2-om[m]**2)>0 else -1 for m in M for p in P)
def Qsig(om):
    return tuple(1 if (om[p]**2+om[q]**2-om[m]**2)>0 else -1 for m in M for (p,q) in combinations(P,2))
def magword(om):
    # sort legs by |omega|, record the momentum-sign sequence (question.md 8-word selector)
    order=sorted(range(6), key=lambda i:abs(om[i]))
    return tuple(C.SIGMA[i] for i in order)

def dual_symmetry_and_degree():
    rng=random.Random(3)
    om=B.rand_onshell(rng)
    s0=C.S_resid(om)
    # permute minus legs and plus legs
    bad=0
    for pm in permutations([0,1,2]):
        for pp in permutations([3,4,5]):
            om2=[om[pm[0]],om[pm[1]],om[pm[2]],om[3+ (pp[0]-3)],om[3+(pp[1]-3)],om[3+(pp[2]-3)]]
            if C.S_resid(om2)!=s0: bad+=1
    # degree-8 homogeneity: scale omega by lambda -> S scales by lambda^8
    lam=Fr(3,2)
    oms=[w*lam for w in om]
    s_scaled=C.S_resid(oms)
    homog = (s_scaled == s0*lam**8)
    return bad, homog

def fit_bucket(pts):
    fitpts=pts[:20]; holds=pts[20:]
    A=[B.basis_row(om) for om,_ in fitpts]; y=[s for _,s in fitpts]
    rk,ra,sol,cons=B.rref_solve(A,y)
    if sol is None: return rk,ra,cons,None
    maxr=Fr(0)
    for om,s in holds:
        r=abs(sum(c*b for c,b in zip(sol,B.basis_row(om)))-s)
        if r>maxr: maxr=r
    return rk,ra,cons,maxr

_POOL=None
def get_pool(n=800):
    global _POOL
    if _POOL is not None: return _POOL
    rng=random.Random(20260726)
    pool=[]
    for _ in range(n):
        om=B.rand_onshell(rng)
        try: s=C.S_resid(om)
        except Exception: continue
        pool.append((om,s))
    _POOL=pool
    return pool

def run(keyfn, label, minpts=30):
    buckets={}
    for om,s in get_pool():
        buckets.setdefault(keyfn(om),[]).append((om,s))
    big=sorted(buckets.items(),key=lambda kv:-len(kv[1]))
    ntested=ncons=0
    lines=[]
    for key,pts in big:
        if len(pts)<minpts: continue
        rk,ra,cons,maxr=fit_bucket(pts)
        ntested+=1
        ok=(maxr==0) if maxr is not None else False
        if ok: ncons+=1
        lines.append((len(pts),rk,ra,str(maxr)))
    print(f"[{label}] buckets(>= {minpts}): {ntested} ; S is single dual-sym deg8 poly: {ncons}/{ntested}")
    for l in lines[:8]:
        print(f"     n={l[0]:3d} rankA={l[1]} rankAug={l[2]} holdout_max={l[3]}")
    return ntested,ncons

if __name__=="__main__":
    bad,homog=dual_symmetry_and_degree()
    print(f"S dual-symmetry violations over 36 perms: {bad} (0 = symmetric)")
    print(f"S degree-8 homogeneous under scaling: {homog}")
    print("-"*50)
    run(lambda om:qsig(om), "q-signs only")
    run(lambda om:(qsig(om),Qsig(om)), "q+Q signs")
    run(lambda om:(qsig(om),Qsig(om),magword(om)), "q+Q signs + magword")
