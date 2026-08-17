#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path


getcontext().prec = 60

ROOT = Path(__file__).resolve().parents[3]
BOT_DIR = ROOT / "bots" / "student-1"
BG = BOT_DIR / "code" / "bg"
OUT_JSON = BOT_DIR / "data" / "n4_limit_probes_round2.json"
OUT_MD = BOT_DIR / "data" / "n4_limit_probes_round2.md"


CASES = [
    {
        "case_id": "s1_n4_lim_generic",
        "regime": "generic",
        "a": Fraction(2),
        "b": Fraction(3),
    },
    {
        "case_id": "s1_n4_lim_large_b",
        "regime": "$b\\gg a$",
        "a": Fraction(2),
        "b": Fraction(100),
    },
    {
        "case_id": "s1_n4_lim_small_b",
        "regime": "$b\\ll a$",
        "a": Fraction(2),
        "b": Fraction(1, 100),
    },
]

EPSILONS = [Fraction(1, 10**p) for p in [1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18]]


def fmt_fraction(x: Fraction) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def decimal_str(x: Fraction, digits: int = 14) -> str:
    value = Decimal(x.numerator) / Decimal(x.denominator)
    return f"{value:.{digits}E}"


def decimal_ratio(num: Fraction, den: Fraction, digits: int = 14) -> str:
    value = (Decimal(num.numerator) / Decimal(num.denominator)) / (Decimal(den.numerator) / Decimal(den.denominator))
    return f"{value:.{digits}E}"


def strict_kinematics(a: Fraction, b: Fraction) -> tuple[list[Fraction], list[Fraction]]:
    w = [-b, a, b, -a]
    k = [-b * b, -a * a, b * b, a * a]
    return k, w


def conjectured_limit_im(a: Fraction, b: Fraction) -> Fraction:
    return -8 * a * b * min(a * a, b * b)


def path_k_plus_12(a: Fraction, b: Fraction, eps: Fraction) -> tuple[list[Fraction], list[Fraction], str]:
    k, w = strict_kinematics(a, b)
    k[2] = b * b * (1 + eps)
    k[3] = a * a * (1 + 2 * eps)
    return k, w, "$K_3=b^2(1+\\epsilon)$, $K_4=a^2(1+2\\epsilon)$; all $\\omega_i$ fixed"


def path_k_plus_31(a: Fraction, b: Fraction, eps: Fraction) -> tuple[list[Fraction], list[Fraction], str]:
    k, w = strict_kinematics(a, b)
    k[2] = b * b * (1 + 3 * eps)
    k[3] = a * a * (1 + eps)
    return k, w, "$K_3=b^2(1+3\\epsilon)$, $K_4=a^2(1+\\epsilon)$; all $\\omega_i$ fixed"


def path_plus_legs_onshell(a: Fraction, b: Fraction, eps: Fraction) -> tuple[list[Fraction], list[Fraction], str]:
    k, w = strict_kinematics(a, b)
    w[2] = b * (1 + eps)
    w[3] = -a * (1 + 2 * eps)
    k[2] = w[2] * w[2]
    k[3] = w[3] * w[3]
    return k, w, "$\\omega_3=b(1+\\epsilon)$, $\\omega_4=-a(1+2\\epsilon)$ with plus-leg dispersion"


def path_negative_momenta(a: Fraction, b: Fraction, eps: Fraction) -> tuple[list[Fraction], list[Fraction], str]:
    k, w = strict_kinematics(a, b)
    k[0] = -b * b * (1 - eps)
    k[1] = -a * a * (1 - 2 * eps)
    return k, w, "$K_1=-b^2(1-\\epsilon)$, $K_2=-a^2(1-2\\epsilon)$; all $\\omega_i$ fixed"


PATHS = [
    ("k_plus_12", path_k_plus_12),
    ("k_plus_31", path_k_plus_31),
    ("plus_legs_onshell", path_plus_legs_onshell),
    ("negative_momenta", path_negative_momenta),
]


