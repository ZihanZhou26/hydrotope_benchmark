#!/usr/bin/env python3
import numpy as np
from fractions import Fraction
from math import gcd

# three primes < 2^31 so that products fit in int64 (p^2 < 9.22e18)
PRIMES = [2147483647, 2147483629, 2147483587]


def _as_mod_matrix(M, p):
    A = np.asarray(M, dtype=object)
    A = (A % p).astype(np.int64)
    return A


def _echelon_mod(M, p):
    A = _as_mod_matrix(M, p)
    n, m = A.shape
    row = 0
    rank = 0
    pivot_cols = []
    perm = np.arange(n)
    for col in range(m):
        sub = A[row:, col]
        nz = np.nonzero(sub)[0]
        if nz.size == 0:
            continue
        piv = row + int(nz[0])
        if piv != row:
            A[[row, piv]] = A[[piv, row]]
            perm[[row, piv]] = perm[[piv, row]]
        inv = pow(int(A[row, col]), p - 2, p)
        A[row] = (A[row] * inv) % p
        if row + 1 < n:
            below = A[row + 1:]
            factors = (below[:, col]).reshape(-1, 1)
            A[row + 1:] = (below - factors * A[row]) % p
        pivot_cols.append(col)
        row += 1
        rank += 1
        if row == n:
            break
    return rank, pivot_cols, perm[:rank].copy()


def _select_rows_for_rank_mod(A, p, target_rank):
    m, n = A.shape
    if target_rank <= 0 or target_rank > m or target_rank > n:
        return []
    # prefer numerically smaller rows first for faster rational recovery downstream
    row_order = sorted(
        range(m),
        key=lambda r: sum(abs(int(v)) for v in A[r, :])
    )

    basis = []
    basis_rows = []
    pivot_cols = []

    for r in row_order:
        row = [int(v) % p for v in A[r].tolist()]
        for brow, pcol in zip(basis, pivot_cols):
            factor = row[pcol]
            if factor == 0:
                continue
            for cc in range(pcol, n):
                row[cc] = (row[cc] - factor * brow[cc]) % p
        pivot = None
        for cc, val in enumerate(row):
            if val != 0:
                pivot = cc
                break
        if pivot is None:
            continue
        inv = pow(row[pivot], p - 2, p)
        row = [(v * inv) % p for v in row[pivot:]]
        # expand row back to full width
        full_row = [0] * pivot + row
        row = full_row

        for bi in range(len(basis)):
            factor = basis[bi][pivot]
            if factor == 0:
                continue
            for cc in range(pivot, n):
                basis[bi][cc] = (basis[bi][cc] - factor * row[cc]) % p

        basis.append(row)
        basis_rows.append(r)
        pivot_cols.append(pivot)
        if len(basis) >= target_rank:
            return basis_rows

    return []


def _solve_square_bareiss(A, b):
    n = A.shape[1]
    m = A.shape[0]
    if m < n:
        return None
    M = []
    for row, rhs in zip(A.tolist(), b.tolist()):
        M.append([int(v) for v in row] + [int(rhs)])
        row_vals = M[-1]
        g = 0
        for v in row_vals:
            av = abs(v)
            if av != 0:
                g = av if g == 0 else gcd(g, av)
                if g == 1:
                    break
        if g > 1:
            for j in range(n + 1):
                row_vals[j] //= g

    # use only the first n rows for square solve
    if len(M) > n:
        M = M[:n]

    prev = 1
    for col in range(n):
        piv = -1
        piv_abs = None
        for rr in range(col, n):
            v = M[rr][col]
            if v == 0:
                continue
            av = abs(v)
            if piv_abs is None or av < piv_abs:
                piv_abs = av
                piv = rr
        if piv == -1:
            return None
        if piv != col:
            M[col], M[piv] = M[piv], M[col]

        pv = M[col][col]
        if pv == 0:
            return None

        for rr in range(col + 1, n):
            if M[rr][col] == 0:
                continue
            fv = M[rr][col]
            rrrow = M[rr]
            crow = M[col]
            for cc in range(col + 1, n + 1):
                num = pv * rrrow[cc] - fv * crow[cc]
                if prev != 1:
                    if num % prev != 0:
                        return None
                    num //= prev
                rrrow[cc] = num
            rrrow[col] = 0

        if pv == 0:
            return None
        prev = pv

    x = [Fraction(0, 1)] * n
    for rr in range(n - 1, -1, -1):
        rhs = M[rr][n]
        for cc in range(rr + 1, n):
            if M[rr][cc] != 0:
                rhs -= M[rr][cc] * x[cc]
        denom = M[rr][rr]
        if denom == 0:
            return None
        x[rr] = Fraction(rhs, denom)
    return x


