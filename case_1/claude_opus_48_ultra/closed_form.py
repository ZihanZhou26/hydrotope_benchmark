"""Closed-form evaluator for the two-minus tree amplitude A_n.

Results (all verified to machine precision against BGAmplitude):

  (1) GENERAL n, "principal regime" (the smallest-|omega| leg is one of the two
      sigma=-1 legs -- this regime contains every example used by the reference
      OnShellBG.m, and is sign-robust):

            A_n  =  2^{n-1} * w1 * w2 * ( min(w1^2, w2^2) )^{n-3}     (times i)

  (2) n = 5, COMPLETE (valid in every chamber / for arbitrary kinematics):

            A_5  =  P0(w)  +  sum_{mu in {1,2}, j in {3,4,5}} P_{mu j}(w) * |w_j^2 - w_mu^2|

      a single global expression; the |w_j^2 - w_mu^2| = |k_{mu j}| are the
      type-1 (one sigma=-1 leg + one sigma=+1 leg) channel momenta.  The explicit
      P0, P_{mu j} are loaded from the exact rational fit (kabs_sol5.pkl).

The amplitude is purely imaginary: BGAmplitude = i * (value below).
"""
from fractions import Fraction as Q
import math, pickle, os

# ---------- (1) general-n principal-regime formula ----------
def A_principal(n, w):
    """2^{n-1} w1 w2 (min(w1^2,w2^2))^{n-3}.  Exact; valid when min_i w_i^2 is a minus leg."""
    w = [Q(x) for x in w]
    m2 = min(w[0]*w[0], w[1]*w[1])
    return 2**(n-1) * w[0] * w[1] * m2**(n-3)

def softest_is_minus(w):
    w2 = [Q(x)*Q(x) for x in w]
    return w2.index(min(w2)) < 2

# ---------- (2) complete n=5 global formula ----------
_HERE = os.path.dirname(os.path.abspath(__file__))
_sol5 = None
def _load5():
    global _sol5
    if _sol5 is None:
        with open(os.path.join(_HERE, "kabs_sol5.pkl"), "rb") as f:
            _sol5 = [Q(s) for s in pickle.load(f)]
    return _sol5

def A5_complete(w):
    """Complete n=5 amplitude (imag part), valid for ALL kinematics / chambers."""
    from fit_kabs import P0_basis_vals, PEXPS, kabs_basis_vals
    w = tuple(Q(x) for x in w)
    sol = _load5()
    nb0 = len(P0_basis_vals((Q(1),Q(2),Q(3),Q(4),Q(5))))
    vals = P0_basis_vals(w) + kabs_basis_vals(w)
    return sum(sol[j]*vals[j] for j in range(len(vals)))

def predict(n, w):
    """Best available closed form: complete for n=5; principal-regime formula otherwise."""
    if n == 5:
        return A5_complete(w)
    return A_principal(n, w)

if __name__ == "__main__":
    # smoke test against a couple of known values
    from bg import amp_two_minus
    A,_,wL = amp_two_minus(5, [Q(2),Q(5,2),Q(3)])
    print("n=5 (2,5/2,3): BG", A.im, " formula", A5_complete(wL))
    A,_,wL = amp_two_minus(6, [Q(3,2),Q(2),Q(5,2),Q(3)])
    print("n=6 (3/2,2,5/2,3): BG", A.im, " principal-formula", A_principal(6, wL),
          " (softest minus?", softest_is_minus(wL), ")")
