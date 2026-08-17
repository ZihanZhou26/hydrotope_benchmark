#!/usr/bin/env python3
"""Extract EXACT coefficients for N_6 = B + single(1=1) + pair(1=1) + (1=2 corr Q),
using the rank-100 column basis found by r6_fit.py (labels in r6_fit_labels.pkl).
Solve mod P, rational-reconstruct, then VERIFY EXACTLY against ./bg.

  N_6 = corr12(Q) + sum_k coeff_k * column_k(omega)
  column_k = base class  | orbit-sum_G (k03)_+ eval_h(m,'P')  | orbit-sum_G (k03)_+(k14)_+ mon(e)
  A_6 = i * 2^5 g^-3 * N_6 / (e3m+e3p)    (g=1)
"""
from fractions import Fraction as F
import itertools, random, pickle, sys
import chambers_n6 as cn, r5_group as Gp, r5_basis as Bm, r5_global as G2, r5_corr as C, inv, fastbg as FB, harness as h
PR=2**61-1
def minv(a): return pow(a%PR,PR-2,PR)
def fm(fr): return (fr.numerator%PR)*minv(fr.denominator%PR)%PR
G=Gp.full_group()

def ratrecon(a, N=PR):
    """rational reconstruction of residue a mod N -> Fraction p/q (q>0), small."""
    a%=N
    if a==0: return F(0)
    r0,r1=N,a; s0,s1=0,1
    bound=1<<31
    while r1>bound:
        q=r0//r1; r0,r1=r1,r0-q*r1; s0,s1=s1,s0-q*s1
    p=r1; qd=s1
    if qd<0: p,qd=-p,-qd
    if qd==0: return None
    if (p*minv(qd))%N!=a: return None
    return F(p,qd)

# ---- column evaluators (EXACT Fraction) ----
def relabel_rows(o):
    return [[F(x) for x in Gp.apply_perm(perm,o)] for perm in G]
def relu(fr): return fr if fr>0 else F(0)
def col_base_exact(cl,o): return F(G2.eval_base(cl,o))
def col_single_ex(m, rows):
    s=F(0)
    for ro in rows:
        k=ro[3]**2-ro[0]**2
        if k>0: s+= k*Bm.eval_h(m,ro,'P')
    return s
def col_pair_ex(e, rows):
    s=F(0)
    for ro in rows:
        k03=ro[3]**2-ro[0]**2; k14=ro[4]**2-ro[1]**2
        if k03>0 and k14>0:
            v=k03*k14
            for i in range(6):
                if e[i]: v*=ro[i]**e[i]
            s+=v
    return s
def eval_col(label, o, rows):
    typ=label[0]
    if typ=='base': return col_base_exact(label[1],o)
    if typ=='single': return col_single_ex(label[1],rows)
    if typ=='pair': return col_pair_ex(label[1],rows)
    raise ValueError(typ)

def Nfit(o, rows, labels, coeffs):
    return sum(c*eval_col(l,o,rows) for l,c in zip(labels,coeffs))

if __name__=="__main__":
    labels=pickle.load(open("r6_fit_labels.pkl","rb"))
    ncol=len(labels); print("columns:",ncol,flush=True)
    # gen data > ncol
    rnd=random.Random(123); pend=[]; data=[]
    target=ncol+80
    while len(data)<target:
        free=[F(rnd.randint(-95,95),10) for _ in range(4)]
        if 0 in free: continue
        o=cn.solve_squares(free)
        if o is None or any(w==0 for w in o): continue
        pend.append((free,o))
        if len(pend)>=80 or len(data)+len(pend)>=target:
            res=FB.batch_onshell([(6,fr,[-1,-1,-1,1,1,1]) for (fr,_) in pend])
            for (fr,o),r in zip(pend,res):
                if r is None: continue
                e=inv.invariants(o); Nv=F(r[1]*(e[2]+e[3]),32); Mv=Nv-C.corr12(o)
                data.append((o,Mv))
            pend=[]
    print("data:",len(data),flush=True)
    ROWS=[relabel_rows(o) for (o,_) in data]
    # build column matrix mod p
    Acols=[[fm(eval_col(l,data[r][0],ROWS[r])) for r in range(len(data))] for l in labels]
    rhs=[fm(mv) for (_,mv) in data]
    nrow=len(data)
    # transpose to rows x cols, solve square subsystem
    A=[[Acols[c][r] for c in range(ncol)] for r in range(nrow)]
    # gaussian elimination mod p to pick pivots & solve consistency
    Mx=[A[r][:]+[rhs[r]] for r in range(nrow)]
    piv=[]; rr=0
    for c in range(ncol):
        p=next((i for i in range(rr,nrow) if Mx[i][c]),None)
        if p is None: continue
        Mx[rr],Mx[p]=Mx[p],Mx[rr]; iv=minv(Mx[rr][c]); Mx[rr]=[(x*iv)%PR for x in Mx[rr]]
        for i in range(nrow):
            if i!=rr and Mx[i][c]:
                f=Mx[i][c]; Mx[i]=[(Mx[i][k]-f*Mx[rr][k])%PR for k in range(ncol+1)]
        piv.append(c); rr+=1
        if rr==nrow: break
    incons=any(Mx[i][ncol] and all(Mx[i][k]==0 for k in range(ncol)) for i in range(rr,nrow))
    print("rank",rr,"consistent(mod p):",not incons,flush=True)
    # coefficients at pivot columns
    sol={piv[i]:Mx[i][ncol] for i in range(len(piv))}
    coeffs=[sol.get(c,0) for c in range(ncol)]
    # rational reconstruct
    rcoef=[ratrecon(c) for c in coeffs]
    nbad=sum(1 for x in rcoef if x is None)
    print("coeffs rational-reconstructed:",ncol-nbad,"/",ncol,"  (None:",nbad,")",flush=True)
    if nbad==0:
        pickle.dump((labels,rcoef), open("r6_coeffs.pkl","wb"))
        print("saved r6_coeffs.pkl",flush=True)
    else:
        # keep modular for now
        pickle.dump((labels,coeffs,'modp'), open("r6_coeffs_modp.pkl","wb"))
        print("WARN: some coeffs not reconstructed; saved modular",flush=True)
    # quick EXACT verification at fresh points
    print("\n=== EXACT verification A_6 vs ./bg ===",flush=True)
    if nbad==0:
        rnd2=random.Random(999); nok=0; ntot=0
        for _ in range(14):
            free=[F(rnd2.randint(-90,90),10) for _ in range(4)]
            if 0 in free: continue
            o=cn.solve_squares(free)
            if o is None or any(w==0 for w in o): continue
            rows=relabel_rows(o)
            Nv=Nfit(o,rows,labels,rcoef)+C.corr12(o)
            e=inv.invariants(o); denom=e[2]+e[3]
            if denom==0: continue
            A6_im=F(32*Nv, denom)   # A_6 = i*32*N/(e3m+e3p); im coeff
            try: im_o,_,_=h.on_shell(free,[-1,-1,-1,1,1,1])
            except Exception: continue
            ntot+=1; ok=(A6_im==im_o); nok+=ok
            print(f"  free={[str(x) for x in free]}  match={ok}  resid={A6_im-im_o}",flush=True)
        print(f"\nEXACT: {nok}/{ntot} match",flush=True)
