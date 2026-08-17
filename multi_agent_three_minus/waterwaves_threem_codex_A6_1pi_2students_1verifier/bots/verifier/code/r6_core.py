"""
r6_core.py -- independent verifier pipeline, round 6.

Everything transcribed from the WRITTEN formulas (question.md, summary/logic.yaml
F9/F17). No student evaluator is imported. Amplitudes come ONLY from the fresh
md5-matched oracle bg_r6 in exact GMP rational --amp mode.

Legs (0-indexed): M = {0,1,2} minus (sigma=-1), P = {3,4,5} plus (sigma=+1).
sigma_i = -1 for i in M, +1 for i in P ; k_i = sigma_i * w_i^2 (g=1).
"""
import subprocess, os
from fractions import Fraction as Fr
from itertools import combinations

BG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bg_r6")
SIGMA = [-1, -1, -1, 1, 1, 1]
M = [0, 1, 2]
P = [3, 4, 5]

def _fr(s):
    s = s.strip()
    return Fr(s)

_AMP_CACHE = {}
def amp_over_i(Ws):
    """Return A_6/i as an exact Fraction for frequency 6-tuple Ws (Fractions)."""
    Ws = [Fr(w) for w in Ws]
    ckey = tuple(Ws)
    if ckey in _AMP_CACHE:
        return _AMP_CACHE[ckey]
    K = [SIGMA[i] * Ws[i] * Ws[i] for i in range(6)]
    def fmt(x):
        return f"{x.numerator}/{x.denominator}" if x.denominator != 1 else str(x.numerator)
    Ks = ",".join(fmt(x) for x in K)
    Wsr = ",".join(fmt(x) for x in Ws)
    out = subprocess.run([BG, "--amp", "-K", Ks, "-W", Wsr],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         universal_newlines=True, timeout=120)
    if out.returncode != 0:
        raise RuntimeError(f"bg failed: {out.stderr}\n{out.stdout}")
    txt = out.stdout
    # Expect a purely-imaginary result: "A_6 = i * (val)"
    for line in txt.splitlines():
        line = line.strip()
        if line.startswith("A_6 = i * ("):
            val = _fr(line[len("A_6 = i * ("):].rstrip(")"))
            _AMP_CACHE[ckey] = val
            return val
        if line.startswith("A_6 = (") and "+ i *" in line:
            # (re) + i * (im) -> re must be 0 for this sector; capture im
            re_part = line[len("A_6 = ("):line.index(") + i *")]
            im_part = line[line.index("+ i * (")+len("+ i * ("):].rstrip(")")
            if _fr(re_part) != 0:
                raise RuntimeError(f"non-imaginary A_6! {line}")
            val = _fr(im_part)
            _AMP_CACHE[ckey] = val
            return val
    raise RuntimeError(f"could not parse:\n{txt}")

def pos(x):
    return x if x > 0 else Fr(0)

def Hblock(b, c_idx, d_idx, Ws):
    """H(b; c,d) = sum_{S subseteq {c,d}} (-1)^|S| (b - sum_{j in S} w_j^2)_+ .
    NOTE: per question.md's two-minus template the threshold uses the SUM OF
    SQUARES sum_{j in S} w_j^2, NOT (sum w_j)^2. (logic.yaml's 'omega_S^2'
    shorthand is misleading; the sum-of-squares reading reproduces the verified
    anchor P_pole=42588288/7, the other does not.)"""
    wc, wd = Ws[c_idx], Ws[d_idx]
    return (pos(b)
            - pos(b - wc*wc)
            - pos(b - wd*wd)
            + pos(b - wc*wc - wd*wd))

def channels():
    """Yield (m, p, q, tbar, mp1, mp2) for the 9 triple channels."""
    for m in M:
        others_minus = [x for x in M if x != m]
        for (p, q) in combinations(P, 2):
            tbar = [x for x in P if x not in (p, q)][0]
            yield (m, p, q, tbar, others_minus[0], others_minus[1])

def P_pole(Ws, form=1):
    Ws = [Fr(w) for w in Ws]
    C = Ws[0]*Ws[1]*Ws[2] + Ws[3]*Ws[4]*Ws[5]
    tot = Fr(0)
    for (m, p, q, tbar, mp1, mp2) in channels():
        wm, wp, wq, wt = Ws[m], Ws[p], Ws[q], Ws[tbar]
        QT = wp*wp + wq*wq - wm*wm
        if QT <= 0:
            continue
        Hpq = Hblock(min(wm*wm, QT), p, q, Ws)
        Hmm = Hblock(min(wt*wt, QT), mp1, mp2, Ws)
        if form == 1:
            dT = 2*(wm+wp)*(wm+wq)
            tot += wm*wt*QT*QT/dT * Hpq * Hmm
            pref = -64
        else:  # form 2
            tot += wm*wt*(wm+wt)*QT*QT * Hpq * Hmm
            pref = 0
    if form == 1:
        return -64 * tot
    else:
        return Fr(-32, 1)/C * tot

def R_Q(Ws):
    Ws = [Fr(w) for w in Ws]
    tot = Fr(0)
    for m in M:
        others_minus = [x for x in M if x != m]
        for (p, q) in combinations(P, 2):
            tbar = [x for x in P if x not in (p, q)][0]
            wm, wp, wq, wt = Ws[m], Ws[p], Ws[q], Ws[tbar]
            QT = wp*wp + wq*wq - wm*wm
            tot += pos(QT)**3 * wm * wt
    return -32 * tot

def R_spline(Ws):
    return amp_over_i(Ws) - P_pole(Ws)

def S_resid(Ws):
    return R_spline(Ws) - R_Q(Ws)

def q_wall(m, p, Ws):
    """q_{mp} = w_p^2 - w_m^2 = k_{m,p}."""
    return Ws[p]**2 - Ws[m]**2

def Q_wall(m, p, q, Ws):
    return Ws[p]**2 + Ws[q]**2 - Ws[m]**2

if __name__ == "__main__":
    anchor = [Fr(-8), Fr(2), Fr(3), Fr(4), Fr(5), Fr(-6)]
    a = amp_over_i(anchor)
    pp1 = P_pole(anchor, 1)
    pp2 = P_pole(anchor, 2)
    rs = a - pp1
    rq = R_Q(anchor)
    print("A6/i      =", a, " expect -9190656/7")
    print("P_pole f1 =", pp1, " expect 42588288/7")
    print("P_pole f2 =", pp2, " (must equal f1)")
    print("R_spline  =", rs, " expect -7396992")
    print("R_Q       =", rq, " (s1_008 anchor: -136630560)")
    print("S         =", rs - rq, " (s1_008 anchor: 129233568)")
