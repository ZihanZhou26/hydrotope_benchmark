#!/usr/bin/env python3
"""PI round-3: find the DENOMINATOR of the rational A_6 (three-minus).

Strategy: move along an on-shell line in free coords (w2,w3,w4,w5) chosen so that
sumFree = w2+w3+w4+w5 is CONSTANT (sum of the direction's free components = 0).
Then the on-shell solve gives w1,w6 as degree-<=2 POLYNOMIALS in the line param t
(no spurious sumFree denominator), so all six omega_i are polynomials in t, and
A_6(t) = N(t)/D(t) is a rational function whose denominator D(t) is exactly the
product of the genuine |k_S| / propagator factors evaluated along the line.

We:
 (1) exact-rational-interpolate A_6(t): find the minimal denominator degree dD;
 (2) factor D(t) and match its roots to candidate loci  |k_S|(t) and
     (omega_S^2 - |k_S|)(t)  to read off WHICH subset magnitudes survive.

Self-contained; uses only my own ./bg in exact --amp mode.
"""
import subprocess, re
from fractions import Fraction as F
from itertools import combinations

BG = "./bg"
SIG = [-1, -1, -1, 1, 1, 1]

def onshell(freeW):
    s0 = SIG[0]
    sumFree = sum(freeW)
    sumSig = sum(SIG[i + 1] * freeW[i] ** 2 for i in range(4))
    wn = -(s0 * sumFree ** 2 + sumSig) / (2 * s0 * sumFree)
    w1 = -(sumFree + wn)
    W = [w1] + list(freeW) + [wn]
    K = [SIG[i] * W[i] ** 2 for i in range(6)]
    return W, K

