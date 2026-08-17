#!/usr/bin/env python3
"""Round-4 exact reconstruction on full magnitude-sorted cells.

This script reconstructs the pole-subtracted remainder
``R = A6/i - P_pole`` in the degree-8 on-shell quotient basis for the
eight canonical full-magnitude cells
``{+-+--+,+--++-,+--+-+,+---++, -+++--,-++-+-, -++--+,-+-++-}``.

Output:
- bots/student-2/data/round4_full_sort.json
- bots/student-2/data/round4_full_sort_<slug>_solve_input.json
- bots/student-2/data/round4_full_sort_<slug>_solve_output.json

The script is restart-friendly: if a per-cell solve file exists and is marked
``done``, it is reused verbatim.
"""

import argparse
import json
import random
import subprocess
import time
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Tuple

import sympy as sp

from round3_bottomup import (
    BOT,
    DATA,
    R2,
    build_fresh_oracle,
    eval_row_int,
    fstr,
    homogeneous_basis,
    poly_from_coeff,
)

WOLFRAM = Path("/opt/sns/bin/WolframKernel")


CANONICAL_WORDS = [
    "+-+--+",
    "+--++-",
    "+--+-+",
    "+---++",
    "-+++--",
    "-++-+-",
    "-++--+",
    "-+-++-",
]


def word_layout(word: str) -> Dict[int, int]:
    """Canonical label (1..6) at each magnitude position in a word.

    Minus signs map to labels 1,2,3 by left-to-right occurrence; plus signs
    map to 4,5,6 by left-to-right occurrence.
    """
    minus = []
    plus = []
    for pos, ch in enumerate(word):
        if ch == "-":
            minus.append(pos)
        elif ch == "+":
            plus.append(pos)
        else:
            raise ValueError("invalid word %r" % (word,))
    if len(minus) != 3 or len(plus) != 3:
        raise ValueError("invalid word length/sign balance: %r" % word)
    out: Dict[int, int] = {}
    for j, pos in enumerate(minus):
        out[pos] = j + 1
    for j, pos in enumerate(plus):
        out[pos] = 4 + j
    return out


LAYOUT = {w: word_layout(w) for w in CANONICAL_WORDS}


def canonical_omega(point: R2.SixPoint, word: str) -> Tuple[Fraction, ...]:
    """Return canonical (w1..w6) for this cell word.

    point.omega entries are ordered as (w1,w2,w3,w4,w5,w6)=(-a,b,c,d,e,-f).
    """
    sorted_word, strict, order = point.sorted_word()
    if strict is False:
        raise RuntimeError("non-strict sorted word for %s" % point)
    if sorted_word != word:
        raise RuntimeError("word mismatch: observed %s expected %s" % (sorted_word, word))
    layout = LAYOUT[word]
    vals = [None] * 6
    for pos, idx in enumerate(order):
        lab = layout[pos]
        vals[lab - 1] = point.omega[idx]
    return tuple(vals)


def canonical_scaled_w(point: R2.SixPoint, word: str) -> Tuple[int, ...]:
    """Scaled integer W = S*omega in canonical (w1..w6) order."""
    S = point.b + point.c + point.d + point.e
    if S == 0:
        raise RuntimeError("degenerate S=0")
    vals = canonical_omega(point, word)
    scaled = []
    for v in vals[:5]:
        xv = v * S
        if xv.denominator != 1:
            raise RuntimeError("non-integral scaled coordinate in %s" % word)
        scaled.append(xv.numerator)
    return tuple(scaled), S


def generic_for_word(point: R2.SixPoint, word: str) -> bool:
    if point.C == 0:
        return False
    if any(v == 0 for v in point.pair_q.values()):
        return False
    if any(v == 0 for v in point.triple_q.values()):
        return False
    sorted_word, strict, _ = point.sorted_word()
    if sorted_word != word or strict is False:
        return False
    return True


