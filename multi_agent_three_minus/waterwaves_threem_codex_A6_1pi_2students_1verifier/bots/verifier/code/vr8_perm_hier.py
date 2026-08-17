#!/usr/bin/env python3
"""Permutation invariance (minus-leg and plus-leg) + hierarchical regimes."""
from fractions import Fraction as F
from itertools import permutations
import random
import vr8_core as V

random.seed(7)

def test_point(w, tag):
    """Compare BG(--amp, explicit K,W) vs my formula at omega=w (must be on-shell)."""
    K = V.K_of(w)
    a6i = V.bg_amp_explicit(K, w)
    me = V.stripped(list(w))
    return a6i, me, (a6i == me)

# ---- get a batch of genuine on-shell omegas ----
base_points = []
tries = 0
while len(base_points) < 8 and tries < 200:
    tries += 1
    free = [F(random.randint(-9,9), random.choice([1,2,3])) for _ in range(4)]
    if any(x==0 for x in free): continue
    try:
        omega, a6i = V.bg_amp_free(free)
    except Exception:
        continue
    w = list(omega)
    x2=[z*z for z in w]
    if len(set(x2))<6: continue
    base_points.append((w, a6i))

print(f"collected {len(base_points)} on-shell base points\n")

# ---- 1. permutation invariance ----
print("=== permutation invariance within minus {0,1,2} and plus {3,4,5} ===")
perm_fail = 0
perm_checks = 0
formula_noninv = 0
bg_noninv = 0
for w, a6i0 in base_points:
    # verify --amp reproduces the -n result at identity first
    a6i_id, me_id, ok_id = test_point(w, "id")
    if a6i_id != a6i0:
        print("  WARN: --amp != -n at identity", a6i_id, a6i0)
    for pm in permutations(range(3)):
        for pp in permutations(range(3)):
            wp = [w[pm[0]], w[pm[1]], w[pm[2]], w[3+pp[0]], w[3+pp[1]], w[3+pp[2]]]
            a6i, me, ok = test_point(wp, "perm")
            perm_checks += 1
            if a6i != a6i0:
                bg_noninv += 1          # BG amplitude changed under same-sign perm
            if me != a6i:
                perm_fail += 1
            if me != V.stripped(list(w)):
                formula_noninv += 1     # my formula changed under same-sign perm
print(f"  perm checks: {perm_checks}")
print(f"  BG value changed under same-sign permutation (nonzero => not invariant): {bg_noninv}")
print(f"  formula value changed under same-sign permutation: {formula_noninv}")
print(f"  formula != BG (mismatches): {perm_fail}")

# ---- 2. hierarchical regimes ----
print("\n=== hierarchical regimes (one freq >> or << others) ===")
hier_fail = 0
hier_ok = 0
# use free (w2,w3,w4,w5); push one large or small
scales = [F(1,50), F(1,20), 20, 60, 200, F(1,200), 1000]
cases = []
for big in scales:
    cases.append([big, F(2), F(3), F(5)])
    cases.append([F(2), big, F(3), F(5)])
    cases.append([F(3), F(5), big, F(2)])
    cases.append([F(3), F(5), F(2), big])
    cases.append([big, big+1, F(3), F(5)])
for free in cases:
    try:
        omega, a6i = V.bg_amp_free(free)
    except Exception as e:
        continue
    w = list(omega)
    x2=[z*z for z in w]
    if len(set(x2))<6:
        continue
    try:
        me = V.stripped(w)
    except ZeroDivisionError:
        continue
    if me == a6i:
        hier_ok += 1
    else:
        hier_fail += 1
        print("  FAIL free=",free," omega=",omega," diff=",me-a6i)
print(f"  hierarchical ok={hier_ok}  fail={hier_fail}")
