#!/usr/bin/env python3
"""Diagnostic-only scan for the existing round-3 branch polynomials.

This script does not perform any new interpolation. It only
re-queries the BG oracle, compares pointwise residuals against existing
round3_context_{a,b,c,d}.json polynomials, and records signature-based
stability data.
"""

import argparse
import json
import random
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Tuple

import sympy as sp

from round3_bottomup import DATA, R2, build_fresh_oracle, eval_row_int, fstr

PAIR_Q_KEYS = [
    "q_1_4", "q_1_5", "q_1_6",
    "q_2_4", "q_2_5", "q_2_6",
    "q_3_4", "q_3_5", "q_3_6",
]
TRIPLE_Q_KEYS = [
    "q_1_45", "q_1_46", "q_1_56",
    "q_2_45", "q_2_46", "q_2_56",
    "q_3_45", "q_3_46", "q_3_56",
]
W = sp.symbols("w1:6")


def sign_char(x: Fraction) -> str:
    if x > 0:
        return "+"
    if x < 0:
        return "-"
    return "0"


def canonical_layout_from_word(word: str) -> List[int]:
    minus = []
    plus = []
    for pos, ch in enumerate(word):
        if ch == "-":
            minus.append(pos)
        elif ch == "+":
            plus.append(pos)
        else:
            raise ValueError("invalid word %r" % (word,))

    layout = {}
    for j, pos in enumerate(minus):
        layout[pos] = j + 1
    for j, pos in enumerate(plus):
        layout[pos] = 4 + j
    return [layout[pos] for pos in range(6)]


def scaled_w(point: R2.SixPoint):
    S = point.b + point.c + point.d + point.e
    vals = [w * S for w in point.omega[:5]]
    if any(v.denominator != 1 for v in vals):
        raise RuntimeError("non-integral scaled coordinate")
    return tuple(int(v.numerator) for v in vals), S


def evaluate_remainder(oracle: R2.BGOracle, point: R2.SixPoint):
    result, err = R2.safe_on_shell(
        oracle,
        6,
        [point.b, point.c, point.d, point.e],
    )
    if result is None:
        raise RuntimeError(err)
    omega, re_part, im_part = result
    if tuple(omega) != tuple(point.omega):
        raise RuntimeError("oracle returned inconsistent omega ordering")
    if re_part != 0:
        raise RuntimeError("non-imaginary amplitude")
    remainder, _, _ = R2.wall_pole_subtracted(point, im_part)
    return remainder


def point_signature(point: R2.SixPoint):
    sorted_word, strict, _ = point.sorted_word()
    return {
        "word": sorted_word,
        "strict": strict,
        "layout": canonical_layout_from_word(sorted_word),
        "omega_unsorted": "".join(sign_char(x) for x in point.omega),
        "omega_sorted": "".join(sign_char(x) for x in [point.omega[i] for i in sorted(range(6), key=lambda i: abs(point.omega[i]), reverse=True)]),
        "pair_sign": {k: sign_char(point.pair_q[k]) for k in PAIR_Q_KEYS},
        "triple_sign": {k: sign_char(point.triple_q[k]) for k in TRIPLE_Q_KEYS},
    }


def basis_from_payload(payload: Dict[str, object]):
    return [tuple(x) for x in payload["meta"]["basis8"]]


def poly_from_branch(coeff, basis):
    return sp.Poly(
        sum(
            sp.Rational(c.numerator, c.denominator) * sp.prod(W[i] ** e[i] for i in range(5))
            for c, e in zip(coeff, basis)
            if c != 0
        ),
        *W,
        domain=sp.QQ,
    )


