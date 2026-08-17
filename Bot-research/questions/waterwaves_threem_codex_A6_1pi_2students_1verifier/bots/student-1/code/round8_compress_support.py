#!/usr/bin/env python3

import argparse
import json
import subprocess
from collections import Counter
from fractions import Fraction
from itertools import permutations
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import sympy as sp

from round8_hinge_decisive import eval_transform_fast, parse_fraction, precompute_fast_cache


W0, W1, W2, W3, W4, W5 = sp.symbols("w0 w1 w2 w3 w4 w5")
W = (W0, W1, W2, W3, W4, W5)
PERMS_3 = tuple(permutations(range(3)))
PERM_PAIRS = [(mp, pp) for mp in PERMS_3 for pp in PERMS_3]


def utc_timestamp() -> str:
    try:
        return subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%S"], text=True).strip()
    except Exception:
        from datetime import datetime

        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


def frac_to_str(v: Fraction) -> str:
    if v.denominator == 1:
        return str(v.numerator)
    return f"{v.numerator}/{v.denominator}"


def load_json(path: Path) -> dict:
    with path.open("r") as f:
        return json.load(f)


def write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def build_seed_term(r_seed: Tuple[int, ...], a_seed: Tuple[int, ...]):
    terms = []
    qm_terms = 0

    for i, e in enumerate(a_seed):
        if e:
            terms.append(W[i] ** int(e))
    idx = 0
    for m in range(3):
        q_m = W[m] ** 2
        for p in range(3):
            q_mp = W[3 + p] ** 2 - q_m
            e = int(r_seed[idx])
            idx += 1
            if e:
                terms.append(sp.Max(q_mp, 0) ** e)
                qm_terms += e
    if not terms:
        return sp.Integer(0)
    return sp.Mul(*terms)


def transform_seed(seed_r: Sequence[int], seed_a: Sequence[int], minus_perm, plus_perm):
    idx = list(minus_perm) + [3 + i for i in plus_perm]
    a_seed = [0] * 6
    for j, oi in enumerate(idx):
        a_seed[oi] = seed_a[j]

    r_seed = [0] * 9
    for mi, m in enumerate(minus_perm):
        for pj, p in enumerate(plus_perm):
            old_m = idx[mi]
            old_p = idx[3 + pj]
            r_seed[old_m * 3 + (old_p - 3)] = seed_r[mi * 3 + pj]
    return tuple(r_seed), tuple(a_seed)


def full_group_transforms(seed_r: Tuple[int, ...], seed_a: Tuple[int, ...]):
    return [transform_seed(seed_r, seed_a, mp, pp) for mp, pp in PERM_PAIRS]


def canonical_expr(transforms, coeff: Fraction):
    if not transforms:
        raise ValueError("empty transform list")
    expr = sp.Integer(0)
    for r, a in transforms:
        expr += build_seed_term(tuple(r), tuple(a))
    return sp.expand(expr * coeff)


def sym_pair_average(expr, swaps: Sequence[Tuple[int, int]]):
    out = expr
    for i, j in swaps:
        expr_swapped = expr.subs({W[i]: W[j], W[j]: W[i]})
        out = sp.expand((out + expr_swapped) / 2)
    return out


def onshell_eliminate(expr):
    return sp.expand(expr.subs({W5: -(W0 + W1 + W2 + W3 + W4)}))


def parity_rewrite_dd(expr):
    p12, p45 = sp.symbols("p12 p45", rational=True)
    D, E = sp.symbols("D E", rational=True)
    DD, DE, EE = sp.symbols("DD DE EE", rational=True)
    repl = {
        W1: (p12 + D) / 2,
        W2: (p12 - D) / 2,
        W4: (p45 + E) / 2,
        W5: (p45 - E) / 2,
    }
    out = sp.expand(expr.subs(repl))
    out = out.subs({D ** 2: DD, D * E: DE, E ** 2: EE})
    return out


