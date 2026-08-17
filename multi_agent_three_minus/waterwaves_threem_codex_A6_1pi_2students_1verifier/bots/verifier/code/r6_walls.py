"""
r6_walls.py -- round-6 wall-crossing harness.

Re-confirm R_Q globally: on on-shell polynomial lines crossing an ISOLATED
Q-wall, S = R_spline - R_Q must be a SINGLE polynomial (no jump), while
R_spline itself jumps at order 3. And across an isolated q-wall S must jump
at order exactly 1.

Uses r6_core (correct sumsq P_pole, -32 monomial R_Q) for the pipeline and
r5_core only for the pure-arithmetic on-shell-line / exact-polynomial helpers.
"""
from fractions import Fraction as Fr
from itertools import combinations
import r6_core as C
from r5_core import (line, on_shell_ok, poly_interp, poly_eval, poly_sub,
                     poly_divmod, SingularError)

M, P = [0, 1, 2], [3, 4, 5]

def q_walls():
    return [(m, p) for m in M for p in P]           # 9 pair walls

def Q_walls():
    return [(m, p, q) for m in M for (p, q) in combinations(P, 2)]  # 9 triple walls

def wall_crossings(Pv, dv, t_lo, t_hi):
    """Return sorted list of (t_cross, kind, label) where a q- or Q-wall value
    changes sign strictly inside (t_lo,t_hi). Values are exact linear/quadratic
    in t so we just root-find on the polynomial."""
    crossings = []
    def add_roots(coeffs, kind, label):
        # coeffs low->high in t (degree<=2 here); find real rational roots in window
        # sample sign changes on a fine rational grid then refine by exact factor.
        # Since q,Q are quadratics in t, solve exactly.
        import math
        c = [Fr(x) for x in coeffs]
        while len(c) > 1 and c[-1] == 0:
            c.pop()
        deg = len(c)-1
        roots = []
        if deg == 1:
            r = -c[0]/c[1]
            roots = [r]
        elif deg == 2:
            a, b, cc = c[2], c[1], c[0]
            disc = b*b - 4*a*cc
            if disc >= 0:
                s = math.isqrt(disc.numerator) if disc.denominator == 1 else None
                # rational root only if disc is a perfect square rational
                dn, dd = disc.numerator, disc.denominator
                rn = math.isqrt(dn); rd = math.isqrt(dd)
                if rn*rn == dn and rd*rd == dd:
                    sq = Fr(rn, rd)
                    roots = [(-b+sq)/(2*a), (-b-sq)/(2*a)]
                else:
                    roots = []  # irrational crossing; skip (won't be a nice test wall)
        for r in roots:
            if t_lo < r < t_hi:
                crossings.append((r, kind, label))
    for (m, p) in q_walls():
        # q_{mp}(t) = w_p^2 - w_m^2 as poly in t
        wp = (Pv[p], dv[p]); wm = (Pv[m], dv[m])
        # (Pp+dp t)^2 - (Pm+dm t)^2
        coeffs = [Fr(wp[0])**2 - Fr(wm[0])**2,
                  2*(Fr(wp[0])*Fr(wp[1]) - Fr(wm[0])*Fr(wm[1])),
                  Fr(wp[1])**2 - Fr(wm[1])**2]
        add_roots(coeffs, "q", (m, p))
    for (m, p, q) in Q_walls():
        wp = (Fr(Pv[p]), Fr(dv[p])); wq = (Fr(Pv[q]), Fr(dv[q])); wm = (Fr(Pv[m]), Fr(dv[m]))
        coeffs = [wp[0]**2 + wq[0]**2 - wm[0]**2,
                  2*(wp[0]*wp[1] + wq[0]*wq[1] - wm[0]*wm[1]),
                  wp[1]**2 + wq[1]**2 - wm[1]**2]
        add_roots(coeffs, "Q", (m, p, q))
    crossings.sort(key=lambda z: z[0])
    return crossings

def sample_poly(fn, Pv, dv, ts):
    xs, ys = [], []
    for t in ts:
        om = line(Pv, dv, t)
        try:
            ys.append(fn(om)); xs.append(t)
        except SingularError:
            pass
        except RuntimeError as e:
            if "SIGFPE" in str(e) or "rc=" in str(e):
                pass
            else:
                raise
    return xs, ys

def fit_and_check(fn, Pv, dv, t_lo, t_hi, deg=8, npts=14):
    """Fit degree-`deg` poly to `fn` on a window; return (coeffs, max_holdout_resid)."""
    # sample npts+deg+2 generic points, fit on first deg+1, test rest
    span = t_hi - t_lo
    ts = [t_lo + span*Fr(i, npts+deg+3) for i in range(1, npts+deg+2)]
    xs, ys = sample_poly(fn, Pv, dv, ts)
    if len(xs) < deg+1:
        return None, None
    coeffs = poly_interp(xs[:deg+1], ys[:deg+1])
    maxr = Fr(0)
    for x, y in zip(xs[deg+1:], ys[deg+1:]):
        r = abs(poly_eval(coeffs, x) - y)
        if r > maxr:
            maxr = r
    return coeffs, maxr
