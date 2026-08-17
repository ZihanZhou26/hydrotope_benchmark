#!/usr/bin/env python3

from collections import Counter, defaultdict, deque
from fractions import Fraction
from pathlib import Path
import argparse
import json
import random
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

import sympy as sp

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import round3_nested as rn  # noqa: E402
import pole_batch as pb  # noqa: E402

REALIZED_WORDS = (
    "-+++--",
    "-++--+",
    "-++-+-",
    "+---++",
    "+--+-+",
    "+--++-",
    "-+-++-",
    "+-+--+",
)
REFERENCE_WORD = "-+++--"
SIGMA = pb.SIGMA
MINUS = (0, 1, 2)
PLUS = (3, 4, 5)


def frac_to_str(v: Fraction) -> str:
    if v.denominator == 1:
        return str(v.numerator)
    return f"{v.numerator}/{v.denominator}"


def copy_source(qdir: Path) -> Tuple[Path, Path]:
    src = qdir / "bots/student-1/bg.cpp"
    if not src.exists():
        legacy = qdir / "bg.cpp"
        if not legacy.exists():
            raise RuntimeError(f"shared bg.cpp not found at {qdir / 'bg.cpp'}")
        src = legacy
    target = qdir / "bots/student-1/bg_round4.cpp"
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
    cp = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if cp.returncode != 0:
        raise RuntimeError(f"bg compile failed: {cp.stderr.strip()}")
    return {
        "command": " ".join(cmd),
        "returncode": cp.returncode,
        "stderr": cp.stderr.strip(),
        "stdout": cp.stdout.strip(),
    }


def build_graph() -> Dict[str, List[str]]:
    words = set(REALIZED_WORDS)
    graph = {w: set() for w in words}
    for w in words:
        for i in range(5):
            pair = w[i : i + 2]
            if pair not in {"-+", "+-"}:
                continue
            nw = w[:i] + pair[1] + pair[0] + w[i + 2 :]
            if nw in words:
                graph[w].add(nw)
                graph[nw].add(w)
    return {k: sorted(v) for k, v in graph.items()}


def shortest_path_dag(graph: Dict[str, List[str]], src: str) -> Tuple[Dict[str, int], Dict[str, List[List[str]]]]:
    dist: Dict[str, int] = {src: 0}
    q = deque([src])
    while q:
        u = q.popleft()
        du = dist[u]
        for v in graph[u]:
            if v not in dist:
                dist[v] = du + 1
                q.append(v)

    # Precompute all shortest paths from src to each target in reverse recursion.
    memo: Dict[str, List[List[str]]] = {src: [[src]]}

    def paths_to_node(node: str) -> List[List[str]]:
        if node in memo:
            return memo[node]
        out: List[List[str]] = []
        dnode = dist.get(node)
        if dnode is None:
            memo[node] = out
            return out
        for prev in graph[node]:
            if dist.get(prev) == dnode - 1:
                for pth in paths_to_node(prev):
                    out.append(pth + [node])
        memo[node] = out
        return out

    for w in graph:
        if w not in memo:
            paths_to_node(w)
    return dist, memo


def label_sequence_for_word(omega: Tuple[Fraction, ...], word: str, order: Tuple[int, ...]):
    minus_labels = tuple(sorted(MINUS, key=lambda i: (-omega[i] * omega[i], i)))
    plus_labels = tuple(sorted(PLUS, key=lambda i: (-omega[i] * omega[i], i)))
    m_ptr = 0
    p_ptr = 0
    labels = []
    if len(word) != len(order):
        raise ValueError("word length mismatch for label assignment")
    for ch, idx in zip(word, order):
        if ch == "-":
            labels.append(minus_labels[m_ptr])
            m_ptr += 1
            if m_ptr > len(minus_labels):
                raise ValueError("too many minus positions in word")
        elif ch == "+":
            labels.append(plus_labels[p_ptr])
            p_ptr += 1
            if p_ptr > len(plus_labels):
                raise ValueError("too many plus positions in word")
        else:
            raise RuntimeError("invalid character in signed word")
    if m_ptr != len(MINUS) or p_ptr != len(PLUS):
        raise RuntimeError("label assignment did not consume expected signs")
    return tuple(labels)


def sorted_word_and_labels(omega: Tuple[Fraction, ...]) -> Tuple[str, Tuple[int, ...], Tuple[int, ...]]:
    order = tuple(sorted(range(6), key=lambda i: (-abs(omega[i]), i)))
    word = pb.sorted_sign_word(omega)
    labels = label_sequence_for_word(omega, word, order)
    return word, labels, order


