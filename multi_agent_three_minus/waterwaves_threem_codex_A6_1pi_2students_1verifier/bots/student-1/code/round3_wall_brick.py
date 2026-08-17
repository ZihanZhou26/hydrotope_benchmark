#!/usr/bin/env python3

from fractions import Fraction
from pathlib import Path
import json
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import pole_batch as pb
import round3_nested as rn


SIGMA = pb.SIGMA


def fs(x):
    return pb.frac_to_str(Fraction(x))


def omega_path(B, c, e, t):
    B = Fraction(B)
    c = Fraction(c)
    e = Fraction(e)
    t = Fraction(t)
    b = t
    d = B - t
    S = b + c + d + e
    a = d + e + (b * c - d * e) / S
    f = b + c - (b * c - d * e) / S
    omega = (-a, b, c, d, e, -f)
    if not pb.on_shell(omega):
        raise RuntimeError("constructed path is not on shell")
    return omega


def eval_remainder(oracle, omega):
    _, _, pole = pb.build_channels(omega)
    bg = oracle._run_amp(omega, sigma=SIGMA)
    if bg["re"] != 0:
        raise RuntimeError("unexpected real amplitude")
    return bg["im"] - pole


def polyfit(xs, ys, degree):
    A = [[x ** j for j in range(degree + 1)] for x in xs]
    labels = ["x_%s" % fs(x) for x in xs]
    ok, coeff, rank, rank_aug, witness = rn.gauss_solve_exact(A, ys, labels)
    if not ok or rank != degree + 1:
        raise RuntimeError(
            "polynomial fit failed: degree=%d rank=%d/%d witness=%r"
            % (degree, rank, rank_aug, witness)
        )
    return coeff


def polyval(coeff, x):
    return sum(a * x ** j for j, a in enumerate(coeff))


def polyder_at(coeff, x):
    return sum(Fraction(j) * coeff[j] * x ** (j - 1) for j in range(1, len(coeff)))


def q_pattern_at(omega):
    return tuple(
        1 if ch["Q"] > 0 else -1 if ch["Q"] < 0 else 0
        for ch in rn.build_all_channels(omega)
    )


def extract_h24(oracle, B, c, e):
    B = Fraction(B)
    c = Fraction(c)
    e = Fraction(e)
    t0 = B / 2
    step = Fraction(1, 10000)
    offsets = [step * j for j in range(1, 12)]
    left_t = [t0 - z for z in offsets]
    right_t = [t0 + z for z in offsets]

    left_rows = [(t, omega_path(B, c, e, t)) for t in left_t]
    right_rows = [(t, omega_path(B, c, e, t)) for t in right_t]

    left_signatures = {pb.chamber_signature(w) for _, w in left_rows}
    right_signatures = {pb.chamber_signature(w) for _, w in right_rows}
    left_q = {q_pattern_at(w) for _, w in left_rows}
    right_q = {q_pattern_at(w) for _, w in right_rows}
    if len(left_signatures) != 1 or len(right_signatures) != 1:
        raise RuntimeError("another subset wall crosses the local t stencil")
    if len(left_q) != 1 or len(right_q) != 1:
        raise RuntimeError("a Q wall crosses the local t stencil")

    left_y = [eval_remainder(oracle, w) for _, w in left_rows]
    right_y = [eval_remainder(oracle, w) for _, w in right_rows]

    degree = 8
    p_left = polyfit(left_t[: degree + 1], left_y[: degree + 1], degree)
    p_right = polyfit(right_t[: degree + 1], right_y[: degree + 1], degree)
    for t, y in zip(left_t[degree + 1 :], left_y[degree + 1 :]):
        if polyval(p_left, t) != y:
            raise RuntimeError("left branch holdout failed")
    for t, y in zip(right_t[degree + 1 :], right_y[degree + 1 :]):
        if polyval(p_right, t) != y:
            raise RuntimeError("right branch holdout failed")

    wall_left = polyval(p_left, t0)
    wall_right = polyval(p_right, t0)
    if wall_left != wall_right:
        raise RuntimeError("remainder is not continuous at q24 in extracted branches")

    # q24=(B-t)^2-t^2=-2B(t-B/2).  This order matches the
    # independently supplied positive anchor at (B,c,e)=(10,2,3).
    h24 = (polyder_at(p_left, t0) - polyder_at(p_right, t0)) / (-2 * B)
    wall_omega = omega_path(B, c, e, t0)
    return {
        "B": fs(B),
        "c": fs(c),
        "e": fs(e),
        "omega_wall": [fs(x) for x in wall_omega],
        "H24": fs(h24),
        "left_signature": next(iter(left_signatures)),
        "right_signature": next(iter(right_signatures)),
        "left_Q_pattern": list(next(iter(left_q))),
        "right_Q_pattern": list(next(iter(right_q))),
        "branch_degrees": [degree, degree],
        "holdouts_each_side": len(offsets) - degree - 1,
    }, h24


