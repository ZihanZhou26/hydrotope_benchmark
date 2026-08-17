#!/usr/bin/env python3

from collections import Counter
from fractions import Fraction
from pathlib import Path
import argparse
import json
import math
import random
import subprocess
import sys
from itertools import combinations
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union, Iterator

import sympy as sp
import hashlib
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[2]
PY2_DIR = ROOT / "bots" / "student-2" / "code"
if str(PY2_DIR) not in sys.path:
    sys.path.insert(0, str(PY2_DIR))

import pole_batch as pb  # noqa: E402
import round3_nested as rn  # noqa: E402
from round3_bottomup import ModularRank, R2, fstr, homogeneous_basis, reduce_w5  # noqa: E402

SIGMA = pb.SIGMA
MINUS = pb.MINUS
PLUS = pb.PLUS

Q_PAIR_KEYS = [(0, 3), (0, 4), (0, 5), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5)]
Q_TRIPLE_KEYS = [
    (0, 3, 4),
    (0, 3, 5),
    (0, 4, 5),
    (1, 3, 4),
    (1, 3, 5),
    (1, 4, 5),
    (2, 3, 4),
    (2, 3, 5),
    (2, 4, 5),
]
WOLFRAM = Path("/opt/sns/bin/WolframKernel")

BATCH_DATA_SLUG = "round5_joint_fan"
WALL_ANCHOR_P = (Fraction(-8), Fraction(2), Fraction(3), Fraction(4), Fraction(5), Fraction(-6))
WALL_DIRECTION = (Fraction(-2), Fraction(1), Fraction(0), Fraction(2), Fraction(-1), Fraction(0))


def fraction_to_str(v: Union[Fraction, int, str]) -> str:
    if not isinstance(v, Fraction):
        v = Fraction(v)
    if v.denominator == 1:
        return str(v.numerator)
    return f"{v.numerator}/{v.denominator}"


def sign_char(v: Fraction) -> str:
    if v > 0:
        return "1"
    if v < 0:
        return "-1"
    return "0"


def sorted_by_magnitude(omega: Sequence[Fraction]) -> Tuple[int, ...]:
    return tuple(sorted(range(6), key=lambda i: (-abs(omega[i]), i)))


def sha256_text(text: str) -> str:
    h = hashlib.sha256()
    h.update(text.encode())
    return h.hexdigest()


def labeled_magnitude_word(omega: Sequence[Fraction]) -> str:
    order = sorted_by_magnitude(omega)
    return "".join("-" if SIGMA[i] == -1 else "+" for i in order)


def q_pattern(point: R2.SixPoint) -> Tuple[str, ...]:
    return tuple(sign_char(point.pair_q[f"q_{m + 1}_{p + 1}"]) for m, p in Q_PAIR_KEYS)


def Q_pattern(point: R2.SixPoint) -> Tuple[str, ...]:
    return tuple(sign_char(point.triple_q[f"q_{m + 1}_{p + 1}{q + 1}"]) for m, p, q in Q_TRIPLE_KEYS)


def find_points(seed: int, max_iter: int = 120000) -> Iterator[R2.SixPoint]:
    rng = random.Random(seed)
    bounds = [6, 10, 16, 24, 34, 48, 74, 110]
    for bound in bounds:
        for _ in range(max_iter):
            b = Fraction(rng.randint(-bound, bound))
            c = Fraction(rng.randint(-bound, bound))
            d = Fraction(rng.randint(-bound, bound))
            e = Fraction(rng.randint(-bound, bound))
            if b == 0 or c == 0 or d == 0 or e == 0:
                continue
            try:
                p = R2.SixPoint(b, c, d, e)
            except Exception:
                continue
            if not p.is_generic():
                continue
            if p.C == 0:
                continue
            yield p


def find_points_from_seed(seed: int, max_iter: int = 200000) -> Iterator[R2.SixPoint]:
    yield from find_points(seed, max_iter=max_iter)


def unique_scale_key(point: R2.SixPoint) -> Tuple[str, ...]:
    prim, _ = point.primitive_scale()
    return tuple(str(v) for v in prim)


