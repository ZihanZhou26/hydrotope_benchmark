#!/usr/bin/env python3
"""Round-8 library (student-2, top-down all-n).

Provides:
 - exact on-shell three-minus amplitude A_n/i via fastbg (any n)
 - the KNOWN two-minus closed form A^{2-}_n/i (base case / boundary)
 - C_n = A_n/(i 2^{n-1} g^{3-n})  (g=1) , the natural rational object
 - D_n = prod_{i in M, j in P}(w_i + w_j)  (minimal denominator, n!=6)
 - N_n = C_n * D_n  (the spline numerator, polynomial per chamber)
All exact (Fraction).
"""
from fractions import Fraction as F
from itertools import combinations
import fastbg

# ---- three-minus oracle (fastbg) ----
def threem_signs(n):
    return [-1,-1,-1] + [1]*(n-3)

def A_over_i_3m(free, n):
    """free = n-2 frequencies (legs 2..n-1). Returns (A_n/i, omegas) exact."""
    return fastbg.A_over_i([F(x) for x in free], threem_signs(n))

def C_n(free, n):
    """C_n = A_n/(i 2^{n-1}) at g=1.  Returns (C, omegas)."""
    im, oms = A_over_i_3m(free, n)
    return F(im, 2**(n-1)), oms

def Dn(oms):
    """minimal denominator prod_{i in M, j in P}(w_i+w_j); M={1,2,3}, P=rest."""
    n = len(oms)
    M = oms[:3]; P = oms[3:]
    d = F(1)
    for wi in M:
        for wj in P:
            d *= (wi + wj)
    return d

def Nn(free, n):
    """N_n = C_n * D_n (the polynomial spline numerator, full denominator)."""
    C, oms = C_n(free, n)
    return C * Dn(oms), oms

# ---- two-minus closed form (KNOWN; minus legs a,b given by their 0-based index) ----
def A2m_over_i(oms, a, b, g=F(1)):
    """Two-minus law. oms: list of all freqs. a,b: 0-based indices of the two MINUS legs.
       A/i = 2^{n-1} g^{3-n} w_a w_b sum_{S subset P} (-1)^|S| (beta^2 - sum_S w_j^2)_+^{n-3},
       beta^2 = min(w_a^2, w_b^2), P = all other legs."""
    n = len(oms)
    P = [k for k in range(n) if k not in (a,b)]
    wa, wb = oms[a], oms[b]
    beta2 = min(wa*wa, wb*wb)
    m = n-3
    tot = F(0)
    for r in range(len(P)+1):
        for S in combinations(P, r):
            val = beta2 - sum(oms[j]*oms[j] for j in S)
            if val > 0:
                tot += (-1)**r * val**m
    return 2**(n-1) * (g**(3-n) if g!=1 else 1) * wa * wb * tot

# ---- two-minus oracle check helper ----
def twom_signs(n):
    return [-1,-1] + [1]*(n-2)

if __name__ == "__main__":
    # 1) verify two-minus closed form vs oracle (minus legs 0,1 = legs 1,2)
    print("=== two-minus closed form vs oracle ===")
    import harness as h
    for free in [[2,3,5],[2,3,5,7],[3,5,7,11,2]]:
        n = len(free)+2
        im_o, _, oms_o = h.on_shell(free, twom_signs(n))
        # build full oms via fastbg solve
        oms = fastbg.solve_legs([F(x) for x in free], twom_signs(n))
        cf = A2m_over_i(oms, 0, 1)
        print(f"n={n}: closed={cf}  oracle={im_o}  match={cf==F(im_o)}")

    # 2) three-minus: C_n, D_n, N_n sanity at n=6
    print("\n=== n=6 three-minus N_6 = C_6 * D_6 ===")
    N, oms = Nn([2,3,5,7], 6)
    print(f"oms={[str(x) for x in oms]}")
    print(f"N_6 = {N}")
