#!/usr/bin/env python3
"""COMPREHENSIVE exact verification of the assembled closed form
  A_6 = i 2^5 g^-3 N_6/(e3m+e3p),
  N_6 = corr12(Q) + sum_k coeff_k * column_k   [base + single(1=1) + pair(1=1)]
against BOTH ./bg (own copy) and the independent pybg evaluator, across >=4 chamber
types, plus two-sided limits onto a (1=1) wall, a (1=2) wall, and a matching corner.
"""
from fractions import Fraction as F
import random, pickle
import chambers_n6 as cn, r5_corr as C, inv, harness as h, pybg
import r6_extract as E

labels,rcoef=pickle.load(open("r6_coeffs.pkl","rb"))
SIG=[-1,-1,-1,1,1,1]

def A6_formula(o):
    """imaginary coeff of A_6 from the closed form (g=1)."""
    rows=E.relabel_rows(o)
    Nv=E.Nfit(o,rows,labels,rcoef)+C.corr12(o)
    e=inv.invariants(o); denom=e[2]+e[3]
    return F(32*Nv, denom), denom

def chamber_type(o):
    sq=[w*w for w in o]; return cn.canonical(sq)

if __name__=="__main__":
    print("=== 1) generic points across chamber types: formula vs ./bg vs pybg (EXACT) ===",flush=True)
    rnd=random.Random(2024); seen={}; tested=0; ok=0
    tries=0
    while (len(seen)<6 or tested<16) and tries<4000:
        tries+=1
        free=[F(rnd.randint(-90,90),10) for _ in range(4)]
        if 0 in free: continue
        o=cn.solve_squares(free)
        if o is None or any(w==0 for w in o): continue
        ct=chamber_type(o)
        if ct is None: continue
        # limit repeats per chamber type so we span types
        if seen.get(ct,0)>=3: continue
        Af,denom=A6_formula(o)
        if denom==0: continue
        try:
            im_bg,_,_=h.on_shell(free,SIG)
            im_py,_,_=pybg.amp_onshell(free,SIG)
        except Exception: continue
        match=(Af==im_bg==im_py)
        seen[ct]=seen.get(ct,0)+1; tested+=1; ok+=match
        print(f"  type#{list(seen).index(ct)} free={[str(x) for x in free]}  formula==bg: {Af==im_bg}  ==pybg: {Af==im_py}  resid={Af-im_bg}",flush=True)
    print(f"\n  chamber types spanned: {len(seen)}   EXACT matches: {ok}/{tested}",flush=True)

    print("\n=== 2) two-sided limits onto walls (oracle SIGFPEs ON wall; formula is exact) ===",flush=True)
    def near_wall(name, free_of_eps):
        print(f"  -- {name} --",flush=True)
        for eps in [F(1,10),F(1,100),F(1,1000)]:
            for sgn in (+1,-1):
                free=free_of_eps(sgn*eps)
                o=cn.solve_squares(free)
                if o is None or any(w==0 for w in o): print("    degen"); continue
                Af,denom=A6_formula(o)
                try: im_bg,_,_=h.on_shell(free,SIG)
                except Exception: im_bg='SIGFPE'
                tag='OK' if (im_bg!='SIGFPE' and Af==im_bg) else ('(on/over wall)' if im_bg=='SIGFPE' else 'MISMATCH')
                print(f"    eps={sgn*eps}: formula A6/i={Af}  bg={im_bg}  {tag}",flush=True)
    # (1=1) wall a2=b4: w4 -> w2.  base w2=3,w3=5,w5=7 (>0 distinct); w4=3+eps
    near_wall("(1=1) wall a2=b4 (w4->w2=3)", lambda e: [F(3),F(5),F(3)+e,F(7)])
    # (1=2) wall a_i=b_j+b_k: use w4^2=w2^2+w3^2 with w2=3,w3=4 -> w4=5; vary w4=5+eps
    near_wall("(1=2) wall b4=a?..: w4^2->w2^2+w3^2 (w2=3,w3=4,w4->5)", lambda e: [F(3),F(4),F(5)+e,F(6)])
    # matching corner: a2=b4 AND a3=b5 -> w4=w2,w5=w3 simultaneously. approach along w4=w2+eps,w5=w3+eps
    near_wall("matching corner a2=b4 & a3=b5 (w4->3,w5->5)", lambda e: [F(3),F(5),F(3)+e,F(5)+e])
