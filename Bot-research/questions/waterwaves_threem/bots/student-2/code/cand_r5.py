#!/usr/bin/env python3
"""Round-5 candidate tester: evaluate a proposed closed form for A_n/i against the
EXACT oracle at many on-shell points spanning several chambers + near walls.

A candidate is a function cand(w) where w is a 1-based dict {1..n: Fraction} of the
on-shell frequencies; it returns A_n/i (a Fraction) or None if undefined.

Usage: import and call check(cand, n, npts, ...) or run the built-in self-test that
just prints oracle values for inspection.
"""
import itertools, random
from fractions import Fraction as F
import harness as h, r4lib

random.seed(12345)


def rand_free(n, lo=-9, hi=9, dmax=12):
    """Random rational free frequencies (legs 2..n-1) with small denominators."""
    out = []
    for _ in range(n - 2):
        num = random.randint(lo, hi)
        den = random.randint(1, dmax)
        out.append(F(num, den))
    return out


def gen_points(n, npts, seed=None):
    """Generate npts on-shell points (free-freq lists) that the oracle accepts
    (no SIGFPE). Returns list of (free, omegas-dict, A/i)."""
    if seed is not None:
        random.seed(seed)
    pts, tries = [], 0
    while len(pts) < npts and tries < npts * 60:
        tries += 1
        free = rand_free(n)
        if sum(free) == 0:
            continue
        try:
            im, oms, re_p = h.on_shell(free, r4lib.threeminus_signs(n))
        except Exception:
            continue
        if re_p != 0:
            continue
        w = {i + 1: F(oms[i]) for i in range(n)}
        # avoid being on a wall: all mixed sums and matchings nonzero
        ok = all(w[i] != 0 for i in w)
        pts.append((free, w, F(im)))
    return pts


def chamber_tag(w, n):
    """Coarse chamber label: signs of all mixed (1=1) and (1=2) wall functions."""
    M = (1, 2, 3)
    P = tuple(range(4, n + 1))
    tag = []
    for i in M:
        for j in P:
            tag.append('+' if w[j]**2 - w[i]**2 > 0 else '-')
    return ''.join(tag)


def check(cand, n=6, npts=40, verbose=True, seed=7):
    pts = gen_points(n, npts, seed=seed)
    chambers = {}
    ok = bad = undef = 0
    fails = []
    for free, w, im in pts:
        val = cand(w)
        tag = chamber_tag(w, n)
        chambers.setdefault(tag, [0, 0])
        if val is None:
            undef += 1
            continue
        if val == im:
            ok += 1
            chambers[tag][0] += 1
        else:
            bad += 1
            chambers[tag][1] += 1
            if len(fails) < 8:
                fails.append((free, im, val, im - val))
    if verbose:
        print(f"n={n}: {ok}/{ok+bad+undef} exact  (bad={bad}, undef={undef}), "
              f"{len(chambers)} chamber types")
        for free, im, val, d in fails:
            print(f"   FAIL free={[str(x) for x in free]}\n      oracle={im}\n      cand  ={val}\n      diff  ={d}  ratio={F(im)/val if val else None}")
    return ok, bad, undef


if __name__ == "__main__":
    # show the spread of oracle values / chambers we can reach
    for n in (5, 6, 7):
        pts = gen_points(n, 25, seed=3)
        tags = set(chamber_tag(w, n) for _, w, _ in pts)
        print(f"n={n}: {len(pts)} pts, {len(tags)} distinct chamber tags")