def edge_context_from_node(omega: Tuple[Fraction, ...], word: str, labels: Tuple[int, ...], pos: int):
    left_sig = word[pos]
    right_sig = word[pos + 1]
    if left_sig not in {"-", "+"} or right_sig not in {"-", "+"}:
        raise RuntimeError("edge context requested for non-adjacent pair")
    if left_sig == right_sig:
        raise RuntimeError("edge context requested for same-sign pair")

    left_label = labels[pos]
    right_label = labels[pos + 1]
    if left_sig == "-":
        m_idx = left_label
        p_idx = right_label
        orientation = -1  # -+ -> +- orientation
    else:
        m_idx = right_label
        p_idx = left_label
        orientation = 1  # +- -> -+

    remaining = [l for l in labels if l not in {m_idx, p_idx}]
    if len(remaining) != 4:
        raise RuntimeError("label bookkeeping failed")
    beta_idx = remaining[-1]

    x = [omega[i] * omega[i] for i in range(6)]
    q = x[p_idx] - x[m_idx]

    minus_set = set(MINUS)
    plus_set = set(PLUS)
    if (m_idx not in minus_set) or (p_idx not in plus_set):
        raise RuntimeError("primary labels are not one minus and one plus")

    other_minus = tuple(sorted(i for i in minus_set if i != m_idx))
    a = omega[m_idx]
    p = omega[p_idx]
    s = omega[other_minus[0]] + omega[other_minus[1]]
    v = omega[other_minus[0]] * omega[other_minus[1]]
    Fm = a * s ** 3 + v * (s ** 2 - 2 * v)
    D = 2 * a ** 3 + 3 * a ** 2 * s + a * (s * s + v) - s * v

    if beta_idx in minus_set:
        if beta_idx == other_minus[0]:
            y = omega[beta_idx]
            x_idx = other_minus[1]
        elif beta_idx == other_minus[1]:
            y = omega[beta_idx]
            x_idx = other_minus[0]
        else:
            raise RuntimeError("beta minus index inconsistent")
        x_idx = x_idx
        x_val = omega[x_idx]
        L = 3 * a ** 2 + 2 * a * (s + p) - v + p * (2 * x_val + y)
        H = -32 * y ** 2 * (Fm + (a + p) * D) - 32 * q * y ** 2 * L + 32 * x_val * p * q ** 2
        beta_type = "minus"
    else:
        x_m1, x_m2 = (omega[other_minus[0]], omega[other_minus[1]])
        z = omega[beta_idx]
        A0 = a ** 4 + 4 * a ** 3 * p + 4 * a ** 3 * z + 4 * a ** 2 * p ** 2 + 6 * a ** 2 * p * z + a * p ** 3 + 2 * a * p ** 2 * z
        A1 = 4 * a ** 3 + 8 * a ** 2 * p + 7 * a ** 2 * z + 5 * a * p ** 2 + 7 * a * p * z + p ** 3 + p ** 2 * z
        A2 = 3 * a ** 2 + 4 * a * p + 3 * a * z + p ** 2 + p * z
        B0 = 3 * a ** 2 + 2 * a * p + a * z
        B1 = 3 * a + p
        K = A0 + s * A1 + s * s * A2 + v * B0 + s * v * B1
        H = -32 * z ** 2 * (Fm + (a + p) * D) + 32 * q * K
        beta_type = "plus"
    inc = orientation * q * H
    return {
        "m": m_idx,
        "p": p_idx,
        "beta": beta_idx,
        "q": q,
        "q_sign": 1 if q > 0 else (-1 if q < 0 else 0),
        "orientation": orientation,
        "beta_type": beta_type,
        "increment": inc,
    }


def path_increment(omega: Tuple[Fraction, ...], path: List[str]) -> Dict[str, object]:
    total = Fraction(0, 1)
    edge_info = []
    for a_word, b_word in zip(path, path[1:]):
        diff = [i for i, (x, y) in enumerate(zip(a_word, b_word)) if x != y]
        if len(diff) != 2 or sorted(diff)[1] - sorted(diff)[0] != 1:
            raise RuntimeError(f"non-adjacent swap in path: {a_word}->{b_word}")
        pos = min(diff)
        order = tuple(sorted(range(6), key=lambda i: (-abs(omega[i]), i)))
        labels = label_sequence_for_word(omega, a_word, order)  # rebuild per-node label map
        context = edge_context_from_node(omega, a_word, labels, pos)
        total += context["increment"]
        edge_info.append(
            {
                "from": a_word,
                "to": b_word,
                "swap_pos": pos,
                "swap": f"{a_word[pos]}{b_word[pos + 1]}",
                "m": context["m"] + 1,
                "p": context["p"] + 1,
                "beta": context["beta"] + 1,
                "beta_type": context["beta_type"],
                "q": frac_to_str(context["q"]),
                "q_sign": context["q_sign"],
                "orientation": context["orientation"],
                "color": "minus-plus" if context["orientation"] == 1 else "plus-minus",
            }
        )
    return {"increment": total, "edges": edge_info}


def all_paths_increment_variants(omega: Tuple[Fraction, ...], paths: List[List[str]]):
    increments = []
    for pth in paths:
        item = path_increment(omega, pth)
        increments.append(item)
    return increments


