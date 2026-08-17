"""gendata.py — generate exact three-minus (free_w -> omega, B) tables.

B := A/i (real). We store omega (Fractions) and B (Fraction). Used for fitting
and verification. Sampling uses the on-shell solver (free freqs = omega_2..omega_{n-1}).
"""
import json, itertools, random
from fractions import Fraction as Fr
import harness


def three_minus_sigma(n):
    return [-1, -1, -1] + [1] * (n - 3)


def gen(n, free_list, g=1, double=False):
    sigma = three_minus_sigma(n)
    rows = []
    for fw in free_list:
        try:
            r = harness.onshell(n, fw, sigma, g=g, double=double)
        except Exception as e:
            rows.append({"free_w": [str(x) for x in fw], "error": str(e)})
            continue
        rows.append({
            "free_w": [str(x) for x in fw],
            "omega": [str(x) for x in r["omega"]],
            "A_re": str(r["A_re"]),
            "B": str(r["A_im"]),
        })
    return rows


def rand_free(n, rng, denom=6, lo=1, hi=8):
    """Random rational free freqs (positive); n-2 of them."""
    out = []
    for _ in range(n - 2):
        num = rng.randint(lo, hi * denom)
        out.append(Fr(num, rng.randint(1, denom)))
    return out


def grid_free_n5(maxv=6):
    """All integer (w2,w3,w4) in [1,maxv]^3 (w2,w3 minus; w4 plus)."""
    out = []
    for a in range(1, maxv + 1):
        for b in range(a, maxv + 1):       # w2<=w3 by symmetry of minus legs
            for c in range(1, maxv + 1):   # w4 plus
                out.append([a, b, c])
    return out


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    rng = random.Random(12345)
    if n == 5:
        fl = grid_free_n5(6)
    else:
        fl = [rand_free(n, rng) for _ in range(60)]
    rows = gen(n, fl)
    out = f"../data/three_minus_n{n}.json"
    with open(out, "w") as f:
        json.dump(rows, f)
    nbad = sum(1 for r in rows if "error" in r)
    print(f"n={n}: wrote {len(rows)} rows ({nbad} errors) -> {out}")
