#!/usr/bin/env python3
"""ROUND 6 (student-1): characterize the (1=1) box-spline CROSS-TERMS of N_6.

The (1=1) single-wall jump coefficient P_{ij} (across {a_i=b_j}, jump N_+-N_- =
k_{ij} P_{ij}, k_{ij}=b_j-a_i, oriented k>0 active) is CHAMBER-DEPENDENT (s1_014):
it is itself a SPLINE on the wall, kinking on the sub-loci where the wall meets the
OTHER (1=1) walls in a perfect matching.

This script extracts P on the reference wall {a_0=b_3} (0-indexed legs 0 minus, 3
plus) at MANY wall points (harvested from all 9 (1=1) walls, relabelled to the
reference by S_3xS_3), tracking the sub-wall context, to (a) confirm P is not a
single deg-9 polynomial and (b) read off the cross-term structure.

Reference wall {a_0=b_3}: minus legs {0,1,2} (0 on wall), plus legs {3,4,5} (3 on
wall). Matchings through 0->3:
  sigma_a: 0->3,1->4,2->5  sub-locus {a_1=b_4} (== {a_2=b_5} on the wall)
  sigma_b: 0->3,1->5,2->4  sub-locus {a_1=b_5} (== {a_2=b_4} on the wall)
Sub-wall functions (on the wall): s_a = a_1-b_4 = w1^2-w4^2, s_b = a_1-b_5 = w1^2-w5^2
(0-indexed).  Walls sharing a leg with {a_0=b_3} meet it only on same-type (analytic)
loci, so P kinks ONLY across s_a, s_b.
"""
from fractions import Fraction as F
import itertools, sympy as sp, random
import r5lib as L, r5_walls as W, r5_group as Gp, chambers_n6 as cn, r5_basis as B, inv
t=W.t
M=[0,1,2]; P=[3,4,5]

def harvest_P(target=160, seed=11, span=F(6), step=F(1,40)):
    """Collect (ref_omega, P_value, subsigns) over the reference (1=1) wall."""
    rnd=random.Random(seed); data=[]; tries=0
    while len(data)<target and tries<2000:
        tries+=1
        vals=[F(rnd.randint(-70,70),10) for _ in range(4)]; w2,w3,a,b=vals
        if 0 in vals or len(set(vals))<4: continue
        if w2+w3+a+b==0: continue
        crs=W.find_crossings(w2,w3,a,b,step,span)
        for (lo,hi,key) in crs:
            if key[0]!='1': continue
            i=key[1]; j=key[2]
            # only walls with RATIONAL crossing t*: minus legs idx{1,2}, plus idx{3,4}
            # (solved legs 0,5 give w^2 quadratic in t -> irrational roots)
            if i not in (1,2) or j not in (3,4): continue
            r=W.extract_bracket(w2,w3,a,b,lo,hi,key,F(1,120),20)
            if r[0]=='fitfail' or not r[4]: continue
            kk,jump,kp,coef,isp=r
            # wall t*: b_j-a_i=0. j=3 -> w4=a+t=+-w_{i}; j=4 -> w5=b-t=+-w_{i}
            wi=w2 if i==1 else w3
            if j==3: cand=[-a+wi,-a-wi]
            else:    cand=[b-wi,b+wi]
            tstar=next((c for c in cand if lo<=c<=hi),None)
            if tstar is None: continue
            o=cn.solve_squares(L.fc_free(w2,w3,a,b,tstar))
            if o is None or any(w==0 for w in o): continue
            Pval=coef.subs(t,sp.Rational(tstar.numerator,tstar.denominator))
            Pval=F(sp.Rational(Pval).p,sp.Rational(Pval).q)
            perm=Gp.relabel_11_to_ref(i,j)
            ro=[F(x) for x in Gp.apply_perm(perm,o)]
            # sub-wall functions in ref frame
            sa=ro[1]**2-ro[4]**2; sb=ro[1]**2-ro[5]**2
            data.append((tuple(ro), Pval, (1 if sa>0 else -1, 1 if sb>0 else -1)))
            if len(data)>=target: break
    return data

if __name__=="__main__":
    data=harvest_P()
    print("harvested",len(data),"reference-wall P samples",flush=True)
    from collections import Counter
    cc=Counter(d[2] for d in data)
    print("sub-wall sign distribution (sa,sb):",dict(cc),flush=True)
    # save for reuse
    import pickle
    with open("r6_Pdata.pkl","wb") as f: pickle.dump(data,f)
    print("saved r6_Pdata.pkl",flush=True)
