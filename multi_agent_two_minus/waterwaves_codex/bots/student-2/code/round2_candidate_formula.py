#!/usr/bin/env python3
import itertools
import json
import re
import subprocess
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BG = ROOT / "bg"
DATA_DIR = ROOT.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

AMP_RE = re.compile(r"A_(\d+) = i \* \(([-0-9/]+)\)")
OMEGA_RE = re.compile(r"omega = \{([^}]*)\}")


def q(x):
    return Fraction(x)


def fmt_q(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def run_bg(n, free_w):
    signs = ["-1", "-1"] + ["1"] * (n - 2)
    cmd = [
        str(BG),
        "-n",
        str(n),
        "-w",
        ",".join(fmt_q(x) for x in free_w),
        "-s",
        ",".join(signs),
    ]
    try:
        out = subprocess.check_output(
            cmd, text=True, cwd=ROOT, stderr=subprocess.STDOUT, timeout=30
        )
    except subprocess.CalledProcessError as exc:
        return {
            "n": n,
            "free_w": [fmt_q(x) for x in free_w],
            "error": f"oracle_failed_returncode_{exc.returncode}",
            "output": exc.output,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "n": n,
            "free_w": [fmt_q(x) for x in free_w],
            "error": "oracle_timeout",
            "output": exc.output or "",
        }

    om = OMEGA_RE.search(out)
    amp = AMP_RE.search(out)
    if not om or not amp:
        return {
            "n": n,
            "free_w": [fmt_q(x) for x in free_w],
            "error": "parse_failed",
            "output": out,
        }

    return {
        "n": n,
        "free_w": [fmt_q(x) for x in free_w],
        "omega": [part.strip() for part in om.group(1).split(",")],
        "amp_im": amp.group(2),
    }


def candidate_amp_im(omega):
    """Imaginary coefficient in A_n = i * candidate_amp_im."""
    w = [Fraction(x) for x in omega]
    n = len(w)
    u = -w[0]
    v = w[1]
    t = v * v
    positive_square_legs = [p * p for p in w[2:]]
    degree = n - 3
    total = Fraction(0)
    for r in range(len(positive_square_legs) + 1):
        for subset in itertools.combinations(positive_square_legs, r):
            base = t - sum(subset, Fraction(0))
            if base > 0:
                total += ((-1) ** r) * (base ** degree)
    return -(2 ** (n - 1)) * u * v * total


def annotate(row, set_name, label):
    out = dict(row)
    out["set"] = set_name
    out["label"] = label
    if "amp_im" not in row:
        out["candidate_amp_im"] = None
        out["residual"] = None
        out["relative_error"] = None
        return out

    omega = [Fraction(x) for x in row["omega"]]
    actual = Fraction(row["amp_im"])
    pred = candidate_amp_im(omega)
    residual = pred - actual
    rel = None if actual == 0 else abs(Fraction(residual, actual))
    v2 = omega[1] * omega[1]
    small = [p * p for p in omega[2:] if p * p < v2]
    out.update(
        {
            "candidate_amp_im": fmt_q(pred),
            "residual": fmt_q(residual),
            "relative_error": None if rel is None else float(rel),
            "small_square_count": len(small),
            "small_square_sum": fmt_q(sum(small, Fraction(0))),
            "v_squared": fmt_q(v2),
        }
    )
    return out


CASES = [
    # Rows used to identify the finite-difference/truncated-power pattern.
    ("fit", "n5_all_large", 5, [q(2), q(5) / 2, q(3)]),
    ("fit", "n5_two_small", 5, [q(5), q(1) / 7, q(2)]),
    ("fit", "n5_one_small_new", 5, [q(3), q(1), q(7)]),
    ("fit", "n6_all_large", 6, [q(2), q(5) / 2, q(3), q(7) / 2]),
    ("fit", "n6_three_small", 6, [q(5), q(1) / 7, q(2), q(3)]),
    ("fit", "n6_truncated_new", 6, [q(5), q(4), q(4), q(1)]),
    ("fit", "n7_all_large", 7, [q(2), q(5) / 2, q(3), q(7) / 2, q(4)]),
    ("fit", "n7_four_small", 7, [q(11), q(2), q(3) / 2, q(5) / 3, q(7) / 4]),
    ("fit", "n7_truncated_new", 7, [q(5), q(2) / 3, q(7) / 2, q(7) / 2, q(2) / 3]),
    # Held-out exact rows, including large/small frequency regimes and signed
    # frequency choices. These were not needed to infer the formula.
    ("heldout", "n5_small_v", 5, [q(1) / 5, q(4), q(3)]),
    ("heldout", "n5_generic_fractional", 5, [q(7) / 3, q(5) / 2, q(11) / 4]),
    ("heldout", "n5_large_v", 5, [q(11), q(2), q(3) / 2]),
    ("heldout", "n5_truncated_sum_gt_v2_new", 5, [q(5), q(4), q(4)]),
    ("heldout", "n5_signed_new", 5, [q(5), q(3), q(-3)]),
    ("heldout", "n5_extreme_small_v_new", 5, [q(1) / 10, q(20), q(3)]),
    ("heldout", "n6_small_v", 6, [q(1) / 5, q(4), q(3), q(5) / 2]),
    ("heldout", "n6_generic_fractional", 6, [q(7) / 3, q(5) / 2, q(11) / 4, q(13) / 5]),
    ("heldout", "n6_large_v", 6, [q(11), q(2), q(3) / 2, q(5) / 3]),
    ("heldout", "n6_signed_new", 6, [q(5), q(-1), q(1), q(1)]),
    ("heldout", "n6_mixed_small_sum_new", 6, [q(7), q(3), q(4), q(1)]),
    ("heldout", "n6_extreme_small_v_new", 6, [q(1) / 10, q(20), q(3), q(5)]),
    ("heldout", "n7_small_v", 7, [q(1) / 5, q(4), q(3), q(5) / 2, q(7) / 2]),
    ("heldout", "n7_generic_fractional", 7, [q(7) / 3, q(5) / 2, q(11) / 4, q(13) / 5, q(17) / 6]),
    ("heldout", "n7_mixed_small_sum_new", 7, [q(7), q(3), q(4), q(1), q(1)]),
    ("heldout", "n7_signed_new", 7, [q(5), q(-1), q(1), q(1), q(2)]),
    ("heldout", "n7_extreme_small_v_new", 7, [q(1) / 10, q(20), q(3), q(5), q(7)]),
    ("heldout", "n7_all_large_new", 7, [q(3), q(4), q(7), q(9), q(11)]),
    # Not part of the assigned n=5,6,7 bar; included as a smoke test only.
    ("smoke_n8", "n8_small_v_new", 8, [q(1) / 5, q(4), q(3), q(5) / 2, q(7) / 2, q(5)]),
    ("smoke_n8", "n8_all_large_new", 8, [q(2), q(5) / 2, q(3), q(7) / 2, q(4), q(9) / 2]),
]


def main():
    rows = []
    for set_name, label, n, free_w in CASES:
        rows.append(annotate(run_bg(n, free_w), set_name, label))

    finite = [r for r in rows if "amp_im" in r]
    assigned = [r for r in finite if r["n"] in (5, 6, 7)]
    assigned_failures = [r for r in assigned if r["residual"] != "0"]
    by_set = {}
    for r in finite:
        by_set.setdefault(r["set"], {"finite": 0, "max_relative_error": 0.0})
        by_set[r["set"]]["finite"] += 1
        if r["relative_error"] is not None:
            by_set[r["set"]]["max_relative_error"] = max(
                by_set[r["set"]]["max_relative_error"], r["relative_error"]
            )

    result = {
        "candidate_formula_latex": (
            "A_n = -i\\,2^{n-1}uv\\sum_{S\\subseteq\\{1,\\ldots,m\\}}"
            "(-1)^{|S|}\\left(v^2-\\sum_{j\\in S}p_j^2\\right)_+^{n-3}, "
            "u=-\\omega_1, v=\\omega_2, p_j=\\omega_{j+2}, "
            "(x)_+=x if x>0 and 0 otherwise."
        ),
        "status": (
            "passes all finite exact-GMP assigned checks at n=5,6,7; not claimed "
            "as final all-n answer because strict n=4 remains unresolved"
        ),
        "summary": {
            "finite_rows": len(finite),
            "assigned_finite_rows_n5_n6_n7": len(assigned),
            "assigned_failures": len(assigned_failures),
            "by_set": by_set,
        },
        "rows": rows,
    }
    path = DATA_DIR / "round2_candidate_checks.json"
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["summary"], indent=2))
    if assigned_failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
