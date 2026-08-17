"""
Fast exact (Gaussian-rational) port of the Berends-Giele recursion in OnShellBG.m,
for 1D deep-water surface waves on the resonant manifold.

Re-implemented from the definitions in OnShellBG.m (the one allowed code file).
Validated against the Mathematica reference values.

All input frequencies are rationals -> all arithmetic is exact.
Amplitudes come out as i * (rational); we carry full Gaussian rationals (a+bi).
"""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import permutations
import math

# ---- Gaussian rational: (re, im) both Fraction ----
class CR:
    __slots__ = ("re", "im")
    def __init__(self, re=0, im=0):
        self.re = re if isinstance(re, Q) else Q(re)
        self.im = im if isinstance(im, Q) else Q(im)
    def __add__(a, b):
        b = a._c(b); return CR(a.re + b.re, a.im + b.im)
    __radd__ = __add__
    def __sub__(a, b):
        b = a._c(b); return CR(a.re - b.re, a.im - b.im)
    def __neg__(a): return CR(-a.re, -a.im)
    def __mul__(a, b):
        b = a._c(b)
        return CR(a.re*b.re - a.im*b.im, a.re*b.im + a.im*b.re)
    __rmul__ = __mul__
    def divreal(a, r):   # divide by a real Fraction r
        r = Q(r); return CR(a.re/r, a.im/r)
    @staticmethod
    def _c(b):
        if isinstance(b, CR): return b
        return CR(b, 0)
    def __repr__(self): return f"CR({self.re},{self.im})"

I = CR(0, 1)

def mag(k):  # k is a Fraction
    return k if k >= 0 else -k

# Kernels are REAL (Fraction). Memoize on momentum tuple.
@lru_cache(maxsize=None)
def EKernel(ps):
    n = len(ps)
    if n == 3:
        return Q(-1,2)*(mag(ps[0])*mag(ps[1]) + ps[0]*ps[1])
    if n < 3:
        raise ValueError("EKernel needs >=3")
    p1, p2, rest = ps[0], ps[1], ps[2:]
    qp2 = mag(p2)
    trest = sum(rest)
    result = qp2**(n-3) * EKernel((p1, p2, trest)) / math.factorial(n-2)
    # ^ math.factorial returns int; division Fraction/int stays Fraction
    for m in range(1, n-3+1):
        sub = (p1, p2 + sum(rest[:m])) + rest[m:]
        result -= qp2**m / math.factorial(m) * EKernel(sub)
    return result

@lru_cache(maxsize=None)
def FKernel(ps):
    n = len(ps)
    if n == 3:
        return Q(-1) - ps[0]*ps[1]/(mag(ps[0])*mag(ps[1]))
    if n < 3:
        raise ValueError("FKernel needs >=3")
    p1, p2, rest = ps[0], ps[1], ps[2:]
    qp1 = mag(p1); qp2 = mag(p2)
    result = 2*EKernel(ps)/qp1
    for m in range(1, n-3+1):
        sigM = p2 + sum(rest[:m])
        a = (-sigM, p2) + rest[:m]
        b = (p1, sigM) + rest[m:]
        result -= 2*EKernel(a)*FKernel(b)
    return result/qp2

def Vertex(moms, omegas):
    # moms, omegas tuples of length n;  (-I/2) sum_perm omega[p0] omega[p1] F[moms[perm]]
    n = len(moms)
    acc = Q(0)
    for p in permutations(range(n)):
        permmoms = tuple(moms[i] for i in p)
        acc += omegas[p[0]]*omegas[p[1]]*FKernel(permmoms)
    return (CR(0, Q(-1,2)) * acc)  # (-I/2)*acc  ; acc real

def Propagator(wS, kS, g):
    # -I/(wS^2/|kS| - g)
    denom = wS*wS/mag(kS) - g
    return CR(0, -1).divreal(denom)

# ---- set partitions of a list S into exactly k nonempty blocks (Mathematica order-agnostic) ----
def set_partitions_k(S, k):
    S = list(S)
    if k == 1:
        return [[tuple(S)]]
    if k > len(S):
        return []
    res = []
    mn = min(S)
    others = [x for x in S if x != mn]
    # choose subset 'sub' of others to join mn as first block; size 0..len(S)-k
    from itertools import combinations
    for size in range(0, len(S)-k+1):
        for sub in combinations(others, size):
            fp = (mn,) + sub
            rem = [x for x in S if x not in fp]
            if len(rem) >= k-1:
                for sp in set_partitions_k(rem, k-1):
                    res.append([fp] + sp)
    return res

