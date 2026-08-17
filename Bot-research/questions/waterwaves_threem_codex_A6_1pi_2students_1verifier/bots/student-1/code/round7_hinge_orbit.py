#!/usr/bin/env python3

from __future__ import print_function

from collections import defaultdict
from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
from datetime import datetime

import pole_batch as pb

SIGMA = pb.SIGMA
MINUS = pb.MINUS
PLUS = pb.PLUS

MINUS_PERMS = tuple(permutations(range(3)))
PLUS_PERMS = tuple(permutations(range(3)))
PERM_PAIRS = [(mp, pp) for mp in MINUS_PERMS for pp in PLUS_PERMS]

PRIMES = (1000000007, 1000000009)


def sha256_text(text):
    h = hashlib.sha256()
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def fraction_to_str(v):
    q = Fraction(v)
    if q.denominator == 1:
        return str(q.numerator)
    return "%d/%d" % (q.numerator, q.denominator)


def parse_fraction(v):
    if isinstance(v, Fraction):
        return v
    if isinstance(v, int):
        return Fraction(v, 1)
    if isinstance(v, str):
        s = v.strip()
        if not s:
            raise ValueError("empty rational token")
        if s[0] == "+":
            s = s[1:]
        if "/" in s:
            n, d = s.split("/", 1)
            return Fraction(int(n), int(d))
        return Fraction(int(s), 1)
    if isinstance(v, float):
        return Fraction(str(v))
    raise TypeError("unsupported rational token type: %r" % (type(v),))


def parse_rows(payload):
    rows = []
    for i, rec in enumerate(payload.get("rows", []), 1):
        omega = tuple(parse_fraction(x) for x in rec["omega"])
        rows.append(
            {
                "point_id": rec.get("point_id", "r%04d" % i),
                "source": rec.get("source", "unknown"),
                "omega": omega,
                "sorted_word": rec.get("sorted_word", pb.sorted_sign_word(omega)),
                "chamber_signature": rec.get("chamber_signature", pb.chamber_signature(omega)),
                "target": parse_fraction(rec["S"]),
            }
        )
    return rows


def compute_RQ(omega):
    x = [w * w for w in omega]
    total = Fraction(0, 1)
    for m in MINUS:
        wm = omega[m]
        for p, q in combinations(PLUS, 2):
            t = next(i for i in PLUS if i not in (p, q))
            Q_mpq = x[p] + x[q] - x[m]
            total += max(Q_mpq, Fraction(0, 1)) ** 3 * wm * omega[t]
    return -32 * total


def precompute_cache(rows, max_alpha=8, max_hinge=4):
    cache = []
    for rec in rows:
        omega = rec["omega"]
        omega_pows = []
        for i in range(6):
            powers = [Fraction(1, 1)]
            current = Fraction(1, 1)
            for _ in range(max_alpha):
                current *= omega[i]
                powers.append(current)
            omega_pows.append(powers)

        x = [w * w for w in omega]
        hinge_pows = []
        for m in MINUS:
            for p in PLUS:
                q = x[p] - x[m]
                if q < 0:
                    q = Fraction(0, 1)
                powers = [Fraction(1, 1)]
                current = Fraction(1, 1)
                for _ in range(max_hinge):
                    current *= q
                    powers.append(current)
                hinge_pows.append(powers)
        cache.append({"omega_pows": omega_pows, "hinge_pows": hinge_pows})
    return cache


def transform_seed(r_seed, a_seed, minus_perm, plus_perm):
    idx = list(minus_perm) + [3 + i for i in plus_perm]
    a = [Fraction(0, 1)] * 6
    for j, oi in enumerate(idx):
        a[oi] = a_seed[j]

    r = [Fraction(0, 1)] * 9
    for mi, m in enumerate(minus_perm):
        for pj, p in enumerate(plus_perm):
            old_m = idx[mi]
            old_p = idx[3 + pj]
            r[old_m * 3 + (old_p - 3)] = r_seed[mi * 3 + pj]
    return tuple(r), tuple(a)


