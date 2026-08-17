#!/usr/bin/env python3
"""Correction evaluators using the extracted Q (1=2). Test M = N - (1=2 corr) is (1=2)-smooth."""
from fractions import Fraction as F
import itertools, sympy as sp
import r5lib as L, r5_walls as W, r5_group as Gp, chambers_n6 as cn, inv
t=W.t; SIG=[-1,-1,-1,1,1,1]
M=[0,1,2]; P=[3,4,5]

def Qref(o):
    """o = omegas list, reference (1=2) wall minus0 + plus{3,4}, excluded plus 5."""
    x=o[0]; A1=o[1]+o[2]; A2=o[1]*o[2]; B1=o[3]+o[4]; B2=o[3]*o[4]; y=o[5]
    return (-A1**2*A2*B1 - A1*A2*B1**2 + A2**2*B1 - A2*B1*B2 + A2*B1*y**2
            + A2*B2*y - B1*B2*y**2 - B2**2*y)

def corr12(o):
    """sum over 9 (1=2) walls (i,{j,k}) of (k_S)_+^3 * Q_S, k_S=a_i-b_j-b_k."""
    tot=F(0)
    for i in M:
        for (j,k) in itertools.combinations(P,2):
            kS=o[i]**2 - o[j]**2 - o[k]**2
            if kS>0:
                perm=Gp.relabel_12_to_ref(i,(j,k))
                ro=Gp.apply_perm(perm,o)
                tot+= kS**3 * Qref(ro)
    return tot

def Nval(o,im):
    e=inv.invariants(o); return F(im*(e[2]+e[3]),32)

def Mside(w2,w3,a,b,tstart,direction,step,maxn,ref):
    """collect M = N - corr12 along an in-chamber side (batched N)."""
    import fastbg as FB
    tvals=[]; omsl=[]
    for kk in range(0,maxn+1):
        tt=tstart+direction*step*kk
        o=cn.solve_squares(L.fc_free(w2,w3,a,b,tt))
        if o is None or any(w==0 for w in o): break
        s=W.msig(o)
        if s is None or s!=ref: break
        tvals.append(tt); omsl.append(o)
    if not tvals: return []
    res=FB.batch_onshell([(6,L.fc_free(w2,w3,a,b,tt),SIG) for tt in tvals])
    out=[]
    for tt,o,r in zip(tvals,omsl,res):
        if r is None: continue
        out.append((tt, Nval(o,r[1]) - corr12(o)))
    return out

if __name__=="__main__":
    # TEST 1: M smooth across a (1=2) wall (jump should be 0)
    print("=== M = N - (1=2 corr): jump across (1=2) walls (expect 0) ===")
    for (w2,w3,a,b) in [(F(3),F(11,2),F(9,2),F(15,2)),(2,3,5,7)]:
        crs=W.find_crossings(w2,w3,a,b,F(1,40),F(6))
        for (lo,hi,key) in crs:
            if key[0]!='2': continue
            sL=W.msig(cn.solve_squares(L.fc_free(w2,w3,a,b,lo)))
            sR=W.msig(cn.solve_squares(L.fc_free(w2,w3,a,b,hi)))
            ptsL=Mside(w2,w3,a,b,lo,-1,F(1,120),32,sL)
            ptsR=Mside(w2,w3,a,b,hi,+1,F(1,120),32,sR)
            sl=L.fit_poly(ptsL,22); sr=L.fit_poly(ptsR,22)
            if sl is None or sr is None: print(f"  {key}: fit fail"); continue
            jump=sp.expand(L.poly(sr)-L.poly(sl))
            print(f"  slice({w2},{w3},{a},{b}) wall {key}: M jump = {jump}  -> {'SMOOTH' if jump==0 else 'STILL KINKS'}")
            break