def candidate_stream(seed: int):
    rng = random.Random(seed)
    for bound in [16, 28, 44, 64, 90, 130, 190, 270, 370, 520, 760]:
        for _ in range(700):
            yield (
                rng.randint(-bound, bound),
                rng.randint(-bound, bound),
                rng.randint(-bound, bound),
                rng.randint(-bound, bound),
            )
        half = list(range(-bound // 2, bound // 2 + 1))
        for b in half:
            for c in half:
                for d in half:
                    for e in half:
                        if rng.random() > 0.20:
                            continue
                        yield (b, c, d, e)
    while True:
        yield (rng.randint(-2000, 2000), rng.randint(-2000, 2000), rng.randint(-2000, 2000), rng.randint(-2000, 2000))


def build_branch_entry(context: Dict[str, object], tag: str, side: str):
    rec = context[side]
    if not rec.get("coefficients"):
        return None
    coeff = [Fraction(x) for x in rec["coefficients"]]
    basis = basis_from_payload(context)
    poly = poly_from_branch(coeff, basis)

    sample = rec["samples"][0] if rec.get("samples") else rec["holdouts"][0]
    source_point = R2.SixPoint(*[Fraction(x) for x in sample["free"]])
    sig = point_signature(source_point)

    return {
        "branch_id": f"{tag}_{side}",
        "tag": tag,
        "side": side,
        "coeff": coeff,
        "basis": basis,
        "poly": poly,
        "signature": sig,
        "source_free": [fstr(x) for x in (source_point.b, source_point.c, source_point.d, source_point.e)],
    }


def hamming_diff(a: Dict[str, str], b: Dict[str, str]):
    return [k for k in TRIPLE_Q_KEYS if a[k] != b[k]]


def probe_branch(oracle: R2.BGOracle, branch: Dict[str, object], max_attempts: int, controls_target: int, diff_target: int):
    coeff = branch["coeff"]
    basis = branch["basis"]
    sig = branch["signature"]
    source_key = tuple(branch["source_free"])

    out = {
        "meta": {
            "branch_id": branch["branch_id"],
            "word": sig["word"],
            "layout": sig["layout"],
            "omega_unsorted": sig["omega_unsorted"],
            "pair_sign": sig["pair_sign"],
            "triple_sign": sig["triple_sign"],
            "poly_terms": len(branch["poly"].terms()),
        },
        "stats": {
            "attempts": 0,
            "paired_attempts": 0,
            "same_triple_found": 0,
            "same_triple_zero": 0,
            "single_diff_found": 0,
            "single_diff_zero": 0,
            "single_diff_records": 0,
        },
        "same_triple_controls": [],
        "single_diff_triples": [],
        "notes": [],
    }

    stream = candidate_stream(sum(ord(x) for x in branch["branch_id"]))
    same_count = 0
    single_count = 0

    for b, c, d, e in stream:
        if out["stats"]["attempts"] >= max_attempts:
            break
        out["stats"]["attempts"] += 1

        key = (fstr(b), fstr(c), fstr(d), fstr(e))
        if key == source_key:
            continue

        try:
            point = R2.SixPoint(Fraction(b), Fraction(c), Fraction(d), Fraction(e))
        except Exception:
            continue
        if not point.is_generic():
            continue

        sorted_word, strict, _ = point.sorted_word()
        if not strict or sorted_word != sig["word"]:
            continue

        pair_sig = {k: sign_char(point.pair_q[k]) for k in PAIR_Q_KEYS}
        if pair_sig != sig["pair_sign"]:
            continue

        out["stats"]["paired_attempts"] += 1

        triple_sig = {k: sign_char(point.triple_q[k]) for k in TRIPLE_Q_KEYS}
        W5, S = scaled_w(point)
        row = eval_row_int(W5, basis)
        pred = sum(c * Fraction(v) for c, v in zip(coeff, row))
        try:
            obs = evaluate_remainder(oracle, point) * (S ** 8)
        except Exception:
            continue
        residual = pred - obs

        diff = hamming_diff(sig["triple_sign"], triple_sig)

        rec = {
            "free": [fstr(point.b), fstr(point.c), fstr(point.d), fstr(point.e)],
            "S": fstr(S),
            "R_scaled8": fstr(obs),
            "pred_scaled8": fstr(pred),
            "residual": fstr(residual),
            "triple_sign": triple_sig,
            "pair_sign": pair_sig,
            "triple_diff_flags": diff,
        }

        if len(diff) == 0:
            same_count += 1
            if same_count <= controls_target:
                out["same_triple_controls"].append(rec)
            if residual == 0:
                out["stats"]["same_triple_zero"] += 1
            out["stats"]["same_triple_found"] = min(same_count, controls_target)

        elif len(diff) == 1:
            single_count += 1
            out["stats"]["single_diff_records"] += 1
            if residual == 0:
                out["stats"]["single_diff_zero"] += 1
            if single_count <= diff_target:
                out["single_diff_triples"].append(rec)
            out["stats"]["single_diff_found"] = min(single_count, diff_target)

        if same_count >= controls_target and single_count >= diff_target:
            break

    if out["stats"]["same_triple_found"] < controls_target:
        out["notes"].append(
            "insufficient same-triple controls after {} paired attempts".format(
                out["stats"]["paired_attempts"]
            )
        )
    if out["stats"]["single_diff_found"] < diff_target:
        out["notes"].append(
            "insufficient single-flag triple probes after {} paired attempts".format(
                out["stats"]["paired_attempts"]
            )
        )
    return out


def compare_two_polys(contexts: Dict[str, object], a_tag: str, a_side: str, b_tag: str, b_side: str):
    def branch_poly(tag, side):
        context = contexts[tag]
        rec = context[side]
        coeff = [Fraction(x) for x in rec["coefficients"]]
        basis = [tuple(x) for x in context["meta"]["basis8"]]
        poly = poly_from_branch(coeff, basis)
        sample = rec["samples"][0] if rec.get("samples") else rec["holdouts"][0]
        sig = point_signature(R2.SixPoint(*[Fraction(x) for x in sample["free"]]))
        return poly, sig

    poly_a, sig_a = branch_poly(a_tag, a_side)
    poly_b, sig_b = branch_poly(b_tag, b_side)
    diff = poly_a - poly_b
    terms = diff.terms()

    if terms:
        lead_mono, lead_coeff = terms[0]
    else:
        lead_mono, lead_coeff = (), 0

    return {
        "term_count": len(terms),
        "leading_term": {
            "monomial": list(lead_mono),
            "coefficient": str(lead_coeff),
        },
        "same_sorted_word": sig_a["word"] == sig_b["word"],
        "same_pair_sign": sig_a["pair_sign"] == sig_b["pair_sign"],
        "word_a": sig_a["word"],
        "word_b": sig_b["word"],
    }


def corrected_wall_trace_scan():
    src = DATA / "round3_wall_trace_scan.json"
    dst = DATA / "round3_wall_trace_scan_corrected.json"
    if not src.exists():
        return None
    payload = json.loads(src.read_text())
    for rec in payload.get("results", []):
        if "H_wall_compact_formula" in rec:
            rec["deprecated_H_wall_compact_formula_stale"] = rec.pop("H_wall_compact_formula")
    payload["deprecation_note"] = "H_wall_beta_formula is authoritative; deprecated field used the old minus-only beta selector."
    dst.write_text(json.dumps(payload, indent=2, sort_keys=True))
    return str(dst)


def short_report(path: Path, branch_reports: Dict[str, object], pair_reports: Dict[str, object], corrected: str):
    out = [
        "# Round-4 refinement diagnostic",
        "",
        f"- output: {path}",
        "",
        "## Branch summaries",
        "",
        "| branch | same_triple_controls | single_diff_triples | attempts | paired_attempts |",
        "| --- | --- | --- | --- | --- |",
    ]
    for branch, rec in sorted(branch_reports.items()):
        out.append(
            "| {} | {} | {} | {} | {} |".format(
                branch,
                rec["stats"]["same_triple_found"],
                rec["stats"]["single_diff_found"],
                rec["stats"]["attempts"],
                rec["stats"]["paired_attempts"],
            )
        )
    out.extend([
        "",
        "## Pair comparison",
        "",
        *[
            "- {}: terms={}, leading={}, coeff={}".format(
                key,
                val["term_count"],
                val["leading_term"]["monomial"],
                val["leading_term"]["coefficient"],
            )
            for key, val in sorted(pair_reports.items())
        ],
        "",
        f"- corrected wall-trace copy: {corrected}",
    ])
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--controls", type=int, default=12)
    parser.add_argument("--diff", type=int, default=20)
    parser.add_argument("--max-attempts", type=int, default=120000)
    args = parser.parse_args()

    DATA.mkdir(parents=True, exist_ok=True)
    oracle, build_cmd = build_fresh_oracle()

    branch_reports = {}
    contexts = {}
    for tag in ["a", "b", "c", "d"]:
        payload = json.loads((DATA / f"round3_context_{tag}.json").read_text())
        contexts[tag] = payload
        for side in ["left", "right"]:
            entry = build_branch_entry(payload, tag, side)
            if entry is None:
                continue
            key = f"round3_context_{tag}_{side}"
            print(f"scanning {key}")
            branch_reports[key] = probe_branch(
                oracle,
                entry,
                max_attempts=args.max_attempts,
                controls_target=args.controls,
                diff_target=args.diff,
            )

    pair_reports = {
        "a_left_minus_c_right": compare_two_polys(contexts, "a", "left", "c", "right"),
        "a_right_minus_c_left": compare_two_polys(contexts, "a", "right", "c", "left"),
    }

    corrected = corrected_wall_trace_scan()

    out = {
        "meta": {
            "build_command": " ".join(build_cmd),
            "controls_target": args.controls,
            "diff_target": args.diff,
            "max_attempts": args.max_attempts,
            "source_count": len(branch_reports),
            "wall_trace_scan_corrected": corrected,
        },
        "branches": branch_reports,
        "pair_differences": pair_reports,
        "stats": {
            "same_triple_zero": sum(b["stats"]["same_triple_zero"] for b in branch_reports.values()),
            "single_diff_zero": sum(b["stats"]["single_diff_zero"] for b in branch_reports.values()),
        },
    }

    out_path = DATA / "round4_refinement_diagnostic.json"
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True))

    report_path = DATA / "round4_refinement_diagnostic_report.md"
    report_path.write_text(short_report(out_path, branch_reports, pair_reports, str(corrected)))

    print(out_path)
    print(report_path)


if __name__ == "__main__":
    main()
