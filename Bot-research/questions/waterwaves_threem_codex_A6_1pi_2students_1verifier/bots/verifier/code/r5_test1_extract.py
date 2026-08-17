#!/usr/bin/env python3
"""Round-5 verifier test 1: foundation + canonical Q_{1;46} brick extraction +
decisive global smoothness of (R_spline - R_Q) across the Q wall."""
from fractions import Fraction as F
from r5_core import (amp_from_omega, solve_onshell, P_pole, R_spline, R_Q,
                     G_brick, Q_T_val, poly_interp, poly_eval, poly_sub,
                     poly_divmod, line, on_shell_ok, gen_ts, collect,
                     SingularError, _fmt, M, P)
import itertools

def hr(t): print("="*70); print(t); print("="*70)

# ---------------- Foundation on fresh oracle ----------------
hr("FOUNDATION (fresh bg_r5)")
a1 = solve_onshell(2,3,4,5)
print("anchor omega:", [_fmt(x) for x in a1])
print("  A6/i     =", _fmt(amp_from_omega(a1)), " expect -9190656/7")
print("  P_pole   =", _fmt(P_pole(a1)), " expect 42588288/7")
print("  R_spline =", _fmt(R_spline(a1)), " expect -7396992")
w = [F(21,2), -8, 1, -7, -6, F(19,2)]
print("witness on-shell:", on_shell_ok(w),
      " R_spline(witness) =", _fmt(R_spline(w)), " expect -49008548")

# ---------------- Canonical line crossing Q_{1;46}=0 ----------------
hr("CANONICAL LINE: Q_{1;46}=0 at t0=1/4  (m=1,p=4,q=6, omitted plus t=5)")
Pvec = [8,2,-3,-5,4,-6]; dvec = [-2,1,0,2,-1,0]
print("P on-shell:", on_shell_ok(line(Pvec,dvec,0)),
      " tangent (t=7 on-shell):", on_shell_ok(line(Pvec,dvec,7)))
m,p,q = 0,3,5
tleg = [x for x in P if x not in (p,q)][0]

# wall-free windows from r5_diag_walls.py: left (-0.50,0.25), right (0.25,0.536)
left_ts  = gen_ts(F(-9,20), F(11,50), 16)   # Q<0 side, inside one cell
right_ts = gen_ts(F(28,100), F(52,100), 16) # Q>0 side, inside one cell
xL, ysL = collect(R_spline, Pvec, dvec, left_ts)
xR, ysR = collect(R_spline, Pvec, dvec, right_ts)
print(f"usable left pts {len(xL)}, right pts {len(xR)}")
# sanity: Q sign on each side
print("  Q left sample:", _fmt(Q_T_val(line(Pvec,dvec,xL[0]),m,p,q)),
      " Q right sample:", _fmt(Q_T_val(line(Pvec,dvec,xR[0]),m,p,q)))

cL = poly_interp(xL[:9], ysL[:9]); cR = poly_interp(xR[:9], ysR[:9])
print("deg left:", len(cL)-1, " deg right:", len(cR)-1)
def resid(coeffs, xs, ys):
    return sum(1 for x,y in zip(xs,ys) if poly_eval(coeffs,x)!=y)
print("left holdouts bad:", resid(cL, xL[9:], ysL[9:]),
      " right holdouts bad:", resid(cR, xR[9:], ysR[9:]))
print("left poly on RIGHT pts (expect >0 = jump):", resid(cL, xR, ysR))

# ---------------- Jump = Q^3 * G, order exactly 3 ----------------
hr("JUMP: dR = R|_{Q>0} - R|_{Q<0} = R_right - R_left ; divide by Q^3")
dR = poly_sub(cR, cL)
print("dR coeffs low->high:", [_fmt(c) for c in dR], " (lowest nonzero power = jump order)")
lowest = next(i for i,c in enumerate(dR) if c!=0)
print("lowest nonzero power of dR:", lowest, "(expect 3 = order exactly 3)")

# Q_{1;46}(t) polynomial in t
def Q_poly(m,p,q):
    def sq(idx):
        a,b = F(Pvec[idx]), F(dvec[idx]); return [a*a, 2*a*b, b*b]
    def addp(x,y):
        n=max(len(x),len(y)); x=x+[F(0)]*(n-len(x)); y=y+[F(0)]*(n-len(y))
        return [x[i]+y[i] for i in range(n)]
    return addp(addp(sq(p),sq(q)), [-c for c in sq(m)])
Qp = Q_poly(m,p,q)
print("Q_{1;46}(t):", [_fmt(c) for c in Qp], " (expect linear -3+12t)")
Qcube=[F(1)]
for _ in range(3):
    new=[F(0)]*(len(Qcube)+len(Qp)-1)
    for i,ci in enumerate(Qcube):
        for j,cj in enumerate(Qp): new[i+j]+=ci*cj
    Qcube=new
quot, rem = poly_divmod(dR, Qcube)
print("remainder dR/Q^3 (expect 0):", [_fmt(c) for c in rem])
print("quotient G(t):", [_fmt(c) for c in quot], " deg:", len(quot)-1, "(expect 2)")
print("--- selector: quotient vs my -16 max(wm^2,wt^2) ---")
for t in [F(3,10), F(1,2), F(-1,4)]:
    om=line(Pvec,dvec,t)
    print(f"  t={_fmt(t)}: quot={_fmt(poly_eval(quot,t))}  G_brick={_fmt(G_brick(om,m,p,q))}"
          f"  -16wm^2={_fmt(-16*om[m]**2)} -16wt^2={_fmt(-16*om[tleg]**2)}"
          f"  Q={_fmt(Q_T_val(om,m,p,q))}")

# ---------------- DECISIVE: R_spline - R_Q single poly across wall ----------------
hr("DECISIVE: (R_spline - R_Q) is ONE degree-8 poly across Q_{1;46}=0")
def RmQ(om): return R_spline(om) - R_Q(om)
allts = left_ts + right_ts
xA, yA = collect(RmQ, Pvec, dvec, allts)
c = poly_interp(xA[:9], yA[:9])
bad = resid(c, xA, yA)
print(f"deg {len(c)-1}; single-poly residuals over {len(xA)} pts spanning wall: {bad}")
print("  0 => R_Q EXACTLY captures the Q_{1;46} jump (brick value + (Q)_+^3).")
