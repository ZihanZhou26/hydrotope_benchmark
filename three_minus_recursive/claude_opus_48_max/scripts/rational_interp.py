"""rational_interp.py — exact univariate rational interpolation of B along a line.

Vary one free frequency t (others fixed rational), sample B(t) exactly from the
oracle, and fit B(t) = N(t)/D(t) over Q. Roots of D reveal poles; we then match
each pole to a factorization channel w_S^2 = |k_S|.
"""
import sympy as sp
from fractions import Fraction as Fr
import harness

t = sp.symbols('t')


def three_minus_sigma(n):
    return [-1, -1, -1] + [1] * (n - 3)


def sample_line(n, free_template, idx, tvals, g=1):
    """free_template: list of n-2 free freqs with a placeholder at position idx.
    tvals: list of Fractions for t. Returns list of (tval, omega, B) skipping walls."""
    sigma = three_minus_sigma(n)
    out = []
    for tv in tvals:
        fw = list(free_template)
        fw[idx] = tv
        try:
            r = harness.onshell(n, fw, sigma, g=g)
            out.append((tv, r["omega"], r["A_im"]))
        except Exception:
            pass
    return out


def fit_rational(samples, dN, dD):
    """samples: list of (tval Fraction, B Fraction). Fit N(t)/D(t), D monic deg dD.
    Returns (N, D) sympy polys or None if inconsistent."""
    # unknowns: a0..a_dN (N), b0..b_{dD-1} (D, with b_dD=1)
    a = sp.symbols(f'a0:{dN+1}')
    b = sp.symbols(f'b0:{dD}')
    eqs = []
    for (tv, B) in samples:
        tv = sp.Rational(Fr(tv).numerator, Fr(tv).denominator)
        B = sp.Rational(Fr(B).numerator, Fr(B).denominator)
        N = sum(a[i] * tv**i for i in range(dN+1))
        D = sum(b[i] * tv**i for i in range(dD)) + tv**dD
        eqs.append(sp.Eq(N, B * D))
    sol = sp.linsolve(eqs, list(a) + list(b))
    if not sol:
        return None
    sol = list(sol)
    if len(sol) != 1:
        return None
    vals = sol[0]
    # check fully determined (no free symbols)
    if any(v.free_symbols for v in vals):
        return None
    av = vals[:dN+1]
    bv = vals[dN+1:]
    N = sum(av[i] * t**i for i in range(dN+1))
    D = sum(bv[i] * t**i for i in range(dD)) + t**dD
    return sp.Poly(N, t), sp.Poly(D, t)


def autofit(samples, maxdeg=10):
    """Try increasing (dN,dD); validate on held-out half. Return first exact fit."""
    half = len(samples) // 2
    train, hold = samples[:half], samples[half:]
    for total in range(1, maxdeg+1):
        for dD in range(0, total+1):
            dN = total - dD
            need = dN + dD + 1
            if len(train) < need:
                continue
            res = fit_rational(train[:need], dN, dD)
            if res is None:
                continue
            N, D = res
            # validate
            ok = True
            for (tv, B) in train + hold:
                tv = sp.Rational(Fr(tv).numerator, Fr(tv).denominator)
                Bq = sp.Rational(Fr(B).numerator, Fr(B).denominator)
                if D.eval(tv) == 0:
                    ok = False; break
                if sp.simplify(N.eval(tv)/D.eval(tv) - Bq) != 0:
                    ok = False; break
            if ok:
                return dN, dD, N, D
    return None


if __name__ == "__main__":
    n = 6
    # line: vary plus free leg omega_5 (free index 3: free=[w2,w3,w4,w5]); fix others
    base = [Fr(2), Fr(3), Fr(5), None]
    idx = 3
    t0 = Fr(7, 2)
    tvals = [t0 + Fr(j, 60) for j in range(-18, 19) if j != 0]
    samples = [(tv, B) for (tv, om, B) in sample_line(n, base, idx, tvals)]
    print(f"collected {len(samples)} samples near omega_5={float(t0)}")
    fit = autofit([(tv, B) for (tv, B) in samples], maxdeg=12)
    if fit:
        dN, dD, N, D = fit
        print(f"FIT: degN={dN} degD={dD}")
        print("D(t) =", sp.factor(D.as_expr()))
        print("N(t) =", sp.factor(N.as_expr()))
        print("poles (roots of D):", sp.roots(D.as_expr(), t))
    else:
        print("no rational fit up to maxdeg; likely crossing a wall in this interval")