def candidate_stream(seed: int):
    """Deterministic generator over candidate integer b,c,d,e.

    Uses expanding ranges and randomized offsets to give broad diversity.
    """
    rng = random.Random(seed)
    # bounded random phase sequence; each phase expands the search volume.
    for phase, bound in enumerate([6, 10, 15, 22, 30, 42, 58, 78]):
        _ = phase
        # structured parity/offset sweep
        for _ in range(420):
            span = max(1, bound)
            b = rng.randint(-span, span)
            c = rng.randint(-span, span)
            d = rng.randint(-span, span)
            e = rng.randint(-span, span)
            yield (b, c, d, e)
        # deterministic-ish sign-combo sweep in the same box
        base = list(range(-bound // 2, bound // 2 + 1))
        for b in base:
            for c in base:
                for sign in (-1, 1):
                    d = sign * (abs(b) + 1 + (c % 3))
                    e = sign * (abs(c) + 2)
                    yield (b + sign, c + 1, d, e)
    # final broad fallback
    while True:
        b = rng.randint(-200, 200)
        c = rng.randint(-200, 200)
        d = rng.randint(-200, 200)
        e = rng.randint(-200, 200)
        yield (b, c, d, e)


def evaluate_remainder(oracle: R2.BGOracle, point: R2.SixPoint) -> Tuple[Fraction, Fraction, str]:
    result, err = R2.safe_on_shell(
        oracle,
        6,
        [point.b, point.c, point.d, point.e],
    )
    if result is None:
        raise RuntimeError(err)
    omega, re, im = result
    if re != 0:
        raise RuntimeError("non-imaginary amplitude for %s" % point.sorted_word()[0])
    if tuple(omega) != tuple(point.omega):
        raise RuntimeError("oracle returned inconsistent omega ordering")
    remainder, _, _ = R2.wall_pole_subtracted(point, im)
    return remainder, im, tuple(pair for pair in point.pair_q.values())


def modular_row_select(target: int):
    """Incremental row-rank selection in a fixed finite field."""
    rows = {}

    def add(row):
        p = 1000000007
        v = [int(x) % p for x in row]
        for pivot in sorted(rows):
            if v[pivot]:
                factor = v[pivot]
                base = rows[pivot]
                for j in range(pivot, len(v)):
                    v[j] = (v[j] - factor * base[j]) % p
        pivot = next((j for j, x in enumerate(v) if x), None)
        if pivot is None:
            return False
        inv = pow(v[pivot], p - 2, p)
        for j in range(pivot, len(v)):
            v[j] = (v[j] * inv) % p
        for old, base in list(rows.items()):
            if base[pivot]:
                factor = base[pivot]
                rows[old] = [
                    (base[j] - factor * v[j]) % p if j >= old else base[j]
                    for j in range(len(v))
                ]
        rows[pivot] = v
        return True

    return add, lambda: len(rows)


def solve_cell(cell_word: str, oracle: R2.BGOracle, basis8: List[Tuple[int, ...]], holdouts_required: int = 30):
    slug = cell_word.replace("+", "p").replace("-", "m")
    cell_file = DATA / f"round4_full_sort_{slug}.json"
    if cell_file.exists():
        payload = json.loads(cell_file.read_text())
        if payload.get("status") == "done":
            return payload

    add_row, rank = modular_row_select(len(basis8))

    attempts = 0
    selected: List[Dict[str, object]] = []
    selected_rows = []
    selected_rhs: List[str] = []
    selected_free = set()
    seen = set()
    seed = (sum(ord(c) for c in cell_word) + len(cell_word) * 129 + 3)

    stream = candidate_stream(seed)

    while rank() < len(basis8):
        attempts += 1
        if attempts > 400000:
            raise RuntimeError("rank search exhausted for %s" % cell_word)
        b, c, d, e = next(stream)
        b, c, d, e = Fraction(b), Fraction(c), Fraction(d), Fraction(e)
        free_key = tuple(fstr(x) for x in (b, c, d, e))
        if free_key in seen:
            continue
        seen.add(free_key)

        try:
            p = R2.SixPoint(*map(Fraction, free_key))
        except Exception:
            continue
        if not generic_for_word(p, cell_word):
            continue

        try:
            R, im, _ = evaluate_remainder(oracle, p)
        except Exception:
            continue

        W, S = canonical_scaled_w(p, cell_word)
        row = eval_row_int(W, basis8)
        if add_row(row):
            canon = canonical_omega(p, cell_word)
            selected_rows.append(list(map(int, row)))
            selected_rhs.append(fstr(R * (S ** 8)))
            selected.append(
                {
                    "free": list(free_key),
                    "S": fstr(S),
                    "scaled_W5": [str(x) for x in W],
                    "canonical_omega": [fstr(x) for x in canon],
                    "R_scaled8": fstr(R * (S ** 8)),
                    "amp_im": fstr(im),
                    "signature": {
                        "omega_sign": "".join("+" if x > 0 else "-" for x in p.omega),
                        "pair_signs": {k: ("+" if v > 0 else "-") for k, v in p.pair_q.items()},
                        "triple_signs": {k: ("+" if v > 0 else "-") for k, v in p.triple_q.items()},
                    },
                }
            )
            selected_free.add(free_key)

    # Exact solve using Wolfram kernel (existing pipeline).
    solve_in = DATA / f"round4_full_sort_{slug}_solve_input.json"
    solve_out = DATA / f"round4_full_sort_{slug}_solve_output.json"
    solve_payload = {
        "matrix": selected_rows,
        "rhs": selected_rhs,
    }
    solve_in.write_text(json.dumps(solve_payload, sort_keys=True))

    t0 = time.time()
    proc = subprocess.run(
        [str(WOLFRAM), "-script", str(BOT / "code" / "solve_exact.wl"), str(solve_in), str(solve_out)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    if proc.returncode != 0:
        raise RuntimeError("Wolfram solve failed for %s: %s %s" % (cell_word, proc.stdout, proc.stderr))

    solved = json.loads(solve_out.read_text())
    coeff = [Fraction(str(x)) for x in solved["coefficients"]]

    # Holdouts: exact checks on fresh points and signature diversity.
    holdouts = []
    hold_sig = {}
    attempts_hold = 0
    seen_holdouts = set(seen)
    stream = candidate_stream(seed + 1000)
    while len(holdouts) < holdouts_required:
        attempts_hold += 1
        if attempts_hold > 300000:
            raise RuntimeError("holdout search exhausted for %s" % cell_word)
        b, c, d, e = next(stream)
        b, c, d, e = Fraction(b), Fraction(c), Fraction(d), Fraction(e)
        free = (b, c, d, e)
        free_key = tuple(fstr(x) for x in free)
        if free_key in seen_holdouts:
            continue
        seen_holdouts.add(free_key)
        try:
            p = R2.SixPoint(*free)
        except Exception:
            continue
        if not generic_for_word(p, cell_word):
            continue
        if free_key in selected_free:
            continue

        try:
            R, im, _ = evaluate_remainder(oracle, p)
        except Exception:
            continue

        W, S = canonical_scaled_w(p, cell_word)
        row = eval_row_int(W, basis8)
        pred = sum(Fraction(c) * Fraction(v) for c, v in zip(coeff, row))
        obs = R * (S ** 8)
        sig_key = (
            tuple("+" if x > 0 else "-" for x in p.omega),
            tuple(("+" if p.pair_q[k] > 0 else "-") for k in sorted(p.pair_q)),
            tuple(("+" if p.triple_q[k] > 0 else "-") for k in sorted(p.triple_q)),
        )
        if hold_sig.get(sig_key, 0) > 3 and len(holdouts) >= 12:
            continue
        hold_sig[sig_key] = hold_sig.get(sig_key, 0) + 1
        canon = canonical_omega(p, cell_word)
        holdouts.append(
            {
                "free": [fstr(x) for x in free],
                "S": fstr(S),
                "scaled_W5": [str(x) for x in W],
                "canonical_omega": [fstr(x) for x in canon],
                "R_scaled8": fstr(R * (S ** 8)),
                "predicted_scaled8": fstr(pred),
                "residual": fstr(pred - obs),
                "amp_im": fstr(im),
                "signature": {
                    "omega_sign": "".join("+" if x > 0 else "-" for x in p.omega),
                    "pair_signs": {k: ("+" if v > 0 else "-") for k, v in p.pair_q.items()},
                    "triple_signs": {k: ("+" if v > 0 else "-") for k, v in p.triple_q.items()},
                },
            }
        )
    poly = poly_from_coeff(coeff, basis8, sp.symbols("w1:6"))

    payload = {
        "word": cell_word,
        "slug": slug,
        "status": "done",
        "basis_degree": 8,
        "basis_size": len(basis8),
        "solve_input": str(solve_in),
        "solve_output": str(solve_out),
        "solve_runtime_seconds": solved["solve_seconds"],
        "solve_rank": solved["rank"],
        "zero_residual": solved["zero_residual"],
        "solve_rows": len(selected),
        "attempts": attempts,
        "attempts_holdouts": attempts_hold,
        "row_rank": rank(),
        "samples": selected,
        "holdouts": holdouts,
        "holdout_zero_count": sum(1 for h in holdouts if h["residual"] == "0"),
        "nonzero_coefficients": sum(c != 0 for c in coeff),
        "coefficients": [fstr(c) for c in coeff],
        "coefficients_basis": [list(x) for x in basis8],
        "poly_terms": len(poly.terms()),
        "signature_diversity": {
            "samples": len(set((rec["signature"]["omega_sign"], tuple(sorted(rec["signature"]["pair_signs"].items())), tuple(sorted(rec["signature"]["triple_signs"].items()))) for rec in selected)),
            "holdouts": {
                "omega_sign": len({tuple(h["signature"]["omega_sign"]) for h in holdouts}),
                "triple_sign": len({tuple(sorted(h["signature"]["triple_signs"].items())) for h in holdouts}),
                "pair_sign": len({tuple(sorted(h["signature"]["pair_signs"].items())) for h in holdouts}),
            },
        },
    }

    cell_file.write_text(json.dumps(payload, indent=2, sort_keys=True))
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--holdouts", type=int, default=30)
    args = parser.parse_args()

    DATA.mkdir(parents=True, exist_ok=True)
    basis8 = homogeneous_basis(8)
    if len(basis8) != 285:
        raise RuntimeError("unexpected degree-8 basis size: %d" % len(basis8))

    oracle, build_cmd = build_fresh_oracle()

    cells = {}
    for word in CANONICAL_WORDS:
        cells[word] = solve_cell(word, oracle, basis8, holdouts_required=args.holdouts)

    done = [c for c in cells.values() if c.get("status") == "done"]
    payload = {
        "meta": {
            "basis_degree": 8,
            "basis_size": len(basis8),
            "words": CANONICAL_WORDS,
            "holdouts_required": args.holdouts,
            "build_command": " ".join(build_cmd),
        },
        "cells": cells,
        "counts": {
            "done": len(done),
            "total": len(CANONICAL_WORDS),
            "full_rank_cells": sum(1 for c in done if c.get("row_rank") == 285),
            "nonzero_coeffs_total": sum(c.get("nonzero_coefficients", 0) for c in done),
            "total_holdouts": sum(c.get("holdout_zero_count", 0) for c in done),
        },
    }

    out = DATA / "round4_full_sort.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print("%s" % out)


if __name__ == "__main__":
    main()
