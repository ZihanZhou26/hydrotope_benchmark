#!/usr/bin/env python3
"""Decisive independent test of student-2's Q_T-wall claim (s2_009).

Build a genuine ON-SHELL POLYNOMIAL line omega(t) = P + t*d (all six omega_i
degree-1 in t, exactly on-shell for all t). Along such a line R_spline(t) is a
genuine degree-<=8 polynomial in t PROVIDED omega(t) stays inside one polynomial
cell of R_spline. If R_spline's cells are ONLY the magnitude-tie walls
|omega_i|=|omega_j|, then across a factorization wall Q_{m;pq}=0 (which is NOT a
magnitude tie) R_spline(t) must remain a SINGLE degree-8 polynomial. If instead
R_spline jumps at Q_T=0, a degree-8 fit from one side fails to predict the other.

On-shell line conditions on d: sum d_i = 0 ; sum sigma_i P_i d_i = 0 ;
sum sigma_i d_i^2 = 0. Then omega(t) satisfies both conservation laws for all t.
"""
from fractions import Fraction as F
from r4_verify import amp_from_omega, P_pole, R_spline, SIG, _fmt, M, P
import itertools

# ---------- exact rational linear algebra ----------
def nullspace(rows, ncol):
    """Return a rational basis (list of vectors) of the nullspace of `rows`."""
    A = [[F(x) for x in r] for r in rows]
    nr = len(A)
    pivots = []
    r = 0
    for c in range(ncol):
        piv = None
        for i in range(r, nr):
            if A[i][c] != 0:
                piv = i; break
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        inv = F(1)/A[r][c]
        A[r] = [x*inv for x in A[r]]
        for i in range(nr):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [A[i][j]-f*A[r][j] for j in range(ncol)]
        pivots.append(c); r += 1
        if r == nr: break
    free = [c for c in range(ncol) if c not in pivots]
    basis = []
    for fc in free:
        v = [F(0)]*ncol
        v[fc] = F(1)
        for ri, pc in enumerate(pivots):
            v[pc] = -A[ri][fc]
        basis.append(v)
    return basis

def find_direction(Pt):
    """Find rational d != 0 with sum d=0, sum sigma P d=0, sum sigma d^2=0."""
    L1 = [1,1,1,1,1,1]
    L2 = [SIG[i]*Pt[i] for i in range(6)]
    basis = nullspace([L1, L2], 6)      # 4-dim
    # d = sum c_k basis[k]; impose quadratic sum sigma_i d_i^2 = 0.
    nb = len(basis)
    best = None
    for c in itertools.product(range(-6,7), repeat=nb):
        if all(x==0 for x in c):
            continue
        d = [sum(c[k]*basis[k][i] for k in range(nb)) for i in range(6)]
        q = sum(SIG[i]*d[i]*d[i] for i in range(6))
        if q == 0:
            # prefer directions where all |omega_i| stay distinct & moving
            best = d
            # scale to integers
            from math import gcd
            dens = [x.denominator for x in d]
            L = 1
            for dd in dens: L = L*dd//gcd(L,dd)
            d = [x*L for x in d]
            g = 0
            for x in d: g = gcd(g, x.numerator)
            if g: d = [F(x.numerator//g, 1) for x in d]
            return d
    return best

def omega_of_t(Pt, d, t):
    t = F(t)
    return [Pt[i] + t*d[i] for i in range(6)]

def word_of(omega):
    """sorted |omega| order with sigma signs -> the 8-word / magnitude cell id."""
    order = sorted(range(6), key=lambda i: abs(omega[i]))
    return tuple(SIG[i] for i in order), tuple(order)

def QT_signs(omega):
    s = {}
    for m in M:
        for pq in itertools.combinations(P,2):
            p,q = pq
            Q = omega[p]**2+omega[q]**2-omega[m]**2
            s[(m,pq)] = (0 if Q==0 else (1 if Q>0 else -1))
    return s

def q_signs(omega):
    s = {}
    for m in M:
        for p in P:
            v = omega[p]**2-omega[m]**2
            s[(m,p)] = (0 if v==0 else (1 if v>0 else -1))
    return s

# polynomial fit: solve for coeffs of degree-deg poly through (t_i, y_i) exactly
def poly_fit(ts, ys, deg):
    n = deg+1
    assert len(ts) >= n
    # Vandermonde solve (use first n points), exact
    Aug = []
    for i in range(n):
        row = [ts[i]**j for j in range(n)] + [ys[i]]
        Aug.append(row)
    # gaussian elimination
    for c in range(n):
        piv = next(r for r in range(c,n) if Aug[r][c]!=0)
        Aug[c],Aug[piv]=Aug[piv],Aug[c]
        inv=F(1)/Aug[c][c]
        Aug[c]=[x*inv for x in Aug[c]]
        for r in range(n):
            if r!=c and Aug[r][c]!=0:
                f=Aug[r][c]
                Aug[r]=[Aug[r][j]-f*Aug[c][j] for j in range(n+1)]
    return [Aug[r][n] for r in range(n)]

def poly_eval(coeffs, t):
    return sum(coeffs[j]*t**j for j in range(len(coeffs)))

if __name__ == "__main__":
    # generic on-shell base point (distinct magnitudes), from -n solver style
    from r4_verify import solve_onshell
    Pt = solve_onshell(F(13,5), F(17,3), F(9,4), F(29,7))
    print("base omega:", [_fmt(x) for x in Pt])
    print("on-shell:", _fmt(sum(Pt)), _fmt(sum(SIG[i]*Pt[i]**2 for i in range(6))))
    d = find_direction(Pt)
    print("direction d:", [_fmt(x) for x in d])
    # verify line stays on-shell at a few t
    for t in [F(-2), F(1,2), F(3)]:
        o = omega_of_t(Pt,d,t)
        assert sum(o)==0 and sum(SIG[i]*o[i]**2 for i in range(6))==0, "off-shell!"
    print("line is exactly on-shell (checked).")

    # scan t to map magnitude-cell (word) and Q_T sign changes
    import numpy as np
    print("\n t        word_signs           QT-sign-vector")
    prev=None
    ts_scan=[F(k,4) for k in range(-40,41)]
    rows=[]
    for t in ts_scan:
        o=omega_of_t(Pt,d,t)
        w,order=word_of(o)
        qt=QT_signs(o)
        qq=q_signs(o)
        rows.append((t,w,order,qt,qq))
    # find windows of constant word where a single Q_T flips
    print("\nMagnitude-cell (word) segments along the line:")
    seg_start=ts_scan[0]; cur=rows[0][1:3]
    for i in range(1,len(rows)):
        if rows[i][1:3]!=cur:
            print(f"  t in [{_fmt(seg_start)}, {_fmt(ts_scan[i-1])}]  word={cur[0]} order={cur[1]}")
            seg_start=ts_scan[i]; cur=rows[i][1:3]
    print(f"  t in [{_fmt(seg_start)}, {_fmt(ts_scan[-1])}]  word={cur[0]} order={cur[1]}")
