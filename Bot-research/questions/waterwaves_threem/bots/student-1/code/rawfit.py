#!/usr/bin/env python3
"""Per-RAW-chamber exact hypothesis testing for A_6 three-minus.
A canonical chamber is a union of symmetry-related raw chambers separated by
walls, so the per-chamber polynomial must be fit on a single RAW chamber
(fixed (W1,W2) sign pattern)."""
import itertools, random, sys
from fractions import Fraction as F
import harness as h, chambers_n6 as cn
from exactfit import exact_solve

SIG = [-1, -1, -1, 1, 1, 1]

# most common raw chamber (a_1 dominates the minus legs)
RAW0 = ((1, 1, 1, -1, -1, -1, -1, -1, -1), (1, 1, 1, -1, -1, -1, -1, -1, -1))


def gather_raw(rawsig, n, seed, denom=6, rng=30):
    rnd = random.Random(seed)
    pts = []; seen = set()
    tries = 0
    while len(pts) < n and tries < n * 2000:
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


def Sinv(oms):
    s = oms[0] + oms[1] + oms[2]
    return s * s


def pos(x):
    return x if x > 0 else F(0)


def subset_sums(vals):
    out = []
    for mask in range(8):
        s = F(0); k = 0
        for b in range(3):
            if mask & (1 << b):
                s += vals[b]; k += 1
        out.append((s, k))
    return out


def B3(a, b):
    SA = subset_sums(a); SB = subset_sums(b); t = F(0)
    for sS, kS in SA:
        for sT, kT in SB:
            t += ((-1) ** (kS + kT)) * pos(sT - sS) ** 3
    return t


def run_test(label, pts, target_fn, feat_fn, ntrain):
    rows = []; ys = []
    for (free, oms, sq, im) in pts:
        t = target_fn(im, oms, sq)
        if t is None:
            continue
        rows.append(feat_fn(oms, sq)); ys.append(t)
    if len(rows) < ntrain + 5:
        print(f"[{label}] not enough usable points ({len(rows)})")
        return None
    sol = exact_solve(rows[:ntrain], ys[:ntrain])
    if sol is None:
        print(f"[{label}] INCONSISTENT")
        return None
    ok = bad = 0
    for row, y in zip(rows[ntrain:], ys[ntrain:]):
        pred = sum(c * v for c, v in zip(sol, row))
        if pred == y:
            ok += 1
        else:
            bad += 1
    nz = sum(1 for c in sol if c != 0)
    print(f"[{label}] consistent; held-out exact {ok}/{ok+bad}; nonzero {nz}/{len(sol)}")
    return sol if bad == 0 else None


def monos_sq(deg):
    M = [e for e in itertools.product(range(deg + 1), repeat=6) if sum(e) == deg]
    def f(oms, sq):
        return [sq[0]**e[0]*sq[1]**e[1]*sq[2]**e[2]*sq[3]**e[3]*sq[4]**e[4]*sq[5]**e[5] for e in M]
    return f, M


if __name__ == "__main__":
    pts = gather_raw(RAW0, 220, seed=11)
    print(f"gathered {len(pts)} points in raw chamber RAW0")
    pairs = list(itertools.combinations_with_replacement(range(6), 2))
    # H1: C = (deg-2 bare poly) * B3
    run_test("H1: C=(deg2 bare omega)*B3", pts, lambda im, oms, sq: F(im, 32),
             lambda oms, sq: [oms[i]*oms[j]*B3(sq[0:3], sq[3:6]) for (i, j) in pairs], 30)
    # H2: C / (1/2 (S-Q)) = deg-3 poly in squares  (n=5 analog)
    f3, M3 = monos_sq(3)
    def tgt2(im, oms, sq):
        pref = (Sinv(oms) - (sq[0]+sq[1]+sq[2])) / 2
        return None if pref == 0 else F(im, 32) / pref
    run_test("H2: C/(1/2(S-Q))=deg3 poly in squares", pts, tgt2, f3, 65)
    # H3: C = deg-4 poly in squares
    f4, M4 = monos_sq(4)
    run_test("H3: C=deg4 poly in squares", pts, lambda im, oms, sq: F(im, 32), f4, 135)
