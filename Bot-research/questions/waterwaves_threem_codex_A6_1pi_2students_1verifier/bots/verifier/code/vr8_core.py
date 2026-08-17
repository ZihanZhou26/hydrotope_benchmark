#!/usr/bin/env python3
"""Round-8 INDEPENDENT verifier core.

Everything here is transcribed BY HAND from the WRITTEN derivation
    bots/student-1/derivations/s1_010_round8_compact_hinge_candidate.md
(NOT copied from the student's round8_compact_candidate.py evaluator).
The oracle is my own fresh build bg_r8 (md5 of source = shared 41715c...).

Convention (question.md + bg.cpp): the three-minus BG amplitude prints as
A_6 = i * (rational). The candidate is  A_6 = i g^{-3}(P_pole + R_Q + R_0 + R_q),
so  A_6/i * g^3  must equal  (P_pole + R_Q + R_0 + R_q).
"""

from fractions import Fraction as F
from itertools import combinations, permutations
import subprocess, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
BG = os.path.join(HERE, "bg_r8")

MINUS = (0, 1, 2)   # legs 1,2,3  (sigma = -1)
PLUS = (3, 4, 5)    # legs 4,5,6  (sigma = +1)


def pos(x):
    return x if x > 0 else F(0)


# ---------------------------------------------------------------------------
# H-block  H(B;c,d) = B - (B-wc^2)_+ - (B-wd^2)_+ + (B-wc^2-wd^2)_+
# ---------------------------------------------------------------------------
def Hblock(B, c2, d2):
    return B - pos(B - c2) - pos(B - d2) + pos(B - c2 - d2)


# ---------------------------------------------------------------------------
# P_pole  (settled, transcribed from the .md boxed formula)
#   P_pole = -64  sum_{m in M, {p,q} in P, Q>0}
#              w_m w_t Q^2 / d_{m;pq}
#              * H(min(w_m^2,Q); p,q) * H(min(w_t^2,Q); r,s)
#   Q_{m;pq}=w_p^2+w_q^2-w_m^2 ,  d_{m;pq}=2(w_m+w_p)(w_m+w_q),
#   {r,s}=M\{m}, {t}=P\{p,q}.
# ---------------------------------------------------------------------------
def P_pole(w):
    x2 = [z * z for z in w]
    tot = F(0)
    for m in MINUS:
        r, s = [j for j in MINUS if j != m]
        for p, q in combinations(PLUS, 2):
            t = [j for j in PLUS if j not in (p, q)][0]
            Q = x2[p] + x2[q] - x2[m]
            if Q <= 0:
                continue
            d = 2 * (w[m] + w[p]) * (w[m] + w[q])
            if d == 0:
                raise ZeroDivisionError("d_{m;pq}=0 genuine pole")
            left = Hblock(min(x2[m], Q), x2[p], x2[q])
            right = Hblock(min(x2[t], Q), x2[r], x2[s])
            tot += -64 * w[m] * w[t] * Q * Q * left * right / d
    return tot


# ---------------------------------------------------------------------------
# R_Q = -32 sum_{m in M, {p,q} in P} (Q_{m;pq})_+^3 w_m w_t
# ---------------------------------------------------------------------------
def R_Q(w):
    x2 = [z * z for z in w]
    tot = F(0)
    for m in MINUS:
        for p, q in combinations(PLUS, 2):
            t = [j for j in PLUS if j not in (p, q)][0]
            Q = x2[p] + x2[q] - x2[m]
            tot += pos(Q) ** 3 * w[m] * w[t]
    return -32 * tot


# ---------------------------------------------------------------------------
# Seed polynomials H1(a,b,s,v), H2(a,b,s,v,c), H0(u,v,e-,e+)
# transcribed from the LaTeX in the .md.
# ---------------------------------------------------------------------------
def H1(a, b, s, v):
    return 2 * (
        12*s**6 - 21*s**5*a - 22*s**5*b - 115*s**4*v - 48*s**4*a*b - 58*s**4*b**2
        + 36*s**3*v*a + 44*s**3*v*b + 13*s**3*a**3 + 12*s**3*a**2*b - 5*s**3*a*b**2 - 4*s**3*b**3
        + 268*s**2*v**2 + 25*s**2*v*a**2 + 308*s**2*v*a*b + 323*s**2*v*b**2
        - 16*s**2*a**4 - 66*s**2*a**3*b - 62*s**2*a**2*b**2 + 30*s**2*a*b**3 + 42*s**2*b**4
        + 240*s*v**2*a + 240*s*v**2*b - 92*s*v*a**3 + 14*s*v*a**2*b + 328*s*v*a*b**2 + 222*s*v*b**3
        - 64*s*a**4*b - 212*s*a**3*b**2 - 206*s*a**2*b**3 - 32*s*a*b**4 + 26*s*b**5
        - 8*v**3 + 42*v**2*a**2 + 72*v**2*a*b + 30*v**2*b**2
        - 36*v*a**4 - 112*v*a**3*b - 78*v*a**2*b**2 + 36*v*a*b**3 + 38*v*b**4
        + 4*a**6 - 44*a**4*b**2 - 112*a**3*b**3 - 112*a**2*b**4 - 40*a*b**5
    )


