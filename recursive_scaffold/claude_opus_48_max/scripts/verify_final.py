"""
Comprehensive final verification of
    A_n = i * 2^(n-1) * w1*w2 * (min(w1^2,w2^2)/g)^(n-3)
(w1,w2 = the two minus legs = allW[0],allW[1]).
Exact for n<=7 (any g), float for n=8. Also characterizes the input domain.
"""
import sys, random
from fractions import Fraction as F
from bg import bg_amplitude, make_kinematics, two_minus_sigmas, DegenerateKinematics
import mpmath as mp
import bg_float
mp.mp.dps = 40


def cand(n, w1, w2, g):
    return 2 ** (n - 1) * (w1 * w2) * (min(w1 * w1, w2 * w2) / g) ** (n - 3)


def interleaving(allW):
    lo = min(abs(allW[0]), abs(allW[1]))
    hi = max(abs(allW[0]), abs(allW[1]))
    return all(lo <= abs(w) <= hi for w in allW[2:])


def oracle_exact(n, fw, g):
    sig = two_minus_sigmas(n)
    allK, allW = make_kinematics(n, [F(x) for x in fw], sig, g)
    A = bg_amplitude(allK, allW, g)
    return A, allW


print("=== (1) EXACT verification at g in {1,2,3,1/2}, n=5,6,7, interleaving points ===", flush=True)
# positive sorted-ish free freqs tend to be interleaving
pts = {
    5: [[1, 2, 3], [2, F(5, 2), 3], [3, 4, 5], [F(1, 2), 3, 4], [1, 5, 6]],
    6: [[F(3, 2), 2, F(5, 2), 3], [1, 2, 3, 4], [2, 3, 4, 5], [F(1, 3), 3, 4, 5]],
    7: [[F(3, 2), 2, F(5, 2), 3, F(7, 2)], [1, 2, 3, 4, 5], [2, 3, 4, 5, 6]],
}
total = npass = nskip = 0
for n in (5, 6, 7):
    for fw in pts[n]:
        for g in (F(1), F(2), F(3), F(1, 2)):
            try:
                A, allW = oracle_exact(n, fw, g)
            except (DegenerateKinematics, ZeroDivisionError):
                nskip += 1
                continue
            if not interleaving(allW):
                continue
            c = cand(n, allW[0], allW[1], g)
            ok = (A.re == 0 and A.im == c)
            total += 1
            npass += ok
            if not ok:
                print(f"  FAIL n={n} fw={[str(x) for x in fw]} g={g}: oracle={A.re}+{A.im}i cand={c}", flush=True)
print(f"  exact interleaving tests: {npass}/{total} PASS  (skipped {nskip} degenerate)", flush=True)

print("\n=== (2) n=4 limit value (formula) ===", flush=True)
for (w1, w2) in [(F(-4), F(1)), (F(-3), F(2)), (F(-7), F(3))]:
    for g in (F(1), F(2)):
        print(f"  minus=({w1},{w2}) g={g}: a_4 = {cand(4, w1, w2, g)}  (eps-limit confirmed in verify_n4.py at g=1)", flush=True)

print("\n=== (3) input-domain: do ALL-POSITIVE free freqs give interleaving? ===", flush=True)
rng = random.Random(77)
for n in (5, 6, 7):
    ninter = npos = 0
    pass_inter = 0
    got = 0
    while got < 60:
        fw = [F(rng.randint(1, 9), rng.randint(1, 3)) for _ in range(n - 2)]  # all positive
        try:
            A, allW = oracle_exact(n, fw, F(1))
        except (DegenerateKinematics, ZeroDivisionError):
            continue
        if A.re != 0:
            continue
        got += 1
        npos += 1
        inter = interleaving(allW)
        ninter += inter
        if inter:
            pass_inter += (A.im == cand(n, allW[0], allW[1], F(1)))
    print(f"  n={n}: of {npos} all-positive-free-freq points, interleaving={ninter}; "
          f"formula passes {pass_inter}/{ninter} interleaving", flush=True)

print("\n=== (4) n=8 via float (g=1), interleaving points ===", flush=True)
def flat_cfg_float(n, w1, w2, free):
    A = -(w1 + w2); B = w1 ** 2 + w2 ** 2
    s = A - sum(free); q = B - sum(v * v for v in free)
    disc = 2 * q - s ** 2
    if disc < 0:
        return None
    r = mp.sqrt(disc)
    return [w1, w2] + list(free) + [(s + r) / 2, (s - r) / 2]

rng2 = random.Random(5)
n = 8
done = 0
attempts = 0
while done < 4 and attempts < 6000:
    attempts += 1
    w1, w2 = mp.mpf(-6), mp.mpf(2)
    m, M = 2, 6
    free = [mp.mpf(rng2.uniform(-5.8, 5.8)) for _ in range(n - 4)]
    if any(not (m < abs(v) < M) for v in free):
        continue
    cfg = flat_cfg_float(n, w1, w2, free)
    if cfg is None:
        continue
    x, y = cfg[-2], cfg[-1]
    if not (m < abs(x) < M and m < abs(y) < M):
        continue
    try:
        A = bg_float.amp_from_allW(cfg, [-1, -1] + [1] * (n - 2))
    except Exception:
        continue
    if abs(A.real) > mp.mpf('1e-20'):
        continue
    cc = 2 ** (n - 1) * (w1 * w2) * (min(w1 * w1, w2 * w2) / 1) ** (n - 3)
    relerr = abs(A.imag - cc) / abs(cc)
    print(f"  n=8 minus=(-6,2): oracle={mp.nstr(A.imag,18)} cand={mp.nstr(cc,18)} relerr={mp.nstr(relerr,3)}", flush=True)
    done += 1

print("\n=== (5) required regimes (in-domain), exact n=5,6 ===", flush=True)
regimes = [
    (5, [F(2), F(3), F(50)], "one plus freq much larger"),
    (5, [F(1, 100), F(2), F(3)], "free minus freq much smaller"),
    (6, [F(1, 50), F(2), F(3), F(4)], "free minus freq much smaller"),
    (6, [F(2), F(3), F(4), F(99)], "one plus freq much larger"),
]
for n, fw, desc in regimes:
    A, allW = oracle_exact(n, fw, F(1))
    c = cand(n, allW[0], allW[1], F(1))
    print(f"  n={n} [{desc}] fw={[str(x) for x in fw]}: inter={interleaving(allW)} "
          f"oracle={A.im} cand={c} {'OK' if A.im==c else 'DIFF'}", flush=True)
print("DONE", flush=True)
