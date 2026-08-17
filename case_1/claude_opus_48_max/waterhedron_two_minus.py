"""
waterhedron_two_minus.py
========================

Self-contained tools for the **two-minus sector** of tree-level on-shell
n-point scattering amplitudes for 1D deep-water surface waves.

Dispersion:   omega_i^2 = g |k_i|,   k_i = sigma_i omega_i^2 / g,  sigma_i in {+1,-1}.
Two-minus sector:   sigma = (-1, -1, +1, ..., +1)  (legs 1,2 are minus).
On-shell:     sum_i omega_i = 0,   sum_i sigma_i omega_i^2 = 0.

Contents
--------
* `make_kinematics(n, free_w, sigmas, g)` : Python port of MakeKinematics.
* `bg_amplitude(momenta, omegas, g)`      : Python (float) port of the
  Berends-Giele recursion in OnShellBG.m -- an INDEPENDENT cross-check of
  the reference Wolfram code.
* `A_canonical(omegas)`  : the closed-form CANONICAL formula
        A_n = 2^(n-1) i * omega_1 * omega_2^(2n-5)
  valid whenever |omega_2| = min_i |omega_i|  (true for the standard
  ascending-positive free-frequency sampling, e.g. the OnShellBG.m examples).
* `A_canonical_free(n, free_w, g)` : the equivalent free-frequency RATIONAL
  form (numerator/denominator, simple pole on the channel sub-energy
  S1 = omega_2+...+omega_{n-1} = -(omega_1+omega_n)).
* `A_n5_general(omegas)`  : the FULL piecewise rule for n=5 valid for
  generic kinematics in any chamber where the two smallest |omega| determine
  the amplitude (documents the genuinely chamber-dependent structure).

All amplitudes come out purely imaginary, returned as Python complex.
"""

from itertools import permutations, combinations
from functools import lru_cache
from math import factorial
from fractions import Fraction as Fr


# --------------------------------------------------------------------------
#  Exact Gaussian-rational arithmetic  (a + b i,  a,b in Q)  for an
#  EXACT cross-check of the float Berends-Giele port.
# --------------------------------------------------------------------------

class Cx:
    __slots__ = ("re", "im")

    def __init__(self, re=0, im=0):
        self.re = Fr(re); self.im = Fr(im)

    def __add__(s, o):
        o = s._c(o); return Cx(s.re + o.re, s.im + o.im)
    __radd__ = __add__

    def __sub__(s, o):
        o = s._c(o); return Cx(s.re - o.re, s.im - o.im)

    def __rsub__(s, o):
        o = s._c(o); return Cx(o.re - s.re, o.im - s.im)

    def __mul__(s, o):
        o = s._c(o)
        return Cx(s.re * o.re - s.im * o.im, s.re * o.im + s.im * o.re)
    __rmul__ = __mul__

    def __truediv__(s, o):
        o = s._c(o); d = o.re * o.re + o.im * o.im
        return Cx((s.re * o.re + s.im * o.im) / d, (s.im * o.re - s.re * o.im) / d)

    def __rtruediv__(s, o):
        return s._c(o).__truediv__(s)

    def __pow__(s, n):
        r = Cx(1, 0)
        for _ in range(int(n)):
            r = r * s
        return r

    def __neg__(s):
        return Cx(-s.re, -s.im)

    @staticmethod
    def _c(o):
        return o if isinstance(o, Cx) else Cx(o, 0)

    def __repr__(s):
        return f"{s.re} + {s.im} i"

    def complex(s):
        return complex(float(s.re), float(s.im))


I_ = Cx(0, 1)


def _abs_fr(x):
    return x if x >= 0 else -x


# --------------------------------------------------------------------------
#  Berends-Giele recursion  (float port of OnShellBG.m, sections I-V)
# --------------------------------------------------------------------------

def _ekernel(n, ps):
    ps = tuple(ps)
    if n == 3:
        return -0.5 * (abs(ps[0]) * abs(ps[1]) + ps[0] * ps[1])
    p1, p2, rest = ps[0], ps[1], ps[2:]
    qp2 = abs(p2)
    res = qp2 ** (n - 3) * _ekernel(3, (p1, p2, sum(rest))) / factorial(n - 2)
    for m in range(1, n - 3 + 1):
        newps = (p1, p2 + sum(rest[:m])) + rest[m:]
        res -= qp2 ** m / factorial(m) * _ekernel(n - m, newps)
    return res


