#!/usr/bin/env python3
"""Round-3 independent verification.

Attacks the newest load-bearing round-3 claims:
  (V1) foundation re-check on a FRESH build: A_6/i - P_pole is denominator-free
       (degree-8 polynomial spline) across all 8 chambers.
  (V2) pair-wall jump order-1 and anchor H_24 = 12622720/27.
  (V3) student-2's COMPACT same-energy wall brick with the FOUR-LEG beta selector
       H_mp|_{w_p=w_m} = -32 beta^2 [4a^4+6a^3 s+2a^2(s^2+v)+(a s+v)(s^2-2v)],
       a=w_m=w_p, s,v = sum/prod of the two OTHER MINUS legs,
       beta = min|w_j| over ALL FOUR non-primary legs.
       Independently reconstruct H at same-energy walls and compare; also test that
       the earlier two-minus-leg-only beta rule FAILS where four-leg differs.
  (V4) student-1/student-2 verdict "H_mp is itself a spline": the P(u) <-> P(6-u)
       branch exchange across Q_{3;45}=61-12u on the affine slice, with the exact
       residuals from s1_004, plus the four-leg beta formula reproducing BOTH branches.

All BG values come only from my own md5-verified fresh build (oracle.py). P_pole is
my own reimplementation (pole_verify.py, transcribed from the written formula). The
compact wall brick is transcribed HERE from the written derivation, NOT imported.
All arithmetic exact (Fraction).
"""
import sys, os, itertools
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from oracle import amp_from_omega_sigma
from pole_verify import P_pole, C_of, Delta_of, SIGMA, MINUS, PLUS, solve_onshell, word_of

import subprocess
def A6_over_i(w):
    re, im = amp_from_omega_sigma(list(w), SIGMA, g=1)
    assert re == 0, "A6 not imaginary at %s" % (w,)
    return im

def R_spline(w):
    """R = A_6/i - P_pole (g=1). Independent of any student evaluator."""
    return A6_over_i(w) - P_pole(w)

def safe_R(w):
    """R_spline but returns None if BG is singular here (SIGFPE at an internal pole)
    or if P_pole hits d_T=0 -- these on-wall/on-pole points must be skipped."""
    try:
        return R_spline(w)
    except (subprocess.CalledProcessError, ZeroDivisionError, AssertionError):
        return None

