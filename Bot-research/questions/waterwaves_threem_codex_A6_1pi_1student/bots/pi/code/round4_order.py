#!/usr/bin/env python3
"""PI round-4: pin the vanishing ORDER of A_6 as a single leg frequency -> 0,
and the behavior of H = A_6/(i prod omega) there.  Exact GMP via bg_r4.
Family: send chosen free leg -> 0, keep the other three free legs fixed,
solve w1,w6.  Report A_6, A_6/eps, A_6/eps^2, prod, H, H/eps (exact ratios of
consecutive eps to read the integer order)."""
import subprocess, re
from fractions import Fraction as F

BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code/bg_r4"
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
    return F(m2.group(2)) if (m2 and F(m2.group(1)) == 0) else None


def solve(free):
    s = sum(free); ss = sum(SIG[i + 1] * free[i] ** 2 for i in range(4))
    wn = -(SIG[0] * s * s + ss) / (2 * SIG[0] * s)
    return [-(s + wn)] + list(free) + [wn]


def run(name, mk):
    print(f"\n=== {name} ===")
    print(f"{'eps':>10} {'A_6':>16} {'A/eps':>16} {'A/eps^2':>16} {'H=A/prod':>16} {'H/eps':>14}")
    rows = []
    for d in [10, 100, 1000, 10000]:
        eps = F(1, d)
        om = mk(eps)
        if any(w == 0 for w in om):
            print(f"{float(eps):>10.4g}  zero-leg skip"); continue
        A = bg_amp(om)
        if A is None:
            print(f"{float(eps):>10.4g}  bg-fail (wall?)"); continue
        prod = F(1)
        for w in om:
            prod *= w
        H = A / prod
        rows.append((eps, A, H))
        print(f"{float(eps):>10.4g} {float(A):>16.5g} {float(A/eps):>16.5g} "
              f"{float(A/eps/eps):>16.5g} {float(H):>16.6g} {float(H/eps):>14.5g}")
    if len(rows) >= 2:
        e0, A0, H0 = rows[0]; e1, A1, H1 = rows[1]
        rA = float((A1 / A0)) / float((e1 / e0))     # A ~ eps^p  => A1/A0 = (e1/e0)^p
        import math
        pA = math.log(abs(float(A1 / A0))) / math.log(float(e1 / e0))
        pH = math.log(abs(float(H1 / H0))) / math.log(float(e1 / e0)) if H0 != 0 else float('nan')
        print(f"   -> order(A_6) ~ eps^{pA:.3f} ;  order(H) ~ eps^{pH:.3f}")


run("minus leg omega_2 -> 0 (others w3=9,w4=4,w5=-13)",
    lambda e: solve([e, F(9), F(4), F(-13)]))
run("minus leg omega_3 -> 0 (others w2=7,w4=5,w5=-9)",
    lambda e: solve([F(7), e, F(5), F(-9)]))
run("plus  leg omega_4 -> 0 (others w2=7,w3=-11,w5=-9)",
    lambda e: solve([F(7), F(-11), e, F(-9)]))
run("plus  leg omega_5 -> 0 (others w2=7,w3=-11,w4=5)",
    lambda e: solve([F(7), F(-11), F(5), e]))
