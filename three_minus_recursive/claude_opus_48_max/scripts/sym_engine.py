"""sym_engine.py — faithful sympy port of bg.cpp's Berends-Giele engine.

Absolute values |x| are resolved by the SIGN of x at a reference numeric point
(exact Rational), which selects a kinematic chamber. The resulting symbolic
amplitude is valid throughout that chamber. Validate against bg.cpp before trust.

Usage: build Engine(W_syms, sigma, ref) where W_syms are sympy exprs for the n
frequencies, sigma the n signs, ref a dict {symbol: Rational} for sign resolution.
K_i = sigma_i * W_i**2 / g.
"""
import sympy as sp
from itertools import permutations
from functools import lru_cache

I = sp.I


def set_partitions(S, k):
    """All partitions of list S into exactly k nonempty blocks (index lists)."""
    S = list(S)
    if k == 1:
        return [[S]]
    if k > len(S):
        return []
    mn = min(S)
    X = [x for x in S if x != mn]
    L, xs = len(S), len(X)
    out = []
    for mask in range(1 << xs):
        if bin(mask).count("1") > L - k:
            continue
        fp = [mn] + [X[b] for b in range(xs) if mask & (1 << b)]
        fps = set(fp)
        rem = [v for v in S if v not in fps]
        if len(rem) >= k - 1:
            for sp_ in set_partitions(rem, k - 1):
                out.append([sorted(fp)] + sp_)
    return out


class SymEngine:
    def __init__(self, W, sigma, ref, g=1):
        self.n = len(W)
        self.W = [None] + [sp.sympify(w) for w in W]      # 1-indexed
        self.G = sp.sympify(g)
        self.sigma = [None] + list(sigma)
        self.K = [None] + [sp.sympify(sigma[i]) * self.W[i + 1] ** 2 / self.G
                           for i in range(self.n)]
        self.ref = {sp.sympify(k): sp.Rational(v) for k, v in ref.items()}
        self.Em, self.Fm, self.BGm = {}, {}, {}

    NORM = staticmethod(sp.cancel)   # normalizer: cancel keeps rational fns reduced

    def _abs(self, x):
        val = sp.Rational(sp.nsimplify(x.subs(self.ref))) if not x.subs(self.ref).is_number \
              else sp.Rational(x.subs(self.ref))
        s = sp.sign(val)
        if s == 0:
            raise ValueError(f"abs argument vanishes at reference point: {x}")
        return x if s > 0 else -x

    def _key(self, n, ps):
        return (n,) + tuple(sp.srepr(self.NORM(p)) for p in ps)

    def EKernel(self, n, ps):
        if n == 3:
            return sp.Rational(-1, 2) * (self._abs(ps[0]) * self._abs(ps[1]) + ps[0] * ps[1])
        key = self._key(n, ps)
        if key in self.Em:
            return self.Em[key]
        p1, p2, rest = ps[0], ps[1], ps[2:]
        qp2 = self._abs(p2)
        rs = sum(rest)
        res = qp2 ** (n - 3) * self.EKernel(3, [p1, p2, rs]) / sp.factorial(n - 2)
        for m in range(1, n - 2):
            part = sum(rest[:m])
            nl = [p1, p2 + part] + list(rest[m:])
            res = res - qp2 ** m / sp.factorial(m) * self.EKernel(n - m, nl)
        res = self.NORM(res)
        self.Em[key] = res
        return res

    def FKernel(self, n, ps):
        if n == 3:
            return -1 - ps[0] * ps[1] / (self._abs(ps[0]) * self._abs(ps[1]))
        key = self._key(n, ps)
        if key in self.Fm:
            return self.Fm[key]
        p1, p2, rest = ps[0], ps[1], ps[2:]
        qp1, qp2 = self._abs(p1), self._abs(p2)
        res = 2 * self.EKernel(n, ps) / qp1
        for m in range(1, n - 2):
            part = sum(rest[:m])
            sigM = p2 + part
            el = [-sigM, p2] + list(rest[:m])
            fl = [p1, sigM] + list(rest[m:])
            res = res - 2 * self.EKernel(m + 2, el) * self.FKernel(n - m, fl)
        res = self.NORM(res / qp2)
        self.Fm[key] = res
        return res

    def Vertex(self, n, moms, om):
        acc = 0
        idx = list(range(n))
        for p in permutations(idx):
            pm = [moms[i] for i in p]
            acc = acc + om[p[0]] * om[p[1]] * self.FKernel(n, pm)
        return -I * acc / 2   # (-i/2)*acc

    def Propagator(self, wS, kS):
        D = wS ** 2 / self._abs(kS) - self.G
        return -I / D

    def BGCurrent(self, S):
        S = tuple(sorted(S))
        if len(S) == 1:
            return sp.Integer(1)
        if S in self.BGm:
            return self.BGm[S]
        wS = sum(self.W[i] for i in S)
        kS = sum(self.K[i] for i in S)
        result = 0
        for m in range(2, len(S) + 1):
            for part in set_partitions(list(S), m):
                vM = [-kS] + [sum(self.K[i] for i in blk) for blk in part]
                vO = [-wS] + [sum(self.W[i] for i in blk) for blk in part]
                v = self.Vertex(m + 1, vM, vO)
                prod = 1
                for blk in part:
                    prod = prod * self.BGCurrent(blk)
                result = result + v * prod
        result = self.NORM(result * self.Propagator(wS, kS))
        self.BGm[S] = result
        return result

    def BGAmplitude(self):
        N = self.n
        rest = list(range(2, N + 1))
        result = 0
        for m in range(2, N):
            for part in set_partitions(rest, m):
                vM = [self.K[1]] + [sum(self.K[i] for i in blk) for blk in part]
                vO = [self.W[1]] + [sum(self.W[i] for i in blk) for blk in part]
                v = self.Vertex(m + 1, vM, vO)
                prod = 1
                for blk in part:
                    prod = prod * self.BGCurrent(blk)
                result = result + v * prod
        return self.NORM(result)


def amp_symbolic(W, sigma, ref, g=1):
    """Return A (sympy) for frequencies W (exprs), sigma, chamber ref point."""
    eng = SymEngine(W, sigma, ref, g=g)
    return eng.BGAmplitude()