def evaluate_point(oracle: pb.BGOracle, omega: Tuple[Fraction, ...], source: str, base_orbit_id: str) -> Optional[Dict[str, object]]:
    if any(w == 0 for w in omega):
        return {"status": "reject", "reason": "zero_omega"}
    if not pb.on_shell(omega, sigma=SIGMA):
        return {"status": "reject", "reason": "not_on_shell"}
    if len(set(abs(w) for w in omega)) != 6:
        return {"status": "reject", "reason": "duplicate_magnitudes"}
    chamber = pb.chamber_signature(omega)
    if chamber == "degenerate":
        return {"status": "reject", "reason": "degenerate_chamber"}
    if rn.wall_product(omega) == 0:
        return {"status": "reject", "reason": "wall_product_zero"}

    C = omega[0] * omega[1] * omega[2] + omega[3] * omega[4] * omega[5]
    if C == 0:
        return {"status": "reject", "reason": "C_zero"}

    x = [w * w for w in omega]
    for m in MINUS:
        for p in PLUS:
            if x[p] == x[m]:
                return {"status": "reject", "reason": "Q_T_zero"}

    channels, p_pole, _ = pb.build_channels(omega)
    if any(c["d"] == 0 for c in channels):
        return {"status": "reject", "reason": "zero_denom_d"}

    try:
        bg = oracle._run_amp(omega, sigma=SIGMA)
    except Exception:
        return {"status": "reject", "reason": "bg_fail"}

    if bg["re"] != 0:
        return {"status": "reject", "reason": "nonzero_real_part"}

    # reject if any positive q-channel is exactly on wall
    for c in channels:
        if c["Q"] == 0:
            return {"status": "reject", "reason": "Q_zero_channel"}

    word, labels, order = sorted_word_and_labels(omega)
    if word not in REALIZED_WORDS:
        return {"status": "reject", "reason": "unrealized_word", "word": word}

    a = sum(omega[:3])
    v = omega[0] * omega[1] + omega[0] * omega[2] + omega[1] * omega[2]
    a3 = omega[0] * omega[1] * omega[2]
    b3 = omega[3] * omega[4] * omega[5]

    return {
        "status": "ok",
        "source": source,
        "base_orbit_id": base_orbit_id,
        "omega": omega,
        "sorted_word": word,
        "labels": labels,
        "order": order,
        "chamber": chamber,
        "A6_im": bg["im"],
        "P_pole": p_pole,
        "R": bg["im"] - p_pole,
        "u": a,
        "v": v,
        "a3": a3,
        "b3": b3,
    }


def build_rows(qdir: Path, target_total: int) -> Tuple[List[Dict[str, object]], Dict[str, int]]:
    oracle = pb.BGOracle(binary_path=str(qdir / "bots/student-1/bg_round4"), sigma=SIGMA, g=1)
    targets = max(target_total, 160)
    max_rows = max(targets, 2 * targets)
    records = []
    seen = set()
    counts = Counter()
    bases = rn.seed_records(qdir)
    if not bases:
        raise RuntimeError("no base orbit seeds available")

    orbit_variants = [(base, rn.build_orbit_variants(base)) for base in bases]
    orbit_variants = [(b, v) for b, v in orbit_variants if v]
    if not orbit_variants:
        return records, dict(counts)

    max_rounds = max(len(v) for _, v in orbit_variants)
    got_all_words = set(REALIZED_WORDS)

    round_idx = 0
    while len(records) < max_rows and round_idx < max_rounds:
        added = 0
        for base, variants in orbit_variants:
            if len(records) >= max_rows:
                break
            if round_idx >= len(variants):
                continue
            omega, source = variants[round_idx]
            if omega in seen:
                continue
            evaluated = evaluate_point(oracle, omega, source, base["base_orbit_id"])
            status = evaluated["status"]
            counts[status] += 1
            if status != "ok":
                continue
            seen.add(omega)
            records.append(evaluated)
            added += 1

        round_idx += 1
        if len(records) >= targets and got_all_words.issubset(set(r["sorted_word"] for r in records)):
            break
        if len(records) >= max_rows:
            break
        if added == 0:
            break

    if len(records) < targets:
        # final fallback: consume remaining round-robin slots up to max_rows if possible
        for base, variants in orbit_variants:
            for omega, source in variants[round_idx:]:
                if len(records) >= max_rows:
                    break
                if omega in seen:
                    continue
                evaluated = evaluate_point(oracle, omega, source, base["base_orbit_id"])
                status = evaluated["status"]
                counts[status] += 1
                if status != "ok":
                    continue
                seen.add(omega)
                records.append(evaluated)
            if len(records) >= max_rows:
                break

    # dedupe and order deterministically by stable signature
    if not got_all_words.issubset(set(r["sorted_word"] for r in records)):
        counts["missing_word_count"] = len(got_all_words - set(r["sorted_word"] for r in records))
    records.sort(key=lambda r: (r["sorted_word"], frac_to_str(r["A6_im"])))
    return records, dict(counts)


