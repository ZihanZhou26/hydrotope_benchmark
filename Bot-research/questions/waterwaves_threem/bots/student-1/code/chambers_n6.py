#!/usr/bin/env python3
"""Enumerate the REALIZABLE chambers of the n=6 three-minus wall arrangement.

Sector: minus legs {1,2,3}, plus legs {4,5,6}.  On-shell (oracle solve):
  free = (w2,w3,w4,w5);  w1,w6 solved from sum w = 0 and sum sigma w^2 = 0.
Constraints on squares:  a1+a2+a3 = b4+b5+b6 = Q   (a_i=w_i^2 minus, b_j=w_j^2 plus).

Genuine mixed-subset walls k_S = sum_{i in S} sigma_i w_i^2 = 0 reduce to TWO types:
  (1=1)  a_i = b_j                  (S = {i,j}, also the (2,2) complement)
  (1=2)  a_i = b_j + b_k            (S = {i,j,k}; equivalently b_r = a_p + a_q)
All other mixed subsets have a definite sign on-shell (never wall) -- proven in
derivations/n6_chambers.md.  The 9+9 = 18 functions W1[i][j]=a_i-b_j and
W2[i][{j,k}]=a_i-b_j-b_k fully determine the chamber.

This file needs NO oracle: chamber membership depends only on the squares, which
we get from the exact rational on-shell solve.  Fast -> scan millions of points.
"""
import itertools, sys
from fractions import Fraction as F

MINUS = [0, 1, 2]      # 0-indexed legs 1,2,3
PLUS = [3, 4, 5]       # 0-indexed legs 4,5,6
SIGNS = [-1, -1, -1, 1, 1, 1]


def solve_squares(free):
    """free = (w2,w3,w4,w5) Fractions. Return (oms list of 6 Fractions, squares)
    using the SAME solve as bg.cpp. Returns None if sumFree==0 (degenerate)."""
    free = [F(x) for x in free]
    s1 = F(-1)
    sumFree = sum(free)
    if sumFree == 0:
        return None
    # signs of legs 2,3,4,5 = -1,-1,1,1
    sumSig = (-1) * free[0]**2 + (-1) * free[1]**2 + free[2]**2 + free[3]**2
    w6 = -(s1 * sumFree**2 + sumSig) / (2 * s1 * sumFree)
    w1 = -(sumFree + w6)
    oms = [w1, free[0], free[1], free[2], free[3], w6]
    return oms


def wall_signs(sq):
    """sq = list of 6 squares [a1,a2,a3,b4,b5,b6]. Returns (W1signs, W2signs)
    or None if ON a wall (some function == 0)."""
    a = [sq[i] for i in MINUS]
    b = [sq[j] for j in PLUS]
    W1 = []
    for i in range(3):
        for j in range(3):
            v = a[i] - b[j]
            if v == 0:
                return None
            W1.append(1 if v > 0 else -1)
    W2 = []
    for i in range(3):
        for (j, k) in itertools.combinations(range(3), 2):
            v = a[i] - b[j] - b[k]
            if v == 0:
                return None
            W2.append(1 if v > 0 else -1)
    return tuple(W1), tuple(W2)


# ---- symmetry group: 3! perms of minus x 3! perms of plus x Z_2 swap ----
def canonical(sq):
    """Return a canonical (sorted-by-symmetry) signature of the chamber of sq,
    by applying all 72 group elements and taking the min signature tuple.
    Each element: permute minus a's by pm, plus b's by pp, optionally swap a<->b.
    Recompute (W1,W2) for the transformed squares; that already encodes signs."""
    a0 = [sq[i] for i in MINUS]
    b0 = [sq[j] for j in PLUS]
    best = None
    for swap in (False, True):
        A0, B0 = (b0, a0) if swap else (a0, b0)
        for pm in itertools.permutations(range(3)):
            A = [A0[p] for p in pm]
            for pp in itertools.permutations(range(3)):
                B = [B0[p] for p in pp]
                ws = wall_signs(A + B)
                if ws is None:
                    return None
                sig = ws[0] + ws[1]
                if best is None or sig < best:
                    best = sig
    return best


def scan(nsamp, seed, denom=12, span=6):
    import random
    rnd = random.Random(seed)
    chambers = {}   # canonical sig -> [count, representative free point, rep squares]
    raw = {}        # raw (W1,W2) signature -> [count, rep free, rep squares]
    canon_cache = {}  # raw ws -> canonical sig (canonical is a pure fn of raw ws)
    on_wall = 0
    degen = 0
    for _ in range(nsamp):
        free = tuple(F(rnd.randint(-span * denom, span * denom), denom)
                     for _ in range(4))
        if any(x == 0 for x in free):
            continue
        oms = solve_squares(free)
        if oms is None:
            degen += 1
            continue
        if any(w == 0 for w in oms):
            continue
        sq = [w * w for w in oms]
        ws = wall_signs(sq)
        if ws is None:
            on_wall += 1
            continue
        if ws not in raw:
            raw[ws] = [1, free, tuple(sq)]
        else:
            raw[ws][0] += 1
        c = canon_cache.get(ws)
        if c is None:
            c = canonical(sq)
            canon_cache[ws] = c
        if c not in chambers:
            chambers[c] = [1, free, tuple(sq)]
        else:
            chambers[c][0] += 1
    return chambers, raw, on_wall, degen


if __name__ == "__main__":
    nsamp = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
    chambers, raw, on_wall, degen = scan(nsamp, seed=20260626)
    print(f"samples={nsamp}  on_wall_skipped={on_wall}  degen(sumFree=0)={degen}")
    print(f"# distinct RAW chambers (18-sign patterns): {len(raw)}")
    print(f"# distinct chamber TYPES (up to S3xS3xZ2): {len(chambers)}")
    print()
    # order by frequency
    items = sorted(chambers.items(), key=lambda kv: -kv[1][0])
    for idx, (sig, (cnt, free, sq)) in enumerate(items):
        a = [sq[i] for i in MINUS]
        b = [sq[j] for j in PLUS]
        print(f"--- chamber type T{idx}  (count {cnt}) ---")
        print(f"   rep free (w2,w3,w4,w5) = {tuple(str(x) for x in free)}")
        print(f"   minus a={[str(x) for x in a]}")
        print(f"   plus  b={[str(x) for x in b]}")
