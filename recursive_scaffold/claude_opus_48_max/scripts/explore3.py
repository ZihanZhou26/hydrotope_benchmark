"""
Tabulate F_n(e1,e2) for n=5..8 over many minus pairs (flat/interleaving region),
to fit F_5(e1,e2) and the n-ratio c(e1,e2)=F_{n+1}/F_n.
"""
import mpmath as mp
import random
from bg_float import amp_from_allW

mp.mp.dps = 50


def sig(n):
    return [-1, -1] + [1] * (n - 2)


def flat_config(n, w1, w2, free_vals):
    A = -(w1 + w2)
    B = w1 ** 2 + w2 ** 2
    s = A - sum(free_vals)
    q = B - sum(v ** 2 for v in free_vals)
    disc = 2 * q - s ** 2
    if disc < 0:
        return None
    r = mp.sqrt(disc)
    return [w1, w2] + list(free_vals) + [(s + r) / 2, (s - r) / 2]


def get_Fn(n, w1, w2, rng):
    """Find a flat (interleaving) config and return a_n (= F_n(e1,e2))."""
    m, M = abs(w2), abs(w1)
    if m > M:
        m, M = M, m
    for _ in range(8000):
        free = [mp.mpf(rng.uniform(float(-M) + 0.05, float(M) - 0.05)) for _ in range(n - 4)]
        if any(not (m < abs(v) < M) for v in free):
            continue
        cfg = flat_config(n, w1, w2, free)
        if cfg is None:
            continue
        x, y = cfg[-2], cfg[-1]
        if not (m < abs(x) < M and m < abs(y) < M):
            continue
        try:
            A = amp_from_allW(cfg, sig(n))
        except Exception:
            continue
        if abs(A.real) > mp.mpf('1e-25'):
            continue
        return A.imag
    return None


minus_pairs = [(-4, 1), (-5, 2), (-5, 1), (-6, 1), (-6, 2), (-4, 2),
               (-5, 3), (-7, 2), (-6, 3), (-7, 3), (-3, 1), (-8, 3)]

print(f"{'minus':>10} {'e1':>5} {'e2':>5} | {'F5':>14} {'F6':>16} {'F7':>18} | {'F6/F5':>10} {'F7/F6':>10}")
rng = random.Random(11)
rows = []
for (a, b) in minus_pairs:
    w1, w2 = mp.mpf(a), mp.mpf(b)
    e1, e2 = w1 + w2, w1 * w2
    F5 = get_Fn(5, w1, w2, rng)
    F6 = get_Fn(6, w1, w2, rng)
    F7 = get_Fn(7, w1, w2, rng)
    if None in (F5, F6, F7):
        print(f"  ({a},{b}): incomplete")
        continue
    r65 = F6 / F5
    r76 = F7 / F6
    rows.append((float(e1), float(e2), F5, F6, F7, r65, r76))
    print(f"{str((a,b)):>10} {float(e1):>5} {float(e2):>5} | {mp.nstr(F5,10):>14} "
          f"{mp.nstr(F6,10):>16} {mp.nstr(F7,12):>18} | {mp.nstr(r65,8):>10} {mp.nstr(r76,8):>10}")

print("\n=== ratio c = F6/F5 vs (e1,e2): is c degree-2 homogeneous? try c = A*e1^2 + B*e2 ===")
# solve A,B from two rows, then check others
if len(rows) >= 2:
    import numpy as np
    Mx = np.array([[r[0] ** 2, r[1]] for r in rows], dtype=float)
    cc = np.array([float(r[5]) for r in rows], dtype=float)
    coef, res, rank, sv = np.linalg.lstsq(Mx, cc, rcond=None)
    print(f"  fit c ≈ {coef[0]:.6f}*e1^2 + {coef[1]:.6f}*e2")
    for r in rows:
        pred = coef[0] * r[0] ** 2 + coef[1] * r[1]
        print(f"    e1={r[0]:.0f} e2={r[1]:.0f}: c={float(r[5]):.5f}  pred={pred:.5f}  diff={float(r[5])-pred:.2e}")
