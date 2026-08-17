"""formulas.py — candidate closed forms + checkers against the oracle.

All amplitudes in these sectors are pure-imaginary: A = i * (real). We work with
the real coefficient B := A / i = A_im, in exact rational arithmetic.
"""
import itertools
from fractions import Fraction as Fr
import harness


def trunc_pow(x, p):
    """(x)_+^p with the convention (x)_+ = max(x,0), and 0^0 = 1."""
    if x <= 0:
        return Fr(0)
    if p == 0:
        return Fr(1)
    return x ** p


def two_minus_B(n, omega, g=1):
    """Documented two-minus closed form, returned as B = A/i (real, exact).
    omega: list of n frequencies (Fractions). Legs 1,2 minus; 3..n plus."""
    om = [Fr(x) for x in omega]
    w1, w2 = om[0], om[1]
    beta2 = min(abs(w1), abs(w2)) ** 2
    plus = list(range(2, n))  # indices 2..n-1 == legs 3..n
    S = Fr(0)
    for r in range(0, len(plus) + 1):
        for combo in itertools.combinations(plus, r):
            sub = sum(om[j] ** 2 for j in combo)
            S += Fr((-1) ** r) * trunc_pow(beta2 - sub, n - 3)
    pref = Fr(2) ** (n - 1) * Fr(g) ** (3 - n) * w1 * w2
    return pref * S


def special_pair_B(n, omega, special, summed, g=1):
    """Generic 'two-minus-type' law with an arbitrary special PAIR and summed set.
    B = 2^(n-1) g^(3-n) * w_a w_b * sum_{S subset summed} (-1)^|S| (beta^2 - sum_S w_j^2)_+^p
    with beta = min(|w_a|,|w_b|), a,b = special (0-indexed legs), p = (#summed)-1.
    """
    om = [Fr(x) for x in omega]
    a, b = special
    beta2 = min(abs(om[a]), abs(om[b])) ** 2
    p = len(summed) - 1
    S = Fr(0)
    for r in range(0, len(summed) + 1):
        for combo in itertools.combinations(summed, r):
            sub = sum(om[j] ** 2 for j in combo)
            S += Fr((-1) ** r) * trunc_pow(beta2 - sub, p)
    pref = Fr(2) ** (n - 1) * Fr(g) ** (3 - n) * om[a] * om[b]
    return pref * S


def three_minus_n5_twoplus_B(omega, g=1):
    """C1: n=5 three-minus via +/- swap: special pair = plus legs {4,5} (idx 3,4),
    box-spline sum over the 3 minus legs {1,2,3} (idx 0,1,2)."""
    return special_pair_B(5, omega, special=(3, 4), summed=(0, 1, 2), g=g)


def sum_over_pairs_B(n, omega, pair_class="minus", coeff=lambda a, b: 1, g=1):
    """Sum the special-pair law over all pairs drawn from one sign-class.
    For each pair (a,b) in that class, the summed set = all other legs."""
    minus = list(range(0, 3))
    plus = list(range(3, n))
    pool = minus if pair_class == "minus" else plus
    alllegs = list(range(n))
    tot = Fr(0)
    for (a, b) in itertools.combinations(pool, 2):
        summed = tuple(j for j in alllegs if j not in (a, b))
        tot += Fr(coeff(a, b)) * special_pair_B(n, omega, (a, b), summed, g=g)
    return tot


def check_two_minus(points, g=1):
    """points: list of (n, free_w). Compares B-formula to oracle exact."""
    ok = True
    for (n, free_w) in points:
        sigma = [-1, -1] + [1] * (n - 2)
        r = harness.onshell(n, free_w, sigma, g=g)
        om = r["omega"]
        assert r["A_re"] == 0, f"unexpected real part {r['A_re']}"
        Bor = r["A_im"]
        Bf = two_minus_B(n, om, g=g)
        match = (Bf == Bor)
        ok = ok and match
        print(f"n={n} free_w={free_w} omega={[str(x) for x in om]}")
        print(f"   oracle B={Bor}  formula B={Bf}  {'OK' if match else 'MISMATCH'}")
    print("ALL OK" if ok else "SOME MISMATCH")
    return ok


if __name__ == "__main__":
    pts = [
        (5, [2, 3, 5]),
        (5, [Fr(7, 2), 4, Fr(9, 5)]),
        (6, [2, 3, 5, 7]),
        (6, [Fr(3, 2), 4, Fr(5, 3), 6]),
        (7, [2, 3, 5, 7, 4]),
        (7, [1, 2, 3, 4, 5]),
    ]
    check_two_minus(pts)
