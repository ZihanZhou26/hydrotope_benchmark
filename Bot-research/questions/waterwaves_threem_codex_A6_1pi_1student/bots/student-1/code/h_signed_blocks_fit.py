#!/usr/bin/env python3
"""Signed-block-oriented denominator scan fit scaffold.

This is a lightweight, deterministic fitting script intended for post-scan
numerator reconstruction checks.
"""

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import common

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
QUESTION_DIR = ROOT.parent.parent
BG_BIN = ROOT / "code" / "bg_round4"

PAIR_FACTORS = [(i, j) for i in range(3) for j in range(3)]
SIG_FULL = common.SIG_FULL


def frac(v):
    if isinstance(v, Fraction):
        return v
    return common.parse_fraction(v)


def frac_to_str(v: Fraction) -> str:
    return common.frac_to_str(v)


def _pair_factors(omega: Sequence[Fraction]) -> Tuple[Fraction, ...]:
    a = [omega[0] ** 2, omega[1] ** 2, omega[2] ** 2]
    b = [omega[3] ** 2, omega[4] ** 2, omega[5] ** 2]
    out = []
    for i in range(3):
        for j in range(3):
            out.append(a[i] + b[j])
    return tuple(out)


def _mask_product(pf: Sequence[Fraction], mask: int) -> Fraction:
    val = Fraction(1)
    for k in range(len(PAIR_FACTORS)):
        if (mask >> k) & 1:
            val *= pf[k]
    return val