def fit_affine_line_h24(oracle):
    B = Fraction(10)
    L = Fraction(6)
    train_u = [
        Fraction(7, 6), Fraction(4, 3), Fraction(3, 2),
        Fraction(5, 3), Fraction(11, 6), Fraction(2), Fraction(13, 6),
    ]
    same_cell_hold_u = [Fraction(7, 3), Fraction(5, 2)]
    cross_cell_u = [
        Fraction(-4), Fraction(-3), Fraction(-2),
        Fraction(-1), Fraction(-1, 2), Fraction(1, 2),
        Fraction(11, 2), Fraction(13, 2), Fraction(7),
        Fraction(9), Fraction(10),
    ]
    all_u = train_u + same_cell_hold_u + cross_cell_u
    extracted = []
    for u in all_u:
        row, h = extract_h24(oracle, B, u, L - u)
        row["u"] = fs(u)
        row["wall_Q_pattern"] = list(q_pattern_at(omega_path(B, u, L - u, B / 2)))
        extracted.append((u, h, row))

    train = extracted[: len(train_u)]
    coeff = polyfit([u for u, _, _ in train], [h for _, h, _ in train], 6)
    residuals = []
    for u, h, row in extracted[len(train_u) :]:
        pred = polyval(coeff, u)
        residuals.append(
            {
                "u": fs(u),
                "kind": "same_cell" if u in same_cell_hold_u else "cross_cell",
                "wall_Q_pattern": row["wall_Q_pattern"],
                "actual_H24": fs(h),
                "predicted_training_branch": fs(pred),
                "exact_residual": fs(h - pred),
            }
        )
    same_nonzero = sum(
        1 for r in residuals if r["kind"] == "same_cell" and Fraction(r["exact_residual"]) != 0
    )
    cross_nonzero = sum(
        1 for r in residuals if r["kind"] == "cross_cell" and Fraction(r["exact_residual"]) != 0
    )
    if same_nonzero:
        raise RuntimeError("same-cell H24 affine-line holdout failed")
    return {
        "B": fs(B),
        "c_plus_e": fs(L),
        "parameterization": "c=u, e=L-u; all six wall frequencies are affine in u",
        "training_u": [fs(u) for u in train_u],
        "training_Q_pattern": extracted[0][2]["wall_Q_pattern"],
        "degree": 6,
        "coefficients_ascending": [fs(x) for x in coeff],
        "same_cell_holdout_nonzero": same_nonzero,
        "cross_cell_holdout_nonzero": cross_nonzero,
        "residual_rows": residuals,
        "status": "single_polynomial_rejected" if cross_nonzero else "single_polynomial_survives",
    }


def main():
    qdir = SCRIPT_DIR.parents[2]
    oracle = pb.BGOracle(qdir / "bots/student-1/bg", sigma=SIGMA, g=1)

    anchor_row, anchor_h = extract_h24(oracle, 10, 2, 3)
    expected = Fraction(12622720, 27)
    if anchor_h != expected:
        raise RuntimeError("H24 anchor mismatch: got %s expected %s" % (fs(anchor_h), fs(expected)))

    B = Fraction(10)
    L = Fraction(6)
    u0 = Fraction(11, 12)
    delta = Fraction(1, 200)
    left_u = [u0 - j * delta for j in range(1, 10)]
    right_u = [u0 + j * delta for j in range(1, 10)]

    left_rows = []
    right_rows = []
    left_h = []
    right_h = []
    for side, us, rows, hs in (
        ("left", left_u, left_rows, left_h),
        ("right", right_u, right_rows, right_h),
    ):
        for u in us:
            row, h = extract_h24(oracle, B, u, L - u)
            row["u"] = fs(u)
            row["side_of_Q_1_46"] = side
            rows.append(row)
            hs.append(h)

    degree = 6
    p_left = polyfit(left_u[: degree + 1], left_h[: degree + 1], degree)
    p_right = polyfit(right_u[: degree + 1], right_h[: degree + 1], degree)
    left_hold = [polyval(p_left, u) - h for u, h in zip(left_u[degree + 1 :], left_h[degree + 1 :])]
    right_hold = [polyval(p_right, u) - h for u, h in zip(right_u[degree + 1 :], right_h[degree + 1 :])]
    if any(left_hold) or any(right_hold):
        raise RuntimeError("H24(u) branch holdout failed")

    diff = [a - b for a, b in zip(p_left, p_right)]
    diff_at_wall = polyval(diff, u0)
    diff_derivative = polyder_at(diff, u0)
    affine_line_fit = fit_affine_line_h24(oracle)
    payload = {
        "anchor": anchor_row,
        "inner_wall": {
            "B": fs(B),
            "c_plus_e": fs(L),
            "u_definition": "c=u, e=L-u",
            "u0": fs(u0),
            "crossing_channel": "Q_(m=1; plus pair {4,6})",
            "Q_formula": "(B^2-4L^2+8Lu)/4",
            "left_rows": left_rows,
            "right_rows": right_rows,
            "H24_left_coeff_ascending": [fs(x) for x in p_left],
            "H24_right_coeff_ascending": [fs(x) for x in p_right],
            "branch_difference_coeff_ascending": [fs(x) for x in diff],
            "difference_at_Q_wall": fs(diff_at_wall),
            "difference_derivative_at_Q_wall": fs(diff_derivative),
            "left_holdout_residuals": [fs(x) for x in left_hold],
            "right_holdout_residuals": [fs(x) for x in right_hold],
        },
        "affine_line_H24_test": affine_line_fit,
    }
    out = qdir / "bots/student-1/data/round3_wall_brick.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print("anchor H24=%s" % fs(anchor_h))
    print("inner branch difference at wall=%s derivative=%s" % (fs(diff_at_wall), fs(diff_derivative)))
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