def compile_bg_round5(qdir: Path) -> Dict[str, object]:
    shared_bg = qdir / "bg.cpp"
    target_cpp = qdir / "bots" / "student-1" / "bg_round5.cpp"
    target_bin = qdir / "bots" / "student-1" / "bg_round5"
    target_bin.parent.mkdir(parents=True, exist_ok=True)
    if not shared_bg.exists():
        raise RuntimeError(f"shared bg.cpp not found at {shared_bg}")
    target_cpp.write_text(shared_bg.read_text())
    cmd = ["g++", "-O2", "-std=c++17", "-o", str(target_bin), str(target_cpp), "-lgmpxx", "-lgmp"]
    cp = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if cp.returncode != 0:
        raise RuntimeError("bg compile failed: %s" % cp.stderr.strip())
    return {
        "source": str(shared_bg),
        "copied": str(target_cpp),
        "binary": str(target_bin),
        "command": " ".join(cmd),
        "source_sha256": sha256_text(shared_bg.read_text()),
        "copy_sha256": sha256_text(target_cpp.read_text()),
        "build_stdout": cp.stdout.strip(),
        "build_stderr": cp.stderr.strip(),
        "status": "ok",
    }


def eval_row(point: R2.SixPoint, basis: List[Tuple[int, int, int, int, int]]) -> Optional[Dict[str, object]]:
    omega = point.omega
    if any(v == 0 for v in omega):
        return None
    if any(v == 0 for v in (point.b, point.c, point.d, point.e)):
        return None
    if pb.chamber_signature(omega) == "degenerate":
        return None

    channels, _, pole_sum = pb.build_channels(omega)
    if not channels:
        return None
    if any(c["d"] == 0 for c in channels):
        return None

    return {
        "point": point,
        "omega": [fraction_to_str(v) for v in omega],
        "chamber_signature": pb.chamber_signature(omega),
        "sorted_word": labeled_magnitude_word(omega),
        "magnitude_order": [str(i + 1) for i in sorted_by_magnitude(omega)],
        "q_sign": q_pattern(point),
        "Q_sign": Q_pattern(point),
        "pole_sum": fraction_to_str(pole_sum),
        "channels": channels,
    }


def eval_node_row(oracle: pb.BGOracle, point: R2.SixPoint, basis: List[Tuple[int, int, int, int, int]]) -> Optional[Dict[str, object]]:
    rec = eval_row(point, basis)
    if rec is None:
        return None
    try:
        bg = oracle._run_amp(point.omega, sigma=SIGMA)
    except Exception:
        return None
    if bg["re"] != 0:
        return None

    remainder, pole, pole_terms = R2.wall_pole_subtracted(point, bg["im"])
    if not pole_terms:
        # keep only rows where subtraction terms are non-empty for stability
        return None
    W, S = point.primitive_scale()
    degree = sum(basis[0])
    row = []
    for e in basis:
        val = 1
        for w, pw in zip(W, e):
            if pw:
                val *= int(w) ** int(pw)
        row.append(int(val))
    rhs = remainder * (S ** degree)
    rec.update(
        {
            "A6_im": fraction_to_str(bg["im"]),
            "P_pole": fraction_to_str(pole),
            "R": fraction_to_str(remainder),
            "R_scaled_row": row,
            "R_scaled_rhs": fraction_to_str(rhs),
            "bg_command": [str(x) for x in bg["command"]],
        }
    )
    return rec


