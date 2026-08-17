#!/usr/bin/env python3
"""Exact candidate-formula tester for n=6 three-minus, against MY own ./bg.

A candidate is a function cand(oms) -> Fraction giving the predicted A_n/i
(imaginary coefficient), with oms = list of n frequencies (Fractions).
We compare to the oracle's exact A/i at many on-shell points across chambers.
"""
import itertools, sys
from fractions import Fraction as F
import harness as h
import chambers_n6 as cn

SIGNS6 = [-1, -1, -1, 1, 1, 1]


def pos(x):
    return x if x > 0 else F(0)


def oracle(free, signs=SIGNS6):
    im, oms, re_p = h.on_shell(free, signs)
    assert re_p == 0
    return im, oms


# ---------- building blocks ----------
def Pblock(triple_sq, t, d):
    """sum_{S subseteq triple} (-1)^|S| (t - sum_S)_+^d ; triple_sq = 3 squares."""
    s = F(0)
    for mask in range(8):
        c = F(0); k = 0
        for b in range(3):
            if mask & (1 << b):
                c += triple_sq[b]; k += 1
        s += ((-1) ** k) * pos(t - c) ** d
    return s


def collect_points(per_type=6, nsamp=60000, seed=7):
    """Return list of free-tuples, >=per_type interior rational points per chamber
    TYPE (canonicalized), spanning all realizable chambers found."""
    import random
    rnd = random.Random(seed)
    buckets = {}
    tries = 0
    while tries < nsamp:
        tries += 1
        free = tuple(F(rnd.randint(-72, 72), 12) for _ in range(4))
        if any(x == 0 for x in free):
            continue
        oms = cn.solve_squares(free)
        if oms is None or any(w == 0 for w in oms):
            continue
        sq = [w * w for w in oms]
        ws = cn.wall_signs(sq)
        if ws is None:
            continue
        c = cn.canonical(sq)
        buckets.setdefault(c, [])
        if len(buckets[c]) < per_type:
            buckets[c].append(free)
        if all(len(v) >= per_type for v in buckets.values()) and len(buckets) >= 12:
            pass
    pts = []
    for c, lst in buckets.items():
        pts.extend(lst)
    return pts, buckets


def test_candidate(cand, pts, label="cand", verbose=True, prefac=F(1)):
    """cand(oms)->Fraction predicts A/i / prefac. Compare prefac*cand to oracle A/i."""
    ok = 0; bad = 0; ratios = set()
    fails = []
    for free in pts:
        try:
            A, oms = oracle(list(free))
        except Exception:
            continue
        pred = prefac * cand(oms)
        if pred == A:
            ok += 1
        else:
            bad += 1
            if cand(oms) != 0:
                ratios.add(A / cand(oms))
            fails.append((free, A, pred))
    if verbose:
        print(f"[{label}] exact match {ok}/{ok+bad}", end="")
        if bad:
            rs = list(ratios)[:6]
            print(f"   (#distinct A/cand ratios on misses: {len(ratios)}; sample {rs})")
        else:
            print("   ALL EXACT")
    return ok, bad, ratios, fails


if __name__ == "__main__":
    pts, buckets = collect_points()
    print(f"collected {len(pts)} points across {len(buckets)} chamber types")