def amp(K, W):
    Ks = ",".join(str(F(k)) for k in K); Ws = ",".join(str(F(w)) for w in W)
    out = subprocess.run([BG, "--amp", "-K", Ks, "-W", Ws, "-g", "1"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if out.returncode != 0:
        return None
    m = re.search(r"A_\d+ = i \* \(([-0-9/]+)\)", out.stdout)
    if m: return F(m.group(1))
    m = re.search(r"A_\d+ = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)", out.stdout)
    if m:
        assert F(m.group(1)) == 0; return F(m.group(2))
    raise RuntimeError(out.stdout)

# ---- exact null-space (one vector) of a rational matrix, via RREF ----
def nullvec(rows):
    """Return a nonzero rational vector x with rows·x = 0, or None if only trivial."""
    M = [r[:] for r in rows]
    nr = len(M); nc = len(M[0])
    pivots = []
    r = 0
    for c in range(nc):
        pr = next((i for i in range(r, nr) if M[i][c] != 0), None)
        if pr is None:
            continue
        M[r], M[pr] = M[pr], M[r]
        inv = M[r][c]; M[r] = [x / inv for x in M[r]]
        for i in range(nr):
            if i != r and M[i][c] != 0:
                f = M[i][c]; M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        pivots.append(c); r += 1
        if r == nr: break
    free_cols = [c for c in range(nc) if c not in pivots]
    if not free_cols:
        return None
    fc = free_cols[0]
    x = [F(0)] * nc; x[fc] = F(1)
    for idx, c in enumerate(pivots):
        x[c] = -M[idx][fc]
    return x

def rational_interp(ts, ys, dN, dD):
    """Find N (deg dN), D (deg dD, monic-ish) with N(t)=y*D(t) at all sample pts.
       Returns (Ncoef, Dcoef) or None if no nontrivial solution of that bidegree."""
    # unknowns: N_0..N_dN, D_0..D_dD ; equation per point: sum N_i t^i - y*sum D_j t^j = 0
    rows = []
    for t, y in zip(ts, ys):
        row = [t ** i for i in range(dN + 1)] + [-y * t ** j for j in range(dD + 1)]
        rows.append(row)
    x = nullvec(rows)
    if x is None:
        return None
    N = x[:dN + 1]; D = x[dN + 1:]
    if all(d == 0 for d in D):
        return None
    return N, D

def poly_eval(c, t):
    return sum(ci * t ** i for i, ci in enumerate(c))

def find_minimal_denominator(base_free, direction, npts=60, denom=240):
    # build in-chamber sample points (sumFree constant since sum(direction)=0)
    assert sum(direction) == 0, "direction must preserve sumFree"
    pts = []
    sig0 = None
    for k in range(-npts, npts + 1):
        t = F(k, denom)
        free = [base_free[i] + t * direction[i] for i in range(4)]
        W, K = onshell(free)
        if any(w == 0 for w in W):
            continue
        if any(sum(K[i] for i in S) == 0 for r in range(1, 6) for S in combinations(range(6), r)):
            continue
        cs = tuple(1 if sum(K[i] for i in S) > 0 else -1
                   for r in range(1, 6) for S in combinations(range(6), r)) + \
             tuple(1 if w > 0 else -1 for w in W)
        if sig0 is None: sig0 = cs
        if cs != sig0: continue
        a = amp(K, W)
        if a is None: continue
        pts.append((t, a))
    ts = [p[0] for p in pts]; ys = [p[1] for p in pts]
    print(f"  in-chamber points: {len(pts)}  (sumFree const = {sum(base_free)})")
    # search minimal bidegree.  A_6 homog deg 8; along a deg-<=2-in-t curve numerator/denominator
    # degrees can be sizeable.  Scan dD upward; for each, set dN so we have enough eqns.
    for dD in range(0, 17):
        dN = dD + 16   # generous numerator headroom
        need = dN + dD + 2
        if len(pts) < need + 4:
            print(f"  dD={dD}: need {need}+4 pts, have {len(pts)} -- stop"); break
        res = rational_interp(ts[:need], ys[:need], dN, dD)
        if res is None:
            continue
        N, D = res
        # verify on held-out points
        ok = True
        for t, y in zip(ts[need:], ys[need:]):
            if poly_eval(N, t) != y * poly_eval(D, t):
                ok = False; break
        if ok:
            # strip common low-order; report normalized D
            print(f"  >>> minimal denominator degree dD = {dD} (numerator deg used {dN}); verified on {len(pts)-need} held-out pts")
            return ts, ys, N, D, dD, base_free, direction
    print("  no rational model found within scanned bidegrees")
    return None

def main():
    print("=" * 72)
    print("DENOMINATOR HUNT for A_6 (three-minus), sumFree-constant on-shell line")
    base = [F(2), F(3), F(5), F(7)]
    direction = [F(1), F(-1), F(1), F(-1)]   # sum = 0 -> sumFree constant
    out = find_minimal_denominator(base, direction)
    if out is None:
        return
    ts, ys, N, D, dD, base, direction = out
    # Compare D(t) (up to scale) with candidate |k_S|(t) factors along the line.
    print("\n  Matching denominator roots to subset-magnitude loci along the line:")
    # candidate factors: same-type subset sums (sums of squares) and full Q, and propagator dens.
    def freeof(t):
        return [base[i] + t * direction[i] for i in range(4)]
    # Evaluate candidate scalar factors as functions of t at the sample points, get their
    # polynomial-in-t form by interpolation, then test if they divide D(t).
    import math
    def W_of(t):
        return onshell(freeof(t))[0]
    def K_of(t):
        return onshell(freeof(t))[1]
    # Build candidate factor polynomials in t by sampling (they are polynomials of deg<=4 in t).
    def interp_poly(fn, deg):
        xs = [F(k, 240) for k in range(deg + 1)]
        A = [[x ** i for i in range(deg + 1)] for x in xs]
        b = [fn(x) for x in xs]
        # solve exactly
        sol = solve_lin(A, b)
        return sol
    def solve_lin(A, b):
        n = len(A); M = [A[i][:] + [b[i]] for i in range(n)]
        for c in range(n):
            pr = next(i for i in range(c, n) if M[i][c] != 0)
            M[c], M[pr] = M[pr], M[c]
            inv = M[c][c]; M[c] = [x / inv for x in M[c]]
            for i in range(n):
                if i != c and M[i][c] != 0:
                    f = M[i][c]; M[i] = [a - f * b2 for a, b2 in zip(M[i], M[c])]
        return [M[i][n] for i in range(n)]
    # poly division remainder test: does q(t) divide D(t)?
    def polytrim(c):
        while len(c) > 1 and c[-1] == 0: c.pop()
        return c
    def divides(divisor, dividend):
        a = polytrim(dividend[:]); b = polytrim(divisor[:])
        if len(b) == 1:
            return b[0] != 0
        while len(a) >= len(b) and not (len(a) == 1 and a[0] == 0):
            if a[-1] == 0:
                a.pop(); continue
            f = a[-1] / b[-1]; shift = len(a) - len(b)
            for i in range(len(b)):
                a[shift + i] -= f * b[i]
            a = polytrim(a)
            if len(a) == 1:
                break
        return len(a) == 1 and a[0] == 0
    Dt = polytrim(D[:])
    print(f"    D(t) degree = {len(Dt)-1}")
    cand = {}
    # same-type pair magnitudes |k_S| = sum of squares
    pairs_plus = [(3,4),(3,5),(4,5)]; pairs_minus=[(0,1),(0,2),(1,2)]
    for (i,j) in pairs_plus+pairs_minus:
        cand[f"|k_{{{i+1},{j+1}}}|=w{i+1}^2+w{j+1}^2"] = lambda t,i=i,j=j: K_of(t)[i]+K_of(t)[j] if (i>=3 and j>=3) else -(K_of(t)[i]+K_of(t)[j])
    # mixed pair/triple magnitudes (these DO change sign across walls but as factors may appear)
    # Q = sum plus squares
    cand["Q=w4^2+w5^2+w6^2"] = lambda t: K_of(t)[3]+K_of(t)[4]+K_of(t)[5]
    # leg squares
    for i in range(6):
        cand[f"w{i+1}^2"] = lambda t,i=i: W_of(t)[i]**2
    # propagator denominators omega_S^2 - |k_S| for a few channels
    for S in [(1,2,3),(1,2,4),(0,3,4),(0,1,3)]:
        cand[f"D_{{{tuple(s+1 for s in S)}}}=wS^2-|kS|"] = (
            lambda t,S=S: (sum(W_of(t)[s] for s in S))**2 - abs(sum(K_of(t)[s] for s in S)))
    for name, fn in cand.items():
        # degree of candidate in t: sample-fit up to deg 4
        try:
            poly = None
            for dg in range(0,5):
                p = interp_poly(fn, dg)
                # check it's actually degree dg (consistency by one more pt)
                xt = F(99,240);
                if poly_eval(p, xt) == fn(xt):
                    poly = polytrim(p); break
            if poly is None:
                continue
            d = divides(poly, Dt)
            print(f"    {'DIVIDES ' if d else '         '} {name}   (deg {len(poly)-1})")
        except Exception as e:
            print(f"    [skip {name}: {e}]")

if __name__ == "__main__":
    main()
