from functools import lru_cache
from itertools import combinations, permutations
import math


def prod(values):
    out = 1
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


def key(ps):
    return tuple(round(float(p), 13) for p in ps)


@lru_cache(None)
def e_kernel(ps):
    ps = list(ps)
    n = len(ps)
    if n == 3:
        return -0.5 * (abs(ps[0]) * abs(ps[1]) + ps[0] * ps[1])

    p1, p2 = ps[0], ps[1]
    rest = ps[2:]
    qp2 = abs(p2)
    out = qp2 ** (n - 3) * e_kernel(key([p1, p2, sum(rest)])) / math.factorial(n - 2)
    for m in range(1, n - 2):
        out -= (
            qp2**m
            / math.factorial(m)
            * e_kernel(key([p1, p2 + sum(rest[:m])] + rest[m:]))
        )
    return out


@lru_cache(None)
def f_kernel(ps):
    ps = list(ps)
    n = len(ps)
    if n == 3:
        return -1.0 - ps[0] * ps[1] / (abs(ps[0]) * abs(ps[1]))

    p1, p2 = ps[0], ps[1]
    rest = ps[2:]
    out = 2.0 * e_kernel(key(ps)) / abs(p1)
    for m in range(1, n - 2):
        sig_m = p2 + sum(rest[:m])
        out -= 2.0 * e_kernel(key([-sig_m, p2] + rest[:m])) * f_kernel(
            key([p1, sig_m] + rest[m:])
        )
    return out / abs(p2)


def vertex(momenta, omegas):
    out = 0.0
    n = len(momenta)
    for perm in permutations(range(n)):
        out += omegas[perm[0]] * omegas[perm[1]] * f_kernel(key(momenta[i] for i in perm))
    return -0.5j * out


def propagator(omega, momentum, g=1.0):
    return -1j / (omega * omega / abs(momentum) - g)


def bg_amplitude(momenta, omegas, g=1.0):
    momenta = tuple(float(x) for x in momenta)
    omegas = tuple(float(x) for x in omegas)
    n = len(momenta)

    @lru_cache(None)
    def current(subset):
        subset = tuple(subset)
        if len(subset) == 1:
            return 1.0 + 0.0j

        omega_s = sum(omegas[i] for i in subset)
        momentum_s = sum(momenta[i] for i in subset)
        out = 0.0j
        for m in range(2, len(subset) + 1):
            for part in set_partitions(subset, m):
                sub_momenta = [sum(momenta[i] for i in block) for block in part]
                sub_omegas = [sum(omegas[i] for i in block) for block in part]
                out += vertex([-momentum_s] + sub_momenta, [-omega_s] + sub_omegas) * prod(
                    current(block) for block in part
                )
        return out * propagator(omega_s, momentum_s, g)

    rest = tuple(range(1, n))
    out = 0.0j
    for m in range(2, n):
        for part in set_partitions(rest, m):
            sub_momenta = [sum(momenta[i] for i in block) for block in part]
            sub_omegas = [sum(omegas[i] for i in block) for block in part]
            out += vertex([momenta[0]] + sub_momenta, [omegas[0]] + sub_omegas) * prod(
                current(block) for block in part
            )
    return out


def make_kinematics(n, free_omegas, sigmas, g=1.0):
    total_free = sum(free_omegas)
    sigma_free = sigmas[1 : n - 1]
    sum_sigma_w2 = sum(s * w * w for s, w in zip(sigma_free, free_omegas))
    wn = -(sigmas[0] * total_free * total_free + sum_sigma_w2) / (
        2.0 * sigmas[0] * total_free
    )
    w1 = -(total_free + wn)
    omegas = [w1] + list(free_omegas) + [wn]
    momenta = [s * w * w / g for s, w in zip(sigmas, omegas)]
    return momenta, omegas


def two_minus_kinematics(free_omegas):
    n = len(free_omegas) + 2
    return make_kinematics(n, free_omegas, [-1, -1] + [1] * (n - 2))
