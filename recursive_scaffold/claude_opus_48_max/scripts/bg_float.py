"""
bg_float.py -- high-precision (mpmath) port of the BG recursion, for arbitrary
REAL kinematics (not just rational).  Mirrors bg.py exactly but uses mpmath.mpf
for momenta/frequencies and mpmath.mpc for amplitudes.  Used for structural
exploration where irrational kinematics are needed; exact bg.py remains the
verification oracle.
"""
import mpmath as mp
from itertools import permutations, combinations
from functools import lru_cache
from math import factorial

mp.mp.dps = 60  # 60 decimal digits


def mag(k):
    return abs(k)


@lru_cache(maxsize=None)
def EKernel(n, ps):
    if n == 3:
        return mp.mpf(-1) / 2 * (mag(ps[0]) * mag(ps[1]) + ps[0] * ps[1])
    p1, p2, rest = ps[0], ps[1], ps[2:]
    qp2 = mag(p2)
    result = qp2 ** (n - 3) * EKernel(3, (p1, p2, sum(rest))) / factorial(n - 2)
    for m in range(1, n - 2):
        newps = (p1, p2 + sum(rest[:m])) + rest[m:]
        result -= qp2 ** m / factorial(m) * EKernel(n - m, newps)
    return result


@lru_cache(maxsize=None)
def FKernel(n, ps):
    if n == 3:
        return mp.mpf(-1) - ps[0] * ps[1] / (mag(ps[0]) * mag(ps[1]))
    p1, p2, rest = ps[0], ps[1], ps[2:]
    qp1, qp2 = mag(p1), mag(p2)
    result = 2 * EKernel(n, ps) / qp1
    for m in range(1, n - 2):
        sigM = p2 + sum(rest[:m])
        eps = (-sigM, p2) + rest[:m]
        fps = (p1, sigM) + rest[m:]
        result -= 2 * EKernel(m + 2, eps) * FKernel(n - m, fps)
    return result / qp2


def vertex(n, moms, omegas):
    moms = tuple(moms)
    s = mp.mpf(0)
    for p in permutations(range(n)):
        s += omegas[p[0]] * omegas[p[1]] * FKernel(n, tuple(moms[i] for i in p))
    return mp.mpc(0, 1) * (-s / 2)  # (-I/2)*s


def propagator(w, k, g):
    mk = mag(k)
    denom = w * w / mk - g
    return mp.mpc(0, 1) * (-1 / denom)  # -I/denom


def set_partitions(S, k):
    S = list(S)
    if k == 1:
        return [[list(S)]]
    if k > len(S):
        return []
    mn = min(S)
    others = [x for x in S if x != mn]
    result = []
    for sz in range(0, len(S) - k + 1):
        for sub in combinations(others, sz):
            fp = [mn] + list(sub)
            rem = [x for x in S if x not in fp]
            if len(rem) >= k - 1:
                for sp in set_partitions(rem, k - 1):
                    result.append([fp] + sp)
    return result


_kList = None
_wList = None
_gVal = None
_bgcache = {}


def _kof(i):
    return _kList[i - 1]


def _wof(i):
    return _wList[i - 1]


def BGCurrent(S):
    if len(S) == 1:
        return mp.mpc(1)
    if S in _bgcache:
        return _bgcache[S]
    wS = sum(_wof(i) for i in S)
    kS = sum(_kof(i) for i in S)
    result = mp.mpc(0)
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
    global _kList, _wList, _gVal, _bgcache
    n = len(momenta)
    _kList = [mp.mpf(x) for x in momenta]
    _wList = [mp.mpf(x) for x in omegas]
    _gVal = mp.mpf(g)
    _bgcache = {}
    rest = list(range(2, n + 1))
    result = mp.mpc(0)
    for m in range(2, n):
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


def amp_from_allW(allW, sigmas, g=1):
    """Given all frequencies and signs, build momenta and return amplitude (mpc)."""
    allW = [mp.mpf(x) for x in allW]
    sig = [mp.mpf(s) for s in sigmas]
    allK = [sig[i] * allW[i] ** 2 / g for i in range(len(allW))]
    return bg_amplitude(allK, allW, g)


def reset_caches():
    EKernel.cache_clear()
    FKernel.cache_clear()
