#!/usr/bin/env python3
"""Rigorous attribution with left-controls:
 (A) confirm R_spline is a single deg-8 poly on the LEFT (control) and jumps right;
 (B) confirm A_6 itself is NOT smooth across Q_T=0 (with a left control), i.e.
     Q_T=0 (=k_{m,p,q}=0, a 3-leg subset-momentum wall) is a GENUINE chamber wall;
 (C) measure the jump ORDER in (t-t0) ~ Q_T near the wall.
Line: P=[8,2,-3,-5,4,-6], d=[-2,1,0,2,-1,0], t0=1/4, window(-1/2,1),
crossing channel (m=leg1,{leg4,leg6}) i.e. Q_{1;46}.
"""
from fractions import Fraction as F
from r4_verify import amp_from_omega, P_pole, R_spline, SIG, _fmt, M, P
from r4_line_test import omega_of_t, word_of, poly_fit, poly_eval

Pt=[F(8),F(2),F(-3),F(-5),F(4),F(-6)]
d =[F(-2),F(1),F(0),F(2),F(-1),F(0)]
t0=F(1,4); lo,hi=F(-1,2),F(1)

def Cval(o): return o[0]*o[1]*o[2]+o[3]*o[4]*o[5]

# dense samples strictly inside window, off t0
def samples(nL,nR):
    L=[]; R=[]
    # left in (lo,t0), right in (t0,hi)
    for k in range(1,nL+1):
        L.append(lo+(t0-lo)*F(k,nL+1))
    for k in range(1,nR+1):
        R.append(t0+(hi-t0)*F(k,nR+1))
    return L,R

L,R=samples(20,20)
# sanity: order constant
o0=word_of(omega_of_t(Pt,d,L[0]))
for t in L+R:
    assert word_of(omega_of_t(Pt,d,t))==o0, f"order changed at {t}"

# ---------- (A) R_spline deg-8, control on left ----------
RS={t:R_spline(omega_of_t(Pt,d,t)) for t in L+R}
cR=poly_fit(L[:9],[RS[t] for t in L[:9]],8)
ctrlR=all(poly_eval(cR,t)==RS[t] for t in L[9:])
rightR=all(poly_eval(cR,t)==RS[t] for t in R)
print(f"(A) R_spline: deg-8 left-fit; LEFT control 11 holdouts all-zero={ctrlR}; "
      f"RIGHT all-zero={rightR}")

# ---------- (B) A_6 smoothness: fit (A_6/i)*C, control on left ----------
AC={t:amp_from_omega(omega_of_t(Pt,d,t))*Cval(omega_of_t(Pt,d,t)) for t in L+R}
# determine degree by rising until left control passes
degfound=None
for deg in range(8,16):
    if len(L) < deg+1+4: break
    c=poly_fit(L[:deg+1],[AC[t] for t in L[:deg+1]],deg)
    if all(poly_eval(c,t)==AC[t] for t in L[deg+1:deg+1+5]):
        degfound=deg; cAC=c; break
print(f"(B) (A_6/i)*C is a single polynomial of degree {degfound} on the LEFT "
      f"(left control passed).")
if degfound is not None:
    rightAC=all(poly_eval(cAC,t)==AC[t] for t in R)
    print(f"    LEFT poly reproduces RIGHT side across Q_T=0: {rightAC}  => "
          f"A_6 itself is {'SMOOTH' if rightAC else 'NOT smooth (genuine chamber wall)'} at Q_T=0")

# ---------- (C) jump order in Q_T near the wall ----------
# jump(t) = R_spline(t) - leftpoly_R(t); near t0, Q_T ~ linear in (t-t0).
def QT(t):
    o=omega_of_t(Pt,d,t); return o[3]**2+o[5]**2-o[0]**2   # Q_{1;46}: p,q=leg4,leg6=idx3,5; m=leg1=idx0
print("\n(C) jump = R_spline_right - leftpoly ;  jump/Q_T and jump/Q_T^2 near wall:")
for t in R[:6]:
    j=RS[t]-poly_eval(cR,t)
    qt=QT(t)
    print(f"   t={_fmt(t):>10}  Q_T={_fmt(qt):>14}  jump={_fmt(j):>20}  jump/Q_T={float(j/qt):+.6g}  jump/Q_T^2={float(j/qt**2):+.6g}")
print("   (constant jump/Q_T as t->t0 => order-1 jump in Q_T; constant jump/Q_T^2 => order-2)")

# extrapolate jump/Q_T to the wall (t->t0) to see the limit
from fractions import Fraction
xs=[QT(t) for t in R[:8]]; ys=[(RS[t]-poly_eval(cR,t)) for t in R[:8]]
# fit jump as polynomial in Q_T (through wall), lowest power:
# jump(Q) = a1 Q + a2 Q^2 + ... ; solve with Q as variable
cc=poly_fit(xs[:6],ys[:6],5)
print("   jump as power series in Q_T (coeff of Q^0..Q^5):",[ _fmt(x) for x in cc])
