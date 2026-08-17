"""chamber.py — chamber signature (signs of all subset momenta) and single-chamber boxes."""
from fractions import Fraction as Fr
from itertools import combinations
import harness

SIGMA6 = [-1, -1, -1, 1, 1, 1]


def signature(omega, sigma=SIGMA6):
    """Sign vector of subset momenta k_S = sum_{i in S} sigma_i omega_i^2 for all
    subsets S with 1<=|S|<=n-1, canonicalized (S and complement share a wall)."""
    n = len(omega)
    sig = []
    seen = set()
    idx = list(range(n))
    for r in range(1, n):
        for S in combinations(idx, r):
            comp = tuple(i for i in idx if i not in S)
            key = min(S, comp)
            if key in seen:
                continue
            seen.add(key)
            kS = sum(sigma[i] * Fr(omega[i]) ** 2 for i in S)
            sig.append(0 if kS == 0 else (1 if kS > 0 else -1))
    return tuple(sig)


def onshell_omega(free_w, sigma=SIGMA6):
    n = len(sigma)
    W, K = harness.solve_kinematics(n, free_w, sigma)
    return W


def box_single_chamber(centers, idxs, half, steps, sigma=SIGMA6):
    """Check the box (centers +/- half in dims idxs) is one chamber by sampling a
    grid; returns (is_single, signature_or_None, sampled_points list of free_w)."""
    base = list(centers)
    grid_axes = []
    for d in idxs:
        c = centers[d]
        grid_axes.append([c - half + 2 * half * Fr(k, steps) for k in range(steps + 1)])
    pts = []
    sigs = set()
    import itertools
    for combo in itertools.product(*grid_axes):
        fw = list(base)
        for d, v in zip(idxs, combo):
            fw[d] = v
        try:
            om = onshell_omega(fw, sigma)
            s = signature(om, sigma)
            if 0 in s:
                continue  # on a wall
            sigs.add(s)
            pts.append(fw)
        except Exception:
            pass
    return (len(sigs) == 1), (next(iter(sigs)) if len(sigs) == 1 else None), pts


if __name__ == "__main__":
    # canonical free=(2,3,5,4)
    om = onshell_omega([Fr(2), Fr(3), Fr(5), Fr(4)])
    print("canonical omega:", [str(x) for x in om])
    print("canonical signature:", signature(om))
    # find a single-chamber box varying w4,w5 (idx 2,3)
    for half in [Fr(4, 10), Fr(3, 10), Fr(2, 10), Fr(1, 10), Fr(1, 20)]:
        ok, s, pts = box_single_chamber([Fr(2), Fr(3), Fr(5), Fr(4)], [2, 3], half, 8)
        print(f"half={float(half)}: single_chamber={ok}  npts={len(pts)}")
        if ok:
            print("  -> single chamber box found at half=", float(half))
            break