def _fkernel(n, ps):
    ps = tuple(ps)
    if n == 3:
        return -1.0 - ps[0] * ps[1] / (abs(ps[0]) * abs(ps[1]))
    p1, p2, rest = ps[0], ps[1], ps[2:]
    qp1, qp2 = abs(p1), abs(p2)
    res = 2.0 * _ekernel(n, ps) / qp1
    for m in range(1, n - 3 + 1):
        sigM = p2 + sum(rest[:m])
        ek = _ekernel(m + 2, (-sigM, p2) + rest[:m])
        fk = _fkernel(n - m, (p1, sigM) + rest[m:])
        res -= 2.0 * ek * fk
    return res / qp2


def _vertex(n, moms, omegas):
    moms = tuple(moms)
    res = 0.0
    for p in permutations(range(n)):
        res += omegas[p[0]] * omegas[p[1]] * _fkernel(n, tuple(moms[i] for i in p))
    return (-0.5j) * res


def _set_partitions(S, k):
    """Partitions of sorted tuple S into exactly k nonempty blocks (faithful
    port of SetPartitions; blocks identified by their min element)."""
    S = tuple(S)
    if k == 1:
        return [(S,)]
    if k > len(S):
        return []
    mn = min(S)
    rest = tuple(x for x in S if x != mn)
    out = []
    # choose the other members of the block containing mn
    for r in range(0, len(S) - k + 1):
        for sub in combinations(rest, r):
            fp = (mn,) + sub
            rem = tuple(x for x in S if x not in fp)
            if len(rem) >= k - 1:
                for sp in _set_partitions(rem, k - 1):
                    out.append((fp,) + sp)
    return out


def bg_amplitude(momenta, omegas, g):
    """Float port of BGAmplitude.  momenta, omegas are 0-indexed lists."""
    n = len(momenta)
    kL = list(momenta)
    wL = list(omegas)

    @lru_cache(maxsize=None)
    def current(S):  # S : sorted tuple of 0-indexed leg labels
        if len(S) == 1:
            return 1.0 + 0j
        wS = sum(wL[i] for i in S)
        kS = sum(kL[i] for i in S)
        res = 0.0 + 0j
        for m in range(2, len(S) + 1):
            for part in _set_partitions(S, m):
                sMoms = [sum(kL[j] for j in blk) for blk in part]
                sOms = [sum(wL[j] for j in blk) for blk in part]
                vM = [-kS] + sMoms
                vO = [-wS] + sOms
                prod = 1.0 + 0j
                for blk in part:
                    prod *= current(blk)
                res += _vertex(m + 1, vM, vO) * prod
        prop = -1j / (wS ** 2 / abs(kS) - g)
        return res * prop

    rest = tuple(range(1, n))   # legs 2..n  -> 0-indexed 1..n-1
    result = 0.0 + 0j
    for m in range(2, n):
        for part in _set_partitions(rest, m):
            sMoms = [sum(kL[j] for j in blk) for blk in part]
            sOms = [sum(wL[j] for j in blk) for blk in part]
            vM = [kL[0]] + sMoms
            vO = [wL[0]] + sOms
            prod = 1.0 + 0j
            for blk in part:
                prod *= current(blk)
            result += _vertex(m + 1, vM, vO) * prod
    return result


# --------------------------------------------------------------------------
#  EXACT Berends-Giele recursion (Gaussian-rational; mirrors the float port)
# --------------------------------------------------------------------------

def _ekernel_x(n, ps):
    ps = tuple(ps)
    if n == 3:
        return Fr(-1, 2) * (_abs_fr(ps[0]) * _abs_fr(ps[1]) + ps[0] * ps[1])
    p1, p2, rest = ps[0], ps[1], ps[2:]
    qp2 = _abs_fr(p2)
    res = qp2 ** (n - 3) * _ekernel_x(3, (p1, p2, sum(rest))) / factorial(n - 2)
    for m in range(1, n - 3 + 1):
        newps = (p1, p2 + sum(rest[:m])) + rest[m:]
        res -= Fr(qp2 ** m, factorial(m)) * _ekernel_x(n - m, newps)
    return res


