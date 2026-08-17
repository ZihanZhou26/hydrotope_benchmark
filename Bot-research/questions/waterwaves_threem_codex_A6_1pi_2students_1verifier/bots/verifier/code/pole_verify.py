#!/usr/bin/env python3
"""Independent verifier reimplementation of student-1's compact pole part P_pole
and student-2's C / Delta / d_T identities, plus batch tests against a fresh,
md5-verified BG oracle.

NOTHING is imported from any student directory. The only external call is to my
own bg binary (built from an md5-verified copy of the shared bg.cpp) via
oracle.amp_from_omega_sigma. All auxiliary arithmetic is exact (Fraction).

Conventions (transcribed from the WRITTEN formula, not from student code):
  M = minus legs = indices 0,1,2  (legs 1,2,3)
  P = plus  legs = indices 3,4,5  (legs 4,5,6)
  sigma = (-1,-1,-1,+1,+1,+1)

  H(b; c, d) = b - (b-w_c^2)_+ - (b-w_d^2)_+ + (b-w_c^2-w_d^2)_+     (pos part)

  For a channel T = {m; p,q} with m in M and {p,q} subset P, let t be the
  omitted plus leg and {r,s} the two omitted minus legs:
      Q_T = w_p^2 + w_q^2 - w_m^2
      d_T = 2 (w_m + w_p)(w_m + w_q)          [ = w_T^2 - Q_T, w_T=w_m+w_p+w_q ]
  Include the channel only when Q_T > 0. Then
      P_T = -64 * w_m*w_t*Q_T^2 / d_T
              * H(min(w_m^2,Q_T); p,q) * H(min(w_t^2,Q_T); r,s)
  P_pole = sum_T P_T   (one S3(M) x S3(P) orbit; 9 channels max).

At g=1, A_6/i should equal P_pole + R with R a polynomial spline (denominator
free). This module tests exactly that.
"""
import sys, os, itertools, random
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from oracle import amp_from_omega_sigma  # my own oracle wrapper only

MINUS = (0, 1, 2)
PLUS  = (3, 4, 5)
SIGMA = (-1, -1, -1, 1, 1, 1)

def pos(x):
    return x if x > 0 else F(0)

def Hblock(b, wc2, wd2):
    """H(b; c,d) with wc2 = w_c^2, wd2 = w_d^2 already squared."""
    return b - pos(b - wc2) - pos(b - wd2) + pos(b - wc2 - wd2)

def C_of(w):
    """C = w1 w2 w3 + w4 w5 w6 (indices 0..5)."""
    return w[0]*w[1]*w[2] + w[3]*w[4]*w[5]

def Delta_of(w):
    d = F(1)
    for m in MINUS:
        for p in PLUS:
            d *= (w[m] + w[p])
    return d

def channels():
    """Yield (m, (p,q), t, (r,s)) for all 9 channels."""
    for m in MINUS:
        rs = tuple(x for x in MINUS if x != m)
        for pq in itertools.combinations(PLUS, 2):
            p, q = pq
            t = [x for x in PLUS if x not in pq][0]
            yield m, (p, q), t, rs

def P_pole(w):
    """Independent evaluation of P_pole (the bracket, i.e. A_6/i's pole part)."""
    tot = F(0)
    for m, (p, q), t, (r, s) in channels():
        wm2 = w[m]*w[m]
        wp2 = w[p]*w[p]
        wq2 = w[q]*w[q]
        wt2 = w[t]*w[t]
        wr2 = w[r]*w[r]
        ws2 = w[s]*w[s]
        QT = wp2 + wq2 - wm2
        if QT <= 0:
            continue
        dT = 2*(w[m] + w[p])*(w[m] + w[q])
        if dT == 0:
            raise ZeroDivisionError("d_T=0 on wall; approach by limit")
        HL = Hblock(min(wm2, QT), wp2, wq2)
        HR = Hblock(min(wt2, QT), wr2, ws2)
        tot += F(-64) * w[m]*w[t]*QT*QT / dT * HL * HR
    return tot

def A6_over_i(w):
    re, im = amp_from_omega_sigma(list(w), SIGMA, g=1)
    assert re == 0, "A6 not purely imaginary at %s: re=%s" % (w, re)
    return im

# ---------- on-shell sampling (standard sheet + sign variants) -------------
def solve_onshell(b, c, d, e):
    """Standard rational parametrization from student-2's note:
       w = (-a, b, c, d, e, -f), S=b+c+d+e,
       a = d+e+(bc-de)/S, f = b+c-(bc-de)/S.
       Returns the 6-tuple w (Fractions) or None if degenerate."""
    b, c, d, e = F(b), F(c), F(d), F(e)
    S = b + c + d + e
    if S == 0:
        return None
    x = (b*c - d*e) / S
    a = d + e + x
    f = b + c - x
    w = (-a, b, c, d, e, -f)
    # verify on-shell
    if sum(w) != 0:
        return None
    if -w[0]**2 - w[1]**2 - w[2]**2 + w[3]**2 + w[4]**2 + w[5]**2 != 0:
        return None
    return w

def word_of(w):
    """8-word chamber label: sort by |w|, read momentum sign (sigma) in that order."""
    order = sorted(range(6), key=lambda i: abs(w[i]))
    return "".join('+' if SIGMA[i] > 0 else '-' for i in order)

def nondegenerate(w):
    if C_of(w) == 0:
        return False
    if Delta_of(w) == 0:
        return False
    # avoid exact pair walls |w_i|==|w_j| across sectors and zero freqs
    if any(x == 0 for x in w):
        return False
    aw = [abs(x) for x in w]
    for i in range(6):
        for j in range(i+1, 6):
            if aw[i] == aw[j]:
                return False
    return True

def Lscale(w):
    """LCM of denominators of the six frequencies."""
    from math import gcd
    L = 1
    for x in w:
        den = x.denominator
        L = L*den//gcd(L, den)
    return L
