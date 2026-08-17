#!/usr/bin/env python3
"""GLOBAL test of the denominator claim across several chamber types.

Claim: A_6 * D9 is a polynomial in the six frequencies, where
       D9 = prod_{i in {1,2,3}, j in {4,5,6}} (w_i + w_j).
Signature on a free-leg slice (legs 1,6 solved): A_6*D9 reconstructs to
N(t)/sumFree(t)^k -- a PURE power of sumFree (the solve-coordinate artifact),
with NO other (w_i +/- w_j) or irrational factor.  Any other residual factor
would falsify the claim for that chamber.

We pull representative interior points of distinct chamber types from a scan,
and for each run the slice test along two independent free legs.
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


def reconstruct(pts, cap=46):
    nP = len(pts)
    for total in range(0, cap):
        for dD in range(0, total + 1):
            dN = total - dD
            nun = (dN + 1) + dD
            if nP < nun + 4:
                continue
            rows, rhs = [], []
            for (x, G) in pts[:nun]:
                row = [x ** j for j in range(dN + 1)]
                row += [-G * x ** k for k in range(1, dD + 1)]
                rows.append(row); rhs.append(G)
            sol = exact_solve(rows, rhs)
            if sol is None:
                continue
            Nc = sol[:dN + 1]; Dc = [F(1)] + sol[dN + 1:]
            ok = True
            for (x, G) in pts[nun:]:
                num = sum(c * x ** j for j, c in enumerate(Nc))
                den = sum(c * x ** k for k, c in enumerate(Dc))
                if den == 0 or num != G * den:
                    ok = False; break
            if ok:
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


def slice_test(base_free, vary, half=80, dt=F(1, 160)):
    pts = []
    s0 = full_sig(cn.solve_squares(base_free))
    if s0 is None:
        return "base on wall"
    for k in range(-half, half + 1):
        tt = k * dt
        free = list(base_free)
        free[vary - 2] = base_free[vary - 2] + tt
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
        pts.append((tt, im * d9))
    if len(pts) < 30:
        return f"too few pts ({len(pts)})"
    res = reconstruct(pts)
    if res is None:
        return f"reconstruct failed ({len(pts)} pts)"
    dN, dD, Nc, Dc = res
    Dpoly = sum(sp.Rational(c.numerator, c.denominator) * t ** k for k, c in enumerate(Dc))
    sumF0 = sum(base_free)
    # pure-power-of-sumFree?  sumFree(t) = sumF0 + tt (only varied leg moves)
    sf = sp.Rational(sumF0.numerator, sumF0.denominator) + t
    pure = sp.simplify(Dpoly / sf ** dD)
    is_pure = pure.is_number and pure != 0
    return f"degN={dN} degD={dD} D(t)={sp.factor(Dpoly)}  PURE_sumFree^{dD}={is_pure}"


if __name__ == "__main__":
    chambers, raw, on_wall, degen = cn.scan(400000, seed=7)
    items = sorted(chambers.items(), key=lambda kv: -kv[1][0])
    print(f"chamber types found: {len(items)}; testing the top several\n")
    for idx, (sig, (cnt, free, sq)) in enumerate(items[:6]):
        base = [F(x) for x in free]
        print(f"--- chamber type T{idx} (count {cnt})  free={[str(x) for x in base]} ---")
        for vary in (4, 5):
            print(f"   vary w{vary}: {slice_test(base, vary)}")
