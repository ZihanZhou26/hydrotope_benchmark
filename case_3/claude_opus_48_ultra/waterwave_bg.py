"""
waterwave_bg.py
===============
Independent, from-scratch reimplementation (exact rational arithmetic) of the
Berends-Giele recursion for 1D deep-water surface-wave tree amplitudes, ported
directly from OnShellBG.m.  Used to CROSS-CHECK, with no reliance on Mathematica,
the closed-form two-minus-sector amplitude

        A_n  =  2^(n-1) * i * w1 * w2^(2n-5) / g^(n-3)

valid in the principal kinematic chamber (the free minus leg w2 has the smallest
magnitude of all legs -- true for every sorted-positive-frequency configuration).

w1, w2 are the two sigma = -1 ("minus") legs; legs 3..n have sigma = +1.

Author: independent verification for waterhedron_benchmark_blind/case_3.
"""

from fractions import Fraction as F
from math import factorial
from functools import lru_cache
from itertools import permutations


# --------------------------------------------------------------------------
#  Gaussian rationals  z = a + b i,  a,b in Q   (exact complex arithmetic)
# --------------------------------------------------------------------------
class GR:
    __slots__ = ("re", "im")

    def __init__(self, re=0, im=0):
        self.re = F(re)
        self.im = F(im)

    def __add__(s, o):
        o = s._c(o); return GR(s.re + o.re, s.im + o.im)
    __radd__ = __add__

    def __sub__(s, o):
        o = s._c(o); return GR(s.re - o.re, s.im - o.im)

    def __rsub__(s, o):
        o = s._c(o); return GR(o.re - s.re, o.im - s.im)

    def __neg__(s):
        return GR(-s.re, -s.im)

    def __mul__(s, o):
        o = s._c(o)
        return GR(s.re * o.re - s.im * o.im, s.re * o.im + s.im * o.re)
    __rmul__ = __mul__

    def __truediv__(s, o):
        o = s._c(o)
        d = o.re * o.re + o.im * o.im
        return GR((s.re * o.re + s.im * o.im) / d, (s.im * o.re - s.re * o.im) / d)

    def __rtruediv__(s, o):
        return s._c(o).__truediv__(s)

    @staticmethod
    def _c(o):
        return o if isinstance(o, GR) else GR(o, 0)

    def __eq__(s, o):
        o = s._c(o); return s.re == o.re and s.im == o.im

    def __repr__(s):
        return f"({s.re} + {s.im} i)"


I = GR(0, 1)


def mag(k):
    """|k| for a real (rational) momentum."""
    return -k if k < 0 else k


# --------------------------------------------------------------------------
#  I. interaction kernels  (exact, real-rational valued)
# --------------------------------------------------------------------------
def EKernel(n, ps):
    if n == 3:
        return F(-1, 2) * (mag(ps[0]) * mag(ps[1]) + ps[0] * ps[1])
    p1, p2, rest = ps[0], ps[1], ps[2:]
    qp2 = mag(p2)
    srest = sum(rest)
    result = qp2 ** (n - 3) * EKernel(3, [p1, p2, srest]) / F(factorial(n - 2))
    for m in range(1, n - 2):                       # m = 1 .. n-3
        head = [p1, p2 + sum(rest[0:m])] + rest[m:]
        result -= qp2 ** m / F(factorial(m)) * EKernel(n - m, head)
    return result


def FKernel(n, ps):
    if n == 3:
        return F(-1) - ps[0] * ps[1] / (mag(ps[0]) * mag(ps[1]))
    p1, p2, rest = ps[0], ps[1], ps[2:]
    qp1, qp2 = mag(p1), mag(p2)
    result = 2 * EKernel(n, ps) / qp1
    for m in range(1, n - 2):                       # m = 1 .. n-3
        sigM = p2 + sum(rest[0:m])
        e = EKernel(m + 2, [-sigM, p2] + rest[0:m])
        f = FKernel(n - m, [p1, sigM] + rest[m:])
        result -= 2 * e * f
    return result / qp2


# --------------------------------------------------------------------------
#  II. vertex and propagator
# --------------------------------------------------------------------------
def Vertex(n, moms, omegas):
    acc = F(0)
    for p in permutations(range(n)):
        acc += omegas[p[0]] * omegas[p[1]] * FKernel(n, [moms[i] for i in p])
    return GR(0, F(-1, 2)) * acc          # (-i/2) * acc


def Propagator(w, k, g):
    return GR(0, -1) / (w * w / mag(k) - g)   # -i / (w^2/|k| - g)


