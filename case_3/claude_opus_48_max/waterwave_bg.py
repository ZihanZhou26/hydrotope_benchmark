"""
waterwave_bg.py
===============
Self-contained *Python* port of the Berends-Giele recursion in OnShellBG.m for
tree-level on-shell scattering amplitudes of 1-D deep-water surface waves
(dispersion  omega^2 = g|k|), together with the closed-form result derived for
the **two-minus sector**.

Conventions (identical to OnShellBG.m):
  * all momenta/frequencies incoming;  k_i = sigma_i * omega_i^2 / g,
    sigma_i in {+1,-1};
  * on the resonant manifold  sum omega_i = 0  and  sum sigma_i omega_i^2 = 0.

The amplitude returned by `bg_amplitude` matches Mathematica's `BGAmplitude`
(it is purely imaginary in this sector).

This module is exact when fed `fractions.Fraction` kinematics, and fast when fed
floats.  See `closed_form_A` for the analytic two-minus result and
`two_minus_kinematics` for a kinematics generator (port of `MakeKinematics`).
"""

from __future__ import annotations
from itertools import permutations
from functools import lru_cache
from math import factorial

# Imaginary unit used inside Vertex/Propagator.  Default is Python's float `1j`.
# `bg_amplitude_hp` temporarily swaps in an mpmath mpc for arbitrary precision.
_I = 1j

# --------------------------------------------------------------------------
#  I.  Interaction kernels (exact)
# --------------------------------------------------------------------------

def _mag(k):
    return abs(k)


def EKernel(n, ps):
    ps = tuple(ps)
    if n == 3:
        p1, p2 = ps[0], ps[1]
        return -(_mag(p1) * _mag(p2) + p1 * p2) / 2
    p1, p2, rest = ps[0], ps[1], ps[2:]
    qp2 = _mag(p2)
    result = qp2 ** (n - 3) * EKernel(3, (p1, p2, sum(rest))) / factorial(n - 2)
    for m in range(1, n - 2):                      # m = 1 .. n-3
        new = (p1, p2 + sum(rest[:m])) + rest[m:]
        result -= qp2 ** m / factorial(m) * EKernel(n - m, new)
    return result


def FKernel(n, ps):
    ps = tuple(ps)
    if n == 3:
        p1, p2 = ps[0], ps[1]
        return -1 - p1 * p2 / (_mag(p1) * _mag(p2))
    p1, p2, rest = ps[0], ps[1], ps[2:]
    qp1, qp2 = _mag(p1), _mag(p2)
    result = 2 * EKernel(n, ps) / qp1
    for m in range(1, n - 2):                      # m = 1 .. n-3
        sigM = p2 + sum(rest[:m])
        e = EKernel(m + 2, (-sigM, p2) + rest[:m])
        f = FKernel(n - m, (p1, sigM) + rest[m:])
        result -= 2 * e * f
    return result / qp2


# --------------------------------------------------------------------------
#  II.  Vertex and propagator
# --------------------------------------------------------------------------

def Vertex(n, moms, omegas):
    moms = tuple(moms)
    omegas = tuple(omegas)
    result = 0
    for p in permutations(range(n)):
        result += omegas[p[0]] * omegas[p[1]] * FKernel(n, tuple(moms[i] for i in p))
    return (-_I / 2) * result


def Propagator(omega, k, g):
    return -_I / (omega ** 2 / _mag(k) - g)


# --------------------------------------------------------------------------
#  III.  Set partitions into exactly k nonempty blocks (port of OnShellBG.m)
# --------------------------------------------------------------------------

@lru_cache(maxsize=None)
def set_partitions(S, k):
    S = tuple(sorted(S))
    if k == 1:
        return ((S,),)
    if k > len(S):
        return ()
    mn = S[0]
    others = S[1:]
    out = []
    # choose the rest of the block containing the minimum element
    from itertools import combinations
    for r in range(0, len(S) - k + 1):
        for sub in combinations(others, r):
            fp = (mn,) + sub
            rem = tuple(x for x in S if x not in fp)
            if len(rem) >= k - 1:
                for sp in set_partitions(rem, k - 1):
                    out.append((fp,) + sp)
    return tuple(out)


# --------------------------------------------------------------------------
#  IV.  Berends-Giele recursion
# --------------------------------------------------------------------------

def bg_amplitude(momenta, omegas, g):
    """Tree amplitude A_n.  momenta[i] = sigma_i omega_i^2 / g."""
    momenta = list(momenta)
    omegas = list(omegas)
    n = len(momenta)

    @lru_cache(maxsize=None)
    def current(S):                                # S : sorted tuple of indices
        if len(S) == 1:
            return 1
        wS = sum(omegas[i] for i in S)
        kS = sum(momenta[i] for i in S)
        result = 0
        for m in range(2, len(S) + 1):
            for part in set_partitions(S, m):
                sMoms = [sum(momenta[i] for i in blk) for blk in part]
                sOms = [sum(omegas[i] for i in blk) for blk in part]
                vMoms = [-kS] + sMoms
                vOms = [-wS] + sOms
                prod = 1
                for blk in part:
                    prod *= current(blk)
                result += Vertex(m + 1, vMoms, vOms) * prod
        return result * Propagator(wS, kS, g)

    rest = tuple(range(1, n))
    result = 0
    for m in range(2, n):
        for part in set_partitions(rest, m):
            sMoms = [sum(momenta[i] for i in blk) for blk in part]
            sOms = [sum(omegas[i] for i in blk) for blk in part]
            vMoms = [momenta[0]] + sMoms
            vOms = [omegas[0]] + sOms
            prod = 1
            for blk in part:
                prod *= current(blk)
            result += Vertex(m + 1, vMoms, vOms) * prod
    return result


