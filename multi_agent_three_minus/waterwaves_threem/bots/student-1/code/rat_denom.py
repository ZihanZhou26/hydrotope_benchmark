#!/usr/bin/env python3
"""Discover the EXACT denominator of A_6 (three-minus) by exact rational-function
reconstruction on a chamber-interior slice, then identify the surviving subset
square-sum factors k_B.

Method (all exact over Q):
  - Vary omega_4 = a + t, hold omega_2,omega_3,omega_5 fixed. legs 1,6 solved.
  - G(t) := A_6(t) * sumFree(t)^8  (sumFree = w2+w3+w4+w5; clears the leg-1,6 solve
    denominators that come from the oracle's rational solve, NOT from the physics).
  - Reconstruct G(t) = N(t)/D(t) by a Pade linear solve (D monic), increasing the
    total degree until it verifies exactly on held-out points.
  - Factor D(t); strip the (known) sumFree(t) linear factor; the remaining factors
    are the genuine surviving kinematic denominators k_B(t).

If A_6 were a degree-8 polynomial in the 6 freqs, G(t) would be a POLYNOMIAL
(deg(D)=0).  A nontrivial D proves A_6 is rational and *names* the denominator.
"""
from fractions import Fraction as F
import sympy as sp
import harness as h
import chambers_n6 as cn

SIG = [-1, -1, -1, 1, 1, 1]


def exact_solve(A, b):
    """Solve A x = b exactly over Q (A square, list of lists of Fraction)."""
    n = len(A)
    M = [[F(A[i][j]) for j in range(n)] + [F(b[i])] for i in range(n)]
    for col in range(n):
        piv = next((r for r in range(col, n) if M[r][col] != 0), None)
        if piv is None:
            return None
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        M[col] = [x / pv for x in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                M[r] = [M[r][k] - f * M[col][k] for k in range(n + 1)]
    return [M[i][n] for i in range(n)]


def reconstruct(pts):
    """pts = list of (t, G) Fractions.  Return (Ncoeffs, Dcoeffs) with D monic
    (D[0]=1 normalization), minimal total degree that verifies on held-out pts."""
    nP = len(pts)
    for total in range(0, 30):
        for dD in range(0, total + 1):
            dN = total - dD
            # unknowns: N_0..N_dN (dN+1), D_1..D_dD (dD), with D_0 = 1
            nun = (dN + 1) + dD
            if nP < nun + 4:
                continue
            rows, rhs = [], []
            for (t, G) in pts[:nun]:
                row = [t ** j for j in range(dN + 1)]            # N coeffs
                row += [-G * t ** k for k in range(1, dD + 1)]    # D_1..D_dD
                rows.append(row)
                rhs.append(G)                                     # = G * D_0
            sol = exact_solve(rows, rhs)
            if sol is None:
                continue
            Nc = sol[:dN + 1]
            Dc = [F(1)] + sol[dN + 1:]
            ok = True
            for (t, G) in pts[nun:]:
                num = sum(c * t ** j for j, c in enumerate(Nc))
                den = sum(c * t ** k for k, c in enumerate(Dc))
                if den == 0 or num != G * den:
                    ok = False
                    break
            if ok:
                return dN, dD, Nc, Dc
    return None


def run_slice(w2, w3, w5, a4, tlist):
    """Build the slice, collect exact (t, G) in one chamber, reconstruct."""
    pts = []
    s0 = None
    for t in tlist:
        free = (F(w2), F(w3), F(a4) + t, F(w5))
        oms = cn.solve_squares(free)
        if oms is None or any(w == 0 for w in oms):
            continue
        sq = [w * w for w in oms]
        ws = cn.wall_signs(sq)
        if ws is None:
            continue
        # also fix same-type orderings so we stay in ONE analytic piece
        a, b = sq[0:3], sq[3:6]
        if 0 in [a[0]-a[1], a[0]-a[2], a[1]-a[2], b[0]-b[1], b[0]-b[2], b[1]-b[2]]:
            continue
        sa = tuple(1 if a[i] > a[j] else -1 for i, j in [(0,1),(0,2),(1,2)])
        sb = tuple(1 if b[i] > b[j] else -1 for i, j in [(0,1),(0,2),(1,2)])
        sig = ws + (sa, sb)
        if s0 is None:
            s0 = sig
        elif sig != s0:
            continue
        try:
            im, _, _ = h.on_shell(list(free), SIG)
        except Exception:
            continue
        sumF = sum(free)
        G = im * sumF ** 8
        pts.append((t, G))
    return pts, s0


if __name__ == "__main__":
    # chamber-interior slice
    w2, w3, w5, a4 = F(1), F(-27, 10), F(12, 5), F(43, 10)
    tlist = [F(k, 120) for k in range(-90, 91)]
    pts, s0 = run_slice(w2, w3, w5, a4, tlist)
    print(f"in-chamber exact points: {len(pts)}")
    res = reconstruct(pts)
    if res is None:
        print("reconstruction failed (raise degree cap)")
        raise SystemExit
    dN, dD, Nc, Dc = res
    print(f"reconstructed: deg N = {dN}, deg D = {dD}  (D=0 would mean polynomial)")
    t = sp.Symbol('t')
    Dpoly = sum(sp.Rational(c.numerator, c.denominator) * t ** k for k, c in enumerate(Dc))
    Npoly = sum(sp.Rational(c.numerator, c.denominator) * t ** j for j, c in enumerate(Nc))
    Dfac = sp.factor(Dpoly)
    print(f"D(t) factored: {Dfac}")
    # sumFree(t) = w2+w3+w5 + (a4 + t)
    sumF_t = sp.Rational((w2 + w3 + w5 + a4).numerator, (w2 + w3 + w5 + a4).denominator) + t
    print(f"sumFree(t) = {sp.expand(sumF_t)}")
    # remove sumFree powers from D
    Dred = sp.cancel(Dpoly / sumF_t ** 8)
    print(f"D / sumFree^8 = {sp.factor(Dred)}")
    # identify k_B(t) for B subset {2,3,4,5}: only 4 varies, so quadratic in t
    print("\nCandidate k_B(t) for B subset of free legs {2,3,4,5} (varying leg 4):")
    import itertools
    free_legs = [2, 3, 4, 5]   # 1-indexed
    wvals = {2: sp.Rational(w2.numerator, w2.denominator),
             3: sp.Rational(w3.numerator, w3.denominator),
             4: sp.Rational(a4.numerator, a4.denominator) + t,
             5: sp.Rational(w5.numerator, w5.denominator)}
    sgn = {2: -1, 3: -1, 4: 1, 5: 1}
    for r in range(1, 5):
        for B in itertools.combinations(free_legs, r):
            kB = sum(sgn[i] * wvals[i] ** 2 for i in B)
            kB = sp.expand(kB)
            if kB == 0 or kB.is_number:
                continue
            print(f"   k_{B} = {kB}    roots: {sp.solve(kB, t)}")