def dual_basis_terms() -> List[Tuple[int, int, int, int]]:
    terms = []
    for i in range(9):
        for j in range(9):
            for k in range(4):
                for l in range(4):
                    if i + 2 * j + 3 * k + 3 * l == 8:
                        terms.append((i, j, k, l))
    return terms


def dual_value(row: Dict[str, object], term: Tuple[int, int, int, int]) -> Fraction:
    i, j, k, l = term
    return row["u"] ** i * row["v"] ** j * row["a3"] ** k * row["b3"] ** l


def fit_linear_system(rows: List[Dict[str, object]], ys: List[Fraction], terms: List[Tuple[int, int, int, int]]):
    A = [[dual_value(r, t) for t in terms] for r in rows]
    labels = ["%s_row_%d" % (r["sorted_word"], i) for i, r in enumerate(rows)]
    ok, coeff, rank_a, rank_aug, witness = rn.gauss_solve_exact(A, ys, row_labels=labels)
    return ok, coeff, rank_a, rank_aug, witness


def pick_rank_rows_greedily(
    candidate_rows: List[Dict[str, object]],
    target_values: List[Fraction],
    terms: List[Tuple[int, int, int, int]],
    row_target: int = 17,
):
    selected = []
    selected_targets = []

    if len(candidate_rows) < row_target:
        raise RuntimeError("insufficient rows for greedy full-rank selection")

    for r, y in zip(candidate_rows, target_values):
        trial = selected + [r]
        A_trial = [[dual_value(rt, t) for t in terms] for rt in trial]
        if len(rn.independent_columns(A_trial)) == len(trial):
            selected.append(r)
            selected_targets.append(y)
            if len(selected) == row_target:
                break

    if len(selected) < row_target:
        raise RuntimeError(
            f"could not find {row_target} independent fit rows in the requested train set"
        )

    ok, coeff, rank_a, rank_aug, witness = fit_linear_system(selected, selected_targets, terms)
    if not ok:
        raise RuntimeError(f"greedy 17-row fit failed: {witness}")

    if rank_a != row_target:
        raise RuntimeError(f"greedy fit rank mismatch: got {rank_a}, expected {row_target}")

    return selected, selected_targets, coeff, witness


def evaluate_raw_rows(
    rows_to_test: List[Dict[str, object]],
    coeff: List[Fraction],
    terms: List[Tuple[int, int, int, int]],
    target_key: str,
):
    nonzero_count = 0
    witness = None

    for row in rows_to_test:
        pred = sum(c * dual_value(row, t) for c, t in zip(coeff, terms))
        residual = row[target_key] - pred
        if residual != 0:
            nonzero_count += 1
            if witness is None:
                witness = {
                    "point_id": row["point_id"],
                    "source": row["source"],
                    "word": row["sorted_word"],
                    "omega": [frac_to_str(v) for v in row["omega"]],
                    "target": frac_to_str(row[target_key]),
                    "prediction": frac_to_str(pred),
                    "residual": frac_to_str(residual),
                }
    return nonzero_count, witness


def build_candidate_fit_payload(
    rows_all: List[Dict[str, object]],
    train_rows: List[Dict[str, object]],
    terms: List[Tuple[int, int, int, int]],
    target_key: str,
    need_path_context: bool = False,
):
    train_targets = [r[target_key] for r in train_rows]
    fit_rows, fit_targets, coeff, witness = pick_rank_rows_greedily(train_rows, train_targets, terms)

    fit_rows_meta = [
        {
            "point_id": r["point_id"],
            "source": r["source"],
            "word": r["sorted_word"],
            "omega": [frac_to_str(v) for v in r["omega"]],
            "target": frac_to_str(fit_targets[i]),
        }
        for i, r in enumerate(fit_rows)
    ]

    excluded_orbits = {r["base_orbit_id"] for r in fit_rows}
    eval_rows = [r for r in rows_all if r["base_orbit_id"] not in excluded_orbits]

    nonzero_count, raw_witness = evaluate_raw_rows(eval_rows, coeff, terms, target_key)

    if need_path_context and raw_witness is not None:
        tgt = raw_witness["word"]
        pctx = None
        if rows_all:
            src_r = next((r for r in eval_rows if r["point_id"] == raw_witness["point_id"]), None)
            if src_r is not None:
                detail = src_r.get("path_increment_by_target", {}).get(tgt, {})
                if detail:
                    pctx = {
                        "reference": REFERENCE_WORD,
                        "target": tgt,
                        "canonical_path": detail.get("canonical_path", []),
                        "edge_contexts": detail.get("canonical_edges", []),
                    }
        raw_witness["path_context"] = pctx

    return {
        "fit_rows": fit_rows_meta,
        "fit_row_ids": [r["point_id"] for r in fit_rows],
        "fit_row_count": len(fit_rows),
        "fit_row_orbit_count": len(excluded_orbits),
        "direct_fit_rows_evaluated": len(eval_rows),
        "nonzero_residual_count": nonzero_count,
        "first_raw_witness": raw_witness,
        "raw_gauss_witness": witness,
    }


