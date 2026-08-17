import sys
from fractions import Fraction as F
import sympy as sp
from collectlib import full_sig, reconstruct, poly
import harness as h, chambers_n6 as cn, inv
SIG=[-1,-1,-1,1,1,1]; t=sp.Symbol('t')
def pr(*a): print(*a, flush=True)
def ee(oms): e=inv.invariants(oms); return e[2]+e[3]
def Nval(oms,im): return im*ee(oms)
def side(base, vary, direction, step, maxn, fn):
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
        try: im,_,_=h.on_shell(free,SIG); pts.append((s, fn(oms,im)))
        except Exception: break
    return pts,s0
def vanish_order(expr, var, pt):
    """order of vanishing of rational expr at var=pt (numerator power minus denom power)."""
    e=sp.together(expr); n,d=sp.fraction(e)
    def mult(poly_, p):
        m=0; P=sp.Poly(poly_,var)
        while True:
            q,r=sp.div(P, sp.Poly(var-p,var))
            if r==0: m+=1; P=q
            else: break
        return m
    return mult(sp.expand(n),pt)-mult(sp.expand(d),pt)

# (1=1) recheck: w2=3,w3=5/2,w5=53/10, vary w4 across 3 (wall at t=0, w4=w2)
b11=[F(3),F(5,2),F(3),F(53,10)]
ptsA,_=side(b11,4,+1,F(1,90),130,Nval); ptsB,_=side(b11,4,-1,F(1,90),130,Nval)
rA=reconstruct(ptsA); rB=reconstruct(ptsB)
NA=poly(rA[2])/poly(rA[3]); NB=poly(rB[2])/poly(rB[3])
jump=sp.cancel(NA-NB)
pr(f"(1=1) wall w4=w2: jump vanish order at t=0 = {vanish_order(jump,t,sp.Integer(0))}  (A={len(ptsA)},B={len(ptsB)})")

# (1=2): w2=5,w3=-15/2,w5=3, vary w4 across 4 (wall at t=0, w4^2=w2^2-w5^2)
b12=[F(5),F(-15,2),F(4),F(3)]
ptsA,_=side(b12,4,+1,F(1,150),150,Nval); ptsB,_=side(b12,4,-1,F(1,150),150,Nval)
rA=reconstruct(ptsA); rB=reconstruct(ptsB)
NA=poly(rA[2])/poly(rA[3]); NB=poly(rB[2])/poly(rB[3])
jump=sp.cancel(NA-NB)
pr(f"(1=2) wall w4^2+w5^2=w2^2: jump vanish order at t=0 = {vanish_order(jump,t,sp.Integer(0))}  (A={len(ptsA)},B={len(ptsB)})")
# also show jump/t^order factored to see coefficient
o=vanish_order(jump,t,sp.Integer(0))
pr(f"   jump/t^{o} at t=0 (nonzero const => order exact):")
val=sp.limit(sp.cancel(jump/t**o), t, 0)
pr(f"   leading coeff = {val}")
