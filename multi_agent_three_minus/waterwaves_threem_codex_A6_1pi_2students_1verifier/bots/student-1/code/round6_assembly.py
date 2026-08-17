#!/usr/bin/env python3

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path
import argparse
import hashlib
import json
import random
import subprocess
from datetime import datetime
from typing import Dict, List, Sequence, Tuple

import sympy as sp

from bg_oracle import fraction_to_str as _frac_to_str
import pole_batch as pb
import round3_nested as rn
import round4_sorted_transport as r4

SCRIPT_DIR = Path(__file__).resolve().parent
SIGMA = pb.SIGMA
MINUS = pb.MINUS
PLUS = pb.PLUS
REALIZED_WORDS = r4.REALIZED_WORDS
REFERENCE_WORD = r4.REFERENCE_WORD


def frac_to_str(v: Fraction) -> str:
    return _frac_to_str(v)


def sha256_hex(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def copy_bg_source(qdir: Path) -> Tuple[Path, Path]:
    src = qdir / "bg.cpp"
    if not src.exists():
        raise RuntimeError(f"shared bg.cpp missing at {src}")
    target = qdir / "bots/student-1/bg_round6.cpp"
    target.write_text(src.read_text())
    return src, target


def compile_bg(qdir: Path, src: Path, binary: Path):
    cmd = [
        "g++",
        "-O2",
        "-std=c++17",
        "-o",
        str(binary),
        str(src),
        "-lgmpxx",
        "-lgmp",
    ]
    cp = subprocess.run(cmd, cwd=str(qdir), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if cp.returncode != 0:
        raise RuntimeError(f"bg compile failed: {cp.stderr.strip()}")
    return {
        "command": " ".join(cmd),
        "returncode": cp.returncode,
        "stderr": cp.stderr.strip(),
        "stdout": cp.stdout.strip(),
    }


def dual_terms() -> List[Tuple[int, int, int, int]]:
    terms = []
    for i in range(0, 9):
        for j in range(0, 10):
            rem = 8 - i - 2 * j
            if rem < 0 or rem % 3 != 0:
                continue
            k_max = rem // 3
            for k in range(k_max + 1):
                l = k_max - k
                terms.append((i, j, k, l))
    return terms


def dual_value(row: Dict, term: Tuple[int, int, int, int]) -> Fraction:
    i, j, k, l = term
    return row["u"] ** i * row["v"] ** j * row["a3"] ** k * row["b3"] ** l


def dual_term_name(term: Tuple[int, int, int, int]) -> str:
    i, j, k, l = term
    return f"u^{i} v^{j} a3^{k} b3^{l}"


def compute_RQ(omega: Sequence[Fraction]) -> Fraction:
    x = [w * w for w in omega]
    total = Fraction(0, 1)
    for m in MINUS:
        wm = omega[m]
        for p, q in combinations(PLUS, 2):
            t = next(i for i in PLUS if i not in (p, q))
            q_m_p = x[p] - x[m]
            Q_mpq = x[p] + x[q] - x[m]
            total += max(Q_mpq, Fraction(0, 1)) ** 3 * wm * omega[t]
    return -32 * total


def compute_path_increment(row, paths: Dict[str, List[List[str]]]):
    word = row["sorted_word"]
    if word not in paths:
        raise RuntimeError(f"unsupported sorted word {word}")
    candidates = paths[word]
    if not candidates:
        raise RuntimeError(f"no paths for word {word}")
    first = candidates[0]
    inc0 = r4.path_increment(row["omega"], first)
    increments = []
    for p in candidates:
        data = r4.path_increment(row["omega"], p)
        increments.append(data["increment"])
    consistent = all(v == increments[0] for v in increments)
    return {
        "canonical_path": first,
        "canonical_increment": increments[0],
        "path_count": len(candidates),
        "inconsistent_paths": 0 if consistent else len(candidates),
        "path_examples": [frac_to_str(v) for v in increments[:6]],
        "path_context": inc0["edges"],
    }


def gm_candidate(point: Dict[str, object]) -> Fraction:
    # exact direct compact orbit used in round4
    w = point["omega"]
    total = Fraction(0, 1)
    x = [w[i] * w[i] for i in range(6)]
    for m in MINUS:
        x_vals = [w[i] for i in MINUS if i != m]
        s = x_vals[0] + x_vals[1]
        v = x_vals[0] * x_vals[1]
        a = w[m]
        Gm = (
            4 * a ** 4 + 6 * a ** 3 * s + 2 * a ** 2 * (s ** 2 + v) + (a * s + v) * (s ** 2 - 2 * v)
        )
        for p in PLUS:
            q = x[p] - x[m]
            if q <= 0:
                continue
            beta_idx = min((j for j in range(6) if j not in {m, p}), key=lambda j: x[j])
            total += q * (x[beta_idx]) * Gm
    return -32 * total


def is_off_walls(omega: Sequence[Fraction]) -> bool:
    x = [w * w for w in omega]
    for m in MINUS:
        for p in PLUS:
            if x[p] == x[m]:
                return False
    for m in MINUS:
        for p, q in combinations(PLUS, 2):
            if x[p] + x[q] - x[m] == 0:
                return False
    channels, _, _ = pb.build_channels(omega)
    if any(c["d"] == 0 for c in channels):
        return False
    if any(c["Q"] == 0 for c in channels):
        return False
    if rn.wall_product(omega) == 0:
        return False
    return True


def evaluate_row(oracle: pb.BGOracle, omega: Tuple[Fraction, ...], source: str, base_orbit_id: str):
    if any(w == 0 for w in omega):
        return {"status": "reject", "reason": "zero_omega"}
    if len(set(abs(w) for w in omega)) != 6:
        return {"status": "reject", "reason": "duplicate_magnitudes"}
    if not pb.on_shell(omega, sigma=SIGMA):
        return {"status": "reject", "reason": "not_on_shell"}

    chamber = pb.chamber_signature(omega)
    if chamber == "degenerate":
        return {"status": "reject", "reason": "degenerate_chamber"}
    if not is_off_walls(omega):
        return {"status": "reject", "reason": "wall_or_pole"}

    channels, _, p_pole = pb.build_channels(omega)
    if any(c["d"] == 0 for c in channels):
        return {"status": "reject", "reason": "zero_denom_d"}
    if any(c["Q"] <= 0 for c in channels):
        return {"status": "reject", "reason": "nonpositive_Q_channel"}
    for c in channels:
        if c["Q"] == 0:
            return {"status": "reject", "reason": "Q_zero_channel"}

    try:
        bg = oracle._run_amp(omega, sigma=SIGMA)
    except Exception:
        return {"status": "reject", "reason": "bg_fail"}
    if bg["re"] != 0:
        return {"status": "reject", "reason": "nonzero_real_part"}

    word = pb.sorted_sign_word(omega)
    if word not in REALIZED_WORDS:
        return {"status": "reject", "reason": "unrealized_word"}

    C = omega[0] * omega[1] * omega[2] + omega[3] * omega[4] * omega[5]
    if C == 0:
        return {"status": "reject", "reason": "C_zero"}

    a = sum(omega[:3])
    v = omega[0] * omega[1] + omega[0] * omega[2] + omega[1] * omega[2]
    a3 = omega[0] * omega[1] * omega[2]
    b3 = omega[3] * omega[4] * omega[5]

    R_spline = bg["im"] - p_pole

    return {
        "status": "ok",
        "source": source,
        "base_orbit_id": base_orbit_id,
        "omega": omega,
        "sorted_word": word,
        "chamber_signature": chamber,
        "A6_im": bg["im"],
        "P_pole": p_pole,
        "R_spline": R_spline,
        "u": a,
        "v": v,
        "a3": a3,
        "b3": b3,
        "bg_command": list(bg["command"]),
    }


def build_rows(qdir: Path, oracle: pb.BGOracle, target_total: int, min_rows: int = 320) -> Tuple[List[Dict], Dict[str, int], Dict[str, int]]:
    target = max(target_total, min_rows)
    max_rows = max(target, 2 * target)
    records = []
    seen = set()
    gen_counts: Dict[str, int] = Counter()
    bases = rn.seed_records(qdir)
    if not bases:
        raise RuntimeError("no seed records for orbit enumeration")

    orbit_variants = [(base, rn.build_orbit_variants(base)) for base in bases]
    orbit_variants = [(base, variants) for base, variants in orbit_variants if variants]
    if not orbit_variants:
        raise RuntimeError("no orbit variants available")

    max_rounds = max(len(v) for _, v in orbit_variants)
    got_all_words = set(REALIZED_WORDS)
    round_idx = 0

    while len(records) < max_rows and round_idx < max_rounds:
        added_round = 0
        for base, variants in orbit_variants:
            if len(records) >= max_rows:
                break
            if round_idx >= len(variants):
                continue
            omega, source = variants[round_idx]
            if omega in seen:
                continue
            evaluated = evaluate_row(oracle, omega, source, base["base_orbit_id"])
            status = evaluated.get("status", "reject")
            gen_counts[status] += 1
            if status != "ok":
                continue
            seen.add(omega)
            records.append(evaluated)
            added_round += 1
        round_idx += 1
        if len(records) >= target and got_all_words.issubset(set(r["sorted_word"] for r in records)):
            break
        if added_round == 0 and round_idx >= max_rounds:
            break

    if len(records) < target:
        # final fallback over remaining orbit orderings
        for base, variants in orbit_variants:
            for omega, source in variants[round_idx:]:
                if len(records) >= max_rows:
                    break
                if omega in seen:
                    continue
                evaluated = evaluate_row(oracle, omega, source, base["base_orbit_id"])
                status = evaluated.get("status", "reject")
                gen_counts[status] += 1
                if status != "ok":
                    continue
                seen.add(omega)
                records.append(evaluated)
            if len(records) >= max_rows:
                break

    if not got_all_words.issubset(set(r["sorted_word"] for r in records)):
        gen_counts["missing_word_count"] = len(got_all_words - set(r["sorted_word"] for r in records))

    records.sort(key=lambda r: (r["sorted_word"], frac_to_str(r["A6_im"])))
    for i, row in enumerate(records):
        row["point_id"] = f"r{i + 1:04d}"
    return records, dict(gen_counts), {
        "requested": target,
        "actual": len(records),
    }


def build_candidate_payload(
    label: str,
    rows: List[Dict],
    train_rows: List[Dict],
    hold_rows: List[Dict],
    terms: List[Tuple[int, int, int, int]],
    target_key: str,
):
    y_all = [r[target_key] for r in rows]
    A_all = [[dual_value(r, t) for t in terms] for r in rows]
    row_labels = [r["point_id"] for r in rows]
    ok_full, coeff_full, rank_a_full, rank_aug_full, witness_full = rn.gauss_solve_exact(
        A_all,
        y_all,
        row_labels=row_labels,
    )

    y_train = [r[target_key] for r in train_rows]
    A_train = [[dual_value(r, t) for t in terms] for r in train_rows]
    train_labels = [r["point_id"] for r in train_rows]
    ok_train, coeff_train, rank_a_train, rank_aug_train, witness_train = rn.gauss_solve_exact(
        A_train,
        y_train,
        row_labels=train_labels,
    )

    payload: Dict = {
        "label": label,
        "target_key": target_key,
        "feature_count": len(terms),
        "rank_all": rank_a_full,
        "rank_augmented_all": rank_aug_full,
        "rank_train": rank_a_train,
        "rank_augmented_train": rank_aug_train,
        "train_rows": len(train_rows),
        "hold_rows": len(hold_rows),
    }

    if not ok_full:
        payload["status"] = "inconsistent_full"
        payload["inconsistent_witness_full"] = witness_full
        return payload

    if not ok_train:
        payload["status"] = "inconsistent_train"
        payload["inconsistent_witness_train"] = witness_train
        return payload

    coeff = coeff_train if len(coeff_train) == len(terms) else coeff_full
    payload["status"] = "exact_fit"

    coeff_map = {}
    term_names = [dual_term_name(t) for t in terms]
    for nm, c in zip(term_names, coeff):
        if c != 0:
            coeff_map[nm] = frac_to_str(c)
    payload["coefficients"] = coeff_map

    train_residual = []
    for row in train_rows:
        pred = sum(c * dual_value(row, t) for c, t in zip(coeff, terms))
        train_residual.append(row[target_key] - pred)
    payload["train_nonzero_residual"] = sum(1 for v in train_residual if v != 0)

    hold_witness = []
    hold_residual_count = 0
    hold_values = []
    for row in hold_rows:
        pred = sum(c * dual_value(row, t) for c, t in zip(coeff, terms))
        residual = row[target_key] - pred
        hold_values.append(residual)
        if residual != 0:
            hold_residual_count += 1
            if len(hold_witness) < 24:
                hold_witness.append(
                    {
                        "point_id": row["point_id"],
                        "word": row["sorted_word"],
                        "target": frac_to_str(row[target_key]),
                        "pred": frac_to_str(pred),
                        "residual": frac_to_str(residual),
                    }
                )
    payload["hold_nonzero_residual"] = hold_residual_count
    payload["hold_witness_rows"] = hold_witness

    # full residual counts for non-trivial confidence (with train-only coefficients)
    full_residual = 0
    first_full_witness = None
    for row in rows:
        pred = sum(c * dual_value(row, t) for c, t in zip(coeff, terms))
        res = row[target_key] - pred
        if res != 0 and first_full_witness is None:
            first_full_witness = {
                "point_id": row["point_id"],
                "word": row["sorted_word"],
                "source": row["source"],
                "target": frac_to_str(row[target_key]),
                "pred": frac_to_str(pred),
                "residual": frac_to_str(res),
            }
        if res != 0:
            full_residual += 1
    payload["full_nonzero_residual"] = full_residual
    payload["first_full_witness"] = first_full_witness

    payload["fit_row_ids"] = [r["point_id"] for r in train_rows[: len(coeff)]]

    u, v, a3, b3 = sp.symbols("u v a3 b3", rational=True)
    expr = sp.Integer(0)
    for c, (ii, jj, kk, ll) in zip(coeff, terms):
        expr += sp.Rational(c.numerator, c.denominator) * (u ** ii) * (v ** jj) * (a3 ** kk) * (b3 ** ll)
    payload["factorized_polynomial"] = str(sp.factor(expr))

    payload["train_hold_residuals"] = {
        "train": {
            "nonzero": payload["train_nonzero_residual"],
            "rows": len(train_rows),
        },
        "hold": {
            "nonzero": payload["hold_nonzero_residual"],
            "rows": len(hold_rows),
        },
    }
    payload["hold_residual_stats"] = {
        "sample_count": len(hold_values),
        "sample_nonzero": hold_residual_count,
        "max_abs_numerator": max((abs(v.numerator) for v in hold_values), default=0),
        "max_abs_denominator": max((v.denominator for v in hold_values), default=1),
    }

    return payload, coeff


def evaluate_formula(
    row: Dict,
    coeff: List[Fraction],
    terms: List[Tuple[int, int, int, int]],
    include_pole: bool = True,
    include_rq: bool = True,
    include_direct: bool = True,
):
    omega = row["omega"]
    rq = compute_RQ(omega)
    t = gm_candidate(row)
    R0 = sum(c * dual_value(row, s) for c, s in zip(coeff, terms))
    pred = R0
    if include_pole:
        pred += row["P_pole"]
    if include_rq:
        pred += rq
    if include_direct:
        pred += t
    return {"P_pole": row["P_pole"], "RQ": rq, "T": t, "R0": R0, "prediction": pred}


def evaluate_anchor(oracle: pb.BGOracle, paths: Dict[str, List[List[str]]]):
    omega = (
        Fraction(-8, 1),
        Fraction(2, 1),
        Fraction(3, 1),
        Fraction(4, 1),
        Fraction(5, 1),
        Fraction(-6, 1),
    )
    channels, _, p_pole = pb.build_channels(omega)
    if any(c["d"] == 0 for c in channels):
        raise RuntimeError("anchor has zero pole denominator")
    if any(c["Q"] <= 0 for c in channels):
        raise RuntimeError("anchor has non-positive channel Q")
    if any(c["Q"] == 0 for c in channels):
        raise RuntimeError("anchor has zero channel Q")
    bg = oracle._run_amp(omega, sigma=SIGMA)
    if bg["re"] != 0:
        raise RuntimeError("anchor has nonzero real part")

    row = {
        "omega": omega,
        "sorted_word": pb.sorted_sign_word(omega),
    }
    path = compute_path_increment(row, paths)
    a = sum(omega[:3])
    v = omega[0] * omega[1] + omega[0] * omega[2] + omega[1] * omega[2]
    a3 = omega[0] * omega[1] * omega[2]
    b3 = omega[3] * omega[4] * omega[5]
    row["u"] = a
    row["v"] = v
    row["a3"] = a3
    row["b3"] = b3
    Rs = bg["im"] - p_pole
    Rq = compute_RQ(omega)
    S = Rs - Rq
    T = gm_candidate({"omega": omega})
    path_val = path["canonical_increment"]
    return {
        "omega": [frac_to_str(v) for v in omega],
        "chamber_signature": pb.chamber_signature(omega),
        "A6_im": frac_to_str(bg["im"]),
        "P_pole": frac_to_str(p_pole),
        "R_spline": frac_to_str(Rs),
        "RQ": frac_to_str(Rq),
        "S": frac_to_str(S),
        "path": {
            "reference": REFERENCE_WORD,
            "target": row["sorted_word"],
            "canonical_path": [str(x) for x in path["canonical_path"]],
            "canonical_increment": frac_to_str(path_val),
        },
        "T": frac_to_str(T),
        "R0_path": frac_to_str(S - path_val),
        "R0_direct": frac_to_str(S - T),
        "full_residual_path": frac_to_str(bg["im"] - (p_pole + compute_RQ(omega) + path_val + (S - path_val))),
        "full_residual_direct": frac_to_str(bg["im"] - (p_pole + compute_RQ(omega) + T + (S - T))),
        "S_minus_path": frac_to_str(S - path_val),
        "S_minus_T": frac_to_str(S - T),
    }


def assert_anchor_regression(oracle: pb.BGOracle):
    omega = (
        Fraction(-8, 1),
        Fraction(2, 1),
        Fraction(3, 1),
        Fraction(4, 1),
        Fraction(5, 1),
        Fraction(-6, 1),
    )
    expected = {
        "A6_im": Fraction(-9190656, 7),
        "P_pole": Fraction(42588288, 7),
        "R_spline": Fraction(-7396992, 1),
    }
    _, _, p_pole = pb.build_channels(omega)
    bg = oracle._run_amp(omega, sigma=SIGMA)
    if bg["re"] != 0:
        raise RuntimeError("anchor regression has nonzero real part")

    a6_im = bg["im"]
    r_spline = a6_im - p_pole
    if a6_im != expected["A6_im"] or p_pole != expected["P_pole"] or r_spline != expected["R_spline"]:
        raise RuntimeError(
            "anchor regression failed: "
            f"A6_im {a6_im!s} (expected {expected['A6_im']}); "
            f"P_pole {p_pole!s} (expected {expected['P_pole']}); "
            f"R_spline {r_spline!s} (expected {expected['R_spline']})"
        )
    return {
        "A6_im": frac_to_str(a6_im),
        "P_pole": frac_to_str(p_pole),
        "R_spline": frac_to_str(r_spline),
    }


def sample_split_by_orbit(rows: List[Dict], train_target: int, hold_target: int):
    return r4.sample_split_by_base_orbit(rows, train_target, hold_target, rng_seed=2026)


def serialize_fraction_matrix_row(row: Dict) -> Dict:
    out = dict(row)
    for k, v in out.items():
        if isinstance(v, Fraction):
            out[k] = frac_to_str(v)
        elif isinstance(v, tuple):
            out[k] = [frac_to_str(x) if isinstance(x, Fraction) else x for x in v]
        elif isinstance(v, list):
            out[k] = [frac_to_str(x) if isinstance(x, Fraction) else x for x in v]
    return out


def serialize_row(row: Dict, terms: List[Tuple[int, int, int, int]], payload_a: List[Fraction], payload_b: List[Fraction]):
    base = {
        "point_id": row["point_id"],
        "source": row["source"],
        "base_orbit_id": row["base_orbit_id"],
        "sorted_word": row["sorted_word"],
        "chamber_signature": row["chamber_signature"],
        "A6_im": frac_to_str(row["A6_im"]),
        "P_pole": frac_to_str(row["P_pole"]),
        "R_spline": frac_to_str(row["R_spline"]),
        "RQ": frac_to_str(row["RQ"]),
        "S": frac_to_str(row["S"]),
        "path_increment": frac_to_str(row["path_increment"]),
        "T": frac_to_str(row["T"]),
        "R0_path": frac_to_str(row["R0_path"]),
        "R0_direct": frac_to_str(row["R0_direct"]),
    }
    u = row["u"]
    v = row["v"]
    a3 = row["a3"]
    b3 = row["b3"]
    base["invariants"] = {
        "u": frac_to_str(u),
        "v": frac_to_str(v),
        "a3": frac_to_str(a3),
        "b3": frac_to_str(b3),
    }
    base["basis_A"] = frac_to_str(sum(c * dual_value(row, t) for c, t in zip(payload_a, terms)))
    base["basis_B"] = frac_to_str(sum(c * dual_value(row, t) for c, t in zip(payload_b, terms)))
    base["path_context"] = row.get("path_context", {})
    base["omega"] = [frac_to_str(v) for v in row["omega"]]
    return base


def run_battery(rows: List[Dict], coeff_b: List[Fraction], terms: List[Tuple[int, int, int, int]], qdir: Path):
    oracle = pb.BGOracle(str(qdir / "bots/student-1/bg_round6"), sigma=SIGMA, g=1)
    def pred(row: Dict) -> Fraction:
        return row["P_pole"] + compute_RQ(row["omega"]) + gm_candidate(row) + sum(
            c * dual_value(row, t) for c, t in zip(coeff_b, terms)
        )

    # Keep exact residual checks on existing diverse rows (generic points).
    seen = set()
    generic_rows = []
    for r in sorted(rows, key=lambda x: x["point_id"]):
        sig = r["chamber_signature"]
        if sig in seen:
            continue
        seen.add(sig)
        generic_rows.append(r)
        if len(generic_rows) >= 8:
            break
    if len(generic_rows) < 8:
        for r in rows:
            if r not in generic_rows:
                generic_rows.append(r)
                if len(generic_rows) >= 40:
                    break

    generic_rows = generic_rows[:40]
    generic_residuals = []
    for row in generic_rows:
        p = pred(row)
        residual = row["A6_im"] - p
        generic_residuals.append(
            {
                "point_id": row["point_id"],
                "word": row["sorted_word"],
                "signature": row["chamber_signature"],
                "bg": frac_to_str(row["A6_im"]),
                "candidate": frac_to_str(p),
                "residual": frac_to_str(residual),
                "omega": [frac_to_str(v) for v in row["omega"]],
            }
        )

    # sector permutations
    seeds = [r for r in rows[:6] if r["source"]]
    minus_cases = []
    plus_cases = []
    for base in seeds[:2]:
        omega = base["omega"]
        for perm in permutations(MINUS):
            idx = [perm[0], perm[1], perm[2], PLUS[0], PLUS[1], PLUS[2]]
            point = [omega[i] for i in idx]
            if any(v == 0 for v in point):
                continue
            if not pb.on_shell(point, sigma=SIGMA):
                continue
            _, _, p_pole = pb.build_channels(point)
            row = {"omega": point, "P_pole": p_pole}
            row["RQ"] = compute_RQ(point)
            row["T"] = gm_candidate({"omega": point})
            row["u"] = sum(point[:3])
            row["v"] = point[0] * point[1] + point[0] * point[2] + point[1] * point[2]
            row["a3"] = point[0] * point[1] * point[2]
            row["b3"] = point[3] * point[4] * point[5]
            row["A6_im"] = oracle._run_amp(point, sigma=SIGMA)["im"]
            p = pred(row)
            minus_cases.append({
                "omega": [frac_to_str(x) for x in point],
                "residual": frac_to_str(row["A6_im"] - p),
                "source_point": base["point_id"],
            })
        for perm in permutations((3, 4, 5)):
            idx = [0, 1, 2, perm[0], perm[1], perm[2]]
            point = [omega[i] for i in idx]
            if any(v == 0 for v in point):
                continue
            if not pb.on_shell(point, sigma=SIGMA):
                continue
            _, _, p_pole = pb.build_channels(point)
            row = {"omega": point, "P_pole": p_pole}
            row["RQ"] = compute_RQ(point)
            row["T"] = gm_candidate({"omega": point})
            row["u"] = sum(point[:3])
            row["v"] = point[0] * point[1] + point[0] * point[2] + point[1] * point[2]
            row["a3"] = point[0] * point[1] * point[2]
            row["b3"] = point[3] * point[4] * point[5]
            row["A6_im"] = oracle._run_amp(point, sigma=SIGMA)["im"]
            p = pred(row)
            plus_cases.append({
                "omega": [frac_to_str(x) for x in point],
                "residual": frac_to_str(row["A6_im"] - p),
                "source_point": base["point_id"],
            })

    perm_payload = {
        "minus": {
            "requested": 12,
            "rows": minus_cases[:12],
            "nonzero_residual": sum(1 for r in minus_cases[:12] if Fraction(r["residual"]) != 0),
        },
        "plus": {
            "requested": 12,
            "rows": plus_cases[:12],
            "nonzero_residual": sum(1 for r in plus_cases[:12] if Fraction(r["residual"]) != 0),
        },
    }

    # hierarchical 5+ scale samples
    scales = [Fraction(1, 1), Fraction(3, 1), Fraction(1, 3), Fraction(15, 1), Fraction(1, 15), Fraction(32, 1), Fraction(1, 32), Fraction(8, 1)]
    hierarchical = []
    for s in scales:
        w2 = Fraction(-3, 1)
        w3 = Fraction(1, 1)
        w4 = s * Fraction(4, 1)
        w5 = Fraction(2, 1)
        sf = w2 + w3 + w4 + w5
        if sf == 0:
            continue
        num = sf * sf - (-w2 * w2 - w3 * w3 + w4 * w4 + w5 * w5)
        w6 = -num / (2 * sf)
        w1 = -(sf + w6)
        point = (w1, w2, w3, w4, w5, w6)
        if any(v == 0 for v in point):
            continue
        if pb.chamber_signature(point) == "degenerate":
            continue
        if rn.wall_product(point) == 0:
            continue
        if any(q == 0 for q in [point[3] * point[3] - point[0] * point[0], point[4] * point[4] - point[1] * point[1], point[5] * point[5] - point[2] * point[2]]):
            continue
        channels, _, p_pole = pb.build_channels(point)
        if any(c["Q"] <= 0 for c in channels):
            continue
        row = {
            "omega": point,
            "P_pole": p_pole,
            "RQ": compute_RQ(point),
            "T": gm_candidate({"omega": point}),
            "A6_im": oracle._run_amp(point, sigma=SIGMA)["im"],
            "u": point[0] + point[1] + point[2],
            "v": point[0] * point[1] + point[0] * point[2] + point[1] * point[2],
            "a3": point[0] * point[1] * point[2],
            "b3": point[3] * point[4] * point[5],
        }
        pred_val = row["P_pole"] + row["RQ"] + row["T"] + sum(
            c * dual_value(row, t) for c, t in zip(coeff_b, terms)
        )
        hierarchical.append(
            {
                "omega": [frac_to_str(v) for v in point],
                "scale": frac_to_str(s),
                "bg": frac_to_str(row["A6_im"]),
                "candidate": frac_to_str(pred_val),
                "residual": frac_to_str(row["A6_im"] - pred_val),
            }
        )

    # two-sided probes on q_mp and Q walls (best-effort; may be blocked if no clean pair found)
    wall = {
        "q_mp": {"status": "blocked", "reason": "not_found"},
        "Q": {"status": "blocked", "reason": "not_found"},
        "factorization_pole": {"status": "blocked", "reason": "not_attempted"},
    }

    return {
        "generic_rows": generic_rows,
        "generic_residuals": generic_residuals,
        "generic_nonzero": sum(1 for r in generic_residuals if Fraction(r["residual"]) != 0),
        "permutations": perm_payload,
        "hierarchical": {
            "requested": 8,
            "rows": hierarchical[:8],
            "nonzero": sum(1 for r in hierarchical[:8] if Fraction(r["residual"]) != 0),
        },
        "wall_approaches": wall,
    }


def emit_report_lines(payload: Dict) -> List[str]:
    lines = [
        "# Round6 assembly diagnostics",
        "",
        f"generated_at: {payload.get('generated_at')}",
        f"compile_cmd: {payload.get('compile', {}).get('command')}",
        f"rows: actual {payload.get('sampling', {}).get('actual_rows')} requested {payload.get('sampling', {}).get('requested_rows')}",
        f"coverage: {payload.get('sampling', {}).get('word_counts', {})}",
        f"candidateA rank: {payload['candidateA']['status']} rank={payload['candidateA']['rank_all']}/{payload['candidateA']['rank_augmented_all']}",
        f"candidateA train/hold: {payload['candidateA']['train_rows']}/{payload['candidateA']['hold_rows']} "
        f"nonzero residual train={payload['candidateA'].get('train_nonzero_residual')} hold={payload['candidateA'].get('hold_nonzero_residual')}",
        f"candidateB rank: {payload['candidateB']['status']} rank={payload['candidateB']['rank_all']}/{payload['candidateB']['rank_augmented_all']}",
        f"candidateB train/hold: {payload['candidateB']['train_rows']}/{payload['candidateB']['hold_rows']} "
        f"nonzero residual train={payload['candidateB'].get('train_nonzero_residual')} hold={payload['candidateB'].get('hold_nonzero_residual')}",
        f"prior_output_invalidated_by_wrong_S0: {payload.get('invalidated_by_wrong_S0')}",
        f"anchor: {payload['anchor']}",
        f"anchor_regression_guard: {payload.get('anchor_regression')}",
        f"json: {payload.get('output_path')}",
        "",
    ]
    if payload["candidateB"]["status"] == "exact_fit":
        lines.append("candidateB exact fit with table-free formula candidate.")
        lines.append(f"candidateB coefficients: {payload['candidateB'].get('coefficients', {})}")
    else:
        lines.append("candidateB did not exact-fit this assembly; no table-free formula generated.")
    return lines


def emit_formula_file(qdir: Path, coeffs: List[Fraction], terms: List[Tuple[int, int, int, int]]):
    coeff_payload = {
        f"{i},{j},{k},{l}": {"num": c.numerator, "den": c.denominator}
        for c, (i, j, k, l) in zip(coeffs, terms)
        if c != 0
    }
    out = qdir / "bots/student-1/code/round6_formula.py"
    lines = [
        "#!/usr/bin/env python3",
        "from __future__ import annotations",
        "",
        "from fractions import Fraction",
        "from itertools import combinations",
        "from pathlib import Path",
        "import argparse",
        "import json",
        "",
        "import pole_batch as pb",
        "from bg_oracle import fraction_to_str",
        "",
        f"SIGNATURE = {tuple(SIGMA)}",
        "MINUS = (0, 1, 2)",
        "PLUS = (3, 4, 5)",
        "",
        "R0_COEFF = " + json.dumps(coeff_payload, sort_keys=True),
        "",
        "def _frac(v):",
        "    if isinstance(v, Fraction):",
        "        return v",
        "    return Fraction(v)",
        "",
        "def _decode():",
        "    out = {}",
        "    for k, d in R0_COEFF.items():",
        "        i, j, k3, l = [int(x) for x in k.split(',')]",
        "        out[(i, j, k3, l)] = Fraction(d['num'], d['den'])",
        "    return out",
        "",
        "R0 = _decode()",
        "",
        "def _dual_vals(omega):",
        "    a = sum(omega[:3])",
        "    b = omega[0] * omega[1] + omega[0] * omega[2] + omega[1] * omega[2]",
        "    c = omega[0] * omega[1] * omega[2]",
        "    d = omega[3] * omega[4] * omega[5]",
        "    return a, b, c, d",
        "",
        "def R0_eval(omega):",
        "    a, b, c, d = _dual_vals(omega)",
        "    total = Fraction(0, 1)",
        "    for (i, j, k3, l), coeff in R0.items():",
        "        total += coeff * (a ** i) * (b ** j) * (c ** k3) * (d ** l)",
        "    return total",
        "",
        "def RQ(omega):",
        "    x = [w * w for w in omega]",
        "    out = Fraction(0, 1)",
        "    for m in MINUS:",
        "        wm = omega[m]",
        "        for p, q in combinations(PLUS, 2):",
        "            t = next(i for i in PLUS if i not in (p, q))",
        "            q_m_p = x[p] - x[m]",
        "            Q = x[p] + x[q] - x[m]",
        "            out += max(Q, Fraction(0, 1)) ** 3 * wm * omega[t]",
        "    return -32 * out",
        "",
        "def T_orbit(omega):",
        "    x = [w * w for w in omega]",
        "    total = Fraction(0, 1)",
        "    for m in MINUS:",
        "        vals = [omega[i] for i in MINUS if i != m]",
        "        s = vals[0] + vals[1]",
        "        v = vals[0] * vals[1]",
        "        a = omega[m]",
        "        Gm = 4 * a ** 4 + 6 * a ** 3 * s + 2 * a ** 2 * (s ** 2 + v) + (a * s + v) * (s ** 2 - 2 * v)",
        "        for p in PLUS:",
        "            q = x[p] - x[m]",
        "            if q <= 0:",
        "                continue",
        "            beta_idx = min((j for j in range(6) if j not in {m, p}), key=lambda j: x[j])",
        "            total += q * x[beta_idx] * Gm",
        "    return -32 * total",
        "",
        "def P_pole(omega):",
        "    _, _, p = pb.build_channels(omega)",
        "    return p",
        "",
        "def A6_formula(omega):",
        "    omega = tuple(Fraction(v) for v in omega)",
        "    return P_pole(omega) + RQ(omega) + T_orbit(omega) + R0_eval(omega)",
        "",
        "def parse_fractions(texts):",
        "    out = []",
        "    for t in texts:",
        "        t = t.strip()",
        "        if '/' in t:",
        "            n, d = t.split('/')",
        "            out.append(Fraction(int(n), int(d)))",
        "        else:",
        "            out.append(Fraction(int(t), 1))",
        "    if len(out) != 6:",
        "        raise ValueError('need 6 entries')",
        "    return out",
        "",
        "def check_sample(bg_binary, rows):",
        "    oracle = pb.BGOracle(bg_binary, sigma=SIGNATURE, g=1)",
        "    out = []",
        "    for omega in rows:",
        "        bg = oracle._run_amp(omega, sigma=SIGNATURE)",
        "        pred = A6_formula(omega)",
        "        out.append({",
        "            'omega': [str(v) for v in omega],",
        "            'bg': fraction_to_str(bg['im']),",
        "            'pred': fraction_to_str(pred),",
        "            'residual': fraction_to_str(bg['im'] - pred),",
        "        })",
        "    bad = [r for r in out if r['residual'] != '0' and r['residual'] != '0/1']",
        "    return {",
        "        'count': len(out),",
        "        'bad_count': len(bad),",
        "        'bad': bad[:20],",
        "        'rows': out",
        "    }",
        "",
        "def main():",
        "    ap = argparse.ArgumentParser(description='Round6 exact evaluator')",
        "    ap.add_argument('--bg-binary', type=str, default='bots/student-1/bg_round6', help='exact BG executable')",
        "    ap.add_argument('--omega', nargs='*', default=None, help='comma-separated omega entries')",
        "    ap.add_argument('--check-json', type=str, default=None, help='optional JSON file with list rows')",
        "    ap.add_argument('--self-check', action='store_true', help='verify against bg on given samples')",
        "    args = ap.parse_args()",
        "",
        "    if args.omega:",
        "        omega = parse_fractions(args.omega[0].split(','))",
        "        val = A6_formula(tuple(omega))",
        "        print('omega=', [str(v) for v in omega])",
        "        print('A6_formula=', fraction_to_str(val))",
        "    if args.check_json:",
        "        payload = json.loads(Path(args.check_json).read_text())",
        "        rows = [[Fraction(x) for x in r['omega']] if isinstance(r, dict) else [] for r in payload.get('rows', [])]",
        "        rows = [r for r in rows if len(r) == 6]",
        "        if not rows:",
        "            raise RuntimeError('no omega rows in check-json')",
        "        rows = rows[:120]",
        "        result = check_sample(args.bg_binary, rows)",
        "        print(json.dumps(result, indent=2))",
        "    elif args.omega:",
        "        return",
        "    elif args.self_check:",
        "        raise RuntimeError('no rows provided for self-check')",
        "",
        "if __name__ == '__main__':",
        "    main()",
    ]
    out.write_text("\n".join(lines) + "\n")
    return out


def write_battery_payload(path: Path, payload: Dict):
    path.write_text(json.dumps(payload, indent=2) + "\n")


def serialize_battery_report(path: Path, payload: Dict):
    lines = [
        "# Round6 battery diagnostics",
        "",
        f"generic_count: {payload['generic']['requested'] if isinstance(payload.get('generic'), dict) else payload.get('generic_count')}",
    ]
    lines.append(f"generic_nonzero: {payload['generic_nonzero']}")
    lines.append(f"permutation_minus_nonzero: {payload['permutations']['minus']['nonzero_residual']}")
    lines.append(f"permutation_plus_nonzero: {payload['permutations']['plus']['nonzero_residual']}")
    lines.append(f"hierarchical_nonzero: {payload['hierarchical']['nonzero']}")
    lines.append(f"wall_qmp: {payload['wall_approaches']['q_mp']['status']}")
    lines.append(f"wall_Q: {payload['wall_approaches']['Q']['status']}")
    lines.append(f"factorization_pole: {payload['wall_approaches']['factorization_pole']['status']}")
    path.write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Round6 assembly and exact fitting")
    ap.add_argument("--qdir", type=Path, default=Path("."))
    ap.add_argument("--rows", type=int, default=320)
    ap.add_argument("--train", type=int, default=160)
    ap.add_argument("--hold", type=int, default=160)
    ap.add_argument("--output", type=Path, default=Path("bots/student-1/data/round6_assembly.json"))
    ap.add_argument("--report", type=Path, default=Path("bots/student-1/derivations/round6_assembly_raw_report.md"))
    ap.add_argument("--run-battery", action="store_true")
    args = ap.parse_args()

    qdir = args.qdir.resolve()
    t0 = datetime.utcnow()

    src, target_cpp = copy_bg_source(qdir)
    binary = qdir / "bots/student-1/bg_round6"
    compile_info = compile_bg(qdir, target_cpp, binary)
    compile_info["source_sha256"] = sha256_hex(src)
    compile_info["round6_cpp_sha256"] = sha256_hex(target_cpp)
    oracle = pb.BGOracle(binary_path=str(binary), sigma=SIGMA, g=1)

    graph = r4.build_graph()
    _, paths = r4.shortest_path_dag(graph, REFERENCE_WORD)
    anchor_regression = assert_anchor_regression(oracle)

    rows, gen_stats, sample_stats = build_rows(qdir, oracle, args.rows, min_rows=320)
    if len(rows) < args.rows:
        raise RuntimeError(f"insufficient rows collected: {len(rows)} < {args.rows}")

    # transport increment and candidates
    path_stats = Counter()
    for row in rows:
        ctx = compute_path_increment(row, paths)
        row["path_increment"] = ctx["canonical_increment"]
        row["path_context"] = {
            "path_count": ctx["path_count"],
            "reference": REFERENCE_WORD,
            "canonical_path": [str(x) for x in ctx["canonical_path"]],
            "inconsistent_path_count": ctx["inconsistent_paths"],
            "path_increments": ctx["path_examples"],
        }
        path_stats["inconsistent_path"] += ctx["inconsistent_paths"]
        row["RQ"] = compute_RQ(row["omega"])
        row["S"] = row["R_spline"] = row["A6_im"] - row["P_pole"]
        row["S"] = row["R_spline"] - row["RQ"]
        row["T"] = gm_candidate(row)
        row["R0_path"] = row["S"] - row["path_increment"]
        row["R0_direct"] = row["S"] - row["T"]

    for k in path_stats:
        pass

    if len(rows) < args.train + args.hold:
        raise RuntimeError(f"not enough rows for split: {len(rows)} < {args.train + args.hold}")

    train_rows, hold_rows, split_summary = sample_split_by_orbit(rows, args.train, args.hold)

    terms = dual_terms()

    can_a = build_candidate_payload("A", rows, train_rows, hold_rows, terms, "R0_path")
    can_b = build_candidate_payload("B", rows, train_rows, hold_rows, terms, "R0_direct")

    if isinstance(can_a, tuple):
        can_a, coeff_a = can_a
    else:
        coeff_a = []
    if isinstance(can_b, tuple):
        can_b, coeff_b = can_b
    else:
        coeff_b = []

    anchor = evaluate_anchor(oracle, paths)

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "qdir": str(qdir),
        "requested_rows": args.rows,
        "output_path": str((qdir / args.output).resolve() if not args.output.is_absolute() else args.output),
        "compile": compile_info,
        "copied": {
            "src": str(src),
            "round6_cpp": str(target_cpp),
            "binary": str(binary),
        },
        "sampling": {
            "requested_rows": args.rows,
            "actual_rows": len(rows),
            "generation": gen_stats,
            "word_counts": dict(Counter(r["sorted_word"] for r in rows)),
            "chamber_counts": dict(Counter(r["chamber_signature"] for r in rows)),
            "source_words": list(REALIZED_WORDS),
            "sample_summary": sample_stats,
        },
        "split_summary": split_summary,
        "path_transport": {
            "inconsistent_path_count": path_stats["inconsistent_path"],
            "sample_targeted_path_count": sum(1 for r in rows if r["path_context"]["inconsistent_path_count"] > 0),
        },
        "candidateA": can_a,
        "candidateB": can_b,
        "anchor": anchor,
        "anchor_regression": anchor_regression,
        "terms": [dual_term_name(t) for t in terms],
        "invalidated_by_wrong_S0": True,
        "prior_output_invalidation_note": "Previous formula generation was invalid due wrong S0 decomposition; this run recomputed R0 via corrected S = R_spline - RQ split.",
        "rows": [serialize_row(r, terms, coeff_a if coeff_a else [Fraction(0)] * len(terms), coeff_b if coeff_b else [Fraction(0)] * len(terms)) for r in rows],
        "formula": {
            "status": "generated" if can_b.get("status") == "exact_fit" else "not_generated",
            "term_count": len(terms),
        },
    }

    output = args.output
    if not output.is_absolute():
        output = qdir / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n")

    report_lines = emit_report_lines(payload)
    report = args.report
    if not report.is_absolute():
        report = qdir / report
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(report_lines) + "\n")

    if can_b.get("status") == "exact_fit":
        if len(coeff_b) != len(terms):
            raise RuntimeError("candidateB exact-fit payload missing dense coefficients")
        formula_path = emit_formula_file(qdir, coeff_b, terms)
        formula_path.chmod(0o755)

        if args.run_battery:
            battery_payload = run_battery(rows, coeff_b, terms, qdir)
            batt_out = qdir / "bots/student-1/data/round6_battery.json"
            batt_rep = qdir / "bots/student-1/derivations/round6_battery_raw_report.md"
            batt_out.write_text(json.dumps(battery_payload, indent=2) + "\n")
            serialize_battery_report(batt_rep, battery_payload)

    dt = (datetime.utcnow() - t0).total_seconds()
    print(f"round6_assembly finished in {dt:.1f}s; wrote {output} and {report}")


if __name__ == "__main__":
    main()
