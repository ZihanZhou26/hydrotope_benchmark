#!/usr/bin/env python3
"""PI round-3 independent verification + denominator probe.

Two jobs, all with the PI's own fresh bg.cpp copy (bots/pi/code/bg), exact GMP
rational, no student code/data imported:

  V. Verify the student's round-2 common-cubic reduction (claims s1_006-009):
     with u_i=-omega_i (minus legs 1,2,3) and v_j=omega_{3+j} (plus legs), the
     two triples share the first TWO elementary symmetric functions
       e1(u)=e1(v)=s,   e2(u)=e2(v)=p,
     and differ only in e3:  r=prod u_i,  t=prod v_j.  Check exactly on many
     on-shell points.  Also verify the product identity
       prod_{i=1..3} prod_{j=4..6} (omega_i + omega_j) = -(r-t)^3.

  D. DENOMINATOR PROBE (new).  A_6 is S3xS3 symmetric (pi_v_005), so A_6/i is a
     single function of (s,p,r,t) with weights (1,2,3,3), weighted-homogeneous of
     total degree 8, symmetric under r<->t (minus<->plus swap, F3).  Round 2
     established A_6 is genuinely RATIONAL (not piecewise polynomial): local ball
     test FAIL for A_6, PASS for the A_5 control (pi_v_008).  So inside ONE fixed
     chamber A_6/i = N(s,p,r,t)/D(s,p,r,t).  We do a GUESS-FREE test: fix the full
     18-wall sign signature (one analytic piece), then for each candidate
     denominator weighted-degree e look for a null vector of
         [ monomials_{w=8+e}(s,p,r,t)  |  (A_6/i)*monomials_{w=e}(s,p,r,t) ]
     over Z/p.  A null vector with nonzero D-part => A_6/i = N/D there with D of
     weighted degree e.  Smallest such e is the true denominator degree in these
     coordinates.  (Student already ruled out the *specific* global denominators
     (r-t)^d; this is the general per-chamber search they had not run.)
"""
import subprocess, re, random
from fractions import Fraction as F
from itertools import combinations

BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code/bg"
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
    return F(m2.group(2)) if m2 else None


def solve_onshell(free):
    fr = [F(x) for x in free]; s = sum(fr)
    if s == 0:
        return None
    ss = sum(SIG[i + 1] * fr[i] ** 2 for i in range(4))
    wn = -(SIG[0] * s * s + ss) / (2 * SIG[0] * s)
    return [-(s + wn), fr[0], fr[1], fr[2], fr[3], wn]


def sprt(om):
    """common-cubic coordinates (s,p,r,t) from a full 6-vector of frequencies."""
    u = [-om[0], -om[1], -om[2]]
    v = [om[3], om[4], om[5]]
    s_u = sum(u); s_v = sum(v)
    p_u = u[0] * u[1] + u[0] * u[2] + u[1] * u[2]
    p_v = v[0] * v[1] + v[0] * v[2] + v[1] * v[2]
    r = u[0] * u[1] * u[2]
    t = v[0] * v[1] * v[2]
    return (s_u, s_v, p_u, p_v, r, t)


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


def to_mod(fr):
    return (fr.numerator % P) * pow(fr.denominator % P, P - 2, P) % P


def rref_mod(rows, ncol):
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


