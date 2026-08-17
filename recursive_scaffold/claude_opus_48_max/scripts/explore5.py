"""
Probe a non-interleaving region for a possible general formula.
n=6, region: minus=(-8,2) (|w1|=8>|w2|=2), ONE soft plus leg s (|s|<2), three
plus legs interleaving (|w| in (2,8)). Given (minus,s) the 3 legs have 1 free
param t. Test: does a_6 depend only on (minus,s) in this region? Then map G(s).
"""
import mpmath as mp
import bg_float
mp.mp.dps = 40
w1, w2 = mp.mpf(-8), mp.mpf(2)
m, M = mp.mpf(2), mp.mpf(8)
sig6 = [-1, -1, 1, 1, 1, 1]
A_ = -(w1 + w2)   # = 6
B_ = w1 ** 2 + w2 ** 2  # = 68


def three_legs(s, t):
    """legs: s (soft), t (free interleaving), and two solved."""
    S = A_ - s - t
    Q = B_ - s ** 2 - t ** 2
    disc = 2 * Q - S ** 2
    if disc < 0:
        return None
    r = mp.sqrt(disc)
    return t, (S + r) / 2, (S - r) / 2


def a6(s, t):
    pc = three_legs(s, t)
    if pc is None:
        return None
    p1, p2, p3 = pc
    # interleaving check on the three
    if not all(m < abs(v) < M for v in (p1, p2, p3)):
        return None
    allW = [w1, w2, s, p1, p2, p3]
    try:
        A = bg_float.amp_from_allW(allW, sig6)
    except Exception:
        return None
    if abs(A.real) > mp.mpf('1e-18'):
        return None
    return A.imag


print("=== n=6 one-soft-leg region: is a_6 independent of t (the free interleaving leg)? ===", flush=True)
for s in [mp.mpf('1.5'), mp.mpf('1.0'), mp.mpf('0.5'), mp.mpf('-1.0')]:
    vals = []
    for t in [mp.mpf(x) for x in ('3.0', '3.5', '4.0', '4.5', '5.0', '5.5')]:
        v = a6(s, t)
        if v is not None:
            vals.append((t, v))
    if len(vals) >= 2:
        spread = max(v for _, v in vals) - min(v for _, v in vals)
        print(f"  s={mp.nstr(s,4)}: {len(vals)} configs, a_6={mp.nstr(vals[0][1],12)}, "
              f"spread={mp.nstr(spread,4)} => {'(minus,s)-ONLY' if abs(spread)<mp.mpf('1e-20') else 'depends on t too'}", flush=True)
    else:
        print(f"  s={mp.nstr(s,4)}: too few configs", flush=True)

print("\n=== map G(s) = a_6 in this region, compare to interleaving value (s->2) ===", flush=True)
# interleaving value at minus=(-8,2): 2^5 * w1*w2 * min(64,4)^3 = 32*(-16)*64 = -32768
print(f"  interleaving value (all plus in (2,8)) = {32*(-16)*64}", flush=True)
for s in [mp.mpf(x) for x in ('1.9', '1.5', '1.0', '0.5', '0.25', '-0.5', '-1.0', '-1.5')]:
    v = a6(s, mp.mpf('4.0'))
    if v is None:
        v = a6(s, mp.mpf('3.5'))
    if v is None:
        v = a6(s, mp.mpf('4.5'))
    print(f"  s={mp.nstr(s,5):>7}: a_6={mp.nstr(v,12) if v is not None else 'NA'}", flush=True)
