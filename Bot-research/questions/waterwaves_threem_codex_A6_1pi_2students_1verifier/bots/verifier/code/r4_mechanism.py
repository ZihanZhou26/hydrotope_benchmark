#!/usr/bin/env python3
"""Attribute the R_spline Q_T-wall jump: is it EXACTLY the single P_pole channel
term that turns on at Q_T=0 (=> A_6 itself smooth across Q_T=0, and the wall is
an artifact of the pole-subtraction's Q_T>0 truncation)?

Uses the line found by r4_line_test3: P=[8,2,-3,-5,4,-6], d=[-2,1,0,2,-1,0],
t0=1/4, order-constant window (-1/2,1), single crossing channel (m=0,{3,5}).
"""
from fractions import Fraction as F
from r4_verify import amp_from_omega, P_pole, R_spline, SIG, _fmt, M, P, Hblock, pos
from r4_line_test import omega_of_t, word_of, poly_fit, poly_eval

Pt=[F(8),F(2),F(-3),F(-5),F(4),F(-6)]
d =[F(-2),F(1),F(0),F(2),F(-1),F(0)]
t0=F(1,4)
lo,hi=F(-1,2),F(1)
ch=(0,(3,5))              # m=leg1(0idx0), plus pair {leg4,leg6}(0idx3,5)

def channel_term(omega, m, pq):
    """single-channel contribution to P_pole (same formula as P_pole, one T)."""
    p,q=pq
    pbar=[x for x in P if x not in pq][0]
    mp=[x for x in M if x!=m]
    Q_T=omega[p]**2+omega[q]**2-omega[m]**2
    if Q_T<=0: return F(0)
    d_T=2*(omega[m]+omega[p])*(omega[m]+omega[q])
    H1=Hblock(min(omega[m]**2,Q_T),p,q,omega)
    H2=Hblock(min(omega[pbar]**2,Q_T),mp[0],mp[1],omega)
    return -64*omega[m]*omega[pbar]*Q_T*Q_T/d_T*H1*H2

# sample window
span=hi-lo; Ns=13
ts=[lo+span*F(k,2*Ns) for k in range(1,2*Ns) if lo+span*F(k,2*Ns)!=t0]
left=[t for t in ts if t<t0]; right=[t for t in ts if t>t0]

# fit degree-8 R_spline poly on the left
lt=left[:9]
coeffs=poly_fit(lt,[R_spline(omega_of_t(Pt,d,t)) for t in lt],8)

print("Mechanism check on the RIGHT side (Q_T>0):")
print("  delta = leftpoly(t) - R_spline(t)   vs   CT(t)=turned-on channel term")
all_match=True
for t in right:
    o=omega_of_t(Pt,d,t)
    R=R_spline(o)
    lp=poly_eval(coeffs,t)
    delta=lp-R
    CT=channel_term(o,ch[0],ch[1])
    m=(delta==CT)
    all_match&=m
    print(f"  t={_fmt(t):>10}  delta={_fmt(delta):>22}  CT={_fmt(CT):>22}  match={m}")
print("\nAll right-side jumps EXACTLY equal the single turned-on P_pole channel term:",all_match)

# Independent corroboration: A_6/i * C should be one polynomial (deg<=11) across
# the wall if A_6 is smooth (D_min=C). Test that directly.
def Cval(o): return o[0]*o[1]*o[2]+o[3]*o[4]*o[5]
print("\nIndependent check: is (A_6/i)*C a single polynomial across Q_T=0?")
AC_left=[(t, amp_from_omega(omega_of_t(Pt,d,t))*Cval(omega_of_t(Pt,d,t))) for t in left]
# fit degree 11 from 12 left points
lt2=[t for t,_ in AC_left][:12]; ly2=[y for _,y in AC_left][:12]
c2=poly_fit(lt2,ly2,11)
smooth=True
for t in right:
    o=omega_of_t(Pt,d,t)
    val=amp_from_omega(o)*Cval(o)
    r=poly_eval(c2,t)-val
    smooth&=(r==0)
print("  (A_6/i)*C degree-11 left-fit reproduces right side:",smooth,
      "  => A_6 itself is", "SMOOTH" if smooth else "NOT smooth","across Q_T=0")
