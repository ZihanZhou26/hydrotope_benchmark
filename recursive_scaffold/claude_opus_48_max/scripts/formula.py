"""
formula.py -- the final closed-form two-minus-sector amplitude, plus a self-test
against the exact Berends-Giele oracle (bg.py).

    A_n = i * 2^(n-1) * w1*w2 * ( min(w1^2, w2^2) / g )^(n-3)

where w1, w2 are the two minus-sector frequencies (legs with sigma = -1), g is
gravity. Valid in the INTERLEAVING region (every plus leg |w| lies between the two
minus |w|); A_n is purely imaginary. See FINAL_ANSWER.md / SCOPE.md.

Run:  python3 formula.py        # prints a verification table vs the exact oracle
"""
from fractions import Fraction as F


def two_minus_amplitude(n, w1, w2, g=1):
    """
    Closed-form A_n in the two-minus sector (interleaving region).

    Parameters
    ----------
    n  : int   number of legs (>= 4)
    w1 : the frequency of minus leg 1 (sigma=-1); int/Fraction/float
    w2 : the frequency of minus leg 2 (sigma=-1)
    g  : gravity (default 1)

    Returns
    -------
    (re, im) such that A_n = re + i*im.  re is always 0 (A_n is purely imaginary).
    Use exact Fraction inputs for an exact rational result.
    """
    w1 = F(w1) if not isinstance(w1, float) else w1
    w2 = F(w2) if not isinstance(w2, float) else w2
    g = F(g) if not isinstance(g, float) else g
    mu2 = min(w1 * w1, w2 * w2)            # smaller minus-leg omega^2
    a = 2 ** (n - 1) * (w1 * w2) * (mu2 / g) ** (n - 3)   # = Im(A_n)
    return (0, a)                          # A_n = i * a


def two_minus_amplitude_im(n, w1, w2, g=1):
    """Just Im(A_n) (the amplitude is i times this)."""
    return two_minus_amplitude(n, w1, w2, g)[1]


# ---------------------------------------------------------------------------
# Self-test against the exact BG oracle (only runs if bg.py is importable).
# ---------------------------------------------------------------------------
def _selftest():
    from bg import bg_amplitude, make_kinematics, two_minus_sigmas, DegenerateKinematics

    def interleaving(allW):
        lo = min(abs(allW[0]), abs(allW[1])); hi = max(abs(allW[0]), abs(allW[1]))
        return all(lo <= abs(w) <= hi for w in allW[2:])

    cases = [  # (n, free freqs, g) -- interleaving points across n and g
        (5, [F(2), F(5, 2), F(3)], F(1)),
        (5, [F(1), F(2), F(3)], F(2)),
        (5, [F(1), F(3), F(5)], F(1)),
        (6, [F(3, 2), F(2), F(5, 2), F(3)], F(1)),
        (6, [F(1), F(2), F(3), F(4)], F(3)),
        (7, [F(3, 2), F(2), F(5, 2), F(3), F(7, 2)], F(1)),
    ]
    print(f"{'n':>2} {'g':>4} {'minus(w1,w2)':>16} {'BGAmplitude A_n':>22} {'formula':>22}  ok")
    allok = True
    for n, fw, g in cases:
        sig = two_minus_sigmas(n)
        allK, allW = make_kinematics(n, fw, sig, g)
        if not interleaving(allW):
            continue
        A = bg_amplitude(allK, allW, g)
        re, im = two_minus_amplitude(n, allW[0], allW[1], g)
        ok = (A.re == re and A.im == im)
        allok &= ok
        print(f"{n:>2} {str(g):>4} {f'({allW[0]},{allW[1]})':>16} "
              f"{f'{A.re}+{A.im}i':>22} {f'{re}+{im}i':>22}  {'OK' if ok else 'FAIL'}")
    # n=4 limit value
    print("\nn=4 (degenerate boundary, formula = eps->0 limit):")
    for (w1, w2) in [(F(-4), F(1)), (F(-9), F(4))]:
        print(f"  minus=({w1},{w2}) g=1:  A_4 = i*{two_minus_amplitude_im(4, w1, w2)}")
    print("\nALL OK" if allok else "\nSOME FAIL")


if __name__ == "__main__":
    _selftest()
