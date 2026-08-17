"""Test if N kinks across a SAME-TYPE ordering wall (w4=w5, plus-plus) at n=6.
On F-const slice w4=a+t,w5=b-t, same-type wall w4=w5 at t=(b-a)/2 (if same sign).
Reconstruct N on each side; if same polynomial -> analytic; else -> kink (missing wall)."""
from fractions import Fraction as F
import sympy as sp, r5lib as L, r5_walls as W, chambers_n6 as cn, harness as h
t=W.t; SIG=[-1,-1,-1,1,1,1]
def Npoly_side(w2,w3,a,b,tstart,direction,step,span,ref):
    pts=[]
    for k in range(0,span):
        tt=tstart+direction*step*k
        oms=cn.solve_squares(L.fc_free(w2,w3,a,b,tt))
        if oms is None or any(w==0 for w in oms): break
        s=W.msig(oms)
        if s is None or s!=ref: break
        im,_,_=h.on_shell(L.fc_free(w2,w3,a,b,tt),SIG)
        pts.append((tt,L.Nval(oms,im)))
    return pts
# choose slice where w4=w5 crossing is INTERIOR and single (no mixed wall there).
# w4=a+t, w5=b-t cross at t=(b-a)/2. Pick a,b close, w2,w3 generic far.
for (w2,w3,a,b) in [(F(13,2),F(15,2),F(5,2),F(7,2)),(F(7),F(8),F(5,2),F(13,4))]:
    tc=F(b-a,2)
    # check mixed signature same just below/above tc (only same-type flips)
    oL=cn.solve_squares(L.fc_free(w2,w3,a,b,tc-F(1,50)))
    oR=cn.solve_squares(L.fc_free(w2,w3,a,b,tc+F(1,50)))
    mL=W.msig(oL); mR=W.msig(oR)
    print(f"slice({w2},{w3},{a},{b}) same-type w4=w5 at t={tc}: mixed-sig same? {mL==mR}")
    if mL!=mR: 
        print("   (mixed wall also crosses here; pick another slice)"); continue
    ptsL=Npoly_side(w2,w3,a,b,tc-F(1,50),-1,F(1,100),20,mL)
    ptsR=Npoly_side(w2,w3,a,b,tc+F(1,50),+1,F(1,100),20,mR)
    sL=L.fit_poly(ptsL,14); sR=L.fit_poly(ptsR,14)
    if sL is None or sR is None: print("   fit failed",len(ptsL),len(ptsR)); continue
    NL=L.poly(sL); NR=L.poly(sR); d=sp.expand(NR-NL)
    print("   N_R - N_L =", d, " -> ANALYTIC" if d==0 else " -> KINK!")
