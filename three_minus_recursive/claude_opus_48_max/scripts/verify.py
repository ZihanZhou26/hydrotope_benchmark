"""verify.py — exact + double verification of a candidate B-formula vs the oracle.

A candidate is a function f(n, omega_list_Fraction, g) -> Fraction (=B=A/i).
"""
import random, itertools
from fractions import Fraction as Fr
import harness


def three_minus_sigma(n):
    return [-1, -1, -1] + [1] * (n - 3)


def check_point(n, free_w, cand, g=1, exact=True):
    sigma = three_minus_sigma(n)
    r = harness.onshell(n, free_w, sigma, g=g, double=not exact)
    om = r["omega"]
    if exact:
        Bor = r["A_im"]
        Bf = cand(n, [Fr(x) for x in om], g)
        return ("exact", om, Bor, Bf, Bf == Bor)
    else:
        Bor = r["A_im"]
        Bf = float(cand(n, [Fr(x) for x in om], g))
        rel = abs(Bf - Bor) / max(1e-30, abs(Bor))
        return ("double", om, Bor, Bf, rel <= 1e-10)


def rand_free(n, rng, kind="generic"):
    if kind == "generic":
        return [Fr(rng.randint(1, 40), rng.randint(1, 7)) for _ in range(n - 2)]
    if kind == "biglast":   # one plus freq huge
        f = [Fr(rng.randint(1, 6), rng.randint(1, 4)) for _ in range(n - 3)]
        return f + [Fr(rng.randint(200, 400))]
    if kind == "smalllast":  # one plus freq tiny
        f = [Fr(rng.randint(2, 8)) for _ in range(n - 3)]
        return f + [Fr(1, rng.randint(50, 200))]
    if kind == "bigminus":   # one free minus freq huge
        return [Fr(rng.randint(200, 400))] + [Fr(rng.randint(1, 6)) for _ in range(n - 3)]


def batch(n, cand, ntest=200, seed=7, exact=True, kinds=("generic",)):
    rng = random.Random(seed)
    npass = nfail = nerr = 0
    fails = []
    for _ in range(ntest):
        kind = rng.choice(kinds)
        fw = rand_free(n, rng, kind)
        try:
            mode, om, Bor, Bf, ok = check_point(n, fw, cand, exact=exact)
        except Exception as e:
            nerr += 1
            continue
        if ok:
            npass += 1
        else:
            nfail += 1
            if len(fails) < 10:
                fails.append((kind, [str(x) for x in fw], [str(x) for x in om],
                              str(Bor), str(Bf)))
    return npass, nfail, nerr, fails


if __name__ == "__main__":
    import sys, formulas
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    cand = lambda n, om, g: formulas.three_minus_n5_twoplus_B(om, g)
    for kinds in [("generic",), ("biglast",), ("smalllast",), ("bigminus",)]:
        npass, nfail, nerr, fails = batch(n, cand, ntest=120, kinds=kinds)
        print(f"n={n} {kinds[0]:10s}: pass={npass} fail={nfail} err(wall)={nerr}")
        for f in fails[:5]:
            print("   FAIL", f)
