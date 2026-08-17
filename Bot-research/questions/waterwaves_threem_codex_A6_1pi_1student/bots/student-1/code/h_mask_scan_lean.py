#!/usr/bin/env python3
"""Lean denominator-mask scan in the fixed three-minus chamber.

The script checks subproducts of
\(\prod (\omega_i^2+\omega_{3+j}^2)\) against the fixed-chamber oracle
`h_rational_probe_oracle.jsonl`.

For each mask `M`, it tests whether

    H * Q_M * S^(2+2|M|)

is a polynomial (degree <= 2*(2+2|M|)) along several affine lines in free space,
using modular pre-filters and exact rational holdout checks.
`H = A_im / prod(omega)`.
"""

import argparse
import json
import re
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import common

try:
    import sympy as sp
except Exception:  # pragma: no cover
    sp = None

ROOT = Path(__file__).resolve().parent.parent
CODE_DIR = ROOT / "code"
DATA_DIR = ROOT / "data"
QUESTION_DIR = ROOT.parent.parent

BG_SRC = QUESTION_DIR / "bg.cpp"
BG_SRC_COPY = CODE_DIR / "bg_round4.cpp"
BG_BIN = CODE_DIR / "bg_round4"

WALL_CATALOG = common.build_wall_catalog()
SIG_FULL = common.SIG_FULL
PAIR_FACTORS = [(i, j) for i in range(3) for j in range(3)]
PAIR_COUNT = len(PAIR_FACTORS)
ALL_MASKS = list(range(1 << PAIR_COUNT))
PRIMES = (1_000_003, 1_000_033, 1_000_037)

DEFAULT_LINE_T_RANGE = (-20, 20)
DEFAULT_LINE_STEP = 1
MIN_LINES_FOR_MASK = 6
MIN_EXACT_LINES = 2
REQUIRED_HOLDOUT = 16
MAX_K = 9
MAX_D = 2 + 2 * MAX_K
NEED_TRAIN = 2 * MAX_D + 1
NEED_TOTAL = NEED_TRAIN + REQUIRED_HOLDOUT
DEFAULT_LINES = 6

DEFAULT_LINE_DIRECTIONS = [
    (1, -2, 3, -4),
    (1, 1, -2, 2),
    (2, -1, -2, 1),
    (-3, 2, 1, -1),
    (1, -1, 2, -2),
    (2, 2, -1, -3),
]


def utc_timestamp() -> str:
    return subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%S"], universal_newlines=True).strip()


def frac(v) -> Fraction:
    if isinstance(v, Fraction):
        return v
    return common.parse_fraction(v)


def frac_to_str(v: Fraction) -> str:
    return common.frac_to_str(v)


def _mod_from_value(v, p: int) -> int:
    if isinstance(v, Fraction):
        return _frac_to_mod(v, p)
    return _mod(int(v), p)


def _sort_by_groups(omega: Sequence[Fraction]) -> Tuple[Fraction, ...]:
    minus = sorted(range(3), key=lambda i: (omega[i] * omega[i], omega[i]))
    plus = sorted(range(3, 6), key=lambda i: (omega[i] * omega[i], omega[i]))
    return tuple(omega[i] for i in minus) + tuple(omega[i] for i in plus)


def _mod(v: int, p: int) -> int:
    v %= p
    if v < 0:
        v += p
    return v


def _mod_inv(v: int, p: int) -> int:
    v = _mod(v, p)
    if v == 0:
        raise ZeroDivisionError
    return pow(v, p - 2, p)


def _frac_to_mod(v: Fraction, p: int) -> int:
    den = _mod(v.denominator, p)
    if den == 0:
        raise ZeroDivisionError
    return _mod(v.numerator, p) * _mod_inv(den, p) % p


def _mask_expr(mask: int) -> List[str]:
    terms: List[str] = []
    for k in range(PAIR_COUNT):
        if (mask >> k) & 1:
            i, j = PAIR_FACTORS[k]
            terms.append(f"(a{i}_+b{j})")
    return terms


def _pair_factors_from_omega(omega: Sequence[Fraction]) -> Tuple[Fraction, ...]:
    a = [omega[0] ** 2, omega[1] ** 2, omega[2] ** 2]
    b = [omega[3] ** 2, omega[4] ** 2, omega[5] ** 2]
    out: List[Fraction] = []
    for i in range(3):
        for j in range(3):
            out.append(a[i] + b[j])
    return tuple(out)


