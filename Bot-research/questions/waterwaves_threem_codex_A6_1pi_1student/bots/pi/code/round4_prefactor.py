#!/usr/bin/env python3
"""PI round-4: re-verify the parts of pi_v_012 that survive the evenness failure:
 (1) A_6 vanishes LINEARLY as any single leg frequency -> 0 (so prod omega | A_6);
 (2) H = A_6/(i prod omega) is EXACTLY degree-2 homogeneous.
Exact GMP via fresh bg_r4.  We also confirm H is NOT even by a fresh partner pair.
"""
import subprocess, re
from fractions import Fraction as F

BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code/bg_r4"
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
    if m2 and F(m2.group(1)) == 0:
        return F(m2.group(2))
    return None


def solve_w1_w6(w2, w3, w4, w5):
    free = [w2, w3, w4, w5]; s = sum(free)
    ss = sum(SIG[i + 1] * free[i] ** 2 for i in range(4))
    w6 = -(SIG[0] * s * s + ss) / (2 * SIG[0] * s)
    return [-(s + w6), w2, w3, w4, w5, w6]


def H_of(om):
    A = bg_amp(om)
    prod = F(1)
    for w in om:
        prod *= w
    return None if A is None else A / prod


# (1) single-leg vanishing: build an on-shell family where a chosen leg -> 0.
# Vary a minus leg (index 2, i.e. w3) toward 0 by scaling; recompute on-shell.
print("=" * 72)
print("(1) A_6 -> 0 linearly as a single leg -> 0  (prod omega | A_6)")
for label, mk in [
    ("minus leg w3", lambda e: solve_w1_w6(F(7), e, F(5), F(-9))),
    ("plus  leg w5", lambda e: solve_w1_w6(F(7), F(-11), F(5), e)),
]:
    print(f"  {label} -> 0:")
    for e in [F(1, 4), F(1, 16), F(1, 64), F(1, 256)]:
        om = mk(e)
        if any(w == 0 for w in om):
            continue
        A = bg_amp(om)
        # ratio A / (the vanishing leg):  if finite and nonzero -> linear zero
        leg = e
        print(f"     eps={str(e):>7}  A_im={float(A):+.6e}  A_im/eps={float(A/leg):+.6e}")

# (2) degree-2 homogeneity of H, exact
print("=" * 72)
print("(2) H is exactly degree-2 homogeneous  H(lam*om) = lam^2 H(om)")
om0 = solve_w1_w6(F(7), F(-11), F(5), F(-9))
H0 = H_of(om0)
for lam in [F(2), F(3, 2), F(5)]:
    omL = [lam * w for w in om0]
    HL = H_of(omL)
    print(f"   lam={str(lam):>4}: H(lam om)/H(om) = {HL / H0}   expect {lam**2}   "
          f"{'OK' if HL == lam*lam*H0 else 'FAIL'}")

# (3) fresh partner (generic, distinct squares) -> H not even
print("=" * 72)
print("(3) fresh partner pair (same squares, flipped signs of legs 2,3,4): H even?")
w2, w3 = F(6), F(5); w4 = -(w2 + w3); w5 = F(3)
om = solve_w1_w6(w2, w3, w4, w5)
omp = om[:]; omp[1], omp[2], omp[3] = -omp[1], -omp[2], -omp[3]
print(f"   om ={[str(w) for w in om]}  squares minus={sorted(w*w for w in om[:3])} plus={sorted(w*w for w in om[3:])}")
print(f"   om'={[str(w) for w in omp]}  squares minus={sorted(w*w for w in omp[:3])} plus={sorted(w*w for w in omp[3:])}")
print(f"   H ={H_of(om)}")
print(f"   H'={H_of(omp)}")
print(f"   EVEN? {H_of(om) == H_of(omp)}")
