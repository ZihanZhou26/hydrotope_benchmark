#!/usr/bin/env python3
"""Round-4 consolidated verification (student-2), EXACT rational throughout.
Checks:
 (1) Soft theorem A_n -> 2(n-3) w_p^2 A_{n-1}, both plus & minus soft legs (n=6): ratio = 6.
 (2) Denominator D_n clears A_n to a polynomial on an F-const slice at n=6 AND n=7.
 (3) A_6 has SIMPLE poles exactly at perfect-matching loci (n=6 slice): denominator of
     the reduced rational function factors into the active matching linear forms.
 (4) Per-chamber form A_6/i = sextic / (active matchings).
"""
import sympy as sp
from fractions import Fraction as F
import harness as h, r4lib

t = sp.Symbol('t')


def interp(ts, vs):
    return sp.expand(sp.interpolate(
        [(sp.Rational(a.numerator, a.denominator), sp.Rational(b.numerator, b.denominator))
         for a, b in zip(ts, vs)], t))


def is_poly_on_slice(free_fn, sig, npts, label, den=120):
    """free_fn(t)->free freq list. Check A_n*D_n is polynomial in t (exact),
    using a NARROW range tv=k/den to stay inside one chamber (no wall crossing)."""
    n = len(sig)
    ts, Nv = [], []
    for k in range(1, npts + 1):
        tv = F(k, den)
        free = free_fn(tv)
        try:
            im, oms, _ = h.on_shell(free, sig)
        except Exception:
            continue
        d = r4lib.Dn(oms)
        ts.append(tv); Nv.append(F(im) * d)
    Np = interp(ts, Nv)
    # verify the interpolant predicts held-out points exactly
    ok = True
    for k in range(npts + 1, npts + 6):
        tv = F(k, den)
        free = free_fn(tv)
        try:
            im, oms, _ = h.on_shell(free, sig)
        except Exception:
            continue
        d = r4lib.Dn(oms)
        pred = Np.subs(t, sp.Rational(tv.numerator, tv.denominator))
        actual = sp.Rational((F(im) * d).numerator, (F(im) * d).denominator)
        if sp.expand(pred - actual) != 0:
            ok = False
    print(f"({label}) A_n*D_n polynomial on slice (deg {sp.degree(Np,t)}), "
          f"held-out exact: {ok}")
    return ok


def soft_ratio(free_fn_eps, sig, surviving_amp, label):
    """lim A_n/(i eps^2 A_{n-1}) via Richardson, should be 2(n-3)."""
    n = len(sig)
    seq = []
    for k in range(3, 10):
        eps = F(1, 2 ** k)
        free = free_fn_eps(eps)
        im, oms, _ = h.on_shell(free, sig)
        seq.append((eps, F(im) / eps ** 2))
    lim = sp.expand(sp.interpolate(
        [(sp.Rational(e.numerator, e.denominator), sp.Rational(v.numerator, v.denominator))
         for e, v in seq], t)).subs(t, 0)
    A_surv = surviving_amp()
    print(f"({label}) lim A/(i eps^2) = {float(lim):.6g}; A_(n-1)/i = {float(A_surv):.6g}; "
          f"ratio = {sp.nsimplify(lim/A_surv)} (expect {2*(n-3)})")


def A5_threeminus(w1, w2, w3, w4, w5):
    import itertools
    m = min(w4 ** 2, w5 ** 2); tot = F(0); legs = [w1, w2, w3]
    for r in range(4):
        for S in itertools.combinations(range(3), r):
            v = m - sum(legs[i] ** 2 for i in S)
            if v > 0:
                tot += F((-1) ** r) * v ** 2
    return 16 * w4 * w5 * tot


def A5_twominus(wa, wb, plus):
    import itertools
    beta2 = min(wa ** 2, wb ** 2); tot = F(0)
    for r in range(4):
        for S in itertools.combinations(range(3), r):
            v = beta2 - sum(plus[i] ** 2 for i in S)
            if v > 0:
                tot += F((-1) ** r) * v ** 2
    return 16 * wa * wb * tot


if __name__ == "__main__":
    SIG6 = [-1, -1, -1, 1, 1, 1]; SIG7 = [-1, -1, -1, 1, 1, 1, 1]
    print("--- (1) SOFT THEOREM (both legs) ---")
    # plus leg 5 -> 0; surviving n=5 three-minus, plus legs {4,6}; eval at EXACT eps=0
    def surv_plus():
        free = [F(3), F(5), F(4), F(0)]
        oms = h.solve_legs_1n(free, SIG6); w = [F(o) for o in oms]
        return A5_threeminus(w[0], w[1], w[2], w[3], w[5])
    soft_ratio(lambda e: [F(3), F(5), F(4), e], SIG6, surv_plus, "plus leg soft")
    # minus leg 2 -> 0; surviving n=5 two-minus, minus {1,3}, plus {4,5,6}; eval at eps=0
    def surv_minus():
        free = [F(0), F(5), F(4), F(6)]
        oms = h.solve_legs_1n(free, SIG6); w = [F(o) for o in oms]
        return A5_twominus(w[0], w[2], [w[3], w[4], w[5]])
    soft_ratio(lambda e: [e, F(5), F(4), F(6)], SIG6, surv_minus, "minus leg soft")

    print("\n--- (2) DENOMINATOR D_n clears A_n (n=6, n=7) ---")
    is_poly_on_slice(lambda tv: [F(2), F(3), F(5) + tv, F(7) - tv], SIG6, 18, "n=6")
    is_poly_on_slice(lambda tv: [F(2), F(3), F(5) + tv, F(7) - tv, F(11)], SIG7, 22, "n=7")

    print("\n--- (3,4) POLES AT PERFECT MATCHINGS (n=6 slice) ---")
    import residue as R
    A = R.slice_rational(2, 3, 5, 7)
    num, den = sp.fraction(A)
    print("A_6/i =", sp.factor(A))
    print("denominator roots (= perfect-matching loci):", sp.roots(sp.Poly(den, t)))
    print("numerator degree (sextic core):", sp.degree(sp.Poly(num, t)))
