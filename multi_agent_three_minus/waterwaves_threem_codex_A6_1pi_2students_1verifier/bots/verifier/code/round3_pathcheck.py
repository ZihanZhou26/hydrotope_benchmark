#!/usr/bin/env python3
"""Decisive path-independence check for the q24 same-energy wall brick H24.

H24 at a wall point is a function of the wall omega ALONE; it must be identical
along ANY affine transversal path crossing q24=0 at that point. If two paths give
different H24, my extraction is contaminated (extra wall/structure). If they agree
with each other but disagree with student-2's compact four-leg formula, the formula
has a genuine counterexample.

We keep S=b+c+d+e constant along each path so omega is affine in tau (=> R restricts
to a degree-8 polynomial per side, exactly reconstructible)."""
import sys, os
from fractions import Fraction as F
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pole_verify import solve_onshell, C_of, Delta_of, MINUS, PLUS
from round3_verify import (safe_R, fit_poly, peval, pderiv_eval,
                           compact_same_energy_H)

def branch(pathfn, sgn, h, want=9, off=F(1)):
    ts, ys = [], []
    k = 0; tried = 0
    while len(ts) < want and tried < want*5 + 10:
        tried += 1
        tau = sgn * h * (off + k); k += 1
        bcde = pathfn(tau)
        w = solve_onshell(*bcde)
        if w is None or any(x == 0 for x in w) or C_of(w)==0 or Delta_of(w)==0:
            continue
        y = safe_R(w)
        if y is None: continue
        ts.append(tau); ys.append(y)
    if len(ts) < want: return None
    return ts, ys

LADDER = (F(1,6),F(1,12),F(1,24),F(1,60),F(1,120),F(1,300),F(1,600),
          F(1,1200),F(1,3000),F(1,6000),F(1,15000),F(1,40000),F(1,100000),
          F(1,300000),F(1,1000000))

def H24_along(pathfn, q24p0):
    """Return (H24, continuous, h). ACCEPT only when holdouts vanish AND the two
    branches meet continuously at the wall (R_L(0)=R_R(0)) -- this guarantees the
    cluster is in the cell IMMEDIATELY adjacent to the wall (no nearer wall skipped).
    Shrinks h aggressively; q24p0 = d/dtau q24 at tau=0."""
    for h in LADDER:
        L = branch(pathfn, -1, h); R = branch(pathfn, +1, h)
        if L is None or R is None: continue
        cL = fit_poly(L[0], L[1], 8); cR = fit_poly(R[0], R[1], 8)
        Lh = branch(pathfn, -1, h, want=5, off=F(3,2))
        Rh = branch(pathfn, +1, h, want=5, off=F(3,2))
        if Lh is None or Rh is None: continue
        okL = all(peval(cL,t)-y == 0 for t,y in zip(*Lh))
        okR = all(peval(cR,t)-y == 0 for t,y in zip(*Rh))
        if not (okL and okR): continue
        cont = (peval(cL,0) - peval(cR,0) == 0)   # continuity at wall (tau=0)
        if not cont:
            continue   # cluster not adjacent to wall -> shrink further
        Gp = pderiv_eval(cL,0) - pderiv_eval(cR,0)
        return Gp / q24p0, True, h
    return None, False, None

# ---- wall points and multiple affine paths to each ----
def make_paths(a, cval, eval_, b0=None):
    """Standard family for wall at (b,c,d,e)=(a,cval,a,eval_) i.e. w2=w4=a.
    Returns list of (name, pathfn, q24prime0). Each keeps S const."""
    # base coords at wall: b=a, c=cval, d=a, e=eval_ ; S = 2a+cval+eval_
    paths = []
    # path1: b=a+tau, d=a-tau (c,e fixed). q24=d^2-b^2 => q24'(0)=2a(-1)-2a(1)=-4a
    paths.append(("p1 b+,d-",
                  lambda tau: (a+tau, cval, a-tau, eval_),
                  F(-4)*a))
    # path2: b=a+2tau, c=cval-tau, d=a-tau (e fixed). S const. q24'(0)=2a(-1)-2a(2)=-6a
    paths.append(("p2 b+2,c-,d-",
                  lambda tau: (a+2*tau, cval-tau, a-tau, eval_),
                  F(-6)*a))
    # path3: b=a+tau, d=a-3tau, e=eval_+2tau (c fixed). S const. q24'(0)=2a(-3)-2a(1)=-8a
    paths.append(("p3 b+,d-3,e+2",
                  lambda tau: (a+tau, cval, a-3*tau, eval_+2*tau),
                  F(-8)*a))
    return paths

def run_env(name, a, cval, eval_):
    print("="*70)
    print(f"ENV {name}: wall (b,c,d,e)=({a},{cval},{a},{eval_}) -> w2=w4={a}")
    w_wall = solve_onshell(a, cval, a, eval_)
    print("  wall omega:", w_wall)
    Hform = compact_same_energy_H(w_wall, 1, 3, 'four')
    print("  four-leg compact formula H24 =", Hform)
    vals = []
    for pname, pf, q0 in make_paths(a, cval, eval_):
        H, cont, h = H24_along(pf, q0)
        vals.append(H)
        print(f"  [{pname:14s}] H24={H}  continuous={cont}  step={h}  matches_formula={H==Hform}")
    allsame = all(v==vals[0] for v in vals) and vals[0] is not None
    print(f"  --> all paths agree: {allsame}   agrees with formula: {vals[0]==Hform}")
    return allsame, vals[0], Hform

if __name__ == "__main__":
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all","C"):
        run_env("C (was suspect)", F(6), F(5), F(1))
    if which in ("all","E"):
        run_env("E (was suspect)", F(8), F(6), F(1))
    if which in ("all","A"):
        run_env("A (control, minus-min)", F(5), F(2), F(3))
    if which in ("all","B"):
        run_env("B (control, plus-min)", F(5), F(4), F(1))
