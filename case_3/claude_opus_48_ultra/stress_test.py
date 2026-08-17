"""
Randomised stress test (independent Python BG, exact rational).
Goal: confirm that the predicate  |w2| = min_i |w_i|  EXACTLY characterises
the chamber where  A_n = 2^(n-1) i w1 w2^(2n-5) / g^(n-3)  holds.
"""
from fractions import Fraction as F
import random
from waterwave_bg import (BGAmplitude, make_kinematics, two_minus_sigma,
                          closed_form)

random.seed(20260621)

def rand_frac(allow_neg):
    num = random.randint(1, 40)
    den = random.randint(1, 12)
    f = F(num, den)
    if allow_neg and random.random() < 0.35:
        f = -f
    return f

def w2_is_min(ws):
    return ws[1] ** 2 == min(w ** 2 for w in ws)

print(f"{'n':>2} {'free freqs':<34} {'|w2|=min?':>9} {'formula==BG?':>12}  consistent?")
print("-" * 78)
agree_all = True
n_principal = 0
n_total = 0
for n in (5, 6):
    for trial in range(40):
        allow_neg = (trial % 3 == 0)
        freeW = [rand_frac(allow_neg) for _ in range(n - 2)]
        if sum(freeW) == 0:
            continue
        try:
            ks, ws = make_kinematics(n, freeW, two_minus_sigma(n), 1)
        except Exception:
            continue
        if any(w == 0 for w in ws):
            continue
        try:
            bg = BGAmplitude(ks, ws, 1)          # skip degenerate (|k_S|=0) points
        except ZeroDivisionError:
            continue
        cf = closed_form(n, ws, 1)
        match = (bg == cf)
        principal = w2_is_min(ws)
        consistent = (match == principal)
        agree_all = agree_all and consistent
        n_total += 1
        n_principal += principal
        flag = "" if consistent else "   <<< INCONSISTENT"
        print(f"{n:>2} {str([str(x) for x in freeW]):<34} {str(principal):>9} "
              f"{str(match):>12}  {consistent}{flag}")

print("-" * 78)
print(f"Total points: {n_total},  principal-chamber points: {n_principal}")
print(f"Predicate (|w2|=min)  <=>  (formula matches BG)  holds for ALL points: {agree_all}")
