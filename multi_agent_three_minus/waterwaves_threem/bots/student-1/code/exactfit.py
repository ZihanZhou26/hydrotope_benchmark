#!/usr/bin/env python3
"""Exact (Fraction) per-chamber polynomial fitting / hypothesis testing.
Reusable: given a chamber signature, a target function target(im,oms,sq),
and a feature list feats(oms,sq) -> list[Fraction], fit exactly and validate
on held-out points (exact rational match)."""
import itertools, random
from fractions import Fraction as F
import harness as h
import chambers_n6 as cn

SIG = [-1, -1, -1, 1, 1, 1]


def gather(sig, n, seed, rng=12):
    rnd = random.Random(seed)
    pts = []
    seen = set()
    while len(pts) < n:
        free = tuple(F(rnd.randint(-rng, rng)) for _ in range(4))
        if any(x == 0 for x in free) or free in seen:
            continue
        seen.add(free)
        oms = cn.solve_squares(free)
        if oms is None or any(w == 0 for w in oms):
            continue
        sq = [w * w for w in oms]
        ws = cn.wall_signs(sq)
        if ws is None or cn.canonical(sq) != sig:
            continue
        try:
            im, om2, _ = h.on_shell(list(free), SIG)
        except Exception:
            continue   # oracle |k_S|=0 SIGFPE on this lattice point; skip
        pts.append((free, oms, sq, im))
    return pts


def exact_solve(rows, ys):
    ncol = len(rows[0])
    A = [r[:] + [ys[i]] for i, r in enumerate(rows)]
    nr = len(A)
    piv = []
    r = 0
    for c in range(ncol):
        pr = None
        for rr in range(r, nr):
            if A[rr][c] != 0:
                pr = rr; break
        if pr is None:
            continue
        A[r], A[pr] = A[pr], A[r]
        inv = A[r][c]
        A[r] = [x / inv for x in A[r]]
        for rr in range(nr):
            if rr != r and A[rr][c] != 0:
                f = A[rr][c]
                A[rr] = [A[rr][k] - f * A[r][k] for k in range(ncol + 1)]
        piv.append(c); r += 1
        if r == nr:
            break
    for rr in range(nr):
        if all(A[rr][c] == 0 for c in range(ncol)) and A[rr][ncol] != 0:
            return None
    sol = [F(0)] * ncol
    for i, c in enumerate(piv):
        sol[c] = A[i][ncol]
    return sol


def test_hyp(sig, label, target_fn, feat_fn, nfeat_hint, ntrain, pts):
    rows = []; ys = []
    for (free, oms, sq, im) in pts:
        t = target_fn(im, oms, sq)
        if t is None:
            continue
        rows.append(feat_fn(oms, sq)); ys.append(t)
    sol = exact_solve(rows[:ntrain], ys[:ntrain])
    if sol is None:
        print(f"[{label}] INCONSISTENT (target is not in the feature span)")
        return False, None
    ok = bad = 0
    for row, y in zip(rows[ntrain:], ys[ntrain:]):
        pred = sum(c * v for c, v in zip(sol, row))
        if pred == y:
            ok += 1
        else:
            bad += 1
    nz = sum(1 for c in sol if c != 0)
    print(f"[{label}] consistent on {ntrain}; held-out exact {ok}/{ok+bad}; nonzero coeffs {nz}/{len(sol)}")
    return bad == 0, sol


# ---------- feature builders ----------
def monos(deg, nv):
    return [e for e in itertools.product(range(deg + 1), repeat=nv) if sum(e) == deg]


def sq_features(deg):
    M = monos(deg, 6)
    def f(oms, sq):
        return [sq[0]**e[0]*sq[1]**e[1]*sq[2]**e[2]*sq[3]**e[3]*sq[4]**e[4]*sq[5]**e[5]
                for e in M]
    return f, M


if __name__ == "__main__":
    T0free = (F(11, 12), F(11, 4), F(4, 3), F(5, 12))
    sig = cn.canonical([w*w for w in cn.solve_squares(T0free)])
    pts = gather(sig, 200, seed=5, rng=13)
    print(f"gathered {len(pts)} integer points in chamber T0")
    f4, M4 = sq_features(4)
    test_hyp(sig, "C = deg4 poly in squares",
             lambda im, oms, sq: F(im, 32),
             f4, len(M4), 130, pts)