# ---------- exact linear algebra over Fraction ----------
def solve_linear(A, b):
    """Solve A x = b exactly. A: list of rows (Fraction), b: list. Returns x or None."""
    n = len(A)
    M = [[F(A[i][j]) for j in range(n)] + [F(b[i])] for i in range(n)]
    for col in range(n):
        piv = None
        for r in range(col, n):
            if M[r][col] != 0:
                piv = r; break
        if piv is None:
            return None
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        M[col] = [x/pv for x in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0:
                fac = M[r][col]
                M[r] = [M[r][k]-fac*M[col][k] for k in range(n+1)]
    return [M[i][n] for i in range(n)]

def fit_poly(ts, ys, deg):
    """Fit exact polynomial of given degree through (ts,ys); requires len==deg+1.
    Returns coefficient list c[0..deg] (c[0] constant)."""
    assert len(ts) == deg+1
    A = [[F(t)**j for j in range(deg+1)] for t in ts]
    c = solve_linear(A, [F(y) for y in ys])
    return c

def peval(c, t):
    t = F(t); s = F(0)
    for j in range(len(c)-1, -1, -1):
        s = s*t + c[j]
    return s

def pderiv_eval(c, t):
    """Evaluate derivative of poly c at t."""
    t = F(t); s = F(0)
    for j in range(len(c)-1, 0, -1):
        s = s*t + j*c[j]
    return s

# ---------- cell/wall diagnostics ----------
def q_mp(w, m, p):     # pair wall omega_p^2 - omega_m^2
    return w[p]*w[p] - w[m]*w[m]

def Q_T(w, m, p, q):   # triple invariant
    return w[p]*w[p] + w[q]*w[q] - w[m]*w[m]

def fine_signature(w):
    """Signs of all pair walls (m in M, p in P) and all triple Q_T. Used to check we
    stay in a single analytic cell along a path (excluding the crossing wall)."""
    sig = {}
    for m in MINUS:
        for p in PLUS:
            v = q_mp(w, m, p)
            sig[('q', m, p)] = (v > 0) - (v < 0)
    for m in MINUS:
        for pq in itertools.combinations(PLUS, 2):
            v = Q_T(w, m, pq[0], pq[1])
            sig[('Q', m, pq)] = (v > 0) - (v < 0)
    return sig

# ---------- same-energy q24 wall reconstruction on path b=t,d=B-t ----------
def path_point(B, c, e, t):
    """Return the 6-vector on the path (b=t, c, d=B-t, e) via the standard param."""
    return solve_onshell(t, c, B - t, e)

def _collect(B, c, e, sgn, h, want, offset0):
    """Collect `want` valid (t, R) samples on side sgn starting at multiples of h,
    skipping degenerate / SIGFPE points. Points span at most ~ (want*3)*h in t so
    they stay tightly clustered near the wall. Returns (ts, ys) or None."""
    ts, ys = [], []
    k = 0
    tried = 0
    while len(ts) < want and tried < want*4 + 8:
        tried += 1
        t = F(B, 2) + sgn * h * (offset0 + k)
        k += 1
        w = path_point(B, c, e, t)
        if w is None or any(x == 0 for x in w) or C_of(w) == 0 or Delta_of(w) == 0:
            continue
        y = safe_R(w)
        if y is None:
            continue
        ts.append(t); ys.append(y)
    if len(ts) < want:
        return None
    return ts, ys

def _branch_at(B, c, e, sgn, h):
    """Reconstruct one degree-8 branch of R on side sgn (-1 left / +1 right) of the
    q24 wall t0=B/2 at step h. Fit 9 clustered points; VALIDATE on 6 fresh
    out-of-sample holdouts (half-integer offsets). Returns (coeffs, holds) or (None,r)."""
    fit = _collect(B, c, e, sgn, h, 9, F(1))
    if fit is None:
        return None, 'nofit'
    coeffs = fit_poly(fit[0], fit[1], 8)
    hold = _collect(B, c, e, sgn, h, 6, F(3, 2))  # off the integer-multiple grid
    if hold is None:
        return None, 'nohold'
    holds = [peval(coeffs, t) - y for t, y in zip(hold[0], hold[1])]
    return coeffs, holds

def reconstruct_H24(B, c, e, verbose=False):
    """Reconstruct H_24 at the same-energy q24 wall (t0=B/2) for slice (B,c,e).
    ADAPTIVE: shrink the step until BOTH branches pass all 6 out-of-sample holdouts
    exactly (certifies a single analytic degree-8 branch on each side).
    q24 = (B-t)^2 - t^2 = -2B(t - B/2), R(q24>0)=left branch (t<B/2)."""
    t0 = F(B, 2)
    out = {'B': B, 'c': c, 'e': e, 't0': t0}
    ladder = (F(1,6), F(1,12), F(1,24), F(1,60), F(1,120), F(1,300), F(1,600),
              F(1,1200), F(1,3000), F(1,6000), F(1,15000), F(1,40000),
              F(1,100000), F(1,300000), F(1,1000000))
    for h in ladder:
        cL, hL = _branch_at(B, c, e, -1, h)
        cR, hR = _branch_at(B, c, e, +1, h)
        okL = (cL is not None) and all(x == 0 for x in hL)
        okR = (cR is not None) and all(x == 0 for x in hR)
        if not (okL and okR):
            if verbose: print(f"  h={h}: okL={okL} okR={okR}")
            continue
        cont = peval(cL, t0) - peval(cR, t0)
        # require continuity: guarantees the clusters are in the cells IMMEDIATELY
        # adjacent to the wall (no nearer wall skipped -> no contaminated jump).
        if cont != 0:
            if verbose: print(f"  h={h}: holdouts ok but DIScontinuous ({cont}); shrinking")
            continue
        out['step'] = h
        out['left_ok'] = out['right_ok'] = True
        out['left_holdouts'] = hL; out['right_holdouts'] = hR
        out['continuity'] = cont
        Gp = pderiv_eval(cL, t0) - pderiv_eval(cR, t0)
        out['H24'] = Gp / (F(-2) * B)
        out['wall_omega'] = path_point(B, c, e, t0)
        return out
    out['left_ok'] = out.get('left_ok', False)
    out['right_ok'] = out.get('right_ok', False)
    return out

# ---------- compact wall brick (transcribed from s2_007, NOT imported) ----------
def compact_same_energy_H(w, m, p, beta_mode='four'):
    """H_mp|_{w_p=w_m} per student-2 post_011 / s2_007.
       a = w_m (= w_p on wall); other minus legs r,s: S=w_r+w_s, V=w_r w_s.
       beta_mode 'four': min|w_j| over the four non-primary legs;
                 'minus': min over the two OTHER MINUS legs only (the earlier rule)."""
    a = w[m]
    others_minus = [i for i in MINUS if i != m]
    r, s_ = others_minus
    S = w[r] + w[s_]
    V = w[r] * w[s_]
    others_plus = [i for i in PLUS if i != p]
    if beta_mode == 'four':
        cand = [abs(w[i]) for i in (others_minus + others_plus)]
    else:
        cand = [abs(w[i]) for i in others_minus]
    beta = min(cand)
    bracket = 4*a**4 + 6*a**3*S + 2*a**2*(S**2 + V) + (a*S + V)*(S**2 - 2*V)
    return F(-32) * beta**2 * bracket

# P(u) from s1_004 (transcribed) for the affine-slice cross-check.
def P_s1(u):
    u = F(u)
    return -(u**2)/16 * (219*u**4 - 2628*u**3 + 55226*u**2 - 284052*u - 2037485)

if __name__ == "__main__":
    print("="*70)
    print("md5 check of my bg.cpp vs shared:")
    print("="*70)
