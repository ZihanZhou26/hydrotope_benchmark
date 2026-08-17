"""Probe invariants of a_n = Im(A_n): scaling, permutation symmetry, sign."""
from fractions import Fraction as F
from itertools import permutations
import math
from bg import amp_two_minus, bg_amplitude, two_minus_sigmas, make_kinematics


def a_of(n, freeW, g=1):
    A, allW, allK = amp_two_minus(n, [F(x) for x in freeW], g)
    assert A.re == 0, f"A not purely imaginary: {A}"
    return A.im, allW, allK


print("=== values ===")
pts = {
    5: [[1, 2, 3], [2, F(5, 2), 3], [1, 3, 5], [2, 3, 7]],
    6: [[F(3, 2), 2, F(5, 2), 3], [1, 2, 3, 4], [1, 3, 5, 7]],
    7: [[F(3, 2), 2, F(5, 2), 3, F(7, 2)], [1, 2, 3, 4, 5]],
}
for n in (5, 6, 7):
    for fw in pts[n]:
        a, allW, allK = a_of(n, fw)
        print(f"n={n} freeW={[str(x) for x in fw]} allW={[str(x) for x in allW]} a={a}")

print("\n=== scaling: a_n(lambda*omega)/a_n(omega) ===")
for n in (5, 6, 7):
    fw = pts[n][0]
    a1, _, _ = a_of(n, fw)
    for lam in (2, 3):
        a2, _, _ = a_of(n, [F(lam) * F(x) for x in fw])
        r = F(a2) / F(a1)
        d = math.log(float(r)) / math.log(lam)
        print(f"n={n} lambda={lam}: ratio={r}  ~ lambda^{d:.4f}")

print("\n=== permutation symmetry (full-leg relabeling of allK,allW) ===")
# build a generic on-shell point, then permute legs within sectors and recompute
for n in (5, 6):
    fw = pts[n][0]
    sig = two_minus_sigmas(n)
    allK, allW = make_kinematics(n, [F(x) for x in fw], sig, 1)
    A0 = bg_amplitude(allK, allW, 1)
    base = A0.im
    print(f"n={n} base a={base}")
    # swap the two minus legs (positions 0,1)
    perm = list(range(n)); perm[0], perm[1] = perm[1], perm[0]
    A = bg_amplitude([allK[i] for i in perm], [allW[i] for i in perm], 1)
    print(f"   swap minus legs (1<->2): a={A.im}  {'INVARIANT' if A.im==base else 'CHANGED'}")
    # swap two plus legs (positions 2,3)
    perm = list(range(n)); perm[2], perm[3] = perm[3], perm[2]
    A = bg_amplitude([allK[i] for i in perm], [allW[i] for i in perm], 1)
    print(f"   swap plus legs (3<->4): a={A.im}  {'INVARIANT' if A.im==base else 'CHANGED'}")
    # cyclic shift of all plus legs
    if n >= 5:
        perm = [0, 1] + list(range(3, n)) + [2]
        A = bg_amplitude([allK[i] for i in perm], [allW[i] for i in perm], 1)
        print(f"   cycle plus legs: a={A.im}  {'INVARIANT' if A.im==base else 'CHANGED'}")
