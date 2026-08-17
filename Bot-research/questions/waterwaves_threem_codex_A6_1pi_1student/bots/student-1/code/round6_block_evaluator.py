#!/usr/bin/env python3
"""Round-6 block-wise evaluator for reconstructed 3-variable pieces."""

import argparse
import json
import re
import subprocess
from fractions import Fraction as F
from pathlib import Path

import sympy as sp

SIG = (-1, -1, -1, 1, 1, 1)

ROOT = Path(__file__).resolve().parent.parent.parent.parent
STUDENT_DIR = ROOT / "bots" / "student-1"
CODE_DIR = STUDENT_DIR / "code"
DATA_DIR = STUDENT_DIR / "data"
PIECE_DIR = DATA_DIR / "round6_pieces"
REPORT_JSON = DATA_DIR / "round6_piece_report.json"
BG_BIN = CODE_DIR / "bg_s1_r6"

X, Y, Z = sp.symbols("x y z")


def parse_fraction(text):
    return F(str(text))


def to_fraction(sym):
    if isinstance(sym, sp.Rational):
        return F(sym.p, sym.q)
    if isinstance(sym, sp.Integer):
        return F(int(sym), 1)
    return F(str(sp.simplify(sym)))


def solve_from_free(free):
    free = [F(v) for v in free]
    s = sum(free)
    if s == 0:
        raise ValueError("sum free frequencies is zero")
    ss = sum(SIG[i + 1] * free[i] * free[i] for i in range(4))
    w6 = -(SIG[0] * s * s + ss) / (2 * SIG[0] * s)
    w1 = -(s + w6)
    return (w1, free[0], free[1], free[2], free[3], w6)


def bg_h_value(omega):
    moms = [str(SIG[i] * omega[i] * omega[i]) for i in range(6)]
    cmd = [
        str(BG_BIN),
        "--amp",
        "-K",
        ",".join(moms),
        "-W",
        ",".join(str(w) for w in omega),
    ]
    p = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or "bg eval failed")
    m1 = re.search(r"A_6 = i \* \(([^)]*)\)", p.stdout)
    if m1:
        A = F(m1.group(1))
    else:
        m2 = re.search(r"A_6 = \(([^)]*)\) \+ i \* \(([^)]*)\)", p.stdout)
        if m2 and F(m2.group(1)) == 0:
            A = F(m2.group(2))
        else:
            raise RuntimeError("unexpected bg output")

    prod = F(1)
    for w in omega:
        prod *= w
    return A / prod


def load_piece_records(piece_dir, report_json):
    records = {}
    if not piece_dir.exists():
        return records
    for dpath in sorted(piece_dir.glob("piece_*_detail.json")):
        name = dpath.name
        if name.startswith("piece_") and name.endswith("_detail.json"):
            sig = name[len("piece_"):-len("_detail.json")]
        else:
            sig = name
        try:
            detail = json.loads(dpath.read_text())
        except Exception:
            continue
        points_path = Path(detail.get("point_file", piece_dir / f"piece_{sig}_points.json"))
        if points_path.exists():
            try:
                pts = json.loads(points_path.read_text()).get("points", [])
            except Exception:
                pts = []
        else:
            pts = []

        records[sig] = {
            "detail": detail,
            "points": [(parse_fraction(x), parse_fraction(y), parse_fraction(z), parse_fraction(h))
                       for x, y, z, h in pts],
        }
    return records


def piece_status_map(report_json):
    if not report_json.exists():
        return {}
    try:
        return {r["signature_hash"]: r for r in json.loads(report_json.read_text()).get("piece_reports", [])}
    except Exception:
        return {}


