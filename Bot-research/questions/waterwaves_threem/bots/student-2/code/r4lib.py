#!/usr/bin/env python3
"""Round-4 shared utilities (student-2). Exact-rational throughout.

Conventions (PI-verified, board posts 7-9):
  A_n^{3-} = i * 2^{n-1} * g^{3-n} * N_n(omega) / D_n(omega),
  D_n = prod_{i in minus={1,2,3}} prod_{j in plus={4..n}} (omega_i + omega_j),
  N_n piecewise-polynomial spline, deg 5n-13, S_3 wr Z_2-symmetric, odd under omega->-omega.

We work with g=1 (homogeneity restores g^{3-n}). The oracle returns A_n = i*(im),
so A_n/i = im, and N_n = im * D_n / 2^{n-1}.
"""
import os, itertools
from fractions import Fraction as F
import harness as h

MINUS = (1, 2, 3)            # leg indices (1-based) carrying sigma=-1


def plus_legs(n):
    return tuple(range(4, n + 1))


def Dn(omega):
    """D_n = prod over mixed pairs (omega_i + omega_j), omega is 1-based dict or
    0-based list of all n frequencies."""
    n = len(omega)
    w = {i + 1: F(omega[i]) for i in range(n)} if isinstance(omega, (list, tuple)) else omega
    d = F(1)
    for i in MINUS:
        for j in plus_legs(n):
            d *= (w[i] + w[j])
    return d


def Nn_value(free, signs, double=False):
    """Return (N_n value, omegas, im) at an on-shell point given by free freqs.
    N_n = (A_n/i) * D_n / 2^{n-1}."""
    im, oms, re_p = h.on_shell(free, signs, double=double)
    assert (re_p == 0) or abs(re_p) < 1e-9, f"nonzero real part {re_p}"
    n = len(signs)
    d = Dn(oms)
    N = F(im) * d / F(2 ** (n - 1))
    return N, oms, im


def amp_value(free, signs, double=False):
    im, oms, re_p = h.on_shell(free, signs, double=double)
    return im, oms


def threeminus_signs(n):
    return [-1, -1, -1] + [1] * (n - 3)


if __name__ == "__main__":
    # sanity: N_6 at a generic point should be an exact rational; print it.
    for free, n in [([2, 3, 5], 5), ([2, 3, 5, 7], 6), ([2, 3, 5, 7, 11], 7)]:
        signs = threeminus_signs(n)
        N, oms, im = Nn_value([F(x) for x in free], signs)
        print(f"n={n}: A/i={im}")
        print(f"       omega={[str(o) for o in oms]}")
        print(f"       D_n={Dn(oms)}")
        print(f"       N_n={N}  (is_integer={N.denominator==1})")