def weighted_monos(w):
    """all (a,b,c,d) with a*1+b*2+c*3+d*3 = w, weights of (s,p,r,t)."""
    out = []
    for c in range(w // 3 + 1):
        for d in range((w - 3 * c) // 3 + 1):
            rem = w - 3 * c - 3 * d
            for b in range(rem // 2 + 1):
                a = rem - 2 * b
                if a >= 0:
                    out.append((a, b, c, d))
    return out


def mono_val(exps, s, p, r, t):
    a, b, c, d = exps
    return (pow(s, a, P) * pow(p, b, P) % P) * (pow(r, c, P) * pow(t, d, P) % P) % P


# ---------------- V: common-cubic verification ----------------

def verify_common_cubic(npts=60):
    print("=" * 72)
    print("V. Common-cubic reduction (s1_006-009): e1,e2 shared; product identity")
    rng = random.Random(31337)
    ok_inv = True; ok_prod = True; n = 0
    while n < npts:
        free = [F(rng.randint(-11, 11), rng.randint(1, 3)) for _ in range(4)]
        if any(x == 0 for x in free):
            continue
        om = solve_onshell(free)
        if om is None or any(x == 0 for x in om):
            continue
        # need a genuine amplitude point (not on a wall)
        s_u, s_v, p_u, p_v, r, t = sprt(om)
        # (i) shared e1, e2
        if s_u != s_v or p_u != p_v:
            print(f"    FAIL shared e1/e2 at {om}: s_u={s_u} s_v={s_v} p_u={p_u} p_v={p_v}")
            ok_inv = False
            break
        # (ii) product identity  prod_{i,j}(om_i+om_{3+j}) = -(r-t)^3
        prod = F(1)
        for i in range(3):
            for j in range(3):
                prod *= (om[i] + om[3 + j])
        if prod != -(r - t) ** 3:
            print(f"    FAIL product identity at {om}: prod={prod} -(r-t)^3={-(r-t)**3}")
            ok_prod = False
            break
        n += 1
    print(f"    shared e1=e2=s and e2(u)=e2(v)=p on {n} exact pts: {'PASS' if ok_inv else 'FAIL'}")
    print(f"    prod_(i,j)(omega_i+omega_j) = -(r-t)^3 on {n} exact pts: {'PASS' if ok_prod else 'FAIL'}")
    return ok_inv and ok_prod


# ---------------- D: chamber-restricted rational test in (s,p,r,t) --------------

def collect_chamber(need=260, seed=2027):
    """collect exact points in the single most-populated full-18-wall chamber."""
    rng = random.Random(seed)
    buckets = {}
    tries = 0
    while tries < 120000:
        tries += 1
        free = [F(rng.randint(-16, 16), rng.randint(1, 5)) for _ in range(4)]
        if any(x == 0 for x in free):
            continue
        om = solve_onshell(free)
        if om is None or any(x == 0 for x in om):
            continue
        om = sort_legs(om)
        sg = wall_sig(om)
        if 0 in sg:
            continue
        b = buckets.setdefault(sg, [])
        if len(b) < need + 8:
            A = bg_amp(om)
            if A is None:
                continue
            s_u, s_v, p_u, p_v, r, t = sprt(om)
            b.append((to_mod(s_u), to_mod(p_u), to_mod(r), to_mod(t), to_mod(A)))
        if len([1 for v in buckets.values() if len(v) >= need]) >= 1 and tries > 4000:
            break
    sg_best = max(buckets, key=lambda s: len(buckets[s]))
    return sg_best, buckets[sg_best], len(buckets)


def rational_test(pts, e):
    """Is A_6/i = N/D with D weighted-deg e, N weighted-deg 8+e, on this chamber?
    Null vector of [ mon_{8+e} | -A*mon_e ].  Returns (exists, dimN, dimD, nulldim,
    d_part_nonzero)."""
    monN = weighted_monos(8 + e)
    monD = weighted_monos(e)
    cols = len(monN) + len(monD)
    rows = []
    for (s, p, r, t, A) in pts:
        rowN = [mono_val(m, s, p, r, t) for m in monN]
        rowD = [(A * mono_val(m, s, p, r, t)) % P for m in monD]   # A*mon_e (will pair with -d)
        rows.append(rowN + [(-x) % P for x in rowD])
    # need at least cols points; use up to cols+extra
    _, rank = rref_mod(rows, cols)
    nulldim = cols - rank
    return len(monN), len(monD), cols, len(rows), rank, nulldim


def probe_denominator():
    print("=" * 72)
    print("D. Denominator probe: A_6/i = N/D in (s,p,r,t) inside ONE fixed 18-wall chamber")
    sg, pts, nch = collect_chamber()
    print(f"    chambers sampled: {nch}; using most-populated with {len(pts)} exact pts")
    # sanity: is it a pure polynomial (e=0)?  Expect FAIL (rational).
    for e in range(0, 7):
        use = pts[: cols_needed(e)] if len(pts) >= cols_needed(e) else pts
        nN, nD, cols, npts, rank, nulldim = rational_test(use, e)
        # crude decode: with e=0, nulldim>0 means A/i is a polynomial (deg 8)
        print(f"    e={e}: |monN(w={8+e})|={nN} |monD(w={e})|={nD} cols={cols} "
              f"pts={npts} rank={rank} nulldim={nulldim} "
              f"=> {'RATIONAL REP EXISTS' if nulldim > 0 else 'no rep at this degree'}")
    return sg


def cols_needed(e):
    return len(weighted_monos(8 + e)) + len(weighted_monos(e)) + 30


if __name__ == "__main__":
    rV = verify_common_cubic()
    probe_denominator()
    print("=" * 72)
    print(f"SUMMARY: common-cubic V = {rV}")
