"""
Map the piecewise structure and confirm a_n = F_n(e1,e2) in the 'interleaving'
region (all plus |omega| between the two minus |omega|), for n=5,6,7.
"""
import mpmath as mp
import random
from bg_float import amp_from_allW

mp.mp.dps = 50


def sig(n):
    return [-1, -1] + [1] * (n - 2)


def a_n(allW, n):
    A = amp_from_allW(allW, sig(n))
    return A.imag, A.real


print("=== (1) fine z-scan, n=5, minus=(-4,1) ===")
w1, w2 = mp.mpf(-4), mp.mpf(1)
A_ = -(w1 + w2)
B_ = w1 ** 2 + w2 ** 2
z = mp.mpf('-2.0')
while z <= mp.mpf('4.0'):
    s = A_ - z
    q = B_ - z ** 2
    disc = 2 * q - s ** 2  # = s^2-4xy
    if disc >= 0:
        r = mp.sqrt(disc)
        x, y = (s + r) / 2, (s - r) / 2
        try:
            im, re = a_n([w1, w2, x, y, z], 5)
            mags = sorted([abs(x), abs(y), abs(z)])
            flat = all(mp.mpf(1) < abs(v) < mp.mpf(4) for v in (x, y, z))
            print(f"  z={mp.nstr(z,3):>6}  plus|w|={[mp.nstr(m,3) for m in mags]}  "
                  f"a_5={mp.nstr(im,12):>16}  flat={flat}")
        except Exception as e:
            pass
    z += mp.mpf('0.25')


def flat_config(n, w1, w2, free_vals):
    """Build plus legs: free_vals (len n-4) plus 2 solved legs. Returns allW or None."""
    A = -(w1 + w2)
    B = w1 ** 2 + w2 ** 2
    s = A - sum(free_vals)
    q = B - sum(v ** 2 for v in free_vals)
    disc = 2 * q - s ** 2
    if disc < 0:
        return None
    r = mp.sqrt(disc)
    x, y = (s + r) / 2, (s - r) / 2
    return [w1, w2] + list(free_vals) + [x, y]


def in_interval(v, m, M):
    return m < abs(v) < M


print("\n=== (2) F_n(e1,e2)-only test in interleaving region ===")
rng = random.Random(3)
for n in (5, 6, 7):
    # minus pair with |w1|>|w2|
    w1, w2 = mp.mpf(-5), mp.mpf(2)
    m, M = abs(w2), abs(w1)
    vals = []
    attempts = 0
    while len(vals) < 6 and attempts < 4000:
        attempts += 1
        free = [mp.mpf(rng.uniform(-4.9, 4.9)) for _ in range(n - 4)]
        if any(not in_interval(v, m, M) for v in free):
            continue
        cfg = flat_config(n, w1, w2, free)
        if cfg is None:
            continue
        x, y = cfg[-2], cfg[-1]
        if not (in_interval(x, m, M) and in_interval(y, m, M)):
            continue
        try:
            im, re = a_n(cfg, n)
        except Exception:
            continue
        if abs(re) > mp.mpf('1e-30'):
            continue
        vals.append(im)
    if len(vals) >= 2:
        spread = max(vals) - min(vals)
        e1, e2 = w1 + w2, w1 * w2
        print(f"  n={n} minus=(-5,2) e1={e1} e2={e2}: {len(vals)} flat configs, "
              f"a_n={mp.nstr(vals[0],12)}, spread={mp.nstr(spread,4)} "
              f"=> {'F_n(e1,e2) ONLY' if abs(spread)<mp.mpf('1e-25') else 'DEPENDS ON PLUS'}")
    else:
        print(f"  n={n}: not enough flat configs found")
