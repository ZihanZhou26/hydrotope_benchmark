from functools import lru_cache
from fractions import Fraction
from itertools import combinations, permutations
import math


def q(value):
    return value if isinstance(value, Fraction) else Fraction(value)


def cadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def cmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def cscale(a, r):
    return (a[0] * r, a[1] * r)


def cprod(values):
    out = (Fraction(1), Fraction(0))
    for value in values:
        out = cmul(out, value)
    return out


def prod(values):
    out = Fraction(1)
    for value in values:
        out *= value
    return out


@lru_cache(None)
def set_partitions(items, blocks):
    items = tuple(items)
    if blocks == 1:
        return ((items,),)
    if blocks > len(items):
        return ()

    first = min(items)
    rest = tuple(x for x in items if x != first)
    out = []
    for size in range(0, len(items) - blocks + 1):
        for sub in combinations(rest, size):
            head = tuple(sorted((first,) + sub))
            rem = tuple(x for x in items if x not in head)
            if len(rem) >= blocks - 1:
                for tail in set_partitions(rem, blocks - 1):
                    out.append((head,) + tail)
    return tuple(out)


@lru_cache(None)
def e_kernel(ps):
    ps = tuple(q(p) for p in ps)
    n = len(ps)
    if n == 3:
        return -Fraction(1, 2) * (abs(ps[0]) * abs(ps[1]) + ps[0] * ps[1])

    p1, p2 = ps[0], ps[1]
    rest = ps[2:]
    qp2 = abs(p2)
    out = qp2 ** (n - 3) * e_kernel((p1, p2, sum(rest))) / math.factorial(n - 2)
    for m in range(1, n - 2):
        out -= (
            qp2**m
            / math.factorial(m)
            * e_kernel((p1, p2 + sum(rest[:m])) + rest[m:])
        )
    return out


@lru_cache(None)
def f_kernel(ps):
    ps = tuple(q(p) for p in ps)
    n = len(ps)
    if n == 3:
        return -1 - ps[0] * ps[1] / (abs(ps[0]) * abs(ps[1]))

    p1, p2 = ps[0], ps[1]
    rest = ps[2:]
    out = 2 * e_kernel(ps) / abs(p1)
    for m in range(1, n - 2):
        sig_m = p2 + sum(rest[:m])
        out -= 2 * e_kernel((-sig_m, p2) + rest[:m]) * f_kernel(
            (p1, sig_m) + rest[m:]
        )
    return out / abs(p2)


def vertex(momenta, omegas):
    out = Fraction(0)
    n = len(momenta)
    for perm in permutations(range(n)):
        out += omegas[perm[0]] * omegas[perm[1]] * f_kernel(
            tuple(momenta[i] for i in perm)
        )
    return (Fraction(0), -Fraction(1, 2) * out)


def propagator(omega, momentum):
    den = omega * omega / abs(momentum) - 1
    return (Fraction(0), -1 / den)


def bg_amplitude(momenta, omegas):
    momenta = tuple(q(x) for x in momenta)
    omegas = tuple(q(x) for x in omegas)
    n = len(momenta)

    @lru_cache(None)
    def current(subset):
        subset = tuple(subset)
        if len(subset) == 1:
            return (Fraction(1), Fraction(0))

        omega_s = sum(omegas[i] for i in subset)
        momentum_s = sum(momenta[i] for i in subset)
        out = (Fraction(0), Fraction(0))
        for m in range(2, len(subset) + 1):
            for part in set_partitions(subset, m):
                sub_momenta = [sum(momenta[i] for i in block) for block in part]
                sub_omegas = [sum(omegas[i] for i in block) for block in part]
                term = cmul(
                    vertex([-momentum_s] + sub_momenta, [-omega_s] + sub_omegas),
                    cprod(current(block) for block in part),
                )
                out = cadd(out, term)
        return cmul(out, propagator(omega_s, momentum_s))

    rest = tuple(range(1, n))
    out = (Fraction(0), Fraction(0))
    for m in range(2, n):
        for part in set_partitions(rest, m):
            sub_momenta = [sum(momenta[i] for i in block) for block in part]
            sub_omegas = [sum(omegas[i] for i in block) for block in part]
            term = cmul(
                vertex([momenta[0]] + sub_momenta, [omegas[0]] + sub_omegas),
                cprod(current(block) for block in part),
            )
            out = cadd(out, term)
    return out


def make_kinematics(n, free_omegas, sigmas):
    free_omegas = [q(w) for w in free_omegas]
    total_free = sum(free_omegas)
    sum_sigma_w2 = sum(s * w * w for s, w in zip(sigmas[1 : n - 1], free_omegas))
    wn = -(sigmas[0] * total_free * total_free + sum_sigma_w2) / (
        2 * sigmas[0] * total_free
    )
    w1 = -(total_free + wn)
    omegas = [w1] + free_omegas + [wn]
    momenta = [s * w * w for s, w in zip(sigmas, omegas)]
    return momenta, omegas


def two_minus_kinematics(free_omegas):
    n = len(free_omegas) + 2
    return make_kinematics(n, free_omegas, [-1, -1] + [1] * (n - 2))
