#!/usr/bin/env python3
"""ROUND 6 global fit: does N_6 = base + single(1=1) + pair(1=1) + triple(1=1) + (1=2)?

Work with M = N - corr12 (subtract the known (1=2) part; M is a pure (1=1) box spline).
Test whether M is spanned by:
  - base B: 12 G-symmetric odd deg-11 invariant classes
  - single (1=1): orbit-sum_G  (k_03)_+ * eval_h(m,'P')         [m: 125 deg-9 mode-P templates]
  - pair   (1=1): orbit-sum_G  (k_03)_+(k_14)_+ * mon(m)         [m: deg-7 monomials, greedy]
  - triple (1=1): orbit-sum_G  (k_03)_+(k_14)_+(k_25)_+ * mon(m) [m: deg-5 monomials, greedy]
k_03=b3-a0, k_14=b4-a1, k_25=b5-a2 (difference branch). (x)_+=max(x,0).
EXACT relu (sign from Fraction), arithmetic mod P=2^61-1. Greedy: keep rank-increasing cols.
"""
from fractions import Fraction as F
import itertools, random, sys
import chambers_n6 as cn, r5_group as Gp, r5_basis as Bm, r5_global as G2, r5_corr as C, inv, fastbg as FB
PR=2**61-1
def minv(a): return pow(a%PR,PR-2,PR)
def fm(fr): return (fr.numerator%PR)*minv(fr.denominator%PR)%PR
G=Gp.full_group()
M_=[0,1,2]; P_=[3,4,5]
baseC=G2.base_classes()
gdeg=(1,1,1,2,1,2)
monsP,_=Bm.independent_subset(Bm.hinv_mons(9,gdeg),'P')   # 125 single-(1=1) templates

def gen_data(npts, seed):
    rnd=random.Random(seed); pend=[]; out=[]
    while len(out)<npts:
        free=[F(rnd.randint(-95,95),10) for _ in range(4)]
        if 0 in free: continue
        o=cn.solve_squares(free)
        if o is None or any(w==0 for w in o): continue
        pend.append((free,o))
        if len(pend)>=80 or len(out)+len(pend)>=npts:
            res=FB.batch_onshell([(6,fr,[-1,-1,-1,1,1,1]) for (fr,_) in pend])
            for (fr,o),r in zip(pend,res):
                if r is None: continue
                e=inv.invariants(o); Nv=F(r[1]*(e[2]+e[3]),32); Mv=Nv-C.corr12(o)
                out.append((o,Mv))
            pend=[]
    return out

def precompute(o):
    """per point: list over G of (omegas_modp[6], reluk03, reluk14, reluk25) all mod p."""
    rows=[]
    for perm in G:
        ro=Gp.apply_perm(perm,o)
        om=[fm(F(x)) for x in ro]
        k03=ro[3]**2-ro[0]**2; k14=ro[4]**2-ro[1]**2; k25=ro[5]**2-ro[2]**2
        r03=fm(k03) if k03>0 else 0
        r14=fm(k14) if k14>0 else 0
        r25=fm(k25) if k25>0 else 0
        rows.append((om,r03,r14,r25))
    return rows

def mon_modp(e, om):
    v=1
    for i in range(6):
        if e[i]: v=v*pow(om[i],e[i],PR)%PR
    return v

def col_base(cl,o): return fm(G2.eval_base(cl,o))
def col_single(m,gp,o):
    s=0
    for (om,r03,r14,r25) in gp:
        if r03: s=(s+r03*fm(Bm.eval_h(m,[F(x) for x in []] or _ro(om), 'P')))%PR  # placeholder
    return s

def _ro(om): return om  # unused

# eval_h needs exact omegas; precompute exact relabeled omegas too
def precompute_exact(o):
    return [ [F(x) for x in Gp.apply_perm(perm,o)] for perm in G]

