"""
symbolic.py — symbolic BG amplitude as a function of independent omega_1..omega_n.

We treat all omega_i as independent symbols (matching bg.cpp --amp with K_i = sigma_i omega_i^2),
resolve every abs(.) by the sign at a generic reference point in the physical chamber,
reduce, and return the (purely imaginary) amplitude a_n(omega) = Im(A_n).

For n=4 the on-shell surface is exactly omega_1=-omega_3, omega_4=-omega_2, where the
internal {2,4} current is 0/0; computing OFF-shell (independent omega) and only afterward
restricting to the surface lets the removable singularity cancel.
"""
import sys
import sympy as sp
from fractions import Fraction
from engine import Engine


def make_resolver(ref):
    """ref: dict sym->Fraction (generic chamber point). Returns absf(expr)->+/-expr."""
    def absf(expr):
        if expr == 0:
            return expr
        val = sp.nsimplify(expr.subs(ref)) if hasattr(expr, 'subs') else sp.Integer(expr)
        # evaluate exactly using Rational substitution
        v = expr.subs(ref)
        v = sp.nsimplify(v, rational=True)
        if v > 0:
            return expr
        elif v < 0:
            return -expr
        else:
            raise ValueError(f"non-generic reference: abs argument vanishes: {expr}")
    return absf


def symbolic_amp(N, sigma, ref):
    """Return (re, im) symbolic, with independent omega symbols w1..wN."""
    w = {i: sp.Symbol(f'w{i}', real=True) for i in range(1, N+1)}
    K = {i: sp.Integer(sigma[i-1]) * w[i]**2 for i in range(1, N+1)}
    refsub = {w[i]: sp.Rational(ref[i].numerator, ref[i].denominator) for i in range(1, N+1)}
    absf = make_resolver(refsub)
    E = Engine('sympy', absf=absf, G=1)
    re, im = E.BGAmplitude(N, K, w)
    return sp.cancel(re), sp.cancel(im), w


if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    sigma = [-1, -1] + [1]*(N-2)
    # generic chamber reference: legs 2..N-1 positive, legs 1,N negative, OFF on-shell surface
    # generic chamber: plus-legs magnitudes ~powers of 2 (distinct subset sums), legs 1,N negative
    if N == 4:
        ref = {1: Fraction(-5), 2: Fraction(1), 3: Fraction(2), 4: Fraction(-3)}
    elif N == 5:
        ref = {1: Fraction(-7), 2: Fraction(1), 3: Fraction(2), 4: Fraction(4), 5: Fraction(-5)}
    elif N == 6:
        ref = {1: Fraction(-11), 2: Fraction(1), 3: Fraction(2), 4: Fraction(4), 5: Fraction(8), 6: Fraction(-7)}
    else:
        raise SystemExit("set a reference for this N")

    re, im, w = symbolic_amp(N, sigma, ref)
    print("Re A_n (cancelled) =", re)
    print()
    print("a_n = Im A_n (cancelled):")
    sp.pprint(im)
    print()
    print("factored:")
    sp.pprint(sp.factor(im))
