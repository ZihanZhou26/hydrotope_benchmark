#!/usr/bin/env python3
"""Fast symbolic BG engine for ONE chamber on an F-constant slice.

Speed fixes vs symbolic_bg.py:
  - sgn(expr) evaluates expr at the numeric reference as a float (no sp.simplify).
  - We use an F-constant slice (w4=a+t, w5=b-t, ...) so sumFree is constant and the
    on-shell-solved legs 1,n are POLYNOMIALS in t (no denominators); every K_i is a
    polynomial in t. Final A_n(t) is rational in t with only the matching poles.

Returns A_n(t)/i as an exact sympy rational function of t (and the omega_i(t)).
"""
import sympy as sp
from itertools import permutations

t = sp.Symbol('t')


def set_partitions(S, k):
    S = list(S)
    if k == 1:
        return [[tuple(S)]]
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
                out.append([tuple(sorted(fp))] + sp_)
    return out


class FastEngine:
    def __init__(self, K, W, refval, G=1):
        self.K = K            # dict 1..N -> sympy poly in t
        self.W = W
        self.N = len(W)
        self.refval = refval  # numeric value of t in the chamber interior
        self.G = sp.Integer(G)
        self._Em = {}
        self._Fm = {}
        self._BG = {}

    def sgn(self, expr):
        v = float(expr.subs(t, self.refval))
        if abs(v) < 1e-12:
            raise ValueError(f"sign ~0 at ref (wall): {expr} -> {v}")
        return sp.Integer(1) if v > 0 else sp.Integer(-1)

    def absR(self, expr):
        return self.sgn(expr) * expr

    def EKernel(self, n, ps):
        ps = tuple(ps)
        if n == 3:
            return sp.Rational(-1, 2) * (self.absR(ps[0]) * self.absR(ps[1]) + ps[0] * ps[1])
        key = (n, ps)
        if key in self._Em:
            return self._Em[key]
        p1, p2 = ps[0], ps[1]
        rest = list(ps[2:])
        qp2 = self.absR(p2)
        rs = sum(rest)
        res = qp2 ** (n - 3) * self.EKernel(3, (p1, p2, rs)) / sp.factorial(n - 2)
        for m in range(1, n - 2):
            part = sum(rest[:m])
            nl = [p1, p2 + part] + rest[m:]
            res = res - qp2 ** m / sp.factorial(m) * self.EKernel(n - m, nl)
        res = sp.expand(res)
        self._Em[key] = res
        return res

    def FKernel(self, n, ps):
        ps = tuple(ps)
        if n == 3:
            return sp.Integer(-1) - ps[0] * ps[1] / (self.absR(ps[0]) * self.absR(ps[1]))
        key = (n, ps)
        if key in self._Fm:
            return self._Fm[key]
        p1, p2 = ps[0], ps[1]
        rest = list(ps[2:])
        qp1, qp2 = self.absR(p1), self.absR(p2)
        res = sp.Integer(2) * self.EKernel(n, ps) / qp1
        for m in range(1, n - 2):
            part = sum(rest[:m])
            sigM = p2 + part
            el = [-sigM, p2] + rest[:m]
            fl = [p1, sigM] + rest[m:]
            res = res - sp.Integer(2) * self.EKernel(m + 2, el) * self.FKernel(n - m, fl)
        res = sp.cancel(res / qp2)
        self._Fm[key] = res
        return res

    def Vertex(self, n, moms, om):
        acc = sp.Integer(0)
        idx = list(range(n))
        for p in permutations(idx):
            pm = [moms[i] for i in p]
            acc = acc + om[p[0]] * om[p[1]] * self.FKernel(n, pm)
        return (sp.Integer(0), sp.cancel(-acc / 2))

    def Propagator(self, wS, kS):
        D = wS * wS / self.absR(kS) - self.G
        return (sp.Integer(0), sp.cancel(sp.Integer(-1) / D))

    @staticmethod
    def cadd(a, b):
        return (a[0] + b[0], a[1] + b[1])

    @staticmethod
    def cmul(a, b):
        return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])

    def BGCurrent(self, S):
        S = tuple(sorted(S))
        if len(S) == 1:
            return (sp.Integer(1), sp.Integer(0))
        if S in self._BG:
            return self._BG[S]
        wS = sum(self.W[i] for i in S)
        kS = sum(self.K[i] for i in S)
        result = (sp.Integer(0), sp.Integer(0))
        for m in range(2, len(S) + 1):
            for part in set_partitions(S, m):
                vM = [-kS] + [sum(self.K[i] for i in blk) for blk in part]
                vO = [-wS] + [sum(self.W[i] for i in blk) for blk in part]
                v = self.Vertex(m + 1, vM, vO)
                prod = (sp.Integer(1), sp.Integer(0))
                for blk in part:
                    prod = self.cmul(prod, self.BGCurrent(blk))
                result = self.cadd(result, self.cmul(v, prod))
        result = self.cmul(result, self.Propagator(wS, kS))
        result = (sp.cancel(result[0]), sp.cancel(result[1]))
        self._BG[S] = result
        return result

    def BGAmplitude(self):
        N = self.N
        rest = tuple(range(2, N + 1))
        result = (sp.Integer(0), sp.Integer(0))
        for m in range(2, N):
            for part in set_partitions(rest, m):
                vM = [self.K[1]] + [sum(self.K[i] for i in blk) for blk in part]
                vO = [self.W[1]] + [sum(self.W[i] for i in blk) for blk in part]
                v = self.Vertex(m + 1, vM, vO)
                prod = (sp.Integer(1), sp.Integer(0))
                for blk in part:
                    prod = self.cmul(prod, self.BGCurrent(blk))
                result = self.cadd(result, self.cmul(v, prod))
        return (sp.cancel(result[0]), sp.cancel(result[1]))


def slice_engine(w2, w3, a, b, refval, signs=(-1, -1, -1, 1, 1, 1)):
    """F-const slice: w2,w3 fixed (minus); w4=a+t, w5=b-t (plus); legs 1,6 solved.
    Returns engine with W,K as polynomials in t."""
    w2, w3, a, b = map(sp.Rational, (w2, w3, a, b))
    w4 = a + t
    w5 = b - t
    sumFree = w2 + w3 + w4 + w5            # constant (= w2+w3+a+b)
    s1 = sp.Integer(signs[0])
    sumSig = (sp.Integer(signs[1]) * w2**2 + sp.Integer(signs[2]) * w3**2
              + sp.Integer(signs[3]) * w4**2 + sp.Integer(signs[4]) * w5**2)
    w6 = sp.expand(-(s1 * sumFree**2 + sumSig) / (2 * s1 * sumFree))
    w1 = sp.expand(-(sumFree + w6))
    W = {1: w1, 2: w2, 3: w3, 4: w4, 5: w5, 6: w6}
    K = {i: sp.Integer(signs[i - 1]) * W[i]**2 for i in W}
    return FastEngine(K, W, sp.Rational(refval)), W


if __name__ == "__main__":
    import time
    # chamber-1 reference, slice through interior at t=0 (w4=5,w5=7)
    E, W = slice_engine(2, 3, 5, 7, 0)
    t0 = time.time()
    re, im = E.BGAmplitude()
    print(f"BG took {time.time()-t0:.1f}s")
    A = sp.cancel(im)
    print("A_6(t)/i =", A)
    print("factored:", sp.factor(A))
    # check vs oracle at t=0: should be -29948208/17
    print("at t=0:", A.subs(t, 0))