def _mask_product(pair_factors: Tuple[Fraction, ...], mask: int) -> Fraction:
    val = Fraction(1)
    for k in range(PAIR_COUNT):
        if (mask >> k) & 1:
            val *= pair_factors[k]
    return val


def _wall_signature_from_omega(omega: Sequence[Fraction]) -> str:
    return common.serialize_signs(common.wall_sign_map(omega, WALL_CATALOG), WALL_CATALOG)


def _run_bg_binary() -> None:
    stale = not BG_BIN.exists() or not BG_SRC_COPY.exists()
    if not stale:
        if BG_SRC_COPY.stat().st_mtime < BG_SRC.stat().st_mtime:
            stale = True
        if BG_BIN.stat().st_mtime < BG_SRC_COPY.stat().st_mtime:
            stale = True

    if stale:
        shutil.copy2(BG_SRC, BG_SRC_COPY)
        proc = subprocess.run(
            [
                "g++",
                "-O2",
                "-std=c++17",
                "-o",
                str(BG_BIN),
                str(BG_SRC_COPY),
                "-lgmpxx",
                "-lgmp",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            universal_newlines=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"bg_round4 compile failed: {proc.stderr.strip() or proc.stdout.strip()}")


def _parse_bg_output(text: str) -> Tuple[Fraction, Fraction]:
    m = re.search(r"A_6\s*=\s*\(\s*([^)]*?)\s*\)\s*\+\s*i\s*\(\s*([^)]*?)\s*\)", text)
    if m:
        return frac(m.group(1)), frac(m.group(2))

    m = re.search(r"A_6\s*=\s*i\s*\*?\s*\(?\s*([^ )\n]+)\s*\)?", text)
    if m:
        return Fraction(0), frac(m.group(1))

    raise ValueError("unable to parse bg output")


def evaluate_from_free(free: Sequence[Fraction]) -> Tuple[Tuple[Fraction, ...], Fraction, Fraction, str]:
    omega = common.solve_from_free(free, SIG_FULL)
    omega = _sort_by_groups(omega)
    if any(w == 0 for w in omega):
        raise ValueError("zero frequency")
    if sum(omega) != 0:
        raise ValueError("not_on_shell_free_sum")
    if sum(SIG_FULL[i] * omega[i] * omega[i] for i in range(6)) != 0:
        raise ValueError("not_on_shell_dispersion")

    mom = ",".join(frac_to_str(SIG_FULL[i] * omega[i] * omega[i]) for i in range(6))
    wtxt = ",".join(frac_to_str(w) for w in omega)
    proc = subprocess.run(
        [str(BG_BIN), "--amp", "-K", mom, "-W", wtxt],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        universal_newlines=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"bg failed: {proc.stderr.strip() or proc.stdout.strip()}")

    a_re, a_im = _parse_bg_output(proc.stdout)
    if a_re != 0:
        raise ValueError("non-imaginary A_6")
    if a_im == 0:
        raise ValueError("zero A_im")

    prod = Fraction(1)
    for w in omega:
        prod *= w
    if prod == 0:
        raise ValueError("zero product")

    h = a_im / prod
    wall_sig = _wall_signature_from_omega(omega)
    return omega, h, wall_sig


class OracleRow:
    __slots__ = ("sample_id", "free", "omega", "h", "wall_signature_raw")

    def __init__(self, sample_id, free, omega, h, wall_signature_raw):
        self.sample_id = sample_id
        self.free = free
        self.omega = omega
        self.h = h
        self.wall_signature_raw = wall_signature_raw

def parse_oracle(path: Path) -> List[OracleRow]:
    rows: List[OracleRow] = []
    with path.open("r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            d = json.loads(ln)
            rows.append(
                OracleRow(
                    sample_id=d.get("sample_id", ""),
                    free=tuple(frac(x) for x in d["free_w"]),
                    omega=tuple(frac(x) for x in d["omega"]),
                    h=frac(d.get("H", "0")),
                    wall_signature_raw=d["wall_signature_raw"],
                )
            )
    if not rows:
        raise RuntimeError(f"empty oracle file: {path}")
    return rows


def _build_line_t_values(t_min: int, t_max: int, step: int) -> List[Fraction]:
    if step <= 0:
        raise ValueError("line step must be positive")
    if t_min > t_max:
        raise ValueError("line t-min must be <= t-max")
    t_vals: List[Fraction] = []
    seen = set()
    needed = max(NEED_TOTAL, 57)

    for denom in range(1, 32):
        for n in range(t_min * denom, t_max * denom + 1, step):
            t = Fraction(n, denom)
            if t in seen:
                continue
            seen.add(t)
            t_vals.append(t)
        if len(t_vals) >= needed:
            break

    if len(t_vals) < needed:
        raise RuntimeError(f"insufficient adaptive t-grid points: got {len(t_vals)} < {needed}")

    return sorted(t_vals, key=lambda x: (x.denominator, x.numerator))


def _build_lines(
    oracle_rows: List[OracleRow],
    target_signature: str,
    line_count: int,
    t_values: Sequence[Fraction],
    directions: Sequence[Tuple[int, int, int, int]],
) -> List["LineSample"]:
    class LineSample:
        __slots__ = ("line_id", "t_values", "h", "s", "pair_factors")

        def __init__(
            self,
            line_id: str,
            t_values: List[Fraction],
            h: List[Fraction],
            s: List[Fraction],
            pair_factors: List[Tuple[Fraction, ...]],
        ):
            self.line_id = line_id
            self.t_values = t_values
            self.h = h
            self.s = s
            self.pair_factors = pair_factors

    eval_cache: Dict[Tuple[Fraction, Fraction, Fraction, Fraction], Optional[Tuple[Tuple[Fraction, ...], Fraction, str]]] = {}
    lines: List[LineSample] = []

    for anchor in oracle_rows:
        if len(lines) >= line_count:
            break

        for didx, direction in enumerate(directions):
            if len(lines) >= line_count:
                break

            ts: List[Fraction] = []
            hs: List[Fraction] = []
            s_vals: List[Fraction] = []
            pairs: List[Tuple[Fraction, ...]] = []

            for t in t_values:
                t_frac = Fraction(t)
                free = (
                    anchor.free[0] + direction[0] * t_frac,
                    anchor.free[1] + direction[1] * t_frac,
                    anchor.free[2] + direction[2] * t_frac,
                    anchor.free[3] + direction[3] * t_frac,
                )

                cached = eval_cache.get(free)
                if cached is not None:
                    omega_sig = cached
                    if omega_sig is None:
                        continue
                else:
                    try:
                        omega, h_val, sig_val = evaluate_from_free(free)
                    except Exception:
                        eval_cache[free] = None
                        continue
                    omega_sig = (omega, h_val, sig_val)
                    eval_cache[free] = omega_sig

                omega, h_val, sig_val = omega_sig
                if sig_val != target_signature:
                    continue

                ts.append(t_frac)
                hs.append(h_val)
                s_vals.append(sum(free))
                pairs.append(_pair_factors_from_omega(omega))

            if len(ts) < NEED_TOTAL:
                continue

            line = LineSample(
                line_id=f"L{len(lines):02d}_{anchor.sample_id}_d{didx}",
                t_values=ts,
                h=hs,
                s=s_vals,
                pair_factors=pairs,
            )
            lines.append(line)

    return lines


def _eval_yvals(line: "LineSample", mask: int, d: int) -> List[Tuple[Fraction, Fraction]]:
    out: List[Tuple[Fraction, Fraction]] = []
    for t, h_val, s_val, pf in zip(line.t_values, line.h, line.s, line.pair_factors):
        if s_val == 0:
            continue
        q_val = _mask_product(pf, mask)
        if q_val == 0:
            continue
        out.append((t, h_val * q_val * (s_val ** d)))
    return out


def _solve_linear_mod(A: List[List[int]], b: List[int], p: int) -> Optional[List[int]]:
    n = len(A)
    if n == 0:
        return None
    if any(len(row) != n for row in A):
        return None
    if len(b) != n:
        return None

    mat = [[_mod_from_value(v, p) for v in row] + [_mod_from_value(r, p)] for row, r in zip(A, b)]

    row = 0
    col = 0
    pivot_cols: List[int] = []

    while row < n and col < n:
        pivot = row
        while pivot < n and mat[pivot][col] == 0:
            pivot += 1
        if pivot == n:
            col += 1
            continue

        if pivot != row:
            mat[row], mat[pivot] = mat[pivot], mat[row]

        inv = _mod_inv(mat[row][col], p)
        for cc in range(col, n + 1):
            mat[row][cc] = _mod(mat[row][cc] * inv, p)

        for rr in range(n):
            if rr == row:
                continue
            factor = mat[rr][col]
            if factor == 0:
                continue
            for cc in range(col, n + 1):
                mat[rr][cc] = _mod(mat[rr][cc] - factor * mat[row][cc], p)

        pivot_cols.append(col)
        row += 1
        col += 1

    if row != n:
        return None

    x = [0] * n
    for rr in range(n):
        pivot = None
        for cc in range(n):
            if mat[rr][cc] != 0:
                pivot = cc
                break
        if pivot is None:
            if mat[rr][n] != 0:
                return None
            continue
        x[pivot] = mat[rr][n]

    return x


def _solve_linear_rational(A: List[List[Fraction]], b: List[Fraction]) -> Optional[List[Fraction]]:
    n = len(A)
    if n == 0:
        return None
    if any(len(row) != n for row in A):
        return None
    if len(b) != n:
        return None

    mat = [row[:] + [rhs] for row, rhs in zip(A, b)]

    row = 0
    col = 0
    pivot_cols: List[int] = []

    while row < n and col < n:
        pivot = row
        while pivot < n and mat[pivot][col] == 0:
            pivot += 1
        if pivot == n:
            col += 1
            continue

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

        pivot_cols.append(col)
        row += 1
        col += 1

    if row != n:
        return None

    x = [Fraction(0, 1)] * n
    for rr in range(n):
        pivot = None
        for cc in range(n):
            if mat[rr][cc] != 0:
                pivot = cc
                break
        if pivot is None:
            if mat[rr][n] != 0:
                return None
            continue
        x[pivot] = mat[rr][n]

    return x


def _eval_poly(coeffs: Sequence[Fraction], x: Fraction) -> Fraction:
    out = Fraction(0)
    p = Fraction(1)
    for c in coeffs:
        out += c * p
        p *= x
    return out


def _has_modular_signature(values: List[Tuple[Fraction, Fraction]], d: int, p: int) -> bool:
    need_train = 2 * d + 1
    need_hold = REQUIRED_HOLDOUT
    if len(values) < need_train + need_hold:
        return False

    A = []
    b = []
    for x, y in values[:need_train]:
        xi = _frac_to_mod(x, p)
        row = [pow(xi, k, p) for k in range(need_train)]
        try:
            yi = _frac_to_mod(y, p)
        except Exception:
            return False
        A.append(row)
        b.append(yi)

    coeff = _solve_linear_mod(A, b, p)
    if coeff is None:
        return False

    for x, y in values[need_train : need_train + need_hold]:
        xi = _frac_to_mod(x, p)
        pred = 0
        powx = 1
        for c in coeff:
            pred = (pred + c * powx) % p
            powx = (powx * xi) % p
        try:
            if pred != _frac_to_mod(y, p):
                return False
        except Exception:
            return False

    return True


def _fit_exact_polynomial(values: List[Tuple[Fraction, Fraction]], d: int) -> Optional[List[Fraction]]:
    need_train = 2 * d + 1
    need_hold = REQUIRED_HOLDOUT
    if len(values) < need_train + need_hold:
        return None

    train = values[:need_train]
    if sp is not None:
        z = sp.symbols("z")
        pts = [(sp.Rational(x.numerator, x.denominator), sp.Rational(y.numerator, y.denominator)) for x, y in train]
        poly = sp.expand(sp.interpolate(pts, z))
        p = sp.Poly(poly, z)
        if p.degree() > 2 * d:
            return None
        coeffs_all = p.all_coeffs()
        coeffs: List[Fraction] = []
        for c in reversed(coeffs_all):
            if isinstance(c, sp.Integer):
                coeffs.append(Fraction(int(c), 1))
            else:
                c = sp.Rational(c)
                coeffs.append(Fraction(int(c.q), int(c.p)) if False else Fraction(int(c.p), int(c.q)))
        # exact degree is at most 2d
        if len(coeffs) < 2 * d + 1:
            coeffs.extend([Fraction(0, 1)] * ((2 * d + 1) - len(coeffs)))
        return coeffs[: 2 * d + 1]

    A = [[pow(x.numerator // x.denominator, k) if x.denominator == 1 else x ** k for k in range(2 * d + 1)] for x, _ in train]
    # with integer t only in our construction
    rhs = [y for _, y in train]
    return _solve_linear_rational(A, rhs)


def _test_mask_on_line(line: "LineSample", mask: int, d: int, run_exact: bool = True) -> Dict[str, object]:
    values = _eval_yvals(line, mask, d)
    need_train = 2 * d + 1
    need_total = need_train + REQUIRED_HOLDOUT

    if len(values) < need_total:
        return {
            "status": "insufficient_points",
            "available": len(values),
            "required": need_total,
        }

    for prime in PRIMES:
        if not _has_modular_signature(values, d, prime):
            return {
                "status": "modular_fail",
                "prime": prime,
                "line_id": line.line_id,
                "available": len(values),
            }

    if not run_exact:
        return {
            "status": "modular_pass",
            "line_id": line.line_id,
            "point_count": len(values),
            "train": need_train,
            "holdout": REQUIRED_HOLDOUT,
        }

    coeffs = _fit_exact_polynomial(values, d)
    if coeffs is None:
        return {"status": "exact_solve_error", "line_id": line.line_id}

    hold = values[need_train : need_train + REQUIRED_HOLDOUT]
    for x, y_true in hold:
        y_pred = _eval_poly(coeffs, x)
        if y_pred != y_true:
            return {"status": "exact_holdout_fail", "line_id": line.line_id}

    coeff_payload = {str(i): frac_to_str(c) for i, c in enumerate(coeffs)}
    return {
        "status": "pass",
        "line_id": line.line_id,
        "point_count": len(values),
        "train": need_train,
        "holdout": len(hold),
        "coefficients": coeff_payload,
    }


def _scan_masks(lines: List["LineSample"]) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []

    for mask in ALL_MASKS:
        k = mask.bit_count() if hasattr(int, "bit_count") else bin(mask).count("1")
        d = 2 + 2 * k

        tested = 0
        modular_pass_count = 0
        exact_pass_count = 0
        modular_fails = 0
        exact_fails = 0
        exact_checks = 0
        line_reports: List[Dict[str, object]] = []

        for line in lines:
            rpt = _test_mask_on_line(line, mask, d, run_exact=False)
            if rpt["status"] == "insufficient_points":
                continue
            tested += 1
            line_reports.append(rpt)
            if rpt["status"] == "modular_fail":
                modular_fails += 1
                continue

            if rpt["status"] == "modular_pass":
                modular_pass_count += 1

            if exact_checks < MIN_EXACT_LINES and rpt["status"] == "modular_pass":
                exact_checks += 1
                exact_rpt = _test_mask_on_line(line, mask, d, run_exact=True)
                line_reports[-1] = exact_rpt
                if exact_rpt["status"] == "pass":
                    exact_pass_count += 1
                else:
                    exact_fails += 1

        results.append(
            {
                "mask": mask,
                "bit_count": k,
                "d": d,
                "factor_expr": _mask_expr(mask),
                "pass": tested >= MIN_LINES_FOR_MASK and modular_fails == 0 and exact_checks >= MIN_EXACT_LINES and exact_fails == 0,
                "tested_lines": tested,
                "good_lines": exact_pass_count,
                "modular_pass_lines": modular_pass_count,
                "modular_fail_lines": modular_fails,
                "exact_fail_lines": exact_fails,
                "exact_check_lines": exact_checks,
                "line_reports": line_reports,
            }
        )

    return results


def _compute_inclusion_minimal(passed_masks: List[int]) -> List[int]:
    pass_set = set(passed_masks)
    out: List[int] = []
    for m in sorted(pass_set):
        minimal = True
        for sub in pass_set:
            if sub == m:
                continue
            if (sub & m) == sub and sub < m:
                minimal = False
                break
        if minimal:
            out.append(m)
    return out


def _load_fresh_structure(path: Path) -> Dict[str, List[dict]]:
    by_sig: Dict[str, List[dict]] = {}
    with path.open("r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            d = json.loads(ln)
            by_sig.setdefault(d["wall_signature_raw"], []).append(d)
    return by_sig


def _cross_chambers_report(target_masks: List[int], t_values: Sequence[Fraction]) -> Dict[str, object]:
    fresh_path = DATA_DIR / "fresh_structure_oracle_v2.jsonl"
    if not fresh_path.exists():
        return {"status": "missing_fresh_oracle", "path": str(fresh_path)}

    by_sig = _load_fresh_structure(fresh_path)
    sigs = sorted(by_sig.items(), key=lambda kv: len(kv[1]), reverse=True)
    sigs = [s for s, rows in sigs if len(rows) >= 35][:8]

    report: Dict[str, object] = {
        "status": "ok",
        "signatures": sigs,
        "mask_reports": {},
        "tested_signatures": 0,
        "tested_masks": 0,
    }

    # convert rows to OracleRow and derive signed H = A_im/prod(omega)
    rows_by_sig: Dict[str, List[OracleRow]] = {}
    for sig, rows in by_sig.items():
        if sig not in sigs:
            continue
        out_rows: List[OracleRow] = []
        for idx, row in enumerate(rows):
            try:
                omega = tuple(frac(x) for x in row["omega"])
                free = tuple(frac(x) for x in row["free_w"])
            except Exception:
                continue
            prod = Fraction(1)
            for w in omega:
                prod *= w
            if prod == 0:
                continue
            out_rows.append(
                OracleRow(
                    sample_id=f"fresh-{sig[:6]}-{idx}",
                    free=free,
                    omega=omega,
                    h=frac(row.get("A_im", "0")) / prod,
                    wall_signature_raw=sig,
                )
            )
        rows_by_sig[sig] = out_rows

    for mask in target_masks:
        k = mask.bit_count() if hasattr(int, "bit_count") else bin(mask).count("1")
        d = 2 + 2 * k
        sig_report: Dict[str, object] = {}

        for sig in sigs:
            rows = rows_by_sig.get(sig, [])
            if len(rows) < 3:
                sig_report[sig] = {"status": "insufficient_rows", "rows": len(rows)}
                continue

            lines = _build_lines(rows, sig, line_count=2, t_values=t_values, directions=DEFAULT_LINE_DIRECTIONS)
            if len(lines) < 1:
                sig_report[sig] = {"status": "insufficient_lines", "rows": len(rows)}
                continue

            pass_count = 0
            tested = 0
            for line in lines[:2]:
                rpt = _test_mask_on_line(line, mask, d)
                if rpt["status"] in ("pass", "modular_fail", "exact_holdout_fail", "exact_solve_error"):
                    tested += 1
                    if rpt["status"] == "pass":
                        pass_count += 1

            sig_report[sig] = {
                "tested_lines": tested,
                "passed_lines": pass_count,
                "status": "pass" if (pass_count == tested and tested > 0) else "fail",
            }
            report["tested_signatures"] += 1

        report["mask_reports"][str(mask)] = sig_report
        report["tested_masks"] += 1

    return report


def run_scan(
    line_count: int,
    t_min: int,
    t_max: int,
    t_step: int,
    do_cross: bool,
) -> Dict[str, object]:
    start = None
    import time

    start = time.time()

    _run_bg_binary()

    oracle = parse_oracle(DATA_DIR / "h_rational_probe_oracle.jsonl")
    sig_count: Dict[str, int] = {}
    for row in oracle:
        sig_count[row.wall_signature_raw] = sig_count.get(row.wall_signature_raw, 0) + 1

    target_signature, target_count = max(sig_count.items(), key=lambda kv: kv[1])
    target_rows = [r for r in oracle if r.wall_signature_raw == target_signature]

    t_values = _build_line_t_values(t_min, t_max, t_step)
    lines = _build_lines(target_rows, target_signature, line_count=line_count, t_values=t_values, directions=DEFAULT_LINE_DIRECTIONS)

    mask_results = _scan_masks(lines)
    passed = [r for r in mask_results if r["pass"]]
    minimal = _compute_inclusion_minimal([r["mask"] for r in passed])
    full_mask = (1 << PAIR_COUNT) - 1
    full_diag = next((r for r in mask_results if r["mask"] == full_mask), None)

    payload: Dict[str, object] = {
        "timestamp": utc_timestamp(),
        "bg_binary": str(BG_BIN),
        "wall_signature_raw": target_signature,
        "signature_rows": len(oracle),
        "signature_target_count": target_count,
        "line_count_requested": line_count,
        "line_count_built": len(lines),
        "line_t": {"min": t_min, "max": t_max, "step": t_step},
        "line_directions": [list(d) for d in DEFAULT_LINE_DIRECTIONS],
        "total_masks": len(mask_results),
        "passed_masks": len(passed),
        "minimal_masks": minimal,
        "full_mask": {
            "mask": full_mask,
            "status": "passed" if full_diag and full_diag["pass"] else "failed",
            "diagnostic": full_diag,
        },
        "mask_results": mask_results,
        "duration_sec": round(time.time() - start, 3),
    }

    if do_cross and passed:
        payload["cross_chambers"] = _cross_chambers_report(
            target_masks=sorted(set(minimal[:5] + [full_mask])),
            t_values=t_values,
        )

    return payload


def write_reports(payload: Dict[str, object]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    json_path = DATA_DIR / "h_mask_scan_lean.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)

    md_lines = [
        "# Lean mask scan",
        "",
        f"timestamp: {payload['timestamp']}",
        f"target wall signature: `{payload['wall_signature_raw']}`",
        f"rows: {payload['signature_rows']} (target signature rows: {payload['signature_target_count']})",
        f"lines built: {payload['line_count_built']}",
        f"passed masks: {payload['passed_masks']} / {payload['total_masks']}",
        f"minimal passing masks: {payload['minimal_masks']}",
        "",
        "## Full mask",
        f"- {payload['full_mask']['status']}",
        "",
        "## Passing masks",
    ]

    passing = [r for r in payload["mask_results"] if r["pass"]]
    if not passing:
        md_lines.append("- none")
    else:
        for r in sorted(passing, key=lambda x: (x["bit_count"], x["mask"])):
            md_lines.append(
                f"- mask={r['mask']}, bits={r['bit_count']}, d={r['d']}, "
                f"tested={r['tested_lines']}, good={r['good_lines']}, "
                f"mod_fail={r['modular_fail_lines']}, exact_fail={r['exact_fail_lines']}"
            )

    if "cross_chambers" in payload:
        md_lines.extend([
            "",
            "## Cross-chamber status",
            f"- tested signatures: {payload['cross_chambers'].get('tested_signatures')}",
            f"- tested masks: {payload['cross_chambers'].get('tested_masks')}",
        ])

    md_path = DATA_DIR / "h_mask_scan_lean.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    if "cross_chambers" in payload:
        cross_path = DATA_DIR / "h_mask_cross_chambers.json"
        with cross_path.open("w", encoding="utf-8") as f:
            json.dump(payload["cross_chambers"], f, indent=2, sort_keys=True)


def write_stage0_report() -> Path:
    proc = subprocess.run(
        ["ps", "-eo", "pid,ppid,etime,stat,rss,args"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    live: List[Dict[str, object]] = []
    commands: List[str] = []
    if proc.returncode == 0:
        lines = proc.stdout.splitlines()
        for ln in lines[1:]:
            if "h_mask_scan_lean.py" not in ln and "h_rational_probe.py" not in ln and "h_signed_blocks_fit.py" not in ln:
                continue
            parts = ln.split(None, 5)
            if len(parts) < 6:
                continue
            pid = parts[0]
            live.append(
                {
                    "pid": pid,
                    "ppid": parts[1],
                    "etime": parts[2],
                    "stat": parts[3],
                    "rss_kb": parts[4],
                    "cmd": parts[5],
                }
            )
            commands.append(f"kill -TERM {pid}")

    payload = {
        "timestamp": utc_timestamp(),
        "status": "terminated",
        "live_processes": live,
        "commands": commands,
        "notes": "lean stage continuation after heavy detached run",
    }
    p = DATA_DIR / "h_mask_stage0_termination.txt"
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return p


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--lines", type=int, default=DEFAULT_LINES)
    p.add_argument("--line-t-min", type=int, default=DEFAULT_LINE_T_RANGE[0])
    p.add_argument("--line-t-max", type=int, default=DEFAULT_LINE_T_RANGE[1])
    p.add_argument("--line-t-step", type=int, default=DEFAULT_LINE_STEP)
    p.add_argument("--cross", action="store_true", help="run cross-signature diagnostic")
    p.add_argument("--write-stage0", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.write_stage0:
        write_stage0_report()
    payload = run_scan(
        line_count=args.lines,
        t_min=args.line_t_min,
        t_max=args.line_t_max,
        t_step=args.line_t_step,
        do_cross=args.cross,
    )
    write_reports(payload)


if __name__ == "__main__":
    main()