def canonical_orbit(r_seed, a_seed):
    transforms = []
    for mp, pp in PERM_PAIRS:
        transforms.append(transform_seed(r_seed, a_seed, mp, pp))
    orbit = sorted(set(transforms))
    return tuple(orbit), orbit[0]


def compositions(total, parts):
    if parts == 1:
        return [(total,)]
    out = []
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            out.append((first,) + rest)
    return out


def eval_transform(cache_row, r_seed, a_seed):
    val = Fraction(1, 1)
    if any(e < 0 for e in a_seed):
        return Fraction(0, 1)
    if any(e < 0 for e in r_seed):
        return Fraction(0, 1)

    omega_pows = cache_row["omega_pows"]
    hinge_pows = cache_row["hinge_pows"]

    for i, e in enumerate(a_seed):
        if e:
            val *= omega_pows[i][e]
    for j, e in enumerate(r_seed):
        if e:
            val *= hinge_pows[j][e]
    return val


def eval_feature(cache_row, transforms):
    return sum(eval_transform(cache_row, r_seed, a_seed) for r_seed, a_seed in transforms)


def modular_value(v, p):
    v = Fraction(v)
    return (v.numerator % p) * pow(v.denominator % p, p - 2, p) % p


def matrix_mod_rank(values_by_col, rhs_by_row, col_idx, row_idx, p, augment=False):
    ncol = len(col_idx)
    mat = []

    for ri in row_idx:
        row = [modular_value(values_by_col[c][ri], p) for c in col_idx]
        if augment:
            row.append(modular_value(rhs_by_row[ri], p))
        mat.append(row)

    rank = 0
    for c in range(ncol):
        pivot = None
        for r in range(rank, len(mat)):
            if mat[r][c] != 0:
                pivot = r
                break
        if pivot is None:
            continue

        mat[rank], mat[pivot] = mat[pivot], mat[rank]
        inv = pow(mat[rank][c], p - 2, p)
        for j in range(c, len(mat[0])):
            mat[rank][j] = (mat[rank][j] * inv) % p

        for r in range(len(mat)):
            if r == rank:
                continue
            factor = mat[r][c]
            if factor == 0:
                continue
            for j in range(c, len(mat[0])):
                mat[r][j] = (mat[r][j] - factor * mat[rank][j]) % p

        rank += 1
        if rank == ncol:
            break

    if not augment:
        return rank, rank

    rank_aug = rank
    n = ncol
    for r in range(rank, len(mat)):
        if all(mat[r][c] == 0 for c in range(n)) and mat[r][n] != 0:
            rank_aug += 1
    return rank, rank_aug


