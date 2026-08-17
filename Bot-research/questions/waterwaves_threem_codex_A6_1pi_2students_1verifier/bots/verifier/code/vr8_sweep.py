#!/usr/bin/env python3
"""Broad random multi-chamber exact sweep + chamber coverage census."""
from fractions import Fraction as F
from itertools import combinations
import random, sys
import vr8_core as V

random.seed(20260726)

def chamber_sig(w):
    x2 = [z*z for z in w]
    qs = []
    for m in V.MINUS:
        for p in V.PLUS:
            qs.append(1 if x2[p]-x2[m] > 0 else 0)
    Qs = []
    for m in V.MINUS:
        for p, q in combinations(V.PLUS, 2):
            Qs.append(1 if x2[p]+x2[q]-x2[m] > 0 else 0)
    return (tuple(qs), tuple(Qs))

def rand_free():
    # mix of integers and rationals, varied scales
    def r():
        num = random.randint(-9, 9)
        den = random.choice([1,1,1,2,3,5])
        while num == 0:
            num = random.randint(-9, 9)
        return F(num, den)
    return [r() for _ in range(4)]

n_ok = 0
n_fail = 0
fails = []
chambers = {}
worst = None
N = int(sys.argv[1]) if len(sys.argv) > 1 else 400
for i in range(N):
    free = rand_free()
    try:
        omega, a6i = V.bg_amp_free(free)
    except Exception:
        continue
    w = list(omega)
    # skip degenerate (equal magnitudes -> on a wall) just in case
    x2 = [z*z for z in w]
    bad = False
    for a in range(6):
        for b in range(a+1,6):
            if x2[a]==x2[b]:
                bad = True
    if bad:
        continue
    try:
        me = V.stripped(w)
    except ZeroDivisionError:
        continue
    sig = chamber_sig(w)
    chambers.setdefault(sig, 0)
    chambers[sig] += 1
    if me == a6i:
        n_ok += 1
    else:
        n_fail += 1
        fails.append((free, omega, a6i, me))

print(f"samples ok(exact match)={n_ok}  fail={n_fail}")
print(f"distinct chamber signatures visited: {len(chambers)}")
# report q-signature multiplicity and Q-signature multiplicity separately
qset = set(k[0] for k in chambers)
Qset = set(k[1] for k in chambers)
print(f"  distinct q-wall sign patterns: {len(qset)}")
print(f"  distinct Q-wall sign patterns: {len(Qset)}")
if fails:
    print("\n=== FAILURES ===")
    for free, omega, a6i, me in fails[:20]:
        print("free:", free)
        print("  omega:", omega)
        print("  BG A6/i:", a6i)
        print("  mine   :", me)
        print("  diff   :", me - a6i)
else:
    print("\nNo mismatches across the whole sweep.")
