#!/usr/bin/env python3
"""Exact bottom-up reconstruction of pair-wall bricks for round 3.

The amplitude oracle and compact pole subtraction are imported from the
round-2 driver.  Cell polynomials are reconstructed in the homogeneous
on-shell quotient basis after eliminating omega_6.  Large exact linear
systems are delegated to the locally installed Wolfram kernel; all sampling,
rank certification, quotient checks, and holdouts remain in this driver.
"""

import argparse
import importlib.util
import json
import random
import shutil
import subprocess
import time
from fractions import Fraction
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]
BOT = ROOT / "bots" / "student-2"
DATA = BOT / "data"
WOLFRAM = Path("/opt/sns/bin/WolframKernel")


def load_round2():
    path = HERE.with_name("round2_exact.py")
    spec = importlib.util.spec_from_file_location("round2_exact_local", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


R2 = load_round2()


def fstr(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else "%d/%d" % (x.numerator, x.denominator)


def parse_fraction(text):
    return Fraction(str(text).replace(" ", ""))


def homogeneous_basis(degree):
    """Exponent tuples for w1,...,w5, with exponent(w5) <= 1."""
    ans = []
    for e5 in range(min(1, degree) + 1):
        rem = degree - e5
        for e1 in range(rem + 1):
            for e2 in range(rem - e1 + 1):
                for e3 in range(rem - e1 - e2 + 1):
                    e4 = rem - e1 - e2 - e3
                    ans.append((e1, e2, e3, e4, e5))
    return ans


def signature(point, include_energy=True):
    pair, triple = point.sign_maps()
    values = []
    keys = []
    if include_energy:
        for i, w in enumerate(point.omega):
            keys.append("omega_%d" % (i + 1))
            values.append("+" if w > 0 else "-" if w < 0 else "0")
    for key in sorted(pair):
        keys.append(key)
        values.append(pair[key])
    for key in sorted(triple):
        keys.append(key)
        values.append(triple[key])
    return tuple(values), tuple(keys)


def generic_oracle_point(point):
    if not point.is_generic() or point.C == 0:
        return False
    for m in R2.MINUS_IDX:
        for p in R2.PLUS_IDX:
            if point.omega[m] + point.omega[p] == 0:
                return False
    return True


def scaled_w(point):
    """Integer W=S*omega for integral free parameters."""
    S = point.b + point.c + point.d + point.e
    vals = [w * S for w in point.omega[:5]]
    if any(v.denominator != 1 for v in vals):
        raise AssertionError("scaled coordinates were not integral")
    return tuple(v.numerator for v in vals), S


def eval_row_int(W, basis):
    powers = []
    degree = sum(basis[0])
    for x in W:
        powers.append([pow(x, k) for k in range(degree + 1)])
    return [
        powers[0][e[0]] * powers[1][e[1]] * powers[2][e[2]]
        * powers[3][e[3]] * powers[4][e[4]]
        for e in basis
    ]


class ModularRank:
    """Incremental row-rank selection over a prime field."""

    def __init__(self, ncols, prime=1000000007):
        self.ncols = ncols
        self.p = prime
        self.rows = {}

    def add(self, row):
        p = self.p
        v = [x % p for x in row]
        for pivot in sorted(self.rows):
            if v[pivot]:
                factor = v[pivot]
                base = self.rows[pivot]
                for j in range(pivot, self.ncols):
                    v[j] = (v[j] - factor * base[j]) % p
        pivot = next((j for j, x in enumerate(v) if x), None)
        if pivot is None:
            return False
        inv = pow(v[pivot], p - 2, p)
        for j in range(pivot, self.ncols):
            v[j] = v[j] * inv % p
        # Reduced pivots make later row processing cheaper and deterministic.
        for old, base in list(self.rows.items()):
            if base[pivot]:
                factor = base[pivot]
                self.rows[old] = [
                    (base[j] - factor * v[j]) % p if j >= old else base[j]
                    for j in range(self.ncols)
                ]
        self.rows[pivot] = v
        return True

    @property
    def rank(self):
        return len(self.rows)


def center_for(seed, side, scale=120, offset=6):
    B, c, e = seed
    # b<d is the L side; b>d is the R side.
    b = scale * B // 2 + (-offset if side == "L" else offset)
    d = scale * B // 2 + (offset if side == "L" else -offset)
    return (b, scale * c, d, scale * e)


def target_signature(seed, side):
    B, c, e = seed
    eps = Fraction(1, 1000)
    t = Fraction(B, 2) + (-eps if side == "L" else eps)
    point = R2.SixPoint(t, c, Fraction(B) - t, e)
    return signature(point)


def candidate_stream(seed, side, rng):
    """Local integral points in the same open conic cell."""
    center = center_for(seed, side)
    radius = 34
    while True:
        # A common positive rescaling moves through the cone; independent
        # integral perturbations provide generic projective directions.
        mult = rng.randint(1, 5)
        vals = [
            mult * x + rng.randint(-radius, radius)
            for x in center
        ]
        if sum(vals) == 0:
            continue
        try:
            yield R2.SixPoint(*vals)
        except Exception:
            continue


def evaluate_remainder(oracle, point):
    result, err = R2.safe_on_shell(
        oracle, 6, [point.b, point.c, point.d, point.e]
    )
    if result is None:
        raise RuntimeError("BG failure: %s" % err)
    omega, re_part, im_part = result
    if re_part != 0 or tuple(omega) != tuple(point.omega):
        raise AssertionError("oracle mismatch")
    remainder, pole, _ = R2.wall_pole_subtracted(point, im_part)
    return remainder, im_part, pole


def build_fresh_oracle():
    src = ROOT / "bg.cpp"
    dst = BOT / "bg.cpp"
    shutil.copy2(str(src), str(dst))
    binary = BOT / "bg"
    cmd = [
        "g++", "-O2", "-std=c++17", "-o", str(binary), str(dst),
        "-lgmpxx", "-lgmp",
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True)
    if proc.returncode:
        raise RuntimeError(proc.stderr)
    return R2.BGOracle(binary), cmd


def reconstruct_branch(oracle, seed, side, basis, rng, tag, holdouts=20):
    target, sig_keys = target_signature(seed, side)
    ranker = ModularRank(len(basis))
    selected = []
    attempts = 0
    for point in candidate_stream(seed, side, rng):
        attempts += 1
        if attempts > 200000:
            raise RuntimeError("failed to obtain full-rank sample for %s" % tag)
        if not generic_oracle_point(point):
            continue
        sig, keys = signature(point)
        if keys != sig_keys or sig != target:
            continue
        W, S = scaled_w(point)
        row = eval_row_int(W, basis)
        if ranker.add(row):
            selected.append((point, W, S, row))
            if ranker.rank == len(basis):
                break

    matrix = []
    rhs = []
    sample_records = []
    for point, W, S, row in selected:
        remainder, amp, pole = evaluate_remainder(oracle, point)
        value = remainder * (S ** 8)
        matrix.append([str(x) for x in row])
        rhs.append(fstr(value))
        sample_records.append({
            "free": [fstr(x) for x in (point.b, point.c, point.d, point.e)],
            "W": [str(x) for x in W],
            "S": fstr(S),
            "R_scaled8": fstr(value),
        })

    solve_in = DATA / ("%s_solve_input.json" % tag)
    solve_out = DATA / ("%s_solve_output.json" % tag)
    with solve_in.open("w") as fh:
        json.dump({"matrix": matrix, "rhs": rhs}, fh, separators=(",", ":"))
    solver = HERE.with_name("solve_exact.wl")
    start = time.time()
    proc = subprocess.run(
        [str(WOLFRAM), "-script", str(solver), str(solve_in), str(solve_out)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
        timeout=540,
    )
    if proc.returncode:
        raise RuntimeError("Wolfram solve failed: %s %s" % (proc.stdout, proc.stderr))
    with solve_out.open() as fh:
        solved = json.load(fh)
    coeff = [parse_fraction(x) for x in solved["coefficients"]]

    hold = []
    seen = {tuple(x["free"]) for x in sample_records}
    for point in candidate_stream(seed, side, rng):
        if len(hold) >= holdouts:
            break
        if not generic_oracle_point(point):
            continue
        sig, keys = signature(point)
        if sig != target:
            continue
        free_key = tuple(fstr(x) for x in (point.b, point.c, point.d, point.e))
        if free_key in seen:
            continue
        W, S = scaled_w(point)
        row = eval_row_int(W, basis)
        pred = sum(c * x for c, x in zip(coeff, row))
        remainder, amp, pole = evaluate_remainder(oracle, point)
        obs = remainder * (S ** 8)
        hold.append({
            "free": list(free_key),
            "observed": fstr(obs),
            "predicted": fstr(pred),
            "residual": fstr(pred - obs),
        })

    return {
        "tag": tag,
        "seed": list(seed),
        "side": side,
        "signature_keys": list(sig_keys),
        "signature": list(target),
        "attempts": attempts,
        "rank_mod_prime": ranker.rank,
        "solve_rank": solved["rank"],
        "solve_zero_residual": solved["zero_residual"],
        "solve_seconds": solved["solve_seconds"],
        "wall_seconds": time.time() - start,
        "coefficients": [fstr(x) for x in coeff],
        "nonzero_coefficients": sum(x != 0 for x in coeff),
        "samples": sample_records,
        "holdouts": hold,
        "holdout_zero_count": sum(x["residual"] == "0" for x in hold),
    }, coeff


def poly_from_coeff(coeff, basis, symbols):
    return sp.Poly(
        sum(
            sp.Rational(c.numerator, c.denominator)
            * sp.prod(symbols[i] ** e[i] for i in range(5))
            for c, e in zip(coeff, basis) if c
        ),
        *symbols, domain=sp.QQ,
    )


def fraction_coeff_map(poly):
    out = {}
    for mon, coeff in poly.terms():
        out[",".join(map(str, mon))] = str(coeff)
    return out


def reduce_w5(expr, symbols):
    w1, w2, w3, w4, w5 = symbols
    S4 = w1 + w2 + w3 + w4
    K = -w1**2 - w2**2 - w3**2 + w4**2 + S4**2
    relation = 2*w5**2 + 2*S4*w5 + K
    return sp.Poly(sp.rem(sp.Poly(sp.expand(expr), w5),
                          sp.Poly(relation, w5)).as_expr(),
                   *symbols, domain=sp.QQ)


def analyze_brick(left_coeff, right_coeff, basis8, left_q24_sign):
    symbols = sp.symbols("w1:6")
    w1, w2, w3, w4, w5 = symbols
    left = poly_from_coeff(left_coeff, basis8, symbols)
    right = poly_from_coeff(right_coeff, basis8, symbols)
    # Normalize to the intrinsic positive-minus-negative branch difference.
    # For B<0 the parameter label "L" has q24<0, reversing the raw order.
    jump = left - right if left_q24_sign == "+" else right - left
    q24 = sp.Poly(w4**2 - w2**2, *symbols, domain=sp.QQ)
    H24, rem = sp.div(jump, q24)
    if not rem.is_zero:
        raise AssertionError("jump was not exactly divisible by q24")
    H14 = sp.Poly(H24.as_expr().xreplace({w1: w2, w2: w1}),
                  *symbols, domain=sp.QQ)
    swap23 = sp.Poly(H14.as_expr().xreplace({w2: w3, w3: w2}),
                     *symbols, domain=sp.QQ) - H14
    # Under 5<->6, old w5 is replaced by w6=-(w1+...+w5), then reduced.
    swap56 = reduce_w5(
        H14.as_expr().subs({w5: -(w1+w2+w3+w4+w5)}, simultaneous=True),
        symbols,
    ) - H14
    factors = sp.factor_list(H14.as_expr())
    factor_text = str(sp.factor(H14.as_expr()))
    test_factors = {}
    candidates = {}
    for i in range(5):
        for j in range(i + 1, 5):
            candidates["w%d-w%d" % (i+1, j+1)] = symbols[i] - symbols[j]
            candidates["w%d+w%d" % (i+1, j+1)] = symbols[i] + symbols[j]
    w6 = -(w1+w2+w3+w4+w5)
    candidates["C"] = w1*w2*w3 + w4*w5*w6
    for name, candidate in candidates.items():
        quo, r = sp.div(H14, sp.Poly(candidate, *symbols, domain=sp.QQ))
        test_factors[name] = {
            "divides": bool(r.is_zero),
            "quotient_terms": len(quo.terms()) if r.is_zero else None,
        }
    return {
        "left_terms": len(left.terms()),
        "right_terms": len(right.terms()),
        "jump_terms": len(jump.terms()),
        "left_q24_sign": left_q24_sign,
        "jump_convention": "R(q24>0)-R(q24<0)",
        "q24_remainder_zero": rem.is_zero,
        "H24_terms": len(H24.terms()),
        "H14_terms": len(H14.terms()),
        "H24_coefficients": fraction_coeff_map(H24),
        "H14_coefficients": fraction_coeff_map(H14),
        "H14_factor": factor_text,
        "H14_factor_list": [
            [str(base), int(power)] for base, power in factors[1]
        ],
        "H14_swap23_zero": swap23.is_zero,
        "H14_swap56_zero": swap56.is_zero,
        "linear_and_C_factor_tests": test_factors,
    }, H24, H14


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default="10,2,3")
    parser.add_argument("--holdouts", type=int, default=20)
    parser.add_argument("--output-tag", default="round3_context_a")
    args = parser.parse_args()
    seed = tuple(int(x) for x in args.seed.split(","))
    DATA.mkdir(parents=True, exist_ok=True)
    basis8 = homogeneous_basis(8)
    basis6 = homogeneous_basis(6)
    if len(basis8) != 285 or len(basis6) != 140:
        raise AssertionError((len(basis8), len(basis6)))
    oracle, build_cmd = build_fresh_oracle()
    rng = random.Random(20260726 + sum(seed))
    t0 = time.time()
    left_record, left_coeff = reconstruct_branch(
        oracle, seed, "L", basis8, rng, args.output_tag + "_L",
        holdouts=args.holdouts,
    )
    right_record, right_coeff = reconstruct_branch(
        oracle, seed, "R", basis8, rng, args.output_tag + "_R",
        holdouts=args.holdouts,
    )
    q24_index = left_record["signature_keys"].index("q_2_4")
    left_q24_sign = left_record["signature"][q24_index]
    brick, H24, H14 = analyze_brick(
        left_coeff, right_coeff, basis8, left_q24_sign
    )
    payload = {
        "meta": {
            "seed": list(seed),
            "build_command": " ".join(build_cmd),
            "basis8_dimension": len(basis8),
            "basis6_dimension": len(basis6),
            "basis8": [list(x) for x in basis8],
            "basis6": [list(x) for x in basis6],
            "runtime_seconds": time.time() - t0,
        },
        "left": left_record,
        "right": right_record,
        "brick": brick,
    }
    out = DATA / ("%s.json" % args.output_tag)
    with out.open("w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
    report = DATA / ("%s_report.md" % args.output_tag)
    report.write_text("\n".join([
        "# Exact round-3 cell reconstruction: `%s`" % args.output_tag,
        "",
        "- seed `(B,c,e)`: `%s`" % (seed,),
        "- quotient-basis dimensions: degree 8 = %d, degree 6 = %d"
          % (len(basis8), len(basis6)),
        "- left solve: rank %s, %d/%d exact holdouts, %d nonzero coefficients"
          % (left_record["solve_rank"], left_record["holdout_zero_count"],
             len(left_record["holdouts"]), left_record["nonzero_coefficients"]),
        "- right solve: rank %s, %d/%d exact holdouts, %d nonzero coefficients"
          % (right_record["solve_rank"], right_record["holdout_zero_count"],
             len(right_record["holdouts"]), right_record["nonzero_coefficients"]),
        "- exact divisibility: `R_L-R_R = q_24 H_24`: `%s`"
          % brick["q24_remainder_zero"],
        "- terms: jump %d, H24 %d, H14 %d"
          % (brick["jump_terms"], brick["H24_terms"], brick["H14_terms"]),
        "- residual symmetry: H14 swap(2,3) `%s`; swap(5,6) `%s`"
          % (brick["H14_swap23_zero"], brick["H14_swap56_zero"]),
        "- factorization: `%s`" % brick["H14_factor"],
        "- runtime seconds: `%.3f`" % payload["meta"]["runtime_seconds"],
        "",
        "Full coefficients and holdouts: `%s`." % out,
    ]))
    print(str(out))
    print(str(report))


if __name__ == "__main__":
    main()
