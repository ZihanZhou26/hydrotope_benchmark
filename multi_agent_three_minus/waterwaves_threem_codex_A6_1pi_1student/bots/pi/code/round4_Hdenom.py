#!/usr/bin/env python3
"""PI round-4: independent discovery of the denominator of H = A_6/(i prod omega).

Method (guess-free, exact):
  - sample exact on-shell three-minus points, SCALE to all-integer frequencies
    (on-shell is scale invariant), so A_6/i, prod omega, and every candidate
    factor are integers;
  - H = A_im / prod(omega) as a reduced Fraction; factor its denominator;
  - compare the prime factorization of denom(H) with the values of physically
    motivated candidate factors (p=e2, mixed-triple inverse propagators h_{lj}
    on the S_{lj} branch, a_i+b_j, D_ij, S_ij, r-t) to read off which combine
    to give denom(H).
Everything uses the PI's own fresh bg (bg_r4), exact GMP rational.
"""
import subprocess, re, random
from fractions import Fraction as F
from math import gcd
from sympy import factorint

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


def solve_onshell(free):
    fr = [F(x) for x in free]; s = sum(fr)
    if s == 0:
        return None
    ss = sum(SIG[i + 1] * fr[i] ** 2 for i in range(4))
    wn = -(SIG[0] * s * s + ss) / (2 * SIG[0] * s)
    return [-(s + wn), fr[0], fr[1], fr[2], fr[3], wn]


def to_int_point(om):
    """scale rational on-shell om to primitive integer vector."""
    from functools import reduce
    dens = [w.denominator for w in om]
    L = reduce(lambda a, b: a * b // gcd(a, b), dens, 1)
    ints = [int(w * L) for w in om]
    g = reduce(gcd, [abs(x) for x in ints if x != 0], 0)
    if g:
        ints = [x // g for x in ints]
    return ints  # integers, still on-shell


def wall_sig(om):
    a = [om[i] ** 2 for i in range(3)]; b = [om[3 + j] ** 2 for j in range(3)]
    T = a[0] + a[1] + a[2]
    s = []
    for i in range(3):
        for j in range(3):
            v = a[i] - b[j]; s.append(1 if v > 0 else -1 if v < 0 else 0)
    for i in range(3):
        for j in range(3):
            v = a[i] + b[j] - T; s.append(1 if v > 0 else -1 if v < 0 else 0)
    return tuple(s)


def sort_legs(om):
    m = sorted(om[:3], key=lambda w: (w * w, w))
    pl = sorted(om[3:], key=lambda w: (w * w, w))
    return m + pl


def candidates(om):
    """dict name->integer value of candidate degree<=2 factors at integer om."""
    w = om
    a = [w[i] ** 2 for i in range(3)]
    b = [w[3 + j] ** 2 for j in range(3)]
    T = sum(a)
    # p = e2 of minus = e2 of plus (should coincide on shell)
    p_minus = w[0] * w[1] + w[0] * w[2] + w[1] * w[2]
    p_plus = w[3] * w[4] + w[3] * w[5] + w[4] * w[5]
    c = {"p_minus": p_minus, "p_plus": p_plus}
    # a_i + b_j (sign-definite positive), D_ij=a_i-b_j, S_ij=a_i+b_j-T
    for i in range(3):
        for j in range(3):
            c[f"apb_{i}{j}"] = a[i] + b[j]
            c[f"D_{i}{j}"] = a[i] - b[j]
            c[f"S_{i}{j}"] = a[i] + b[j] - T
    # mixed-triple inverse propagator h_{lj}: triple = two minus (!=l) + plus j.
    #   S_lj = a_l + b_j - T ; if <0 : h=2(x+z)(y+z) with x,y minus freqs, z plus freq
    #   if >0 : irreducible quadratic 2(x^2+y^2+xy+z(x+y))
    for l in range(3):
        mm = [k for k in range(3) if k != l]
        x, y = w[mm[0]], w[mm[1]]
        for j in range(3):
            z = w[3 + j]
            Slj = a[l] + b[j] - T
            if Slj < 0:
                h = 2 * (x + z) * (y + z)
            else:
                h = 2 * (x * x + y * y + x * y + z * (x + y))
            c[f"h_{l}{j}"] = h
    # r - t
    u = [-w[0], -w[1], -w[2]]; v = [w[3], w[4], w[5]]
    r = u[0] * u[1] * u[2]; t = v[0] * v[1] * v[2]
    c["r_minus_t"] = r - t
    return c


def main():
    rng = random.Random(4040)
    pts = []
    target_sig = None
    while len(pts) < 8:
        free = [rng.randint(-9, 9) for _ in range(4)]
        if any(x == 0 for x in free):
            continue
        om = solve_onshell(free)
        if om is None or any(x == 0 for x in om):
            continue
        om = sort_legs(om)
        sg = wall_sig(om)
        if 0 in sg:
            continue
        if target_sig is None:
            target_sig = sg
        if sg != target_sig:
            continue
        iom = to_int_point(om)
        A = bg_amp([F(x) for x in iom])
        if A is None:
            continue
        prod = 1
        for x in iom:
            prod *= x
        H = F(A, 1) / F(prod, 1)
        pts.append((iom, A, prod, H))

    print("=" * 72)
    print("Fixed chamber wall signature:", target_sig)
    print("=" * 72)
    denom_primes = {}
    for (iom, A, prod, H) in pts:
        dfac = factorint(H.denominator)
        for pr, e in dfac.items():
            denom_primes[pr] = max(denom_primes.get(pr, 0), e)
        print(f"om={iom}")
        print(f"   A_im={A}  prod_omega={prod}")
        print(f"   H = {H.numerator} / {H.denominator}")
        print(f"   denom(H) factor = {dict(sorted(dfac.items()))}")
    print("-" * 72)

    # For each point, try to explain denom(H) via candidate factors:
    print("Explaining denom(H) by candidate factors (per point):")
    for (iom, A, prod, H) in pts:
        D = H.denominator
        cand = candidates(iom)
        expl = {}
        remaining = D
        # greedily divide by candidate |values| that divide remaining
        for name, val in sorted(cand.items(), key=lambda kv: -abs(kv[1]) if kv[1] else 0):
            v = abs(val)
            if v > 1:
                while remaining % v == 0:
                    remaining //= v
                    expl[name] = expl.get(name, 0) + 1
        print(f"om={iom}")
        print(f"   denom(H)={D}  -> factors used {expl}  remainder={remaining}")


if __name__ == "__main__":
    main()
