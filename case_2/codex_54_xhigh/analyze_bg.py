from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations


def F(x):
    return x if isinstance(x, Fraction) else Fraction(x)


def mag(k):
    return abs(k)


@lru_cache(maxsize=None)
def factorial(n: int) -> int:
    out = 1
    for i in range(2, n + 1):
        out *= i
    return out


@lru_cache(maxsize=None)
def ekernel(n, ps):
    if n == 3:
        return -Fraction(1, 2) * (mag(ps[0]) * mag(ps[1]) + ps[0] * ps[1])
    p1, p2 = ps[0], ps[1]
    rest = ps[2:]
    qp2 = mag(p2)
    result = qp2 ** (n - 3) * ekernel(3, (p1, p2, sum(rest, F(0)))) / factorial(n - 2)
    for m in range(1, n - 2):
        moved = p2 + sum(rest[:m], F(0))
        tail = rest[m:]
        result -= qp2**m / factorial(m) * ekernel(n - m, (p1, moved, *tail))
    return result


@lru_cache(maxsize=None)
def fkernel(n, ps):
    if n == 3:
        return -1 - ps[0] * ps[1] / (mag(ps[0]) * mag(ps[1]))
    p1, p2 = ps[0], ps[1]
    rest = ps[2:]
    qp1, qp2 = mag(p1), mag(p2)
    result = 2 * ekernel(n, ps) / qp1
    for m in range(1, n - 2):
        sigm = p2 + sum(rest[:m], F(0))
        left = (-sigm, p2, *rest[:m])
        right = (p1, sigm, *rest[m:])
        result -= 2 * ekernel(m + 2, left) * fkernel(n - m, right)
    return result / qp2


def vertex_coeff(n, moms, omegas):
    result = Fraction(0)
    for p in permutations(range(n)):
        result += omegas[p[0]] * omegas[p[1]] * fkernel(n, tuple(moms[i] for i in p))
    return result


def propagator_coeff(omega, k, g):
    return Fraction(-1, 1) / (omega * omega / mag(k) - g)


def set_partitions(items, k):
    if k == 1:
        return [(items,)]
    if k > len(items):
        return []
    mn = min(items)
    out = []
    others = tuple(i for i in items if i != mn)
    for r in range(0, len(items) - k + 1):
        for sub in combinations(others, r):
            first = tuple(sorted((mn, *sub)))
            rem = tuple(i for i in items if i not in first)
            if len(rem) < k - 1:
                continue
            for sp in set_partitions(rem, k - 1):
                out.append((first, *sp))
    return out


class BG(object):
    def __init__(self, k_list, w_list, g):
        self.k_list = k_list
        self.w_list = w_list
        self.g = g
        self._memo = {}

    def current(self, subset):
        if len(subset) == 1:
            return Fraction(1, 1)
        if subset in self._memo:
            return self._memo[subset]
        omega_s = sum((self.w_list[i] for i in subset), F(0))
        k_s = sum((self.k_list[i] for i in subset), F(0))
        result = Fraction(0, 1)
        for m in range(2, len(subset) + 1):
            for part in set_partitions(subset, m):
                s_moms = [sum((self.k_list[i] for i in block), F(0)) for block in part]
                s_omegas = [sum((self.w_list[i] for i in block), F(0)) for block in part]
                v_moms = [-k_s, *s_moms]
                v_omegas = [-omega_s, *s_omegas]
                prod = Fraction(1, 1)
                for block in part:
                    prod *= self.current(block)
                result += Fraction(-1, 2) * vertex_coeff(m + 1, v_moms, v_omegas) * prod
        result *= -propagator_coeff(omega_s, k_s, self.g)
        self._memo[subset] = result
        return result

    def amplitude_coeff(self):
        n = len(self.k_list)
        rest = tuple(range(1, n))
        result = Fraction(0, 1)
        for m in range(2, n):
            for part in set_partitions(rest, m):
                s_moms = [sum((self.k_list[i] for i in block), F(0)) for block in part]
                s_omegas = [sum((self.w_list[i] for i in block), F(0)) for block in part]
                v_moms = [self.k_list[0], *s_moms]
                v_omegas = [self.w_list[0], *s_omegas]
                prod = Fraction(1, 1)
                for block in part:
                    prod *= self.current(block)
                result += Fraction(-1, 2) * vertex_coeff(m + 1, v_moms, v_omegas) * prod
        return result

    def amplitude(self):
        return complex(0.0, float(self.amplitude_coeff()))


def make_kinematics(free_w, g=1):
    free_w = [F(x) for x in free_w]
    n = len(free_w) + 2
    sigmas = [-1, -1] + [1] * (n - 2)
    sum_free = sum(free_w, F(0))
    sum_sigma_w2 = -free_w[0] ** 2 + sum((x * x for x in free_w[1:]), F(0))
    wn = (sum_sigma_w2 - sum_free ** 2) / (2 * sum_free)
    w1 = -(sum_free + wn)
    all_w = [w1, *free_w, wn]
    all_k = [F(sigmas[i]) * all_w[i] ** 2 / F(g) for i in range(n)]
    return all_k, all_w


def amplitude_from_free(free_w):
    ks, ws = make_kinematics(free_w)
    return BG(tuple(ks), tuple(ws), F(1)).amplitude()


def amplitude_coeff_from_free(free_w):
    ks, ws = make_kinematics(free_w)
    return BG(tuple(ks), tuple(ws), F(1)).amplitude_coeff()


def main():
    samples = [
        [2, 3],
        [2, 3, 4],
        [2, 3, 4, 5],
        [2, 3, 4, 5, 6],
    ]
    for fw in samples:
        amp = amplitude_coeff_from_free(fw)
        print(len(fw) + 2, fw, amp)


if __name__ == "__main__":
    main()
