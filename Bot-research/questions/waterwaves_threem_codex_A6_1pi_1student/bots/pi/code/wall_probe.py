#!/usr/bin/env python3
"""Does A_6 DIVERGE at a momentum wall q_S = g k_S = 0 (chamber boundary), or
stay finite?  q_S enters the BG kernels through 1/|k_S|.  If A_6 ~ 1/q_S the
wall form q_S sits in the denominator Delta (A_6 genuinely rational); if A_6
stays finite it is a piecewise chamber jump.  Two-sided approaches to a diff
wall (a_i=b_j) and a sum wall (a_i+b_j=T)."""
import subprocess, re
from fractions import Fraction as F

BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code/bg"
SIG = [-1, -1, -1, 1, 1, 1]


def bg_amp(om, g=F(1)):
    K = [SIG[i] * om[i] * om[i] / g for i in range(6)]
    p = subprocess.run([BG, "--amp", "-K", ",".join(str(x) for x in K),
                        "-W", ",".join(str(x) for x in om), "-g", str(g)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if p.returncode != 0:
        return None
    m = re.search(r"A_6 = i \* \(([^)]*)\)", p.stdout)
    if m:
        return F(m.group(1))
    m2 = re.search(r"A_6 = \(([^)]*)\) \+ i \* \(([^)]*)\)", p.stdout)
    return F(m2.group(2)) if m2 else None


def solve(free):
    fr = [F(x) for x in free]; s = sum(fr)
    if s == 0:
        return None
    ss = sum(SIG[i + 1] * fr[i] ** 2 for i in range(4))
    wn = -(SIG[0] * s * s + ss) / (2 * SIG[0] * s)
    return [-(s + wn), fr[0], fr[1], fr[2], fr[3], wn]


def qS(om, S):
    return sum(SIG[i] * om[i] ** 2 for i in S)   # = g k_S


def approach(S, base, ax, lab):
    def qv(x):
        f = list(base); f[ax] = x
        om = solve(f)
        return (om, qS(om, S)) if om else (None, None)
    lo, hi = F(base[ax]), F(base[ax]) + F(6)
    om, qlo = qv(lo); _, qhi = qv(hi)
    st = 0
    while qlo is not None and qhi is not None and (qlo > 0) == (qhi > 0) and st < 60:
        hi += F(1, 2); _, qhi = qv(hi); st += 1
    if qlo is None or qhi is None or (qlo > 0) == (qhi > 0):
        print(f"  [{lab}] no sign change found"); return
    for _ in range(60):
        mid = (lo + hi) / 2; om, qm = qv(mid)
        if qm is None:
            return
        if (qm > 0) == (qlo > 0):
            lo, qlo = mid, qm
        else:
            hi, qhi = mid, qm
    root = (lo + hi) / 2
    print(f"  [{lab}] S={tuple(i+1 for i in S)}, wall q_S=0 at free[{ax}]~{float(root):.6f}")
    print(f"    {'delta':>11} {'q_S':>13} {'|A6|':>15} {'|A6*q_S|':>15}")
    for d in [F(1,10), F(1,100), F(1,1000), F(1,10000), F(1,100000)]:
        for sgn in (+1, -1):
            f = list(base); f[ax] = root + sgn * d
            om = solve(f)
            if om is None:
                continue
            q = qS(om, S); A = bg_amp(om)
            if A is None:
                print(f"    {float(sgn*d):11.2e}  bg failed"); continue
            print(f"    {float(sgn*d):11.2e} {float(q):13.3e} {float(abs(A)):15.6e} {float(abs(A*q)):15.6e}")


if __name__ == "__main__":
    # free = (omega2, omega3, omega4, omega5) at indices ax=0,1,2,3
    # diff wall via S={2,4} (legs 2,4 both FREE): q = -a2 + b1 = -omega2^2 + omega4^2;
    # fix omega2=3, vary omega4 -> wall at omega4=3 (a2=b1).
    approach([1, 3], [F(3), F(5), F(1), F(-6)], 2, "diff wall a2=b1 (S={2,4})")
    print()
    # sum-type wall via S={2,3,4}: q = -a2 - a3 + b1 ; wall b1 = a2+a3 -> a1+b1 = T.
    # fix omega2=3, omega3=5, vary omega4 -> wall at omega4^2 = 34.
    approach([1, 2, 3], [F(3), F(5), F(4), F(-6)], 2, "sum wall a1+b1=T (S={2,3,4})")