def col_single_exact(m, exrows, gp):
    s=0
    for k in range(len(G)):
        r03=gp[k][1]
        if r03: s=(s+r03*fm(Bm.eval_h(m, exrows[k], 'P')))%PR
    return s
def col_pair(e, gp):
    s=0
    for (om,r03,r14,r25) in gp:
        if r03 and r14: s=(s+r03*r14*mon_modp(e,om))%PR
    return s
def col_triple(e, gp):
    s=0
    for (om,r03,r14,r25) in gp:
        if r03 and r14 and r25: s=(s+r03*r14*r25*mon_modp(e,om))%PR
    return s

def oddmons(deg):
    out=[]
    for e in itertools.product(range(deg+1),repeat=6):
        if sum(e)==deg: out.append(e)
    return out

if __name__=="__main__":
    npts=int(sys.argv[1]) if len(sys.argv)>1 else 300
    print("generating data...",flush=True)
    data=gen_data(npts, seed=7)
    print("data:",len(data),flush=True)
    GP=[precompute(o) for (o,_) in data]
    EX=[precompute_exact(o) for (o,_) in data]
    rhs=[fm(mv) for (_,mv) in data]
    nrow=len(data)

    # build columns level by level, GREEDY (keep rank-increasing)
    cols=[]; labels=[]
    # working RREF state: list of (pivot_col_index_in_current_matrix, normalized_row)
    # We'll do incremental rank with a reduced row-echelon over the GROWING column set.
    # Simpler: collect all candidate columns per level, then one big RREF for rank/consistency,
    # but to extract we want a basis. Do greedy via maintaining reduced basis of column vectors.
    basis=[]   # each: list length nrow (a column vector mod p), reduced
    pivrow=[]  # pivot row index for each basis vector
    def reduce_vec(v):
        v=v[:]
        for bi,pr_ in zip(basis,pivrow):
            if v[pr_]:
                f=v[pr_]
                v=[(v[i]-f*bi[i])%PR for i in range(nrow)]
        return v
    def try_add(v,label):
        rv=reduce_vec(v)
        pr_=next((i for i in range(nrow) if rv[i]),None)
        if pr_ is None: return False
        iv=minv(rv[pr_]); rv=[(x*iv)%PR for x in rv]
        # back-reduce existing
        for k in range(len(basis)):
            if basis[k][pr_]:
                f=basis[k][pr_]; basis[k]=[(basis[k][i]-f*rv[i])%PR for i in range(nrow)]
        basis.append(rv); pivrow.append(pr_); cols.append(v); labels.append(label)
        return True

    # base
    for cl in baseC: try_add([col_base(cl,data[r][0]) for r in range(nrow)], ('base',cl))
    print("after base: rank",len(basis),flush=True)
    # single (1=1)
    for m in monsP: try_add([col_single_exact(m,EX[r],GP[r]) for r in range(nrow)], ('single',m))
    print("after single(1=1): rank",len(basis),flush=True)
    # pair (1=1)
    addp=0
    for e in oddmons(7):
        if try_add([col_pair(e,GP[r]) for r in range(nrow)], ('pair',e)): addp+=1
    print(f"after pair(1=1): rank {len(basis)} (+{addp})",flush=True)
    # triple (1=1)
    addt=0
    for e in oddmons(5):
        if try_add([col_triple(e,GP[r]) for r in range(nrow)], ('triple',e)): addt+=1
    print(f"after triple(1=1): rank {len(basis)} (+{addt})",flush=True)

    # consistency: is rhs in span? reduce rhs against basis
    rv=reduce_vec(rhs[:])
    consistent=all(x==0 for x in rv)
    print("\nTOTAL columns(rank):",len(basis),"  npts:",nrow,flush=True)
    print("M in span (CONSISTENT):",consistent,flush=True)
    # held-out: fit on first 80%, predict last 20%
    import pickle
    with open("r6_fit_labels.pkl","wb") as f: pickle.dump(labels,f)
