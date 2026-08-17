"""
bg.py -- exact Python port of the Berends-Giele recursion in OnShellBG.m.

Faithful translation (1-indexed Wolfram -> 0-indexed Python) of:
  mag, EKernel, FKernel, Vertex, Propagator, SetPartitions, BGCurrent,
  BGAmplitude, MakeKinematics.

All arithmetic is exact: real momenta/frequencies are fractions.Fraction;
amplitudes are complex-rational (class CQ with Fraction real/imag parts).
EKernel/FKernel are pure functions of their momentum tuple -> globally memoized.
BGCurrent depends on the global kinematics -> its cache is reset per amplitude.

Validated to reproduce the wolframscript oracle (bg_oracle.wls) EXACTLY.
"""
from fractions import Fraction as F
from itertools import permutations, combinations
from functools import lru_cache
from math import factorial


class DegenerateKinematics(Exception):
    """Raised when an internal propagator hits |k_S| = 0 (0/0 or pole)."""


class CQ:
    """Exact complex-rational number a + b i, a,b in Q."""
    __slots__ = ("re", "im")

    def __init__(self, re=0, im=0):
        self.re = re if isinstance(re, F) else F(re)
        self.im = im if isinstance(im, F) else F(im)

    def __add__(self, o):
        o = _cq(o)
        return CQ(self.re + o.re, self.im + o.im)
    __radd__ = __add__

    def __sub__(self, o):
        o = _cq(o)
        return CQ(self.re - o.re, self.im - o.im)

    def __rsub__(self, o):
        o = _cq(o)
        return CQ(o.re - self.re, o.im - self.im)

    def __neg__(self):
        return CQ(-self.re, -self.im)

    def __mul__(self, o):
        o = _cq(o)
        return CQ(self.re * o.re - self.im * o.im,
                  self.re * o.im + self.im * o.re)
    __rmul__ = __mul__

    def __truediv__(self, o):
        o = _cq(o)
        d = o.re * o.re + o.im * o.im
        if d == 0:
            raise ZeroDivisionError("CQ division by zero")
        return CQ((self.re * o.re + self.im * o.im) / d,
                  (self.im * o.re - self.re * o.im) / d)

    def __eq__(self, o):
        o = _cq(o)
        return self.re == o.re and self.im == o.im

    def __repr__(self):
        return f"CQ({self.re}, {self.im})"

    def is_real(self):
        return self.im == 0

    def is_imag(self):
        return self.re == 0


def _cq(x):
    if isinstance(x, CQ):
        return x
    return CQ(x, 0)


def mag(k):
    return abs(k)


# ---------------- kernels (pure, globally memoized) ----------------
@lru_cache(maxsize=None)
def EKernel(n, ps):
    if n == 3:
        return F(-1, 2) * (mag(ps[0]) * mag(ps[1]) + ps[0] * ps[1])
    p1, p2, rest = ps[0], ps[1], ps[2:]
    qp2 = mag(p2)
    result = qp2 ** (n - 3) * EKernel(3, (p1, p2, sum(rest))) / factorial(n - 2)
    for m in range(1, n - 2):  # m = 1 .. n-3
        newps = (p1, p2 + sum(rest[:m])) + rest[m:]
        result -= qp2 ** m / factorial(m) * EKernel(n - m, newps)
    return result


@lru_cache(maxsize=None)
def FKernel(n, ps):
    if n == 3:
        return F(-1) - ps[0] * ps[1] / (mag(ps[0]) * mag(ps[1]))
    p1, p2, rest = ps[0], ps[1], ps[2:]
    qp1, qp2 = mag(p1), mag(p2)
    result = 2 * EKernel(n, ps) / qp1
    for m in range(1, n - 2):  # m = 1 .. n-3
        sigM = p2 + sum(rest[:m])
        eps = (-sigM, p2) + rest[:m]
        fps = (p1, sigM) + rest[m:]
        result -= 2 * EKernel(m + 2, eps) * FKernel(n - m, fps)
    return result / qp2


def vertex(n, moms, omegas):
    # (-I/2) * sum over permutations of omegas[p0]*omegas[p1]*FKernel[n, moms[p]]
    moms = tuple(moms)
    s = F(0)
    for p in permutations(range(n)):
        s += omegas[p[0]] * omegas[p[1]] * FKernel(n, tuple(moms[i] for i in p))
    # (-I/2)*s  ==  purely imaginary CQ(0, -s/2)
    return CQ(0, -s / 2)


