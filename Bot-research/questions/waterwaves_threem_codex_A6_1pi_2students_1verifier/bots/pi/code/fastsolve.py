#!/usr/bin/env python3
"""
fastsolve.py -- fast EXACT consistency / rank test + exact rational recovery for a
linear system  A x = y  with INTEGER (or Fraction) entries.

Purpose (round 8): the round-7 hinge-orbit test died because a pure-Python SCALAR
Gaussian elimination did full row reduction inside every pivot loop and never
finished, and (separately) the assembled matrix omitted the 17 R0 columns.  This
module replaces the slow elimination with a VECTORIZED modular rank test (seconds,
not minutes) and gives an exact rational recovery only on the pivotal subsystem.

Decisive science:
  * consistent (a solution exists) IFF rank(A) == rank([A|y]) at EVERY prime;
  * if inconsistent -> y is NOT in the span of your building blocks: a genuine
    obstruction (the hinge/nested-truncated-power algebra is insufficient as posed).

The matrix build (features + R0 basis) is YOURS; feed A and y here.  A must include
BOTH the hinge-orbit feature columns AND the 17 global dual-S3 R0 basis columns,
or the test is meaningless (that was the round-7 bug).

Author: PI (bots/pi/code).  Verified on synthetic systems before hand-off.
"""
import numpy as np
from fractions import Fraction

# three primes < 2^31 so that products fit in int64 (p^2 < 9.22e18)
PRIMES = [2147483647, 2147483629, 2147483587]


def _echelon_mod(M, p):
    """Forward elimination mod p (fully vectorized). Returns (rank, pivot_cols, pivot_rows).
    pivot_rows are indices into the ORIGINAL row order that became pivots."""
    A = (np.asarray(M, dtype=object)  # object->int64 after reduce, keeps big ints safe
         ).astype(np.int64)
    A = A % p
    n, m = A.shape
    row = 0
    rank = 0
    pivot_cols = []
    perm = np.arange(n)  # track original row indices
    for col in range(m):
        sub = A[row:, col] % p
        nz = np.nonzero(sub)[0]
        if nz.size == 0:
            continue
        piv = row + int(nz[0])
        if piv != row:
            A[[row, piv]] = A[[piv, row]]
            perm[[row, piv]] = perm[[piv, row]]
        inv = pow(int(A[row, col]), p - 2, p)
        A[row] = (A[row] * inv) % p
        below = A[row + 1:]
        if below.shape[0]:
            factors = (below[:, col] % p).reshape(-1, 1)
            A[row + 1:] = (below - factors * A[row]) % p
        pivot_cols.append(col)
        pivot_rows = perm[:row + 1].copy()
        row += 1
        rank += 1
        if row == n:
            break
    return rank, pivot_cols, perm[:rank].copy()


def rank_mod(M, p):
    return _echelon_mod(M, p)[0]


def consistency(A, y, primes=PRIMES, verbose=True):
    """Return dict with rank(A), rank([A|y]) per prime and overall 'consistent' bool.
    A: 2D int array (rows=samples, cols=features incl R0). y: 1D int array (target S)."""
    A = np.asarray(A, dtype=object).astype(np.int64)
    y = np.asarray(y, dtype=object).astype(np.int64).reshape(-1, 1)
    Ay = np.hstack([A, y])
    out = {"per_prime": [], "consistent": True, "rank_A": None}
    for p in primes:
        rA = rank_mod(A, p)
        rAy = rank_mod(Ay, p)
        out["per_prime"].append({"p": p, "rank_A": rA, "rank_Ay": rAy})
        if rAy != rA:
            out["consistent"] = False
        out["rank_A"] = rA
        if verbose:
            print(f"  p={p}: rank(A)={rA}  rank([A|y])={rAy}  "
                  f"{'CONSISTENT' if rAy == rA else 'INCONSISTENT (no solution in this basis)'}")
    return out


def exact_solve(A, y, primes=PRIMES):
    """If consistent, return an EXACT rational solution vector x (free vars = 0) as a
    list of Fraction, plus the set of pivotal column indices used. Verifies x on ALL
    rows with exact Fraction arithmetic. Returns (x, pivot_cols, residual_ok:bool)."""
    con = consistency(A, y, primes, verbose=False)
    if not con["consistent"]:
        return None, None, False
    p0 = primes[0]
    rank, pivot_cols, pivot_rows = _echelon_mod(A, p0)
    # square exact system: rows = pivot_rows, cols = pivot_cols, free cols set to 0
    Af = [[Fraction(int(A[r][c])) for c in pivot_cols] for r in pivot_rows]
    yf = [Fraction(int(y[r])) for r in pivot_rows]
    # Gaussian elimination with Fraction on the rank x rank system
    n = len(pivot_cols)
    M = [Af[i] + [yf[i]] for i in range(n)]
    for i in range(n):
        # find nonzero pivot
        piv = next((r for r in range(i, n) if M[r][i] != 0), None)
        if piv is None:
            return None, None, False
        M[i], M[piv] = M[piv], M[i]
        inv = M[i][i]
        M[i] = [v / inv for v in M[i]]
        for r in range(n):
            if r != i and M[r][i] != 0:
                f = M[r][i]
                M[r] = [M[r][k] - f * M[i][k] for k in range(n + 1)]
    xpiv = [M[i][n] for i in range(n)]
    x = [Fraction(0)] * A.shape[1]
    for c, val in zip(pivot_cols, xpiv):
        x[c] = val
    # exact verify on ALL rows
    ok = True
    for r in range(A.shape[0]):
        s = sum(Fraction(int(A[r][c])) * x[c] for c in range(A.shape[1]) if x[c] != 0)
        if s != Fraction(int(y[r])):
            ok = False
            break
    return x, pivot_cols, ok


if __name__ == "__main__":
    # self-test: consistent system + inconsistent system
    import random
    random.seed(0)  # deterministic; do not rely on this in the real run
    ncol, nrow = 40, 120
    Atrue = np.array([[random.randint(-9, 9) for _ in range(ncol)] for _ in range(nrow)])
    xtrue = np.array([random.randint(-5, 5) for _ in range(ncol)])
    y = Atrue.dot(xtrue)
    print("[self-test 1] consistent system (should be CONSISTENT, rank<=40):")
    consistency(Atrue, y)
    x, piv, ok = exact_solve(Atrue, y)
    print("  exact recovery verifies on all rows:", ok)
    y2 = y.copy(); y2[0] += 1  # break consistency
    print("[self-test 2] perturbed target (should be INCONSISTENT):")
    consistency(Atrue, y2)