def _fkernel_x(n, ps):
    ps = tuple(ps)
    if n == 3:
        return Fr(-1) - ps[0] * ps[1] / (_abs_fr(ps[0]) * _abs_fr(ps[1]))
    p1, p2, rest = ps[0], ps[1], ps[2:]
    qp1, qp2 = _abs_fr(p1), _abs_fr(p2)
    res = 2 * _ekernel_x(n, ps) / qp1
    for m in range(1, n - 3 + 1):
        sigM = p2 + sum(rest[:m])
        ek = _ekernel_x(m + 2, (-sigM, p2) + rest[:m])
        fk = _fkernel_x(n - m, (p1, sigM) + rest[m:])
        res -= 2 * ek * fk
    return res / qp2


def _vertex_x(n, moms, omegas):
    moms = tuple(moms)
    res = Fr(0)
    for p in permutations(range(n)):
        res += omegas[p[0]] * omegas[p[1]] * _fkernel_x(n, tuple(moms[i] for i in p))
    return Cx(0, Fr(-1, 2)) * res


def bg_amplitude_exact(momenta, omegas, g):
    """EXACT (Gaussian-rational) port of BGAmplitude.  Inputs must be
    Fraction/int.  Returns a Cx.  Use .complex() to get a Python complex."""
    n = len(momenta)
    kL = [Fr(x) for x in momenta]
    wL = [Fr(x) for x in omegas]
    g = Fr(g)

    @lru_cache(maxsize=None)
    def current(S):
        if len(S) == 1:
            return Cx(1, 0)
        wS = sum(wL[i] for i in S)
        kS = sum(kL[i] for i in S)
        res = Cx(0, 0)
        for m in range(2, len(S) + 1):
            for part in _set_partitions(S, m):
                sMoms = [sum(kL[j] for j in blk) for blk in part]
                sOms = [sum(wL[j] for j in blk) for blk in part]
                vM = [-kS] + sMoms
                vO = [-wS] + sOms
                prod = Cx(1, 0)
                for blk in part:
                    prod = prod * current(blk)
                res = res + _vertex_x(m + 1, vM, vO) * prod
        prop = Cx(0, -1) / (wS ** 2 / _abs_fr(kS) - g)
        return res * prop

    rest = tuple(range(1, n))
    result = Cx(0, 0)
    for m in range(2, n):
        for part in _set_partitions(rest, m):
            sMoms = [sum(kL[j] for j in blk) for blk in part]
            sOms = [sum(wL[j] for j in blk) for blk in part]
            vM = [kL[0]] + sMoms
            vO = [wL[0]] + sOms
            prod = Cx(1, 0)
            for blk in part:
                prod = prod * current(blk)
            result = result + _vertex_x(m + 1, vM, vO) * prod
    return result


# --------------------------------------------------------------------------
#  Kinematics (port of MakeKinematics)
# --------------------------------------------------------------------------

def make_kinematics(n, free_w, sigmas, g=1.0):
    assert len(free_w) == n - 2, "need n-2 free frequencies"
    assert sigmas[0] + sigmas[n - 1] == 0, "need sigma_1 + sigma_n = 0"
    sumFree = sum(free_w)
    sumSigmaW2 = sum(sigmas[i + 1] * free_w[i] ** 2 for i in range(n - 2))
    wn = -(sigmas[0] * sumFree ** 2 + sumSigmaW2) / (2 * sigmas[0] * sumFree)
    w1 = -(sumFree + wn)
    allW = [w1] + list(free_w) + [wn]
    allK = [sigmas[i] * allW[i] ** 2 / g for i in range(n)]
    return allK, allW


def two_minus_sigma(n):
    return [-1, -1] + [1] * (n - 2)


# --------------------------------------------------------------------------
#  The closed-form formulas
# --------------------------------------------------------------------------

