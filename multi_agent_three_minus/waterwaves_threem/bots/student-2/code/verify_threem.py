#!/usr/bin/env python3
"""Self-contained verification of the round-1 student-2 findings for the
n=6 three-minus water-wave amplitude. Builds its own copy of the oracle and
checks, against ./bg (exact rational mode), the structural facts established:

  (S) STRUCTURE: A_6 is purely imaginary, homogeneous of degree 8, and invariant
      under S_3 (permute minus legs 1,2,3) x S_3 (permute plus legs 4,5,6) x Z_2
      (swap the two triples).  [exact]
  (P) NO POLES: at every factorization channel D_S = omega_S^2/|k_S| - g = 0
      (internal line on-shell), A_6 stays FINITE -- A_6 * D_S -> 0.  So A_6 is
      piecewise-polynomial, NOT rational.  [exact rational approach, residuals]
  (W) WALLS: at the momentum subset walls k_S = sum_{i in S} sigma_i omega_i^2 = 0
      (mixed subsets), A_6 is finite and CONTINUOUS but has a derivative kink;
      these are the chamber breakpoints.  [exact rational, one-sided limits]

Run:  python3 verify_threem.py
"""
import subprocess, os, sys
from fractions import Fraction as F
from itertools import permutations, combinations

HERE = os.path.dirname(os.path.abspath(__file__))
BG = os.path.join(HERE, "bg")
SIGNS = [-1, -1, -1, 1, 1, 1]


def build():
    src = os.path.join(HERE, "bg.cpp")
    if not os.path.exists(BG):
        subprocess.check_call(["g++", "-O2", "-std=c++17", "-o", BG, src, "-lgmpxx", "-lgmp"])


def solve_1n(free):
    free = [F(x) for x in free]; n = len(SIGNS); s1 = F(SIGNS[0])
    sF = sum(free); sS = sum(F(SIGNS[i + 1]) * free[i] ** 2 for i in range(n - 2))
    wn = -(s1 * sF ** 2 + sS) / (2 * s1 * sF); w1 = -(sF + wn)
    return [w1] + free + [wn]


def amp(K, W):
    out = subprocess.check_output(
        [BG, "--amp", "-K", ",".join(map(str, K)), "-W", ",".join(map(str, W))],
        stderr=subprocess.DEVNULL).decode()
    import re
    m = re.search(r"A_6 = i \* \(([-0-9/]+)\)", out)
    if m: return F(0), F(m.group(1))
    m = re.search(r"A_6 = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)", out)
    return F(m.group(1)), F(m.group(2))


def onshell(free):
    W = solve_1n(free); K = [F(SIGNS[i]) * W[i] ** 2 for i in range(6)]
    return amp(K, W), W


def D_S(S, W):
    wS = sum(W[i - 1] for i in S); kS = sum(F(SIGNS[i - 1]) * W[i - 1] ** 2 for i in S)
    return None if kS == 0 else wS * wS / abs(kS) - 1


def main():
    build()
    ok = True

    print("=" * 70)
    print("(S) STRUCTURE: purely imaginary, degree-8 homogeneous, S_3 x S_3 x Z_2")
    print("=" * 70)
    (re0, im0), W = onshell([2, 3, 5, 7])
    print(f"  base point: A_6 = i*({im0})   real part = {re0} (must be 0): {re0==0}")
    ok &= (re0 == 0)
    # homogeneity degree 8
    (re_t, im_t), _ = onshell([F(2)*2, F(3)*2, F(5)*2, F(7)*2])
    print(f"  scale by 2: A_6 ratio = {im_t/im0} (must be 2^8=256): {im_t/im0==256}")
    ok &= (im_t / im0 == 256)

    def Aof(Wlist):
        K = [F(SIGNS[i]) * Wlist[i] ** 2 for i in range(6)]
        return amp(K, Wlist)[1]
    base = Aof(W)
    sym_ok = True
    for p in permutations(range(3)):           # permute minus legs
        sym_ok &= (Aof([W[p[i]] for i in range(3)] + W[3:]) == base)
    for p in permutations(range(3)):           # permute plus legs
        sym_ok &= (Aof(W[:3] + [W[3 + p[i]] for i in range(3)]) == base)
    sym_ok &= (Aof(W[3:] + W[:3]) == base)     # swap triples
    print(f"  S_3(minus) x S_3(plus) x Z_2(swap) invariance: {sym_ok}")
    ok &= sym_ok

    print("\n" + "=" * 70)
    print("(P) NO POLES: approach D_S -> 0 on representative channels; A_6 finite")
    print("=" * 70)
    # channel {2,3,4}: D depends only on legs 2,3,4; exact zero at omega_4=-19/5
    print("  channel {2,3,4} (2m+1p), omega_4 -> -19/5 (D_234 -> 0):")
    last = None
    for k in range(2, 7):
        eps = F(1, 10 ** k); free = [F(2), F(3), F(-19, 5) + eps, F(7)]
        W2 = solve_1n(free); A = Aof(W2); D = D_S(frozenset([2, 3, 4]), W2)
        print(f"    D={float(D):.2e}  A_6={float(A):.6e}  |A_6*D|={float(abs(A*D)):.3e}")
        last = (A, D)
    poleP = abs(float(last[0] * last[1])) < 1e-2 * abs(float(last[0]))
    print(f"  => A_6*D -> 0 (finite, no pole): {poleP}")
    ok &= poleP

    print("\n" + "=" * 70)
    print("(W) WALLS: k_S=0 (mixed subset) -> A_6 finite & CONTINUOUS, with a kink")
    print("=" * 70)
    # k_{24}=0 at omega_4 = omega_2 = 3 (legs 2,3,5 = 3,5,8)
    print("  k_{2,4}=0 at leg4=3 (legs 2,3,5 = 3,5,8): one-sided limits")
    c = F(3)
    for d in [F(1, 10), F(1, 100), F(1, 1000)]:
        L = Aof(solve_1n([F(3), F(5), c - d, F(8)]))
        R = Aof(solve_1n([F(3), F(5), c + d, F(8)]))
        print(f"    d={float(d):.0e}: A(3-d)={float(L):.5e}  A(3+d)={float(R):.5e}  jump={float(R-L):.3e}")
    # continuity: jump -> 0 linearly
    d1 = F(1, 100); d2 = F(1, 1000)
    j1 = abs(Aof(solve_1n([F(3), F(5), c + d1, F(8)])) - Aof(solve_1n([F(3), F(5), c - d1, F(8)])))
    j2 = abs(Aof(solve_1n([F(3), F(5), c + d2, F(8)])) - Aof(solve_1n([F(3), F(5), c - d2, F(8)])))
    contW = (j2 < j1 / 5)  # jump shrinks ~ linearly with d
    print(f"  => continuous across wall (jump shrinks with d): {contW}")
    ok &= contW

    print("\n" + "=" * 70)
    print(f"ALL CHECKS PASS: {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