# --------------------------------------------------------------------------
#  III. set partitions of a list into exactly m non-empty blocks
# --------------------------------------------------------------------------
def set_partitions_k(elts, m):
    elts = list(elts)
    n = len(elts)
    if m == 1:
        yield [tuple(elts)]; return
    if m == n:
        yield [(e,) for e in elts]; return
    if m > n or m <= 0:
        return
    first, rest = elts[0], elts[1:]
    # first in its own new block -> partition rest into m-1 blocks
    for sub in set_partitions_k(rest, m - 1):
        yield [(first,)] + sub
    # first added to one of the m existing blocks
    for sub in set_partitions_k(rest, m):
        for i in range(len(sub)):
            yield sub[:i] + [(first,) + sub[i]] + sub[i + 1:]


# --------------------------------------------------------------------------
#  IV. Berends-Giele recursion
# --------------------------------------------------------------------------
def BGAmplitude(momenta, omegas, g):
    momenta = [F(x) for x in momenta]
    omegas = [F(x) for x in omegas]
    g = F(g)
    n = len(momenta)

    @lru_cache(maxsize=None)
    def BGCurrent(S):                      # S: sorted tuple of 0-indexed legs
        if len(S) == 1:
            return GR(1, 0)
        wS = sum(omegas[i] for i in S)
        kS = sum(momenta[i] for i in S)
        result = GR(0, 0)
        for m in range(2, len(S) + 1):
            for part in set_partitions_k(S, m):
                sMoms = [sum(momenta[j] for j in blk) for blk in part]
                sOme = [sum(omegas[j] for j in blk) for blk in part]
                vMoms = [-kS] + sMoms
                vOme = [-wS] + sOme
                term = Vertex(m + 1, vMoms, vOme)
                for blk in part:
                    term = term * BGCurrent(tuple(sorted(blk)))
                result = result + term
        return result * Propagator(wS, kS, g)

    rest = tuple(range(1, n))              # legs 2..n  (0-indexed 1..n-1)
    result = GR(0, 0)
    for m in range(2, n):                  # m = 2 .. n-1
        for part in set_partitions_k(rest, m):
            sMoms = [sum(momenta[j] for j in blk) for blk in part]
            sOme = [sum(omegas[j] for j in blk) for blk in part]
            vMoms = [momenta[0]] + sMoms
            vOme = [omegas[0]] + sOme
            term = Vertex(m + 1, vMoms, vOme)
            for blk in part:
                term = term * BGCurrent(tuple(sorted(blk)))
            result = result + term
    return result


# --------------------------------------------------------------------------
#  V. kinematic solver  (two-minus sector)  &  the closed form
# --------------------------------------------------------------------------
def make_kinematics(n, freeW, sigmas, g):
    """Solve energy+momentum conservation for {w1, wn}; sigma_1+sigma_n=0."""
    freeW = [F(x) for x in freeW]
    assert len(freeW) == n - 2
    assert sigmas[0] + sigmas[-1] == 0
    sumFree = sum(freeW)
    sigmaFree = sigmas[1:n - 1]
    sumSigmaW2 = sum(s * w * w for s, w in zip(sigmaFree, freeW))
    wn = -(sigmas[0] * sumFree ** 2 + sumSigmaW2) / (2 * sigmas[0] * sumFree)
    w1 = -(sumFree + wn)
    allW = [w1] + freeW + [wn]
    allK = [s * w * w / F(g) for s, w in zip(sigmas, allW)]
    return allK, allW


def two_minus_sigma(n):
    return [-1, -1] + [1] * (n - 2)


def closed_form(n, w, g):
    """A_n = 2^(n-1) i w1 w2^(2n-5) / g^(n-3)   (principal chamber)."""
    return GR(0, 1) * (2 ** (n - 1)) * F(w[0]) * F(w[1]) ** (2 * n - 5) / F(g) ** (n - 3)


if __name__ == "__main__":
    g = 1
    print("Independent Python BG  vs  closed form   (exact rational arithmetic)\n")
    cases = [
        (5, [F(3, 2), 2, F(5, 2)]),
        (5, [2, 3, 7]),
        (5, [1, 10, 100]),
        (5, [F(1, 1000), 1, 1]),
        (6, [F(3, 2), 2, F(5, 2), 3]),
        (6, [1, 3, 5, 7]),
        (7, [F(3, 2), 2, F(5, 2), 3, F(7, 2)]),
        (7, [1, 2, 3, 4, 5]),
    ]
    for n, freeW in cases:
        ks, ws = make_kinematics(n, freeW, two_minus_sigma(n), g)
        bg = BGAmplitude(ks, ws, g)
        cf = closed_form(n, ws, g)
        ok = (bg == cf)
        print(f"n={n} free={freeW}")
        print(f"   w        = {[str(x) for x in ws]}")
        print(f"   BG (py)  = {bg}")
        print(f"   formula  = {cf}")
        print(f"   EXACT match: {ok}\n")
