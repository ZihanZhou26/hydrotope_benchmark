#!/usr/bin/env python3
"""Evaluate the strongest explicit eight-point formula from each run.

The diagnostic target is the normalized eight-point amplitude

    Phi_8 = A_8 / (128 i omega_1 omega_2).

The original symbolic-regression rows are not archived in this repository, so
this script creates a separate deterministic panel of on-shell two-minus
points.  The first 750 generated rows are discarded and the last 250 are used
only for evaluation.  None of the discovery runs saw these rows.

For a chamber- or chart-limited result, its submitted algebraic expression is
evaluated literally on every row.  A missing value means that the final answer
does not contain an executable n=8 closed formula; a recursion or an unfitted
ansatz is not counted as one.
"""

from __future__ import annotations

import csv
import itertools
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
POINTS_CSV = HERE / "checkpoint_mae_n8_points.csv"
RESULTS_CSV = HERE / "checkpoint_formula_mae.csv"

N_POINT = 8
POWER = N_POINT - 3
SEED = 2025
N_TOTAL = 1000
N_HELD_OUT = 250
FREQUENCY_SCALE = 2.5


def positive_part(x: float) -> float:
    return max(0.0, x)


def subset_sum_formula(threshold: float, squares: list[float]) -> float:
    """Alternating subset sum of fifth positive-part powers."""
    value = 0.0
    for size in range(len(squares) + 1):
        for subset in itertools.combinations(squares, size):
            value += (-1.0) ** size * positive_part(threshold - sum(subset)) ** POWER
    return value


def phi8_exact(omega: np.ndarray) -> float:
    beta_squared = min(omega[0] ** 2, omega[1] ** 2)
    return subset_sum_formula(beta_squared, [x**2 for x in omega[2:]])


def phi8_soft_min(omega: np.ndarray) -> float:
    """Symmetric principal-chamber monomial, extrapolated to every row."""
    beta_squared = min(omega[0] ** 2, omega[1] ** 2)
    return beta_squared**POWER


def phi8_soft_omega2(omega: np.ndarray) -> float:
    """Submitted omega_2 principal-chart monomial, extrapolated to every row."""
    return (omega[1] ** 2) ** POWER


def phi8_chart_tied(omega: np.ndarray) -> float:
    """Submitted chart omitting solved plus leg omega_8."""
    return subset_sum_formula(omega[1] ** 2, [x**2 for x in omega[2:-1]])


def phi8_sorted_individual(omega: np.ndarray) -> float:
    """Codex 5.5's size-capped ordinary-power finite difference."""
    threshold = min(omega[0] ** 2, omega[1] ** 2)
    squares = sorted(x**2 for x in omega[2:])
    active_count = min(POWER, sum(x < threshold for x in squares))
    selected = squares[:active_count]
    value = 0.0
    for size in range(active_count + 1):
        for subset in itertools.combinations(selected, size):
            value += (-1.0) ** size * (threshold - sum(subset)) ** POWER
    return value


CANDIDATES = {
    "global": phi8_exact,
    "chart_tied": phi8_chart_tied,
    "soft_min": phi8_soft_min,
    "soft_omega2": phi8_soft_omega2,
    "sorted_individual": phi8_sorted_individual,
}


RUN_CANDIDATES = {
    "case_1/claude_opus_48_max": "soft_omega2",
    # Its all-chamber expression stops at n=5; its principal formula is all-n.
    "case_1/claude_opus_48_ultra": "soft_min",
    "case_1/codex_54_xhigh": "chart_tied",
    "case_1/codex_55_xhigh": None,
    "case_1/deepseek_v4_pro": None,
    "case_1/fugu_ultra": "soft_omega2",
    "case_2/claude_opus_48_max": "global",
    "case_2/claude_opus_48_ultra": "global",
    "case_2/codex_54_xhigh": "chart_tied",
    "case_2/codex_55_xhigh": "global",
    "case_2/deepseek_v4_pro": None,
    "case_2/fugu_ultra": "global",
    "case_3/claude_opus_48_max": "soft_min",
    "case_3/claude_opus_48_ultra": "soft_omega2",
    "case_3/codex_54_xhigh": "soft_omega2",
    "case_3/codex_55_xhigh": "sorted_individual",
    "case_3/deepseek_v4_pro": "soft_omega2",
    "case_3/fugu_ultra": "chart_tied",
}


