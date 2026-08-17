#!/usr/bin/env python3
"""PI round-4: identify H's denominator by the divisibility criterion.

If H = P/Q with Q a polynomial denominator (P,Q polynomials in the leg
frequencies, up to a global rational constant), then at every integer on-shell
point the reduced denominator of H must divide Q(point).  So: for each candidate
factor C(omega), test whether denom(H) | C at EVERY sampled point in a fixed
chamber.  The minimal product of candidates that always covers denom(H) is Q.
"""
import subprocess, re, random
from fractions import Fraction as F
from math import gcd
from functools import reduce

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
    dens = [w.denominator for w in om]
    L = reduce(lambda a, b: a * b // gcd(a, b), dens, 1)
    ints = [int(w * L) for w in om]
    g = reduce(gcd, [abs(x) for x in ints if x != 0], 0)
    return [x // g for x in ints] if g else ints


def wall_sig(om):
    a = [om[i] ** 2 for i in range(3)]; b = [om[3 + j] ** 2 for j in range(3)]
    T = sum(a); s = []
    for i in range(3):
        for j in range(3):
            v = a[i] - b[j]; s.append(1 if v > 0 else -1 if v < 0 else 0)
    for i in range(3):
        for j in range(3):
            v = a[i] + b[j] - T; s.append(1 if v > 0 else -1 if v < 0 else 0)
    return tuple(s)


def sort_legs(om):
    return sorted(om[:3], key=lambda w: (w * w, w)) + sorted(om[3:], key=lambda w: (w * w, w))


def candidates(om):
    w = om
    a = [w[i] ** 2 for i in range(3)]; b = [w[3 + j] ** 2 for j in range(3)]
    T = sum(a)
    c = {}
    c["p"] = w[0] * w[1] + w[0] * w[2] + w[1] * w[2]        # = e2(minus)=e2(plus)
    for i in range(3):
        for j in range(3):
            c[f"apb_{i}{j}"] = a[i] + b[j]
            c[f"D_{i}{j}"] = a[i] - b[j]
            c[f"S_{i}{j}"] = a[i] + b[j] - T
    for l in range(3):
        mm = [k for k in range(3) if k != l]
        x, y = w[mm[0]], w[mm[1]]
        for j in range(3):
            z = w[3 + j]; Slj = a[l] + b[j] - T
            c[f"h_{l}{j}"] = 2 * (x + z) * (y + z) if Slj < 0 else 2 * (x * x + y * y + x * y + z * (x + y))
    u = [-w[0], -w[1], -w[2]]; v = [w[3], w[4], w[5]]
    c["r_minus_t"] = u[0] * u[1] * u[2] - v[0] * v[1] * v[2]
    # symmetric aggregates
    c["prod_apb"] = reduce(lambda A, B: A * B, [a[i] + b[j] for i in range(3) for j in range(3)], 1)
    return c


def main():
    rng = random.Random(4040)
    pts = []; target_sig = None
    while len(pts) < 12:
        free = [rng.randint(-9, 9) for _ in range(4)]
        if any(x == 0 for x in free):
            continue
        om = solve_onshell(free)
        if om is None or any(x == 0 for x in om):
            continue
        om = sort_legs(om); sg = wall_sig(om)
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
        prod = reduce(lambda p, x: p * x, iom, 1)
        H = F(A, 1) / F(prod, 1)
        pts.append((iom, H))
    print("chamber signature:", target_sig, " points:", len(pts))

    names = list(candidates(pts[0][0]).keys())
    # For each candidate, does denom(H) | C at every point (up to the prime; test full divisibility of denom by combos)?
    # Simple: track, per point, gcd(denom(H), C).  A factor "covers" denom at a point if denom | C.
    print("\nCandidate factors that FULLY divide denom(H) at every point:")
    always = []
    for nm in names:
        ok = True
        for (iom, H) in pts:
            D = H.denominator; C = candidates(iom)[nm]
            if C == 0 or D % abs(C) != 0:
                ok = False; break
        if ok:
            always.append(nm)
    print("  ", always if always else "(none single-handedly)")

    # residual after dividing denom by each candidate's gcd, iterate greedily over the
    # PHYSICAL symmetric set to see what covers denom(H):
    print("\nPer-point: denom(H) and its gcd with p, prod_apb, and full triple product:")
    for (iom, H) in pts:
        D = H.denominator; c = candidates(iom)
        trip = c["p"]
        for l in range(3):
            for j in range(3):
                trip *= c[f"h_{l}{j}"]
        g_p = gcd(D, abs(c["p"]))
        g_pa = gcd(D, abs(c["prod_apb"]))
        g_tr = gcd(D, abs(trip))
        # does denom divide product p * prod_apb * (triple product)?
        big = abs(c["p"]) * abs(c["prod_apb"]) * abs(trip)
        covers = (big % D == 0)
        print(f"  om={iom} denom={D}  gcd(p)={g_p} gcd(prodApB)={g_pa} gcd(tripleprod)={g_tr}  denom|big={covers}")


if __name__ == "__main__":
    main()
