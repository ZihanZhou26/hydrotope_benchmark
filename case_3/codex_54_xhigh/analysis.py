import functools
import itertools
import sympy as sp


I = sp.I


def mag(k):
    return abs(k)


@functools.lru_cache(maxsize=None)
def ekernel(ps):
    n = len(ps)
    if n == 3:
        return -sp.Rational(1, 2) * (mag(ps[0]) * mag(ps[1]) + ps[0] * ps[1])

    p1 = ps[0]
    p2 = ps[1]
    rest = ps[2:]
    qp2 = mag(p2)
    result = qp2 ** (n - 3) * ekernel((p1, p2, sum(rest))) / sp.factorial(n - 2)
    for m in range(1, n - 2):
        result -= qp2**m / sp.factorial(m) * ekernel(
            (p1, p2 + sum(rest[:m]), *rest[m:])
        )
    return sp.simplify(result)


@functools.lru_cache(maxsize=None)
def fkernel(ps):
    n = len(ps)
    if n == 3:
        return -1 - ps[0] * ps[1] / (mag(ps[0]) * mag(ps[1]))

    p1 = ps[0]
    p2 = ps[1]
    rest = ps[2:]
    qp1 = mag(p1)
    qp2 = mag(p2)
    result = 2 * ekernel(ps) / qp1
    for m in range(1, n - 2):
        sig_m = p2 + sum(rest[:m])
        left = ekernel((-sig_m, p2, *rest[:m]))
        right = fkernel((p1, sig_m, *rest[m:]))
        result -= 2 * left * right
    return sp.simplify(result / qp2)


@functools.lru_cache(maxsize=None)
def vertex(moms, omegas):
    n = len(moms)
    result = 0
    for perm in itertools.permutations(range(n)):
        result += omegas[perm[0]] * omegas[perm[1]] * fkernel(
            tuple(moms[idx] for idx in perm)
        )
    return sp.simplify((-I / 2) * result)


def propagator(omega, k, g):
    return -I / (omega**2 / mag(k) - g)


@functools.lru_cache(maxsize=None)
def set_partitions(s, k):
    if k == 1:
        return ((s,),)
    if k > len(s):
        return ()

    mn = min(s)
    rest = tuple(x for x in s if x != mn)
    result = []
    for size in range(0, len(s) - k + 1):
        for sub in itertools.combinations(rest, size):
            first_part = tuple(sorted((mn, *sub)))
            remaining = tuple(x for x in s if x not in first_part)
            if len(remaining) >= k - 1:
                for sparts in set_partitions(remaining, k - 1):
                    result.append((first_part, *sparts))
    return tuple(result)


class BGEngine:
    def __init__(self, momenta, omegas, g):
        self.momenta = momenta
        self.omegas = omegas
        self.g = g
        self._bgcurrent_cache = {}

    def bgcurrent(self, s):
        if len(s) == 1:
            return 1
        if s in self._bgcurrent_cache:
            return self._bgcurrent_cache[s]

        omega_s = sum(self.omegas[i - 1] for i in s)
        k_s = sum(self.momenta[i - 1] for i in s)
        result = 0
        for m in range(2, len(s) + 1):
            for part in set_partitions(s, m):
                s_moms = tuple(sum(self.momenta[i - 1] for i in block) for block in part)
                s_omegas = tuple(sum(self.omegas[i - 1] for i in block) for block in part)
                v_moms = (-k_s, *s_moms)
                v_omegas = (-omega_s, *s_omegas)
                prod = 1
                for block in part:
                    prod *= self.bgcurrent(block)
                result += vertex(v_moms, v_omegas) * prod

        result = sp.simplify(result * propagator(omega_s, k_s, self.g))
        self._bgcurrent_cache[s] = result
        return result

    def amplitude(self):
        n = len(self.momenta)
        rest = tuple(range(2, n + 1))
        result = 0
        for m in range(2, n):
            for part in set_partitions(rest, m):
                s_moms = tuple(sum(self.momenta[i - 1] for i in block) for block in part)
                s_omegas = tuple(sum(self.omegas[i - 1] for i in block) for block in part)
                v_moms = (self.momenta[0], *s_moms)
                v_omegas = (self.omegas[0], *s_omegas)
                prod = 1
                for block in part:
                    prod *= self.bgcurrent(block)
                result += vertex(v_moms, v_omegas) * prod
        return sp.simplify(result)


def make_kinematics(n, free_w, sigmas, g=1):
    if len(free_w) != n - 2:
        raise ValueError("need n-2 free frequencies")
    if sigmas[0] + sigmas[-1] != 0:
        raise ValueError("need sigma_1 + sigma_n = 0")

    free_w = [sp.nsimplify(w) for w in free_w]
    sum_free = sum(free_w)
    sigma_free = sigmas[1 : n - 1]
    sum_sigma_w2 = sum(s * w**2 for s, w in zip(sigma_free, free_w))
    wn = -(sigmas[0] * sum_free**2 + sum_sigma_w2) / (2 * sigmas[0] * sum_free)
    w1 = -(sum_free + wn)
    all_w = (sp.simplify(w1), *(sp.simplify(w) for w in free_w), sp.simplify(wn))
    all_k = tuple(sp.simplify(s * w**2 / g) for s, w in zip(sigmas, all_w))
    return all_k, all_w


def two_minus_sigmas(n):
    return [-1, -1] + [1] * (n - 2)


def amplitude_two_minus(n, free_w, g=1):
    sigmas = two_minus_sigmas(n)
    ks, ws = make_kinematics(n, free_w, sigmas, g)
    amp = BGEngine(ks, ws, g).amplitude()
    return ws, sp.simplify(amp)


def demo():
    cases = {
        4: [[sp.Rational(2), sp.Rational(3)]],
        5: [[sp.Rational(2), sp.Rational(5, 2), sp.Rational(3)]],
        6: [[sp.Rational(3, 2), sp.Rational(2), sp.Rational(5, 2), sp.Rational(3)]],
    }
    for n, free_ws in cases.items():
        print(f"n = {n}")
        for free_w in free_ws:
            ws, amp = amplitude_two_minus(n, free_w)
            print("  free_w =", free_w)
            print("  ws     =", ws)
            print("  amp    =", sp.simplify(amp))
            print("  amp/I  =", sp.simplify(amp / I))


if __name__ == "__main__":
    demo()
