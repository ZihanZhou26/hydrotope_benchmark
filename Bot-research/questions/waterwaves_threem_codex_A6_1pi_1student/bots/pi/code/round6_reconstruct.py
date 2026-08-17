#!/usr/bin/env python3
"""PI round-6: DEHOMOGENIZED in-piece reconstruction of H = A_6/(i prod omega).

pi_v_019 fit H in the 4 free frequencies with inhomogeneous monomials of degree
<= d and found NO rep for d<=7 (=> in-piece denom degree >= 6-8), but stopped
before actually finding H because a 4-var deg-10 fit is too big.

KEY OPTIMIZATION: H is EXACTLY degree-2 homogeneous (pi_v_012), and ALL 53
surfaces (18 walls + 35 factorization surfaces h_S) are homogeneous of degree 2,
so a single true piece is a CONE.  Scale every point to omega2=1: with
x=w3/w2, y=w4/w2, z=w5/w2 the target
      h(x,y,z) := H(omega) / omega2^2
is an INHOMOGENEOUS rational function of just 3 variables.  Fit
      h = P(x,y,z) / Q(x,y,z),   deg P, deg Q <= d,
by a modular null-space search of [ M_{<=d}(x,y,z) | -h*M_{<=d}(x,y,z) ].
Minimal d with a null vector = degP = degQ+2; extract & FACTOR Q.

Phase 1 (rank scan): numpy over the 31-bit Mersenne prime (fast) to find d_min.
Phase 2 (extract): recompute the unique null vector over P=2^61-1 with exact
python-int RREF, rational-reconstruct, hand P,Q to sympy.factor.

Exact: fresh bg_r6 (GMP).  Points collected once and reused for all degrees.
"""
import subprocess, re, random, sys, json
from itertools import combinations
from fractions import Fraction as F

BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code/bg_r6"
SIG = [-1, -1, -1, 1, 1, 1]
P61 = (1 << 61) - 1
P31 = (1 << 31) - 1          # 2147483647, Mersenne prime, numpy-int64 safe