CANDIDATE_NOTES = {
    "global": "complete all-chamber eight-point formula",
    "chart_tied": "literal n=8 extrapolation of chart-tied subset formula",
    "soft_min": "literal n=8 extrapolation of symmetric principal-chamber monomial",
    "soft_omega2": "literal n=8 extrapolation of omega_2 principal-chart monomial",
    "sorted_individual": "literal n=8 extrapolation of size-capped finite difference",
    None: "no executable n=8 closed formula in final answer",
}


def make_held_out_panel() -> np.ndarray:
    """Generate on-shell two-minus n=8 frequencies deterministically."""
    rng = np.random.default_rng(SEED)
    # Free entries are omega_2,...,omega_7.  The construction below solves the
    # energy and momentum constraints for omega_1 and omega_8.
    free = rng.normal(0.0, FREQUENCY_SCALE, size=(N_TOTAL, N_POINT - 2))
    summed = free.sum(axis=1)
    if np.any(summed == 0.0):
        raise RuntimeError("generated a singular free-frequency row")

    plus_square_sum = np.square(free[:, 1:]).sum(axis=1)
    omega_1 = (free[:, 0] ** 2 - plus_square_sum - summed**2) / (2.0 * summed)
    omega_8 = -omega_1 - summed
    omega = np.column_stack([omega_1, free, omega_8])

    energy_residual = np.abs(omega.sum(axis=1)).max()
    momentum_residual = np.abs(
        -omega[:, 0] ** 2
        - omega[:, 1] ** 2
        + np.square(omega[:, 2:]).sum(axis=1)
    ).max()
    if energy_residual > 1e-10 or momentum_residual > 1e-8:
        raise RuntimeError(
            f"on-shell construction failed: energy={energy_residual}, "
            f"momentum={momentum_residual}"
        )
    return omega[-N_HELD_OUT:]


def write_points(omega: np.ndarray, target: np.ndarray) -> None:
    with POINTS_CSV.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["point", *[f"omega_{i}" for i in range(1, 9)], "phi_8"])
        for index, (row, value) in enumerate(zip(omega, target), start=1):
            writer.writerow([index, *[f"{x:.17g}" for x in row], f"{value:.17g}"])


def write_results(omega: np.ndarray, target: np.ndarray) -> None:
    rows = []
    for run, candidate in RUN_CANDIDATES.items():
        if candidate is None:
            mae = None
        else:
            prediction = np.array([CANDIDATES[candidate](row) for row in omega])
            mae = float(np.mean(np.abs(prediction - target)))
            if candidate == "global" and mae > 1e-10:
                raise RuntimeError(f"exact formula has nonzero MAE for {run}: {mae}")
        rows.append((run, candidate or "none", mae, CANDIDATE_NOTES[candidate]))

    with RESULTS_CSV.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["run", "candidate", "mae_phi8", "n_evaluation", "seed", "frequency_scale", "note"]
        )
        for run, candidate, mae, note in rows:
            writer.writerow(
                [
                    run,
                    candidate,
                    "" if mae is None else f"{mae:.15g}",
                    N_HELD_OUT,
                    SEED,
                    FREQUENCY_SCALE,
                    note,
                ]
            )


def main() -> None:
    omega = make_held_out_panel()
    target = np.array([phi8_exact(row) for row in omega])
    write_points(omega, target)
    write_results(omega, target)
    print(f"wrote {POINTS_CSV.name} ({len(omega)} rows)")
    print(f"wrote {RESULTS_CSV.name} ({len(RUN_CANDIDATES)} rows)")


if __name__ == "__main__":
    main()
