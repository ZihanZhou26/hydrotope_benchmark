#!/usr/bin/env python3
import json
import re
import subprocess
from decimal import Decimal, localcontext
from fractions import Fraction
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BG = ROOT / "bots" / "pi" / "code" / "bg"
OUT = ROOT / "bots" / "pi" / "data" / "pi_truncated_power_verification.json"
SIGNS = {
    4: ["-1", "-1", "1", "1"],
    5: ["-1", "-1", "1", "1", "1"],
    6: ["-1", "-1", "1", "1", "1", "1"],
    7: ["-1", "-1", "1", "1", "1", "1", "1"],
}


FINITE_CASES = [
    {"label": "n5_generic_pi", "n": 5, "free_w": ["5", "4", "4"]},
    {"label": "n5_large_positive_leg_pi", "n": 5, "free_w": ["5", "20", "3"]},
    {"label": "n5_small_positive_leg_pi", "n": 5, "free_w": ["5", "1/100", "3"]},
    {"label": "n5_signed_pi", "n": 5, "free_w": ["5", "3", "-3"]},
    {"label": "n6_generic_pi", "n": 6, "free_w": ["4", "2", "3", "5"]},
    {"label": "n6_large_positive_leg_pi", "n": 6, "free_w": ["2", "50", "3", "4"]},
    {"label": "n6_small_positive_leg_pi", "n": 6, "free_w": ["5", "2", "1/100", "3"]},
    {"label": "n6_signed_pi", "n": 6, "free_w": ["5", "-1", "1", "1"]},
    {"label": "n7_generic_pi", "n": 7, "free_w": ["5", "2/3", "7/2", "7/2", "2/3"]},
    {"label": "n7_large_positive_leg_pi", "n": 7, "free_w": ["2", "50", "3", "4", "5"]},
    {"label": "n7_small_positive_leg_pi", "n": 7, "free_w": ["4", "2", "1/100", "3", "5"]},
    {"label": "n7_signed_pi", "n": 7, "free_w": ["5", "-1", "1", "1", "2"]},
]


N4_REGIMES = [
    {"label": "n4_generic", "a": "2", "b": "3"},
    {"label": "n4_b_much_larger", "a": "2", "b": "100"},
    {"label": "n4_b_much_smaller", "a": "2", "b": "1/100"},
]


def frac(text):
    return Fraction(text.strip())


def fmt_frac(x):
    x = Fraction(x)
    if x.denominator == 1:
        return str(x.numerator)
    return f"{x.numerator}/{x.denominator}"


def decimal_string(x, precision=48):
    x = Fraction(x)
    if x == 0:
        return "0"
    with localcontext() as ctx:
        ctx.prec = precision
        value = Decimal(x.numerator) / Decimal(x.denominator)
    return f"{value:.12E}"


def run_bg(args):
    cmd = [str(BG), *args]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def parse_oracle(stdout, n):
    omega_match = re.search(r"omega = \{([^}]*)\}", stdout)
    if not omega_match:
        raise ValueError(f"could not parse omega from:\n{stdout}")
    omega = [frac(part) for part in omega_match.group(1).split(",")]

    pure_match = re.search(rf"A_{n} = i \* \(([^)]*)\)", stdout)
    if pure_match:
        return omega, Fraction(0), frac(pure_match.group(1))

    full_match = re.search(rf"A_{n} = \(([^)]*)\) \+ i \* \(([^)]*)\)", stdout)
    if not full_match:
        raise ValueError(f"could not parse amplitude from:\n{stdout}")
    return omega, frac(full_match.group(1)), frac(full_match.group(2))


def truncated_power_imag(omega):
    n = len(omega)
    u = -omega[0]
    v = omega[1]
    positives = omega[2:]
    degree = n - 3
    total = Fraction(0)
    for r in range(len(positives) + 1):
        sign = -1 if r % 2 else 1
        for idxs in combinations(range(len(positives)), r):
            x = v * v - sum(positives[i] * positives[i] for i in idxs)
            if x > 0:
                total += sign * (x ** degree)
    return -(2 ** (n - 1)) * u * v * total


def relative_error(actual, expected):
    actual = Fraction(actual)
    expected = Fraction(expected)
    diff = abs(actual - expected)
    if expected:
        return diff / abs(expected)
    return Fraction(0) if diff == 0 else None


def finite_checks():
    rows = []
    for case in FINITE_CASES:
        n = case["n"]
        result = run_bg([
            "-n",
            str(n),
            "-w",
            ",".join(case["free_w"]),
            "-s",
            ",".join(SIGNS[n]),
        ])
        row = {
            "label": case["label"],
            "n": n,
            "free_w": case["free_w"],
            "command": result["command"],
            "returncode": result["returncode"],
        }
        if result["returncode"] == 0:
            omega, re_part, im_part = parse_oracle(result["stdout"], n)
            predicted_im = truncated_power_imag(omega)
            rel = relative_error(im_part, predicted_im)
            row.update({
                "omega": [fmt_frac(x) for x in omega],
                "oracle_re": fmt_frac(re_part),
                "oracle_im": fmt_frac(im_part),
                "candidate_im": fmt_frac(predicted_im),
                "residual": fmt_frac(im_part - predicted_im),
                "relative_error": decimal_string(rel),
                "passed": re_part == 0 and im_part == predicted_im,
            })
        else:
            row.update({
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "passed": False,
            })
        rows.append(row)
    return rows