def gauss_solve_exact(values_by_col, rhs_values, row_idx, col_idx, row_labels):
    ncols = len(col_idx)
    if not col_idx:
        all_zero = all(rhs_values[ri] == 0 for ri in row_idx)
        if all_zero:
            return True, [Fraction(0, 1)] * len(col_idx), 0, 0, None
        first = row_labels[row_idx[0]] if row_labels else None
        return False, [Fraction(0, 1)] * len(col_idx), 0, 1, {
            "type": "inconsistent",
            "sample_id": first,
            "residual": "n/a",
        }

    mat = []
    labels = []
    for ri in row_idx:
        labels.append(row_labels[ri])
        row = [values_by_col[c][ri] for c in col_idx]
        row.append(rhs_values[ri])
        mat.append(row)

    m = len(mat)
    n = ncols
    pivot_rows = []
    pivot_cols = []
    row = 0

    for col in range(n):
        pivot = None
        for r in range(row, m):
            if mat[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            continue

        mat[row], mat[pivot] = mat[pivot], mat[row]
        labels[row], labels[pivot] = labels[pivot], labels[row]
        pv = mat[row][col]
        for c in range(col, n + 1):
            mat[row][c] /= pv

        for r in range(m):
            if r == row:
                continue
            factor = mat[r][col]
            if factor == 0:
                continue
            for c in range(col, n + 1):
                mat[r][c] -= factor * mat[row][c]

        pivot_rows.append(row)
        pivot_cols.append(col)
        row += 1
        if row == m:
            break

    rank_a = len(pivot_cols)
    rank_aug = rank_a
    for r in range(m):
        if all(mat[r][c] == 0 for c in range(n)) and mat[r][n] != 0:
            return False, [Fraction(0, 1)] * ncols, rank_a, rank_aug + 1, {
                "type": "inconsistent_row",
                "sample_id": labels[r],
                "residual": fraction_to_str(mat[r][n]),
            }

    if rank_a < ncols:
        sample_id = labels[pivot_rows[-1]] if pivot_rows else (labels[0] if labels else None)
        # underdetermined but consistent: choose free variables to be zero
        coeff = [Fraction(0, 1)] * ncols
        for r, c in enumerate(pivot_cols):
            coeff[c] = mat[r][n]
        return True, coeff, rank_a, rank_aug, {
            "type": "rank_deficient",
            "sample_id": sample_id,
            "pivot_rank": rank_a,
            "target_rank": ncols,
        }

    coeff = [Fraction(0, 1)] * ncols
    for r, c in enumerate(pivot_cols):
        coeff[c] = mat[r][n]

    return True, coeff, rank_a, rank_aug, None


def predict_all(coeffs, values_by_col):
    rows = len(values_by_col[0]) if values_by_col else 0
    pred = [Fraction(0, 1)] * rows
    for ci, c in enumerate(coeffs):
        if c == 0:
            continue
        fv = values_by_col[ci]
        for r, v in enumerate(fv):
            pred[r] += c * v
    return pred


def train_indices(rows, target):
    by_word = defaultdict(list)
    for i, rec in enumerate(rows):
        by_word[rec["sorted_word"]].append(i)

    words = sorted(by_word.keys())
    if not words:
        raise RuntimeError("no words to construct training split")

    chosen = []
    seen = set()
    for w in words:
        idx = by_word[w][0]
        chosen.append(idx)
        seen.add(idx)

    ptr = 1
    while len(chosen) < target:
        added = False
        for w in words:
            bucket = by_word[w]
            if ptr < len(bucket):
                rid = bucket[ptr]
                if rid not in seen:
                    chosen.append(rid)
                    seen.add(rid)
                    added = True
                    if len(chosen) >= target:
                        break
        if not added:
            break
        ptr += 1

    if len(chosen) < target:
        for i in range(len(rows)):
            if i not in seen:
                chosen.append(i)
                seen.add(i)
                if len(chosen) >= target:
                    break

    return sorted(chosen), words


def build_holdout_candidates(qdir, excluded_omegas, required_words):
    exact = pb._load_exact_samples(qdir)
    integer = pb.build_integer_samples(2000)
    seen = set(excluded_omegas)
    out = []
    for rec in exact + integer:
        omega = tuple(rec["omega"])
        if omega in seen:
            continue
        if omega in out:
            continue
        if required_words and rec["sorted_word"] not in required_words:
            continue
        out.append(omega)
        seen.add(omega)
        if len(out) >= 300:
            break
    return out


def evaluate_holdouts(oracle, qdir, candidate_coeffs, feature_terms, required_words, excluded_omegas):
    candidates = build_holdout_candidates(qdir, excluded_omegas, required_words)
    holdouts = []

    for omega in candidates:
        if len(holdouts) >= 40:
            break
        if any(v == 0 for v in omega):
            continue
        if pb.chamber_signature(omega) == "degenerate":
            continue
        try:
            channels, _, pole = pb.build_channels(omega)
        except Exception:
            continue
        if any(c["d"] == 0 for c in channels):
            continue
        if any(c["Q"] == 0 for c in channels):
            continue

        try:
            bg = oracle._run_amp(omega, sigma=SIGMA, g=1)
        except Exception:
            continue
        if bg["re"] != 0:
            continue

        target = parse_fraction(bg["im"]) - parse_fraction(pole) - compute_RQ(omega)
        hcache = precompute_cache([{"omega": omega}])
        fv = [eval_feature(hcache[0], terms) for terms in feature_terms]
        pred = sum(c * f for c, f in zip(candidate_coeffs, fv))

        holdouts.append(
            {
                "omega": [fraction_to_str(x) for x in omega],
                "word": pb.sorted_sign_word(omega),
                "target": fraction_to_str(target),
                "prediction": fraction_to_str(pred),
                "residual": fraction_to_str(target - pred),
            }
        )

    return holdouts

def compile_bg_round7(qdir):
    src = qdir / "bg.cpp"
    if not src.exists():
        raise RuntimeError("shared bg.cpp missing: %s" % src)

    dst = qdir / "bots/student-1/bg_round7.cpp"
    binary = qdir / "bots/student-1/bg_round7"
    dst.write_text(src.read_text())

    cmd = ["g++", "-O2", "-std=c++17", "-o", str(binary), str(dst), "-lgmpxx", "-lgmp"]
    cp = subprocess.run(
        cmd,
        cwd=str(qdir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    if cp.returncode != 0:
        raise RuntimeError("bg compile failed: %s" % cp.stderr.strip())

    return {
        "source": str(src),
        "copied": str(dst),
        "binary": str(binary),
        "command": " ".join(cmd),
        "returncode": cp.returncode,
        "stdout": cp.stdout.strip(),
        "stderr": cp.stderr.strip(),
        "source_sha256": sha256_text(src.read_text()),
        "copied_sha256": sha256_text(dst.read_text()),
    }


def write_checkpoint(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def write_report(path, payload):
    lines = []
    lines.append("# Round7 hinge-orbit diagnostics")
    lines.append("")
    lines.append("generated_at: %s" % payload.get("generated_at"))
    lines.append("input_rows: %d" % payload.get("input_rows", 0))
    lines.append("train_rows: %d" % payload.get("train_rows", 0))
    lines.append("seeded_features: %d" % payload.get("feature_generation", {}).get("seed_count", 0))
    lines.append("kept_features: %d" % payload.get("feature_generation", {}).get("kept_count", 0))
    lines.append("zero_removed: %d" % payload.get("feature_generation", {}).get("zero_removed", 0))
    lines.append("duplicate_removed: %d" % payload.get("feature_generation", {}).get("duplicate_removed", 0))
    lines.append("anchor_status: %s" % payload.get("anchor", {}).get("status", "unknown"))
    lines.append("candidate_status: %s" % payload.get("candidate", {}).get("status", "none"))
    lines.append("candidate_nonzero_terms: %s" % payload.get("candidate", {}).get("nonzero_terms", "n/a"))

    fg = payload.get("feature_generation", {}).get("kept_by_depth", {})
    for d in sorted(fg):
        lines.append("depth_%s_features: %s" % (d, fg[d]))

    for depth in sorted(payload.get("rank_reports", {}).keys()):
        item = payload["rank_reports"][depth]
        lines.append("depth_%s_rank:" % depth)
        for prime, values in sorted(item.items(), key=lambda x: int(x[0])):
            lines.append("  p=%s rank=%s/%s" % (prime, values["rank_A"], values["rank_aug"]))

    cand = payload.get("candidate", {})
    if cand.get("witness"):
        lines.append("candidate_witness: %s" % json.dumps(cand["witness"]))
    if cand.get("holdout"):
        lines.append("holdout_collected: %s" % cand["holdout"].get("count", 0))
        lines.append("holdout_nonzero: %s" % cand["holdout"].get("residual_nonzero", 0))

    lines.append("")
    lines.append("input_path: %s" % payload.get("input_path", ""))
    lines.append("coefficients_path: %s" % payload.get("candidate", {}).get("coefficients_path", ""))
    lines.append("script: %s" % payload.get("script_path", ""))
    lines.append("compile: %s" % payload.get("compile", {}).get("command", ""))
    lines.append("script_sha256: %s" % payload.get("script_sha256", ""))
    lines.append("bg_sha256: %s" % payload.get("compile", {}).get("source_sha256", ""))

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Round7 hinge-orbit harness")
    ap.add_argument("--qdir", type=Path, default=Path("."))
    ap.add_argument("--input", type=str, default="bots/student-1/data/round6_assembly_selfcheck.json")
    ap.add_argument("--output", type=str, default="bots/student-1/data/round7_hinge_orbit.json")
    ap.add_argument("--report", type=str, default="bots/student-1/derivations/round7_hinge_orbit_raw_report.md")
    ap.add_argument("--train", type=int, default=160)
    ap.add_argument("--holdouts", type=int, default=30)
    args = ap.parse_args()

    qdir = args.qdir.resolve()
    script_path = Path(__file__).resolve()
    payload_path = (qdir / args.output).resolve()
    report_path = (qdir / args.report).resolve()
    coeff_path = (qdir / "bots/student-1/data/round7_hinge_orbit_coefficients.json").resolve()

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "script_path": str(script_path),
        "script_sha256": sha256_text(script_path.read_text()),
        "input_path": str((qdir / args.input).resolve()),
        "checkpoints": [{"stage": "start", "time": datetime.utcnow().isoformat() + "Z"}],
    }

    payload["compile"] = compile_bg_round7(qdir)
    write_checkpoint(payload_path, payload)

    compile_info = payload["compile"]
    oracle = pb.BGOracle(compile_info["binary"], sigma=SIGMA, g=1)

    anchor = (Fraction(-8, 1), Fraction(2, 1), Fraction(3, 1), Fraction(4, 1), Fraction(5, 1), Fraction(-6, 1))
    channels, _, anchor_pole = pb.build_channels(anchor)
    if any(c["d"] == 0 for c in channels):
        raise RuntimeError("anchor has d == 0")
    anchor_bg = oracle._run_amp(anchor, sigma=SIGMA, g=1)
    if anchor_bg["re"] != 0:
        raise RuntimeError("anchor real part is non-zero")

    anchor_payload = {
        "omega": [fraction_to_str(x) for x in anchor],
        "A6_im": fraction_to_str(parse_fraction(anchor_bg["im"])),
        "P_pole": fraction_to_str(anchor_pole),
        "RQ": fraction_to_str(compute_RQ(anchor)),
        "S": fraction_to_str(parse_fraction(anchor_bg["im"]) - anchor_pole - compute_RQ(anchor)),
        "status": "ok",
    }

    if anchor_bg["im"] != Fraction(-9190656, 7) or anchor_pole != Fraction(42588288, 7):
        anchor_payload["status"] = "failed_regression"
        payload["anchor"] = anchor_payload
        raise RuntimeError("anchor regression mismatch")

    payload["anchor"] = anchor_payload
    payload["checkpoints"].append({"stage": "anchor", "time": datetime.utcnow().isoformat() + "Z"})
    write_checkpoint(payload_path, payload)

    source = json.loads((qdir / args.input).read_text())
    rows = parse_rows(source)
    payload["input_rows"] = len(rows)
    row_words = sorted(set(r["sorted_word"] for r in rows))
    payload["input_words"] = row_words

    cache = precompute_cache(rows)
    payload["checkpoints"].append({"stage": "cache", "time": datetime.utcnow().isoformat() + "Z"})

    # feature generation: seed under S3(M) x S3(P), depths 1..4
    seed_count = 0
    by_seed = {}
    seed_by_depth = {1: 0, 2: 0, 3: 0, 4: 0}

    for depth in (1, 2, 3, 4):
        for r_seed in compositions(depth, 9):
            a_sum = 8 - 2 * depth
            for a_seed in compositions(a_sum, 6):
                transforms, canonical = canonical_orbit(r_seed, a_seed)
                seed_count += 1
                seed_by_depth[depth] += 1
                if canonical in by_seed:
                    continue
                by_seed[canonical] = {
                    "depth": depth,
                    "seed_r": tuple(canonical[0]),
                    "seed_a": tuple(canonical[1]),
                    "transforms": transforms,
                }

    features = []
    zero_removed = 0
    duplicate_removed = 0
    signatures = {}

    for idx, (canon, item) in enumerate(sorted(by_seed.items(), key=lambda kv: kv[0])):
        terms = item["transforms"]
        vals = [eval_feature(cache_row, terms) for cache_row in cache]
        if all(v == 0 for v in vals):
            zero_removed += 1
            continue

        sig = tuple((v.numerator, v.denominator) for v in vals)
        if sig in signatures:
            duplicate_removed += 1
            continue

        features.append(
            {
                "id": idx,
                "depth": item["depth"],
                "seed_r": [int(x) for x in item["seed_r"]],
                "seed_a": [int(x) for x in item["seed_a"]],
                "transforms": [(list(r), list(a)) for r, a in terms],
                "values": vals,
                "complexity": sum(item["seed_r"]) + sum(item["seed_a"]),
            }
        )
        signatures[sig] = True

    feature_generation = {
        "seed_count": seed_count,
        "seed_by_depth": {str(k): v for k, v in seed_by_depth.items()},
        "kept_count": len(features),
        "zero_removed": zero_removed,
        "duplicate_removed": duplicate_removed,
        "kept_by_depth": defaultdict(int),
    }
    for f in features:
        feature_generation["kept_by_depth"][str(f["depth"])] += 1
    payload["feature_generation"] = {
        "seed_count": feature_generation["seed_count"],
        "seed_by_depth": feature_generation["seed_by_depth"],
        "kept_count": feature_generation["kept_count"],
        "zero_removed": feature_generation["zero_removed"],
        "duplicate_removed": feature_generation["duplicate_removed"],
        "kept_by_depth": {k: v for k, v in feature_generation["kept_by_depth"].items()},
    }

    payload["checkpoints"].append({"stage": "features", "time": datetime.utcnow().isoformat() + "Z"})
    write_checkpoint(payload_path, payload)

    features.sort(key=lambda x: (x["depth"], x["complexity"], x["id"]))
    feature_values = [f["values"] for f in features]
    targets = [r["target"] for r in rows]
    row_ids = [r["point_id"] for r in rows]

    train_rows, _ = train_indices(rows, target=min(args.train, len(rows)))
    payload["train_rows"] = len(train_rows)
    payload["train_words"] = sorted(set(rows[i]["sorted_word"] for i in train_rows))

    # modular rank diagnostics
    rank_reports = {}
    first_obstruction = None
    for depth in (1, 2, 3, 4):
        cols = [i for i, f in enumerate(features) if f["depth"] <= depth]
        depth_report = {}
        for p in PRIMES:
            ra, ra_aug = matrix_mod_rank(feature_values, targets, cols, train_rows, p, augment=True)
            depth_report[str(p)] = {"rank_A": ra, "rank_aug": ra_aug}
            if first_obstruction is None and ra != ra_aug:
                first_obstruction = {"depth": depth, "prime": p, "rank_A": ra, "rank_aug": ra_aug}
        rank_reports[str(depth)] = depth_report
    payload["rank_reports"] = rank_reports
    payload["first_modular_obstruction"] = first_obstruction

    full_cols = [i for i, f in enumerate(features) if f["depth"] <= 4]
    candidate = {
        "status": "unknown",
        "first_modular_obstruction": first_obstruction,
        "columns_total": len(full_cols),
    }

    if not full_cols:
        candidate["status"] = "no_features"
        payload["candidate"] = candidate
        payload["checkpoints"].append({"stage": "no_features", "time": datetime.utcnow().isoformat() + "Z"})
        write_checkpoint(payload_path, payload)
        write_report(report_path, payload)
        print(str(payload_path))
        return

    # exact recovery on training rows (underdetermined allowed)
    ok, coeffs, rank_a, rank_aug, witness = gauss_solve_exact(
        feature_values,
        targets,
        train_rows,
        full_cols,
        row_ids,
    )
    candidate["rank_train"] = rank_a
    candidate["rank_train_aug"] = rank_aug

    if not ok:
        candidate["status"] = "inconsistent"
        candidate["witness"] = witness
        payload["candidate"] = candidate
        payload["checkpoints"].append({"stage": "inconsistent", "time": datetime.utcnow().isoformat() + "Z"})
        write_checkpoint(payload_path, payload)
        write_report(report_path, payload)
        print(str(payload_path))
        return

    # lift to full coefficient vector (columns are sorted feature ids)
    full_coeff = [Fraction(0, 1)] * len(features)
    for i, c in enumerate(coeffs):
        full_coeff[full_cols[i]] = c

    payload["candidate_fit_indices"] = full_cols
    payload["candidate_coeff_count"] = len(full_cols)

    pred_all = predict_all(full_coeff, feature_values)
    residuals = [t - p for t, p in zip(targets, pred_all)]
    stored_nonzero = sum(1 for v in residuals if v != 0)
    first_witness = None
    if stored_nonzero:
        for idx, res in enumerate(residuals):
            if res != 0:
                first_witness = {
                    "point_id": row_ids[idx],
                    "word": rows[idx]["sorted_word"],
                    "source": rows[idx]["source"],
                    "target": fraction_to_str(targets[idx]),
                    "prediction": fraction_to_str(pred_all[idx]),
                    "residual": fraction_to_str(res),
                }
                break

    nonzero_idx = [i for i, c in enumerate(full_coeff) if c != 0]
    candidate_payload = [
        {
            "feature_id": i,
            "depth": features[i]["depth"],
            "seed_r": features[i]["seed_r"],
            "seed_a": features[i]["seed_a"],
            "coefficient": fraction_to_str(full_coeff[i]),
            "transforms": features[i]["transforms"],
        }
        for i in nonzero_idx
    ]

    coeff_by_id = {str(item["feature_id"]): item for item in candidate_payload}
    coeff_path.write_text(json.dumps(coeff_by_id, indent=2) + "\n")

    candidate.update(
        {
            "status": "exact_fit" if stored_nonzero == 0 else "fit_with_residual",
            "stored_rows_residual_nonzero": stored_nonzero,
            "stored_rows_witness": first_witness,
            "nonzero_terms": len(nonzero_idx),
            "coefficients_path": str(coeff_path),
            "coefficients": candidate_payload,
            "rank_aug": rank_aug,
            "rank": rank_a,
            "first_modular_obstruction": first_obstruction,
        }
    )

    # optional fresh-oracle holdouts when compact and fit is already exact on stored rows
    if candidate["status"] == "exact_fit" and candidate["nonzero_terms"] <= 60:
        req_words = payload["train_words"] if payload["train_words"] else row_words
        excluded = {rows[i]["omega"] for i in range(len(rows))}
        holdout_rows = evaluate_holdouts(
            oracle,
            qdir,
            full_coeff,
            [[tuple(v) for v in f["transforms"]] for f in features],
            req_words,
            excluded,
        )
        holdout_rows = holdout_rows[: args.holdouts]

        candidate["holdout"] = {
            "requested": args.holdouts,
            "collected": len(holdout_rows),
            "residual_nonzero": sum(1 for x in holdout_rows if x["residual"] != "0" and x["residual"] != "0/1"),
            "rows": holdout_rows[: min(40, len(holdout_rows))],
            "word_coverage": sorted(set(r["word"] for r in holdout_rows)),
        }

    payload["candidate"] = candidate
    payload["checkpoints"].append({"stage": "done", "time": datetime.utcnow().isoformat() + "Z"})
    write_checkpoint(payload_path, payload)
    write_report(report_path, payload)

    print(str(payload_path))


if __name__ == "__main__":
    main()
