#!/usr/bin/env python3
"""Decisive: is A_6 LOCALLY a degree-8 polynomial?

Sample ~330 on-shell points in a tiny ball around ONE generic interior base
point.  A ball small enough lies inside a single polynomial piece for ANY
piecewise-polynomial structure (all wall forms keep their sign).  Fit a general
degree-8 polynomial (eliminate omega_1 via sum=0) and cross-validate, in Z/p.

PASS  => A_6 is locally polynomial => piecewise-polynomial (finite kink walls,
         so the global chamber fit failed only because it spanned >1 piece).
FAIL  => A_6 is genuinely rational even locally.
Control: the same run on the two-minus A_5 (a known polynomial) must PASS.
"""
import subprocess, re, random
from fractions import Fraction as F
from itertools import combinations_with_replacement

BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code/bg"
P = (1 << 61) - 1


def bg_amp6(om, g=F(1)):
    sig = [-1, -1, -1, 1, 1, 1]
    K = [sig[i] * om[i] * om[i] / g for i in range(6)]
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


def solve6(free):
    sig = [-1, -1, -1, 1, 1, 1]
    fr = [F(x) for x in free]; s = sum(fr)
    if s == 0:
        return None
    ss = sum(sig[i + 1] * fr[i] ** 2 for i in range(4))
    wn = -(sig[0] * s * s + ss) / (2 * sig[0] * s)
    return [-(s + wn), fr[0], fr[1], fr[2], fr[3], wn]


def to_mod(fr):
    return (fr.numerator % P) * pow(fr.denominator % P, P - 2, P) % P


def run(vars_used, deg, base_free, solve, bg_amp, nfree, label):
    MONS = [tuple(c.count(v) for v in range(vars_used))
            for c in combinations_with_replacement(range(vars_used), deg)]
    print(f"[{label}] degree-{deg} monomials in {vars_used} vars = {len(MONS)}")
    rng = random.Random(2026)
    pts = []
    D = 10 ** 6
    target = len(MONS) + 40
    tries = 0
    while len(pts) < target and tries < 200000:
        tries += 1
        free = [F(base_free[i]) + F(rng.randint(-40, 40), D) for i in range(nfree)]
        om = solve(free)
        if om is None or any(x == 0 for x in om):
            continue
        A = bg_amp(om)
        if A is None:
            continue
        pts.append((om, A))
    print(f"  collected {len(pts)} nearby on-shell pts (tries={tries})")

    def feats(om):
        vv = [to_mod(x) for x in om[1:1 + vars_used]]
        pw = [[1] * (deg + 1) for _ in range(vars_used)]
        for v in range(vars_used):
            for e in range(1, deg + 1):
                pw[v][e] = pw[v][e - 1] * vv[v] % P
        out = []
        for mon in MONS:
            m = 1
            for v in range(vars_used):
                if mon[v]:
                    m = m * pw[v][mon[v]] % P
            out.append(m)
        return out

    nfit = min(len(pts) - 25, len(MONS) + 20)
    fit = pts[:nfit]; hold = pts[nfit:nfit + 25]
    A = [feats(om) for (om, _) in fit]
    y = [to_mod(v) for (_, v) in fit]

    def rref(rows, ncol):
        R = [r[:] for r in rows]; m = len(R); rank = 0
        for col in range(ncol):
            piv = next((r for r in range(rank, m) if R[r][col] % P), None)
            if piv is None:
                continue
            R[rank], R[piv] = R[piv], R[rank]
            inv = pow(R[rank][col], P - 2, P)
            R[rank] = [(x * inv) % P for x in R[rank]]
            for r in range(m):
                if r != rank and R[r][col] % P:
                    f = R[r][col]
                    R[r] = [(R[r][c] - f * R[rank][c]) % P for c in range(len(R[r]))]
            rank += 1
            if rank == m:
                break
        return R, rank

    _, base = rref(A, len(MONS))
    M, aug = rref([A[i] + [y[i]] for i in range(len(A))], len(MONS) + 1)
    print(f"  fit pts={len(fit)}  rank(F)={base}  rank[F|y]={aug}")
    xok = None
    if base == aug and hold:
        coeff = [0] * len(MONS)
        for row in M:
            pc = next((c for c in range(len(MONS)) if row[c] % P), None)
            if pc is not None:
                coeff[pc] = row[len(MONS)] % P
        xok = all(sum((coeff[k] * feats(om)[k]) % P for k in range(len(MONS)) if coeff[k]) % P
                  == to_mod(v) % P for (om, v) in hold)
        print(f"  cross-validation on {len(hold)} nearby pts: {'PASS' if xok else 'FAIL'}")
    ok = (base == aug) and xok
    print(f"  => LOCAL POLYNOMIAL: {'YES' if ok else 'NO'}")
    return ok


def bg_amp5(free):
    p = subprocess.run([BG, "-n", "5", "-w", ",".join(str(x) for x in free),
                        "-s", "-1,-1,1,1,1", "-g", "1"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if p.returncode != 0:
        return None
    m = re.search(r"omega = \{([^}]*)\}", p.stdout)
    om = [F(t.strip()) for t in m.group(1).split(",")]
    mm = re.search(r"A_5 = i \* \(([^)]*)\)", p.stdout)
    return F(mm.group(1)) if mm else None


def solve5(free):
    sig = [-1, -1, 1, 1, 1]
    fr = [F(x) for x in free]; s = sum(fr)
    if s == 0:
        return None
    ss = sum(sig[i + 1] * fr[i] ** 2 for i in range(3))
    wn = -(sig[0] * s * s + ss) / (2 * sig[0] * s)
    return [-(s + wn), fr[0], fr[1], fr[2], wn]


def bg_amp5_full(free):
    a = bg_amp5(free)
    return a


if __name__ == "__main__":
    # A_5 control (known polynomial): must be LOCAL POLYNOMIAL = YES
    run(4, 6, [F(2), F(9), F(-4)], solve5, lambda om: bg_amp5_full([om[1], om[2], om[3]]), 3,
        "A5 two-minus control")
    print()
    # A_6: the test
    run(5, 8, [F(2), F(9), F(4), F(-13)], solve6, bg_amp6, 4, "A6 three-minus")
