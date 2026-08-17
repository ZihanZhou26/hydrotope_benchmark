"""
Closed-form tree amplitude A_n for 1D deep-water surface gravity waves
in the TWO-MINUS sector  sigma = (-1, -1, +1, +1, ..., +1).

Dispersion:  omega_i^2 = g |k_i|,   k_i = sigma_i omega_i^2 / g.
On-shell / resonant manifold:
        sum_i omega_i = 0 ,     sum_i sigma_i omega_i^2 = 0 .

Result (valid for all n >= 4):

    A_n  =  -i * 2^(n-1) * g^-(n-3) * omega_1 * omega_2
                * SUM_{ S subset of {3,...,n} }
                      (-1)^(|S|+1) * [ ( omega_2^2 - q_S )_+ ]^(n-3)

where  q_S = sum_{j in S} omega_j^2 ,  legs 1,2 are the two sigma=-1 legs,
legs 3..n are the sigma=+1 legs, and (x)_+ = max(x, 0) (truncated power,
so a subset S contributes only when omega_2^2 > q_S).

Equivalently, using the on-shell magnitudes |k_j| = omega_j^2 / g, the g's
cancel inside the bracket and A_n = -i*2^(n-1)*omega_1*omega_2 *
SUM (-1)^(|S|+1) [ ( |k_2| - sum_{j in S}|k_j| )_+ ]^(n-3).  At g = 1
(the convention used throughout the benchmark) the prefactor g^-(n-3) = 1.

This is a PIECEWISE HOMOGENEOUS POLYNOMIAL of degree 2(n-2) in the
frequencies.  The "chambers" are the regions of fixed active set
    A = { S subset of {3..n} : omega_2^2 > q_S } ;
on each chamber A_n is the single homogeneous polynomial obtained by
summing the active terms.

Symmetry / well-definedness:  the amplitude is symmetric under exchanging
the two minus legs (1<->2) and under permuting the plus legs.  Although the
threshold above uses omega_2^2, one may equally use omega_1^2: because there
are n-2 plus legs but the power is only n-3, the full alternating sum
    SUM_{S subset {3..n}} (-1)^|S| (x - q_S)^(n-3) = 0   (identically),
which forces the truncated sums built from omega_1^2 and omega_2^2 to agree
(note omega_1^2 + omega_2^2 = q_{full} on shell).
"""

from itertools import combinations
from fractions import Fraction


def _subsets(items):
    for r in range(len(items) + 1):
        for c in combinations(items, r):
            yield c


def A_two_minus(omegas, g=1):
    """Tree amplitude A_n in the two-minus sector.

    Parameters
    ----------
    omegas : sequence of length n (n >= 4)
        Frequencies (omega_1, omega_2 are the sigma=-1 legs; the rest sigma=+1).
        Exact arithmetic if you pass Fraction / int.
    g : gravitational constant; A_n scales as g^-(n-3).  Pass Fraction for exact.

    Returns
    -------
    (re, im) where A_n = re + i*im.  Here re == 0 and the physical content is im
    (the amplitude is purely imaginary).  We return the pair so the routine is
    exact when fed Fractions.
    """
    n = len(omegas)
    if n < 4:
        raise ValueError("two-minus sector is defined for n >= 4")
    w = list(omegas)
    w1, w2 = w[0], w[1]
    x = w2 * w2
    plus = list(range(2, n))           # 0-based indices of plus legs (legs 3..n)
    m = n - 3
    total = 0
    for S in _subsets(plus):
        qS = sum(w[j] * w[j] for j in S)
        d = x - qS
        if d > 0:                       # truncated power: only active subsets
            sign = -1 if (len(S) % 2 == 0) else 1     # (-1)^(|S|+1)
            total += sign * (d ** m)
    coeff = (2 ** (n - 1)) * w1 * w2 * total
    if g != 1:
        coeff = coeff / (g ** (n - 3))
    # A_n = -i * coeff   ->  real part 0, imaginary part -coeff
    return (0, -coeff)


def imag_part(omegas, g=1):
    """Convenience: Im(A_n) (the amplitude is -i * (real polynomial))."""
    return A_two_minus(omegas, g)[1]


# ---------------------------------------------------------------------------
# self-test against Berends-Giele values computed independently in Mathematica
# (A_n is reported as A/(-i); i.e. -imag_part below).
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    F = Fraction
    cases = [
        # (omegas, A/(-i) expected)   from BGAmplitude
        ([F(-4), F(1), F(2), F(3), F(-2)], F(64)),                 # n=5
        ([F(-13, 2), F(2), F(3), F(5), F(-7, 2)], F(3328)),        # n=5
        ([F(-233, 18), F(2), F(5), F(11), F(-91, 18)], F(59648, 9)),# n=5
        ([F(-32, 5), F(1), F(2), F(3), F(4), F(-18, 5)], F(1024, 5)),     # n=6
        ([F(-184, 17), F(2), F(3), F(5), F(7), F(-105, 17)], F(753664, 17)),# n=6
        ([F(-139, 15), F(1), F(2), F(3), F(4), F(5), F(-86, 15)], F(8896, 15)),# n=7
        ([F(-123, 7), F(2), F(3), F(5), F(7), F(11), F(-73, 7)], F(4030464, 7)),# n=7
        ([F(-3), F(1), F(3), F(-1)], F(24)),                       # n=4 (limit)
    ]
    ok = True
    for w, expect in cases:
        got = -imag_part(w)            # A/(-i) = -Im(A)
        status = "OK " if got == expect else "FAIL"
        if got != expect:
            ok = False
        print(f"{status} n={len(w):d}  A/(-i) = {str(got):>14s}   expected {str(expect)}")
    print("ALL PASS" if ok else "SOME FAILED")