def propagator(w, k, g):
    mk = mag(k)
    if mk == 0:
        raise DegenerateKinematics(f"|k_S|=0 (w={w}, k={k})")
    denom = w * w / mk - g
    if denom == 0:
        raise DegenerateKinematics(f"on-shell internal pole (w={w}, k={k}, g={g})")
    # -I/denom  ==  CQ(0, -1/denom)
    return CQ(0, -F(1) / denom)


# ---------------- set partitions ----------------
def set_partitions(S, k):
    """Unordered set partitions of list S into exactly k nonempty blocks.
    Faithful port of the Wolfram SetPartitions (min-element-first)."""
    S = list(S)
    if k == 1:
        return [[list(S)]]
    if k > len(S):
        return []
    mn = min(S)
    others = [x for x in S if x != mn]
    result = []
    maxsize = len(S) - k  # subset sizes 0 .. len(S)-k
    for sz in range(0, maxsize + 1):
        for sub in combinations(others, sz):
            fp = [mn] + list(sub)
            rem = [x for x in S if x not in fp]
            if len(rem) >= k - 1:
                for sp in set_partitions(rem, k - 1):
                    result.append([fp] + sp)
    return result


# ---------------- BG recursion ----------------
_kList = None
_wList = None
_gVal = None
_bgcache = {}


def _kof(label):
    return _kList[label - 1]


def _wof(label):
    return _wList[label - 1]


def BGCurrent(S):
    """S: sorted tuple of 1-indexed leg labels."""
    if len(S) == 1:
        return CQ(1)
    if S in _bgcache:
        return _bgcache[S]
    wS = sum(_wof(i) for i in S)
    kS = sum(_kof(i) for i in S)
    result = CQ(0)
    Slist = list(S)
    for m in range(2, len(S) + 1):
        for part in set_partitions(Slist, m):
            sMoms = [sum(_kof(i) for i in block) for block in part]
            sOmegas = [sum(_wof(i) for i in block) for block in part]
            vMoms = [-kS] + sMoms
            vOmegas = [-wS] + sOmegas
            term = vertex(m + 1, vMoms, vOmegas)
            for block in part:
                term = term * BGCurrent(tuple(sorted(block)))
            result = result + term
    result = result * propagator(wS, kS, _gVal)
    _bgcache[S] = result
    return result


def bg_amplitude(momenta, omegas, g):
    """Exact two-... (any sector) tree amplitude. Returns CQ."""
    global _kList, _wList, _gVal, _bgcache
    n = len(momenta)
    _kList = [F(x) for x in momenta]
    _wList = [F(x) for x in omegas]
    _gVal = F(g)
    _bgcache = {}
    rest = list(range(2, n + 1))  # labels 2..n
    result = CQ(0)
    for m in range(2, n):  # m = 2 .. n-1
        for part in set_partitions(rest, m):
            sMoms = [sum(_kof(i) for i in block) for block in part]
            sOmegas = [sum(_wof(i) for i in block) for block in part]
            vMoms = [_kList[0]] + sMoms
            vOmegas = [_wList[0]] + sOmegas
            term = vertex(m + 1, vMoms, vOmegas)
            for block in part:
                term = term * BGCurrent(tuple(sorted(block)))
            result = result + term
    return result


def make_kinematics(n, freeW, sigmas, g):
    """Returns (allK, allW) as lists of Fractions. Port of MakeKinematics."""
    freeW = [F(x) for x in freeW]
    sigmas = [F(x) for x in sigmas]
    g = F(g)
    assert len(freeW) == n - 2, "need n-2 free frequencies"
    assert sigmas[0] + sigmas[n - 1] == 0, "need sigma_1 + sigma_n = 0"
    sumFree = sum(freeW)
    sigmaFree = sigmas[1:n - 1]
    sumSigmaW2 = sum(sigmaFree[i] * freeW[i] ** 2 for i in range(len(freeW)))
    wn = -(sigmas[0] * sumFree ** 2 + sumSigmaW2) / (2 * sigmas[0] * sumFree)
    w1 = -(sumFree + wn)
    allW = [w1] + freeW + [wn]
    allK = [sigmas[i] * allW[i] ** 2 / g for i in range(n)]
    return allK, allW


def two_minus_sigmas(n):
    return [F(-1), F(-1)] + [F(1)] * (n - 2)


def amp_two_minus(n, freeW, g=1):
    """Two-minus-sector amplitude for free frequencies freeW (len n-2)."""
    sig = two_minus_sigmas(n)
    allK, allW = make_kinematics(n, freeW, sig, g)
    A = bg_amplitude(allK, allW, g)
    return A, allW, allK