def rank_mod(M, p):
    return _echelon_mod(M, p)[0]


def consistency(A, y, primes=PRIMES, verbose=True):
    A = np.asarray(A, dtype=object)
    y = np.asarray(y, dtype=object).reshape(-1, 1)
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
    con = consistency(A, y, primes, verbose=False)
    if not con["consistent"]:
        return None, None, False

    A = np.asarray(A, dtype=object)
    yv = np.asarray(y, dtype=object)
    if A.shape[1] == 0:
        x = [Fraction(0)] * 0
        ok = all(Fraction(int(v)) == Fraction(0, 1) for v in yv)
        return x, [], ok

    last_info = None
    for p in primes:
        rank, pivot_cols, _ = _echelon_mod(A, p)
        if rank == 0:
            continue
        if rank > A.shape[1]:
            return None, None, False
        cols = np.array(pivot_cols, dtype=int)[:rank]
        A_sub = A[:, cols]
        y_sub = yv

        row_idx = _select_rows_for_rank_mod(A_sub, p, rank)
        if len(row_idx) < rank:
            row_idx = list(np.array(_echelon_mod(A_sub, p)[2], dtype=int))

        if len(row_idx) >= rank:
            A_sq = A_sub[row_idx[:rank], :]
            y_sq = np.array([int(y_sub[r]) for r in row_idx[:rank]], dtype=object)
        else:
            A_sq = A_sub
            y_sq = y_sub
        piv_sol = _solve_square_bareiss(A_sq, y_sq)
        last_info = (rank, cols, piv_sol)
        if piv_sol is None:
            if len(row_idx) >= rank:
                # already tried the preferred row set and it failed; retry direct pivot rows if available
                row_idx2 = np.array(_echelon_mod(A, p)[2], dtype=int)
            else:
                row_idx2 = np.array(_echelon_mod(A, p)[2], dtype=int)
            if len(row_idx2) < rank:
                continue
            A_sq2 = A_sub[row_idx2, :]
            y_sq2 = np.array([int(y_sub[r]) for r in row_idx2], dtype=object)
            piv_sol = _solve_square_bareiss(A_sq2, y_sq2)
            last_info = (rank, cols, piv_sol)
            if piv_sol is None:
                continue

        x = [Fraction(0)] * A.shape[1]
        for idx, cidx in enumerate(cols):
            x[cidx] = piv_sol[idx]

        ok = True
        for rr in range(A.shape[0]):
            s = Fraction(0, 1)
            for cc in cols:
                cval = x[cc]
                if cval != 0:
                    s += Fraction(int(A[rr][cc]), 1) * cval
            if s != Fraction(int(yv[rr])):
                ok = False
                break
        if ok:
            return x, list(cols), True

        # keep trying other primes even if residual is bad

    if last_info is not None:
        rank, cols, piv_sol = last_info
        if piv_sol is not None:
            x = [Fraction(0)] * A.shape[1]
            for idx, cidx in enumerate(cols):
                x[cidx] = piv_sol[idx]
            return x, list(cols), False
    return None, None, False
