#!/usr/bin/env python3

import argparse
import importlib.util
import json
import math
import hashlib
import subprocess
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import pole_batch as pb
import round6_assembly as round6
import round7_hinge_orbit as r7

SIGMA = pb.SIGMA
MINUS = pb.MINUS
PLUS = pb.PLUS
ANCHOR_OMEGA = (Fraction(-8, 1), Fraction(2, 1), Fraction(3, 1), Fraction(4, 1), Fraction(5, 1), Fraction(-6, 1))
ANCHOR_EXPECT = {
    "A6_im": Fraction(-9190656, 7),
    "P_pole": Fraction(42588288, 7),
    "RQ": Fraction(-136630560, 1),
    "S": Fraction(129233568, 1),
}

TARGET_ROWS = 900


def utc_timestamp() -> str:
    try:
        return subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%S"], text=True).strip()
    except Exception:
        return __import__("datetime").datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


def sha256_text(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def fraction_to_str(v: Fraction) -> str:
    v = Fraction(v)
    if v.denominator == 1:
        return str(v.numerator)
    return f"{v.numerator}/{v.denominator}"


def parse_fraction(v):
    if isinstance(v, Fraction):
        return v
    if isinstance(v, int):
        return Fraction(v, 1)
    if isinstance(v, str):
        s = v.strip()
        if not s:
            raise ValueError("empty fraction token")
        if s[0] == "+":
            s = s[1:]
        if "/" in s:
            n, d = s.split("/", 1)
            return Fraction(int(n), int(d))
        return Fraction(int(s), 1)
    raise TypeError(f"unsupported fraction token type {type(v)!r}")


def write_json(path: Path, payload: Dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def lcm(a: int, b: int) -> int:
    return abs(a // math.gcd(a, b) * b)


def safe_lcm(values: Sequence[int]) -> int:
    out = 1
    for v in values:
        out = lcm(out, int(v))
    return out


def copy_and_compile_bg(qdir: Path) -> Dict:
    src = qdir / "bg.cpp"
    if not src.exists():
        raise RuntimeError(f"missing shared bg.cpp at {src}")
    dst = qdir / "bots/student-1/bg_round8.cpp"
    dst.write_text(src.read_text())

    binary = qdir / "bots/student-1/bg_round8"
    cmd = ["g++", "-O2", "-std=c++17", "-o", str(binary), str(dst), "-lgmpxx", "-lgmp"]
    proc = subprocess.run(cmd, cwd=str(qdir), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if proc.returncode != 0:
        raise RuntimeError(f"bg compile failed: {proc.stderr.strip()}")

    payload = {
        "source": str(src),
        "copied": str(dst),
        "binary": str(binary),
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "source_sha256": sha256_text(src),
        "copied_sha256": sha256_text(dst),
    }
    if payload["source_sha256"] != payload["copied_sha256"]:
        raise RuntimeError("bg source/copy SHA mismatch")
    return payload


def compute_RQ(omega: Sequence[Fraction]) -> Fraction:
    x = [w * w for w in omega]
    total = Fraction(0, 1)
    for m in MINUS:
        for p, q in combinations(PLUS, 2):
            t = next(i for i in PLUS if i not in (p, q))
            Q = x[p] + x[q] - x[m]
            total += max(Q, Fraction(0, 1)) ** 3 * omega[m] * omega[t]
    return -32 * total


def check_row_filters(omega: Sequence[Fraction]):
    if len(omega) != 6:
        return False, "len_not_6"
    if any(w == 0 for w in omega):
        return False, "zero_omega"
    if not pb.on_shell(omega, sigma=SIGMA):
        return False, "not_on_shell"
    chamber = pb.chamber_signature(omega)
    if chamber == "degenerate":
        return False, "degenerate_chamber"

    sq = [w * w for w in omega]
    for m in MINUS:
        for p in PLUS:
            if sq[p] - sq[m] == 0:
                return False, "q_wall"
    for m in MINUS:
        for p, q in combinations(PLUS, 2):
            if sq[p] + sq[q] - sq[m] == 0:
                return False, "Q_wall"

    channels, _, _ = pb.build_channels(omega)
    if any(c["d"] == 0 for c in channels):
        return False, "zero_denom_d"
    return True, chamber


def build_candidate_rows(qdir: Path, oracle, target_rows: int = TARGET_ROWS):
    source = json.loads((qdir / "bots/student-1/data/round6_assembly_selfcheck.json").read_text())
    source_rows = source.get("rows", [])
    if not source_rows:
        raise RuntimeError("selfcheck payload missing rows")
    expected_words = list(dict.fromkeys(source.get("sampling", {}).get("source_words", [])))
    if not expected_words:
        expected_words = sorted({r["sorted_word"] for r in source_rows if "sorted_word" in r})

    accepted = []
    seen = set()
    seen_words = set()
    rejects = Counter()
    checkpoints = []

    out = {
        "generated_at": utc_timestamp(),
        "selfcheck_source_rows": len(source_rows),
        "expected_words": expected_words,
        "sample_rows": 0,
    }

    def row_from_rec(rec, source_label):
        omega = tuple(parse_fraction(x) for x in rec["omega"])
        if omega in seen:
            return None

        ok, reason = check_row_filters(omega)
        if not ok and reason != "":
            rejects[reason] += 1
            return None
        _, _, p_pole = pb.build_channels(omega)
        bg = oracle._run_amp(omega, sigma=SIGMA)
        if bg["re"] != 0:
            rejects["nonzero_real"] += 1
            return None

        rq = compute_RQ(omega)
        target = bg["im"] - p_pole - rq
        seen.add(omega)
        return {
            "point_id": f"r{len(accepted) + 1:04d}",
            "source": source_label,
            "omega": tuple(omega),
            "sorted_word": pb.sorted_sign_word(omega),
            "chamber_signature": pb.chamber_signature(omega),
            "A6_im": bg["im"],
            "P_pole": p_pole,
            "RQ": rq,
            "target": target,
            "u": sum(omega[:3]),
            "v": omega[0] * omega[1] + omega[0] * omega[2] + omega[1] * omega[2],
            "e3m": omega[0] * omega[1] * omega[2],
            "e3p": omega[3] * omega[4] * omega[5],
        }

    # Seed pool: all selfcheck rows first.
    for rec in source_rows:
        try:
            row = row_from_rec(rec, rec.get("source", rec.get("point_id", "selfcheck")))
        except Exception:
            rejects["parse_error"] += 1
            continue
        if row is None:
            continue
        accepted.append(row)
        seen_words.add(row["sorted_word"])
        if len(accepted) % 25 == 0:
            checkpoints.append({"stage": "selfcheck", "accepted": len(accepted), "words": sorted(seen_words)})

    # Integer expansion in deterministic batches.
    batch = 3000
    while len(accepted) < target_rows or not set(expected_words).issubset(seen_words):
        if batch > 24000:
            raise RuntimeError("insufficient deterministic rows to satisfy target/coverage")

        added = 0
        for rec in pb.build_integer_samples(batch):
            if len(accepted) >= target_rows and set(expected_words).issubset(seen_words):
                break
            row = None
            try:
                omega = tuple(parse_fraction(x) for x in rec["omega"])
                if omega in seen:
                    continue
                # row_from_rec accepts rec with existing omega field
                tmp = dict(rec)
                tmp["omega"] = omega
                row = row_from_rec(tmp, rec.get("source", "integer"))
            except Exception:
                rejects["integer_parse_error"] += 1
                continue
            if row is None:
                continue
            accepted.append(row)
            seen_words.add(row["sorted_word"])
            added += 1
            if len(accepted) % 25 == 0:
                checkpoints.append({"stage": "integer", "accepted": len(accepted), "words": sorted(seen_words)})

        if added == 0:
            raise RuntimeError(f"integer expansion batch={batch} produced no accepted rows")

        batch *= 2

    out.update(
        {
            "accepted_rows": len(accepted),
            "word_counts": dict(Counter(r["sorted_word"] for r in accepted)),
            "chamber_counts": dict(Counter(r["chamber_signature"] for r in accepted)),
            "rejects": dict(rejects),
        }
    )

    missing = sorted(set(expected_words) - seen_words)
    if missing:
        raise RuntimeError(f"expected words missing from accepted rows: {missing}")

    return accepted, out, checkpoints


def precompute_fast_cache(rows: List[Dict], max_alpha: int = 8, max_hinge: int = 4):
    cache = []
    for rec in rows:
        omega = rec["omega"]

        omega_pows_num = []
        omega_pows_den = []
        for i in range(6):
            w = omega[i]
            wn, wd = int(w.numerator), int(w.denominator)
            num_pows = [1]
            den_pows = [1]
            cur_num = wn
            cur_den = wd
            for _ in range(max_alpha):
                num_pows.append(cur_num)
                den_pows.append(cur_den)
                cur_num *= wn
                cur_den *= wd
            omega_pows_num.append(num_pows)
            omega_pows_den.append(den_pows)

        x = [w * w for w in omega]
        hinge_pows_num = []
        hinge_pows_den = []
        for m in MINUS:
            for p in PLUS:
                q = x[p] - x[m]
                if q < 0:
                    q_num, q_den = 0, 1
                else:
                    q_num, q_den = int(q.numerator), int(q.denominator)

                num_pows = [1]
                den_pows = [1]
                cur_num = q_num
                cur_den = q_den
                for _ in range(max_hinge):
                    num_pows.append(cur_num)
                    den_pows.append(cur_den)
                    cur_num *= q_num
                    cur_den *= q_den
                hinge_pows_num.append(num_pows)
                hinge_pows_den.append(den_pows)

        cache.append(
            {
                "omega_pows_num": omega_pows_num,
                "omega_pows_den": omega_pows_den,
                "hinge_pows_num": hinge_pows_num,
                "hinge_pows_den": hinge_pows_den,
            }
        )
    return cache


def eval_transform_fast(cache_row: Dict, r_seed: Tuple[int, ...], a_seed: Tuple[int, ...]):
    if any(e < 0 for e in a_seed) or any(e < 0 for e in r_seed):
        return Fraction(0, 1)

    num = 1
    den = 1
    omega_pows_num = cache_row["omega_pows_num"]
    omega_pows_den = cache_row["omega_pows_den"]
    for i, e in enumerate(a_seed):
        if e:
            num *= omega_pows_num[i][e]
            den *= omega_pows_den[i][e]

    hinge_pows_num = cache_row["hinge_pows_num"]
    hinge_pows_den = cache_row["hinge_pows_den"]
    for i, e in enumerate(r_seed):
        if e:
            num *= hinge_pows_num[i][e]
            den *= hinge_pows_den[i][e]

    if num == 0:
        return Fraction(0, 1)
    if den == 0:
        raise ZeroDivisionError("zero denominator in feature evaluation")
    g = math.gcd(num, den)
    return Fraction(num // g, den // g)


def eval_feature_fast(cache_row: Dict, transforms: List[Tuple[Tuple[int, ...], Tuple[int, ...]]]):
    total_num = 0
    total_den = 1
    has_value = False

    for r_seed, a_seed in transforms:
        v = eval_transform_fast(cache_row, r_seed, a_seed)
        if v.numerator == 0:
            continue
        if not has_value:
            total_num = v.numerator
            total_den = v.denominator
            has_value = True
            continue

        g = math.gcd(total_den, v.denominator)
        lcm = (total_den // g) * v.denominator
        total_num = total_num * (lcm // total_den) + v.numerator * (lcm // v.denominator)
        total_den = lcm
        g2 = math.gcd(abs(total_num), total_den)
        total_num //= g2
        total_den //= g2

    if not has_value:
        return Fraction(0, 1)
    return Fraction(total_num, total_den)


def build_hinge_features(rows: List[Dict], qdir: Path, progress_path: Path):
    cache = precompute_fast_cache(rows, max_alpha=8, max_hinge=4)

    by_seed = {}
    seed_count = 0
    seed_by_depth = defaultdict(int)
    for depth in (1, 2, 3, 4):
        for r_seed in r7.compositions(depth, 9):
            a_sum = 8 - 2 * depth
            for a_seed in r7.compositions(a_sum, 6):
                transforms, canonical = r7.canonical_orbit(r_seed, a_seed)
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

    candidate = []
    signatures = {}
    zero_removed = 0
    duplicate_removed = 0
    seed_items = sorted(by_seed.items(), key=lambda kv: kv[0])
    for idx, (_, item) in enumerate(seed_items):
        terms = item["transforms"]
        values = [eval_feature_fast(cache_row, terms) for cache_row in cache]
        if all(v == 0 for v in values):
            zero_removed += 1
            continue
        sig = tuple((v.numerator, v.denominator) for v in values)
        if sig in signatures:
            duplicate_removed += 1
            continue
        signatures[sig] = True
        candidate.append(
            {
                "id": idx,
                "depth": item["depth"],
                "seed_r": [int(x) for x in item["seed_r"]],
                "seed_a": [int(x) for x in item["seed_a"]],
                "transforms": [(list(r), list(a)) for r, a in terms],
                "complexity": sum(item["seed_r"]) + sum(item["seed_a"]),
                "values": values,
            }
        )

        if len(candidate) % 75 == 0:
            ch = json.loads(progress_path.read_text())
            ch.setdefault("checkpoints", []).append(
                {"stage": "features_chunk", "kept": len(candidate), "seed_seen": idx + 1, "time": utc_timestamp()}
            )
            write_json(progress_path, ch)

    ordered = sorted(candidate, key=lambda f: (f["depth"], f["complexity"], f["id"]))
    kept_by_depth = Counter(f["depth"] for f in ordered)
    nrows = len(rows)
    nfeat = len(ordered)
    A_hinge = np.empty((nrows, nfeat), dtype=object)
    feature_meta = []
    for j, f in enumerate(ordered):
        A_hinge[:, j] = np.array(f["values"], dtype=object)
        feature_meta.append(
            {
                "id": f["id"],
                "depth": f["depth"],
                "seed_r": f["seed_r"],
                "seed_a": f["seed_a"],
                "transforms": f["transforms"],
                "complexity": f["complexity"],
            }
        )

    # checkpoint per depth chunk
    for d in (1, 2, 3, 4):
        upto = len([f for f in ordered if f["depth"] <= d])
        if upto == 0:
            continue
        np.save(qdir / "bots/student-1/data/round8_A_features.npy", A_hinge[:, :upto])
        ch = json.loads(progress_path.read_text())
        ch.setdefault("checkpoints", []).append({"stage": "feature_depth_chunk", "depth": d, "columns": upto, "time": utc_timestamp()})
        write_json(progress_path, ch)

    stats = {
        "seed_count": seed_count,
        "seed_by_depth": {str(k): v for k, v in seed_by_depth.items()},
        "kept_count": nfeat,
        "zero_removed": zero_removed,
        "duplicate_removed": duplicate_removed,
        "kept_by_depth": {str(k): v for k, v in kept_by_depth.items()},
    }
    return feature_meta, A_hinge, stats


def build_global_columns(rows: List[Dict]):
    terms = round6.dual_terms()
    if len(terms) != 17:
        raise RuntimeError(f"unexpected dual term count {len(terms)} != 17")
    nrows = len(rows)
    A_global = np.empty((nrows, len(terms)), dtype=object)
    global_meta = []
    for j, (i, j2, k, l) in enumerate(terms):
        global_meta.append(
            {
                "id": 588 + j,
                "depth": "dual",
                "seed_r": [],
                "seed_a": [],
                "transforms": [],
                "complexity": i + 2 * j2 + 3 * k + 3 * l,
                "term": [int(i), int(j2), int(k), int(l)],
                "name": f"u^{i} v^{j2} e3m^{k} e3p^{l}",
            }
        )
        for ridx, row in enumerate(rows):
            A_global[ridx, j] = row["u"] ** i * row["v"] ** j2 * row["e3m"] ** k * row["e3p"] ** l
    return A_global, global_meta


def write_patched_fastsolve(qdir: Path):
    src = qdir / "bots/student-1/code/fastsolve.py"
    if not src.exists():
        src = qdir / "bots/pi/code/fastsolve.py"
    dst = qdir / "bots/student-1/code/fastsolve.py"
    raw = src.read_text()
    dst.write_text(raw)
    return dst


def smoke_test(fs):
    import random

    random.seed(0)
    ncol, nrow = 40, 120
    A = np.array([[random.randint(-9, 9) for _ in range(ncol)] for _ in range(nrow)], dtype=object)
    xtrue = np.array([random.randint(-5, 5) for _ in range(ncol)], dtype=object)
    y = A.dot(xtrue)

    c1 = fs.consistency(A, y)
    x, piv, ok = fs.exact_solve(A, y)
    base_ok = c1["consistent"] and x is not None and ok

    y2 = y.copy()
    y2[0] += 1
    c2 = fs.consistency(A, y2)
    return {"base": c1, "base_ok": bool(base_ok), "perturbed": c2}


def row_scale_to_int_arrays(A_rat: np.ndarray, y_rat: np.ndarray):
    nrows, ncols = A_rat.shape
    A_int = np.empty_like(A_rat, dtype=object)
    y_int = np.empty_like(y_rat, dtype=object)
    scales = []

    for r in range(nrows):
        denoms = [Fraction(v).denominator for v in A_rat[r, :]]
        denoms.append(Fraction(y_rat[r]).denominator)
        scale = safe_lcm(denoms)
        scales.append(scale)
        for c in range(ncols):
            fv = Fraction(A_rat[r, c])
            A_int[r, c] = fv.numerator * (scale // fv.denominator)
        fy = Fraction(y_rat[r])
        y_int[r] = fy.numerator * (scale // fy.denominator)

    return A_int, y_int, scales


def main():
    ap = argparse.ArgumentParser(description="Round8 decisive hinge/dual exact test")
    ap.add_argument("--qdir", type=Path, default=Path("."))
    ap.add_argument("--target", type=int, default=TARGET_ROWS)
    ap.add_argument("--skip-exact", action="store_true", help="skip full exact reconstruction and only write consistency checks")
    args = ap.parse_args()

    qdir = args.qdir.resolve()
    progress_path = qdir / "bots/student-1/data/round8_hinge_decisive.json"
    rows_path = qdir / "bots/student-1/data/round8_hinge_decisive_rows.json"
    report_path = qdir / "bots/student-1/derivations/round8_hinge_decisive_raw_report.md"
    coeff_path = qdir / "bots/student-1/data/round8_hinge_decisive_solution.json"
    meta_path = qdir / "bots/student-1/data/round8_A_meta.json"
    diag_path = qdir / "bots/student-1/data/round8_hinge_decisive_diag.json"

    t0 = __import__("time").time()
    payload = {
        "generated_at": utc_timestamp(),
        "script_path": str(Path(__file__).resolve()),
        "script_sha256": sha256_text(Path(__file__).resolve()),
        "qdir": str(qdir),
        "checkpoints": [{"stage": "start", "time": utc_timestamp()}],
        "artifact_paths": {},
    }

    log_path = qdir / "bots/student-1/data/round8_hinge_decisive.log"
    with log_path.open("w", encoding="utf-8") as lf:
        def log(msg):
            line = f"[{utc_timestamp()}] {msg}"
            print(line, file=lf)
            print(line)

    write_json(progress_path, payload)
    compile_info = copy_and_compile_bg(qdir)
    payload["compile"] = compile_info
    payload["checkpoints"].append({"stage": "compile", "time": utc_timestamp()})
    write_json(progress_path, payload)

    oracle = pb.BGOracle(compile_info["binary"], sigma=SIGMA)

    anchor_bg = oracle._run_amp(ANCHOR_OMEGA, sigma=SIGMA, g=1)
    _, _, anchor_pole = pb.build_channels(ANCHOR_OMEGA)
    anchor_rq = compute_RQ(ANCHOR_OMEGA)
    anchor_s = anchor_bg["im"] - anchor_pole - anchor_rq

    payload["anchor"] = {
        "omega": [fraction_to_str(x) for x in ANCHOR_OMEGA],
        "A6_im": fraction_to_str(anchor_bg["im"]),
        "P_pole": fraction_to_str(anchor_pole),
        "RQ": fraction_to_str(anchor_rq),
        "S": fraction_to_str(anchor_s),
    }
    if anchor_bg["re"] != 0:
        raise RuntimeError("anchor non-zero real part")
    if (
        anchor_bg["im"] != ANCHOR_EXPECT["A6_im"]
        or anchor_pole != ANCHOR_EXPECT["P_pole"]
        or anchor_rq != ANCHOR_EXPECT["RQ"]
        or anchor_s != ANCHOR_EXPECT["S"]
    ):
        raise RuntimeError("anchor regression mismatch")
    payload["anchor"]["status"] = "ok"

    payload["checkpoints"].append({"stage": "anchor", "time": utc_timestamp()})
    write_json(progress_path, payload)

    rows, row_summary, row_ckpts = build_candidate_rows(qdir, oracle, args.target)
    payload["sample_summary"] = row_summary
    payload["row_checkpoints"] = row_ckpts
    payload["checkpoints"].append({"stage": "rows", "time": utc_timestamp(), "count": len(rows)})
    write_json(progress_path, payload)

    rows_for_json = []
    for r in rows:
        rows_for_json.append(
            {
                "point_id": r["point_id"],
                "source": r["source"],
                "omega": [fraction_to_str(x) for x in r["omega"]],
                "sorted_word": r["sorted_word"],
                "chamber_signature": r["chamber_signature"],
                "A6_im": fraction_to_str(r["A6_im"]),
                "P_pole": fraction_to_str(r["P_pole"]),
                "RQ": fraction_to_str(r["RQ"]),
                "target": fraction_to_str(r["target"]),
            }
        )
    write_json(rows_path, {"generated_at": utc_timestamp(), "rows": rows_for_json, "rows_count": len(rows_for_json)})
    payload["artifact_paths"]["rows"] = str(rows_path)

    feature_meta, A_hinge, feat_stats = build_hinge_features(rows, qdir, progress_path)
    if feat_stats["kept_count"] != 588:
        raise RuntimeError(f"unexpected hinge feature count {feat_stats['kept_count']} != 588")
    if feat_stats["kept_by_depth"] != {"1": 188, "2": 244, "3": 134, "4": 22}:
        raise RuntimeError(f"unexpected depth split {feat_stats['kept_by_depth']}")

    payload["feature_stats"] = feat_stats
    payload["checkpoints"].append({"stage": "features", "time": utc_timestamp()})

    A_global, global_meta = build_global_columns(rows)
    A_rational = np.concatenate([A_hinge, A_global], axis=1)
    if A_rational.shape != (len(rows), 605):
        raise RuntimeError(f"unexpected A shape {A_rational.shape}")

    y_rational = np.array([r["target"] for r in rows], dtype=object)
    np.save(qdir / "bots/student-1/data/round8_A_rational.npy", A_rational)
    np.save(qdir / "bots/student-1/data/round8_y_rational.npy", y_rational)
    payload["artifact_paths"]["A_rational"] = str(qdir / "bots/student-1/data/round8_A_rational.npy")
    payload["artifact_paths"]["y_rational"] = str(qdir / "bots/student-1/data/round8_y_rational.npy")

    A_int, y_int, scales = row_scale_to_int_arrays(A_rational, y_rational)
    np.save(qdir / "bots/student-1/data/round8_A_int.npy", A_int)
    np.save(qdir / "bots/student-1/data/round8_y_int.npy", y_int)
    payload["artifact_paths"]["A_int"] = str(qdir / "bots/student-1/data/round8_A_int.npy")
    payload["artifact_paths"]["y_int"] = str(qdir / "bots/student-1/data/round8_y_int.npy")
    write_json(qdir / "bots/student-1/data/round8_row_scales.json", {"row_scales": [str(v) for v in scales]})

    # deterministic recover checks
    check_rows = sorted(set([0, len(rows) // 3, 2 * len(rows) // 3, len(rows) - 1]))
    recover_checks = []
    for ridx in check_rows:
        scale = scales[ridx]
        ok = True
        for cidx in range(min(20, A_rational.shape[1])):
            if Fraction(int(A_int[ridx, cidx]), scale) != Fraction(A_rational[ridx, cidx]):
                ok = False
                break
        if Fraction(int(y_int[ridx]), scale) != Fraction(y_rational[ridx]):
            ok = False
        recover_checks.append({"row": ridx + 1, "ok": ok})
        if not ok:
            raise RuntimeError(f"recoverability check failed row={ridx}")
    payload["integer_recover_checks"] = recover_checks

    fs_path = write_patched_fastsolve(qdir)
    payload["artifact_paths"]["fastsolve"] = str(fs_path)
    spec = importlib.util.spec_from_file_location("round8_fastsolve", str(fs_path))
    fastsolve = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fastsolve)  # type: ignore

    t_smoke0 = __import__("time").time()
    smoke = smoke_test(fastsolve)
    payload["smoke_test"] = smoke
    payload["timings"] = {"smoke_sec": __import__("time").time() - t_smoke0}

    t_cons = __import__("time").time()
    con = fastsolve.consistency(A_int, y_int)
    payload["timings"]["consistency_sec"] = __import__("time").time() - t_cons

    payload["consistency"] = {
        "status": "consistent" if con["consistent"] else "inconsistent",
        "per_prime": con["per_prime"],
    }
    if con["per_prime"]:
        rank_ref = con["per_prime"][0]["rank_A"]
        payload["rank_reference"] = rank_ref
        payload["rank_deficiency"] = A_rational.shape[1] - rank_ref

    if con["consistent"]:
        t_sol = __import__("time").time()
        if args.skip_exact:
            payload["timings"]["exact_sec"] = 0.0
            payload["solution"] = {"status": "skipped", "residual_ok": False, "support_count": 0, "support": []}
        else:
            x, piv, ok = fastsolve.exact_solve(A_int, y_int)
            payload["timings"]["exact_sec"] = __import__("time").time() - t_sol
            total_meta = [dict(item) for item in feature_meta] + [dict(item) for item in global_meta]
            if not ok or x is None:
                solution = {"status": "failed", "residual_ok": False, "support_count": 0, "support": []}
            else:
                nonzero = [(i, fraction_to_str(c)) for i, c in enumerate(x) if c != 0]
                support = []
                for i, c in nonzero:
                    item = total_meta[i]
                    support.append({"column": i, "value": c, "kind": "hinge" if i < len(feature_meta) else "dual", "metadata": item})
                solution = {
                    "status": "ok" if ok else "residual_bad",
                    "support_count": len(nonzero),
                    "support": support,
                    "residual_ok": bool(ok),
                    "pivot_columns": piv,
                }
            payload["solution"] = solution
    else:
        payload["solution"] = {"status": "skipped_inconsistent"}

    payload["artifact_paths"]["solution"] = str(coeff_path)
    write_json(coeff_path, payload["solution"])

    payload["A_shape"] = list(A_rational.shape)
    payload["checkpoints"].append({"stage": "done", "time": utc_timestamp()})
    payload["total_seconds"] = __import__("time").time() - t0

    write_json(progress_path, payload)

    write_json(meta_path, {
        "feature_meta": feature_meta,
        "global_meta": global_meta,
        "feature_stats": feat_stats,
        "generated_at": utc_timestamp(),
    })

    report = [
        "# round8_hinge_decisive raw report",
        "",
        f"rows: {len(rows)}",
        f"A shape: {tuple(A_rational.shape)}",
        f"features: {len(feature_meta)}",
        f"global_columns: {len(global_meta)}",
        f"consistency: {payload['consistency']['status']}",
        f"rank: {payload.get('rank_reference')}",
        f"support: {payload['solution'].get('support_count', 0) if isinstance(payload['solution'], dict) else 0}",
        f"timing: {payload['total_seconds']:.3f}s",
    ]
    q = []
    for name, path in payload.get("artifact_paths", {}).items():
        q.append(f"- {name}: {path}")
    report.extend(["", "artifacts:"] + q)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report) + "\n")
    write_json(diag_path, payload)

if __name__ == "__main__":
    main()
