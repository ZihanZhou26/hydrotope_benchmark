"""
n=4 is the degenerate boundary (oracle gives 0/0). Verify the formula's n=4 value
  a_4 = 8 * w1*w2 * min(w1^2,w2^2)
two independent ways:
 (A) epsilon-deformation: perturb w4 = -w2 + eps off the exact n=4 manifold (so the
     {2,4} and {1,3} channels are non-degenerate), compute exact a_4(eps), extrapolate eps->0.
 (B) regularized propagator: define Propagator(0,0,g) := I/g (the proportional limit),
     recompute BGAmplitude at the exact n=4 point.
Both should equal the formula.
"""
from fractions import Fraction as F
import bg
from bg import bg_amplitude, two_minus_sigmas


def cand4(w1, w2):
    return 8 * (w1 * w2) * min(w1 * w1, w2 * w2)


print("=== (A) epsilon-deformation of n=4 (keep all 4 legs on-shell, relax momentum cons by O(eps)) ===")
# n=4 forced manifold: minus (w1,w2), plus (w3=-w1, w4=-w2). We deform w4 = -w2 + eps,
# keep energy cons by adjusting w3 = -(w1+w2+w4). Each leg stays on-shell (k=sigma*w^2).
# Momentum sum is then O(eps); we extrapolate a_4(eps) -> eps=0.
def a4_eps(w1, w2, eps):
    w4 = -w2 + eps
    w3 = -(w1 + w2 + w4)
    allW = [w1, w2, w3, w4]
    sig = two_minus_sigmas(4)
    allK = [sig[i] * allW[i] ** 2 for i in range(4)]  # g=1
    A = bg_amplitude(allK, allW, 1)
    return A


for (w1, w2) in [(F(-4), F(1)), (F(-3), F(2)), (F(-5), F(2)), (F(-7), F(3))]:
    print(f"  minus=({w1},{w2}) formula a_4={cand4(w1,w2)}")
    for eps in [F(1, 10), F(1, 100), F(1, 1000), F(1, 100000)]:
        try:
            A = a4_eps(w1, w2, eps)
            print(f"     eps={float(eps):.0e}: A_4={A.re}{'+' if A.im>=0 else ''}{A.im} i")
        except Exception as e:
            print(f"     eps={float(eps)}: {type(e).__name__}")
    print()


print("=== (B) regularized propagator Propagator(0,0,g):=I/g, exact n=4 point ===")
_orig_prop = bg.propagator


def reg_prop(w, k, g):
    mk = bg.mag(k)
    if mk == 0:
        # limit of -I/(w^2/|k| - g): if w=0 too, proportional approach -> -I/(0-g)=I/g
        if w == 0:
            return bg.CQ(0, F(1) / g)  # I/g
        else:
            return bg.CQ(0, 0)  # -I/(inf) -> 0
    denom = w * w / mk - g
    if denom == 0:
        return bg.CQ(0, 0)
    return bg.CQ(0, -F(1) / denom)


bg.propagator = reg_prop
for (w1, w2) in [(F(-4), F(1)), (F(-3), F(2)), (F(-5), F(2)), (F(-7), F(3)), (F(-5), F(-2))]:
    w3, w4 = -w1, -w2  # forced n=4 manifold
    allW = [w1, w2, w3, w4]
    sig = two_minus_sigmas(4)
    allK = [sig[i] * allW[i] ** 2 for i in range(4)]
    try:
        A = bg_amplitude(allK, allW, 1)
        c = cand4(w1, w2)
        print(f"  minus=({w1},{w2}): reg A_4={A.re}+{A.im}i  formula i*{c}  {'OK' if (A.re==0 and A.im==c) else 'DIFF'}")
    except Exception as e:
        print(f"  minus=({w1},{w2}): {type(e).__name__}: {e}")
bg.propagator = _orig_prop