def A_canonical(omegas):
    """A_n = 2^(n-1) i omega_1 omega_2^(2n-5).
    Valid when |omega_2| = min_i |omega_i| (e.g. ascending-positive sampling)."""
    n = len(omegas)
    return 2 ** (n - 1) * 1j * omegas[0] * omegas[1] ** (2 * n - 5)


def A_canonical_free(n, free_w, g=1.0):
    """Equivalent free-frequency RATIONAL form (omega_1, omega_n eliminated):
        A_n = -2^(n-2) i * w2^(2n-5) (S1^2 - w2^2 + sum_{i>=3} wi^2) / S1,
    S1 = w2 + ... + w_{n-1}.  (Same chamber of validity as A_canonical.)"""
    w = list(free_w)                       # w[0]=omega_2, ..., w[n-3]=omega_{n-1}
    w2 = w[0]
    S1 = sum(w)
    quad = S1 ** 2 - w2 ** 2 + sum(wi ** 2 for wi in w[1:])
    return -(2 ** (n - 2)) * 1j * w2 ** (2 * n - 5) * quad / S1


def A_n5_general(omegas):
    """Full n=5 piecewise rule, generic chamber where the TWO smallest |omega|
    fix the amplitude:
        A5 = 16 i (w1 w2) * Phi,   f1<=f2 = two smallest |omega|, s1,s2 sigma
        s1=-1            : Phi = f1^4
        s1=+1, s2=-1     : Phi = f1^2 (2 f2^2 - f1^2)
        s1=+1, s2=+1     : Phi = 2 f1^2 f2^2
    (Legs 1,2 minus; 3,4,5 plus.  Holds in the all-positive-free-frequency
    region; finer chambers exist for mixed signs.)"""
    assert len(omegas) == 5
    prodMu = omegas[0] * omegas[1]
    mags = [abs(x) for x in omegas]
    order = sorted(range(5), key=lambda i: mags[i])
    l1, l2 = order[0], order[1]
    f1, f2 = mags[l1], mags[l2]
    s1 = -1 if l1 <= 1 else 1
    s2 = -1 if l2 <= 1 else 1
    if s1 == -1:
        phi = f1 ** 4
    elif s2 == -1:
        phi = f1 ** 2 * (2 * f2 ** 2 - f1 ** 2)
    else:
        phi = 2 * f1 ** 2 * f2 ** 2
    return 16j * prodMu * phi


# --------------------------------------------------------------------------
#  Quick self-test when run directly
# --------------------------------------------------------------------------

if __name__ == "__main__":
    # Reference values computed by the Wolfram BGAmplitude in OnShellBG.m:
    ref = {
        (5, (2, 3, 5)): -3328j,
        (5, (3, 5, 7)): -37584j,
        (6, (2, 3, 5, 7)): Fr(-753664) * 1j / 17,
        (7, (2, 3, 5, 7, 11)): Fr(-4030464) * 1j / 7,
    }
    print(" n  free_w             Im[BG_exact](py)     Im[canonical]    exact?")
    for (n, fw), rv in ref.items():
        ks, ws = make_kinematics(n, [Fr(x) for x in fw], two_minus_sigma(n), Fr(1))
        bgx = bg_amplitude_exact(ks, ws, Fr(1))                  # exact, purely imaginary
        ca_im = Fr(2) ** (n - 1) * ws[0] * ws[1] ** (2 * n - 5)  # exact Im[A_canonical]
        exact_ok = (bgx.re == 0) and (bgx.im == ca_im)
        print(f" {n}  {str(fw):16s}  {str(bgx.im):>16s}  {str(ca_im):>16s}   {exact_ok}")
        assert bgx.re == 0, "amplitude should be purely imaginary"
        assert bgx.im == ca_im, "EXACT BG vs canonical mismatch"
        # cross-check against the float port and the Wolfram reference too:
        assert abs(bg_amplitude(ks, [float(x) for x in ws], 1.0) - complex(rv)) \
            <= 1e-6 * abs(complex(rv))
    print("All self-tests passed: EXACT Gaussian-rational BG == canonical formula,")
    print("and the float BG port agrees with the Wolfram reference values.")
