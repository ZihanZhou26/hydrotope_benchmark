#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from fractions import Fraction
from pathlib import Path
from subprocess import CalledProcessError


ROOT = Path(__file__).resolve().parents[3]
BOT_DIR = ROOT / "bots" / "student-1"
BG = BOT_DIR / "code" / "bg"
OUT_JSON = BOT_DIR / "data" / "oracle_table_round1.json"
OUT_MD = BOT_DIR / "data" / "oracle_table_round1.md"


CASES = [
    {
        "case_id": "s1_n4_generic",
        "n": 4,
        "regime": "generic",
        "free_w": ["2", "3"],
        "large_or_small_leg": None,
    },
    {
        "case_id": "s1_n4_large_plus",
        "n": 4,
        "regime": "one plus-sign free leg much larger",
        "free_w": ["2", "100"],
        "large_or_small_leg": "leg 3",
    },
    {
        "case_id": "s1_n4_small_plus",
        "n": 4,
        "regime": "one plus-sign free leg much smaller",
        "free_w": ["2", "1/100"],
        "large_or_small_leg": "leg 3",
    },
    {
        "case_id": "s1_n5_generic",
        "n": 5,
        "regime": "generic",
        "free_w": ["2", "5/2", "3"],
        "large_or_small_leg": None,
    },
    {
        "case_id": "s1_n5_large_plus",
        "n": 5,
        "regime": "one plus-sign free leg much larger",
        "free_w": ["2", "100", "3"],
        "large_or_small_leg": "leg 3",
    },
    {
        "case_id": "s1_n5_small_plus",
        "n": 5,
        "regime": "one plus-sign free leg much smaller",
        "free_w": ["2", "1/100", "3"],
        "large_or_small_leg": "leg 3",
    },
    {
        "case_id": "s1_n6_generic",
        "n": 6,
        "regime": "generic",
        "free_w": ["2", "5/2", "3", "7/2"],
        "large_or_small_leg": None,
    },
    {
        "case_id": "s1_n6_large_plus",
        "n": 6,
        "regime": "one plus-sign free leg much larger",
        "free_w": ["2", "100", "3", "7/2"],
        "large_or_small_leg": "leg 3",
    },
    {
        "case_id": "s1_n6_small_plus",
        "n": 6,
        "regime": "one plus-sign free leg much smaller",
        "free_w": ["2", "1/100", "3", "7/2"],
        "large_or_small_leg": "leg 3",
    },
    {
        "case_id": "s1_n7_generic",
        "n": 7,
        "regime": "generic",
        "free_w": ["2", "5/2", "3", "7/2", "4"],
        "large_or_small_leg": None,
    },
    {
        "case_id": "s1_n7_large_plus",
        "n": 7,
        "regime": "one plus-sign free leg much larger",
        "free_w": ["2", "100", "3", "7/2", "4"],
        "large_or_small_leg": "leg 3",
    },
    {
        "case_id": "s1_n7_small_plus",
        "n": 7,
        "regime": "one plus-sign free leg much smaller",
        "free_w": ["2", "1/100", "3", "7/2", "4"],
        "large_or_small_leg": "leg 3",
    },
]


def signs(n: int) -> list[str]:
    return ["-1", "-1"] + ["1"] * (n - 2)


def solve_omega(n: int, free_w: list[str]) -> list[str]:
    sig = [Fraction(s) for s in signs(n)]
    free = [Fraction(w) for w in free_w]
    sum_free = sum(free, Fraction(0))
    sum_sig = sum(sig[i + 1] * free[i] * free[i] for i in range(n - 2))
    wn = -(sig[0] * sum_free * sum_free + sum_sig) / (2 * sig[0] * sum_free)
    w1 = -(sum_free + wn)
    return [fmt_fraction(w1)] + [fmt_fraction(w) for w in free] + [fmt_fraction(wn)]