def H2(a, b, s, v, c):
    return -4 * (
        4*c*s**2 + 4*c*s*a + 4*c*s*b + 22*c*a**2 + 4*c*a*b - 22*c*b**2
        + 4*s**4 + 4*s**3*a + 4*s**3*b - 8*s**2*v + 12*s**2*a**2 - 16*s**2*b**2
        - 8*s*v*a - 8*s*v*b + s*a**3 - 9*s*a*b**2 - 4*s*b**3
        - 23*v*a**2 + 19*v*b**2 + 12*a**4 + 22*a**3*b - 12*a**2*b**2 - 22*a*b**3
    )


def H0(u, v, em, ep):
    return 16 * (
        69*em**2*v - 126*em*ep*u**2 - 18*em*ep*v - 40*em*u*v**2
        + 42*ep**2*u**2 - 57*ep**2*v - 52*ep*u**5 + 204*ep*u**3*v - 54*ep*u*v**2
        + 4*u**8 - 32*u**6*v + 68*u**4*v**2 - 16*u**2*v**3
    )


# ---------------------------------------------------------------------------
# R_q  (my own independent assembly of the two group sums from the .md)
#   R_q = 4 sum_{m,p} h_{mp} H1(w_m,w_p, w_r+w_s, w_r w_s)
#       + 2 sum_{m,p} sum_phi h_{r,phi(r)} h_{s,phi(s)}
#             H2(w_m,w_p, w_r+w_s, w_r w_s, w_r w_{phi(r)}+w_s w_{phi(s)})
#   h_{ij}=(w_j^2-w_i^2)_+ ,  {r,s}=M\{m}, phi: {r,s}->{P\{p}} 2 bijections.
# ---------------------------------------------------------------------------
def h(i, j, w):
    return pos(w[j] ** 2 - w[i] ** 2)


def R_q(w):
    tot = F(0)
    for m in MINUS:
        r, s = [j for j in MINUS if j != m]
        S = w[r] + w[s]
        V = w[r] * w[s]
        for p in PLUS:
            tz = [j for j in PLUS if j != p]           # {t,z} = P\{p}
            # --- single-hinge term ---
            tot += 4 * h(m, p, w) * H1(w[m], w[p], S, V)
            # --- double-hinge matching term: two bijections phi:{r,s}->{t,z} ---
            for phir, phis in ((tz[0], tz[1]), (tz[1], tz[0])):
                c = w[r] * w[phir] + w[s] * w[phis]
                tot += 2 * h(r, phir, w) * h(s, phis, w) * \
                    H2(w[m], w[p], S, V, c)
    return tot


def R_0(w):
    u = w[0] + w[1] + w[2]
    v = w[0]*w[1] + w[0]*w[2] + w[1]*w[2]
    em = w[0] * w[1] * w[2]
    ep = w[3] * w[4] * w[5]
    return H0(u, v, em, ep)


def stripped(w):
    """(P_pole + R_Q + R_0 + R_q) = A_6/i * g^3 (candidate)."""
    return P_pole(w) + R_Q(w) + R_0(w) + R_q(w)


# ---------------------------------------------------------------------------
# Fresh oracle wrapper (bg_r8), exact rational.
# ---------------------------------------------------------------------------
def _run(args):
    out = subprocess.run([BG] + args, capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise RuntimeError("bg_r8 failed: " + out.stderr + out.stdout)
    return out.stdout


def bg_amp_free(free4, g=1):
    """-n 6 mode: give (w2,w3,w4,w5), bg solves w1,w6. Return (omega6, A6_over_i)."""
    ws = ",".join(str(x) for x in free4)
    txt = _run(["-n", "6", "-w", ws, "-s", "-1,-1,-1,1,1,1", "-g", str(g)])
    om = re.search(r"omega = \{([^}]*)\}", txt).group(1)
    omega = tuple(F(t.strip()) for t in om.split(","))
    m = re.search(r"A_6 = i \* \(([^)]*)\)", txt)
    if not m:
        m2 = re.search(r"A_6 = \(([^)]*)\) \+ i \* \(([^)]*)\)", txt)
        re_part = F(m2.group(1))
        if re_part != 0:
            raise RuntimeError("nonzero real part! " + txt)
        return omega, F(m2.group(2))
    return omega, F(m.group(1))


def bg_amp_explicit(K, W, g=1):
    """--amp mode with explicit six momenta and six frequencies. Return A6/i."""
    ks = ",".join(str(x) for x in K)
    Ws = ",".join(str(x) for x in W)
    txt = _run(["--amp", "-K", ks, "-W", Ws, "-g", str(g)])
    m = re.search(r"A_6 = i \* \(([^)]*)\)", txt)
    if m:
        return F(m.group(1))
    m2 = re.search(r"A_6 = \(([^)]*)\) \+ i \* \(([^)]*)\)", txt)
    if m2:
        if F(m2.group(1)) != 0:
            raise RuntimeError("nonzero real part in --amp: " + txt)
        return F(m2.group(2))
    raise RuntimeError("could not parse: " + txt)


def K_of(w, g=1):
    """on-shell momenta k_i = sigma_i w_i^2 / g."""
    sig = [-1, -1, -1, 1, 1, 1]
    return [sig[i] * w[i] * w[i] / F(g) for i in range(6)]
