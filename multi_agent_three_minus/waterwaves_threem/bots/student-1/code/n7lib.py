#!/usr/bin/env python3
"""n=7 three-minus shared library (student-1, round 7).

Sector: minus legs {1,2,3} (0-indexed 0,1,2), plus legs {4,5,6,7} (0-indexed 3,4,5,6).
On-shell (oracle solve): free = (w2,w3,w4,w5,w6) = 5 free freqs (legs 2..6);
legs 1,7 solved from sum w = 0 and sum sigma w^2 = 0.
  free legs: w2,w3 MINUS;  w4,w5,w6 PLUS.   solved: w1 MINUS, w7 PLUS.

Amplitude:  A_7 = i * 2^6 g^{-3-... } ... ->  A_7 = i 2^{n-1} g^{3-n} N_7 / D_7,  n=7, g=1:
  A_7 = i * 2^6 * N_7 / D_7 = i*64*N_7/D_7,   D_7 = prod_{i in M, j in P}(w_i+w_j) (12 pairs).
So  N_7 = im(A_7) * D_7 / 64.

Mixed subset-sum walls k_S = sum_{i in S} sigma_i w_i^2 = 0 reduce (mod complement
k_S = -k_{S^c} on the manifold) to THREE orbit types under S_3(minus) x S_4(plus):
  (1=1)  a_i = b_j                 [12 walls]   f = b_j - a_i
  (1=2)  a_i = b_j + b_k           [18 walls]   f = b_j+b_k - a_i
  (1=3)  a_i = b_j + b_k + b_l      [12 walls]  f = b_j+b_k+b_l - a_i
(a_i=w_i^2 minus, b_j=w_j^2 plus.)  Total 42 wall functions; each a distinct locus.
The (2=1) walls a_p+a_q=b_j are the SAME loci as (1=3) by complement, so already covered.
"""
from fractions import Fraction as F
import itertools, os, subprocess
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
BG = os.path.join(HERE, "bg")
SIG7 = [-1, -1, -1, 1, 1, 1, 1]
MINUS = [0, 1, 2]            # legs 1,2,3
PLUS = [3, 4, 5, 6]          # legs 4,5,6,7

# ---------- on-shell solve (same as bg.cpp) ----------
def solve_squares(free):
    """free = (w2,w3,w4,w5,w6) -> oms = [w1..w7] (Fractions), or None if degenerate."""
    free = [F(x) for x in free]
    s1 = F(-1)
    sumFree = sum(free)
    if sumFree == 0:
        return None
    # signs of legs 2..6 = -1,-1,1,1,1
    sumSig = (-1)*free[0]**2 + (-1)*free[1]**2 + free[2]**2 + free[3]**2 + free[4]**2
    w7 = -(s1*sumFree**2 + sumSig)/(2*s1*sumFree)
    w1 = -(sumFree + w7)
    return [w1, free[0], free[1], free[2], free[3], free[4], w7]

# ---------- denominator ----------
def D7(oms):
    d = F(1)
    for i in MINUS:
        for j in PLUS:
            d *= (oms[i] + oms[j])
    return d

def N7_from_im(oms, im):
    """N_7 = im(A_7) * D_7 / 64."""
    return F(im) * D7(oms) / 64

# ---------- batch oracle (exact) ----------
def batch_amp(list_of_free):
    """Return list of im(A_7) (Fraction) or None, via ./bg --batch (exact GMP)."""
    lines = []
    for free in list_of_free:
        lines.append("7|" + ",".join(str(F(x)) for x in free) + "|" +
                     ",".join(str(s) for s in SIG7))
    out = subprocess.run([BG, "--batch"], input="\n".join(lines).encode(),
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode()
    res = []
    for ln in out.strip().split("\n"):
        if ln == "ERR" or ln == "":
            res.append(None); continue
        re_s, im_s = ln.split(";")
        res.append(F(im_s))
    return res

def amp_one(free, double=False):
    """single exact (or double) amplitude via ./bg -n 7."""
    cmd = [BG] + (["--double"] if double else []) + [
        "-n", "7", "-w", ",".join(str(F(x)) for x in free),
        "-s", ",".join(str(s) for s in SIG7), "-g", "1"]
    out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
    import re
    if double:
        m = re.search(r"A_7 \(double\) = ([-0-9.eE+]+) \+ ([-0-9.eE+]+) i", out)
        return float(m.group(2))
    m = re.search(r"A_7 = i \* \(([-0-9/]+)\)", out)
    if m:
        return F(m.group(1))
    m = re.search(r"A_7 = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)", out)
    return F(m.group(2))

# ---------- wall functions ----------
def wall_list():
    """Return list of ('11'/'12'/'13', S_minus_tuple, S_plus_tuple) describing the 42 walls."""
    W = []
    for i in MINUS:
        for j in PLUS:
            W.append(('11', (i,), (j,)))
        for (j, k) in itertools.combinations(PLUS, 2):
            W.append(('12', (i,), (j, k)))
        for (j, k, l) in itertools.combinations(PLUS, 3):
            W.append(('13', (i,), (j, k, l)))
    return W

WALLS = wall_list()

def wall_value(w, sq):
    """signed value of wall function: sum_{plus} b - sum_{minus} a (so wall = 0)."""
    typ, sm, sp_ = w
    v = F(0)
    for j in sp_:
        v += sq[j]
    for i in sm:
        v -= sq[i]
    return v

def signature(oms, with_orderings=True):
    """(tuple of 42 wall signs) [+ same-type orderings]; None if ON a wall/tie."""
    sq = [w*w for w in oms]
    sgn = []
    for w in WALLS:
        v = wall_value(w, sq)
        if v == 0:
            return None
        sgn.append(1 if v > 0 else -1)
    if not with_orderings:
        return tuple(sgn)
    # same-type orderings (analytic at n=6, but track for safety)
    a = [sq[i] for i in MINUS]; b = [sq[j] for j in PLUS]
    oa = tuple(1 if a[i] > a[j] else -1 for i, j in itertools.combinations(range(3), 2))
    ob = tuple(1 if b[i] > b[j] else -1 for i, j in itertools.combinations(range(4), 2))
    if 0 in [a[i]-a[j] for i,j in itertools.combinations(range(3),2)]: return None
    if 0 in [b[i]-b[j] for i,j in itertools.combinations(range(4),2)]: return None
    return tuple(sgn) + oa + ob

# ---------- F-const slice (vary leg p = A+t, compensate leg q = B-t) ----------
def fc_free(base_free, p, q, A, B, tt):
    """base_free = list of 5 free values; set free[p]=A+tt, free[q]=B-tt (others fixed)."""
    fr = list(F(x) for x in base_free)
    fr[p] = F(A) + tt
    fr[q] = F(B) - tt
    return fr

if __name__ == "__main__":
    # smoke test vs ./bg and pybg
    import pybg
    free = [F(2), F(3), F(5), F(7), F(11,2)]
    oms = solve_squares(free)
    im_b = amp_one(free)
    im_p, _, _ = pybg.amp_onshell(free, SIG7)
    print("oms =", [str(x) for x in oms])
    print("im(A7) ./bg =", im_b)
    print("im(A7) pybg =", im_p, " match:", im_b == im_p)
    print("D7 =", D7(oms))
    print("N7 =", N7_from_im(oms, im_b))
    print("#walls =", len(WALLS), " sig len =", len(signature(oms)))
    # batch test
    res = batch_amp([free, [F(2),F(3),F(5),F(7),F(13,2)]])
    print("batch:", res[0] == im_b, res)
