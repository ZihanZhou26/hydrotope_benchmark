#!/usr/bin/env python3
"""Round-5 independent verifier core.

Everything here is (re)implemented from the WRITTEN derivations. Amplitudes come
ONLY from my own freshly built oracle bg_r5 (md5-matched shared bg.cpp) in exact
rational mode. All auxiliary arithmetic uses fractions.Fraction. No student
evaluator is imported.

Independent pieces:
  * amp_from_omega  -> A_6/i via fresh bg_r5 --amp (exact GMP)
  * P_pole          -> my own table-free transcription of F9 (authored round 4)
  * R_spline        -> A_6/i - P_pole
  * R_Q             -> my own transcription of the ROUND-5 CANDIDATE brick
                       R_Q = -16 sum_{m,p<q} (Q_{m;pq})_+^3 [ w_m^2 + (q_{mt})_+ ]
  * exact univariate polynomial interpolation (Lagrange over Fraction)
"""
import subprocess, itertools, re, os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BG = os.path.join(HERE, "bg_r5")
SIG = [-1, -1, -1, 1, 1, 1]      # minus legs 1,2,3 ; plus legs 4,5,6 (0-indexed)
M = [0, 1, 2]
P = [3, 4, 5]

def _fmt(x):
    x = F(x)
    return f"{x.numerator}/{x.denominator}" if x.denominator != 1 else str(x.numerator)

# ---------- fresh exact oracle ----------
class SingularError(RuntimeError):
    """BG hit a wall/pole (SIGFPE, rc<0): the point is on a singular locus."""

def amp_from_omega(omega):
    """omega (6 exact freqs, on-shell) -> A_6/i as Fraction via fresh bg_r5."""
    omega = [F(w) for w in omega]
    K = [SIG[i]*omega[i]*omega[i] for i in range(6)]
    ks = ",".join(_fmt(k) for k in K)
    ws = ",".join(_fmt(w) for w in omega)
    out = subprocess.run([BG, "--amp", "-K", ks, "-W", ws, "-g", "1"],
                         capture_output=True, text=True)
    if out.returncode < 0:
        raise SingularError(f"bg SIGFPE rc={out.returncode} (on a wall/pole)")
    if out.returncode != 0:
        raise RuntimeError(f"bg failed rc={out.returncode}: {out.stderr}\n{out.stdout}")
    txt = out.stdout
    m = re.search(r"A_6 = i \* \(([-0-9/]+)\)", txt)
    if m:
        return F(m.group(1))
    m = re.search(r"A_6 = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)", txt)
    if m:
        if F(m.group(1)) != 0:
            raise RuntimeError(f"A_6 has nonzero real part:\n{txt}")
        return F(m.group(2))
    raise RuntimeError(f"could not parse:\n{txt}")

def solve_onshell(w2, w3, w4, w5):
    """Solve omega_1, omega_6 exactly (matches bg.cpp free-leg convention)."""
    free = [F(w2), F(w3), F(w4), F(w5)]
    sig_free = [-1, -1, 1, 1]
    s0 = SIG[0]
    sumFree = sum(free)
    sumSig = sum(sig_free[i]*free[i]*free[i] for i in range(4))
    wn = -(s0*sumFree*sumFree + sumSig)/(2*s0*sumFree)
    w1 = -(sumFree + wn)
    return [w1, free[0], free[1], free[2], free[3], wn]

# ---------- table-free P_pole (my own, from F9) ----------
def pos(x):
    x = F(x)
    return x if x > 0 else F(0)

def Hblock(b, c, d, omega):
    wc2 = omega[c]*omega[c]; wd2 = omega[d]*omega[d]
    return pos(b) - pos(b - wc2) - pos(b - wd2) + pos(b - wc2 - wd2)

def P_pole(omega):
    omega = [F(w) for w in omega]
    total = F(0)
    for m in M:
        mp = [x for x in M if x != m]
        for pq in itertools.combinations(P, 2):
            p, q = pq
            pbar = [x for x in P if x not in pq][0]
            Q_T = omega[p]**2 + omega[q]**2 - omega[m]**2
            if Q_T <= 0:
                continue
            d_T = 2*(omega[m]+omega[p])*(omega[m]+omega[q])
            H1 = Hblock(min(omega[m]**2, Q_T), p, q, omega)
            H2 = Hblock(min(omega[pbar]**2, Q_T), mp[0], mp[1], omega)
            total += omega[m]*omega[pbar]*Q_T*Q_T/d_T * H1 * H2
    return -64*total

def R_spline(omega):
    return amp_from_omega(omega) - P_pole(omega)