def _build_data_rows(path: Path) -> List[Dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            d = json.loads(ln)
            d["omega"] = [frac(x) for x in d["omega"]]
            d["free_w"] = [frac(x) for x in d["free_w"]]
            d["A_im"] = frac(d.get("A_im", "0"))
            d["A_re"] = frac(d.get("A_re", "0"))
            prod = Fraction(1)
            for w in d["omega"]:
                prod *= w
            if prod == 0:
                continue
            d["H"] = d["A_im"] / prod
            d["pair_factors"] = _pair_factors(d["omega"])
            d["signature"] = d["wall_signature_raw"]
            rows.append(d)
    return rows


def _load_scan(report_path: Path) -> Dict:
    if not report_path.exists():
        return {}
    with report_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _iter_monomials(nvar: int, max_degree: int) -> List[Tuple[int, ...]]:
    out: List[Tuple[int, ...]] = []
    exps = [0] * nvar

    def rec(i: int, rem: int) -> None:
        if i == nvar - 1:
            exps[i] = rem
            out.append(tuple(exps))
            return
        for k in range(rem + 1):
            exps[i] = k
            rec(i + 1, rem - k)

    for d in range(max_degree + 1):
        rec(0, d)

    return out


def _eval_monomial(exp: Tuple[int, ...], omega: Sequence[Fraction]) -> Fraction:
    out = Fraction(1)
    for e, w in zip(exp, omega):
        if e:
            out *= w ** e
    return out


def _gauss_solve_exact(A: List[List[Fraction]], b: List[Fraction]) -> List[Fraction]:
    n = len(A)
    if n == 0:
        return []
    if any(len(row) != n for row in A) or len(b) != n:
        raise ValueError("non-square")

    mat = [row[:] + [rhs] for row, rhs in zip(A, b)]

    row = 0
    for col in range(n):
        pivot = row
        while pivot < n and mat[pivot][col] == 0:
            pivot += 1
        if pivot == n:
            raise ValueError("singular")
        if pivot != row:
            mat[row], mat[pivot] = mat[pivot], mat[row]

        inv = Fraction(1, 1) / mat[row][col]
        mat[row] = [x * inv for x in mat[row]]

        for rr in range(n):
            if rr == row:
                continue
            factor = mat[rr][col]
            if factor == 0:
                continue
            mat[rr] = [a - factor * b for a, b in zip(mat[rr], mat[row])]

        row += 1

    x = [Fraction(0)] * n
    for rr in range(n):
        pivot = None
        for cc in range(n):
            if mat[rr][cc] != 0:
                pivot = cc
                break
        if pivot is None:
            if mat[rr][n] != 0:
                raise ValueError("inconsistent")
            continue
        x[pivot] = mat[rr][n]

    return x


def _fit_for_mask(rows: List[Dict], mask: int, max_degree: int, min_train: int, max_fail: int) -> Dict[str, object]:
    pf_rows = []
    for row in rows:
        d = 2 + 2 * (mask.bit_count() if hasattr(int, "bit_count") else bin(mask).count("1"))
        q = _mask_product(row["pair_factors"], mask)
        s = row["free_w"][0] + row["free_w"][1] + row["free_w"][2] + row["free_w"][3]
        if q == 0 or s == 0:
            continue
        y = row["H"] * q * (s ** d)
        pf_rows.append((row["omega"], y, row.get("split", "train")))

    if not pf_rows:
        return {"status": "empty", "mask": mask}

    train_rows = [r for r in pf_rows if r[2] == "train"]
    hold_rows = [r for r in pf_rows if r[2] != "train"]
    if len(train_rows) < 6:
        train_rows = pf_rows[: max(min_train, len(pf_rows) // 2)]
        hold_rows = pf_rows[max(min_train, len(pf_rows) // 2):]

    if len(train_rows) < min_train:
        return {"status": "insufficient_train", "train": len(train_rows)}

    # hard thresholds: feature count can never exceed train rows for exact solve.
    for deg in range(1, max_degree + 1):
        monoms = _iter_monomials(6, deg)
        if len(monoms) > len(train_rows):
            continue

        X = []
        yv = []
        for omega, y, _ in train_rows[: len(monoms)]:
            X.append([_eval_monomial(e, omega) for e in monoms])
            yv.append(y)

        try:
            coeff = _gauss_solve_exact(X, yv)
        except Exception:
            continue

        bad = []
        for omega, y, split in hold_rows:
            pred = sum(c * _eval_monomial(e, omega) for c, e in zip(coeff, monoms))
            if pred != y:
                bad.append(split)
                if len(bad) > max_fail:
                    break

        if len(bad) <= max_fail:
            return {
                "status": "pass",
                "mask": mask,
                "degree": deg,
                "feature_count": len(monoms),
                "train_rows": len(train_rows),
                "holdout_rows": len(hold_rows),
                "holdout_fail": len(bad),
                "residual": [frac_to_str(v) for v in coeff[: min(12, len(coeff))]],
            }

    return {
        "status": "no_pass",
        "mask": mask,
        "train_rows": len(train_rows),
        "holdout_rows": len(hold_rows),
    }


def run_scan(report_path: Path, oracle_path: Path, max_degree: int, min_train: int, max_fail: int, max_masks: int) -> Dict[str, object]:
    rows = _build_data_rows(oracle_path)
    if not rows:
        raise RuntimeError(f"no rows in {oracle_path}")

    scan = _load_scan(report_path)
    cand_masks: List[int] = []
    if scan:
        by_mask = {str(r["mask"]): r for r in scan.get("mask_results", [])}
        for k, v in sorted(by_mask.items(), key=lambda kv: int(kv[0])):
            if v.get("pass"):
                cand_masks.append(int(k))
    if not cand_masks and "full_mask" in scan:
        cand_masks = [int(scan["full_mask"]["mask"])]
    if not cand_masks:
        cand_masks = [0, (1 << 6) - 1]
    cand_masks = cand_masks[: max_masks]

    outcomes = []
    for m in cand_masks:
        outcomes.append(_fit_for_mask(rows, m, max_degree=max_degree, min_train=min_train, max_fail=max_fail))
        if outcomes[-1]["status"] == "pass":
            # keep early-stop behavior per-mask and stop whole scan once one hit passes.
            outcomes[-1]["early_stop"] = True
            break

    out = {
        "timestamp": __import__("subprocess").check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%S"], universal_newlines=True).strip(),
        "oracle_path": str(oracle_path),
        "scan_path": str(report_path),
        "max_degree": max_degree,
        "min_train": min_train,
        "max_fail": max_fail,
        "max_masks": max_masks,
        "outcomes": outcomes,
    }

    return out


def write_reports(payload: Dict[str, object], out_path: Path) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)

    md = [
        "# Signed-block fit scaffold",
        f"timestamp: {payload['timestamp']}",
        f"scan: {payload['scan_path']}",
        f"oracle: {payload['oracle_path']}",
        f"max degree: {payload['max_degree']}",
        "",
        "## Outcomes",
    ]

    for out in payload["outcomes"]:
        if out.get("status") == "pass":
            md.append(f"- mask={out['mask']} status=PASS degree={out['degree']} feature_count={out['feature_count']} holdout_fail={out['holdout_fail']}")
        else:
            md.append(f"- mask={out['mask']} status={out['status']}")

    with (DATA_DIR / "h_signed_blocks_fit.md").open("w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--scan-json", default=str(DATA_DIR / "h_mask_scan_lean.json"))
    p.add_argument("--oracle", default=str(DATA_DIR / "fresh_structure_oracle_v2.jsonl"))
    p.add_argument("--max-degree", type=int, default=8)
    p.add_argument("--min-train", type=int, default=18)
    p.add_argument("--max-fail", type=int, default=0)
    p.add_argument("--max-masks", type=int, default=8)
    p.add_argument("--out", default=str(DATA_DIR / "h_signed_blocks_fit.json"))
    return p.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_scan(
        report_path=Path(args.scan_json),
        oracle_path=Path(args.oracle),
        max_degree=args.max_degree,
        min_train=args.min_train,
        max_fail=args.max_fail,
        max_masks=args.max_masks,
    )
    write_reports(payload, Path(args.out))


if __name__ == "__main__":
    main()
