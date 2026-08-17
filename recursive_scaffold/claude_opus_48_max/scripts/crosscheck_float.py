"""Cross-check bg_float (mpmath) vs bg.py (exact Fraction) at rational points,
interleaving AND non-interleaving, to gauge float-port reliability."""
from fractions import Fraction as F
import mpmath as mp
from bg import bg_amplitude, make_kinematics, two_minus_sigmas
import bg_float
mp.mp.dps = 50


def both(n, fw):
    sig = two_minus_sigmas(n)
    sig_int = [-1, -1] + [1] * (n - 2)
    allK, allW = make_kinematics(n, [F(x) for x in fw], sig, 1)
    Aexact = bg_amplitude(allK, allW, 1)
    bg_float.reset_caches()
    Afloat = bg_float.amp_from_allW([float(x) for x in allW], sig_int)
    return allW, Aexact.im, Afloat.imag


def interleaving(allW):
    lo = min(abs(allW[0]), abs(allW[1])); hi = max(abs(allW[0]), abs(allW[1]))
    return all(lo <= abs(w) <= hi for w in allW[2:])


cases = [
    (5, [2, F(5, 2), 3]),
    (5, [1, 3, 5]),
    (5, [F(7, 3), F(-1, 3), F(5, 2)]),   # non-interleaving (from verify1a-style)
    (6, [F(3, 2), 2, F(5, 2), 3]),
    (6, [F(-3), F(-1, 3), F(-5, 3), 4]),  # likely non-interleaving
    (7, [F(3, 2), 2, F(5, 2), 3, F(7, 2)]),
]
for n, fw in cases:
    try:
        allW, ex, fl = both(n, fw)
        relerr = abs(float(ex) - float(fl)) / (abs(float(ex)) + 1e-30)
        print(f"n={n} inter={interleaving(allW)} allW={[str(x) for x in allW]}")
        print(f"    exact={ex}  float={mp.nstr(fl,16)}  relerr={relerr:.2e}  {'OK' if relerr<1e-12 else 'FLOAT-OFF'}")
    except Exception as e:
        print(f"n={n} fw={fw}: {type(e).__name__}: {e}")
