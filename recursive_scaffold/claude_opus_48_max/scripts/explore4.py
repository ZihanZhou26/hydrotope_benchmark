"""
(1) g-power vs n (exact).
(2) Map the simplest NON-interleaving region for n=5: one plus leg 's' softer than
    both minus legs. Fix minus=(-4,1); vary s in (-1,1); the other two plus legs are
    determined. Tabulate a_5(s) and look for structure.
(3) Test in that region whether a_5 depends only on (minus, s) for n=6 (vary the
    remaining interleaving plus legs).
"""
import mpmath as mp
from fractions import Fraction as F
from bg import amp_two_minus, bg_amplitude, two_minus_sigmas
import bg_float
mp.mp.dps = 50

print("=== (1) g-power vs n (exact) ===", flush=True)
for n, fw in [(5, [F(2), F(5, 2), F(3)]), (6, [F(3, 2), F(2), F(5, 2), F(3)]),
              (7, [F(3, 2), F(2), F(5, 2), F(3), F(7, 2)])]:
    A1, allW, _ = amp_two_minus(n, fw, g=1)
    sig = two_minus_sigmas(n)
    g = F(2)
    allK_g = [sig[i] * allW[i] ** 2 / g for i in range(n)]
    Ag = bg_amplitude(allK_g, allW, g)
    ratio = Ag.im / A1.im
    # ratio = 2^p
    import math
    p = math.log(float(ratio)) / math.log(0.5)  # ratio = (1/2)^? => 2^-?
    print(f"  n={n}: a_n(2)/a_n(1) = {ratio}  => g-power p where ratio=g^p: "
          f"p={math.log(float(ratio))/math.log(2):.4f}", flush=True)

print("\n=== (2) n=5 'one soft plus leg' region: minus=(-4,1), vary s in (-1,1) ===", flush=True)
w1, w2 = mp.mpf(-4), mp.mpf(1)
A_ = -(w1 + w2)
B_ = w1 ** 2 + w2 ** 2
sig5 = [-1, -1, 1, 1, 1]
print(f"  interleaving value would be a_5 = -64", flush=True)
s = mp.mpf('-0.9')
while s <= mp.mpf('0.9'):
    if abs(s) > mp.mpf('0.05'):
        ss = A_ - s
        qq = B_ - s ** 2
        disc = 2 * qq - ss ** 2
        if disc >= 0:
            r = mp.sqrt(disc)
            x, y = (ss + r) / 2, (ss - r) / 2
            allW = [w1, w2, s, x, y]
            try:
                A = bg_float.amp_from_allW(allW, sig5)
                # candidate ideas to compare
                print(f"  s={mp.nstr(s,4):>7}: plus=({mp.nstr(s,4)},{mp.nstr(x,4)},{mp.nstr(y,4)}) "
                      f"a_5={mp.nstr(A.imag,12):>16}", flush=True)
            except Exception:
                pass
    s += mp.mpf('0.15')
