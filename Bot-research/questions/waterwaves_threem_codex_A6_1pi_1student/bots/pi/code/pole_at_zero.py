#!/usr/bin/env python3
"""Does a single minus-leg frequency omega_2 -> 0 make A_6 blow up (~ 1/omega_2^m)?

The only BG denominators that are sign-definite on the WHOLE physical on-shell
domain (never a real pole, yet non-cancelling) are the single-leg momentum norms
|k_i| = omega_i^2 from the F-kernel 1/|p| divisions.  If they survive in reduced
A_6, then A_6 ~ C / omega_2^{2m} as omega_2 -> 0.

We use the exact on-shell solver with free frequencies (omega_2, omega_3, omega_4,
omega_5); omega_1 and omega_6 are solved.  Set omega_2 = eps and fix
omega_3,4,5, so eps -> 0 is an exact rational 1-parameter family with a single
minus-leg frequency going to zero.  Read the order from A_6 * eps^k.
"""
import subprocess, re
from fractions import Fraction as F

BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code/bg"
SIG = [-1, -1, -1, 1, 1, 1]


def bg_amp(om):
    K = [SIG[i] * om[i] * om[i] for i in range(6)]
    p = subprocess.run([BG, "--amp", "-K", ",".join(str(x) for x in K),
                        "-W", ",".join(str(x) for x in om), "-g", "1"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if p.returncode != 0:
        return None
    m = re.search(r"A_6 = i \* \(([^)]*)\)", p.stdout)
    if m:
        return F(m.group(1))
    m2 = re.search(r"A_6 = \(([^)]*)\) \+ i \* \(([^)]*)\)", p.stdout)
    return F(m2.group(2)) if m2 else None


def solve_onshell(free):
    fr = [F(x) for x in free]; s = sum(fr)
    if s == 0:
        return None
    ss = sum(SIG[i + 1] * fr[i] ** 2 for i in range(4))
    wn = -(SIG[0] * s * s + ss) / (2 * SIG[0] * s)
    return [-(s + wn), fr[0], fr[1], fr[2], fr[3], wn]


def offwall(om):
    a = [om[i] ** 2 for i in range(3)]; b = [om[3 + j] ** 2 for j in range(3)]
    T = sum(a)
    if any(a[i] == b[j] for i in range(3) for j in range(3)):
        return False
    if any(a[i] + b[j] == T for i in range(3) for j in range(3)):
        return False
    return True


def main():
    w3, w4, w5 = F(9), F(4), F(-13)     # fixed; omega_2 = eps -> 0
    print(f"family: free=(omega_2=eps, {w3}, {w4}, {w5}); omega_1,omega_6 solved; eps->0")
    print(f"{'eps':>12} {'A_6':>24} {'A_6*eps':>18} {'A_6*eps^2':>18} {'omega_2^2*A_6':>18}")
    prev = None
    for epsden in [4, 10, 40, 100, 400, 1000, 4000, 10000]:
        eps = F(1, epsden)
        om = solve_onshell([eps, w3, w4, w5])
        if om is None or any(x == 0 for x in om) or not offwall(om):
            print(f"{float(eps):>12.6g}   (degenerate/wall — skipped)")
            continue
        A6 = bg_amp(om)
        if A6 is None:
            print(f"{float(eps):>12.6g}   (bg failed)")
            continue
        print(f"{float(eps):>12.6g} {float(A6):>24.6g} {float(A6*eps):>18.6g} "
              f"{float(A6*eps*eps):>18.6g} {float(eps*eps*A6):>18.6g}")
        prev = A6
    print()
    print("Reading: A_6 -> finite  => omega_2^2 NOT in the denominator;")
    print("         A_6 ~ 1/eps^2 (A_6*eps^2 -> const) => denominator carries omega_2^2.")


if __name__ == "__main__":
    main()
