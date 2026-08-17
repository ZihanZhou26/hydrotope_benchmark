#!/usr/bin/env python3
"""PI round-3 INDEPENDENT resolution of the gate conflict:
   is A_n (three-minus) piecewise-POLYNOMIAL (student-2 / gate) or
   piecewise-RATIONAL (student-1)?

Fully self-contained: my own on-shell solve (transcribed from bg.cpp:155-161),
my own exact polynomial fit (Fraction Gaussian elimination), my own chamber
check. Calls only my own ./bg (bots/pi/code/bg) in EXACT rational --amp mode.
Does NOT import any student module.

Logic of the test (student-1's, re-derived and re-implemented by me):
  The oracle eliminates legs 1 and n via the on-shell solve, in which the solved
  frequencies are (deg<=2 poly)/sumFree, sumFree = sum of the n-2 free freqs.
  If A_n were a homogeneous degree-(2n-4) POLYNOMIAL in the n frequencies, then
  on any 1-D line in the free-freq space, A_n * sumFree^(2n-4) is a polynomial in
  the line parameter t of degree <= 2*(2n-4).  In particular some p <= 2n-4 makes
  A_n * sumFree^p polynomial.  If NO p (up to a generous bound) works while we
  stay strictly inside ONE chamber, A_n is rational.
Control: run the identical test at n=5, where A_5 is KNOWN polynomial -> must
return POLYNOMIAL.  This certifies the method.
"""
import subprocess, re
from fractions import Fraction as F

BG = "./bg"

# ---- exact polynomial linear algebra (Fraction Gaussian elimination) ----
def solve_linear(A, b):
    """Solve A x = b exactly over the rationals. A: list of rows. Returns x or None if inconsistent/singular."""
    n = len(A); m = len(A[0])
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    # forward elimination
    r = 0
    piv_cols = []
    for c in range(m):
        # find pivot
        pr = None
        for i in range(r, n):
            if M[i][c] != 0:
                pr = i; break
        if pr is None:
            continue
        M[r], M[pr] = M[pr], M[r]
        inv = M[r][c]
        M[r] = [x / inv for x in M[r]]
        for i in range(n):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b_ for a, b_ in zip(M[i], M[r])]
        piv_cols.append(c); r += 1
        if r == n: break
    # check consistency for rows beyond rank
    for i in range(r, n):
        if M[i][m] != 0 and all(M[i][c] == 0 for c in range(m)):
            return None
    if len(piv_cols) < m:
        return "underdetermined"
    x = [F(0)] * m
    for idx, c in enumerate(piv_cols):
        x[c] = M[idx][m]
    return x

def fit_poly_exact(ts, ys, deg):
    """Fit y = sum_{i=0}^{deg} c_i t^i exactly to the first deg+1 points; verify on the rest.
       Returns True iff a polynomial of given degree reproduces ALL points exactly."""
    if len(ts) < deg + 1:
        return None
    A = [[t ** i for i in range(deg + 1)] for t in ts[:deg + 1]]
    bb = ys[:deg + 1]
    sol = solve_linear(A, bb)
    if sol is None or sol == "underdetermined":
        return False
    for t, y in zip(ts[deg + 1:], ys[deg + 1:]):
        val = sum(c * t ** i for i, c in enumerate(sol))
        if val != y:
            return False
    return True

# ---- on-shell solve, transcribed from bg.cpp runMode (lines 155-161) ----
def onshell(freeW, sig):
    """freeW: list of n-2 Fractions; sig: list of n signs (+/-1). Returns (W,K) 1-based-as-0-based lists or None."""
    N = len(sig)
    assert len(freeW) == N - 2
    s0 = sig[0]
    if sig[0] + sig[N - 1] != 0:
        return None
    sumFree = sum(freeW)
    if sumFree == 0:
        return None
    sumSig = sum(sig[i + 1] * freeW[i] * freeW[i] for i in range(N - 2))
    wn = -(s0 * sumFree * sumFree + sumSig) / (2 * s0 * sumFree)
    w1 = -(sumFree + wn)
    W = [w1] + list(freeW) + [wn]
    K = [sig[i] * W[i] * W[i] for i in range(N)]   # g=1
    return W, K

