#!/usr/bin/env python3
"""Symbolic Berends-Giele engine (sympy), a faithful transcription of bg.cpp.

Every absR(expr) (an absolute value of a momentum partial sum) is resolved to
sgn*expr, where sgn is the sign of expr at a fixed reference point omega* that
lies in the interior of a chosen kinematic chamber. The result is the EXACT
symbolic amplitude valid on that chamber (the propagator denominators D_S cancel
because the three-minus sector is pole-free -- verified numerically).

Run with on-shell omega (Sum w=0, Sum sigma w^2 = 0) substituted to compare to
./bg, or keep symbolic to read off the per-chamber polynomial.
"""
import sympy as sp
from functools import lru_cache
from itertools import permutations

# --- set partitions of S into exactly k blocks (index-only) ---
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


class SymEngine:
    """Mirrors Engine<R> in bg.cpp. K, W are 1-indexed dicts of sympy exprs.
    sgn(expr) returns +1/-1 by evaluating at the reference point self.ref."""
    def __init__(self, K, W, ref, G=1):
        self.K = K  # dict 1..N -> sympy expr (momentum)
        self.W = W  # dict 1..N -> sympy expr (freq)
        self.N = len(W)
        self.ref = ref  # dict symbol->rational for sign evaluation
        self.G = sp.Integer(G)
        self._Em = {}
        self._Fm = {}
        self._BG = {}

    def sgn(self, expr):
        v = sp.nsimplify(expr.subs(self.ref)) if not expr.is_number else expr
        v = sp.simplify(expr.subs(self.ref))
        if v == 0:
            raise ValueError(f"sign of zero at reference (on a wall): {expr}")
        return sp.Integer(1) if v > 0 else sp.Integer(-1)

    def absR(self, expr):
        return self.sgn(expr) * expr

    def fact(self, k):
        return sp.factorial(k)

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
        res = qp2 ** (n - 3) * self.EKernel(3, (p1, p2, rs)) / self.fact(n - 2)
        for m in range(1, n - 2):
            part = sum(rest[:m])
            nl = [p1, p2 + part] + rest[m:]
            res = res - qp2 ** m / self.fact(m) * self.EKernel(n - m, nl)
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
        res = res / qp2
        self._Fm[key] = res
        return res

    def Vertex(self, n, moms, om):
        # returns the imaginary coefficient acc, with Vertex = (0, -acc/2) as (re,im)
        acc = sp.Integer(0)
        idx = list(range(n))
        for p in permutations(idx):
            pm = [moms[i] for i in p]
            acc = acc + om[p[0]] * om[p[1]] * self.FKernel(n, pm)
        return (sp.Integer(0), -acc / 2)

    def Propagator(self, wS, kS):
        D = wS * wS / self.absR(kS) - self.G
        return (sp.Integer(0), sp.Integer(-1) / D)

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
        return result


def build_engine(omega_vals_or_syms, signs, ref):
    """omega: dict 1..N -> sympy expr. signs: list of +-1 (0-indexed)."""
    W = omega_vals_or_syms
    K = {i: sp.Integer(signs[i - 1]) * W[i] ** 2 for i in W}  # g=1
    return SymEngine(K, W, ref)


if __name__ == "__main__":
    # VALIDATION: numeric on-shell point vs oracle (n=5 then n=6)
    import harness as h
    from fractions import Fraction as F

    for free, signs, label in [
        ([F(2), F(3), F(5)], [-1, -1, -1, 1, 1], "n=5"),
        ([F(2), F(3), F(5), F(7)], [-1, -1, -1, 1, 1, 1], "n=6"),
    ]:
        oms = h.solve_legs_1n(free, signs)
        N = len(signs)
        ref = {sp.Symbol(f"w{i+1}"): sp.Rational(oms[i].numerator, oms[i].denominator)
               for i in range(N)}
        Wnum = {i + 1: sp.Rational(oms[i].numerator, oms[i].denominator) for i in range(N)}
        E = build_engine(Wnum, signs, ref)
        re, im = E.BGAmplitude()
        im = sp.simplify(im)
        oim, _, _ = h.on_shell(free, signs)
        print(f"{label}: sym A={im}  oracle={oim}  match={sp.Rational(oim.numerator,oim.denominator)==im}")
