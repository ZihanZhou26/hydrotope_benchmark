#!/usr/bin/env python3
"""Regression tests for round6_piece_pipeline helpers."""

from fractions import Fraction as F
from random import Random

from round6_piece_pipeline import (
    RANK_PRIMES,
    EXTRACT_PRIMES,
    monomials_upto,
    build_rows_rhs,
    solve_linear_mod,
    crt_pair,
    rat_recon,
    rank_mod,
)


def rank_mod_reference(matrix, p):
    A = [[int(v) % p for v in row] for row in matrix]
    if not A:
        return 0
    m = len(A)
    n = len(A[0]) if m else 0
    rank = 0
    col = 0
    while col < n and rank < m:
        pivot = None
        for r in range(rank, m):
            if A[r][col] % p:
                pivot = r
                break
        if pivot is None:
            col += 1
            continue
        A[rank], A[pivot] = A[pivot], A[rank]
        inv = pow(A[rank][col], p - 2, p)
        A[rank] = [x * inv % p for x in A[rank]]

        for r in range(m):
            if r == rank:
                continue
            if A[r][col] % p == 0:
                continue
            factor = A[r][col]
            A[r] = [(a - factor * b) % p for a, b in zip(A[r], A[rank])]
        rank += 1
        col += 1
    return rank


def test_rank_primes(seed=0):
    rng = Random(seed)
    for p in RANK_PRIMES:
        for _ in range(64):
            m = rng.randint(1, 9)
            n = rng.randint(1, 9)
            M = [[rng.randint(-4, 4) for _ in range(n)] for _ in range(m)]
            got = rank_mod(M, p)
            ref = rank_mod_reference(M, p)
            if got != ref:
                print("rank mismatch", p, got, ref)
                return False
    return True


def eval_poly(coeffs, mon, x, y, z):
    out = F(0)
    for c, (a, b, cexp) in zip(coeffs, mon):
        out += c * (x ** a) * (y ** b) * (z ** cexp)
    return out


def test_reconstruction(seed=1):
    rng = Random(seed)
    deg = 3
    mon = monomials_upto(deg)
    nm = len(mon)
    if nm < 2:
        return False

    # include nontrivial sign and rational structure
    coeff_true = []
    for _ in range(nm):
        num = rng.choice([-3, -2, -1, 1, 2, 3])
        den = rng.choice([1, 1, 1, 2, 3])
        coeff_true.append(F(num, den))

    if all(c == 0 for c in coeff_true):
        coeff_true[0] = F(1)

    sample_count = max(14, nm + 4)
    pts = []
    for _ in range(sample_count):
        x = F(rng.randint(-5, 5) or 1, 1)
        y = F(rng.randint(-5, 5) or 1, 1)
        z = F(rng.randint(-5, 5) or 1, 1)
        h = eval_poly(coeff_true, mon, x, y, z)
        pts.append((x, y, z, h))

    coeffs_mod = {}
    for p in EXTRACT_PRIMES:
        M, b = build_rows_rhs(pts, mon, p)
        sol, rk = solve_linear_mod(M, b, p)
        if sol is None or rk != nm:
            print("failed linear solve", p, rk)
            return False
        coeffs_mod[p] = [v % p for v in sol]

    reconstructed = []
    for k in range(nm):
        residue = coeffs_mod[EXTRACT_PRIMES[0]][k]
        modulus = EXTRACT_PRIMES[0]
        for p in EXTRACT_PRIMES[1:]:
            residue, modulus = crt_pair(residue, modulus, coeffs_mod[p][k], p)
        fr = rat_recon(residue, modulus)
        if fr is None:
            print("rat_recon failed", k)
            return False
        reconstructed.append(fr)

    if reconstructed != coeff_true:
        print("coeff mismatch")
        print("true", coeff_true)
        print("recon", reconstructed)
        return False

    for x, y, z, target in pts:
        got = eval_poly(reconstructed, mon, x, y, z)
        if got != target:
            print("point mismatch", x, y, z, got, target)
            return False

    return True


if __name__ == "__main__":
    ok = True
    ok &= test_rank_primes(0)
    ok &= test_reconstruction(3)
    print("ROUND6_PIPELINE_TESTS", "PASS" if ok else "FAIL")
    raise SystemExit(0 if ok else 1)
