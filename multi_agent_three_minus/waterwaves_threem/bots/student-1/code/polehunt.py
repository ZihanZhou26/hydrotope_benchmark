#!/usr/bin/env python3
"""Targeted pole hunt: drive onto channel S={2,4,5} (1 minus + 2 plus, m=1) where
the factorization residue = (two-minus 4pt) x (two-minus 4pt), both NONZERO, so a
GENUINE pole is expected (unlike the m=2/removable channels PI checked).
D_{245}=0 solved at w2=-2,w4=2,w5=3 (k_{245}=9>0)."""
from fractions import Fraction as F
import harness as h, chambers_n6 as cn
SIG=[-1,-1,-1,1,1,1]
def evalpt(w2,w3,w4,w5):
    free=(w2,w3,w4,w5)
    oms=cn.solve_squares(free)
    if oms is None or any(w==0 for w in oms): return None
    try: im,_,_=h.on_shell(list(free),SIG)
    except Exception: return "SIGFPE"
    w245=oms[1]+oms[3]+oms[4]; k245=-oms[1]**2+oms[3]**2+oms[4]**2
    D=w245**2-abs(k245)
    return im,D,k245
print("Channel S={2,4,5}: w2=-2+eps, w3=1, w4=2, w5=3  (D_245->0, k_245>0, m=1)")
print(f"{'eps':>12} {'A6/i':>20} {'D_245':>16} {'A6*D_245':>18} {'k245':>8}")
for eps in [F(1,5),F(1,20),F(1,100),F(1,500),F(1,2000),F(-1,20),F(-1,100),F(-1,500)]:
    w2=F(-2)+eps
    r=evalpt(w2,F(1),F(2),F(3))
    if r is None or r=="SIGFPE": print(f"{str(eps):>12}  {r}"); continue
    im,D,k=r
    print(f"{str(eps):>12} {float(im):>20.3f} {float(D):>16.8f} {float(im*D):>18.5f} {float(k):>8.3f}")
