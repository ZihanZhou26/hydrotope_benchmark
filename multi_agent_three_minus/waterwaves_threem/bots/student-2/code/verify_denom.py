#!/usr/bin/env python3
"""Check a candidate symmetric denominator D(omega) for A_6 (three-minus).

If candidate D contains the true denominator, then on ANY 1-D line held inside
ONE chamber, A_6(t)*D(t) is a POLYNOMIAL in t.  We test this by exact polynomial
interpolation at many SMALL rational nodes t (all inside one chamber -- verified
by requiring identical signs of every mixed k_S at every node): fit a degree-d
polynomial through d+1 nodes and require it to predict the remaining nodes
exactly.  Smallest d that works = degree of A_6*D; failure for all d up to a
bound => A_6*D still rational => candidate D is missing a factor.

Use several slices (vary different leg pairs, sumFree held constant) so different
factors of D become non-constant; collectively they pin D.
"""
from fractions import Fraction as Fr
from itertools import combinations
import sympy as sp
import harness as h

SIG = [-1,-1,-1,1,1,1]

def mixed_subsets():
    out=[]
    for r in range(1,6):
        for S in combinations(range(1,7), r):
            mns=[i for i in S if SIG[i-1]<0]; pls=[i for i in S if SIG[i-1]>0]
            if mns and pls: out.append(S)
    return out
MIXED = mixed_subsets()

def ksign(oms, S):
    w=[None]+[Fr(x) for x in oms]
    v=sum(Fr(SIG[i-1])*w[i]**2 for i in S)
    return 0 if v==0 else (1 if v>0 else -1)

def line_points(base, vary, ts):
    """base dict legs2..5; vary=(i,j) hold sumFree const (w_i+=t, w_j-=t)."""
    i,j=vary; out=[]
    for t in ts:
        free=[]
        for leg in (2,3,4,5):
            v=Fr(base[leg])
            if leg==i: v+=t
            if leg==j: v-=t
            free.append(v)
        out.append((t,free))
    return out

def slice_poly_degree(D, base, vary, label, dmax=70):
    # small DENSE nodes inside one chamber
    ts=[Fr(k,300) for k in range(1, 95)]   # t in (0.003,0.31): one chamber
    pts=line_points(base, vary, ts)
    data=[]; sigref=None
    for t,free in pts:
        try:
            oim,oms,_=h.on_shell(free, SIG)
        except Exception:
            continue
        sg=tuple(ksign(oms,S) for S in MIXED)
        if sigref is None: sigref=sg
        if sg!=sigref:
            continue  # left the chamber; drop
        Dv=D(oms)
        data.append((sp.Rational(t.numerator,t.denominator),
                     sp.Rational((oim*Dv).numerator,(oim*Dv).denominator)))
    xs=[x for x,_ in data]; ys=[y for _,y in data]
    npts=len(data)
    d=min(dmax, npts-8)               # single high-degree fit (extra coeffs->0)
    if d<2:
        print(f"[{label}] vary{vary}: too few in-chamber pts ({npts})"); return None
    Vm=sp.Matrix([[xs[k]**p for p in range(d+1)] for k in range(d+1)])
    Yv=sp.Matrix(ys[:d+1])
    try:
        c=Vm.LUsolve(Yv)
    except Exception:
        print(f"[{label}] vary{vary}: solve failed"); return None
    ok=True
    for k in range(d+1, npts):
        pred=sum(c[p]*xs[k]**p for p in range(d+1))
        if sp.simplify(pred-ys[k])!=0: ok=False; break
    if ok:
        truedeg=max([p for p in range(d+1) if c[p]!=0], default=0)
        print(f"[{label}] vary{vary}: A_6*D POLYNOMIAL in t, degree {truedeg} "
              f"(fit deg {d}, {npts} pts, holdout {npts-d-1} ok)")
        return truedeg
    print(f"[{label}] vary{vary}: A_6*D NOT polynomial (fit deg {d}, {npts} pts) "
          f"-> D missing a factor")
    return None

def D_one(o): return Fr(1)
def D_Q(o):
    w=[None]+[Fr(x) for x in o]; return w[1]**2+w[2]**2+w[3]**2
def D_pp(o):
    w=[None]+[Fr(x) for x in o]
    return (w[4]**2+w[5]**2)*(w[4]**2+w[6]**2)*(w[5]**2+w[6]**2)
def D_pm(o):
    w=[None]+[Fr(x) for x in o]
    return (w[1]**2+w[2]**2)*(w[1]**2+w[3]**2)*(w[2]**2+w[3]**2)
def D_all(o): return D_pp(o)*D_pm(o)
def D_allQ(o):
    w=[None]+[Fr(x) for x in o]; Q=w[1]**2+w[2]**2+w[3]**2
    return D_all(o)*Q
def D_ppQ(o):
    w=[None]+[Fr(x) for x in o]; Q=w[1]**2+w[2]**2+w[3]**2
    return D_pp(o)*Q
def e2p(o):
    w=[None]+[Fr(x) for x in o]; return w[4]*w[5]+w[4]*w[6]+w[5]*w[6]
def e2m(o):
    w=[None]+[Fr(x) for x in o]; return w[1]*w[2]+w[1]*w[3]+w[2]*w[3]
def D_e2p(o): return e2p(o)
def D_e2p2(o): return e2p(o)**2
def D_e2pm(o): return e2p(o)*e2m(o)
def D_e2pm2(o): return (e2p(o)*e2m(o))**2
def D_e2p_pp(o): return e2p(o)*D_pp(o)
def D_e2p_all(o): return e2p(o)*D_all(o)
def D_e2pm_all(o): return e2p(o)*e2m(o)*D_all(o)
def D_mixsum(o):
    w=[None]+[Fr(x) for x in o]; pr=Fr(1)
    for i in (1,2,3):
        for j in (4,5,6):
            pr*= (w[i]+w[j])
    return pr
def D_allsum(o):
    w=[None]+[Fr(x) for x in o]; pr=Fr(1)
    for i in range(1,7):
        for j in range(i+1,7):
            pr*=(w[i]+w[j])
    return pr

if __name__=="__main__":
    base={2:2,3:3,4:5,5:7}
    print("=== D=1 (is A_6 polynomial?) ==="); slice_poly_degree(D_one, base,(4,5),"D=1")
    print("=== D=e2(plus) ==="); slice_poly_degree(D_e2p, base,(4,5),"e2p")
    print("=== D=e2(plus)^2 ==="); slice_poly_degree(D_e2p2, base,(4,5),"e2p^2")
    print("=== D=e2p*e2m ==="); slice_poly_degree(D_e2pm, base,(4,5),"e2p*e2m")
    print("=== D=(e2p*e2m)^2 ==="); slice_poly_degree(D_e2pm2, base,(4,5),"(e2p*e2m)^2")
    print("=== D=e2p*plus-pairs ==="); slice_poly_degree(D_e2p_pp, base,(4,5),"e2p*pp")
    print("=== D=e2p*all-pairs ==="); slice_poly_degree(D_e2p_all, base,(4,5),"e2p*all")
    print("=== D=e2p*e2m*all-pairs ==="); slice_poly_degree(D_e2pm_all, base,(4,5),"e2pm*all")
    print("=== D = prod_{i in minus, j in plus} (w_i+w_j)  [9 mixed sums] ===")
    slice_poly_degree(D_mixsum, base,(4,5),"mixsum"); slice_poly_degree(D_mixsum, base,(2,4),"mixsum")
    print("=== D = prod_{all i<j} (w_i+w_j)  [15 sums] ===")
    slice_poly_degree(D_allsum, base,(4,5),"allsum")