def run_raw_amp(k_values: list[Fraction], w_values: list[Fraction]) -> dict[str, object]:
    cmd = [
        str(BG),
        "--amp",
        "-K",
        ",".join(fmt_fraction(x) for x in k_values),
        "-W",
        ",".join(fmt_fraction(x) for x in w_values),
    ]
    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    result: dict[str, object] = {
        "command": " ".join(cmd),
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }
    if completed.returncode != 0:
        return result
    re_im = re.search(r"A_4 = \(([^)]*)\) \+ i \* \(([^)]*)\)", completed.stdout)
    only_im = re.search(r"A_4 = i \* \(([^)]*)\)", completed.stdout)
    if re_im:
        result["amplitude_re"] = re_im.group(1).strip()
        result["amplitude_im"] = re_im.group(2).strip()
    elif only_im:
        result["amplitude_re"] = "0"
        result["amplitude_im"] = only_im.group(1).strip()
    return result


def run_strict_status(a: Fraction, b: Fraction) -> dict[str, object]:
    cmd = [
        str(BG),
        "-n",
        "4",
        "-w",
        f"{fmt_fraction(a)},{fmt_fraction(b)}",
        "-s",
        "-1,-1,1,1",
    ]
    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "command": " ".join(cmd),
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def summarize_limit(rows: list[dict[str, object]], target_im: Fraction) -> dict[str, object]:
    finite = [r for r in rows if r.get("returncode") == 0 and "amplitude_im" in r]
    if not finite:
        return {"status": "no_finite_rows"}
    values = [Fraction(str(r["amplitude_im"])) for r in finite]
    last = values[-1]
    prev = values[-2] if len(values) >= 2 else last
    delta_last_prev = last - prev
    last_minus_target = last - target_im
    rel_denom = abs(target_im) if target_im != 0 else Fraction(1)
    return {
        "last_epsilon": finite[-1]["epsilon"],
        "last_im": fmt_fraction(last),
        "last_im_decimal": decimal_str(last, 18),
        "previous_im": fmt_fraction(prev),
        "previous_im_decimal": decimal_str(prev, 18),
        "last_minus_previous": fmt_fraction(delta_last_prev),
        "last_minus_previous_decimal": decimal_str(delta_last_prev, 18),
        "conjectured_limit_im": fmt_fraction(target_im),
        "conjectured_limit_im_decimal": decimal_str(target_im, 18),
        "last_minus_conjectured_limit": fmt_fraction(last_minus_target),
        "last_minus_conjectured_limit_decimal": decimal_str(last_minus_target, 18),
        "relative_last_minus_conjectured_limit_decimal": decimal_ratio(abs(last_minus_target), rel_denom, 18),
    }


