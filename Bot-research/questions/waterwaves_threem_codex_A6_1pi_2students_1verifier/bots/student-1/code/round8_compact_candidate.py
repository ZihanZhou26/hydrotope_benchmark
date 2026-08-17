#!/usr/bin/env python3
"""Table-free round-8 candidate for the complete three-minus A6 coefficient.

The amplitude convention is

    A6 = i * g**(-3) * stripped_amplitude(omega).

The regular q-wall part is evaluated from two fixed S3 x S3 group sums and
three explicit invariant polynomials.  No chamber coefficient table is read.
"""

from fractions import Fraction
from itertools import combinations, permutations
import argparse


MINUS = (0, 1, 2)
PLUS = (3, 4, 5)
PERMS3 = tuple(permutations(range(3)))


def pos(x):
    return x if x > 0 else Fraction(0, 1)


def h_block(beta2, c2, d2):
    return (
        beta2
        - pos(beta2 - c2)
        - pos(beta2 - d2)
        + pos(beta2 - c2 - d2)
    )


def pole_part(w):
    """Settled nine-channel factorization part P_pole."""
    total = Fraction(0, 1)
    x2 = [z * z for z in w]
    for m in MINUS:
        other_minus = [r for r in MINUS if r != m]
        r, s = other_minus
        for p, q in combinations(PLUS, 2):
            t = next(z for z in PLUS if z not in (p, q))
            Q = x2[p] + x2[q] - x2[m]
            if Q <= 0:
                continue
            d = 2 * (w[m] + w[p]) * (w[m] + w[q])
            if d == 0:
                raise ZeroDivisionError("genuine factorization divisor d_T=0")
            left = h_block(min(x2[m], Q), x2[p], x2[q])
            right = h_block(min(x2[t], Q), x2[r], x2[s])
            total += -64 * w[m] * w[t] * Q**2 * left * right / d
    return total


def r_q_cubic(w):
    """Settled Q-wall orbit R_Q."""
    total = Fraction(0, 1)
    x2 = [z * z for z in w]
    for m in MINUS:
        for p, q in combinations(PLUS, 2):
            t = next(z for z in PLUS if z not in (p, q))
            Q = x2[p] + x2[q] - x2[m]
            total += pos(Q) ** 3 * w[m] * w[t]
    return -32 * total


def H1(a, b, s, v):
    """Degree-six coefficient of the single-hinge full group sum."""
    return 2 * (
        12 * s**6
        - 21 * s**5 * a
        - 22 * s**5 * b
        - 115 * s**4 * v
        - 48 * s**4 * a * b
        - 58 * s**4 * b**2
        + 36 * s**3 * v * a
        + 44 * s**3 * v * b
        + 13 * s**3 * a**3
        + 12 * s**3 * a**2 * b
        - 5 * s**3 * a * b**2
        - 4 * s**3 * b**3
        + 268 * s**2 * v**2
        + 25 * s**2 * v * a**2
        + 308 * s**2 * v * a * b
        + 323 * s**2 * v * b**2
        - 16 * s**2 * a**4
        - 66 * s**2 * a**3 * b
        - 62 * s**2 * a**2 * b**2
        + 30 * s**2 * a * b**3
        + 42 * s**2 * b**4
        + 240 * s * v**2 * a
        + 240 * s * v**2 * b
        - 92 * s * v * a**3
        + 14 * s * v * a**2 * b
        + 328 * s * v * a * b**2
        + 222 * s * v * b**3
        - 64 * s * a**4 * b
        - 212 * s * a**3 * b**2
        - 206 * s * a**2 * b**3
        - 32 * s * a * b**4
        + 26 * s * b**5
        - 8 * v**3
        + 42 * v**2 * a**2
        + 72 * v**2 * a * b
        + 30 * v**2 * b**2
        - 36 * v * a**4
        - 112 * v * a**3 * b
        - 78 * v * a**2 * b**2
        + 36 * v * a * b**3
        + 38 * v * b**4
        + 4 * a**6
        - 44 * a**4 * b**2
        - 112 * a**3 * b**3
        - 112 * a**2 * b**4
        - 40 * a * b**5
    )


def H2(a, b, s, v, c):
    """Degree-four coefficient of the double-hinge matching group sum."""
    return -4 * (
        4 * c * s**2
        + 4 * c * s * a
        + 4 * c * s * b
        + 22 * c * a**2
        + 4 * c * a * b
        - 22 * c * b**2
        + 4 * s**4
        + 4 * s**3 * a
        + 4 * s**3 * b
        - 8 * s**2 * v
        + 12 * s**2 * a**2
        - 16 * s**2 * b**2
        - 8 * s * v * a
        - 8 * s * v * b
        + s * a**3
        - 9 * s * a * b**2
        - 4 * s * b**3
        - 23 * v * a**2
        + 19 * v * b**2
        + 12 * a**4
        + 22 * a**3 * b
        - 12 * a**2 * b**2
        - 22 * a * b**3
    )


def H0(u, v, em, ep):
    """Global dual-S3 degree-eight polynomial R0."""
    return 16 * (
        69 * em**2 * v
        - 126 * em * ep * u**2
        - 18 * em * ep * v
        - 40 * em * u * v**2
        + 42 * ep**2 * u**2
        - 57 * ep**2 * v
        - 52 * ep * u**5
        + 204 * ep * u**3 * v
        - 54 * ep * u * v**2
        + 4 * u**8
        - 32 * u**6 * v
        + 68 * u**4 * v**2
        - 16 * u**2 * v**3
    )


def regular_s(w):
    """Return S=R0+Rq from 9 single-edge and 18 matching terms."""
    rq = Fraction(0, 1)
    for m in MINUS:
        r, s = (j for j in MINUS if j != m)
        env_sum = w[r] + w[s]
        env_product = w[r] * w[s]
        for p in PLUS:
            t, z = (j for j in PLUS if j != p)
            rq += 4 * pos(w[p] ** 2 - w[m] ** 2) * H1(
                w[m], w[p], env_sum, env_product
            )

            for pr, ps in ((t, z), (z, t)):
                rq += (
                    2
                    * pos(w[pr] ** 2 - w[r] ** 2)
                    * pos(w[ps] ** 2 - w[s] ** 2)
                    * H2(
                        w[m],
                        w[p],
                        env_sum,
                        env_product,
                        w[r] * w[pr] + w[s] * w[ps],
                    )
                )

    u = w[0] + w[1] + w[2]
    v = w[0] * w[1] + w[0] * w[2] + w[1] * w[2]
    em = w[0] * w[1] * w[2]
    ep = w[3] * w[4] * w[5]
    return rq + H0(u, v, em, ep)


def stripped_amplitude(w):
    return pole_part(w) + r_q_cubic(w) + regular_s(w)


def parse_fraction(token):
    return Fraction(token)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--omega",
        required=True,
        help="six comma-separated rational frequencies in leg order",
    )
    ap.add_argument("--g", default="1", help="positive rational g")
    args = ap.parse_args()
    w = tuple(parse_fraction(x.strip()) for x in args.omega.split(","))
    if len(w) != 6:
        raise SystemExit("--omega requires exactly six entries")
    g = parse_fraction(args.g)
    value = stripped_amplitude(w) / g**3
    print(value)


if __name__ == "__main__":
    main()
