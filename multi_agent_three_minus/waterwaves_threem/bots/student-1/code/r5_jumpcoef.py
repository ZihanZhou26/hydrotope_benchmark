#!/usr/bin/env python3
"""Round 5: extract the JUMP COEFFICIENT polynomials along clean single-wall slices.
 N = A_6*(e3m+e3p)/32  (g=1).  N = base + sum (k_ij)_+ P_ij + sum (k_ijk)_+^3 Q_ijk.
 Across a single (1=1) wall: jump N_+ - N_- = (k_ij)^1 * P_ij  -> P along slice = jump/k.
 Across a single (1=2) wall: jump = (k_ijk)^3 * Q_ijk          -> Q along slice = jump/k^3.
"""
from fractions import Fraction as F
import sympy as sp
from collectlib import full_sig, reconstruct, poly
import harness as h, chambers_n6 as cn, inv
SIG=[-1,-1,-1,1,1,1]; t=sp.Symbol('t')
def ee(oms): e=inv.invariants(oms); return e[2]+e[3]
def Nval(oms,im): return im*ee(oms)/32   # N value (= A6/i * (e3m+e3p)/32)
def side(base, vary, direction, step, maxn):
    pts=[]; s0=None
    for k in range(1,maxn+1):
        s=direction*step*k
        free=list(base); free[vary-2]=base[vary-2]+s
        oms=cn.solve_squares(free)
        if oms is None or any(w==0 for w in oms): break
        sig=full_sig(oms)
        if sig is None: break
        if s0 is None: s0=sig
        elif sig!=s0: break
        try: im,_,_=h.on_shell(free,SIG); pts.append((s, Nval(oms,im)))
        except Exception: break
    return pts,s0
def jumppoly(base, vary, step):
    A,_=side(base,vary,+1,step,170); B,_=side(base,vary,-1,step,170)
    rA=reconstruct(A); rB=reconstruct(B)
    if rA is None or rB is None: return None
    NA=poly(rA[2])/poly(rA[3]); NB=poly(rB[2])/poly(rB[3])
    return sp.cancel(NA-NB), rA, rB

print("=== (1=1) wall  a2=b4 (base w2=3,w3=5/2,w5=53/10, vary w4 across 3) ===")
res=jumppoly([F(3),F(5,2),F(3),F(53,10)],4,F(1,90))
jump,rA,rB=res
jump=sp.expand(jump)
print("jump (N_+ - N_-) =", jump)
print("deg jump =", sp.degree(jump,t))
# k_24 = b4 - a2 = w4^2 - w2^2 ; on slice w4 = 3 + t' but our slice var is the actual w4 value offset.
# Here vary=4 means free[2]=w4 = base + s; the reconstruction var t = s = w4-3. So w4 = 3+t, w2=3.
k = (3+t)**2 - 3**2
print("k_24(t) = (3+t)^2-9 =", sp.expand(k))
P_slice = sp.cancel(jump/k)
print("P along slice = jump/k =", sp.expand(P_slice), " (should be polynomial, deg", sp.degree(sp.expand(P_slice),t),")")
print()
print("=== (1=2) wall a2=b4+b5 (base w2=6,w3=-87/10,w5=3, vary w4 across sqrt27) ===")
res=jumppoly([F(6),F(-87,10),F(26,5),F(3)],4,F(1,200))
jump,rA,rB=res
jump=sp.expand(jump)
print("deg jump =", sp.degree(jump,t))
# slice var t = w4 - 26/5 ; w4 = 26/5 + t ; w2=6, w5=3 ; k_245 = a2-b4-b5 = w2^2-w4^2-w5^2 = 36 - w4^2 - 9 = 27 - w4^2
w4 = F(26,5)+t
k = 6**2 - w4**2 - 3**2
k = sp.expand(k)
print("k_245(t) = 27 - (26/5+t)^2 =", k)
Q_slice = sp.cancel(jump/k**3)
print("Q along slice = jump/k^3 =", sp.expand(Q_slice))
print("  deg Q_slice =", sp.degree(sp.together(Q_slice).as_numer_denom()[0],t), "num /", sp.degree(sp.together(Q_slice).as_numer_denom()[1],t),"den")