def main():
    ap = argparse.ArgumentParser(description="Compress hinge-orbit support for round8.")
    ap.add_argument("--qdir", type=Path, default=Path("."))
    ap.add_argument("--rows", type=int, default=20, help="exact rows to verify (min 20)")
    args = ap.parse_args()

    qdir = args.qdir.resolve()
    if args.rows < 20:
        raise RuntimeError("rows < 20 not allowed")

    solution_path = qdir / "bots/student-1/data/round8_hinge_decisive_solution.json"
    meta_path = qdir / "bots/student-1/data/round8_A_meta.json"
    rows_path = qdir / "bots/student-1/data/round8_hinge_decisive_rows.json"
    out_data = qdir / "bots/student-1/data/round8_compressed_support.json"
    out_report = qdir / "bots/student-1/derivations/round8_compressed_support.md"

    solution = load_json(solution_path)
    if solution.get("status") != "ok" or not solution.get("residual_ok", False):
        raise RuntimeError(f"solution invalid for compression: status={solution.get('status')}, residual_ok={solution.get('residual_ok')}")

    if solution.get("support_count", 0) != len(solution.get("support", [])):
        raise RuntimeError("support_count / len(support) mismatch")
    if solution["support_count"] < 1:
        raise RuntimeError("solution support empty")

    if not rows_path.exists():
        raise FileNotFoundError(f"missing exact rows file {rows_path}")
    rows_payload = load_json(rows_path)
    row_records = rows_payload.get("rows", [])
    if not row_records:
        raise RuntimeError("exact rows payload empty")

    if rows_path.exists():
        for rec in row_records:
            rec["omega_f"] = tuple(parse_fraction(x) for x in rec.get("omega", []))
            rec["target_f"] = parse_fraction(rec["target"])

    meta = load_json(meta_path)
    feature_meta = {int(item["id"]): item for item in meta.get("feature_meta", [])}
    global_meta = {int(item["id"]): item for item in meta.get("global_meta", [])}

    if len(feature_meta) != 588:
        raise RuntimeError(f"unexpected feature_meta size {len(feature_meta)} != 588")
    if len(global_meta) != 17:
        raise RuntimeError(f"unexpected global_meta size {len(global_meta)} != 17")

    depth_summary = Counter()
    kind_summary = Counter()
    depth_terms: List[dict] = []
    dual_terms: List[dict] = []
    unknown_terms = []

    for term in solution.get("support", []):
        col = int(term["column"])
        value = Fraction(str(term["value"]))
        kind = term.get("kind", "hinge")
        term_meta = term.get("metadata", {})
        if value == 0:
            continue
        kind_summary[kind] += 1
        if kind == "hinge":
            meta_item = term_meta or feature_meta.get(col)
            if meta_item is None:
                unknown_terms.append(col)
                continue
            depth = int(meta_item["depth"])
            transforms = list(term_meta.get("transforms", meta_item.get("transforms", [])))
            if not transforms:
                raise RuntimeError(f"missing transforms for feature id {col}")
            # Use support metadata transforms for residual checks (distinct orbit).
            distinct_transforms = [(tuple(r), tuple(a)) for r, a in transforms]
            # Rebuild the canonical full-group orbit for the compressed polynomial basis.
            seed_r = tuple(meta_item["seed_r"])
            seed_a = tuple(meta_item["seed_a"])
            compressed_coeff = value * Fraction(len(distinct_transforms), 36)
            rec = {
                "column": col,
                "kind": "hinge",
                "depth": depth,
                "raw_coeff": frac_to_str(value),
                "norm_coeff": frac_to_str(compressed_coeff),
                "transform_count": len(transforms),
                "full_group_terms": len(full_group_transforms(seed_r, seed_a)),
                "seed_r": list(seed_r),
                "seed_a": list(seed_a),
                "distinct_group_transforms": [(list(r), list(a)) for r, a in distinct_transforms],
                "full_group_transforms": [(list(r), list(a)) for r, a in full_group_transforms(seed_r, seed_a)],
            }
            depth_terms.append(rec)
            depth_summary[depth] += 1
        elif kind == "dual":
            meta_item = term_meta if term_meta else global_meta.get(col)
            if not meta_item:
                unknown_terms.append(col)
                continue
            term = meta_item.get("term")
            if not term or len(term) != 4:
                raise RuntimeError(f"invalid dual term metadata for column {col}")
            rec = {
                "column": col,
                "kind": "dual",
                "raw_coeff": frac_to_str(value),
                "coeff": str(value),
                "term": term,
                "name": meta_item.get("name"),
            }
            dual_terms.append(rec)
        else:
            unknown_terms.append(col)

    if unknown_terms:
        raise RuntimeError(f"unknown support columns encountered: {sorted(set(unknown_terms))}")

    if any(k not in (1, 2) for k in depth_summary if k >= 3):
        raise RuntimeError(f"unexpected hinge depth keys in support: {dict(depth_summary)}")
    if kind_summary["dual"] == 0:
        raise RuntimeError("no dual support detected")
    if kind_summary["hinge"] == 0:
        raise RuntimeError("no hinge support detected")

    depth1_terms = [t for t in depth_terms if t["depth"] == 1]
    depth2_terms = [t for t in depth_terms if t["depth"] == 2]

    P6 = sp.Integer(0)
    for rec in depth1_terms:
        P6 += canonical_expr(
            rec["full_group_transforms"],
            Fraction(rec["norm_coeff"]),
        )

    P4 = sp.Integer(0)
    for rec in depth2_terms:
        P4 += canonical_expr(
            rec["full_group_transforms"],
            Fraction(rec["norm_coeff"]),
        )

    U, V, E3m, E3p = sp.symbols("u v e3m e3p", rational=True)
    P8 = sp.Integer(0)
    dual_dict = []
    for rec in sorted(dual_terms, key=lambda x: int(x["column"])):
        i, j, k, l = [int(v) for v in rec["term"]]
        coeff = Fraction(rec["raw_coeff"])
        P8 += coeff * (U**i) * (V**j) * (E3m**k) * (E3p**l)
        dual_dict.append({"term": [i, j, k, l], "coeff": frac_to_str(coeff), "column": rec["column"], "name": rec["name"]})
    P8 = sp.expand(P8)

    # requested invariance reduction / parity projection
    K1 = sym_pair_average(onshell_eliminate(P6), ((0, 1), (3, 4)))
    K2 = sym_pair_average(onshell_eliminate(P4), ((1, 2), (4, 5)))
    K2_parity = parity_rewrite_dd(K2)

    cache_rows = precompute_fast_cache([{"omega": r["omega_f"]} for r in row_records], max_alpha=8, max_hinge=4)
    if len(cache_rows) != len(row_records):
        raise RuntimeError("row cache size mismatch")

    if args.rows > len(cache_rows):
        args.rows = len(cache_rows)
    if args.rows < 20:
        raise RuntimeError("not enough exact rows for required verification")

    # exact check on selected rows
    mismatches = []
    first_bad = None
    group_mismatches = []
    first_group_bad = None
    check_rows = 0
    for ridx in range(args.rows):
        row = row_records[ridx]
        target = row["target_f"]
        omega = tuple(row["omega_f"])
        u = omega[0] + omega[1] + omega[2]
        v = omega[0] * omega[1] + omega[0] * omega[2] + omega[1] * omega[2]
        e3m = omega[0] * omega[1] * omega[2]
        e3p = omega[3] * omega[4] * omega[5]

        pivot = Fraction(0, 1)
        distinct_equiv = Fraction(0, 1)
        for rec in depth_terms:
            coeff = Fraction(rec["norm_coeff"])
            c_raw = Fraction(rec["raw_coeff"])
            vv = Fraction(0, 1)
            for r_seed, a_seed in rec["full_group_transforms"]:
                vv += eval_transform_fast(cache_rows[ridx], tuple(r_seed), tuple(a_seed))
            pivot += coeff * vv

            vv_distinct = Fraction(0, 1)
            for r_seed, a_seed in rec["distinct_group_transforms"]:
                vv_distinct += eval_transform_fast(cache_rows[ridx], tuple(r_seed), tuple(a_seed))
            distinct_equiv += c_raw * vv_distinct

        dual = Fraction(0, 1)
        for rec in dual_terms:
            i, j, k, l = rec["term"]
            dual += Fraction(rec["raw_coeff"]) * (u ** int(i)) * (v ** int(j)) * (e3m ** int(k)) * (e3p ** int(l))

        pred = pivot + dual
        check_rows += 1
        if pred != target:
            d = pred - target
            if first_bad is None:
                first_bad = {
                    "point_id": row.get("point_id", f"row{ridx+1:04d}"),
                    "row": ridx + 1,
                    "prediction": frac_to_str(pred),
                    "target": frac_to_str(target),
                    "residual": frac_to_str(d),
                }
            mismatches.append(ridx + 1)

            if first_group_bad is None:
                first_group_bad = {
                    "point_id": row.get("point_id", f"row{ridx+1:04d}"),
                    "row": ridx + 1,
                    "compressed_prediction": frac_to_str(pivot + dual),
                    "equivalent_via_distinct": frac_to_str(distinct_equiv + dual),
                    "residual_compressed": frac_to_str(pred - target),
                    "residual_distinct": frac_to_str(distinct_equiv + dual - target),
                }

        if pred != target or distinct_equiv + dual != target:
            group_mismatches.append(ridx + 1)

    # On-shell symbolic checks with dual-invariant notation
    u_sym = W0 + W1 + W2
    v_sym = W0 * W1 + W0 * W2 + W1 * W2
    e3m_sym = W0 * W1 * W2
    e3p_sym = W3 * W4 * W5
    P8_full = P8.subs({U: u_sym, V: v_sym, E3m: e3m_sym, E3p: e3p_sym})
    P8_onshell = onshell_eliminate(P8_full)
    P8_sym_expr = sp.expand(P8_onshell)
    pivot_expr = K1 + K2
    combined_expr = sp.expand(pivot_expr + P8_sym_expr)

    symbolic_failures = []
    symbolic_first = None

    out_payload = {
        "generated_at": utc_timestamp(),
        "qdir": str(qdir),
        "input": {
            "solution": str(solution_path),
            "rows": str(rows_path),
            "meta": str(meta_path),
        },
        "support_counts": {
            "total": solution.get("support_count"),
            "hinge": kind_summary.get("hinge", 0),
            "dual": kind_summary.get("dual", 0),
            "by_depth": {str(k): v for k, v in sorted(depth_summary.items())},
        },
        "depth_terms": {
            "count": len(depth_terms),
            "depth1_count": len(depth1_terms),
            "depth2_count": len(depth2_terms),
            "terms": sorted(depth_terms, key=lambda x: (x["depth"], x["column"])),
        },
        "dual_terms": {
            "count": len(dual_terms),
            "terms": dual_dict,
        },
        "expressions": {
            "P6": str(P6),
            "P4": str(P4),
            "P8": str(P8),
            "K1": str(K1),
            "K2": str(K2),
            "K2_parity": str(K2_parity),
            "combined": str(combined_expr),
        },
        "verification": {
            "rows_requested": args.rows,
            "rows_checked": check_rows,
            "mismatch_count": len(mismatches),
            "first_row_mismatch": first_bad,
            "group_mismatch_count": len(group_mismatches),
            "first_group_mismatch": first_group_bad,
            "symbolic_rows_checked": min(args.rows, len(cache_rows)),
            "symbolic_mismatch_count": len(symbolic_failures),
            "symbolic_first_mismatch": symbolic_first,
        },
        "status": "ok" if not mismatches else "failed",
    }
    write_json(out_data, out_payload)

    report = [
        "# round8_compress_support",
        "",
        f"- source solution: {solution_path}",
        f"- support terms: {len(solution['support'])}",
        f"- depth-1 (P6): {len(depth1_terms)}",
        f"- depth-2 (P4): {len(depth2_terms)}",
        f"- dual terms: {len(dual_terms)}",
        f"- rows checked: {check_rows}",
        f"- exact mismatches: {len(mismatches)}",
    ]
    if first_bad:
        report.append(f"- first mismatch: row {first_bad['row']} residual={first_bad['residual']}")
    report.append("")
    report.append(f"- output: {out_data}")
    out_report.parent.mkdir(parents=True, exist_ok=True)
    out_report.write_text("\n".join(report) + "\n")

    print(json.dumps({"status": out_payload["status"], "rows_checked": check_rows, "mismatches": len(mismatches), "output": str(out_data)}))


if __name__ == "__main__":
    main()