def fmt_fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def run_bg(n: int, free_w: list[str], use_double: bool = False) -> str:
    cmd = [str(BG)]
    if use_double:
        cmd.append("--double")
    cmd.extend(["-n", str(n), "-w", ",".join(free_w), "-s", ",".join(signs(n))])
    return subprocess.check_output(cmd, cwd=ROOT, text=True)


def run_bg_status(n: int, free_w: list[str], use_double: bool = False) -> dict[str, object]:
    cmd = [str(BG)]
    if use_double:
        cmd.append("--double")
    cmd.extend(["-n", str(n), "-w", ",".join(free_w), "-s", ",".join(signs(n))])
    completed = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {
        "command": " ".join(cmd),
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def run_raw_amp(k_values: list[str], w_values: list[str]) -> str:
    cmd = [str(BG), "--amp", "-K", ",".join(k_values), "-W", ",".join(w_values)]
    return subprocess.check_output(cmd, cwd=ROOT, text=True)


def parse_fraction(text: str) -> Fraction:
    return Fraction(text.strip())


def parse_exact(output: str, n: int) -> dict[str, object]:
    omega_match = re.search(r"omega = \{([^}]*)\}", output)
    if not omega_match:
        raise ValueError(output)
    omega = [x.strip() for x in omega_match.group(1).split(",")]
    imag_match = re.search(rf"A_{n} = i \* \(([^)]*)\)", output)
    if imag_match:
        return {"omega": omega, "amplitude_re": "0", "amplitude_im": imag_match.group(1).strip()}
    full_match = re.search(rf"A_{n} = \(([^)]*)\) \+ i \* \(([^)]*)\)", output)
    if not full_match:
        raise ValueError(output)
    return {
        "omega": omega,
        "amplitude_re": full_match.group(1).strip(),
        "amplitude_im": full_match.group(2).strip(),
    }


def parse_double(output: str, n: int) -> dict[str, float]:
    match = re.search(rf"A_{n} \(double\) = ([^ ]+) \+ ([^ ]+) i", output)
    if not match:
        raise ValueError(output)
    return {"amplitude_re": float(match.group(1)), "amplitude_im": float(match.group(2))}


def n4_regularized_probes(omega: list[str]) -> list[dict[str, object]]:
    w = [Fraction(x) for x in omega]
    sig = [Fraction("-1"), Fraction("-1"), Fraction("1"), Fraction("1")]
    k0 = [sig_i * w_i * w_i for sig_i, w_i in zip(sig, w)]
    probes = []
    for exp in [6, 8, 10, 12]:
        eps = Fraction(1, 10**exp)
        k = list(k0)
        k[2] = k[2] * (1 + eps)
        k[3] = k[3] * (1 + 2 * eps)
        k_str = [fmt_fraction(x) for x in k]
        out = run_raw_amp(k_str, omega)
        parsed = parse_exact(out, 4)
        im = parse_fraction(str(parsed["amplitude_im"]))
        probes.append(
            {
                "epsilon": fmt_fraction(eps),
                "path": "$K_3\\to K_3(1+\\epsilon)$, $K_4\\to K_4(1+2\\epsilon)$ with $\\omega$ fixed",
                "K": k_str,
                "W": omega,
                "amplitude_re": parsed["amplitude_re"],
                "amplitude_im": parsed["amplitude_im"],
                "numeric_im": float(im),
            }
        )
    return probes


def rel_diff(exact: Fraction, approx: float) -> float:
    exact_float = float(exact)
    scale = max(1.0, abs(exact_float))
    return abs(exact_float - approx) / scale


def main() -> None:
    records = []
    for case in CASES:
        n = int(case["n"])
        free_w = list(case["free_w"])
        solved_omega = solve_omega(n, free_w)
        if n == 4:
            exact_status = run_bg_status(n, free_w, use_double=False)
            double_status = run_bg_status(n, free_w, use_double=True)
            records.append(
                {
                    **case,
                    "signs": signs(n),
                    "command": exact_status["command"],
                    "precision_mode": "exact GMP rational",
                    "omega": solved_omega,
                    "strict_on_shell_result": {
                        "exact": exact_status,
                        "double": double_status,
                        "interpretation": "The strict resonant two-minus $n=4$ input forces zero total $(\\omega,k)$ in opposite-sign pairs; the copied oracle raises SIGFPE in exact mode and returns nan in double mode.",
                    },
                    "regularized_raw_probes": n4_regularized_probes(solved_omega),
                }
            )
            continue

        try:
            exact_raw = run_bg(n, free_w, use_double=False)
        except CalledProcessError as exc:
            raise RuntimeError(f"exact oracle failed for {case['case_id']}: {exc}") from exc
        double_raw = run_bg(n, free_w, use_double=True)
        exact = parse_exact(exact_raw, n)
        double = parse_double(double_raw, n)
        re_exact = parse_fraction(str(exact["amplitude_re"]))
        im_exact = parse_fraction(str(exact["amplitude_im"]))
        command = f"{BG} -n {n} -w {','.join(free_w)} -s {','.join(signs(n))}"
        records.append(
            {
                **case,
                "signs": signs(n),
                "command": command,
                "precision_mode": "exact GMP rational",
                "omega": exact["omega"],
                "omega_formula_check": solved_omega,
                "amplitude": {
                    "re": exact["amplitude_re"],
                    "im": exact["amplitude_im"],
                    "numeric_re": float(re_exact),
                    "numeric_im": float(im_exact),
                },
                "double_sanity_check": {
                    "command": command.replace(str(BG), f"{BG} --double"),
                    "numeric_re": double["amplitude_re"],
                    "numeric_im": double["amplitude_im"],
                    "relative_error_re": rel_diff(re_exact, double["amplitude_re"]),
                    "relative_error_im": rel_diff(im_exact, double["amplitude_im"]),
                },
                "raw_exact_output": exact_raw.strip(),
            }
        )

    payload = {
        "bot": "student-1",
        "task": "round 1 oracle data table for two-minus sector",
        "oracle_source": "bots/student-1/code/bg.cpp copied from shared bg.cpp",
        "records": records,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# Round 1 Oracle Table",
        "",
        "Private oracle build: `bots/student-1/code/bg` from copied `bg.cpp`.",
        "All primary values below use exact GMP rational mode. The final column is the relative difference between exact rational $\\operatorname{Im} A_n$ converted to double and the oracle's `--double` path.",
        "",
        "| case | $n$ | regime | free $\\omega_2,\\ldots,\\omega_{n-1}$ | signs | solved $\\omega_1,\\ldots,\\omega_n$ | $A_n$ | double rel. diff. |",
        "| --- | ---: | --- | --- | --- | --- | --- | ---: |",
    ]
    for rec in records:
        if rec["n"] == 4:
            probe = rec["regularized_raw_probes"][-1]
            lines.append(
                "| {case_id} | {n} | {regime} | `{free_w}` | `{signs}` | `{omega}` | strict on-shell oracle: exact `SIGFPE`, double `nan`; raw probe $\\epsilon={eps}$ gives $i\\,({im})$ | n/a |".format(
                    case_id=rec["case_id"],
                    n=rec["n"],
                    regime=rec["regime"],
                    free_w=",".join(rec["free_w"]),
                    signs=",".join(rec["signs"]),
                    omega=", ".join(rec["omega"]),
                    eps=probe["epsilon"],
                    im=probe["amplitude_im"],
                )
            )
        else:
            amp = rec["amplitude"]
            rel = rec["double_sanity_check"]["relative_error_im"]
            lines.append(
                "| {case_id} | {n} | {regime} | `{free_w}` | `{signs}` | `{omega}` | $i\\,({im})$ | {rel:.3e} |".format(
                    case_id=rec["case_id"],
                    n=rec["n"],
                    regime=rec["regime"],
                    free_w=",".join(rec["free_w"]),
                    signs=",".join(rec["signs"]),
                    omega=", ".join(rec["omega"]),
                    im=amp["im"],
                    rel=rel,
                )
            )
    OUT_MD.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