def solve_with_wolfram(input_path: Path, output_path: Path):
    solver = SCRIPT_DIR / "round5_solve_exact.wl"
    proc = subprocess.run(
        [str(WOLFRAM), "-script", str(solver), str(input_path), str(output_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    if proc.returncode != 0:
        raise RuntimeError("wolfram solve failed: %s %s" % (proc.stdout, proc.stderr))
    return json.loads(output_path.read_text())


def fit_polynomial(
    name: str,
    qdir: Path,
    basis: List[Tuple[int, int, int, int, int]],
    rows: List[Dict[str, object]],
    target_rows: int,
    holdout_rows: int,
    holdout_cross_rows: int = 0,
    target_signature: Tuple[str, ...] = (),
) -> Tuple[Dict[str, object], List[Fraction]]:
    out_prefix = f"{BATCH_DATA_SLUG}_{name}"
    solve_input = qdir / "bots" / "student-1" / "data" / f"{out_prefix}_solve_input.json"
    solve_output = qdir / "bots" / "student-1" / "data" / f"{out_prefix}_solve_output.json"
    solve_input.parent.mkdir(parents=True, exist_ok=True)

    if len(rows) < target_rows:
        raise RuntimeError("insufficient rows for fit %s: got %d" % (name, len(rows)))

    mat: List[List[str]] = []
    rhs: List[str] = []
    for r in rows[:target_rows]:
        row = r["R_scaled_row"]
        mat.append([str(x) for x in row])
        rhs.append(str(r["R_scaled_rhs"]))
    solve_input.write_text(json.dumps({"matrix": mat, "rhs": rhs}, indent=2))
    solved = solve_with_wolfram(solve_input, solve_output)
    coeff = [Fraction(str(x)) for x in solved["coefficients"]]
    rank = solved.get("rank", 0)
    status = "ok" if (solved.get("rank") == len(basis) and solved.get("zero_residual")) else "fail"

    fit_payload = {
        "name": name,
        "basis_size": len(basis),
        "target_signature": tuple(target_signature),
        "train_target": target_rows,
        "holdout_target": holdout_rows,
        "rows_used": len(rows),
        "solve_input": str(solve_input),
        "solve_output": str(solve_output),
        "solve_rank": rank,
        "solve_zero_residual": solved.get("zero_residual"),
        "solve_status": status,
        "coefficients": [fraction_to_str(c) for c in coeff],
        "status": status,
        "nonzero_coefficients": sum(1 for c in coeff if c != 0),
        "term_count": len(coeff),
        "matrix_rows": len(mat),
        "matrix_cols": len(basis),
        "zero_residual": solved.get("zero_residual"),
        "solve_seconds": solved.get("solve_seconds"),
    }

    train_residuals = []
    for r, c_rhs in zip(rows[:target_rows], rhs):
        pred = sum(ci * Fraction(str(x)) for ci, x in zip(coeff, r["R_scaled_row"]))
        residual = Fraction(str(c_rhs)) - pred
        if residual != 0:
            train_residuals.append(residual)
    fit_payload["train_residual_nonzero"] = len(train_residuals)
    fit_payload["train_residual_witness"] = [fraction_to_str(v) for v in train_residuals[:12]]

    hold_same = []
    hold_cross = []
    for r in rows[target_rows:]:
        pred = sum(ci * Fraction(str(x)) for ci, x in zip(coeff, r["R_scaled_row"]))
        residual = Fraction(str(r["R_scaled_rhs"])) - pred
        if residual == 0:
            continue
        key = "same_chamber" if r.get("chamber_signature", "") == rows[0].get("chamber_signature", "") else "cross_chamber"
        entry = {
            "point": r["omega"],
            "residual": fraction_to_str(residual),
            "actual": str(r["R_scaled_rhs"]),
            "prediction": fraction_to_str(pred),
            "chamber_signature": r.get("chamber_signature"),
            "sorted_word": r.get("sorted_word"),
            "Q_sign": r.get("Q_sign"),
            "q_sign": r.get("q_sign"),
        }
        if key == "same_chamber":
            hold_same.append(entry)
        else:
            hold_cross.append(entry)
    hold_targets = hold_same[:holdout_rows]
    fit_payload["holdout_nonzero"] = len(hold_targets)
    fit_payload["holdout"] = hold_targets
    fit_payload["holdout_witness"] = [x["residual"] for x in hold_targets[:10]]
    if holdout_cross_rows:
        payload_cross = hold_cross[:holdout_cross_rows]
        fit_payload["cross_component_holdout_count"] = len(payload_cross)
        fit_payload["cross_component_holdout_witness"] = payload_cross
    return fit_payload, coeff


def collect_component_rows(
    oracle: pb.BGOracle,
    basis: List[Tuple[int, int, int, int, int]],
    target_q: Tuple[str, ...],
    target_Q: Tuple[str, ...],
    seed: int,
    max_points: int = 3200,
    target_train: int = 285,
) -> Tuple[List[Dict[str, object]], Dict[str, object]]:
    ranker = ModularRank(len(basis))
    points = []
    seen = set()
    stats = Counter(seed=seed, attempts=0, candidate_points=0, accepted=0, dedup_duplicates=0, signature_mismatch=0, rejected_bg_fail=0, rejected_wall=0)
    for p in find_points(seed, max_iter=max_points):
        stats["attempts"] += 1
        qsig = q_pattern(p)
        Qsig = Q_pattern(p)
        if qsig != target_q or Qsig != target_Q:
            stats["signature_mismatch"] += 1
            continue
        key = unique_scale_key(p)
        if key in seen:
            stats["dedup_duplicates"] += 1
            continue
        rec = eval_node_row(oracle, p, basis)
        if rec is None:
            stats["rejected_bg_fail"] += 1
            continue
        if rec["pole_sum"] == "0":
            stats["rejected_wall"] += 1
            continue
        seen.add(key)
        stats["candidate_points"] += 1
        if rec["chamber_signature"] == "degenerate":
            continue
        row = rec["R_scaled_row"]
        if ranker.add([int(x) for x in row]):
            points.append(rec)
            stats["accepted"] += 1
        if len(points) >= target_train and ranker.rank == len(basis):
            break
    stats["modular_rank"] = ranker.rank
    stats["full_rank"] = ranker.rank == len(basis)
    return points, dict(stats)


def collect_holdout_rows(
    oracle: pb.BGOracle,
    basis: List[Tuple[int, int, int, int, int]],
    target_q: Tuple[str, ...],
    target_Q: Tuple[str, ...],
    seen_keys: Iterable[Tuple[str, ...]],
    seed: int,
    target_hold: int = 40,
    cross_target: int = 0,
    chamber_ref: str = "",
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], Dict[str, object]]:
    seen = set(tuple(x) for x in seen_keys)
    hold = []
    cross = []
    attempts = 0
    same_chamber = 0
    cross_chamber = 0
    for p in find_points(seed, max_iter=200000):
        attempts += 1
        if attempts > 200000:
            break
        if q_pattern(p) != target_q or Q_pattern(p) != target_Q:
            continue
        key = unique_scale_key(p)
        if key in seen:
            continue
        rec = eval_node_row(oracle, p, basis)
        if rec is None:
            continue
        seen.add(key)
        if chamber_ref and rec["chamber_signature"] == chamber_ref:
            if same_chamber < target_hold:
                hold.append(rec)
                same_chamber += 1
        elif cross_target and cross_chamber < cross_target:
            cross.append(rec)
            cross_chamber += 1
        if same_chamber >= target_hold and cross_chamber >= cross_target:
            break
    return hold, cross, {"attempts": attempts, "same_chamber_collected": same_chamber, "cross_component_collected": cross_chamber}


def verify_wall_anchor(anchor: Tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction], oracle: pb.BGOracle) -> Dict[str, str]:
    if pb.chamber_signature(anchor) == "degenerate":
        raise RuntimeError("anchor is degenerate")
    point = R2.SixPoint(anchor[1], anchor[2], anchor[3], anchor[4])
    bg = oracle._run_amp(anchor, sigma=SIGMA)
    if bg["re"] != 0:
        raise RuntimeError("anchor has nonzero real part")
    remainder, pole, _ = R2.wall_pole_subtracted(point, bg["im"])
    return {
        "anchor": [fraction_to_str(x) for x in anchor],
        "A6_im": fraction_to_str(bg["im"]),
        "P_pole": fraction_to_str(pole),
        "R": fraction_to_str(remainder),
    }


def basis2_degree():
    # quotient-side degree-2 support count check with w6 elimination and on-shell reduction
    out = []
    for e5 in range(0, 2):
        rem = 2 - e5
        for e1 in range(rem + 1):
            for e2 in range(rem - e1 + 1):
                for e3 in range(rem - e1 - e2 + 1):
                    e4 = rem - e1 - e2 - e3
                    out.append((e1, e2, e3, e4, e5))
    seen = {}
    w1, w2, w3, w4, w5 = sp.symbols("w1 w2 w3 w4 w5")
    reduced = []
    for e in out:
        mon = w1**e[0] * w2**e[1] * w3**e[2] * w4**e[3] * w5**e[4]
        mon = sp.expand(reduce_w5(mon, (w1, w2, w3, w4, w5)).as_expr())
        poly = sp.Poly(mon, w1, w2, w3, w4, w5, domain=sp.QQ)
        terms = poly.terms()
        items = tuple(terms[0][0]) if terms else (0, 0, 0, 0, 0)
        if items not in seen:
            seen[items] = e
            reduced.append(items)
    return list(seen.keys()), len(out), len(reduced), [str(k) for k in seen.keys()]


class ComponentResult:
    __slots__ = (
        "name",
        "q_sign",
        "Q_sign",
        "rows",
        "hold",
        "hold_cross",
        "fit_payload",
        "coeff",
        "signature_map_ok",
        "signature_counterexample",
        "source",
    )

    def __init__(
        self,
        name: str,
        q_sign: Tuple[str, ...],
        Q_sign: Tuple[str, ...],
        rows: List[Dict[str, Any]],
        hold: List[Dict[str, Any]],
        hold_cross: List[Dict[str, Any]],
        fit_payload: Dict[str, Any],
        coeff: List[Fraction],
        signature_map_ok: bool,
        signature_counterexample: Optional[Dict[str, Any]],
        source: str,
    ):
        self.name = name
        self.q_sign = q_sign
        self.Q_sign = Q_sign
        self.rows = rows
        self.hold = hold
        self.hold_cross = hold_cross
        self.fit_payload = fit_payload
        self.coeff = coeff
        self.signature_map_ok = signature_map_ok
        self.signature_counterexample = signature_counterexample
        self.source = source


def build_component(
    oracle: pb.BGOracle,
    qdir: Path,
    basis8: List[Tuple[int, int, int, int, int]],
    component_index: int,
    q_sign: Tuple[str, ...],
    Q_sign: Tuple[str, ...],
    seed: int,
) -> Optional[ComponentResult]:
    component_rows, collect_stats = collect_component_rows(
        oracle=oracle, basis=basis8, target_q=q_sign, target_Q=Q_sign, seed=seed, target_train=285, max_points=220000
    )
    if len(component_rows) < 285 or collect_stats.get("modular_rank", 0) < len(basis8):
        return None
    chamber_ref = component_rows[0]["chamber_signature"]
    hold, cross_hold, _ = collect_holdout_rows(
        oracle=oracle,
        basis=basis8,
        target_q=q_sign,
        target_Q=Q_sign,
        seen_keys=[unique_scale_key(point["point"]) for point in component_rows],
        chamber_ref=chamber_ref,
        seed=seed + 111,
        target_hold=40,
        cross_target=20,
    )
    combo_rows = component_rows + hold + cross_hold
    fit_payload, coeff = fit_polynomial(
        name=f"component_{component_index:02d}_{''.join(q_sign)}_{''.join(Q_sign)}",
        qdir=qdir,
        basis=basis8,
        rows=combo_rows,
        target_rows=285,
        holdout_rows=40,
        holdout_cross_rows=20,
        target_signature=tuple(q_sign + Q_sign),
    )
    signature_map = {tuple(q_sign + Q_sign): chamber_ref}
    consistent = True
    counterexample = None
    for rec in combo_rows:
        key = rec["q_sign"] + rec["Q_sign"]
        if key in signature_map and signature_map[key] != rec["chamber_signature"]:
            consistent = False
            if counterexample is None:
                counterexample = {
                    "signature": key,
                    "expected": signature_map[key],
                    "observed": rec["chamber_signature"],
                    "point": rec["omega"],
                }
        else:
            signature_map[key] = rec["chamber_signature"]
    return ComponentResult(
        name=f"component_{component_index:02d}",
        q_sign=q_sign,
        Q_sign=Q_sign,
        rows=component_rows,
        hold=hold,
        hold_cross=cross_hold,
        fit_payload=fit_payload,
        coeff=coeff,
        signature_map_ok=consistent,
        signature_counterexample=counterexample,
        source=f"seed={seed}",
    )


def q_wall_sorted_transport_payload(rows: List[Dict[str, object]]) -> Tuple[List[str], Dict[str, object]]:
    import round4_sorted_transport as rt
    import round3_nested as rn_local  # noqa: F401

    graph = rt.build_graph()
    _, paths = rt.shortest_path_dag(graph, rt.REFERENCE_WORD)
    ref = rt.REFERENCE_WORD
    inconsistencies = 0
    per_row = []
    for row in rows:
        omega = [Fraction(x) for x in row["point"].omega]
        increments = []
        for tgt in paths:
            incs = rt.all_paths_increment_variants(omega, paths[tgt])
            vals = [x["increment"] for x in incs]
            if len(set(vals)) > 1:
                inconsistencies += 1
            increments.append(
                {
                    "target": tgt,
                    "count": len(vals),
                    "sample": str(vals[0]) if vals else "0",
                    "paths": len(incs),
                }
            )
        per_row.append({"point": row.get("omega"), "sorted_word": row["sorted_word"], "inconsistencies": increments})
    return [ref], {"reference_word": ref, "inconsistency_count": inconsistencies, "sample_rows": per_row[:16]}


def main():
    parser = argparse.ArgumentParser(description="Round5 joint-fan wall-batch harness")
    parser.add_argument("--qdir", type=Path, default=Path("."))
    parser.add_argument("--components", type=int, default=3)
    parser.add_argument("--component-train", type=int, default=285)
    parser.add_argument("--component-hold", type=int, default=40)
    parser.add_argument("--component-cross-hold", type=int, default=20)
    parser.add_argument("--assembly-points", type=int, default=340)
    parser.add_argument("--assembly-hold", type=int, default=100)
    args = parser.parse_args()

    qdir = args.qdir.resolve()
    output = qdir / "bots" / "student-1" / "data" / f"{BATCH_DATA_SLUG}.json"
    report = qdir / "bots" / "student-1" / "derivations" / f"{BATCH_DATA_SLUG}_raw_report.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)

    compile_info = compile_bg_round5(qdir)
    oracle = pb.BGOracle(qdir / "bots" / "student-1" / "bg_round5", sigma=SIGMA, g=1)
    anchor = verify_wall_anchor(WALL_ANCHOR_P, oracle)

    basis8 = homogeneous_basis(8)
    if len(basis8) != 285:
        raise RuntimeError("unexpected basis8 size=%d" % len(basis8))
    deg2_full = basis2_degree()

    # Discover at least the requested number of distinct (q,Q) signatures from random scans.
    discovered: Dict[Tuple[Tuple[str, ...], Tuple[str, ...]], int] = {}
    discovery_order: List[Tuple[Tuple[str, ...], Tuple[str, ...], str, int]] = []
    for seed in range(2027, 2077):
        for p in find_points_from_seed(seed, max_iter=2000):
            qsig = q_pattern(p)
            Qsig = Q_pattern(p)
            if "0" in qsig or "0" in Qsig:
                continue
            key = (qsig, Qsig)
            if key not in discovered:
                discovered[key] = seed
                discovery_order.append((qsig, Qsig, labeled_magnitude_word(p.omega), seed))
            if len(discovery_order) >= max(args.components, 8):
                break
        if len(discovery_order) >= max(args.components, 8):
            break

    selected = discovery_order[: args.components]
    if len(selected) < args.components:
        raise RuntimeError(f"insufficient distinct open signatures found: {len(selected)}")

    components = []
    comp_failures = []
    for idx, (qsig, Qsig, _word, seed) in enumerate(selected[: args.components]):
        try:
            result = build_component(
                oracle=oracle,
                qdir=qdir,
                basis8=basis8,
                component_index=idx,
                q_sign=qsig,
                Q_sign=Qsig,
                seed=seed,
            )
        except Exception as exc:
            comp_failures.append({"component": idx, "seed": seed, "signature": {"q": qsig, "Q": Qsig}, "error": str(exc)})
            continue
        if result is not None:
            components.append(result)

    # lightweight joint-wall and transport summary from the existing sorted-word machinery
    wall_payload = {"status": "insufficient_lines", "candidate_points": []}
    line_points = []
    for t in [Fraction(k, 12) for k in range(-12, 13) if k != 3]:
        w = tuple(WALL_ANCHOR_P[i] + t * WALL_DIRECTION[i] for i in range(6))
        if any(x == 0 for x in w) or pb.chamber_signature(w) == "degenerate":
            continue
        try:
            p = R2.SixPoint(w[1], w[2], w[3], w[4])
        except Exception:
            continue
        row = eval_node_row(oracle, p, basis8)
        if row is None:
            continue
        row["t_param"] = str(t)
        line_points.append(row)
    if line_points:
        wall_payload = {
            "candidate_points": [
                {
                    "t": r.get("t_param"),
                    "omega": r["omega"],
                    "q_sign": r["q_sign"],
                    "Q_sign": r["Q_sign"],
                    "sorted_word": r["sorted_word"],
                    "subset_signature": r["chamber_signature"],
                }
                for r in line_points
            ],
            "line_points": len(line_points),
            "status": "collected",
        }

    # Generic assembly-style sanity bundle
    assembly_rows = []
    for p in find_points_from_seed(2028, max_iter=40000):
        if any(v == 0 for v in p.omega):
            continue
        rec = eval_node_row(oracle, p, basis8)
        if rec is None:
            continue
        assembly_rows.append(rec)
        if len(assembly_rows) >= args.assembly_points:
            break
    if len(assembly_rows) >= args.assembly_points:
        ref_words, transport_payload = q_wall_sorted_transport_payload(assembly_rows)
        assembly_status = {
            "status": "collected",
            "rows": len(assembly_rows),
            "reference_words": ref_words,
            "subset": transport_payload,
        }
    else:
        assembly_status = {"status": "insufficient_assembly_points", "collected": len(assembly_rows)}

    component_rows = [
        {
            "name": c.name,
            "source": c.source,
            "q_sign": "".join(c.q_sign),
            "Q_sign": "".join(c.Q_sign),
            "train_rows": len(c.rows),
            "holdout_rows": len(c.hold),
            "holdout_cross_rows": len(c.hold_cross),
            "fit": c.fit_payload,
            "signature_map_ok": c.signature_map_ok,
            "signature_counterexample": c.signature_counterexample,
        }
        for c in components
    ]

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "qdir": str(qdir),
        "compile": compile_info,
        "anchor": anchor,
        "basis": {
            "size8": len(basis8),
            "size2": deg2_full[1],
            "size2_quotient": deg2_full[2],
            "size2_reduced_terms": deg2_full[3],
        },
        "component_discovery": {
            "requested": args.components,
            "discovered": len(discovery_order),
            "selected": len(selected),
            "ordered": [
                {
                    "q_sign": "".join(x[0]),
                    "Q_sign": "".join(x[1]),
                    "word": x[2],
                    "seed": x[3],
                }
                for x in selected
            ],
        },
        "component_failures": comp_failures,
        "components": component_rows,
        "line_wall": wall_payload,
        "assembly": assembly_status,
        "notes": [
            "run includes per-fit inputs/outputs under bots/student-1/data/ with prefix round5_.",
        ],
    }
    output.write_text(json.dumps(payload, indent=2))

    lines = [
        "# Round-5 joint fan harness (round5_joint_fan)",
        "",
        f"- anchor A6/i: {payload['anchor']['A6_im']}",
        f"- anchor P_pole: {payload['anchor']['P_pole']}",
        f"- components requested/found: {args.components}/{len(components)}",
        f"- line wall samples: {wall_payload.get('line_points', 0)}",
        f"- assembly status: {payload['assembly']['status']}",
    ]
    for c in component_rows:
        lines.append(
            "- %s: rank %s, holdout nonzero %s/%d, cross-chamber %d, signature map ok=%s"
            % (
                c["name"],
                c["fit"].get("solve_rank"),
                c["fit"].get("holdout_nonzero"),
                c["holdout_rows"],
                c["signature_map_ok"],
            )
        )
    report.write_text("\n".join(lines) + "\n")

    print(str(output))
    print(str(report))
    print("component_count=%d" % len(components))


if __name__ == "__main__":
    main()