def main() -> None:
    records: list[dict[str, object]] = []
    for case in CASES:
        a = Fraction(case["a"])
        b = Fraction(case["b"])
        strict_k, strict_w = strict_kinematics(a, b)
        target_im = conjectured_limit_im(a, b)
        case_record: dict[str, object] = {
            "case_id": case["case_id"],
            "regime": case["regime"],
            "a": fmt_fraction(a),
            "b": fmt_fraction(b),
            "conjectured_limit": "$A_4=-8i\\,a b\\,\\min(a^2,b^2)$",
            "conjectured_limit_im": fmt_fraction(target_im),
            "conjectured_limit_im_decimal": decimal_str(target_im, 18),
            "strict_omega": [fmt_fraction(x) for x in strict_w],
            "strict_K": [fmt_fraction(x) for x in strict_k],
            "zero_pairs": [
                {
                    "legs": [1, 3],
                    "omega_sum": fmt_fraction(strict_w[0] + strict_w[2]),
                    "K_sum": fmt_fraction(strict_k[0] + strict_k[2]),
                    "role": "zero internal momentum sum visible to the vertex kernel",
                },
                {
                    "legs": [2, 4],
                    "omega_sum": fmt_fraction(strict_w[1] + strict_w[3]),
                    "K_sum": fmt_fraction(strict_k[1] + strict_k[3]),
                    "role": "zero rest-side BG subcurrent propagator",
                },
            ],
            "strict_on_shell_status": run_strict_status(a, b),
            "paths": [],
        }
        for path_id, path_fn in PATHS:
            path_rows: list[dict[str, object]] = []
            description = ""
            for eps in EPSILONS:
                k_values, w_values, description = path_fn(a, b, eps)
                row = run_raw_amp(k_values, w_values)
                row.update(
                    {
                        "epsilon": fmt_fraction(eps),
                        "K": [fmt_fraction(x) for x in k_values],
                        "W": [fmt_fraction(x) for x in w_values],
                    }
                )
                if row.get("returncode") == 0 and "amplitude_im" in row:
                    row["amplitude_im_decimal"] = decimal_str(Fraction(str(row["amplitude_im"])), 18)
                path_rows.append(row)
            case_record["paths"].append(
                {
                    "path_id": path_id,
                    "description": description,
                    "rows": path_rows,
                    "limit_summary": summarize_limit(path_rows, target_im),
                }
            )
        records.append(case_record)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"records": records}, indent=2) + "\n")

    lines: list[str] = []
    lines.append("# Round 2 $n=4$ Off-Shell Limit Probes")
    lines.append("")
    lines.append("All entries were generated with the private exact-GMP oracle at `bots/student-1/code/bg` in raw `--amp` mode.")
    lines.append("Strict two-minus kinematics are written as $\\omega=(-b,a,b,-a)$ and $K=(-b^2,-a^2,b^2,a^2)$. Full exact rational outputs are in `n4_limit_probes_round2.json`.")
    lines.append("")
    for record in records:
        lines.append(f"## {record['case_id']}: {record['regime']}, $a={record['a']}$, $b={record['b']}$")
        lines.append("")
        lines.append(f"- strict $\\omega$: `{record['strict_omega']}`")
        lines.append(f"- strict $K$: `{record['strict_K']}`")
        lines.append(f"- conjectured limiting value: $A_4=i\\,({record['conjectured_limit_im']})$")
        status = record["strict_on_shell_status"]
        lines.append(f"- strict on-shell command return code: `{status['returncode']}`")
        lines.append("- zero pairs: $\\{1,3\\}$ has $\\omega_1+\\omega_3=K_1+K_3=0$; $\\{2,4\\}$ has $\\omega_2+\\omega_4=K_2+K_4=0$.")
        lines.append("")
        lines.append("| path | last $\\epsilon$ | previous $\\operatorname{Im} A_4$ | last $\\operatorname{Im} A_4$ | last - previous | rel. residual vs conjectured limit |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
        for path in record["paths"]:
            lim = path["limit_summary"]
            lines.append(
                "| "
                + f"`{path['path_id']}` | `{lim['last_epsilon']}` | "
                + f"{lim['previous_im_decimal']} | {lim['last_im_decimal']} | "
                + f"{lim['last_minus_previous_decimal']} | {lim['relative_last_minus_conjectured_limit_decimal']} |"
            )
        lines.append("")
        lines.append("Path definitions:")
        for path in record["paths"]:
            lines.append(f"- `{path['path_id']}`: {path['description']}.")
        lines.append("")
        lines.append("Selected convergence rows:")
        lines.append("")
        lines.append("| path | $\\epsilon$ | $\\operatorname{Im} A_4$ decimal | exact $\\operatorname{Im} A_4$ |")
        lines.append("| --- | ---: | ---: | --- |")
        for path in record["paths"]:
            for row in path["rows"]:
                if row["epsilon"] in {"1/10000", "1/100000000", "1/1000000000000", "1/1000000000000000000"}:
                    lines.append(
                        f"| `{path['path_id']}` | `{row['epsilon']}` | "
                        f"{row.get('amplitude_im_decimal', 'n/a')} | `{row.get('amplitude_im', 'n/a')}` |"
                    )
        lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