class BG:
    def __init__(self, kList, wList, g):
        # kList, wList: tuples of Fractions, index 0..n-1
        self.k = tuple(Q(x) for x in kList)
        self.w = tuple(Q(x) for x in wList)
        self.g = Q(g)
        self.n = len(self.k)
        self._cur = {}

    def total_k(self, S): return sum(self.k[i] for i in S)
    def total_w(self, S): return sum(self.w[i] for i in S)

    def current(self, S):
        # S: tuple of indices (0-based)
        key = tuple(sorted(S))
        if len(key) == 1:
            return CR(1, 0)
        if key in self._cur:
            return self._cur[key]
        wS = self.total_w(key); kS = self.total_k(key)
        result = CR(0, 0)
        for m in range(2, len(key)+1):
            for part in set_partitions_k(key, m):
                sMoms = tuple(self.total_k(b) for b in part)
                sOmegas = tuple(self.total_w(b) for b in part)
                vMoms = (-kS,) + sMoms
                vOmegas = (-wS,) + sOmegas
                v = Vertex(vMoms, vOmegas)
                prod = CR(1, 0)
                for b in part:
                    prod = prod * self.current(b)
                result = result + v*prod
        val = result * Propagator(wS, kS, self.g)
        self._cur[key] = val
        return val

    def amplitude(self):
        n = self.n
        rest = tuple(range(1, n))  # indices 1..n-1 (0-based) == Mathematica 2..n
        result = CR(0, 0)
        k1 = self.k[0]; w1 = self.w[0]
        for m in range(2, n):  # m = 2..n-1
            for part in set_partitions_k(rest, m):
                sMoms = tuple(self.total_k(b) for b in part)
                sOmegas = tuple(self.total_w(b) for b in part)
                vMoms = (k1,) + sMoms
                vOmegas = (w1,) + sOmegas
                v = Vertex(vMoms, vOmegas)
                prod = CR(1, 0)
                for b in part:
                    prod = prod * self.current(b)
                result = result + v*prod
        return result

def make_kinematics(n, freeW, sigmas, g=1):
    """Solve conservation for {w1, wn} given n-2 free freqs and sign vector.
    Mirrors MakeKinematics in OnShellBG.m. Returns (kList, wList) as Fractions."""
    freeW = [Q(x) for x in freeW]
    sigmas = [Q(x) for x in sigmas]
    g = Q(g)
    assert len(freeW) == n-2
    assert sigmas[0] + sigmas[n-1] == 0
    sumFree = sum(freeW)
    sigmaFree = sigmas[1:n-1]
    sumSigmaW2 = sum(s*w*w for s, w in zip(sigmaFree, freeW))
    wn = -(sigmas[0]*sumFree**2 + sumSigmaW2)/(2*sigmas[0]*sumFree)
    w1 = -(sumFree + wn)
    allW = [w1] + freeW + [wn]
    allK = [s*w*w/g for s, w in zip(sigmas, allW)]
    return tuple(allK), tuple(allW)

def two_minus_sigma(n):
    return [Q(-1), Q(-1)] + [Q(1)]*(n-2)

def amp_two_minus(n, freeW, g=1):
    sig = two_minus_sigma(n)
    kL, wL = make_kinematics(n, freeW, sig, g)
    return BG(kL, wL, g).amplitude(), kL, wL

if __name__ == "__main__":
    # validate against Mathematica ground truth
    tests = [
        (5, [Q(2), Q(5,2), Q(3)], "-2304 I"),
        (5, [Q(3,2), Q(11,5), Q(7,3)], "-404919/905 I"),
        (6, [Q(3,2), Q(2), Q(5,2), Q(3)], "-11907/4 I"),
        (6, [Q(2), Q(3), Q(7,2), Q(11,3)], "-6588416/219 I"),
    ]
    for n, fw, expect in tests:
        A, kL, wL = amp_two_minus(n, fw)
        print(f"n={n} free={fw}")
        print(f"   A = {A.re} + {A.im} i   (expect {expect})")
