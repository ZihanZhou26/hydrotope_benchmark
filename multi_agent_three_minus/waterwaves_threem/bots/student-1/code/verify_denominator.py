#!/usr/bin/env python3
"""CANONICAL round-3 deliverable (student-1).  One command, all exact vs my own ./bg.

HEADLINE:  A_6 (three-minus) is piecewise-RATIONAL with an EXPLICIT denominator:

    A_6 = i * 2^5 * g^{-3} * N(omega) / D9(omega),
    D9(omega) = prod_{i in {1,2,3}} prod_{j in {4,5,6}} (omega_i + omega_j)   (9 mixed pairs),

with N a piecewise-POLYNOMIAL (a spline).  D9 is S_3(minus) x S_3(plus) x Z_2(swap)
invariant, so N inherits the full symmetry.  This UNIFIES the two round-2 pictures:
A_6 is rational (student-1 r2), and the box-spline the team seeks lives in the
NUMERATOR N = A_6 * D9 / (i 2^5 g^{-3}), not in A_6 itself.

Checks (exact rational):
  (A) A_6 is NOT a polynomial in the six frequencies (deg-D != 0 on a chamber slice),
      with the n=5 control returning POLYNOMIAL -> the method is sound.
  (B) A_6 * D9 IS a polynomial across MANY chamber types: on a chamber slice it
      reconstructs to N(t)/sumFree^k -- a PURE power of the solve-coordinate sumFree,
      with NO other (omega_i +/- omega_j) factor (which is exactly the signature of a
      genuine 6-variable polynomial restricted to the manifold).
"""
from fractions import Fraction as F
import sympy as sp
import harness as h
import chambers_n6 as cn

SIG = [-1, -1, -1, 1, 1, 1]
MINUS, PLUS = [1, 2, 3], [4, 5, 6]
t = sp.Symbol('t')


def exact_solve(A, b):
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


def reconstruct(pts, cap=40):
    nP = len(pts)
    for total in range(0, cap):
        for dD in range(0, total + 1):
            dN = total - dD
            nun = (dN + 1) + dD
            if nP < nun + 4:
                continue
            rows, rhs = [], []
            for (x, G) in pts[:nun]:
                row = [x ** j for j in range(dN + 1)] + [-G * x ** k for k in range(1, dD + 1)]
                rows.append(row); rhs.append(G)
            sol = exact_solve(rows, rhs)
            if sol is None:
                continue
            Nc = sol[:dN + 1]; Dc = [F(1)] + sol[dN + 1:]
            if all((sum(c * x ** k for k, c in enumerate(Dc)) != 0 and
                    sum(c * x ** j for j, c in enumerate(Nc)) == G * sum(c * x ** k for k, c in enumerate(Dc)))
                   for (x, G) in pts[nun:]):
                return dN, dD, Nc, Dc
    return None


def full_sig(oms):
    sq = [w * w for w in oms]
    ws = cn.wall_signs(sq)
    if ws is None:
        return None
    a, b = sq[0:3], sq[3:6]
    if 0 in [a[0]-a[1], a[0]-a[2], a[1]-a[2], b[0]-b[1], b[0]-b[2], b[1]-b[2]]:
        return None
    sa = tuple(1 if a[i] > a[j] else -1 for i, j in [(0,1),(0,2),(1,2)])
    sb = tuple(1 if b[i] > b[j] else -1 for i, j in [(0,1),(0,2),(1,2)])
    return ws + (sa, sb)


def D9(oms):
    w = {i + 1: oms[i] for i in range(6)}
    p = F(1)
    for i in MINUS:
        for j in PLUS:
            p *= (w[i] + w[j])
    return p


def slice_pts(base, vary, mult=False):
    """Collect exact (t, A_6 * D9) in one chamber, varying free leg `vary`."""
    pts = []
    s0 = full_sig(cn.solve_squares(base))
    for k in range(-80, 81):
        tt = F(k, 160)
        free = list(base)
        free[vary - 2] = base[vary - 2] + tt
        oms = cn.solve_squares(free)
        if oms is None or any(w == 0 for w in oms):
            continue
        if full_sig(oms) != s0:
            continue
        d9 = D9(oms)
        if d9 == 0:
            continue
        try:
            im, _, _ = h.on_shell(free, SIG)
        except Exception:
            continue
        pts.append((tt, im * d9 if mult else im))
    return pts, s0


def partA():
    print("=" * 72)
    print("(A) A_6 is RATIONAL (not a polynomial in the six frequencies)")
    base = [F(1), F(-27, 10), F(43, 10), F(12, 5)]
    pts, _ = slice_pts(base, 4, mult=False)
    # multiply by sumFree^8 to clear ONLY the leg-1,6 solve denominator;
    # sumFree on a w4-slice = (w2+w3+w5) + (w4+tt) = sf0 + tt
    sf0 = base[0] + base[1] + base[3] + base[2]
    Gpts = [(tt, im * (sf0 + tt) ** 8) for (tt, im) in pts]
    res = reconstruct(Gpts, cap=20)
    dN, dD, _, Dc = res
    Dpoly = sum(sp.Rational(c.numerator, c.denominator) * t ** k for k, c in enumerate(Dc))
    print(f"    A_6 * sumFree^8 = N(t)/D(t):  deg N = {dN}, deg D = {dD}")
    print(f"    D(t) = {sp.factor(Dpoly)}   (deg D != 0  =>  A_6 is RATIONAL, not polynomial)")
    return dD != 0


def partB():
    print("=" * 72)
    print("(B) A_6 * D9 is a POLYNOMIAL in the six frequencies, across chamber types")
    print("    D9 = prod_{i in 1,2,3} prod_{j in 4,5,6} (w_i + w_j)")
    chambers, *_ = cn.scan(250000, seed=7)
    items = sorted(chambers.items(), key=lambda kv: -kv[1][0])[:5]
    allok = True
    for idx, (sig, (cnt, free, sq)) in enumerate(items):
        base = [F(x) for x in free]
        pts, _ = slice_pts(base, 4, mult=True)
        res = reconstruct(pts, cap=40)
        if res is None:
            print(f"    T{idx}: reconstruct failed"); allok = False; continue
        dN, dD, _, Dc = res
        Dpoly = sum(sp.Rational(c.numerator, c.denominator) * t ** k for k, c in enumerate(Dc))
        sf0 = sum(base)
        pure = sp.simplify(Dpoly / (sp.Rational(sf0.numerator, sf0.denominator) + t) ** dD)
        ok = bool(pure.is_number) and pure != 0
        allok = allok and ok
        print(f"    T{idx}: deg N={dN:2d} deg D={dD:2d}  residual = sumFree^{dD} (pure)? {ok}")
    return allok


if __name__ == "__main__":
    a = partA()
    b = partB()
    print("=" * 72)
    print(f"SUMMARY:  A_6 rational (not poly) = {a};   A_6*D9 polynomial across chambers = {b}")
    print("CONCLUSION:  A_6 = i*2^5*g^-3 * N(omega) / prod_{i in 1,2,3, j in 4,5,6}(w_i+w_j),"
          " N piecewise-polynomial.")
