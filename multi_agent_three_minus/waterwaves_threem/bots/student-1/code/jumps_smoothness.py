#!/usr/bin/env python3
"""Reproducible: cross-wall jump orders for N=A_6*(e3m+e3p), exact, own ./bg.
Fixed clean single-wall crossings (sign-diff = 1).
  (1=1) wall  w_i = w_j (i minus, j plus):  jump ~ (k_ij)^1   [first-deriv kink]
  (1=2) wall  w_i^2 = w_j^2 + w_k^2:         jump ~ (k_ijk)^3  [cubic kink]
"""
import sys
from fractions import Fraction as F
import sympy as sp
from collectlib import full_sig, reconstruct, poly
import harness as h, chambers_n6 as cn, inv
SIG=[-1,-1,-1,1,1,1]; t=sp.Symbol('t')
def pr(*a): print(*a, flush=True)
def ee(oms): e=inv.invariants(oms); return e[2]+e[3]
def Nval(oms,im): return im*ee(oms)
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
def vanish_order(expr, var, pt):
    e=sp.together(expr); n,d=sp.fraction(e)
    def mult(P):
        m=0; P=sp.Poly(sp.expand(P),var)
        while True:
            q,r=sp.div(P, sp.Poly(var-pt,var))
            if r==0: m+=1; P=q
            else: break
        return m
    return mult(n)-mult(d)
def jump_at(base, vary, step, twall):
    A,_=side(base,vary,+1,step,170); B,_=side(base,vary,-1,step,170)
    rA=reconstruct(A); rB=reconstruct(B)
    if rA is None or rB is None: return None,len(A),len(B)
    NA=poly(rA[2])/poly(rA[3]); NB=poly(rB[2])/poly(rB[3])
    jump=sp.cancel(NA-NB)
    return vanish_order(jump,t,twall),len(A),len(B)

pr("(1=1) wall  w2=w4  (base w2=3,w3=5/2,w5=53/10, vary w4 across 3):")
o,nA,nB=jump_at([F(3),F(5,2),F(3),F(53,10)],4,F(1,90),sp.Integer(0))
pr(f"   jump vanishing order at wall = {o}   (A={nA},B={nB})  -> expect 1")

pr("(1=2) wall  w2^2=w4^2+w5^2  (base w2=6,w3=-87/10,w5=3, vary w4 across 26/5-... ):")
# wall at w4^2 = w2^2 - w5^2 = 36-9 = 27 -> w4 = 3 sqrt3; base w4mid = 26/5 (just below)
twall = -F(26,5)+3*sp.sqrt(3)
o,nA,nB=jump_at([F(6),F(-87,10),F(26,5),F(3)],4,F(1,200),twall)
pr(f"   jump vanishing order at wall = {o}   (A={nA},B={nB})  -> expect 3")