def evaluate_piece(detail, points, max_points=64, check_bg=False):
    status = detail.get("check", {})
    status_label = detail.get("status", "")
    raw_num = detail.get("P", "")
    raw_den = detail.get("Q", "")

    if status_label != "reconstructed" or not raw_num or not raw_den:
        return {
            "signature_hash": detail.get("signature_hash", ""),
            "status": status_label or "pending",
            "dmin": detail.get("dmin"),
            "num_expr": str(raw_num or ""),
            "den_expr": str(raw_den or ""),
            "selected_V": detail.get("selected_V", []),
            "fixed_denominator": detail.get("fixed_denominator", {}),
            "factorP": detail.get("factorP", ""),
            "factorQ": detail.get("factorQ", ""),
            "checks": {
                "piece": status,
                "piece_points_total": 0,
                "piece_points_fail": 0,
                "piece_points_max_abs": "0",
                "skipped": True,
            },
            "sample_rows": [],
        }

    P = sp.sympify(raw_num)
    Q = sp.sympify(raw_den)
    expr = sp.together(P / Q)
    num, den = expr.as_numer_denom()
    out = {
        "signature_hash": detail.get("signature_hash", ""),
        "status": detail.get("status", ""),
        "dmin": detail.get("dmin"),
        "num_expr": str(sp.expand(num)),
        "den_expr": str(sp.expand(den)),
        "selected_V": detail.get("selected_V", []),
        "fixed_denominator": detail.get("fixed_denominator", {}),
        "factorP": detail.get("factorP", ""),
        "factorQ": detail.get("factorQ", ""),
        "checks": {
            "piece": status,
        },
    }
    total = 0
    fail = 0
    max_abs = F(0)
    sample = []

    for x, y, z, h in points[:max_points]:
        xv = sp.Rational(x.numerator, x.denominator)
        yv = sp.Rational(y.numerator, y.denominator)
        zv = sp.Rational(z.numerator, z.denominator)
        hv = sp.simplify(expr.subs({X: xv, Y: yv, Z: zv}))
        h_fit = to_fraction(hv)
        target = h
        diff = h_fit - target
        total += 1
        if diff != 0:
            fail += 1
            max_abs = max(max_abs, abs(diff))
        sample.append({
            "x": str(x),
            "y": str(y),
            "z": str(z),
            "target": str(target),
            "fit": str(h_fit),
            "diff": str(diff),
        })

    bg_fail = None
    if check_bg:
        bg_checked = 0
        bg_fail = 0
        bg_max_abs = F(0)
        for x, y, z, _ in points[:max_points]:
            try:
                omega = solve_from_free((F(1), x, y, z))
            except Exception:
                continue
            if any(w == 0 for w in omega):
                continue
            try:
                h_bg = bg_h_value(omega)
            except Exception:
                continue
            xv = sp.Rational(x.numerator, x.denominator)
            yv = sp.Rational(y.numerator, y.denominator)
            zv = sp.Rational(z.numerator, z.denominator)
            hv = sp.simplify(expr.subs({X: xv, Y: yv, Z: zv}))
            h_fit = to_fraction(hv)
            d = h_fit - h_bg
            bg_checked += 1
            if d != 0:
                bg_fail += 1
                bg_max_abs = max(bg_max_abs, abs(d))
            sample.append({
                "bg_x": str(x),
                "bg_y": str(y),
                "bg_z": str(z),
                "bg_target": str(h_bg),
                "bg_fit": str(h_fit),
                "bg_diff": str(d),
            })
        out["bg_checks"] = {"checked": bg_checked, "fail": bg_fail, "max_abs": str(bg_max_abs)}

    out["checks"]["piece_points_total"] = total
    out["checks"]["piece_points_fail"] = fail
    out["checks"]["piece_points_max_abs"] = str(max_abs)
    out["sample_rows"] = sample[: min(32, len(sample))]
    return out


def print_table(rows):
    print("| signature | status | dmin | check-ok/total | hold-bad |")
    print("|---|---|---:|---:|---:|")
    for r in rows:
        st = r["checks"]["piece"]
        ok = st.get("ok", 0) if isinstance(st, dict) else 0
        total = st.get("total", 0) if isinstance(st, dict) else 0
        hold_bad = st.get("hold_bad", 0) if isinstance(st, dict) else 0
        dmin = r.get("dmin", "NA")
        sig = r.get("signature_hash", "NA")
        print(f"| {sig} | {r.get('status', '')} | {dmin} | {ok}/{total} | {hold_bad} |")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--piece", default="", help="signature hash, or all pieces")
    p.add_argument("--mode", choices=["table", "check"], default="table")
    p.add_argument("--points", type=int, default=80)
    p.add_argument("--bg-check", action="store_true")
    p.add_argument("--piece-dir", default=str(PIECE_DIR))
    p.add_argument("--report-json", default=str(REPORT_JSON))
    p.add_argument("--out", default=str(DATA_DIR / "round6_block_evaluator.json"))
    args = p.parse_args()
    piece_dir = Path(args.piece_dir)
    report_json = Path(args.report_json)

    records = load_piece_records(piece_dir, report_json)
    status_map = piece_status_map(report_json)
    rows = []
    if args.piece:
        picks = {args.piece: records.get(args.piece)} if args.piece in records else {}
    else:
        picks = records
    if not picks:
        raise SystemExit("no piece detail files found")

    for sig, item in sorted(picks.items()):
        if "status" not in item["detail"]:
            item["detail"]["status"] = status_map.get(sig, {}).get("status", "")
            item["detail"]["signature_hash"] = sig
        rows.append(evaluate_piece(item["detail"], item["points"], max_points=args.points, check_bg=args.bg_check))

    if args.mode == "table":
        print_table(rows)
    else:
        for row in rows:
            print(f"\n# signature {row['signature_hash']}")
            print(f"P = {row['num_expr']}")
            print(f"Q = {row['den_expr']}")
            print(f"check total={row['checks']['piece_points_total']} fail={row['checks']['piece_points_fail']} maxabs={row['checks']['piece_points_max_abs']}")
            if "bg_checks" in row:
                print(f"bg check: {row['bg_checks']}")
            if args.points:
                for it in row["sample_rows"][:min(6, len(row["sample_rows"]))]:
                    print("  ", it)

    Path(args.out).write_text(json.dumps({"mode": args.mode, "points": args.points, "bg_check": args.bg_check, "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
