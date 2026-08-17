"""Fast domain + g test (run with python3 -u). Exact for n<=7, float for n=8."""
import sys, random
from fractions import Fraction as F
from bg import amp_two_minus, bg_amplitude, make_kinematics, two_minus_sigmas, DegenerateKinematics


def cand_g1(n, w1, w2):
    return 2 ** (n - 1) * (w1 * w2) * min(w1 * w1, w2 * w2) ** (n - 3)


def interleaving(allW):
    lo = min(abs(allW[0]), abs(allW[1]))
    hi = max(abs(allW[0]), abs(allW[1]))
    return all(lo <= abs(w) <= hi for w in allW[2:])


print("=== (a) g-dependence: a_n(g)/a_n(1), same frequencies ===", flush=True)
n = 5
fw = [F(2), F(5, 2), F(3)]
A1, allW, _ = amp_two_minus(n, fw, g=1)
sig = two_minus_sigmas(n)
for g in (F(2), F(3), F(1, 2)):
    allK_g = [sig[i] * allW[i] ** 2 / g for i in range(n)]
    Ag = bg_amplitude(allK_g, allW, g)
    print(f"  g={g}: ratio a_n(g)/a_n(1) = {Ag.im / A1.im}", flush=True)

print("\n=== (b) MakeKinematics points (exact), diverse free freqs ===", flush=True)
rng = random.Random(2024)
for n in (5, 6, 7):
    npass = 0
    n_inter = n_inter_pass = n_noninter = n_noninter_pass = 0
    got = 0
    examples = []
    while got < 40:
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
            n_inter += 1
            n_inter_pass += ok
            if not ok and len(examples) < 2:
                examples.append(("INTER-FAIL!", allW, A.im, c))
        else:
            n_noninter += 1
            n_noninter_pass += ok
            if not ok and len([e for e in examples if e[0] == 'noninter']) < 2:
                examples.append(("noninter", allW, A.im, c))
        npass += ok
    print(f"  n={n}: total pass={npass}/40 | interleaving {n_inter_pass}/{n_inter} | "
          f"non-interleaving {n_noninter_pass}/{n_noninter}", flush=True)
    for tag, allW, oim, c in examples:
        print(f"      {tag}: allW={[str(x) for x in allW]} oracle={oim} cand={c}", flush=True)

print("\n=== (c) hierarchical regimes (exact n=5) ===", flush=True)
for fw in [[F(2), F(3), F(50)], [F(2), F(3), F(1, 50)], [F(1, 100), F(2), F(3)],
           [F(50), F(2), F(3)], [F(2), F(5, 2), F(3)]]:
    try:
        A, allW, allK = amp_two_minus(5, fw, g=1)
        c = cand_g1(5, allW[0], allW[1])
        print(f"  fw={[str(x) for x in fw]}: allW={[str(x) for x in allW]} "
              f"inter={interleaving(allW)} oracle={A.im} cand={c} {'OK' if A.im==c else 'DIFF'}", flush=True)
    except (DegenerateKinematics, ZeroDivisionError) as e:
        print(f"  fw={[str(x) for x in fw]}: degenerate", flush=True)
print("DONE", flush=True)