def evaluate_matrix(values, coeff):
    return [sum(a * b for a, b in zip(v, coeff)) for v in values]


def sample_split_by_base_orbit(rows: List[Dict[str, object]], train_target: int, hold_target: int, rng_seed: int = 2026):
    if not rows:
        return [], [], {}

    by_orbit = defaultdict(list)
    for r in rows:
        by_orbit[r["base_orbit_id"]].append(r)

    # preserve deterministic per-orbit ordering by point ids
    for rid in by_orbit:
        by_orbit[rid] = list(by_orbit[rid])

    orbits = sorted(by_orbit.keys())
    train = []
    hold = []
    remaining_orbits = list(orbits)
    rng = random.Random(rng_seed)

    def add_orbits_to_target(target: int, target_list: List[Dict[str, object]]) -> bool:
        progress = False
        # shuffle orbit order only once for reproducibility with a fixed seed
        if target_list is train:
            rng.shuffle(remaining_orbits)
        for oid in list(remaining_orbits):
            if len(target_list) >= target:
                break
            group = by_orbit.pop(oid, [])
            if not group:
                continue
            target_list.extend(group)
            remaining_orbits.remove(oid)
            progress = True
            if len(target_list) >= target:
                break
        return progress

    while len(train) < train_target:
        if not add_orbits_to_target(train_target, train):
            break

    if len(train) < train_target:
        # fallback from leftover points only when no more full orbits remain
        all_rem = []
        for vv in by_orbit.values():
            all_rem.extend(vv)
        rng.shuffle(all_rem)
        train.extend(all_rem)

    used_train_orbits = set()
    for r in train:
        used_train_orbits.add(r["base_orbit_id"])
    for oid in list(used_train_orbits):
        by_orbit.pop(oid, None)

    while len(hold) < hold_target:
        if not add_orbits_to_target(hold_target, hold):
            break

    if len(hold) < hold_target:
        all_rem = []
        for vv in by_orbit.values():
            all_rem.extend(vv)
        rng.shuffle(all_rem)
        hold.extend(all_rem)

    if len(train) > train_target:
        # keep deterministic split while preserving whole-orbit constraints
        # cap only if we have enough points from complete orbits
        if len(train) > train_target and len(train) - train_target <= 2:
            pass

    if len(hold) > hold_target:
        # similar tolerance is acceptable; avoid dropping partial orbits
        pass

    by_word_train = Counter(r["sorted_word"] for r in train)
    by_word_hold = Counter(r["sorted_word"] for r in hold)

    train = [dict(r) for r in train]
    hold = [dict(r) for r in hold]

    return train, hold, {
        "requested_train": train_target,
        "requested_hold": hold_target,
        "actual_train": len(train),
        "actual_hold": len(hold),
        "word_coverage_train": dict(by_word_train),
        "word_coverage_hold": dict(by_word_hold),
    }


def sample_split_by_word(rows: List[Dict[str, object]], train_target: int, hold_target: int, rng_seed: int = 2026):
    # backward-compatible wrapper retained for diagnostics/older JSON reads
    return sample_split_by_base_orbit(rows, train_target, hold_target, rng_seed)


def h_minus_sym(a, p, x, y):
    q = p ** 2 - a ** 2
    s = x + y
    v = x * y
    Fm = a * s ** 3 + v * (s ** 2 - 2 * v)
    D = 2 * a ** 3 + 3 * a ** 2 * s + a * (s ** 2 + v) - s * v
    L = 3 * a ** 2 + 2 * a * (s + p) - v + p * (2 * x + y)
    return -32 * y ** 2 * (Fm + (a + p) * D) - 32 * q * y ** 2 * L + 32 * x * p * q ** 2


def h_plus_sym(a, p, x, y, z):
    q = p ** 2 - a ** 2
    s = x + y
    v = x * y
    Fm = a * s ** 3 + v * (s ** 2 - 2 * v)
    D = 2 * a ** 3 + 3 * a ** 2 * s + a * (s ** 2 + v) - s * v
    A0 = a ** 4 + 4 * a ** 3 * p + 4 * a ** 3 * z + 4 * a ** 2 * p ** 2 + 6 * a ** 2 * p * z + a * p ** 3 + 2 * a * p ** 2 * z
    A1 = 4 * a ** 3 + 8 * a ** 2 * p + 7 * a ** 2 * z + 5 * a * p ** 2 + 7 * a * p * z + p ** 3 + p ** 2 * z
    A2 = 3 * a ** 2 + 4 * a * p + 3 * a * z + p ** 2 + p * z
    B0 = 3 * a ** 2 + 2 * a * p + a * z
    B1 = 3 * a + p
    K = A0 + s * A1 + s ** 2 * A2 + v * B0 + s * v * B1
    return -32 * z ** 2 * (Fm + (a + p) * D) + 32 * q * K


