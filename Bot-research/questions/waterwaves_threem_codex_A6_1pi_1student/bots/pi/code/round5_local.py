#!/usr/bin/env python3
"""PI round-5: LOCAL in-piece rational degree of H = A_6/(i prod omega).

Key question: pi_v_015 fit H over a whole 18-wall chamber and found NO rational
rep to total degree 7 (=> apparent denom degree >=8).  But A_6 has derivative
KINKS at walls (pi_v_006) -- the hallmark of PIECEWISE structure -- so an 18-wall
chamber may still contain several distinct rational PIECES (bounded also by
factorization surfaces / positive-part thresholds).  A whole-chamber fit that
mixes pieces would spuriously report a high denominator degree.

A tiny ball around a generic interior point lies inside ONE piece (pi_v_009).
For an EXACT rational H=N/D of in-piece degree d_true, the modular null-space of
[ M_{<=d}(f) | -H M_{<=d}(f) ] has a rep iff d >= d_true (no local Pade escape:
H=P/Q with deg<=d<d_true would force D|Q, impossible).  So the minimal d with a
null vector is the TRUE in-piece rational degree, and the Q-block is the local
denominator polynomial (which we can then factor / identify).

Everything exact: fresh bg_r5 (GMP), reduced mod P=2^61-1.
"""
import subprocess, re, random, sys
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
                fac = R[r][col]
                R[r] = [(R[r][c] - fac * R[rank][c]) % P for c in range(ncol)]
        rank += 1
        if rank == m:
            break
    return R, rank


def collect_ball(base_free, radius_den, need):
    """points in a small ball around base_free (all same piece if radius tiny)."""
    rng = random.Random(9090)
    om0 = solve_onshell(base_free)
    sig0 = wall_sig(om0)
    pts = []
    tries = 0
    while len(pts) < need and tries < 200000:
        tries += 1
        f = [base_free[i] + F(rng.randint(-9, 9), radius_den) for i in range(4)]
        if any(x == 0 for x in f) or sum(f) == 0:
            continue
        om = solve_onshell(f)
        if om is None or any(x == 0 for x in om) or not generic(om):
            continue
        if wall_sig(om) != sig0:            # do not leave the 18-wall chamber
            continue
        A = bg_amp(om)
        if A is None:
            continue
        prod = F(1)
        for wv in om:
            prod *= wv
        H = A / prod
        fmod = [to_mod(x) for x in f]
        pts.append((fmod, to_mod(H)))
    return sig0, pts


def fit(pts, d):
    mon = monos_upto(d, 4)
    nm = len(mon)
    rows = []
    for (f, h) in pts:
        mv = [(pow(f[0], e[0], P) * pow(f[1], e[1], P) % P) *
              (pow(f[2], e[2], P) * pow(f[3], e[3], P) % P) % P for e in mon]
        rows.append(mv + [(-h * v) % P for v in mv])
    ncol = 2 * nm
    _, rank = rref_rank(rows, ncol)
    return nm, ncol, len(rows), rank, ncol - rank


def main():
    # a generic interior base point (integers -> tiny rational ball around it)
    base = [F(3), F(-5), F(7), F(-2)]
    om0 = solve_onshell(base)
    print("base free:", base, " -> om0:", [str(x) for x in om0])
    print("om0 generic:", generic(om0), " 18-wall sig:", wall_sig(om0))
    # radius 9/10000 keeps the ball microscopic (no wall crossed)
    sig0, pts = collect_ball(base, 10000, need=340)
    print(f"collected {len(pts)} exact points in a 9e-4 ball (one piece), sig={sig0}")
    print("-" * 72)
    for d in range(1, 7):
        nm, ncol, npts, rank, nulldim = fit(pts, d)
        need = ncol + 6
        tag = "RATIONAL REP EXISTS" if (nulldim > 0 and npts >= need) else \
              ("no rep" if npts >= need else f"NEED MORE PTS (have {npts}, need {need})")
        print(f"d={d}: |M<=d|={nm} cols={ncol} pts={npts} rank={rank} nulldim={nulldim} => {tag}")
        sys.stdout.flush()
        if nulldim > 0 and npts >= need:
            print(f"  --> minimal LOCAL in-piece rational degree = {d}")
            break


if __name__ == "__main__":
    main()
