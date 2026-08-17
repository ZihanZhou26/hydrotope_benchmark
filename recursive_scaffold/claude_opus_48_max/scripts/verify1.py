"""
Stress-test candidate C2 against the EXACT oracle (bg.py):
 (a) g-dependence (g=2 vs g=1, same frequencies),
 (b) many MakeKinematics points n=5,6,7,8 with diverse free freqs; record
     interleaving status (are the two minus legs the global min & max |omega|?),
 (c) hierarchical regimes (one freq much larger / much smaller).
"""
import random
from fractions import Fraction as F
from bg import amp_two_minus, bg_amplitude, make_kinematics, two_minus_sigmas, DegenerateKinematics


def cand_g1(n, w1, w2):
    e2 = w1 * w2
    mu2 = min(w1 * w1, w2 * w2)
    return 2 ** (n - 1) * e2 * mu2 ** (n - 3)


def interleaving(allW):
    """True iff the two minus legs (idx 0,1) are the global min & max of |omega|."""
    mags = [abs(w) for w in allW]
    mmin, mmax = min(mags), max(mags)
    minus_mags = {abs(allW[0]), abs(allW[1])}
    plus_mags = [abs(w) for w in allW[2:]]
    return all(min(abs(allW[0]), abs(allW[1])) <= pm <= max(abs(allW[0]), abs(allW[1])) for pm in plus_mags)


print("=== (a) g-dependence: a_n(g) / a_n(1) at same frequencies ===")
for g in (F(2), F(3), F(1, 2)):
    # use {2,5/2,3} frequencies (g-independent), compute at g
    n = 5
    fw = [F(2), F(5, 2), F(3)]
    A1, allW, _ = amp_two_minus(n, fw, g=1)
    sig = two_minus_sigmas(n)
    allK_g = [sig[i] * allW[i] ** 2 / g for i in range(n)]
    Ag = bg_amplitude(allK_g, allW, g)
    print(f"  g={g}: a_n(g)/a_n(1) = {Ag.im / A1.im}")

print("\n=== (b) MakeKinematics points, diverse free freqs, n=5..8 ===")
rng = random.Random(2024)
for n in (5, 6, 7, 8):
    npass = nfail = 0
    fail_examples = []
    ninter_pass = nnoninter = nnoninter_pass = 0
    trials = 60 if n < 8 else 20
    got = 0
    while got < trials:
        fw = [F(rng.randint(-7, 7) or 1, rng.randint(1, 3)) for _ in range(n - 2)]
        try:
            A, allW, allK = amp_two_minus(n, fw, g=1)
        except (DegenerateKinematics, ZeroDivisionError):
            continue
        if A.re != 0:
            continue
        got += 1
        c = cand_g1(n, allW[0], allW[1])
        ok = (A.im == c)
        inter = interleaving(allW)
        if inter:
            if ok:
                ninter_pass += 1
            else:
                fail_examples.append(("INTER-FAIL", [str(x) for x in allW], str(A.im), str(c)))
        else:
            nnoninter += 1
            if ok:
                nnoninter_pass += 1
        if ok:
            npass += 1
        else:
            nfail += 1
            if len(fail_examples) < 4 and not inter:
                fail_examples.append(("noninter", [str(x) for x in allW], str(A.im), str(c)))
    print(f"  n={n}: pass={npass}/{got}  (interleaving&pass={ninter_pass}, "
          f"non-interleaving={nnoninter} of which pass={nnoninter_pass})")
    for fe in fail_examples[:3]:
        print(f"      {fe[0]}: allW={fe[1]} oracle={fe[2]} cand={fe[3]}")

print("\n=== (c) hierarchical: one plus freq much larger, and much smaller ===")
# n=5: free = (w2_minus, w3_plus, w4_plus). Make w4 huge or tiny.
for fw in [[F(2), F(3), F(50)], [F(2), F(3), F(1, 50)], [F(1, 100), F(2), F(3)], [F(50), F(2), F(3)]]:
    try:
        A, allW, allK = amp_two_minus(5, fw, g=1)
        c = cand_g1(5, allW[0], allW[1])
        inter = interleaving(allW)
        print(f"  fw={[str(x) for x in fw]}: allW={[str(x) for x in allW]} "
              f"inter={inter} oracle={A.im} cand={c} {'OK' if A.im==c else 'DIFF'}")
    except (DegenerateKinematics, ZeroDivisionError) as e:
        print(f"  fw={[str(x) for x in fw]}: degenerate ({e})")