def bg_amp(om, g=F(1)):
    K = [SIG[i] * om[i] * om[i] / g for i in range(6)]
    p = subprocess.run([BG, "--amp", "-K", ",".join(str(x) for x in K),
                        "-W", ",".join(str(x) for x in om), "-g", str(g)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       universal_newlines=True)
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


def find_base(rng):
    best = None
    for _ in range(40000):
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


def collect(base_f, base_sg, need, seed=777):
    """Collect in-piece points; store exact (x,y,z,h) with x=w3/w2,y=w4/w2,z=w5/w2,
    h = (A_im/prod omega)/w2^2 as exact Fractions."""
    rng = random.Random(seed)
    pts = []; tries = 0
    while len(pts) < need and tries < 3000000:
        tries += 1
        # jitter around the base in the free coords with varied denominators
        den = rng.choice([3, 4, 5, 6, 7, 8, 11, 13])
        f = [base_f[i] + F(rng.randint(-9, 9), den) for i in range(4)]
        if any(x == 0 for x in f) or sum(f) == 0:
            continue
        om = solve_onshell(f)
        if om is None or any(x == 0 for x in om) or not generic(om):
            continue
        sg, _ = full_sign_and_margin(om)
        if sg != base_sg:
            continue
        w2 = om[1]
        if w2 == 0:
            continue
        A = bg_amp(om)
        if A is None:
            continue
        prod = F(1)
        for wv in om:
            prod *= wv
        Hval = A / prod                      # H = A_6/(i prod omega)
        x = om[2] / w2; y = om[3] / w2; z = om[4] / w2
        h = Hval / (w2 * w2)                 # dehomogenized target
        pts.append((x, y, z, h))
    return pts, tries


def monos_upto(d):
    out = []
    for a in range(d + 1):
        for b in range(d + 1 - a):
            for c in range(d + 1 - a - b):
                out.append((a, b, c))
    return out


def reduce_pt(pt, p):
    x, y, z, h = pt
    def rm(fr):
        return (fr.numerator % p) * pow(fr.denominator % p, p - 2, p) % p
    return rm(x), rm(y), rm(z), rm(h)


def build_rows_np(pts, mon, p):
    import numpy as np
    nm = len(mon)
    X = np.empty((len(pts), 2 * nm), dtype=np.int64)
    for r, pt in enumerate(pts):
        xm, ym, zm, hm = reduce_pt(pt, p)
        # monomial values
        xp = [pow(xm, e, p) for e in range(max(m[0] for m in mon) + 1)]
        yp = [pow(ym, e, p) for e in range(max(m[1] for m in mon) + 1)]
        zp = [pow(zm, e, p) for e in range(max(m[2] for m in mon) + 1)]
        mv = np.empty(nm, dtype=np.int64)
        for k, (a, b, c) in enumerate(mon):
            mv[k] = (xp[a] * yp[b] % p) * zp[c] % p
        X[r, :nm] = mv
        X[r, nm:] = (-(hm) % p) * mv % p
        X[r, nm:] %= p
    return X


def rank_mod_np(X, p):
    import numpy as np
    A = X.copy().astype(np.int64) % p
    m, ncol = A.shape
    rank = 0
    for col in range(ncol):
        piv = -1
        for r in range(rank, m):
            if A[r, col] % p != 0:
                piv = r; break
        if piv < 0:
            continue
        A[[rank, piv]] = A[[piv, rank]]
        inv = pow(int(A[rank, col]), p - 2, p)
        A[rank] = (A[rank] * inv) % p
        # eliminate all other rows
        colvals = A[:, col].copy()
        for r in range(m):
            if r != rank and colvals[r] % p != 0:
                A[r] = (A[r] - colvals[r] * A[rank]) % p
        rank += 1
        if rank == m:
            break
    return rank


def main():
    need = int(sys.argv[1]) if len(sys.argv) > 1 else 900
    dmax = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    bseed = int(sys.argv[3]) if len(sys.argv) > 3 else 2026
    ptsfile = sys.argv[4] if len(sys.argv) > 4 else "round6_points.json"
    rng = random.Random(bseed)
    base_f, base_sg, margin, om0 = find_base(rng)
    print("base free:", [str(x) for x in base_f], " om0:", [str(x) for x in om0])
    print("margin:", float(margin))
    pts, tries = collect(base_f, base_sg, need, seed=bseed * 3 + 1)
    print(f"collected {len(pts)} in-piece points (tries={tries})")
    # save points for the extract phase
    with open(ptsfile, "w") as fh:
        json.dump({"base_f": [str(x) for x in base_f], "base_sg": list(base_sg),
                   "pts": [[str(a) for a in pt] for pt in pts]}, fh)
    sys.stdout.flush()

    import numpy as np
    print("-" * 72)
    dmin = None
    for d in range(3, dmax + 1):
        mon = monos_upto(d); nm = len(mon); ncol = 2 * nm
        if len(pts) < ncol + 12:
            print(f"d={d}: cols={ncol} pts={len(pts)} -> NEED MORE PTS ({ncol+12})")
            break
        # use all but 10 holdout rows to fit; then rank test on full
        X = build_rows_np(pts, mon, P31)
        rank = rank_mod_np(X, P31)
        nulldim = ncol - rank
        tag = "REP EXISTS" if nulldim > 0 else "no rep"
        print(f"d={d}: |M|={nm} cols={ncol} pts={len(pts)} rank={rank} "
              f"nulldim={nulldim} => {tag}")
        sys.stdout.flush()
        if nulldim > 0:
            dmin = d
            break
    if dmin is None:
        print("\n==> no rational rep up to d=%d in a single TRUE piece." % dmax)
    else:
        print("\n==> minimal in-piece degree d_min =", dmin,
              "(=> deg Q =", dmin - 2, ", deg P =", dmin, ")")
    with open("round6_rankscan.txt", "a") as fh:
        fh.write(f"need={need} dmax={dmax} dmin={dmin} npts={len(pts)}\n")


if __name__ == "__main__":
    main()
