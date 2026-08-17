#!/usr/bin/env python3
"""Fast modular per-RAW-chamber hypothesis testing for A_6 three-minus.

Work mod a large prime P: map each exact Fraction to its residue, do Gaussian
elimination mod P.  Tests whether a target function lies in the linear span of a
feature set (i.e., the target is exactly that polynomial form), and validates on
held-out points.  ~1000x faster than exact-rational RREF; a consistent fit with
held-out matches mod a 62-bit prime is overwhelming evidence (false positive
prob ~ (#features)/P).  Load-bearing fits are re-confirmed exactly elsewhere.
"""
import itertools, random
from fractions import Fraction as F
import harness as h, chambers_n6 as cn

SIG = [-1, -1, -1, 1, 1, 1]
P = (1 << 61) - 1   # Mersenne prime
RAW0 = ((1, 1, 1, -1, -1, -1, -1, -1, -1), (1, 1, 1, -1, -1, -1, -1, -1, -1))


def fr(x):
    """Fraction -> residue mod P."""
    x = F(x)
    return (x.numerator % P) * pow(x.denominator % P, P - 2, P) % P


def gather_raw(rawsig, n, seed, denom=6, rng=40):
    rnd = random.Random(seed)
    pts = []; seen = set(); tries = 0
    while len(pts) < n and tries < n * 3000:
        tries += 1
        free = tuple(F(rnd.randint(-rng, rng), denom) for _ in range(4))
        if any(x == 0 for x in free) or free in seen:
            continue
        seen.add(free)
        oms = cn.solve_squares(free)
        if oms is None or any(w == 0 for w in oms):
            continue
        sq = [w * w for w in oms]
        ws = cn.wall_signs(sq)
        if ws is None or ws != rawsig:
            continue
        try:
            im, _, _ = h.on_shell(list(free), SIG)
        except Exception:
            continue
        pts.append((free, oms, sq, im))
    return pts


def solve_mod(rows, ys):
    """rows: list[list[int mod P]], ys: list[int mod P]. Return solution vector
    (mod P) if consistent, else None.  Augmented Gaussian elimination."""
    nr = len(rows); nc = len(rows[0])
    A = [rows[i][:] + [ys[i]] for i in range(nr)]
    piv = []; r = 0
    for c in range(nc):
        pr = None
        for rr in range(r, nr):
            if A[rr][c] % P:
                pr = rr; break
        if pr is None:
            continue
        A[r], A[pr] = A[pr], A[r]
        inv = pow(A[r][c], P - 2, P)
        A[r] = [(x * inv) % P for x in A[r]]
        for rr in range(nr):
            if rr != r and A[rr][c] % P:
                f = A[rr][c]
                A[rr] = [(A[rr][k] - f * A[r][k]) % P for k in range(nc + 1)]
        piv.append(c); r += 1
        if r == nr:
            break
    for rr in range(nr):
        if all(A[rr][c] % P == 0 for c in range(nc)) and A[rr][nc] % P:
            return None
    sol = [0] * nc
    for i, c in enumerate(piv):
        sol[c] = A[i][nc]
    return sol, piv


def run_test(label, pts, target_fn, feat_fn, ntrain):
    rows = []; ys = []
    for (free, oms, sq, im) in pts:
        t = target_fn(im, oms, sq)
        if t is None:
            continue
        rows.append([fr(x) for x in feat_fn(oms, sq)])
        ys.append(fr(t))
    if len(rows) < ntrain + 5:
        print(f"[{label}] only {len(rows)} usable pts (<{ntrain}+5)")
        return None
    res = solve_mod(rows[:ntrain], ys[:ntrain])
    if res is None:
        print(f"[{label}] INCONSISTENT mod P (target NOT in feature span)")
        return None
    sol, piv = res
    ok = bad = 0
    for row, y in zip(rows[ntrain:], ys[ntrain:]):
        pred = sum(c * v for c, v in zip(sol, row)) % P
        if pred == y % P:
            ok += 1
        else:
            bad += 1
    nz = sum(1 for c in sol if c % P)
    flag = "  <<< FIT" if bad == 0 else ""
    print(f"[{label}] consistent; held-out {ok}/{ok+bad}; rank {len(piv)}/{len(sol)}; nz {nz}{flag}")
    return (sol, piv) if bad == 0 else None


# ---- invariants ----
def Sinv(oms):
    s = oms[0] + oms[1] + oms[2]
    return s * s


def prod6(oms):
    p = F(1)
    for o in oms:
        p *= o
    return p


def e3(oms3):
    return oms3[0] * oms3[1] * oms3[2]
