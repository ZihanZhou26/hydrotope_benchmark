#!/usr/bin/env python3
"""Consolidated round-5 verification:
(A) Q correct: M=N-corr12 is (1=2)-SMOOTH across several (1=2) walls (jump=0).
(B) M still KINKS across (1=1) walls (so (1=1) part nontrivial).
(C) cross-check corr12/Q via independent pybg evaluator at a point.
"""
from fractions import Fraction as F
import sympy as sp, r5lib as L, r5_walls as W, r5_corr as C, chambers_n6 as cn, harness as h, pybg, inv
t=W.t; SIG=[-1,-1,-1,1,1,1]
def Mside(w2,w3,a,b,tstart,direction,step,maxn,ref):
    import fastbg as FB
    tvals=[];omsl=[]
    for kk in range(0,maxn+1):
        tt=tstart+direction*step*kk
        o=cn.solve_squares(L.fc_free(w2,w3,a,b,tt))
        if o is None or any(w==0 for w in o): break
        s=W.msig(o)
        if s is None or s!=ref: break
        tvals.append(tt);omsl.append(o)
    if not tvals: return []
    res=FB.batch_onshell([(6,L.fc_free(w2,w3,a,b,tt),SIG) for tt in tvals])
    return [(tt, C.Nval(o,r[1])-C.corr12(o)) for tt,o,r in zip(tvals,omsl,res) if r is not None]

print("(A) M=N-corr12 jump across (1=2) walls (expect 0 = Q correct):")
n12=0; ok12=0
for (w2,w3,a,b) in [(F(3),F(11,2),F(9,2),F(15,2)),(2,3,5,7),(F(5,2),F(9,2),4,6),(F(7),F(17,2),3,F(11,2))]:
    for (lo,hi,key) in W.find_crossings(w2,w3,a,b,F(1,40),F(6)):
        if key[0]!='2': continue
        sL=W.msig(cn.solve_squares(L.fc_free(w2,w3,a,b,lo))); sR=W.msig(cn.solve_squares(L.fc_free(w2,w3,a,b,hi)))
        pL=Mside(w2,w3,a,b,lo,-1,F(1,120),32,sL); pR=Mside(w2,w3,a,b,hi,+1,F(1,120),32,sR)
        sl=L.fit_poly(pL,22); sr=L.fit_poly(pR,22)
        if sl is None or sr is None: continue
        j=sp.expand(L.poly(sr)-L.poly(sl)); n12+=1; ok12+= (j==0)
        print(f"   {key} @({w2},{w3},{a},{b}): jump={'0 OK' if j==0 else 'NONZERO!'}")
print(f"   => {ok12}/{n12} (1=2) walls smooth after subtracting corr12\n")

print("(B) M jump across a (1=1) wall (expect NONZERO = (1=1) part remains):")
w2,w3,a=F(4),F(7,2),F(9,2)
for (lo,hi,key) in W.find_crossings(w2,w3,a,F(15,2),F(1,50),F(5)):
    if key[0]!='1': continue
    sL=W.msig(cn.solve_squares(L.fc_free(w2,w3,a,F(15,2),lo))); sR=W.msig(cn.solve_squares(L.fc_free(w2,w3,a,F(15,2),hi)))
    pL=Mside(w2,w3,a,F(15,2),lo,-1,F(1,110),30,sL); pR=Mside(w2,w3,a,F(15,2),hi,+1,F(1,110),30,sR)
    sl=L.fit_poly(pL,22); sr=L.fit_poly(pR,22)
    if sl and sr:
        j=sp.expand(L.poly(sr)-L.poly(sl))
        print(f"   {key}: M jump {'NONZERO (kinks)' if j!=0 else 'ZERO'} deg {sp.degree(j,t) if j!=0 else '-'}")
        break

print("\n(C) Independent pybg cross-check of N and corr12 at free=(2,3,5,7):")
free=[F(2),F(3),F(5),F(7)]; o=cn.solve_squares(free)
im_bg,_,_=h.on_shell(free,SIG); im_py,_,_=pybg.amp_onshell(free,SIG)
print("   N(oracle bg) =", C.Nval(o,im_bg))
print("   N(pybg)      =", C.Nval(o,im_py), " match:", im_bg==im_py)
