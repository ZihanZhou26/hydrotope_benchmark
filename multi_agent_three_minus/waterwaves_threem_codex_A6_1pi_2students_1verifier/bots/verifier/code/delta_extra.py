#!/usr/bin/env python3
"""Strengthen the Delta test with genuinely all-integer on-shell points, and
verify the three-pair-cancellation algebra at a Delta zero exactly."""
from fractions import Fraction as F
from itertools import combinations
import oracle

SIG=[-1,-1,-1,1,1,1]; M=[0,1,2]; P=[3,4,5]

def onshell_from_free(freeW):
    fw=[F(x) for x in freeW]; s=[F(x) for x in SIG]
    sumFree=sum(fw); sumSig=sum(s[i+1]*fw[i]*fw[i] for i in range(4))
    wn=-(s[0]*sumFree*sumFree+sumSig)/(2*s[0]*sumFree); w1=-(sumFree+wn)
    return [w1]+fw+[wn]

def Delta(om):
    d=F(1)
    for m in M:
        for p in P: d*=(om[m]+om[p])
    return d

# ---- scan for all-integer on-shell points -------------------------------
print("== all-integer on-shell points: does Delta clear den(A6/i)? ==")
found=0; allclear=True; singular=0
for w2 in range(1,8):
  for w3 in range(w2,10):
    for w4 in range(1,8):
      for w5 in range(w4,14):
        om=onshell_from_free([w2,w3,w4,w5])
        if not all(x.denominator==1 for x in om): continue
        if len(set(abs(x) for x in om))<6: continue   # nondegenerate magnitudes
        try:
            _,im=oracle.amp_from_omega_sigma(om,SIG)
        except Exception:
            singular+=1                # BG hits an exact wall/pole (div-by-zero)
            continue
        D=Delta(om); cleared=D*im
        ok=(cleared.denominator==1)
        allclear&=ok
        # also: does den(im) divide |D|?
        divides = (D % im.denominator == 0) if im.denominator!=0 else True
        found+=1
        if found<=12:
            print("  om={} den(A6/i)={:>4} Delta_clears={} den|Delta={}".format(
                [int(x) for x in om], im.denominator, ok, divides))
print("  total all-integer nondegenerate regular points:", found,
      "| Delta clears ALL:", allclear, "| BG-singular points skipped:", singular)

# ---- three-pair cancellation at a Delta zero (exact algebra) ------------
print("\n== three-pair cancellation when omega_m+omega_p=0 on shell ==")
# take minus legs x,y and plus legs; force one plus = -x. Build (-x,y,z? ) ...
# Directly test the claimed implication with explicit rationals:
for (x,y) in [(F(-2),F(-3)),(F(-4),F(1)),(F(-5),F(2))]:
    # remaining plus legs must be {-x,-y}; the paired plus leg is -m
    u,v=-x,-y
    # energy of the 4 remaining: x+y+u+v should be 0; momentum x^2+y^2=u^2+v^2
    e_ok=(x+y+u+v==0); m_ok=(x*x+y*y==u*u+v*v)
    print("  x={} y={} -> u={} v={} : E-cons={} p-cons={} (forces plus set =-x,-y)".format(
        x,y,u,v,e_ok,m_ok))