# --------------------------------------------------------------------------
#  V.  Kinematics solver (port of MakeKinematics)
# --------------------------------------------------------------------------

def two_minus_kinematics(n, free_w, g=1):
    """Two-minus sector: sigma = (-1,-1,+1,...,+1).
    free_w = (w2,...,w_{n-1})  (length n-2);  returns (momenta, omegas)."""
    assert len(free_w) == n - 2
    sig = [-1, -1] + [1] * (n - 2)
    sumFree = sum(free_w)
    sumSigmaW2 = sum(sig[i + 1] * free_w[i] ** 2 for i in range(n - 2))  # i=2..n-1
    wn = -(sig[0] * sumFree ** 2 + sumSigmaW2) / (2 * sig[0] * sumFree)
    w1 = -(sumFree + wn)
    allW = [w1] + list(free_w) + [wn]
    allK = [sig[i] * allW[i] ** 2 / g for i in range(n)]
    return allK, allW, sig


# --------------------------------------------------------------------------
#  VI.  Closed form for the two-minus sector  (the result of this work)
# --------------------------------------------------------------------------

def closed_form_A(omegas, sigmas, g=1):
    """Closed-form tree amplitude A_n in the two-minus sector.

        A_n = i * 2^(n-1) * g^(3-n) * (w_a w_b) * [min(w_a^2, w_b^2)]^(n-3)

    where {a,b} are the two 'minus' legs (sigma = -1).  Equivalently, with
    w_<, w_>  the smaller/larger-|.| of the two minus-leg frequencies,

        A_n = i * 2^(n-1) * g^(3-n) * w_>  * w_<^(2n-5).

    Valid (exactly equals bg_amplitude) whenever a minus leg carries the
    smallest |momentum|, min(w_a^2,w_b^2) <= w_j^2 for every plus leg j -- the
    generic/physical regime (true for all the OnShellBG.m test kinematics and
    for large/small *minus* frequencies or large *plus* frequencies).
    """
    n = len(omegas)
    minus = [omegas[i] for i in range(n) if sigmas[i] == -1]
    if len(minus) != 2:
        raise ValueError("two-minus sector needs exactly two sigma=-1 legs")
    wa, wb = minus
    return 1j * 2 ** (n - 1) * g ** (3 - n) * (wa * wb) * min(wa ** 2, wb ** 2) ** (n - 3)


def in_physical_regime(omegas, sigmas):
    """True iff a minus leg has the smallest |momentum| (domain of closed_form_A)."""
    n = len(omegas)
    minus2 = [omegas[i] ** 2 for i in range(n) if sigmas[i] == -1]
    plus2 = [omegas[i] ** 2 for i in range(n) if sigmas[i] == 1]
    return min(minus2) <= min(plus2)


def bg_amplitude_hp(momenta, omegas, g, dps=60):
    """High-precision (mpmath) evaluation of bg_amplitude.  Use to confirm the
    closed form to far below 1e-10.  momenta/omegas may be ints/Fractions/floats."""
    global _I
    import mpmath as mp
    mp.mp.dps = dps
    saved = _I
    _I = mp.mpc(0, 1)
    try:
        mm = [mp.mpf(x.numerator) / mp.mpf(x.denominator) if hasattr(x, "numerator")
              else mp.mpf(x) for x in momenta]
        ww = [mp.mpf(x.numerator) / mp.mpf(x.denominator) if hasattr(x, "numerator")
              else mp.mpf(x) for x in omegas]
        gg = mp.mpf(g.numerator) / mp.mpf(g.denominator) if hasattr(g, "numerator") else mp.mpf(g)
        return bg_amplitude(mm, ww, gg)
    finally:
        _I = saved


if __name__ == "__main__":
    # self-test against the closed form, high precision
    from fractions import Fraction as F
    import mpmath as mp
    mp.mp.dps = 60
    cases = [
        (5, [F(2), F(3), F(5)]),
        (5, [F(1), F(2), F(3)]),
        (6, [F(3, 2), F(2), F(5, 2), F(3)]),
        (7, [F(3, 2), F(2), F(5, 2), F(3), F(7, 2)]),
    ]
    print(f"{'n':>2}  {'BG (mpmath)':>26}  {'closed form':>26}  rel.err")
    for n, fw in cases:
        k, w, sig = two_minus_kinematics(n, fw, 1)
        a = bg_amplitude_hp(k, w, 1, dps=60)
        c = closed_form_A(w, sig, 1)
        rel = abs(a - c) / abs(a) if a != 0 else abs(a - c)
        print(f"{n:>2}  {mp.nstr(a.imag,12)+'i':>26}  {mp.nstr(mp.mpf(c.imag),12)+'i':>26}  {mp.nstr(rel,3)}")