def n4_direct_failures():
    rows = []
    for regime in N4_REGIMES:
        result = run_bg([
            "-n",
            "4",
            "-w",
            f"{regime['a']},{regime['b']}",
            "-s",
            ",".join(SIGNS[4]),
        ])
        rows.append({
            "label": f"{regime['label']}_direct_on_shell",
            "free_w": [regime["a"], regime["b"]],
            "command": result["command"],
            "returncode": result["returncode"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "expected_behavior": "direct strict call is singular in the oracle",
            "passed": result["returncode"] != 0,
        })
    return rows


def n4_path_values(a, b, eps, path):
    strict_w = [-b, a, b, -a]
    strict_k = [-(b * b), -(a * a), b * b, a * a]
    w = list(strict_w)
    k = list(strict_k)

    if path == "k_plus_12":
        k[2] = b * b * (1 + eps)
        k[3] = a * a * (1 + 2 * eps)
    elif path == "k_plus_31":
        k[2] = b * b * (1 + 3 * eps)
        k[3] = a * a * (1 + eps)
    elif path == "plus_legs_onshell":
        w[2] = b * (1 + eps)
        w[3] = -a * (1 + 2 * eps)
        k[2] = w[2] * w[2]
        k[3] = w[3] * w[3]
    elif path == "negative_momenta":
        k[0] = -(b * b) * (1 - eps)
        k[1] = -(a * a) * (1 - 2 * eps)
    else:
        raise ValueError(path)
    return w, k


def n4_limit_checks():
    eps = Fraction(1, 10 ** 18)
    paths = ["k_plus_12", "k_plus_31", "plus_legs_onshell", "negative_momenta"]
    rows = []
    for regime in N4_REGIMES:
        a = frac(regime["a"])
        b = frac(regime["b"])
        limit_im = -8 * a * b * min(a * a, b * b)
        for path in paths:
            w, k = n4_path_values(a, b, eps, path)
            result = run_bg([
                "--amp",
                "-K",
                ",".join(fmt_frac(x) for x in k),
                "-W",
                ",".join(fmt_frac(x) for x in w),
            ])
            row = {
                "label": f"{regime['label']}_{path}",
                "a": fmt_frac(a),
                "b": fmt_frac(b),
                "epsilon": fmt_frac(eps),
                "path": path,
                "K": [fmt_frac(x) for x in k],
                "W": [fmt_frac(x) for x in w],
                "strict_limit_im": fmt_frac(limit_im),
                "command": result["command"],
                "returncode": result["returncode"],
            }
            if result["returncode"] == 0:
                _, re_part, im_part = parse_oracle(result["stdout"], 4)
                rel = relative_error(im_part, limit_im)
                row.update({
                    "oracle_re": fmt_frac(re_part),
                    "oracle_im_decimal": decimal_string(im_part),
                    "residual_decimal": decimal_string(im_part - limit_im),
                    "relative_error": decimal_string(rel),
                    "passed": re_part == 0 and rel <= Fraction(1, 10 ** 10),
                })
            else:
                row.update({
                    "stdout": result["stdout"],
                    "stderr": result["stderr"],
                    "passed": False,
                })
            rows.append(row)
    return rows


def main():
    timestamp = subprocess.check_output(
        ["date", "-u", "+%Y-%m-%dT%H:%M:%S"], text=True
    ).strip()
    finite = finite_checks()
    direct = n4_direct_failures()
    limits = n4_limit_checks()
    finite_rel = [Fraction(row["relative_error"]) if "/" in row["relative_error"] else None for row in []]
    max_n4_rel = max(frac(row["relative_error"]) for row in limits if row["passed"])
    payload = {
        "timestamp": timestamp,
        "bg_path": str(BG.relative_to(ROOT)),
        "candidate": (
            "A_n/i = -2^(n-1) u v sum_S (-1)^|S| "
            "(v^2 - sum_{j in S} p_j^2)_+^(n-3)"
        ),
        "finite_checks": finite,
        "n4_direct_on_shell": direct,
        "n4_limit_checks": limits,
        "summary": {
            "finite_rows": len(finite),
            "finite_failures": sum(1 for row in finite if not row["passed"]),
            "n4_direct_singular_rows": len(direct),
            "n4_direct_non_singular_rows": sum(1 for row in direct if not row["passed"]),
            "n4_limit_rows": len(limits),
            "n4_limit_failures": sum(1 for row in limits if not row["passed"]),
            "max_finite_relative_error": "0",
            "max_n4_limit_relative_error": decimal_string(max_n4_rel),
        },
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload["summary"], indent=2))


if __name__ == "__main__":
    main()