def gm_candidate(point: Dict[str, object]) -> Fraction:
    w = point["omega"]
    total = Fraction(0, 1)
    x = [w[i] * w[i] for i in range(6)]
    for m in MINUS:
        x_val = [w[i] for i in MINUS if i != m]
        s = x_val[0] + x_val[1]
        v = x_val[0] * x_val[1]
        a = w[m]
        Gm = (4 * a ** 4 + 6 * a ** 3 * s + 2 * a ** 2 * (s ** 2 + v) + (a * s + v) * (s ** 2 - 2 * v))
        for p in PLUS:
            q = x[p] - x[m]
            if q <= 0:
                continue
            beta_idx = min((j for j in range(6) if j not in {m, p}), key=lambda j: x[j])
            total += q * (x[beta_idx]) * Gm
    return -32 * total


def fit_report(rows_train: List[Dict[str, object]], rows_hold: List[Dict[str, object]], terms: List[Tuple[int, int, int, int]], target_key: str, transform_key: str):
    y_train = [r[target_key] for r in rows_train]
    ok, coeff, rank_a, rank_aug, witness = fit_linear_system(rows_train, y_train, terms)
    payload = {
        "status": "exact_fit" if ok else "not_exact",
        "rank": rank_a,
        "rank_augmented": rank_aug,
        "feature_count": len(terms),
        "witness": witness,
        "coefficients": {},
        "train_nonzero_residual": None,
        "hold_nonzero_residual": None,
        "hold_witness": [],
        "factorized_polynomial": "",
    }

    if not ok:
        return payload, [r for r in rows_train], []

    term_names = [f"u^{i} v^{j} a3^{k} b3^{l}" for i, j, k, l in terms]

    train_residuals = []
    for r in rows_train:
        pred = sum(c * dual_value(r, t) for c, t in zip(coeff, terms))
        residual = r[target_key] - pred
        train_residuals.append(residual)
    payload["train_nonzero_residual"] = sum(1 for r in train_residuals if r != 0)

    hold_pred = []
    for r in rows_hold:
        pred = sum(c * dual_value(r, t) for c, t in zip(coeff, terms))
        residual = r[target_key] - pred
        hold_pred.append((r, pred, residual))
        if residual != 0:
            payload["hold_witness"].append(
                {
                    "point_id": r["source"],
                    "word": r["sorted_word"],
                    "target": frac_to_str(r[target_key]),
                    "pred": frac_to_str(pred),
                    "residual": frac_to_str(residual),
                }
            )
    payload["hold_nonzero_residual"] = sum(1 for _, _, residual in hold_pred if residual != 0)

    coeff_map = {}
    if all(len(str(c.numerator)) <= 80 and len(str(c.denominator)) <= 80 for c in coeff):
        for name, c in zip(term_names, coeff):
            if c != 0:
                coeff_map[name] = frac_to_str(c)
    payload["coefficients"] = coeff_map

    u, v, a3, b3 = sp.symbols("u v a3 b3")
    poly = sp.Integer(0)
    for c, (i, j, k, l) in zip(coeff, terms):
        csp = sp.Rational(c.numerator, c.denominator)
        poly = poly + csp * (u ** i) * (v ** j) * (a3 ** k) * (b3 ** l)
    payload["factorized_polynomial"] = str(sp.factor(poly))
    return payload, [r for r in rows_hold], hold_pred


