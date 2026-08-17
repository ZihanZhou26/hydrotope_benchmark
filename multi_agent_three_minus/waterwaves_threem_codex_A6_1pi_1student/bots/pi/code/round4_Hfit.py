#!/usr/bin/env python3
"""PI round-4: guess-free modular rational fit of H = A_6/(i prod omega).

Clean coordinates: the 4 FREE frequencies f=(w2,w3,w4,w5).  bg solves w1,w6 as
RATIONAL functions of f (sigma_1+sigma_6=0 makes the two conservation eqs
linear+factorable), so H is a genuine rational function of the 4 unconstrained
variables f -- no manifold ideal to fight.  Inside ONE fixed 18-wall chamber we
search for the minimal total-degree denominator:

  for d = 1,2,...: null vector of [ M_{<=d}(f) | -H * M_{<=d}(f) ] over Z/P.
  A null vector with nonzero Q-block => H = P/Q with deg P,Q <= d there.

All amplitudes from the PI's fresh bg_r4 (exact GMP), reduced mod P=2^61-1.
Also does a fresh-point recheck of student s1_014 (H*prod = A_im exactly).
"""
import subprocess, re, random, sys
from fractions import Fraction as F
from itertools import product as iproduct

BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code/bg_r4"
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


def generic(om):
    sq = sorted(w * w for w in om)
    return all(sq[i] != sq[i + 1] for i in range(5))


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


def rref_rank(rows, ncol):
    R = [r[:] for r in rows]; m = len(R); rank = 0; pivcols = []
    for col in range(ncol):
        piv = next((r for r in range(rank, m) if R[r][col] % P), None)
        if piv is None:
            continue
        R[rank], R[piv] = R[piv], R[rank]
        inv = pow(R[rank][col], P - 2, P)
        R[rank] = [(x * inv) % P for x in R[rank]]
        for r in range(m):
            if r != rank and R[r][col] % P:
                fac = R[r][col]
                R[r] = [(R[r][c] - fac * R[rank][c]) % P for c in range(ncol)]
        pivcols.append(col); rank += 1
        if rank == m:
            break
    return R, rank, pivcols


def collect(chamber_seed=7, need=700):
    rng = random.Random(chamber_seed)
    target = None; pts = []; s14_ok = 0; s14_tot = 0
    tries = 0
    while len(pts) < need and tries < 400000:
        tries += 1
        free = [F(rng.randint(-20, 20), rng.randint(1, 4)) for _ in range(4)]
        if any(x == 0 for x in free):
            continue
        om = solve_onshell(free)
        if om is None or any(x == 0 for x in om):
            continue
        oms = sort_legs(om)
        if not generic(oms):
            continue
        sg = wall_sig(oms)
        if 0 in sg:
            continue
        if target is None:
            target = sg
        if sg != target:
            continue
        A = bg_amp(oms)
        if A is None:
            continue
        prod = F(1)
        for w in oms:
            prod *= w
        H = A / prod
        # s1_014 recheck: H*prod == A (exact)
        s14_tot += 1
        if H * prod == A:
            s14_ok += 1
        # store f=(w2..w5) of the SORTED point and H mod P
        f = [to_mod(oms[i]) for i in range(1, 5)]
        pts.append((f, to_mod(H), oms))
    return target, pts, s14_ok, s14_tot


def rational_fit(pts, d):
    mon = monos_upto(d, 4)
    nm = len(mon)
    rows = []
    for (f, h, _oms) in pts:
        mv = [ (pow(f[0], e[0], P) * pow(f[1], e[1], P) % P) *
               (pow(f[2], e[2], P) * pow(f[3], e[3], P) % P) % P for e in mon]
        row = mv + [(-h * v) % P for v in mv]
        rows.append(row)
    ncol = 2 * nm
    _, rank, _ = rref_rank(rows, ncol)
    nulldim = ncol - rank
    return nm, ncol, len(rows), rank, nulldim


def main():
    target, pts, s14_ok, s14_tot = collect()
    print(f"chamber sig: {target}")
    print(f"collected {len(pts)} generic exact points in this chamber")
    print(f"s1_014 recheck (H*prod_omega == A_im, exact): {s14_ok}/{s14_tot} PASS")
    print("-" * 72)
    for d in range(1, 8):
        nm, ncol, npts, rank, nulldim = rational_fit(pts, d)
        need = ncol + 5
        tag = "RATIONAL REP EXISTS" if nulldim > 0 else "no rep"
        warn = "" if npts >= need else f"  (WARNING pts {npts} < cols+5 {need})"
        print(f"d={d}: |M<=d|={nm} cols={ncol} pts={npts} rank={rank} nulldim={nulldim} => {tag}{warn}")
        sys.stdout.flush()
        if nulldim > 0 and npts >= need:
            print(f"  --> minimal denominator total-degree in free coords f = {d}")
            break


if __name__ == "__main__":
    main()
