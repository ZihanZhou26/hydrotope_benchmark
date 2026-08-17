#!/usr/bin/env python3

from collections import Counter
from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path
import argparse
import json
import random
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Sequence, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import pole_batch as pb  # noqa: E402

MINUS_PERMS = tuple(permutations(range(3)))
PLUS_PERMS = tuple(permutations(range(3)))


def _frac_to_str(v: Fraction) -> str:
    return pb.frac_to_str(v)


def gauss_solve_exact(A: List[List[Fraction]], b: List[Fraction], row_labels: Sequence[str] = None):
    m = len(A)
    if m == 0:
        return False, [], 0, 0, None
    n = len(A[0]) if A else 0
    if n == 0:
        all_zero = all(rhs == 0 for rhs in b)
        return (
            all_zero,
            [],
            0,
            0 if all_zero else 1,
            None if all_zero else {"type": "inconsistent", "sample_id": None, "residual": "n/a"},
        )

    mat = [row[:] + [rhs] for row, rhs in zip(A, b)]

    if row_labels is None:
        row_labels = [str(i) for i in range(m)]
    row_labels = list(row_labels)
    if len(row_labels) != m:
        raise ValueError("row_labels length must match number of rows")

    row = 0
    pivot_cols = []

    for col in range(n):
        pivot = None
        for r in range(row, m):
            if mat[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            continue

        mat[row], mat[pivot] = mat[pivot], mat[row]
        row_labels[row], row_labels[pivot] = row_labels[pivot], row_labels[row]
        pv = mat[row][col]
        for c in range(col, n + 1):
            mat[row][c] /= pv

        for r in range(m):
            if r == row:
                continue
            f = mat[r][col]
            if f == 0:
                continue
            for c in range(col, n + 1):
                mat[r][c] -= f * mat[row][c]

        pivot_cols.append(col)
        row += 1
        if row == m:
            break

    rank_a = len(pivot_cols)
    rank_aug = rank_a
    for r in range(m):
        if all(mat[r][c] == 0 for c in range(n)) and mat[r][n] != 0:
            return False, [], rank_a, rank_a + 1, {
                "type": "inconsistent_row",
                "sample_id": row_labels[r],
                "residual": _frac_to_str(mat[r][n]),
            }

    sol = [Fraction(0, 1)] * n
    for r, piv in enumerate(pivot_cols):
        sol[piv] = mat[r][n]

    return True, sol, rank_a, rank_aug, None


def independent_columns(rows: List[List[Fraction]]) -> List[int]:
    if not rows:
        return []
    m = len(rows)
    n = len(rows[0]) if rows else 0
    if n == 0:
        return []

    work = [row[:] for row in rows]
    pivots = []
    r0 = 0

    for c in range(n):
        pivot = None
        for r in range(r0, m):
            if work[r][c] != 0:
                pivot = r
                break

        if pivot is None:
            continue

        work[r0], work[pivot] = work[pivot], work[r0]
        pv = work[r0][c]
        for j in range(c, n):
            work[r0][j] /= pv

        for r in range(m):
            if r == r0:
                continue
            f = work[r][c]
            if f == 0:
                continue
            for j in range(c, n):
                work[r][j] -= f * work[r0][j]

        pivots.append(c)
        r0 += 1
        if r0 == m:
            break

    return pivots


def _student_bg_source(qdir: Path) -> Path:
    local_src = qdir / "bots/student-1/bg.cpp"
    if local_src.exists():
        return local_src
    fallback = qdir / "bg.cpp"
    if not fallback.exists():
        raise RuntimeError(f"missing bg.cpp at {local_src} or {fallback}")
    return fallback


def _student_bg_binary(qdir: Path) -> Path:
    return qdir / "bots/student-1/bg"


def compile_bg(qdir: Path) -> Dict[str, str]:
    src = _student_bg_source(qdir)
    binary = _student_bg_binary(qdir)
    if binary.exists():
        binary.unlink()

    cmd = ["g++", "-O2", "-std=c++17", "-o", str(binary), str(src), "-lgmpxx", "-lgmp"]
    cp = subprocess.run(
        cmd,
        cwd=str(qdir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    if cp.returncode != 0:
        raise RuntimeError(f"bg compile failed: {cp.stderr.strip()}")
    return {"command": " ".join(cmd), "returncode": cp.returncode, "stderr": cp.stderr.strip()}


def verify_anchor(oracle: pb.BGOracle) -> Dict[str, str]:
    omega = tuple(Fraction(x) for x in (-8, 2, 3, 4, 5, -6))
    channels, _, p_pole = pb.build_channels(omega)
    for ch in channels:
        if ch["Q"] > 0 and ch["d"] == 0:
            raise RuntimeError("anchor invalid: Q>0 with d=0")

    bg = oracle._run_amp(omega, sigma=pb.SIGMA)
    if bg["re"] != 0:
        raise RuntimeError("anchor has nonzero real part")

    expected_a = Fraction(-9190656, 7)
    expected_pole = Fraction(42588288, 7)
    expected_r = Fraction(-7396992, 1)
    if bg["im"] != expected_a or p_pole != expected_pole or bg["im"] - p_pole != expected_r:
        raise RuntimeError(
            "anchor mismatch: A6=%s P_pole=%s R=%s" % (
                _frac_to_str(bg["im"]),
                _frac_to_str(p_pole),
                _frac_to_str(bg["im"] - p_pole),
            )
        )

    return {
        "A6_im": _frac_to_str(bg["im"]),
        "P_pole": _frac_to_str(p_pole),
        "R": _frac_to_str(bg["im"] - p_pole),
        "omega": [_frac_to_str(v) for v in omega],
    }


def wall_product(omega: Sequence[Fraction]) -> Fraction:
    out = Fraction(1, 1)
    for i in range(len(omega)):
        wi = omega[i] * omega[i]
        for j in range(i + 1, len(omega)):
            out *= wi - omega[j] * omega[j]
    return out


def q_sign(v: Fraction) -> str:
    if v > 0:
        return "1"
    if v < 0:
        return "-1"
    return "0"


def dual_vars(omega: Sequence[Fraction]) -> Dict[str, Fraction]:
    minus = omega[:3]
    plus = omega[3:6]

    a = minus[0] + minus[1] + minus[2]
    b = minus[0] * minus[1] + minus[0] * minus[2] + minus[1] * minus[2]
    c = minus[0] * minus[1] * minus[2]
    d = plus[0] * plus[1] * plus[2]

    plus_sum = plus[0] + plus[1] + plus[2]
    plus_pair = plus[0] * plus[1] + plus[0] * plus[2] + plus[1] * plus[2]
    if plus_sum + a != 0:
        raise RuntimeError("dual invariants failed: sum_plus + a != 0")
    if plus_pair != b:
        raise RuntimeError("dual invariants failed: plus_pair != b")

    # keep dual map (a,b,c,d)->(-a,b,d,c)
    return {
        "a": a,
        "b": b,
        "c": c,
        "d": d,
    }


def dual_terms() -> List[Tuple[str, Tuple[int, int, int, int]]]:
    out = []
    for i in range(0, 9):
        for j in range(0, 5):
            rem = 8 - i - 2 * j
            if rem < 0:
                break
            if rem % 3 != 0:
                continue
            t = rem // 3
            for k in range(t + 1):
                l = t - k
                out.append((f"a^{i} b^{j} c^{k} d^{l}", (i, j, k, l)))
    return out


def dual_sym_value(exp: Tuple[int, int, int, int], a: Fraction, b: Fraction, c: Fraction, d: Fraction) -> Fraction:
    i, j, k, l = exp
    m1 = (a ** i) * (b ** j) * (c ** k) * (d ** l)
    m2 = ((-a) ** i) * (b ** j) * (d ** k) * (c ** l)
    return m1 + m2


def build_all_channels(omega: Sequence[Fraction]) -> List[Dict[str, Fraction]]:
    channels = []
    for m in pb.MINUS:
        rem_minus = [x for x in pb.MINUS if x != m]
        for p, q in combinations(pb.PLUS, 2):
            t = next(x for x in pb.PLUS if x not in (p, q))
            r, s = rem_minus
            Q = omega[p] * omega[p] + omega[q] * omega[q] - omega[m] * omega[m]
            B = -Fraction(64) * omega[m] * omega[t] * Q
            B *= pb.H(min(omega[m] * omega[m], Q), omega[p], omega[q])
            B *= pb.H(min(omega[t] * omega[t], Q), omega[r], omega[s])
            d = Fraction(2, 1) * (omega[m] + omega[p]) * (omega[m] + omega[q])
            S_term = Fraction(0, 1)
            S1_term = Fraction(0, 1)
            if d != 0:
                S_term = B / d
                S1_term = (Q * B) / d
            channels.append(
                {
                    "m": m + 1,
                    "p": p + 1,
                    "q": q + 1,
                    "r": r + 1,
                    "s": s + 1,
                    "t": t + 1,
                    "Q": Q,
                    "d": d,
                    "B": B,
                    "S_term": S_term,
                    "S1_term": S1_term,
                    "D": d / Q if Q != 0 else None,
                }
            )
    return channels


def nested_F_for_row(channels: Sequence[Dict[str, Fraction]]) -> List[Fraction]:
    out = [Fraction(0, 1) for _ in range(8)]
    for ch in channels:
        Q = ch["Q"]
        if Q <= 0:
            continue
        wm = ch["m_omega"]
        wt = ch["t_omega"]
        wp = ch["p_omega"]
        wq = ch["q_omega"]
        wr = ch["r_omega"]
        ws = ch["s_omega"]

        u = wp + wq
        v = wr + ws
        up = wp * wq
        vp = wr * ws

        Hm = pb.H(min(wm * wm, Q), wp, wq)
        Hr = pb.H(min(wt * wt, Q), wr, ws)
        weight = Q * Hm * Hr

        P = [
            wm * wt,
            wm * wm + wt * wt,
            wm * u + wt * v,
            wm * v + wt * u,
            u * v,
            u * u + v * v,
            up + vp,
            Q,
        ]

        for i in range(8):
            out[i] += weight * P[i]
    return out


def eval_row(oracle: pb.BGOracle, omega: Tuple[Fraction, ...], source: str, point_id: str, base_orbit_id: str) -> Dict:
    channels_all = build_all_channels(omega)
    for ch in channels_all:
        if ch["Q"] > 0 and ch["d"] == 0:
            return {}

    try:
        bg = oracle._run_amp(omega, sigma=pb.SIGMA)
    except Exception:
        return {}
    if bg["re"] != 0:
        return {}

    if bg["im"] is None:
        return {}

    if wall_product(omega) == 0:
        return {}

    chambers = pb.chamber_signature(omega)
    if chambers == "degenerate":
        return {}

    decorated = []
    for ch in channels_all:
        m = ch["m"] - 1
        p = ch["p"] - 1
        q = ch["q"] - 1
        r = ch["r"] - 1
        s = ch["s"] - 1
        t = ch["t"] - 1
        decorated.append(
            {
                "Q": ch["Q"],
                "m_omega": omega[m],
                "p_omega": omega[p],
                "q_omega": omega[q],
                "r_omega": omega[r],
                "s_omega": omega[s],
                "t_omega": omega[t],
            }
        )

    qpat = tuple(q_sign(ch["Q"]) for ch in decorated)
    if len(qpat) != 9:
        return {}

    _, _, p_pole = pb.build_channels(omega)

    nested = nested_F_for_row(decorated)

    v = dual_vars(omega)
    target = bg["im"] - p_pole

    return {
        "point_id": point_id,
        "source": source,
        "base_orbit_id": base_orbit_id,
        "source_kind": "exact" if str(source).startswith("exact:") else "integer",
        "omega": omega,
        "sorted_word": pb.sorted_sign_word(omega),
        "chamber_signature": chambers,
        "Q_sign_pattern": qpat,
        "channels_Q": tuple(_frac_to_str(ch["Q"]) for ch in decorated),
        "R_freq_denom_lcm": pb.denominator_lcm(omega),
        "A6_im": bg["im"],
        "P_pole": p_pole,
        "R": target,
        "nested_F": nested,
        "dual_vars": v,
        "bg_command": list(bg["command"]),
    }


def orbit_key(omega: Sequence[Fraction]) -> Tuple[Fraction, ...]:
    candidates = []
    for mp in MINUS_PERMS:
        for pp in PLUS_PERMS:
            idx = (
                pb.MINUS[mp[0]], pb.MINUS[mp[1]], pb.MINUS[mp[2]],
                pb.PLUS[pp[0]], pb.PLUS[pp[1]], pb.PLUS[pp[2]],
            )
            p = tuple(omega[i] for i in idx)
            candidates.append(p)
    return min(candidates)


def seed_records(qdir: Path) -> List[Dict]:
    exact = pb._load_exact_samples(qdir)
    integer = pb.build_integer_samples(500)
    generated = []
    rng = random.Random(6142026)
    for trial in range(4000):
        free = []
        for _ in range(4):
            den = rng.randint(1, 9)
            num = rng.randint(-45, 45)
            while num == 0:
                num = rng.randint(-45, 45)
            free.append(Fraction(num, den))
        w2, w3, w4, w5 = free
        sf = w2 + w3 + w4 + w5
        if sf == 0:
            continue
        num = sf * sf - (-w2 * w2 - w3 * w3 + w4 * w4 + w5 * w5)
        w6 = -num / (2 * sf)
        w1 = -(sf + w6)
        omega = (w1, w2, w3, w4, w5, w6)
        if any(v == 0 for v in omega):
            continue
        if not pb.on_shell(omega):
            continue
        if pb.chamber_signature(omega) == "degenerate":
            continue
        if wall_product(omega) == 0:
            continue
        generated.append(
            {
                "omega": omega,
                "source": "generated:%04d" % trial,
            }
        )
        if len(generated) >= 500:
            break

    out = []
    seen = set()

    for rec in list(exact) + list(integer) + generated:
        try:
            omega = tuple(Fraction(x) for x in rec["omega"])
        except Exception:
            continue
        if len(omega) != 6:
            continue
        if any(v == 0 for v in omega):
            continue
        if not pb.on_shell(omega):
            continue
        if pb.chamber_signature(omega) == "degenerate":
            continue

        oid = orbit_key(omega)
        if oid in seen:
            continue
        seen.add(oid)
        out.append(
            {
                "omega": omega,
                "source": rec["source"],
                "base_orbit_id": "%s" % ",".join(_frac_to_str(v) for v in oid),
            }
        )

    out.sort(key=lambda x: (x["source"], x["base_orbit_id"]))
    return out


def build_orbit_variants(base: Dict) -> List[Tuple[Tuple[Fraction, ...], str]]:
    omega = base["omega"]
    source = base["source"]
    oid = base["base_orbit_id"]
    out = []
    seen = set()

    for mp in MINUS_PERMS:
        for pp in PLUS_PERMS:
            idx = (
                pb.MINUS[mp[0]], pb.MINUS[mp[1]], pb.MINUS[mp[2]],
                pb.PLUS[pp[0]], pb.PLUS[pp[1]], pb.PLUS[pp[2]],
            )
            p = tuple(omega[i] for i in idx)
            if p in seen:
                continue
            seen.add(p)
            if any(v == 0 for v in p):
                continue
            if not pb.on_shell(p):
                continue
            if pb.chamber_signature(p) == "degenerate":
                continue
            if wall_product(p) == 0:
                continue
            out.append((p, source))
    return out


def collect_rows(oracle: pb.BGOracle, qdir: Path, sample_target: int) -> List[Dict]:
    bases = seed_records(qdir)
    if len(bases) < 80:
        raise RuntimeError(f"insufficient orbit-inequivalent base points: got {len(bases)}")

    base_pool = bases

    orbit_variants = [(base, build_orbit_variants(base)) for base in base_pool]
    orbit_variants = [(b, v) for b, v in orbit_variants if v]
    if not orbit_variants:
        return []

    max_rounds = max(len(v) for _, v in orbit_variants)

    seen = set()
    rows: List[Dict] = []
    round_idx = 0

    while len(rows) < sample_target:
        added_round = 0
        for base, variants in orbit_variants:
            if len(rows) >= sample_target:
                break
            if round_idx >= len(variants):
                continue
            omega, source = variants[round_idx]
            if omega in seen:
                continue
            row = eval_row(oracle, omega, source=source, point_id=f"p{len(rows) + 1:04d}", base_orbit_id=base["base_orbit_id"])
            if not row:
                continue
            seen.add(omega)
            rows.append(row)
            added_round += 1

        if added_round == 0:
            break
        round_idx += 1
        if round_idx >= max_rounds:
            break

    return rows


def r0_matrix(rows: List[Dict]) -> Tuple[List[str], List[List[Fraction]]]:
    terms = dual_terms()
    names = [n for n, _ in terms]
    raw = [[dual_sym_value(exp, **rows[i]["dual_vars"]) for _, exp in terms] for i in range(len(rows))]
    return names, raw


def drop_dependent(names: List[str], mat: List[List[Fraction]]) -> Tuple[List[str], List[List[Fraction]]]:
    if not mat:
        return [], []
    piv = independent_columns(mat)
    names = [names[i] for i in piv]
    out = [[row[i] for i in piv] for row in mat]
    return names, out


def combine_matrices(mat_a: List[List[Fraction]], names_a: List[str], mat_b: List[List[Fraction]], names_b: List[str]):
    if not mat_a:
        return names_b, mat_b
    if not mat_b:
        return names_a, mat_a
    names = list(names_a) + list(names_b)
    out = [row_a + row_b for row_a, row_b in zip(mat_a, mat_b)]
    return names, out


def nested_matrix(rows: List[Dict], feat: Sequence[str]) -> Tuple[List[str], List[List[Fraction]]]:
    if feat == ["F0"]:
        names = ["F0"]
        mat = [[r["nested_F"][0]] for r in rows]
        return names, mat
    if feat == ["F0", "F1", "F2", "F3", "F4", "F5", "F6", "F7"]:
        names = [f"F{i}" for i in range(8)]
        mat = [[r["nested_F"][i] for i in range(8)] for r in rows]
        return names, mat
    names = list(feat)
    idx = [int(x[1:]) for x in names]
    mat = [[r["nested_F"][k] for k in idx] for r in rows]
    return names, mat


def train_test_split(n: int, groups: Sequence[str], train_frac: float) -> Tuple[List[int], List[int]]:
    if n <= 1:
        return [0], []
    if train_frac >= 1.0:
        return list(range(n)), []

    by_group = {}
    for i, g in enumerate(groups):
        by_group.setdefault(g, []).append(i)

    orbit_ids = sorted(by_group.keys())
    n_orbits = len(orbit_ids)
    if n_orbits == 0:
        return list(range(n)), []

    train_orbit_target = max(1, int(n_orbits * train_frac))
    if train_orbit_target >= n_orbits:
        train_orbit_target = max(1, int(0.8 * n_orbits))
    train_orbit_set = set(orbit_ids[:train_orbit_target])

    train_idx: List[int] = []
    hold_idx: List[int] = []
    for i, g in enumerate(groups):
        if g in train_orbit_set:
            train_idx.append(i)
        else:
            hold_idx.append(i)

    if not hold_idx and train_idx:
        moved = train_idx.pop()
        hold_idx.append(moved)

    return train_idx, hold_idx


def residual_summary(values: List[Fraction], rows: List[Dict], idxs: List[int], scale: bool = False) -> Dict:
    raw = Counter()
    scaled = Counter()
    max_num = 0
    max_den = 0
    max_snum = 0
    max_sden = 0

    for pos, idx in enumerate(idxs):
        v = values[pos]
        if v.denominator != 0:
            raw[str(v.denominator)] += 1
            max_num = max(max_num, abs(v.numerator))
            max_den = max(max_den, int(v.denominator))
        if scale:
            factor = Fraction(rows[idx]["R_freq_denom_lcm"], 1) ** 8
            sv = v * factor
            scaled[str(sv.denominator)] += 1
            max_snum = max(max_snum, abs(sv.numerator))
            max_sden = max(max_sden, int(sv.denominator))

    return {
        "count": len(values),
        "nonzero_count": sum(1 for v in values if v != 0),
        "raw_denominator_summary": {k: v for k, v in sorted(raw.items(), key=lambda x: (int(x[0]), x[0]))},
        "scaled_denominator_summary": {k: v for k, v in sorted(scaled.items(), key=lambda x: (int(x[0]), x[0]))} if scale else {},
        "max_abs_numerator": int(max_num),
        "max_abs_denominator": int(max_den),
        "max_scaled_abs_numerator": int(max_snum),
        "max_scaled_abs_denominator": int(max_sden),
    }


def fit_model(name: str, rows: List[Dict], feature_matrix: List[List[Fraction]], feature_names: List[str], target: str, train_frac: float) -> Dict:
    n = len(rows)
    y = [r[target] for r in rows]
    if n == 0 or not feature_names:
        return {"name": name, "status": "no_data"}

    groups = [r["base_orbit_id"] for r in rows]
    train_idx, hold_idx = train_test_split(n, groups, train_frac)

    A_train = [feature_matrix[i] for i in train_idx]
    y_train = [y[i] for i in train_idx]
    labels = [rows[i]["point_id"] for i in train_idx]

    ok, sol, rank_a, rank_aug, wit = gauss_solve_exact(A_train, y_train, row_labels=labels)

    train_res = []
    for i in train_idx:
        pred = sum(feature_matrix[i][j] * sol[j] for j in range(len(sol)))
        train_res.append(y[i] - pred)

    status = "inconsistent" if not ok else "exact"
    if ok and rank_a < len(feature_names):
        status = "underdetermined"

    out = {
        "name": name,
        "status": status,
        "feature_count": len(feature_names),
        "feature_names": feature_names,
        "rank_A": rank_a,
        "rank_augmented": rank_aug,
        "train_size": len(train_idx),
        "hold_size": len(hold_idx),
        "train_nonzero_residual": int(sum(1 for v in train_res if v != 0)),
        "inconsistent_witness": wit if status == "inconsistent" else None,
    }

    if status in {"inconsistent"}:
        return out

    out["coefficients"] = {
        feature_names[j]: _frac_to_str(sol[j])
        for j in range(len(feature_names))
        if sol[j] != 0
    }

    hold = []
    hold_rows = []
    for i in hold_idx:
        pred = sum(feature_matrix[i][j] * sol[j] for j in range(len(sol)))
        hold_rows.append((rows[i]["point_id"], y[i], pred))
        hold.append(y[i] - pred)

    out["holdout_nonzero"] = int(sum(1 for v in hold if v != 0))
    out["holdout_summary"] = residual_summary(hold, rows, hold_idx, scale=True)
    out["holdout_rows"] = [
        {
            "point_id": pid,
            "target": _frac_to_str(t),
            "pred": _frac_to_str(p),
            "residual": _frac_to_str(t - p),
        }
        for pid, t, p in hold_rows[:16]
    ]
    return out


def run_models(rows: List[Dict], train_frac: float) -> Dict:
    # R0 basis (corrected dual invariant basis)
    r0_names, r0_mat = r0_matrix(rows)

    f_ab = ["F0"]
    f_all = ["F0", "F1", "F2", "F3", "F4", "F5", "F6", "F7"]

    nested_names_ab, nested_ab = nested_matrix(rows, f_ab)
    nested_names_all, nested_all = nested_matrix(rows, f_all)

    model_a_names, model_a = combine_matrices(r0_mat, r0_names, nested_ab, nested_names_ab)
    model_b_names, model_b = combine_matrices(r0_mat, r0_names, nested_all, nested_names_all)

    models = {
        "Model_A": fit_model("A", rows, model_a, model_a_names, "R", train_frac),
        "Model_A_noR0": fit_model("A_nor0", rows, nested_ab, nested_names_ab, "R", train_frac),
        "Model_B": fit_model("B", rows, model_b, model_b_names, "R", train_frac),
        "Model_B_noR0": fit_model("B_nor0", rows, nested_all, nested_names_all, "R", train_frac),
        "r0_only": fit_model("R0_only", rows, r0_mat, r0_names, "R", 1.0),
    }

    return {
        "feature_names": {
            "r0": r0_names,
            "nested": f_all,
        },
        "results": models,
    }


def ablation_groups(rows: List[Dict], group_key: str, r0_mat: List[List[Fraction]], r0_names: List[str], train_frac: float) -> Dict:
    groups: Dict[str, List[int]] = {}
    for i, r in enumerate(rows):
        key = r[group_key]
        groups[str(key)] = groups.get(str(key), [])
        groups[str(key)].append(i)

    out = {}
    for key, idxs in groups.items():
        if len(idxs) < max(2, len(r0_names)):
            out[key] = {"status": "skipped_small", "size": len(idxs)}
            continue

        sub_rows = [rows[i] for i in idxs]
        sub_mat = [r0_mat[i] for i in idxs]
        y = [rows[i]["R"] for i in idxs]

        n = len(sub_rows)
        train_idx, hold_idx = train_test_split(n, [sub_rows[i]["base_orbit_id"] for i in range(n)], train_frac)
        A_train = [sub_mat[i] for i in train_idx]
        y_train = [y[i] for i in train_idx]

        ok, _, rank_a, rank_aug, wit = gauss_solve_exact(
            A_train,
            y_train,
            row_labels=[sub_rows[i]["point_id"] for i in train_idx],
        )
        out[key] = {
            "size": len(idxs),
            "r0_features": len(r0_names),
            "rank_A": rank_a,
            "rank_augmented": rank_aug,
            "train_size": len(train_idx),
            "hold_size": len(hold_idx),
            "consistent": ok,
            "inconsistent_witness": wit if not ok else None,
        }

    return out


def wall_probe(oracle: pb.BGOracle, rows: List[Dict], do_probe: bool) -> Dict:
    if not do_probe:
        return {"status": "disabled"}

    triples = [
        (Fraction(1, 1), Fraction(2, 1), Fraction(3, 1)),
        (Fraction(1, 1), Fraction(2, 1), Fraction(4, 1)),
        (Fraction(2, 1), Fraction(3, 1), Fraction(4, 1)),
        (Fraction(3, 1), Fraction(-2, 1), Fraction(5, 1)),
        (Fraction(-1, 1), Fraction(3, 1), Fraction(4, 1)),
    ]
    lam_steps = [
        Fraction(k, d)
        for d in (1, 2, 3, 4)
        for k in range(-24, 25)
        if k != 0
    ]

    seen = set()
    candidates = []
    counter = 0

    for w2, w3, w5 in triples:
        for lam in lam_steps:
            sf = w2 + w3 + w5 + lam
            if sf == 0:
                continue
            num = sf * sf - (-w2 * w2 - w3 * w3 + lam * lam + w5 * w5)
            w6 = -num / (2 * sf)
            w1 = -(sf + w6)
            omega = (w1, w2, w3, lam, w5, w6)

            if any(v == 0 for v in omega):
                continue
            if not pb.on_shell(omega):
                continue
            if pb.chamber_signature(omega) == "degenerate":
                continue

            key = tuple(omega)
            if key in seen:
                continue
            seen.add(key)

            pid = f"wall_{counter:04d}"
            counter += 1
            row = eval_row(oracle, omega, source="wall_family", point_id=pid, base_orbit_id=f"wf:{w2},{w3},{w5}")
            if not row:
                continue
            q14 = omega[3] * omega[3] - omega[0] * omega[0]
            if q14 == 0:
                continue
            row["q14"] = q14
            row["family_lam"] = lam
            row["family_base"] = f"{w2}_{w3}_{w5}"
            candidates.append(row)

    if not candidates:
        return {"status": "not_feasible", "reason": "no wall-family points"}

    candidates.sort(key=lambda r: (str(r["family_base"]), abs(Fraction(r["q14"]))))
    left = [r for r in candidates if r["q14"] < 0]
    right = [r for r in candidates if r["q14"] > 0]

    if len(left) < 5 or len(right) < 5:
        return {
            "status": "not_feasible",
            "reason": "insufficient side counts",
            "left_count": len(left),
            "right_count": len(right),
            "rows": [serialize_probe_row(r) for r in candidates[:24]],
        }

    left.sort(key=lambda r: abs(Fraction(r["q14"])))
    right.sort(key=lambda r: abs(Fraction(r["q14"])))
    side_left = left[:5]
    side_right = right[:5]

    sig_counter = Counter((r["sorted_word"], r["chamber_signature"]) for r in candidates)
    target_sig = sig_counter.most_common(1)[0][0]

    def side_change(side_rows):
        sig_rows = [r for r in side_rows if (r["sorted_word"], r["chamber_signature"]) == target_sig]
        if len(sig_rows) < 2:
            return None
        prev = sig_rows[0]["Q_sign_pattern"]
        prev_id = sig_rows[0]["point_id"]
        for r in sig_rows[1:]:
            if r["Q_sign_pattern"] != prev:
                return {
                    "signature": {"side": str(target_sig)},
                    "from": {"point_id": prev_id, "pattern": list(prev)},
                    "to": {"point_id": r["point_id"], "pattern": list(r["Q_sign_pattern"])},
                }
            prev_id = r["point_id"]
            prev = r["Q_sign_pattern"]
        return None

    return {
        "status": "ok",
        "left_count": len(left),
        "right_count": len(right),
        "left_rows": [serialize_probe_row(r) for r in side_left],
        "right_rows": [serialize_probe_row(r) for r in side_right],
        "signature_pattern_change": {
            "left": side_change(left),
            "right": side_change(right),
            "selected_signature": target_sig,
        },
    }


def serialize_probe_row(r: Dict) -> Dict:
    return {
        "point_id": r["point_id"],
        "lam": _frac_to_str(r["family_lam"]),
        "q14": _frac_to_str(r["q14"]),
        "family_base": r["family_base"],
        "sorted_word": r["sorted_word"],
        "chamber_signature": r["chamber_signature"],
        "Q_sign_pattern": list(r["Q_sign_pattern"]),
        "R": _frac_to_str(r["R"]),
        "A6_im": _frac_to_str(r["A6_im"]),
        "nested_F": [_frac_to_str(v) for v in r["nested_F"]],
    }


def serialize_row(r: Dict) -> Dict:
    return {
        "point_id": r["point_id"],
        "source": r["source"],
        "base_orbit_id": r["base_orbit_id"],
        "source_kind": r["source_kind"],
        "omega": [_frac_to_str(v) for v in r["omega"]],
        "sorted_word": r["sorted_word"],
        "chamber_signature": r["chamber_signature"],
        "Q_sign_pattern": list(r["Q_sign_pattern"]),
        "channels_Q": list(r["channels_Q"]),
        "R_freq_denom_lcm": int(r["R_freq_denom_lcm"]),
        "A6_im": _frac_to_str(r["A6_im"]),
        "P_pole": _frac_to_str(r["P_pole"]),
        "R": _frac_to_str(r["R"]),
        "nested_F": [_frac_to_str(v) for v in r["nested_F"]],
        "dual_vars": {k: _frac_to_str(v) for k, v in r["dual_vars"].items()},
    }


def run_batch(qdir: Path, sample_target: int, train_frac: float, do_probe: bool) -> Dict:
    compile_info = compile_bg(qdir)
    oracle = pb.BGOracle(_student_bg_binary(qdir), sigma=pb.SIGMA, g=1)

    sanity = verify_anchor(oracle)

    desired_samples = min(240, max(180, sample_target))
    rows = collect_rows(oracle, qdir, desired_samples)
    if len(rows) < desired_samples:
        raise RuntimeError(f"only {len(rows)} rows collected for requested {desired_samples}")

    distinct_orbits = len(set(r["base_orbit_id"] for r in rows))
    if distinct_orbits < 80:
        raise RuntimeError(f"insufficient distinct orbits: {distinct_orbits}")

    qlen_ok = all(len(r["Q_sign_pattern"]) == 9 for r in rows)
    if not qlen_ok:
        bad = [r["point_id"] for r in rows if len(r["Q_sign_pattern"]) != 9]
        raise RuntimeError(f"Q_sign_pattern length mismatch in rows: {bad[:10]}")

    sorted_word_count = Counter(r["sorted_word"] for r in rows)
    if len(sorted_word_count) < 4:
        raise RuntimeError(f"insufficient sorted words: {list(sorted_word_count.keys())}")

    q_pattern_count = Counter(str(list(r["Q_sign_pattern"])) for r in rows)
    if len(q_pattern_count) < 2:
        raise RuntimeError(f"insufficient Q-pattern diversity: {q_pattern_count}")

    coverage = {
        "sorted_words": dict(sorted_word_count),
        "chamber_signatures": dict(Counter(r["chamber_signature"] for r in rows)),
        "q_sign_patterns": dict(q_pattern_count),
        "source_kinds": dict(Counter(r["source_kind"] for r in rows)),
        "distinct_orbit_count": distinct_orbits,
    }

    models = run_models(rows, train_frac)
    r0_names = models["feature_names"]["r0"]

    _, r0_mat = r0_matrix(rows)
    ablations = {
        "by_word": ablation_groups(rows, "sorted_word", r0_mat, r0_names, train_frac=1.0),
        "by_q_pattern": ablation_groups(rows, "Q_sign_pattern", r0_mat, r0_names, train_frac=1.0),
    }

    probe = wall_probe(oracle, rows, do_probe)

    validity_repairs = {
        "deterministic_sampling": True,
        "requested_samples": sample_target,
        "effective_samples": desired_samples,
        "actual_samples": len(rows),
        "distinct_orbit_count": distinct_orbits,
        "distinct_orbit_min_ok": distinct_orbits >= 80,
        "q_pattern_length_ok": qlen_ok,
        "sorted_word_count_ok": len(sorted_word_count) >= 4,
        "q_pattern_diversity_ok": len(q_pattern_count) >= 2,
        "anchor_checked": True,
        "wall_probe_status": probe.get("status"),
    }

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "qdir": str(qdir),
        "sample_target": sample_target,
        "actual_samples": len(rows),
        "compile": compile_info,
        "sanity": sanity,
        "coverage": coverage,
        "feature_names": models["feature_names"],
        "models": models["results"],
        "ablations": ablations,
        "wall_probe": probe,
        "validity_repairs": validity_repairs,
        "rows": [serialize_row(r) for r in rows],
    }
    return payload


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Round3 nested ansatz batch")
    ap.add_argument("--qdir", type=Path, default=Path("."))
    ap.add_argument("--samples", type=int, default=160)
    ap.add_argument("--train-frac", type=float, default=0.8)
    ap.add_argument("--output", type=Path, default=Path("bots/student-1/data/round3_nested_results.json"))
    ap.add_argument("--report", type=Path, default=Path("bots/student-1/derivations/round3_nested_raw_report.md"))
    ap.add_argument("--skip-wall-probe", action="store_true")
    return ap.parse_args()


def write_report(path: Path, payload: Dict):
    lines = [
        "# Round3 nested diagnostic batch",
        "",
        f"Generated: {payload['generated_at']}",
        f"Actual samples: {payload['actual_samples']}",
        f"Sanity A6: {payload['sanity']['A6_im']}",
        f"Sanity P_pole: {payload['sanity']['P_pole']}",
        f"Sanity residual: {payload['sanity']['R']}",
        f"Distinct orbits: {payload['coverage']['distinct_orbit_count']}",
        f"Validity repairs: {payload['validity_repairs']}",
        "",
        "## Coverage",
        f"sorted_word={payload['coverage']['sorted_words']}",
        f"chamber_signatures={payload['coverage']['chamber_signatures']}",
        f"q-pattern counts={payload['coverage']['q_sign_patterns']}",
        "",
        "## Compile / Fit status",
    ]

    for k, v in payload["models"].items():
        lines.append(
            f"{k}: status={v.get('status')} features={v.get('feature_count')} "
            f"rank={v.get('rank_A')}/{v.get('rank_augmented')} train_nonzero={v.get('train_nonzero_residual')}"
        )
        if v.get('status') == 'inconsistent' and v.get('inconsistent_witness') is not None:
            lines.append(f"  witness={v.get('inconsistent_witness')}")

    lines.append("")
    lines.append(f"wall_probe={payload['wall_probe'].get('status')}")
    lines.append(f"wall_details={payload['wall_probe']}")
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main():
    args = parse_args()
    qdir = args.qdir.resolve()
    t0 = datetime.utcnow()

    output = args.output
    if not output.is_absolute():
        output = qdir / output
    report = args.report
    if not report.is_absolute():
        report = qdir / report

    payload = run_batch(qdir, args.samples, args.train_frac, do_probe=not args.skip_wall_probe)

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w") as f:
        json.dump(payload, f, indent=2)

    write_report(report, payload)

    t1 = datetime.utcnow()
    dt = (t1 - t0).total_seconds()
    print(f"round3_nested.py finished in {dt:.1f}s; wrote {output} and {report}")


if __name__ == "__main__":
    main()
