#!/usr/bin/env python3
import json
import re
import subprocess
from fractions import Fraction
from itertools import combinations_with_replacement
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BG = ROOT / "bg"
DATA_DIR = ROOT.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


AMP_RE = re.compile(r"A_(\d+) = i \* \(([-0-9/]+)\)")
OMEGA_RE = re.compile(r"omega = \{([^}]*)\}")


def q(s):
    return Fraction(s)


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
        out = subprocess.check_output(cmd, text=True, cwd=ROOT, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        return {
            "n": n,
            "free_w": [fmt_q(x) for x in free_w],
            "error": f"oracle_failed_returncode_{exc.returncode}",
            "output": exc.output,
        }
    om = OMEGA_RE.search(out)
    amp = AMP_RE.search(out)
    if not om or not amp:
        raise RuntimeError(out)
    omegas = [q(part.strip()) for part in om.group(1).split(",")]
    amp_im = q(amp.group(2))
    return {
        "n": n,
        "free_w": [fmt_q(x) for x in free_w],
        "omega": [fmt_q(x) for x in omegas],
        "amp_im": fmt_q(amp_im),
        "amp_numeric": float(amp_im),
    }


def elementary(vals):
    vals = [Fraction(v) for v in vals]
    out = [Fraction(1)]
    for v in vals:
        out.append(Fraction(0))
        for k in range(len(out) - 1, 0, -1):
            out[k] += out[k - 1] * v
    return out


def features(row):
    w = [Fraction(x) for x in row["omega"]]
    neg_sigma = [w[0], w[1]]
    pos_sigma = w[2:]
    epos = elementary(pos_sigma)
    s1, s2 = neg_sigma
    return {
        "w1": s1,
        "w2": s2,
        "u": -s1,
        "v": s2,
        "p_sum": sum(pos_sigma, Fraction(0)),
        "p_prod": epos[-1],
        "e": epos,
        "amp_im": Fraction(row["amp_im"]),
    }


def monomial_exponents(num_vars, degree):
    if num_vars == 0:
        return [()]
    out = []
    def rec(i, left, acc):
        if i == num_vars - 1:
            out.append(tuple(acc + [left]))
            return
        for k in range(left + 1):
            rec(i + 1, left - k, acc + [k])
    rec(0, degree, [])
    return out


def solve_linear(rows, columns, target):
    import sympy as sp

    mat = sp.Matrix([[sp.Rational(columns[j](r).numerator, columns[j](r).denominator)
                      for j in range(len(columns))] for r in rows])
    vec = sp.Matrix([sp.Rational(target(r).numerator, target(r).denominator)
                     for r in rows])
    sol = sp.linsolve((mat, vec))
    if not sol:
        return None
    sols = list(sol)
    if not sols:
        return None
    if any(v.free_symbols for v in sols[0]):
        return None
    return [Fraction(int(v.p), int(v.q)) for v in sols[0]]


def eval_cols(row, columns, coeffs):
    return sum(c * col(row) for c, col in zip(coeffs, columns))


def build_dataset():
    cases = {
        4: [
            [Fraction(2), Fraction(3)],
            [Fraction(5), Fraction(1, 7)],
            [Fraction(1, 5), Fraction(4)],
            [Fraction(7, 3), Fraction(5, 2)],
            [Fraction(11), Fraction(2)],
        ],
        5: [
            [Fraction(2), Fraction(5, 2), Fraction(3)],
            [Fraction(5), Fraction(1, 7), Fraction(2)],
            [Fraction(1, 5), Fraction(4), Fraction(3)],
            [Fraction(7, 3), Fraction(5, 2), Fraction(11, 4)],
            [Fraction(11), Fraction(2), Fraction(3, 2)],
            [Fraction(3), Fraction(4), Fraction(7)],
        ],
        6: [
            [Fraction(2), Fraction(5, 2), Fraction(3), Fraction(7, 2)],
            [Fraction(5), Fraction(1, 7), Fraction(2), Fraction(3)],
            [Fraction(1, 5), Fraction(4), Fraction(3), Fraction(5, 2)],
            [Fraction(7, 3), Fraction(5, 2), Fraction(11, 4), Fraction(13, 5)],
            [Fraction(11), Fraction(2), Fraction(3, 2), Fraction(5, 3)],
            [Fraction(3), Fraction(4), Fraction(7), Fraction(9)],
        ],
        7: [
            [Fraction(2), Fraction(5, 2), Fraction(3), Fraction(7, 2), Fraction(4)],
            [Fraction(5), Fraction(1, 7), Fraction(2), Fraction(3), Fraction(4)],
            [Fraction(1, 5), Fraction(4), Fraction(3), Fraction(5, 2), Fraction(7, 2)],
            [Fraction(7, 3), Fraction(5, 2), Fraction(11, 4), Fraction(13, 5), Fraction(17, 6)],
            [Fraction(11), Fraction(2), Fraction(3, 2), Fraction(5, 3), Fraction(7, 4)],
        ],
    }
    rows = []
    for n, free_sets in cases.items():
        for free_w in free_sets:
            rows.append(run_bg(n, free_w))
    (DATA_DIR / "oracle_dataset.json").write_text(json.dumps(rows, indent=2) + "\n")
    return rows


def candidate_checks(rows):
    checks = []
    finite_rows = [r for r in rows if "amp_im" in r]
    for n in sorted({r["n"] for r in rows}):
        failures = [r for r in rows if r["n"] == n and "amp_im" not in r]
        if failures:
            checks.append({
                "n": n,
                "name": "oracle_failures",
                "failures": failures,
            })
        fr = [features(r) for r in finite_rows if r["n"] == n]
        if not fr:
            continue
        m = n - 2
        # Candidate 1: A/i depends only on product of positive-sigma frequencies.
        ratios = [r["amp_im"] / r["p_prod"] for r in fr if r["p_prod"]]
        checks.append({
            "n": n,
            "name": "product_only_ratio",
            "values": [fmt_q(x) for x in ratios],
            "passes_constant": len(set(ratios)) == 1,
        })
        degree = n - 2
        uv_columns = []
        uv_labels = []
        for a in range(degree + 1):
            b = degree - a
            uv_labels.append(f"u^{a} v^{b}")
            uv_columns.append(lambda row, a=a, b=b: (row["u"] ** a) * (row["v"] ** b))
        if len(fr) > len(uv_columns):
            uv_coeffs = solve_linear(fr[:len(uv_columns)], uv_columns,
                                     lambda row: row["amp_im"] / row["p_prod"])
            if uv_coeffs is not None:
                residuals = []
                rels = []
                for row in fr[len(uv_columns):]:
                    pred_ratio = eval_cols(row, uv_columns, uv_coeffs)
                    pred = pred_ratio * row["p_prod"]
                    resid = pred - row["amp_im"]
                    rel = abs(Fraction(resid, row["amp_im"])) if row["amp_im"] else None
                    residuals.append(fmt_q(resid))
                    rels.append(None if rel is None else float(rel))
                checks.append({
                    "n": n,
                    "name": "product_times_uv_homogeneous_polynomial",
                    "ansatz": "A_n/i = e_m * P_{n-2}(u,v)",
                    "fit_columns": uv_labels,
                    "fit_rows": len(uv_columns),
                    "heldout_residuals": residuals,
                    "heldout_max_relative": None if any(x is None for x in rels) else max(rels),
                    "passes_heldout": all(x == "0" for x in residuals),
                })
        # Candidate 2: divide by product and fit a polynomial in the two
        # negative-sigma frequencies with total degree <= n-1.
        max_degree = n - 1
        columns = []
        labels = []
        for d in range(max_degree + 1):
            for a, b in monomial_exponents(2, d):
                labels.append(f"u^{a} v^{b}")
                columns.append(lambda row, a=a, b=b: (row["u"] ** a) * (row["v"] ** b))
        target = lambda row: row["amp_im"] / row["p_prod"]
        coeffs = solve_linear(fr[:len(columns)], columns, target) if len(fr) >= len(columns) else None
        if coeffs is None:
            # Underdetermined for small data; fit with all rows via sympy gauss
            # only when enough rows are available.
            pass
        # Candidate 3: simple closed forms suggested by low-n inspection.
        u = lambda row: row["u"]
        v = lambda row: row["v"]
        pprod = lambda row: row["p_prod"]
        simple = []
        formulas = [
            ("-2^(n-1) * p_prod * u * v", lambda row, n=n: -(2 ** (n - 1)) * pprod(row) * u(row) * v(row)),
            ("-2^(n-1) * p_prod * u^(n-3) * v", lambda row, n=n: -(2 ** (n - 1)) * pprod(row) * (u(row) ** (n - 3)) * v(row)),
            ("-2^(n-1) * p_prod * u * v^(n-3)", lambda row, n=n: -(2 ** (n - 1)) * pprod(row) * u(row) * (v(row) ** (n - 3))),
            ("-2^(n-1) * p_prod * (u*v)^(n-2)/(u+v)", lambda row, n=n: -(2 ** (n - 1)) * pprod(row) * ((u(row) * v(row)) ** (n - 2)) / (u(row) + v(row))),
        ]
        for label, fn in formulas:
            residuals = []
            rels = []
            for row in fr:
                pred = fn(row)
                resid = pred - row["amp_im"]
                rel = abs(Fraction(resid, row["amp_im"])) if row["amp_im"] else None
                residuals.append(fmt_q(resid))
                rels.append(None if rel is None else float(rel))
            simple.append({
                "formula": label,
                "residuals": residuals,
                "max_relative": None if any(x is None for x in rels) else max(rels),
            })
        checks.append({"n": n, "name": "simple_formula_failures", "results": simple})
    (DATA_DIR / "ansatz_checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    return checks


def structural_checks():
    cases = []
    perm_pairs = [
        (5, [Fraction(2), Fraction(5, 2), Fraction(3)],
            [Fraction(2), Fraction(3), Fraction(5, 2)]),
        (6, [Fraction(2), Fraction(5, 2), Fraction(3), Fraction(7, 2)],
            [Fraction(2), Fraction(3), Fraction(5, 2), Fraction(7, 2)]),
    ]
    for n, left, right in perm_pairs:
        a = run_bg(n, left)
        b = run_bg(n, right)
        cases.append({
            "kind": "positive_sigma_permutation",
            "n": n,
            "left": a,
            "right": b,
            "same_amp": a.get("amp_im") == b.get("amp_im"),
        })
    scale_bases = [
        (5, [Fraction(2), Fraction(5, 2), Fraction(3)]),
        (6, [Fraction(2), Fraction(5, 2), Fraction(3), Fraction(7, 2)]),
        (7, [Fraction(2), Fraction(5, 2), Fraction(3), Fraction(7, 2), Fraction(4)]),
    ]
    for n, base in scale_bases:
        a = run_bg(n, base)
        b = run_bg(n, [2 * x for x in base])
        ratio = None
        expected = None
        passes = False
        if "amp_im" in a and "amp_im" in b:
            ratio = Fraction(b["amp_im"]) / Fraction(a["amp_im"])
            expected = Fraction(2) ** (2 * n - 4)
            passes = ratio == expected
        cases.append({
            "kind": "scale_by_2",
            "n": n,
            "base": a,
            "scaled": b,
            "ratio": None if ratio is None else fmt_q(ratio),
            "expected_ratio_for_degree_2n_minus_4": None if expected is None else fmt_q(expected),
            "passes": passes,
        })
    (DATA_DIR / "structural_checks.json").write_text(json.dumps(cases, indent=2) + "\n")
    return cases


def main():
    rows = build_dataset()
    checks = candidate_checks(rows)
    structural = structural_checks()
    print(json.dumps({"rows": len(rows), "checks": checks, "structural": structural}, indent=2))


if __name__ == "__main__":
    main()
