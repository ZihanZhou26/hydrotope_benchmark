#!/usr/bin/env python3
"""Soft-limit probe: as a free PLUS leg omega_5 -> 0, the n=6 three-minus config
degenerates to an n=5 three-minus config (legs 1,2,3 minus; 4,6 plus). Study
A_6 as omega_5 -> 0 and compare to the known A_5.

We fix free legs 2,3,4 and let omega_5 = eps -> 0 (legs 1,6 solved each eps).
Print A_6(eps), and the leading behavior / ratio to powers of eps, and the
n=5 value at the limit configuration.
"""
from fractions import Fraction as F
import harness as h
import itertools

SIG6 = [-1, -1, -1, 1, 1, 1]
SIG5 = [-1, -1, -1, 1, 1]


def A5_threeminus(w1, w2, w3, w4, w5):
    """known n=5 closed form C_5 = i 2^4 g^-2 w4 w5 sum_{S subset {1,2,3}}(-1)^|S|(min(w4^2,w5^2)-sum_S)_+^2
    Here legs 4,5 are the two plus legs. Returns imaginary coeff A_5/i."""
    m = min(w4**2, w5**2)
    tot = F(0)
    legs = [w1, w2, w3]
    for r in range(4):
        for S in itertools.combinations(range(3), r):
            c = sum(legs[i]**2 for i in S)
            v = m - c
            if v > 0:
                tot += F((-1)**r) * v**2
    return 16 * w4 * w5 * tot


if __name__ == "__main__":
    base = [F(3), F(5), F(4)]  # legs 2,3,4 fixed
    print("eps=w5 -> 0:  A_6/i,   A_6/(i*eps),  A_6/(i*eps^2)")
    for k in range(1, 8):
        eps = F(1, 2**k)
        free = [base[0], base[1], base[2], eps]   # legs 2,3,4,5
        try:
            im6, om6, _ = h.on_shell(free, SIG6)
        except Exception:
            print(f"eps={eps}: SIGFPE"); continue
        print(f" eps={float(eps):.5f}: A6/i={float(im6):.6g}   /eps={float(im6/eps):.6g}   /eps^2={float(im6/eps**2):.6g}")
    # compare to n=5 at the limit config: legs 1,2,3 minus, 4 and 6 plus, with w5->0
    # at eps->0, solve n=5 with free legs 2,3,4 (plus legs 4 and the solved 5th=leg "n")
    # n=5 three-minus: free = w2,w3,w4 (legs 2,3 minus-free, leg4 plus-free); legs1,5 solved
    print("\nn=5 three-minus at (legs 2,3 minus, 4 plus free):")
    im5, om5, _ = h.on_shell([base[0], base[1], base[2]], SIG5)
    print(" A5/i (oracle) =", float(im5), "  omega5=", [str(o) for o in om5])
    print(" A5/i (formula)=", float(A5_threeminus(*[F(o) for o in om5])))
