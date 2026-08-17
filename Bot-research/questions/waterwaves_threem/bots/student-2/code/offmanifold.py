#!/usr/bin/env python3
"""Is A_6 * D_9 polynomial OFF the resonant manifold (all 6 freqs free)?

If yes, N_6 = A_6*D_9 can be fit as a genuine 6-variable polynomial (symmetry
shrinks the basis), bypassing the manifold-ideal ambiguity. We test on a 1-D
line held inside a single chamber (signs of all absR-arguments fixed) and check
A_6*D_9 is a polynomial in the line parameter t (exact rational interpolation:
fit deg d through d+1 pts, predict more exactly).
"""
import subprocess, os, re
from fractions import Fraction as F
import r4lib

HERE = os.path.dirname(os.path.abspath(__file__))
BG = os.path.join(HERE, "bg")
SIG = [-1, -1, -1, 1, 1, 1]


def amp_raw(omega):
    """A_6 via --amp at arbitrary 6 freqs (k_i = sigma_i omega_i^2). Returns im (A/i)."""
    K = [F(SIG[i]) * F(omega[i]) ** 2 for i in range(6)]
    W = [F(omega[i]) for i in range(6)]
    cmd = [BG, "--amp", "-K", ",".join(str(x) for x in K),
           "-W", ",".join(str(x) for x in W), "-g", "1"]
    out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
    m = re.search(r"A_6 = i \* \(([-0-9/]+)\)", out)
    if m:
        return F(m.group(1))
    m = re.search(r"A_6 = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)", out)
    if m:
        # has real part; return None to signal off-sector
        return ("CPLX", F(m.group(1)), F(m.group(2)))
    raise RuntimeError("parse fail: " + out)


def D9(omega):
    w = {i + 1: F(omega[i]) for i in range(6)}
    d = F(1)
    for i in (1, 2, 3):
        for j in (4, 5, 6):
            d *= (w[i] + w[j])
    return d


def fit_poly_exact(ts, vs, d):
    """Try exact polynomial of degree d through first d+1 pts; check it predicts the rest."""
    import sympy as sp
    pts = list(zip(ts, vs))
    if len(pts) < d + 2:
        return None
    xs = [sp.Rational(t.numerator, t.denominator) for t, _ in pts[:d + 1]]
    ys = [sp.Rational(v.numerator, v.denominator) for _, v in pts[:d + 1]]
    x = sp.Symbol('x')
    poly = sp.interpolate(list(zip(xs, ys)), x)
    for t, v in pts[d + 1:]:
        if sp.expand(poly.subs(x, sp.Rational(t.numerator, t.denominator))) != sp.Rational(v.numerator, v.denominator):
            return False
    return True


if __name__ == "__main__":
    import sympy as sp
    # base point clearly in a generic chamber, off-manifold
    base = [F(-28, 5), F(2), F(3), F(5), F(-22, 5), F(13, 7)]  # arbitrary, NOT on manifold
    # line: vary omega_4 = 5 + t (keep others fixed) -> stays off-manifold, signs fixed for small range
    ts = [F(k, 13) for k in range(1, 16)]  # small rational steps
    vs = []
    good_ts = []
    for t in ts:
        om = list(base); om[3] = base[3] + t  # vary leg 4
        try:
            a = amp_raw(om)
            if isinstance(a, tuple):
                print("complex at t=", t); continue
            d9 = D9(om)
            vs.append(a * d9)
            good_ts.append(t)
        except subprocess.CalledProcessError:
            print("SIGFPE at t=", t)
    print(f"collected {len(vs)} points")
    # Is A_6*D_9 polynomial in t?
    for d in range(0, 20):
        r = fit_poly_exact(good_ts, vs, d)
        if r is True:
            print(f"A_6*D_9 IS polynomial in t, degree <= {d}")
            break
        if r is False:
            continue
    else:
        print("A_6*D_9 NOT polynomial up to degree 19 along this line")
    # Also test A_6 alone (should be rational, not poly)
    vs_a = []
    for t in good_ts:
        om = list(base); om[3] = base[3] + t
        vs_a.append(amp_raw(om))
    for d in range(0, 20):
        r = fit_poly_exact(good_ts, vs_a, d)
        if r is True:
            print(f"A_6 alone IS polynomial degree <= {d} (unexpected)")
            break
    else:
        print("A_6 alone NOT polynomial up to degree 19 (expected: rational)")
