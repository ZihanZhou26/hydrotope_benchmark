#!/usr/bin/env python3
"""
Closed-form tree amplitude A_n in the TWO-MINUS sector of 1D deep-water
surface waves, sigma = (-1,-1,+1,...,+1), g = 1.

    A_n = i * 2^(n-1) * w1*w2 * sum_{S subset Plus} (-1)^|S| (a - sigma_S)_+^(n-3)

where legs 1,2 are the minus-legs, Plus = {w3^2,...,wn^2},
a = min(w1^2, w2^2), sigma_S = sum_{i in S} wi^2, (x)_+ = max(x, 0).

Exact rational arithmetic via fractions.Fraction.  Runs with stdlib only.
"""
from fractions import Fraction
from itertools import combinations


def A_two_minus(omegas):
    """A_n / i  is returned as an exact (real) Fraction; the amplitude is i * that.

    `omegas` : sequence of the n signed frequencies with the two minus-legs FIRST.
               Use Fraction inputs for exact results.
    Returns the Fraction c such that A_n = i * c  (A_n is purely imaginary).
    """
    omegas = [Fraction(x) for x in omegas]
    n = len(omegas)
    m = [w * w for w in omegas]
    a = min(m[0], m[1])
    plus = m[2:]
    d = n - 3
    total = Fraction(0)
    for k in range(len(plus) + 1):
        for S in combinations(plus, k):
            x = a - sum(S, Fraction(0))
            if x > 0:
                total += ((-1) ** k) * (x ** d)
    return (2 ** (n - 1)) * omegas[0] * omegas[1] * total


if __name__ == "__main__":
    # The three original OnShellBG.m test points (two-minus sector).
    # MakeKinematics solves w1, wn from the n-2 free frequencies.
    def make_kinematics(n, freeW):
        freeW = [Fraction(x) for x in freeW]
        sigmas = [-1, -1] + [1] * (n - 2)          # two-minus sector
        sumFree = sum(freeW)
        sumSigmaW2 = sum(s * w * w for s, w in zip(sigmas[1:n-1], freeW))
        wn = -(sigmas[0] * sumFree**2 + sumSigmaW2) / (2 * sigmas[0] * sumFree)
        w1 = -(sumFree + wn)
        return [w1] + freeW + [wn]

    cases = [
        (5, [2, Fraction(5, 2), 3],            Fraction(-2304)),
        (6, [2, Fraction(5, 2), 3, Fraction(7, 2)], Fraction(-295936, 11)),
        (7, [2, Fraction(5, 2), 3, Fraction(7, 2), 4], Fraction(-4333568, 15)),
    ]
    print("n  formula (A_n/i)        expected (BG, A_n/i)     match")
    for n, fw, expected in cases:
        ws = make_kinematics(n, fw)
        c = A_two_minus(ws)
        print(f"{n}  {str(c):22s} {str(expected):22s} {c == expected}")