# ---- call my own oracle, exact rational --amp ----
def amp(K, W, g=1):
    Ks = ",".join(str(F(k)) for k in K)
    Ws = ",".join(str(F(w)) for w in W)
    out = subprocess.run([BG, "--amp", "-K", Ks, "-W", Ws, "-g", str(g)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if out.returncode != 0:
        return None  # SIGFPE on a wall/channel
    t = out.stdout
    m = re.search(r"A_\d+ = i \* \(([-0-9/]+)\)", t)
    if m: return F(m.group(1))
    m = re.search(r"A_\d+ = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)", t)
    if m:
        re_, im_ = F(m.group(1)), F(m.group(2))
        assert re_ == 0, f"unexpected real part {re_}"
        return im_
    raise RuntimeError("parse fail: " + t)

# ---- chamber signature: all k_S signs, all leg signs, all pairwise omega^2 orderings ----
from itertools import combinations
def chamber_sig(W, sig):
    N = len(W)
    K = [sig[i] * W[i] * W[i] for i in range(N)]
    s = []
    # signs of every nonempty proper subset momentum sum (the wall arrangement)
    for r in range(1, N):
        for S in combinations(range(N), r):
            kS = sum(K[i] for i in S)
            s.append(1 if kS > 0 else (-1 if kS < 0 else 0))
    # leg signs
    for i in range(N):
        s.append(1 if W[i] > 0 else (-1 if W[i] < 0 else 0))
    # pairwise omega^2 orderings within each type group is captured by full subset-sum signs above
    return tuple(s)

# =====================================================================
def run_test(N, sig, base_free, direction, label, pmax=14, half=40, denom=120):
    print("=" * 72)
    print(f"{label}: n={N}, sigma={sig}")
    # collect in-chamber points along the line base + t*direction
    sig0 = None
    pts = []
    for k in range(-half, half + 1):
        t = F(k, denom)
        free = [base_free[i] + t * direction[i] for i in range(N - 2)]
        sol = onshell(free, sig)
        if sol is None:
            continue
        W, K = sol
        if any(w == 0 for w in W):
            continue
        if any(sum(K[i] for i in S) == 0 for r in range(1, N) for S in combinations(range(N), r)):
            continue  # on a wall exactly -> oracle SIGFPE; skip
        cs = chamber_sig(W, sig)
        if sig0 is None:
            sig0 = cs
        if cs != sig0:
            continue  # crossed a wall: drop
        a = amp(K, W)
        if a is None:
            continue
        sumFree = sum(free)
        pts.append((t, sumFree, a))
    print(f"  in-chamber exact points collected: {len(pts)}")
    if len(pts) < 30:
        print("  !! too few points; widen the line or pick another chamber")
    ts = [p[0] for p in pts]
    base_deg = 2 * N - 4
    found = None
    for p in range(0, pmax + 1):
        deg = base_deg + p   # A_n * sumFree^p as polynomial in t: degree <= 2*(2N-4)? we test <= base_deg+p generously
        ys = [a * sF ** p for (t, sF, a) in pts]
        ok = fit_poly_exact(ts, ys, deg)
        flag = "  <-- POLYNOMIAL" if ok else ""
        if p <= base_deg or ok:
            print(f"  A_{N} * sumFree^{p} polynomial of deg {deg}? {ok}{flag}")
        if ok and found is None:
            found = p
    verdict = "POLYNOMIAL" if found is not None else "RATIONAL"
    print(f"  VERDICT: A_{N} is {verdict}" + (f" (first working p={found})" if found is not None else
          f" (no p<= {pmax} works; a true degree-{base_deg} polynomial needs p<= {base_deg})"))
    return verdict

if __name__ == "__main__":
    # ---- CONTROL: n=5 three-minus (KNOWN polynomial). sigma=(-1,-1,-1,1,1). ----
    run_test(5, [-1, -1, -1, 1, 1],
             base_free=[F(2), F(3), F(5)], direction=[F(0), F(0), F(1)],
             label="CONTROL n=5 (known polynomial)")
    print()
    # ---- TARGET: n=6 three-minus. sigma=(-1,-1,-1,1,1,1). ----
    run_test(6, [-1, -1, -1, 1, 1, 1],
             base_free=[F(2), F(3), F(5), F(7)], direction=[F(0), F(0), F(1), F(0)],
             label="TARGET n=6 (gate says POLY; student-1 says RATIONAL)")
    print()
    # a second n=6 chamber/direction for robustness
    run_test(6, [-1, -1, -1, 1, 1, 1],
             base_free=[F(1), F(-27, 10), F(43, 10), F(12, 5)], direction=[F(1), F(0), F(0), F(0)],
             label="TARGET n=6 (second chamber, different direction)")
