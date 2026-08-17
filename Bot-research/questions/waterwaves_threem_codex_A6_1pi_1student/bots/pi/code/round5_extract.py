#!/usr/bin/env python3
"""PI round-5: push the single-TRUE-piece rational fit of H to degree 7 and, if a
rep exists, EXTRACT the denominator's null vector (Q-block) and report its
monomial support for factor identification.  A rep at d=7 in ONE piece (where the
whole-18-wall-chamber fit failed at d=7, pi_v_015) also proves the true pieces
are finer than 18-wall chambers.

Exact: fresh bg_r5 (GMP), mod P=2^61-1.  Reuses round5_truefit collection.
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


def full_sign(om):
    a = [om[i] ** 2 for i in range(3)]; b = [om[3 + j] ** 2 for j in range(3)]
    T = sum(a); sg = []
    for i in range(3):
        for j in range(3):
            v = a[i] - b[j]; sg.append(1 if v > 0 else -1 if v < 0 else 0)
    for i in range(3):
        for j in range(3):
            v = a[i] + b[j] - T; sg.append(1 if v > 0 else -1 if v < 0 else 0)
    for r in (2, 3):
        for S in combinations(range(6), r):
            wS = sum(om[i] for i in S)
            kS = sum(SIG[i] * om[i] ** 2 for i in S)
            h = wS * wS - (kS if kS >= 0 else -kS)
            sg.append(1 if h > 0 else -1 if h < 0 else 0)
    return tuple(sg)


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


def nullspace_dim_and_vec(rows, ncol):
    R = [r[:] for r in rows]; m = len(R); rank = 0; pivcol = []
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
        pivcol.append(col); rank += 1
        if rank == m:
            break
    nulldim = ncol - rank
    vec = None
    if nulldim > 0:
        pivset = set(pivcol)
        free_cols = [c for c in range(ncol) if c not in pivset]
        fc = free_cols[0]
        vec = [0] * ncol
        vec[fc] = 1
        for ri, pc in enumerate(pivcol):
            vec[pc] = (-R[ri][fc]) % P
    return nulldim, vec


def collect(base_f, base_sg, radius_den, need):
    rng = random.Random(313)
    pts = []; tries = 0
    while len(pts) < need and tries < 600000:
        tries += 1
        f = [base_f[i] + F(rng.randint(-7, 7), radius_den) for i in range(4)]
        if any(x == 0 for x in f) or sum(f) == 0:
            continue
        om = solve_onshell(f)
        if om is None or any(x == 0 for x in om) or not generic(om):
            continue
        if full_sign(om) != base_sg:
            continue
        A = bg_amp(om)
        if A is None:
            continue
        prod = F(1)
        for wv in om:
            prod *= wv
        pts.append(([to_mod(x) for x in f], to_mod(A / prod)))
    return pts


def fit(pts, d, extract=False):
    mon = monos_upto(d, 4); nm = len(mon); rows = []
    for (f, h) in pts:
        mv = [(pow(f[0], e[0], P) * pow(f[1], e[1], P) % P) *
              (pow(f[2], e[2], P) * pow(f[3], e[3], P) % P) % P for e in mon]
        rows.append(mv + [(-h * v) % P for v in mv])
    ncol = 2 * nm
    nulldim, vec = nullspace_dim_and_vec(rows, ncol)
    return mon, nm, ncol, len(rows), nulldim, vec


def main():
    # reuse the roomy integer base found by round5_truefit
    base_f = [F(7), F(8), F(4), F(3)]
    om0 = solve_onshell(base_f)
    base_sg = full_sign(om0)
    print("base om0:", [str(x) for x in om0])
    pts = collect(base_f, base_sg, 6000, need=740)
    print(f"collected {len(pts)} verified single-true-piece points")
    print("-" * 72)
    for d in (6, 7):
        mon, nm, ncol, npts, nulldim, vec = fit(pts, d)
        needp = ncol + 6
        ok = npts >= needp
        print(f"d={d}: |M|={nm} cols={ncol} pts={npts} need={needp} nulldim={nulldim} "
              f"=> {'RATIONAL REP' if (nulldim>0 and ok) else ('no rep' if ok else 'NEED MORE PTS')}")
        sys.stdout.flush()
        if nulldim > 0 and ok and vec is not None:
            qblock = vec[nm:]              # denominator coefficients
            supp = [(mon[i], qblock[i]) for i in range(nm) if qblock[i] % P != 0]
            print(f"  denominator Q support: {len(supp)} nonzero monomials of {nm}")
            for (e, c) in sorted(supp, key=lambda x: sum(x[0])):
                print(f"    f2^{e[0]} f3^{e[1]} f4^{e[2]} f5^{e[3]}  coeff(modP)={c}")
            break


if __name__ == "__main__":
    main()