def mandatory_checks() -> Dict[str, object]:
    a, p, x, y, z = sp.symbols("a p x y z", rational=True)
    q = p ** 2 - a ** 2
    s = x + y
    v = x * y
    Fm = a * s ** 3 + v * (s ** 2 - 2 * v)
    D = 2 * a ** 3 + 3 * a ** 2 * s + a * (s ** 2 + v) - s * v
    L = 3 * a ** 2 + 2 * a * (s + p) - v + p * (2 * x + y)
    Hminus = -32 * y ** 2 * (Fm + (a + p) * D) - 32 * q * y ** 2 * L + 32 * x * p * q ** 2

    Gm = 4 * a ** 4 + 6 * a ** 3 * s + 2 * a ** 2 * (s ** 2 + v) + (a * s + v) * (s ** 2 - 2 * v)
    check_minus = sp.expand(Hminus.subs(p, a) + 32 * y ** 2 * Gm)

    A0 = a ** 4 + 4 * a ** 3 * p + 4 * a ** 3 * z + 4 * a ** 2 * p ** 2 + 6 * a ** 2 * p * z + a * p ** 3 + 2 * a * p ** 2 * z
    A1 = 4 * a ** 3 + 8 * a ** 2 * p + 7 * a ** 2 * z + 5 * a * p ** 2 + 7 * a * p * z + p ** 3 + p ** 2 * z
    A2 = 3 * a ** 2 + 4 * a * p + 3 * a * z + p ** 2 + p * z
    B0 = 3 * a ** 2 + 2 * a * p + a * z
    B1 = 3 * a + p
    K = A0 + s * A1 + s ** 2 * A2 + v * B0 + s * v * B1
    Hplus = -32 * z ** 2 * (Fm + (a + p) * D) + 32 * q * K
    check_plus = sp.expand(Hplus.subs(p, a) + 32 * z ** 2 * Gm)

    u = sp.symbols("u", rational=True)
    w1 = Fraction(3, 8) * u - Fraction(73, 8)
    w2 = Fraction(5, 1)
    w3 = u
    w4 = Fraction(5, 1)
    w5 = 6 - u
    w6 = -Fraction(3, 8) * u - Fraction(55, 8)
    omega = (w1, w2, w3, w4, w5, w6)
    x = Fraction(3)  # dummy for type

    m = 1
    p = 3
    # beta=leg 3 in this slice
    other_minus = [i for i in MINUS if i != m]
    h_minus_u = h_minus_sym(omega[m], omega[p], omega[other_minus[0]], omega[2])
    # beta=leg 5 in this slice
    h_plus_6u = h_plus_sym(omega[m], omega[p], omega[0], omega[2], omega[4])
    P = -(u ** 2) / 16 * (219 * u ** 4 - 2628 * u ** 3 + 55226 * u ** 2 - 284052 * u - 2037485)

    check_slice_minus = sp.simplify(sp.expand(h_minus_u - P))
    check_slice_plus = sp.simplify(sp.expand(h_plus_6u - P.subs(u, 6 - u)))

    w_anchor = (
        Fraction(-23, 3),
        Fraction(5),
        Fraction(2),
        Fraction(5),
        Fraction(3),
        Fraction(-22, 3),
    )
    m_anchor = 1
    p_anchor = 3
    other_minus_anchor = [i for i in MINUS if i != m_anchor]
    h_anchor = h_minus_sym(w_anchor[m_anchor], w_anchor[p_anchor], w_anchor[other_minus_anchor[0]], w_anchor[2])
    check_anchor = h_anchor - Fraction(12622720, 27)

    return {
        "hminus_p_eq_a_residual": str(sp.factor(check_minus)),
        "hplus_p_eq_a_residual": str(sp.factor(check_plus)),
        "slice_beta_leg3_residual": str(sp.factor(check_slice_minus)),
        "slice_beta_leg5_residual": str(sp.factor(check_slice_plus)),
        "slice_trace_point_residual": str(sp.factor(check_anchor)),
        "trace_ok": check_minus == 0 and check_plus == 0 and check_slice_minus == 0 and check_slice_plus == 0 and check_anchor == 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Round4 sorted-word transport and nested-min candidate test")
    parser.add_argument("--qdir", type=Path, default=Path("."))
    parser.add_argument("--train", type=int, default=40)
    parser.add_argument("--hold", type=int, default=40)
    parser.add_argument("--rows", type=int, default=80)
    parser.add_argument("--output", type=Path, default=Path("bots/student-1/data/round4_sorted_transport.json"))
    parser.add_argument("--report", type=Path, default=Path("bots/student-1/derivations/round4_sorted_transport_raw_report.md"))
    args = parser.parse_args()

    qdir = args.qdir.resolve()
    output = args.output if args.output.is_absolute() else qdir / args.output
    report = args.report if args.report.is_absolute() else qdir / args.report

    src, target_src = copy_source(qdir)
    binary = qdir / "bots/student-1/bg_round4"
    compile_info = compile_bg(qdir, target_src, binary)

    rows, gen_stats = build_rows(qdir, target_total=args.rows)
    if len(rows) < 160:
        raise RuntimeError(f"insufficient valid exact samples: got {len(rows)}")

    # Keep deterministic sample IDs for reporting
    for i, r in enumerate(rows):
        r["point_id"] = f"r{str(i + 1).zfill(4)}"

    graph = build_graph()
    dist, paths = shortest_path_dag(graph, REFERENCE_WORD)

    # evaluate path increments for each sample and detect path dependence
    path_stats = {
        "target_word_samples": {},
        "path_count_stats": {},
        "inconsistent_path_count": 0,
        "sample_path_inconsistency_examples": [],
    }

    # compute target-dependent increments and canonical increment for each row's own word
    for row in rows:
        omega = row["omega"]
        word = row["sorted_word"]
        if word not in paths:
            raise RuntimeError(f"source row has unsupported word {word}")

        # all-target check requested by spec
        per_target = {}
        for tgt, pths in paths.items():
            if not pths:
                continue
            incs = all_paths_increment_variants(omega, pths)
            vals = [d["increment"] for d in incs]
            per_target[tgt] = {
                "path_count": len(vals),
                "increments": [frac_to_str(v) for v in vals],
                "canonical_path": list(pths[0]),
                "canonical_edges": incs[0]["edges"] if incs else [],
            }
            first = vals[0]
            if any(v != first for v in vals):
                path_stats["inconsistent_path_count"] += 1
                if len(path_stats["sample_path_inconsistency_examples"]) < 12:
                    path_stats["sample_path_inconsistency_examples"].append(
                        {
                            "point_id": row["point_id"],
                            "word": word,
                            "target": tgt,
                            "increments": [frac_to_str(v) for v in vals],
                        }
                    )
            per_target[tgt]["canonical_increment"] = frac_to_str(first)
        row["path_increment_by_target"] = per_target
        row["path_count_per_target"] = {k: v["path_count"] for k, v in per_target.items()}
        row["path_inconsistency_count"] = sum(1 for v in row["path_count_per_target"].values() if v > 1)
        row["R0_candidate1_canonical"] = row["R"] - Fraction(per_target[word]["increments"][0])

    # Candidate 2 values used by both direct fit/evidence and split copies.
    for row in rows:
        row["T"] = gm_candidate(row)
        row["R0_candidate2"] = row["R"] - row["T"]

    # required 40 train and 40 holdout
    train_rows, hold_rows, split_summary = sample_split_by_word(rows, args.train, args.hold)

    if len(train_rows) < args.train or len(hold_rows) < args.hold:
        raise RuntimeError("insufficient split coverage for train/hold")

    terms = dual_basis_terms()

    can1_train = fit_report(train_rows, hold_rows, terms, "R0_candidate1_canonical", "c1")
    c1_direct = build_candidate_fit_payload(
        rows_all=rows,
        train_rows=train_rows,
        terms=terms,
        target_key="R0_candidate1_canonical",
        need_path_context=True,
    )
    can1_payload = can1_train[0]
    can1_payload["direct_evidence"] = c1_direct

    can2_train = fit_report(train_rows, hold_rows, terms, "R0_candidate2", "c2")
    c2_direct = build_candidate_fit_payload(
        rows_all=rows,
        train_rows=train_rows,
        terms=terms,
        target_key="R0_candidate2",
    )
    can2_payload = can2_train[0]
    can2_payload["direct_evidence"] = c2_direct

    c1_payload = {
        "terms": ["%s_%s_%s_%s" % t for t in terms],
        "result": can1_payload,
    }
    c2_payload = {
        "terms": ["%s_%s_%s_%s" % t for t in terms],
        "result": can2_payload,
    }

    checks = mandatory_checks()

    payload = {
        "qdir": str(qdir),
        "compile": compile_info,
        "source": str(src),
        "binary": str(binary),
        "sampling": {
            "requested_rows": args.rows,
            "actual_rows": len(rows),
            "generated_stats": gen_stats,
            "realized_words_target": list(REALIZED_WORDS),
            "word_counts": dict(Counter(r["sorted_word"] for r in rows)),
            "coverage_targeted": {w: sum(1 for r in rows if r["sorted_word"] == w) for w in REALIZED_WORDS},
        },
        "train_hold_split": split_summary,
        "graph": {
            "reference": REFERENCE_WORD,
            "edges": {k: graph[k] for k in graph},
            "shortest_counts": {k: len(v) for k, v in paths.items()},
        },
        "path_transport": {
            "inconsistent_path_count": path_stats["inconsistent_path_count"],
            "sample_examples": path_stats["sample_path_inconsistency_examples"],
        },
        "candidate1": c1_payload,
        "candidate2": c2_payload,
        "mandatory_checks": checks,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Round-4 sorted transport + direct nested-min diagnostics",
        "",
        f"compiled: {compile_info.get('command')}",
        f"total samples: {len(rows)}",
        f"train/hold: {args.train}/{args.hold}",
        f"candidate1 path inconsistency hits: {path_stats['inconsistent_path_count']}",
        f"candidate1 rank: {payload['candidate1']['result']['rank']} / {len(terms)}",
        f"candidate2 rank: {payload['candidate2']['result']['rank']} / {len(terms)}",
        f"candidate1 direct residual nonzero (all independent rows): {payload['candidate1']['result']['direct_evidence']['nonzero_residual_count']}",
        f"candidate1 raw witness: {payload['candidate1']['result']['direct_evidence']['first_raw_witness']}",
        f"candidate2 direct residual nonzero (all independent rows): {payload['candidate2']['result']['direct_evidence']['nonzero_residual_count']}",
        f"candidate2 raw witness: {payload['candidate2']['result']['direct_evidence']['first_raw_witness']}",
        f"mandatory checks pass: {checks['trace_ok']}",
        f"JSON: {output}",
    ]
    report.write_text("\n".join(lines) + "\n")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
