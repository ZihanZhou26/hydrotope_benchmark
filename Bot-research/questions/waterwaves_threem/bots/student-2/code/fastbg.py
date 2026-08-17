#!/usr/bin/env python3
"""Fast EXACT in-process Berends-Giele evaluator: pure-Fraction port of bg.cpp.
No subprocess, no sympy -> thousands of exact on-shell amplitudes per second.

Validated against ./bg in __main__. Amplitudes are (re,im) Fractions; in the
three-minus sector re==0 and we return im (= A_n/i).
"""
from fractions import Fraction as F
from functools import lru_cache

def absR(x): return x if x >= 0 else -x

class BG:
    def __init__(self, K, W, G=F(1)):
        self.K = K  # dict 1..N -> Fraction (momentum)
        self.W = W  # dict 1..N -> Fraction (frequency)
        self.N = len(W)
        self.G = F(G)
        self._E = {}
        self._F = {}
        self._BG = {}

    # set partitions of S into exactly k blocks
    def set_partitions(self, S, k):
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
                for spp in self.set_partitions(rem, k - 1):
                    out.append([tuple(sorted(fp))] + spp)
        return out

    def fact(self, k):
        r = F(1)
        for i in range(2, k + 1):
            r *= i
        return r

    def EKernel(self, n, ps):
        if n == 3:
            return F(-1, 2) * (absR(ps[0]) * absR(ps[1]) + ps[0] * ps[1])
        key = (n, ps)
        if key in self._E:
            return self._E[key]
        p1, p2 = ps[0], ps[1]
        rest = list(ps[2:])
        qp2 = absR(p2)
        rs = sum(rest)
        res = qp2 ** (n - 3) * self.EKernel(3, (p1, p2, rs)) / self.fact(n - 2)
        for m in range(1, n - 2):
            part = sum(rest[:m])
            nl = (p1, p2 + part) + tuple(rest[m:])
            res = res - qp2 ** m / self.fact(m) * self.EKernel(n - m, nl)
        self._E[key] = res
        return res

    def FKernel(self, n, ps):
        if n == 3:
            return F(-1) - ps[0] * ps[1] / (absR(ps[0]) * absR(ps[1]))
        key = (n, ps)
        if key in self._F:
            return self._F[key]
        p1, p2 = ps[0], ps[1]
        rest = list(ps[2:])
        qp1, qp2 = absR(p1), absR(p2)
        res = F(2) * self.EKernel(n, ps) / qp1
        for m in range(1, n - 2):
            part = sum(rest[:m])
            sigM = p2 + part
            el = (-sigM, p2) + tuple(rest[:m])
            fl = (p1, sigM) + tuple(rest[m:])
            res = res - F(2) * self.EKernel(m + 2, el) * self.FKernel(n - m, fl)
        res = res / qp2
        self._F[key] = res
        return res

    def Vertex(self, n, moms, om):
        from itertools import permutations
        acc = F(0)
        for p in permutations(range(n)):
            pm = tuple(moms[i] for i in p)
            acc += om[p[0]] * om[p[1]] * self.FKernel(n, pm)
        return (F(0), -acc / 2)

    def Propagator(self, wS, kS):
        D = wS * wS / absR(kS) - self.G
        return (F(0), F(-1) / D)

    @staticmethod
    def cadd(a, b): return (a[0] + b[0], a[1] + b[1])
    @staticmethod
    def cmul(a, b): return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])

    def BGCurrent(self, S):
        S = tuple(sorted(S))
        if len(S) == 1:
            return (F(1), F(0))
        if S in self._BG:
            return self._BG[S]
        wS = sum(self.W[i] for i in S)
        kS = sum(self.K[i] for i in S)
        result = (F(0), F(0))
        for m in range(2, len(S) + 1):
            for part in self.set_partitions(S, m):
                vM = [-kS] + [sum(self.K[i] for i in blk) for blk in part]
                vO = [-wS] + [sum(self.W[i] for i in blk) for blk in part]
                v = self.Vertex(m + 1, vM, vO)
                prod = (F(1), F(0))
                for blk in part:
                    prod = self.cmul(prod, self.BGCurrent(blk))
                result = self.cadd(result, self.cmul(v, prod))
        result = self.cmul(result, self.Propagator(wS, kS))
        self._BG[S] = result
        return result

    def amplitude(self):
        N = self.N
        rest = tuple(range(2, N + 1))
        result = (F(0), F(0))
        for m in range(2, N):
            for part in self.set_partitions(rest, m):
                vM = [self.K[1]] + [sum(self.K[i] for i in blk) for blk in part]
                vO = [self.W[1]] + [sum(self.W[i] for i in blk) for blk in part]
                v = self.Vertex(m + 1, vM, vO)
                prod = (F(1), F(0))
                for blk in part:
                    prod = self.cmul(prod, self.BGCurrent(blk))
                result = self.cadd(result, self.cmul(v, prod))
        return result


SIGN = {}  # cache


def solve_legs(free, signs, g=F(1)):
    """free = n-2 Fractions (legs 2..n-1); return full omega list len n (Fractions)."""
    free = [F(x) for x in free]
    n = len(signs)
    s1 = F(signs[0])
    sumFree = sum(free)
    sumSig = sum(F(signs[i + 1]) * free[i] * free[i] for i in range(n - 2))
    wn = -(s1 * sumFree * sumFree + sumSig) / (2 * s1 * sumFree)
    w1 = -(sumFree + wn)
    return [w1] + free + [wn]


def A_over_i(free, signs, g=F(1)):
    """On-shell A_n/i for free freqs (legs 2..n-1). Returns Fraction; raises on wall."""
    oms = solve_legs(free, signs, g)
    n = len(signs)
    W = {i + 1: oms[i] for i in range(n)}
    K = {i + 1: F(signs[i]) * oms[i] * oms[i] / g for i in range(n)}
    bg = BG(K, W, g)
    re, im = bg.amplitude()
    assert re == 0, f"nonzero re {re}"
    return im, oms


def A_over_i_raw(K, W, g=F(1)):
    n = len(W)
    Wd = {i + 1: F(W[i]) for i in range(n)}
    Kd = {i + 1: F(K[i]) for i in range(n)}
    bg = BG(Kd, Wd, g)
    re, im = bg.amplitude()
    return re, im


if __name__ == "__main__":
    import time, harness as h
    tests = [([2,3,5],[-1,-1,-1,1,1]),
             ([2,3,5,7],[-1,-1,-1,1,1,1]),
             ([2,3,5,7,11],[-1,-1,-1,1,1,1,1])]
    for free, signs in tests:
        im, oms = A_over_i([F(x) for x in free], signs)
        im_o, _, _ = h.on_shell(free, signs)
        print(f"n={len(signs)}: fast={im}  oracle={im_o}  match={im==F(im_o)}")
    # speed
    t0 = time.time(); cnt = 0
    import random; random.seed(1)
    for _ in range(200):
        free = [F(random.randint(-9,9), random.randint(1,7)) for _ in range(4)]
        if sum(free) == 0: continue
        try:
            A_over_i(free, [-1,-1,-1,1,1,1]); cnt += 1
        except Exception: pass
    print(f"n=6: {cnt} exact evals in {time.time()-t0:.2f}s")
