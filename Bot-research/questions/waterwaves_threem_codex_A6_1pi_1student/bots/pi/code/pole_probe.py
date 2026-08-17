#!/usr/bin/env python3
"""PI check: does A_6 genuinely DIVERGE on a factorization surface h_S=0
(internal line on shell, omega_S^2 = g|k_S|)?  If A_6 ~ 1/h_S the pole is
genuine; if A_6*h_S -> 0 it is removable.  Complements the algebraic
non-polynomiality result (rank 18 > 17)."""
import subprocess, re
from fractions import Fraction as F

BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code/bg"
SIG = [-1, -1, -1, 1, 1, 1]


def bg_amp(omega, g=F(1)):
    K = [SIG[i] * omega[i] * omega[i] / g for i in range(6)]
    p = subprocess.run([BG, "--amp", "-K", ",".join(str(x) for x in K),
                        "-W", ",".join(str(x) for x in omega), "-g", str(g)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if p.returncode != 0:
        return None
    m = re.search(r"A_6 = i \* \(([^)]*)\)", p.stdout)
    if m:
        return F(m.group(1))
    m2 = re.search(r"A_6 = \(([^)]*)\) \+ i \* \(([^)]*)\)", p.stdout)
    return F(m2.group(2)) if m2 else None


def solve_onshell(free):
    fr = [F(x) for x in free]
    s = sum(fr)
    if s == 0:
        return None
    ss = sum(SIG[i + 1] * fr[i] ** 2 for i in range(4))
    wn = -(SIG[0] * s * s + ss) / (2 * SIG[0] * s)
    w1 = -(s + wn)
    return [w1, fr[0], fr[1], fr[2], fr[3], wn]


def hS(om, S):
    """h_S = (sum_S omega)^2 - |sum_S sigma omega^2|  (pole when 0)."""
    wsum = sum(om[i] for i in S)
    q = sum(SIG[i] * om[i] ** 2 for i in S)
    return wsum * wsum - abs(q)


def approach(S, base_free, ax, label):
    """Vary free[ax]; bisect for h_S=0 in the free coordinate, then approach two-sided."""
    lo, hi = F(base_free[ax]), F(base_free[ax]) + F(4)
    def hval(x):
        f = list(base_free); f[ax] = x
        om = solve_onshell(f)
        return (om, hS(om, S)) if om else (None, None)
    om, hlo = hval(lo)
    _, hhi = hval(hi)
    # find a sign change
    steps = 0
    while hlo is not None and hhi is not None and (hlo > 0) == (hhi > 0) and steps < 40:
        hi += F(1, 2); _, hhi = hval(hi); steps += 1
    if hlo is None or hhi is None or (hlo > 0) == (hhi > 0):
        return None
    for _ in range(60):
        mid = (lo + hi) / 2
        om, hm = hval(mid)
        if hm is None:
            return None
        if (hm > 0) == (hlo > 0):
            lo, hlo = mid, hm
        else:
            hi, hhi = mid, hm
    root = (lo + hi) / 2
    print(f"  [{label}] S={tuple(i+1 for i in S)}, approaching h_S=0 along free[{ax}]~{float(root):.6f}")
    print(f"    {'delta':>12} {'h_S':>14} {'|A6|':>16} {'|A6*h_S|':>16}")
    for d in [F(1,10), F(1,100), F(1,1000), F(1,10000), F(1,100000)]:
        f = list(base_free); f[ax] = root + d
        om = solve_onshell(f)
        if om is None:
            continue
        h = hS(om, S)
        A = bg_amp(om)
        if A is None:
            print(f"    {float(d):12.2e}  bg failed (on a wall)")
            continue
        print(f"    {float(d):12.2e} {float(h):14.3e} {float(abs(A)):16.6e} {float(abs(A*h)):16.6e}")


if __name__ == "__main__":
    # Generic base points; S = a mixed triple {1,2,4} (2 minus,1 plus) and pure {1,2,3} (3,0)
    for S, base, ax, lab in [
        ([0, 1, 3], [F(3), F(5), F(4), F(-6)], 0, "(2,1) mixed triple"),
        ([0, 1, 2], [F(3), F(5), F(4), F(-6)], 1, "(3,0) minus triple"),
        ([0, 3, 4], [F(2), F(7), F(3), F(-5)], 0, "(1,2) -> pair-ish"),
    ]:
        approach(S, base, ax, lab)
        print()
