from functools import lru_cache
from itertools import permutations, combinations
from math import factorial

import sympy as sp


def set_partitions(items, k):
    if k == 1:
        return ((items,),)
    if k > len(items):
        return ()

    mn = items[0]
    rest = items[1:]
    out = []
    for r in range(len(items) - k + 1):
        for sub in combinations(rest, r):
            first = tuple(sorted((mn,) + sub))
            rem = tuple(x for x in items if x not in first)
            if len(rem) < k - 1:
                continue
            for sparts in set_partitions(rem, k - 1):
                out.append((first,) + sparts)
    return tuple(out)


class ChamberBG:
    def __init__(self, free_symbols, free_values, n):
        self.free_symbols = free_symbols
        self.free_values = free_values
        self.n = n
        assert len(self.free_symbols) == self.n - 2
        assert len(self.free_values) == self.n - 2
        self.sigmas = (-1, -1) + (1,) * (self.n - 2)
        self.free_subs = dict(zip(self.free_symbols, self.free_values))

        free = self.free_symbols
        sum_free = sum(free)
        sum_sigma_w2 = -free[0] ** 2 + sum(x**2 for x in free[1:])
        self.wn = sp.cancel(-(self.sigmas[0] * sum_free**2 + sum_sigma_w2) / (2 * self.sigmas[0] * sum_free))
        self.w1 = sp.cancel(-(sum_free + self.wn))
        self.ws = (self.w1,) + free + (self.wn,)
        self.ks = tuple(sp.cancel(s * w**2) for s, w in zip(self.sigmas, self.ws))

        self.sample_ws = tuple(sp.cancel(w.subs(self.free_subs)) for w in self.ws)
        self.sample_ks = tuple(sp.cancel(k.subs(self.free_subs)) for k in self.ks)

    @lru_cache(maxsize=None)
    def mag(self, expr):
        val = sp.cancel(expr.subs(self.free_subs))
        if val == 0:
            raise ZeroDivisionError(f"sign-ambiguous expression at chamber point: {expr}")
        return expr if sp.sign(val) > 0 else -expr

    @lru_cache(maxsize=None)
    def ekernel(self, n, ps):
        if n == 3:
            return sp.Rational(-1, 2) * (self.mag(ps[0]) * self.mag(ps[1]) + ps[0] * ps[1])
        p1, p2 = ps[0], ps[1]
        rest = ps[2:]
        qp2 = self.mag(p2)
        result = qp2 ** (n - 3) * self.ekernel(3, (p1, p2, sum(rest))) / factorial(n - 2)
        for m in range(1, n - 2):
            merged = p2 + sum(rest[:m])
            tail = rest[m:]
            result -= qp2**m / factorial(m) * self.ekernel(n - m, (p1, merged) + tail)
        return sp.cancel(result)

    @lru_cache(maxsize=None)
    def fkernel(self, n, ps):
        if n == 3:
            return -1 - ps[0] * ps[1] / (self.mag(ps[0]) * self.mag(ps[1]))
        p1, p2 = ps[0], ps[1]
        rest = ps[2:]
        qp1 = self.mag(p1)
        qp2 = self.mag(p2)
        result = 2 * self.ekernel(n, ps) / qp1
        for m in range(1, n - 2):
            sig_m = p2 + sum(rest[:m])
            left = (-sig_m, p2) + rest[:m]
            right = (p1, sig_m) + rest[m:]
            result -= 2 * self.ekernel(m + 2, left) * self.fkernel(n - m, right)
        return sp.cancel(result / qp2)

    @lru_cache(maxsize=None)
    def vertex(self, moms, omegas):
        n = len(moms)
        total = sp.Integer(0)
        for p in permutations(range(n)):
            total += omegas[p[0]] * omegas[p[1]] * self.fkernel(n, tuple(moms[i] for i in p))
        return sp.cancel(-sp.I * total / 2)

    @lru_cache(maxsize=None)
    def propagator(self, omega, k):
        return sp.cancel(-sp.I / (omega**2 / self.mag(k) - 1))

    @lru_cache(maxsize=None)
    def bg_current(self, S):
        if len(S) == 1:
            return sp.Integer(1)

        omega_s = sp.cancel(sum(self.ws[i - 1] for i in S))
        k_s = sp.cancel(sum(self.ks[i - 1] for i in S))
        result = sp.Integer(0)
        for m in range(2, len(S) + 1):
            for part in set_partitions(S, m):
                s_moms = tuple(sp.cancel(sum(self.ks[i - 1] for i in block)) for block in part)
                s_omegas = tuple(sp.cancel(sum(self.ws[i - 1] for i in block)) for block in part)
                v_moms = (-k_s,) + s_moms
                v_omegas = (-omega_s,) + s_omegas
                prod = sp.Integer(1)
                for block in part:
                    prod *= self.bg_current(block)
                result += self.vertex(v_moms, v_omegas) * prod
        return sp.cancel(result * self.propagator(omega_s, k_s))

    def amplitude(self):
        rest = tuple(range(2, self.n + 1))
        result = sp.Integer(0)
        for m in range(2, self.n):
            for part in set_partitions(rest, m):
                s_moms = tuple(sp.cancel(sum(self.ks[i - 1] for i in block)) for block in part)
                s_omegas = tuple(sp.cancel(sum(self.ws[i - 1] for i in block)) for block in part)
                v_moms = (self.ks[0],) + s_moms
                v_omegas = (self.ws[0],) + s_omegas
                prod = sp.Integer(1)
                for block in part:
                    prod *= self.bg_current(block)
                result += self.vertex(v_moms, v_omegas) * prod
        return sp.cancel(result)


def main():
    a, b, c = sp.symbols("a b c")
    bg = ChamberBG((a, b, c), (sp.Rational(4), sp.Rational(3), sp.Rational(2)), 5)
    amp = sp.together(bg.amplitude() / sp.I)
    print("ws =", bg.ws)
    print("amp/I =", sp.factor(amp))


if __name__ == "__main__":
    main()
