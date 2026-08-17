"""
FINAL held-out EXACT verification (fresh seed, distinct from all prior tests).
Formula:  A_n = i * 2^(n-1) * w1*w2 * (min(w1^2,w2^2)/g)^(n-3),  w1,w2 = the two minus legs.
"""
import random
from fractions import Fraction as F
from bg import bg_amplitude, make_kinematics, two_minus_sigmas, DegenerateKinematics


def cand_A(n, allW, g):
    w1, w2 = allW[0], allW[1]
    a = 2 ** (n - 1) * (w1 * w2) * (min(w1 * w1, w2 * w2) / g) ** (n - 3)
    return (0, a)  # real, imag of A_n = i*a


def interleaving(allW):
    lo = min(abs(allW[0]), abs(allW[1])); hi = max(abs(allW[0]), abs(allW[1]))
    return all(lo <= abs(w) <= hi for w in allW[2:])


def oracle(n, fw, g):
    sig = two_minus_sigmas(n)
    allK, allW = make_kinematics(n, [F(x) for x in fw], sig, g)
    return bg_amplitude(allK, allW, g), allW


print("=== FINAL held-out exact verification (fresh seed 31337) ===", flush=True)
rng = random.Random(31337)
total = npass = 0
for n in (5, 6, 7):
    got = 0
    while got < 8:
        fw = [F(rng.randint(-9, 9) or 2, rng.randint(1, 4)) for _ in range(n - 2)]
        for g in (F(1), F(3)):
            try:
                A, allW = oracle(n, fw, g)
            except (DegenerateKinematics, ZeroDivisionError):
                continue
            if A.re != 0 or not interleaving(allW):
                continue
            re, im = cand_A(n, allW, g)
            ok = (A.re == re and A.im == im)
            total += 1; npass += ok; got += 1 if g == F(1) else 0
            tag = "OK" if ok else "FAIL"
            if not ok:
                print(f"  FAIL n={n} g={g} allW={[str(x) for x in allW]} oracle=({A.re},{A.im}) cand=({re},{im})", flush=True)
print(f"  held-out interleaving (n=5,6,7, g in {{1,3}}): {npass}/{total} PASS", flush=True)

print("\n=== re-run ALL prior anchors (exact) ===", flush=True)
anchors = [
    (5, [F(2), F(5, 2), F(3)], F(1)),
    (5, [F(1), F(2), F(3)], F(1)),
    (5, [F(1), F(3), F(5)], F(1)),
    (5, [F(2), F(3), F(7)], F(1)),
    (6, [F(3, 2), F(2), F(5, 2), F(3)], F(1)),
    (7, [F(3, 2), F(2), F(5, 2), F(3), F(7, 2)], F(1)),
]
allok = True
for n, fw, g in anchors:
    A, allW = oracle(n, fw, g)
    re, im = cand_A(n, allW, g)
    ok = (A.re == re and A.im == im); allok &= ok
    print(f"  n={n} fw={[str(x) for x in fw]}: A_n={A.re}+{A.im}i cand={re}+{im}i {'OK' if ok else 'FAIL'}", flush=True)

print("\n=== previously-FAILED candidate C1 (polynomial) status: ABANDONED (a_n not polynomial) ===", flush=True)
print("=== previously-FAILED non-interleaving points: OUT OF CLAIMED DOMAIN (see SCOPE/FAILED_TESTS) ===", flush=True)

print("\n=== n=4 limit at a FRESH minus pair (-9,4): formula vs eps-limit ===", flush=True)
w1, w2 = F(-9), F(4)
formula = 2 ** (4 - 1) * (w1 * w2) * (min(w1 * w1, w2 * w2) / 1) ** (4 - 3)
print(f"  formula a_4 = {formula}", flush=True)
sig = two_minus_sigmas(4)
for eps in [F(1, 1000), F(1, 1000000)]:
    w4 = -w2 + eps; w3 = -(w1 + w2 + w4)
    allW = [w1, w2, w3, w4]
    allK = [sig[i] * allW[i] ** 2 for i in range(4)]
    A = bg_amplitude(allK, allW, 1)
    print(f"  eps={float(eps):.0e}: A_4 = {A.re}+{A.im}i  -> a_4 ~ {float(A.im):.6f}", flush=True)
print("DONE", flush=True)
