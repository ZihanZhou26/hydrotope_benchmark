"""Determine homogeneity degree d_n of A_n and timing."""
from bg import amp_two_minus
from fractions import Fraction as Q
import time

def deg_check(n, free):
    A1,_,_ = amp_two_minus(n, free)
    free2 = [2*x for x in free]
    A2,_,_ = amp_two_minus(n, free2)
    # A2 = 2^d * A1  -> 2^d = A2/A1
    r = A2.im / A1.im
    # find d so 2^d = r
    import math
    d = math.log(abs(float(r)))/math.log(2)
    return A1.im, A2.im, r, d

cases = {
    4: [Q(2), Q(3)],            # n=4 -> may be degenerate
    5: [Q(2), Q(5,2), Q(3)],
    6: [Q(3,2), Q(2), Q(5,2), Q(3)],
    7: [Q(3,2), Q(2), Q(5,2), Q(3), Q(7,2)],
}
for n in [5,6,7]:
    free = cases[n]
    t=time.time()
    try:
        im1, im2, r, d = deg_check(n, free)
        print(f"n={n}: A(free)={im1} i, A(2*free)={im2} i, ratio={r} = 2^{d:.4f}  ({time.time()-t:.2f}s for 2 evals)")
    except Exception as e:
        print(f"n={n}: ERROR {e}")
