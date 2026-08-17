#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
from collections import Counter
from fractions import Fraction
from pathlib import Path

from round8_hinge_decisive import (
    compute_RQ,
    eval_feature_fast,
    parse_fraction,
    precompute_fast_cache,
    check_row_filters,
    SIGMA,
)
import pole_batch as pb


def date_utc() -> str:
    return (
        subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%S"], universal_newlines=True).strip()
    )


def sha256_text(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def omega_key(omega):
    return tuple((w.numerator, w.denominator) for w in omega)


def fraction_str(v: Fraction) -> str:
    if v.denominator == 1:
        return str(v.numerator)
    return f"{v.numerator}/{v.denominator}"


def evaluate_support_point(omega, cache_row, support):
    # u,v,e3m,e3p from explicit formula
    u = omega[0] + omega[1] + omega[2]
    v = omega[0] * omega[1] + omega[0] * omega[2] + omega[1] * omega[2]
    e3m = omega[0] * omega[1] * omega[2]
    e3p = omega[3] * omega[4] * omega[5]

    total = Fraction(0, 1)
    for ent in support:
        coeff = Fraction(str(ent["value"]))
        if ent["kind"] == "hinge":
            transforms = ent["metadata"].get("transforms", [])
            total += coeff * eval_feature_fast(cache_row, [tuple(t) for t in transforms] if transforms else transforms)
        else:
            i, j, k, l = ent["metadata"].get("term", [0, 0, 0, 0])
            total += coeff * (u ** int(i)) * (v ** int(j)) * (e3m ** int(k)) * (e3p ** int(l))
    return total


def read_rows(qdir: Path):
    rows_path = qdir / "bots/student-1/data/round8_hinge_decisive_rows.json"
    with rows_path.open() as f:
        payload = json.load(f)
    rows = payload.get("rows", [])
    fit_keys = set()
    for r in rows:
        try:
            omega = tuple(parse_fraction(x) for x in r["omega"])
        except Exception:
            continue
        fit_keys.add(omega_key(omega))
    return rows, fit_keys, rows_path


def load_solution(qdir: Path):
    path = qdir / "bots/student-1/data/round8_hinge_decisive_solution.json"
    with path.open() as f:
        sol = json.load(f)
    if sol.get("status") != "ok" or not sol.get("residual_ok"):
        raise RuntimeError(f"solution status/residual not ok: {sol}")
    support = sol.get("support", [])
    return sol, support, path


def scan_holdout_points(qdir: Path, fit_keys, target_count=40):
    holdouts = []
    word_counts = Counter()
    seen = set()
    limit = 6000
    inspected = 0
    while len(holdouts) < target_count or len(word_counts) < 6:
        for rec in pb.build_integer_samples(limit):
            inspected += 1
            omega = tuple(parse_fraction(x) for x in rec["omega"])
            key = omega_key(omega)
            if key in fit_keys or key in seen:
                continue
            ok, reason = check_row_filters(omega)
            if not ok:
                continue
            try:
                word = pb.sorted_sign_word(omega)
            except Exception:
                word = pb.chamber_signature(omega) if hasattr(pb, "chamber_signature") else str(omega)
            holdouts.append(
                {
                    "point_id": f"holdout_{len(holdouts)+1:04d}",
                    "omega": list(omega),
                    "word": word,
                }
            )
            seen.add(key)
            word_counts[word] += 1
            if len(holdouts) >= target_count and len(word_counts) >= 6:
                break
        if len(holdouts) >= target_count and len(word_counts) >= 6:
            break
        if limit >= 24000:
            break
        limit *= 2
    return holdouts, word_counts, inspected, len(holdouts), len(word_counts)


def main():
    ap = argparse.ArgumentParser(description="fresh holdout evaluator for round8 formula")
    ap.add_argument("--qdir", type=Path, default=Path("."))
    ap.add_argument("--target", type=int, default=40)
    args = ap.parse_args()

    qdir = args.qdir.resolve()

    solution, support, solution_path = load_solution(qdir)
    _, fit_keys, rows_path = read_rows(qdir)

    holdout_records, word_counts, inspected, count, unique_words = scan_holdout_points(
        qdir, fit_keys, target_count=args.target * 3
    )
    if count < args.target:
        raise RuntimeError(f"insufficient holdouts: got {count}, need {args.target}")
    if unique_words < 6:
        raise RuntimeError(f"insufficient word coverage: {unique_words} words, need >=6")

    cache = precompute_fast_cache([{"omega": r["omega"]} for r in holdout_records], max_alpha=8, max_hinge=4)
    bg_path = qdir / "bots/student-1/bg_round8"
    if not bg_path.exists():
        raise RuntimeError(f"missing bg_round8 binary at {bg_path}")
    oracle = pb.BGOracle(str(bg_path), sigma=SIGMA)

    rows_out = []
    residual_nonzero = 0
    residual_zero = 0
    witness = None
    bg_fail = 0
    evaluated = 0

    for ridx, rec in enumerate(holdout_records):
        omega = rec["omega"]
        try:
            bg = oracle._run_amp(tuple(omega), sigma=SIGMA, g=1)
        except Exception:
            bg_fail += 1
            continue
        _, _, p_pole = pb.build_channels(omega)
        rq = compute_RQ(omega)
        s = Fraction(bg["im"]) - Fraction(p_pole) - rq
        evaluated += 1

        pred = evaluate_support_point(omega, cache[ridx], solution["support"])
        res = pred - s
        if res == 0:
            residual_zero += 1
        else:
            residual_nonzero += 1
            if witness is None:
                witness = {
                    "point_id": rec["point_id"],
                    "omega": [fraction_str(x) for x in omega],
                    "prediction": fraction_str(pred),
                    "target": fraction_str(s),
                    "residual": fraction_str(res),
                    "p_pole": fraction_str(Fraction(p_pole)),
                    "RQ": fraction_str(rq),
                }

        rows_out.append(
            {
                "point_id": rec["point_id"],
                "omega": [fraction_str(x) for x in omega],
                "word": rec["word"],
                "A6_im": fraction_str(Fraction(bg["im"])),
                "P_pole": fraction_str(Fraction(p_pole)),
                "RQ": fraction_str(rq),
                "S": fraction_str(s),
                "prediction": fraction_str(pred),
                "residual": fraction_str(res),
            }
        )

    if evaluated < args.target:
        raise RuntimeError(f"insufficient evaluated holdout points: {evaluated} < target {args.target}")

    if witness is None:
        status = "passed"
    else:
        status = "failed"

    out_path = qdir / "bots/student-1/data/round8_fresh_holdouts.json"
    report_path = qdir / "bots/student-1/derivations/round8_fresh_holdouts_raw_report.md"

    bg_src = qdir / "bg.cpp"
    bg_copy = qdir / "bots/student-1/bg_round8.cpp"
    out_payload = {
        "generated_at": date_utc(),
        "status": status,
        "qdir": str(qdir),
        "target": args.target,
        "sample_rows": len(rows_out),
        "inspected_scans": inspected,
        "word_counts": dict(word_counts),
        "words_covered": len(word_counts),
        "support_count": len(solution["support"]),
        "residual_zero_count": residual_zero,
        "residual_nonzero_count": residual_nonzero,
        "evaluated_count": evaluated,
        "bg_fail_count": bg_fail,
        "solution_path": str(solution_path),
        "rows_file": str(rows_path),
        "bg_binary": str(bg_path),
        "hashes": {
            "solution": sha256_text(solution_path),
            "bg_source": sha256_text(bg_src),
            "bg_copy": sha256_text(bg_copy),
            "bg_binary": sha256_text(bg_path),
        },
        "witness": witness,
        "rows": rows_out,
    }
    out_path.write_text(json.dumps(out_payload, indent=2) + "\n")

    report = [
        "# round8 fresh holdouts report",
        "",
        f"status: {status}",
        f"points: {len(rows_out)}",
        f"residual_zero: {residual_zero}",
        f"residual_nonzero: {residual_nonzero}",
        f"word_counts: {dict(word_counts)}",
        "",
        f"rows_file: {rows_path}",
        f"solution_file: {solution_path}",
        f"holdout_json: {out_path}",
    ]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report) + "\n")


if __name__ == "__main__":
    main()
