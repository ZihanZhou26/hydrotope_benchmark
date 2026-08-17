#!/usr/bin/env python3
"""Soft-theorem recursion on the SPLINE NUMERATOR N_n.

Derivation (g general). A_m = i 2^{m-1} g^{3-m} N_m / D_m, with
  D_m = prod_{i in minus} prod_{j in plus} (omega_i + omega_j).

PLUS leg p soft (omega_p -> 0): A_n -> 2(n-3) omega_p^2 A_{n-1}^{3-}.
  D_n -> (omega_1 omega_2 omega_3) * D_{n-1}^{3-}  [the 3 factors (omega_i+omega_p)->omega_i].
  =>  N_n  ->  (n-3) g omega_1 omega_2 omega_3 * omega_p^2 * N_{n-1}^{3-}.
  i.e. N_n vanishes like omega_p^2; coefficient of omega_p^2 (at omega_p=0) is
       (n-3) g omega_1 omega_2 omega_3 N_{n-1}^{3-}.

MINUS leg p soft (omega_p -> 0, say p=3): A_n -> 2(n-3) omega_p^2 A_{n-1}^{2-}.
  A_{n-1}^{2-} = i 2^{n-2} g^{4-n} omega_1 omega_2 Sigma, Sigma = sum_{S subset plus}
     (-1)^|S| (min(om1^2,om2^2) - sum_{j in S} om_j^2)_+^{n-4}.
  D_n -> (prod_{j in plus} omega_j) * D_{n-1}^{2-},  D_{n-1}^{2-}=prod_{i in {1,2},j in plus}(omega_i+omega_j).
  =>  N_n -> (n-3) g omega_1 omega_2 omega_p^2 Sigma (prod_{j in plus} omega_j) D_{n-1}^{2-}.

We verify both at n=6 by exact-rational Richardson extrapolation of N_6/omega_p^2.
"""
from fractions import Fraction as F
import itertools, sympy as sp
import harness as h, r4lib

SIG6 = [-1, -1, -1, 1, 1, 1]
SIG5 = [-1, -1, -1, 1, 1]


def D_mixed(omega, minus, plus):
    d = F(1)
    for i in minus:
        for j in plus:
            d *= (F(omega[i - 1]) + F(omega[j - 1]))
    return d


def N5_threeminus(omega):
    """N_5 = A_5 * D6 / (i 2^4 g^-2); minus={1,2,3}, plus={4,5}. omega 0-based len5."""
    im, _, _ = h.amp([SIG5[i] * F(omega[i]) ** 2 for i in range(5)], [F(o) for o in omega])
    d6 = D_mixed(omega, (1, 2, 3), (4, 5))
    return F(im) * d6 / F(2 ** 4)


def richardson_limit(seq):
    """seq = list of (eps, value); fit polynomial in eps, return value at eps=0."""
    x = sp.Symbol('e')
    pts = [(sp.Rational(e.numerator, e.denominator), sp.Rational(v.numerator, v.denominator))
           for e, v in seq]
    poly = sp.interpolate(pts, x)
    return sp.expand(poly).subs(x, 0)


def two_minus_amp(omega, minus, plus, g=1):
    """Closed-form two-minus A_{m}/i for given minus pair, plus legs. omega 1-based dict."""
    a, b = minus
    m = len(omega)
    beta2 = min(omega[a] ** 2, omega[b] ** 2)
    tot = F(0)
    P = list(plus)
    for r in range(len(P) + 1):
        for S in itertools.combinations(P, r):
            v = beta2 - sum(omega[j] ** 2 for j in S)
            if v > 0:
                tot += F((-1) ** r) * v ** (m - 3)
    return F(2 ** (m - 1)) * F(g) ** (3 - m) * omega[a] * omega[b] * tot


if __name__ == "__main__":
    print("=== PLUS leg soft (p=5), n=6 ===")
    base = [F(3), F(5), F(4)]  # free legs 2,3,4
    seq = []
    for k in range(3, 10):
        eps = F(1, 2 ** k)
        N6, oms, im = r4lib.Nn_value([base[0], base[1], base[2], eps], SIG6)
        seq.append((eps, N6 / eps ** 2))
    lim = richardson_limit(seq)
    print("lim N_6/omega_5^2 =", lim)
    # predicted = (n-3) g w1 w2 w3 N_5^{3-}, evaluated at omega_5=0 limit point.
    # Build the omega_5=0 limiting 5-pt config: legs 1,2,3 minus; 4 and (solved 6) plus.
    N6_tiny, oms_tiny, _ = r4lib.Nn_value([base[0], base[1], base[2], F(1, 2 ** 14)], SIG6)
    w = [F(o) for o in oms_tiny]            # ~ omega_5=0 limit
    om5 = [w[0], w[1], w[2], w[3], w[5]]     # legs 1,2,3 minus; 4,6 plus -> n=5 three-minus
    N5 = N5_threeminus(om5)
    pred = F(3) * 1 * w[0] * w[1] * w[2] * N5    # (n-3)=3, g=1
    print("predicted (n-3) w1 w2 w3 N_5^{3-} =", float(pred), "  (at eps~0)")
    print("lim/pred ratio ~", float(lim / pred))

    print("\n=== MINUS leg soft (p=3), n=6 ===")
    # free legs are 2,3,4,5 -> make omega_3 -> 0. legs: 1,2,3 minus; 4,5,6 plus.
    base2 = [F(5), F(7)]  # legs 4,5 (plus); leg 2 minus fixed; leg 3 minus -> 0
    seq2 = []
    for k in range(3, 10):
        eps = F(1, 2 ** k)
        # free = [w2, w3=eps, w4, w5]; solve legs 1,6
        free = [F(2), eps, F(5), F(7)]
        N6, oms, im = r4lib.Nn_value(free, SIG6)
        seq2.append((eps, N6 / eps ** 2))
    lim2 = richardson_limit(seq2)
    print("lim N_6/omega_3^2 =", lim2)
    # predicted: (n-3) g w1 w2 Sigma (prod_plus w_j) D_{n-1}^{2-}, at omega_3=0
    free_tiny = [F(2), F(1, 2 ** 14), F(5), F(7)]
    N6_t, oms_t, _ = r4lib.Nn_value(free_tiny, SIG6)
    w = [F(o) for o in oms_t]   # ~ omega_3=0 limit; legs 1,2 minus eff; 4,5,6 plus
    wd = {1: w[0], 2: w[1], 4: w[3], 5: w[4], 6: w[5]}  # drop leg 3
    # two-minus n=5: minus {1,2}, plus {4,5,6}
    beta2 = min(wd[1] ** 2, wd[2] ** 2)
    Sigma = F(0)
    P = [4, 5, 6]
    for r in range(4):
        for Ssub in itertools.combinations(P, r):
            v = beta2 - sum(wd[j] ** 2 for j in Ssub)
            if v > 0:
                Sigma += F((-1) ** r) * v ** 2   # n-4 = 2
    prod_plus = wd[4] * wd[5] * wd[6]
    D2 = F(1)
    for i in (1, 2):
        for j in (4, 5, 6):
            D2 *= (wd[i] + wd[j])
    pred2 = F(3) * 1 * wd[1] * wd[2] * Sigma * prod_plus * D2
    print("predicted (minus-leg) =", float(pred2))
    print("lim2/pred2 ratio ~", float(lim2 / pred2))
