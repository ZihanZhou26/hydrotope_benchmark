#!/usr/bin/env python3
"""PI round-5: TRUE in-piece rational degree of H = A_6/(i prod omega).

pi_v_015 fit H over a whole 18-WALL chamber (deg<=7, no rep) and concluded
"denom degree >=8".  But an 18-wall chamber can contain several TRUE pieces
(bounded also by the 35 factorization surfaces h_S=0), so that fit may MIX
pieces and spuriously inflate the degree.  Here we fit H inside ONE guaranteed
true piece: pick a base far from all 53 surfaces (all |quantities| large), take
a ball, and KEEP ONLY points whose full 53-sign vector equals the base's.

Minimal d with a modular null vector of [ M_{<=d}(f) | -H M_{<=d}(f) ] over Z/P
is the true in-piece rational degree; the Q-block is the local denominator, which
we print (top monomials) for identification.

Exact: fresh bg_r5 (GMP), mod P=2^61-1.
"""
import subprocess, re, random, sys
from itertools import combinations
from fractions import Fraction as F

BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code/bg_r5"
SIG = [-1, -1, -1, 1, 1, 1]
P = (1 << 61) - 1


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


def generic(om):
    sq = sorted(w * w for w in om)
    return all(sq[i] != sq[i + 1] for i in range(5))


def full_sign_and_margin(om):
    a = [om[i] ** 2 for i in range(3)]; b = [om[3 + j] ** 2 for j in range(3)]
    T = sum(a); sg = []; vals = []
    scale = sum(w * w for w in om)
    for i in range(3):
        for j in range(3):
            v = a[i] - b[j]; sg.append(1 if v > 0 else -1 if v < 0 else 0); vals.append(abs(v))
    for i in range(3):
        for j in range(3):
            v = a[i] + b[j] - T; sg.append(1 if v > 0 else -1 if v < 0 else 0); vals.append(abs(v))
    for r in (2, 3):
        for S in combinations(range(6), r):
            wS = sum(om[i] for i in S)
            kS = sum(SIG[i] * om[i] ** 2 for i in S)
            h = wS * wS - (kS if kS >= 0 else -kS)
            sg.append(1 if h > 0 else -1 if h < 0 else 0); vals.append(abs(h))
    margin = min(v for v in vals) / scale if scale else F(0)
    return tuple(sg), margin


def to_mod(fr):
    return (fr.numerator % P) * pow(fr.denominator % P, P - 2, P) % P


def monos_upto(d, nvar=4):
    out = []
    def rec(pos, deg, cur):
        if pos == nvar:
            out.append(tuple(cur)); return
        for e in range(deg + 1):
            rec(pos + 1, deg - e, cur + [e])
    rec(0, d, [])
    return out


def rref(rows, ncol):
    R = [r[:] for r in rows]; m = len(R); rank = 0; piv = []
    for col in range(ncol):
        pr = next((r for r in range(rank, m) if R[r][col] % P), None)
        if pr is None:
            continue
        R[rank], R[pr] = R[pr], R[rank]
        inv = pow(R[rank][col], P - 2, P)
        R[rank] = [(x * inv) % P for x in R[rank]]
        for r in range(m):
            if r != rank and R[r][col] % P:
                fac = R[r][col]
                R[r] = [(R[r][c] - fac * R[rank][c]) % P for c in range(ncol)]
        piv.append(col); rank += 1
        if rank == m:
            break
    return R, rank, piv


def find_base(rng):
    """base free-point with a LARGE margin to all 53 surfaces (roomy true piece)."""
    best = None
    for _ in range(20000):
        f = [F(rng.randint(-9, 9)) for _ in range(4)]
        if any(x == 0 for x in f) or sum(f) == 0:
            continue
        om = solve_onshell(f)
        if om is None or any(x == 0 for x in om) or not generic(om):
            continue
        sg, margin = full_sign_and_margin(om)
        if 0 in sg:
            continue
        if best is None or margin > best[2]:
            best = (f, sg, margin, om)
    return best


def collect(base_f, base_sg, radius_den, need):
    rng = random.Random(313)
    pts = []; tries = 0
    while len(pts) < need and tries < 400000:
        tries += 1
        f = [base_f[i] + F(rng.randint(-7, 7), radius_den) for i in range(4)]
        if any(x == 0 for x in f) or sum(f) == 0:
            continue
        om = solve_onshell(f)
        if om is None or any(x == 0 for x in om) or not generic(om):
            continue
        sg, _ = full_sign_and_margin(om)
        if sg != base_sg:               # stay in the SAME true piece
            continue
        A = bg_amp(om)
        if A is None:
            continue
        prod = F(1)
        for wv in om:
            prod *= wv
        pts.append(([to_mod(x) for x in f], to_mod(A / prod)))
    return pts, tries


def fit(pts, d):
    mon = monos_upto(d, 4); nm = len(mon); rows = []
    for (f, h) in pts:
        mv = [(pow(f[0], e[0], P) * pow(f[1], e[1], P) % P) *
              (pow(f[2], e[2], P) * pow(f[3], e[3], P) % P) % P for e in mon]
        rows.append(mv + [(-h * v) % P for v in mv])
    ncol = 2 * nm
    _, rank, _ = rref(rows, ncol)
    return nm, ncol, len(rows), rank, ncol - rank


def main():
    rng = random.Random(101)
    base = find_base(rng)
    base_f, base_sg, margin, om0 = base
    print("base free:", [str(x) for x in base_f], " om0:", [str(x) for x in om0])
    print("margin (min |surface| / scale):", str(margin), float(margin))
    # radius chosen << margin so a ball stays in one true piece; still verify per point
    pts, tries = collect(base_f, base_sg, 6000, need=460)
    print(f"collected {len(pts)} verified single-true-piece points (tries={tries})")
    print("-" * 72)
    hit = None
    for d in range(1, 7):
        nm, ncol, npts, rank, nulldim = fit(pts, d)
        needp = ncol + 6
        if npts < needp:
            print(f"d={d}: cols={ncol} pts={npts} rank={rank} nulldim={nulldim} "
                  f"NEED MORE PTS ({needp})"); break
        tag = "RATIONAL REP EXISTS" if nulldim > 0 else "no rep"
        print(f"d={d}: |M|={nm} cols={ncol} pts={npts} rank={rank} nulldim={nulldim} => {tag}")
        sys.stdout.flush()
        if nulldim > 0:
            hit = d; break
    if hit:
        print(f"\n==> TRUE in-piece rational degree of H = {hit}")
    else:
        print("\n==> no rep up to tested degree in a single TRUE piece "
              "(in-piece denom degree exceeds tested; matches pi_v_015 spirit).")


if __name__ == "__main__":
    main()