# ---------- candidate order-3 Q-brick orbit (my transcription of s2_010 boxed) ----------
def Q_T_val(omega, m, p, q):
    return omega[p]**2 + omega[q]**2 - omega[m]**2

def G_brick(omega, m, p, q):
    """G_{m;pq} = -16 max(w_m^2, w_t^2), t = omitted plus leg."""
    t = [x for x in P if x not in (p, q)][0]
    return -16*max(omega[m]**2, omega[t]**2)

def R_Q(omega):
    """R_Q = -16 sum_{m, p<q} (Q_{m;pq})_+^3 [ w_m^2 + (w_t^2 - w_m^2)_+ ]."""
    omega = [F(w) for w in omega]
    total = F(0)
    for m in M:
        for p, q in itertools.combinations(P, 2):
            t = [x for x in P if x not in (p, q)][0]
            Q = Q_T_val(omega, m, p, q)
            if Q > 0:
                total += Q**3 * (omega[m]**2 + pos(omega[t]**2 - omega[m]**2))
    return -16*total

# ---------- exact univariate polynomial tools (Lagrange over Fraction) ----------
def poly_interp(xs, ys):
    """Return coefficient list [c0,c1,...] of the exact interpolating poly."""
    n = len(xs)
    xs = [F(x) for x in xs]; ys = [F(y) for y in ys]
    coeffs = [F(0)]*n
    for i in range(n):
        # basis poly L_i(x) = prod_{j!=i}(x-xj)/(xi-xj)
        num = [F(1)]  # polynomial coeffs, low->high
        den = F(1)
        for j in range(n):
            if j == i: continue
            # multiply num by (x - xj)
            new = [F(0)]*(len(num)+1)
            for k,c in enumerate(num):
                new[k]   += c*(-xs[j])
                new[k+1] += c
            num = new
            den *= (xs[i]-xs[j])
        scale = ys[i]/den
        for k,c in enumerate(num):
            coeffs[k] += c*scale
    # trim trailing zeros
    while len(coeffs) > 1 and coeffs[-1] == 0:
        coeffs.pop()
    return coeffs

def poly_eval(coeffs, x):
    x = F(x); r = F(0)
    for c in reversed(coeffs):
        r = r*x + c
    return r

def poly_sub(a, b):
    n = max(len(a), len(b))
    a = a + [F(0)]*(n-len(a)); b = b + [F(0)]*(n-len(b))
    r = [a[i]-b[i] for i in range(n)]
    while len(r) > 1 and r[-1] == 0: r.pop()
    return r

def poly_divmod(num, den):
    """Exact polynomial division num/den -> (quot, rem), coeff lists low->high."""
    num = num[:];
    while len(num) > 1 and num[-1] == 0: num.pop()
    den = den[:]
    while len(den) > 1 and den[-1] == 0: den.pop()
    if den == [F(0)]:
        raise ZeroDivisionError
    q = [F(0)]*(max(1, len(num)-len(den)+1))
    while len(num) >= len(den) and not (len(num)==1 and num[0]==0):
        deg = len(num)-len(den)
        c = num[-1]/den[-1]
        q[deg] = c
        for i in range(len(den)):
            num[deg+i] -= c*den[i]
        while len(num) > 1 and num[-1] == 0: num.pop()
    while len(q) > 1 and q[-1] == 0: q.pop()
    return q, num

def line(Pvec, dvec, t):
    return [F(Pvec[i]) + F(dvec[i])*F(t) for i in range(6)]

def on_shell_ok(omega):
    omega = [F(w) for w in omega]
    c1 = sum(omega)
    c2 = sum(SIG[i]*omega[i]**2 for i in range(6))
    return c1 == 0 and c2 == 0

def gen_ts(t_lo, t_hi, n, den=997):
    """Generic rational sample points strictly inside (t_lo,t_hi), large
    denominator so we almost never land exactly on a wall/pole."""
    t_lo = F(t_lo); t_hi = F(t_hi)
    out = []
    for i in range(1, n+1):
        frac = F(i, n+1)
        # nudge by a coprime offset to avoid nice values
        t = t_lo + (t_hi - t_lo)*frac + F(1, den)*F((i*37) % 11 - 5)
        if t_lo < t < t_hi:
            out.append(t)
    return out

def collect(valfn, Pvec, dvec, ts):
    """Evaluate valfn(line(P,d,t)) at each t, skipping SingularError points."""
    xs, ys = [], []
    for t in ts:
        try:
            y = valfn(line(Pvec, dvec, t))
        except SingularError:
            continue
        xs.append(t); ys.append(y)
    return xs, ys
