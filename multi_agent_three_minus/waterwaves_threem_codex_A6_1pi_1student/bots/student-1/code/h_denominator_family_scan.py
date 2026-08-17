#!/usr/bin/env python3
"""Denominator-family scanner with reusable line cache.

The script probes the fixed-chamber oracle for affine families in free-space and
checks whether\n\
    H * Q * s^d
with Q a subproduct of (a_i+b_j) is polynomial in t along the line, where
s = a+b+c+d (the free-sum parameter) and d = 2 + 2*|Q|.

It emits:
- line cache reused across runs (`h_denominator_line_cache.jsonl`)
- mask-by-family scan results (`h_denominator_family_scan.json`)
- a compact markdown digest (`h_denominator_family_scan.md`)
"""

import argparse
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import common

ROOT = Path(__file__).resolve().parent.parent
QUESTION_DIR = ROOT.parent.parent
DATA_DIR = ROOT / "data"
BG_SRC = QUESTION_DIR / "bg.cpp"
BG_CPP = ROOT / "code" / "bg_round_denom_family.cpp"
BG_BIN = ROOT / "code" / "bg_round_denom_family"

WALL_CATALOG = common.build_wall_catalog()
SIG_FULL = common.SIG_FULL
PAIR_FACTORS = [(i, j) for i in range(3) for j in range(3)]
PAIR_COUNT = len(PAIR_FACTORS)
ALL_MASKS = list(range(1 << PAIR_COUNT))
ALL_MASKS_SORTED = sorted(ALL_MASKS)
PRIMES = (1_000_003, 1_000_007, 1_000_033)

DEFAULT_DIRECTIONS = [
    (1, -2, 3, -4),
    (1, 1, -2, 2),
    (2, -1, -2, 1),
    (-3, 2, 1, -1),
    (1, -1, 2, -2),
    (2, 2, -1, -3),
]

REQUIRED_HOLDOUT = 12


def utc_timestamp() -> str:
    return subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%S"], universal_newlines=True).strip()


def frac_to_str(v: Fraction) -> str:
    return common.frac_to_str(v)


def parse_fraction(v) -> Fraction:
    return common.parse_fraction(v)


def sort_by_groups(omega: Sequence[Fraction]) -> Tuple[Fraction, ...]:
    minus = sorted(range(3), key=lambda i: (omega[i] * omega[i], omega[i]))
    plus = sorted(range(3), key=lambda i: (omega[3 + i] * omega[3 + i], omega[3 + i]))
    return tuple(omega[i] for i in minus) + tuple(omega[3 + i] for i in plus)


def ensure_bg_binary() -> None:
    need = True
    if BG_CPP.exists() and BG_SRC.exists():
        if BG_CPP.stat().st_mtime >= BG_SRC.stat().st_mtime and BG_BIN.exists() and BG_BIN.stat().st_mtime >= BG_CPP.stat().st_mtime:
            need = False

    if need:
        BG_CPP.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["cp", str(BG_SRC), str(BG_CPP)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        proc = subprocess.run(
            [
                "g++",
                "-O2",
                "-std=c++17",
                "-o",
                str(BG_BIN),
                str(BG_CPP),
                "-lgmpxx",
                "-lgmp",
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"bg_round_denom_family compile failed: {proc.stderr.strip() or proc.stdout.strip()}")


def _mod(v: int, p: int) -> int:
    vv = v % p
    return vv + p if vv < 0 else vv


def _mod_inv(v: int, p: int) -> int:
    return pow(_mod(v, p), p - 2, p)


def frac_to_mod(v: Fraction, p: int) -> int:
    den = _mod(v.denominator, p)
    if den == 0:
        raise ZeroDivisionError("denominator not invertible")
    return _mod(v.numerator, p) * _mod_inv(den, p) % p


def wall_signature(omega: Sequence[Fraction]) -> str:
    return common.serialize_signs(common.wall_sign_map(omega, WALL_CATALOG), WALL_CATALOG)


def run_bg_from_omega(omega: Sequence[Fraction]) -> Tuple[Fraction, Fraction]:
    cmd = [
        str(BG_BIN),
        "--amp",
        "-K",
        ",".join(frac_to_str(SIG_FULL[i] * omega[i] * omega[i]) for i in range(6)),
        "-W",
        ",".join(frac_to_str(v) for v in omega),
    ]
    proc = subprocess.run(
        cmd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"bg failed: {proc.stderr.strip() or proc.stdout.strip()}")

    txt = proc.stdout
    import re

    m = re.search(r"A_6\\s*=\\s*\\(\\s*([^)]*?)\\s*\\)\\s*\\+\\s*i\\s*\\(\\s*([^)]*?)\\s*\\)", txt)
    if m:
        return parse_fraction(m.group(1).strip()), parse_fraction(m.group(2).strip())

    m = re.search(r"A_6\\s*=\\s*i\\s*\\*?\\s*\\(?\\s*([^ )\\n]+)\\s*\\)?", txt)
    if m:
        return Fraction(0), parse_fraction(m.group(1).strip())

    raise ValueError(f"unable to parse bg output: {txt}")


def evaluate_free_point(free: Sequence[Fraction]) -> Tuple[Tuple[Fraction, ...], Fraction]:
    omega = common.solve_from_free(list(free), SIG_FULL)
    omega = sort_by_groups(omega)
    if any(v == 0 for v in omega):
        raise ValueError("zero_frequency")
    if sum(omega) != 0:
        raise ValueError("not_on_shell")
    if sum(SIG_FULL[i] * omega[i] * omega[i] for i in range(6)) != 0:
        raise ValueError("not_on_mass_shell")

    _, a_im = run_bg_from_omega(omega)
    if a_im == 0:
        raise ValueError("zero_amplitude_imaginary")

    prod = Fraction(1, 1)
    for x in omega:
        prod *= x
    if prod == 0:
        raise ValueError("zero_product")

    h = a_im / prod
    return omega, h


def pair_factors(omega: Sequence[Fraction]) -> Tuple[Fraction, ...]:
    a = [omega[0] ** 2, omega[1] ** 2, omega[2] ** 2]
    b = [omega[3] ** 2, omega[4] ** 2, omega[5] ** 2]
    out = []
    for i in range(3):
        for j in range(3):
            out.append(a[i] + b[j])
    return tuple(out)


def mask_product(pfactors: Sequence[Fraction], mask: int) -> Fraction:
    out = Fraction(1, 1)
    for k in range(PAIR_COUNT):
        if (mask >> k) & 1:
            out *= pfactors[k]
    return out


def all_mask_products(pfactors: Sequence[Fraction]) -> List[Fraction]:
    out = [Fraction(1, 1)] * (1 << PAIR_COUNT)
    for k, val in enumerate(pfactors):
        bit = 1 << k
        for base in range(bit):
            out[base | bit] = out[base] * val
    return out


def build_t_grid(t_min: int, t_max: int, t_step: int, max_den: int = 12, need: int = 70) -> List[Fraction]:
    if t_step <= 0:
        raise ValueError("t_step must be positive")
    if t_min > t_max:
        raise ValueError("t_min > t_max")

    out: Dict[Tuple[int, int], Fraction] = {}
    values: List[Fraction] = []
    for den in range(1, max_den + 1):
        for n in range(t_min * den, t_max * den + 1, t_step):
            v = Fraction(n, den)
            key = (v.numerator, v.denominator)
            if key in out:
                continue
            out[key] = v
            values.append(v)
        if len(values) >= need:
            break
    values = sorted(values, key=lambda x: (x.denominator, x.numerator))
    if len(values) < need:
        raise RuntimeError(f"insufficient t-grid points: got {len(values)} < {need}")
    return values


def cache_key(anchor_id: str, family_idx: int, direction: Tuple[int, int, int, int], t: Fraction) -> str:
    return f"{anchor_id}|f{family_idx}|[{','.join(str(v) for v in direction)}]|{frac_to_str(t)}"


def line_cache_load(path: Path) -> Dict[str, dict]:
    store: Dict[str, dict] = {}
    if not path.exists():
        return store

    with path.open("r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                payload = json.loads(ln)
            except json.JSONDecodeError:
                continue
            key = str(payload.get("cache_key", ""))
            if key:
                store[key] = payload
    return store


def cache_append(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, sort_keys=True) + "\n")


def parse_oracle_rows(path: Path) -> List[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            d = json.loads(ln)
            rows.append(
                {
                    "sample_id": d.get("sample_id", ""),
                    "split": d.get("split", ""),
                    "free": tuple(parse_fraction(x) for x in d["free_w"]),
                    "omega": tuple(parse_fraction(x) for x in d["omega"]),
                    "A_im": parse_fraction(d.get("A_im", "0")),
                    "wall_signature_raw": d["wall_signature_raw"],
                }
            )

            H = rows[-1]["A_im"]
            prod = Fraction(1, 1)
            for w in rows[-1]["omega"]:
                prod *= w
            if prod != 0:
                rows[-1]["H"] = H / prod
    if not rows:
        raise RuntimeError(f"no rows in {path}")
    return rows


def safe_kinematics_ok(omega: Sequence[Fraction], wall_sig: str) -> bool:
    if any(w == 0 for w in omega):
        return False
    if sum(omega) != 0:
        return False
    if sum(SIG_FULL[i] * omega[i] * omega[i] for i in range(6)) != 0:
        return False

    # wall signatures are serialized as "id:sign" pairs.
    # Only walls with sign 0 are invalid on the chamber boundary.
    for part in wall_sig.split("|"):
        if not part:
            continue
        if part.endswith(":0"):
            return False

    return True


def row_with_signature(rows: List[dict], signature: Optional[str]) -> Tuple[List[dict], str]:
    if signature is None:
        counts = Counter(r["wall_signature_raw"] for r in rows)
        signature = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[0][0]
    selected = [r for r in rows if r["wall_signature_raw"] == signature]
    if not selected:
        raise RuntimeError(f"no oracle rows for signature={signature}")
    return selected, signature


def build_lines(
    anchor_rows: List[dict],
    target_signature: str,
    line_count: int,
    t_values: Sequence[Fraction],
    directions: Sequence[Tuple[int, int, int, int]],
    max_points_per_line: int,
    min_points_per_line: int,
    cache: Dict[str, dict],
    cache_path: Path,
) -> List[dict]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    built = 0
    miss = 0
    hit = 0
    lines: List[dict] = []

    for anchor in anchor_rows:
        if built >= line_count:
            break
        for fidx, direction in enumerate(directions):
            if built >= line_count:
                break

            points = []
            for t in t_values:
                if built >= line_count and len(points) >= min_points_per_line:
                    break

                free = tuple(anchor["free"][i] + Fraction(direction[i]) * t for i in range(4))
                k = cache_key(anchor["sample_id"], fidx, direction, t)
                cached = cache.get(k)
                if cached is not None:
                    hit += 1
                    try:
                        wall_sig = cached["wall_signature_raw"]
                        if wall_sig != target_signature:
                            continue
                        if cached.get("status") != "ok":
                            continue

                        omega = tuple(parse_fraction(v) for v in cached["omega"])
                        h = parse_fraction(cached["H"])
                        s = parse_fraction(cached["s"]) if "s" in cached else sum(free)
                        pf = tuple(parse_fraction(v) for v in cached["pair_factors"])
                        if h == 0 or s == 0:
                            continue
                        if not safe_kinematics_ok(omega, wall_sig):
                            continue

                        points.append(
                            {
                                "anchor_id": anchor["sample_id"],
                                "family_id": fidx,
                                "direction": direction,
                                "t": t,
                                "s": s,
                                "h": h,
                                "pair_factors": pf,
                                "mask_products": None,
                            }
                        )
                        continue
                    except Exception:
                        continue

                try:
                    omega, h = evaluate_free_point(free)
                except Exception:
                    continue

                wall_sig = wall_signature(omega)
                if wall_sig != target_signature:
                    continue

                s = sum(free)
                if s == 0 or h == 0:
                    continue

                pf = pair_factors(omega)
                if not safe_kinematics_ok(omega, wall_sig):
                    continue

                payload = {
                    "cache_key": k,
                    "status": "ok",
                    "anchor_id": anchor["sample_id"],
                    "direction": list(direction),
                    "t": frac_to_str(t),
                    "free": [frac_to_str(v) for v in free],
                    "omega": [frac_to_str(v) for v in omega],
                    "wall_signature_raw": wall_sig,
                    "s": frac_to_str(s),
                    "H": frac_to_str(h),
                    "pair_factors": [frac_to_str(v) for v in pf],
                }
                cache[k] = payload
                cache_append(cache_path, payload)
                miss += 1

                points.append(
                    {
                        "anchor_id": anchor["sample_id"],
                        "family_id": fidx,
                        "direction": direction,
                        "t": t,
                        "s": s,
                        "h": h,
                        "pair_factors": pf,
                        "mask_products": None,
                    }
                )

                if len(points) >= max_points_per_line:
                    break

            if len(points) >= min_points_per_line:
                line = {
                    "line_id": f"L{built:02d}",
                    "anchor_id": anchor["sample_id"],
                    "family_id": fidx,
                    "direction": list(direction),
                    "point_count": len(points),
                    "points": points,
                }
                lines.append(line)
                built += 1

    if built < line_count:
        raise RuntimeError(f"could only build {built} lines (requested {line_count}); try wider t-range or more anchors")

    return lines


def solve_linear_mod(A: List[List[int]], b: List[int], p: int) -> Optional[List[int]]:
    m = len(A)
    if m == 0:
        return None
    n = len(A[0])
    if any(len(row) != n for row in A):
        return None
    if len(b) != m:
        return None
    if m != n:
        return None

    mat = [row[:] + [rhs] for row, rhs in zip(A, b)]
    row = 0
    col = 0

    while row < n and col < n:
        pivot = row
        while pivot < n and mat[pivot][col] % p == 0:
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
            fac = mat[rr][col]
            if fac == 0:
                continue
            for cc in range(col, n + 1):
                mat[rr][cc] = _mod(mat[rr][cc] - fac * mat[row][cc], p)

        row += 1
        col += 1

    if row != n:
        return None

    out = [Fraction(0)] * n
    out_int = [0] * n
    for rr in range(n):
        pivot = None
        for cc in range(n):
            if mat[rr][cc] % p != 0:
                pivot = cc
                break
        if pivot is None:
            return None
        out_int[pivot] = mat[rr][n] % p
    return out_int


def solve_linear_rational(A: List[List[Fraction]], b: List[Fraction]) -> Optional[List[Fraction]]:
    m = len(A)
    if m == 0:
        return None
    n = len(A[0])
    if any(len(row) != n for row in A) or len(b) != m:
        return None
    if m != n:
        return None

    mat = [row[:] + [rhs] for row, rhs in zip(A, b)]
    row = 0
    col = 0

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
        mat[row] = [v * inv for v in mat[row]]

        for rr in range(n):
            if rr == row:
                continue
            fac = mat[rr][col]
            if fac == 0:
                continue
            mat[rr] = [a - fac * b for a, b in zip(mat[rr], mat[row])]

        row += 1
        col += 1

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

    x = [Fraction(0, 1)] * n
    for rr in range(n):
        pivot = None
        for cc in range(n):
            if mat[rr][cc] != 0:
                pivot = cc
                break
        if pivot is not None:
            x[pivot] = mat[rr][n]
    return x


def interpolate_poly(values: List[Tuple[Fraction, Fraction]], d: int) -> Optional[List[Fraction]]:
    need = 2 * d + 1
    if len(values) < need:
        return None

    A: List[List[Fraction]] = []
    b: List[Fraction] = []
    for x, y in values[:need]:
        row = []
        px = Fraction(1, 1)
        for k in range(need):
            row.append(px)
            px *= x
        A.append(row)
        b.append(y)

    coeff = solve_linear_rational(A, b)
    return coeff


def poly_eval(coeff: Sequence[Fraction], x: Fraction) -> Fraction:
    out = Fraction(0, 1)
    for c in reversed(coeff):
        out = out * x + c
    return out


def points_for_mask(line: dict, mask: int, d: int) -> List[Tuple[Fraction, Fraction]]:
    vals: List[Tuple[Fraction, Fraction]] = []
    for p in line["points"]:
        if p["mask_products"] is None:
            p["mask_products"] = all_mask_products(p["pair_factors"])
        q = p["mask_products"][mask]
        if q == 0:
            continue
        s = p["s"]
        if s == 0:
            continue
        y = p["h"] * q * (s ** d)
        vals.append((p["t"], y))
    return vals


def mod_holdout_check(values: List[Tuple[Fraction, Fraction]], d: int, prime: int) -> bool:
    need = 2 * d + 1
    if len(values) < need + REQUIRED_HOLDOUT:
        return False

    A = []
    b = []
    for x, y in values[:need]:
        row = [pow(frac_to_mod(x, prime), k, prime) for k in range(need)]
        A.append(row)
        b.append(frac_to_mod(y, prime))

    coeff = solve_linear_mod(A, b, prime)
    if coeff is None:
        return False

    for x, y in values[need : need + REQUIRED_HOLDOUT]:
        pred = 0
        px = 1
        for c in coeff:
            pred = (pred + c * px) % prime
            px = (px * frac_to_mod(x, prime)) % prime
        if pred != frac_to_mod(y, prime):
            return False
    return True


def exact_holdout_check(values: List[Tuple[Fraction, Fraction]], d: int, coeff: Sequence[Fraction]) -> bool:
    need = 2 * d + 1
    if len(coeff) != need:
        return False
    for x, y in values[need:]:
        if poly_eval(coeff, x) != y:
            return False
    return True


def scan_line(line: dict, max_exact_lines: int) -> Dict[int, dict]:
    reports: Dict[int, dict] = {}
    for mask in ALL_MASKS_SORTED:
        k = mask.bit_count() if hasattr(int, "bit_count") else bin(mask).count("1")
        d = 2 + 2 * k
        values = points_for_mask(line, mask, d)
        report = {
            "line_id": line["line_id"],
            "mask": mask,
            "bit_count": k,
            "d": d,
            "point_count": len(values),
        }

        need = 2 * d + 1
        if len(values) < need + REQUIRED_HOLDOUT:
            report["status"] = "insufficient_points"
            report["required"] = need + REQUIRED_HOLDOUT
            reports[mask] = report
            continue

        mod_ok = True
        for p in PRIMES:
            if not mod_holdout_check(values, d, p):
                report["status"] = "modular_fail"
                report["prime"] = p
                mod_ok = False
                break

        if not mod_ok:
            reports[mask] = report
            continue

        do_exact = max_exact_lines > 0
        if do_exact:
            coeff = interpolate_poly(values, d)
            if coeff is None:
                report["status"] = "exact_solve_error"
                reports[mask] = report
                continue
            if not exact_holdout_check(values, d, coeff):
                report["status"] = "exact_fail"
                report["coeff_head"] = [frac_to_str(c) for c in coeff[: min(6, len(coeff))]]
                report["residual_point_count"] = len(values) - need
                reports[mask] = report
                continue

        report["status"] = "pass" if do_exact else "modular_pass"
        report["coeff_head"] = [frac_to_str(1)]
        reports[mask] = report

    return reports


def scan_families(lines: List[dict], max_exact_lines_per_mask: int, min_lines_for_pass: int) -> Dict[str, object]:
    per_mask_reports: Dict[int, list] = defaultdict(list)
    for line in lines:
        rline = scan_line(line, max_exact_lines_per_mask)
        for mask, payload in rline.items():
            per_mask_reports[mask].append(payload)

    mask_results: List[dict] = []
    passing: List[int] = []

    for mask in ALL_MASKS_SORTED:
        entries = per_mask_reports.get(mask, [])
        tested = len(entries)
        modular_fail = sum(1 for e in entries if e["status"] == "modular_fail")
        exact_fail = sum(1 for e in entries if e["status"] == "exact_fail")
        status = "fail"
        pass_lines = sum(1 for e in entries if e["status"] in {"pass", "modular_pass"})

        if tested >= min_lines_for_pass and modular_fail == 0 and exact_fail == 0:
            status = "pass"
            passing.append(mask)

        line_pattern = "".join("1" if e["status"] in {"pass", "modular_pass"} else "0" for e in sorted(entries, key=lambda x: x["line_id"]))
        if line_pattern and "|" in line_pattern:
            # defensive, should not happen
            line_pattern = line_pattern.replace("|", "")

        sample_line_status = entries[: min(3, len(entries))]
        mask_results.append(
            {
                "mask": mask,
                "bit_count": mask.bit_count() if hasattr(int, "bit_count") else bin(mask).count("1"),
                "d": 2 + 2 * (mask.bit_count() if hasattr(int, "bit_count") else bin(mask).count("1")),
                "status": status,
                "tested_lines": tested,
                "pass_lines": pass_lines,
                "modular_fail_lines": modular_fail,
                "exact_fail_lines": exact_fail,
                "line_pattern": line_pattern,
                "sample_line_status": sample_line_status,
            }
        )

    passing_set = set(passing)
    # family-wise fingerprinting: which family has at least one full-line pass
    families = sorted({line["family_id"] for line in lines})
    line_by_family = defaultdict(list)
    for line in lines:
        line_by_family[line["family_id"]].append(line["line_id"])

    family_results: Dict[str, object] = {}
    for fid in families:
        fid_lines = [line["line_id"] for line in lines if line["family_id"] == fid]
        pass_masks = 0
        fid_entry = {
            "family_id": fid,
            "lines": fid_lines,
            "passing_masks": 0,
            "mask_list": [],
        }

        for mask in sorted(passing_set):
            entries = per_mask_reports.get(mask, [])
            # pass only if any line in this family passes
            if any((e["status"] in {"pass", "modular_pass"}) and e["line_id"] in fid_lines for e in entries):
                fid_entry["passing_masks"] += 1
                fid_entry["mask_list"].append(mask)

        family_results[str(fid)] = fid_entry

    # minimal passing denominators by inclusion
    minimal: List[int] = []
    for m in sorted(passing_set):
        is_minimal = True
        for p in minimal:
            if (p & m) == p:
                is_minimal = False
                break
        if is_minimal:
            minimal.append(m)

    # deterministic fingerprint string + digest
    fp_payload = [
        {
            "mask": mask,
            "bits": mask.bit_count() if hasattr(int, "bit_count") else bin(mask).count("1"),
            "d": 2 + 2 * (mask.bit_count() if hasattr(int, "bit_count") else bin(mask).count("1")),
            "line_pattern": next(r["line_pattern"] for r in mask_results if r["mask"] == mask),
        }
        for mask in sorted(passing_set)
    ]
    fp_blob = json.dumps(fp_payload, sort_keys=True)
    fp_digest = hashlib.sha256(fp_blob.encode()).hexdigest()[:24]

    return {
        "mask_results": mask_results,
        "passing_masks": sorted(passing_set),
        "passing_count": len(passing_set),
        "minimal_masks": minimal,
        "minimal_count": len(minimal),
        "line_count": len(lines),
        "family_results": family_results,
        "denominator_fingerprint": {
            "mask_payload": fp_payload,
            "digest": fp_digest,
        },
        "line_patterns": {str(mask): next(r["line_pattern"] for r in mask_results if r["mask"] == mask) for mask in sorted(passing_set)},
    }


def write_reports(payload: dict, out_json: Path, out_md: Path) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)

    min_masks = payload["scan"]["minimal_masks"]
    pass_count = payload["scan"]["passing_count"]
    lines = payload["scan"]["line_count"]
    signature = payload["target_signature"]
    md_lines = [
        "# Denominator family scan",
        f"timestamp: {payload['timestamp']}",
        f"target wall signature: `{signature}`",
        f"line_count: {lines}",
        f"passing_mask_count: {pass_count}",
        f"minimal_mask_count: {len(min_masks)}",
        f"denominator_fingerprint: {payload['scan']['denominator_fingerprint']['digest']}",
        "",
    ]

    if min_masks:
        md_lines.append("## Minimal passing masks")
        for m in min_masks:
            bits = m.bit_count() if hasattr(int, "bit_count") else bin(m).count("1")
            md_lines.append(f"- mask={format(m, '09b')} bits={bits}")
    else:
        md_lines.append("No mask passed in the configured line-family test.")

    with out_md.open("w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--oracle", default=str(DATA_DIR / "h_rational_probe_oracle.jsonl"))
    p.add_argument("--target-signature", default="")
    p.add_argument("--line-count", type=int, default=6)
    p.add_argument("--line-t-min", type=int, default=-20)
    p.add_argument("--line-t-max", type=int, default=20)
    p.add_argument("--line-t-step", type=int, default=1)
    p.add_argument("--line-max-den", type=int, default=12)
    p.add_argument("--line-points-needed", type=int, default=70)
    p.add_argument("--line-points-max", type=int, default=180)
    p.add_argument("--min-points-per-line", type=int, default=55)
    p.add_argument("--min-lines-per-mask", type=int, default=2)
    p.add_argument("--exact-lines-per-mask", type=int, default=2)
    p.add_argument("--cache", default=str(DATA_DIR / "h_denominator_line_cache.jsonl"))
    p.add_argument("--out-json", default=str(DATA_DIR / "h_denominator_family_scan.json"))
    p.add_argument("--out-md", default=str(DATA_DIR / "h_denominator_family_scan.md"))
    return p


def main() -> None:
    args = make_parser().parse_args()
    start = subprocess.check_output(["date", "+%s"], universal_newlines=True).strip()
    t0 = float(start)

    ensure_bg_binary()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    lines = []

    oracle_rows = parse_oracle_rows(Path(args.oracle))
    selected_rows, target_sig = row_with_signature(oracle_rows, args.target_signature or None)

    cache_path = Path(args.cache)
    cache = line_cache_load(cache_path)

    t_values = build_t_grid(args.line_t_min, args.line_t_max, args.line_t_step, args.line_max_den, args.line_points_needed)

    built_lines = build_lines(
        anchor_rows=selected_rows,
        target_signature=target_sig,
        line_count=args.line_count,
        t_values=t_values,
        directions=DEFAULT_DIRECTIONS,
        max_points_per_line=args.line_points_max,
        min_points_per_line=args.min_points_per_line,
        cache=cache,
        cache_path=cache_path,
    )

    lines_scanned = scan_families(
        built_lines,
        max_exact_lines_per_mask=args.exact_lines_per_mask,
        min_lines_for_pass=args.min_lines_per_mask,
    )

    out = {
        "timestamp": utc_timestamp(),
        "oracle": str(args.oracle),
        "target_signature": target_sig,
        "target_signature_rows": len(selected_rows),
        "total_oracle_rows": len(oracle_rows),
        "line_spec": {
            "requested_lines": args.line_count,
            "built_lines": len(built_lines),
            "line_t": {
                "min": args.line_t_min,
                "max": args.line_t_max,
                "step": args.line_t_step,
                "max_den": args.line_max_den,
            },
            "line_points_needed": args.line_points_needed,
            "line_points_max": args.line_points_max,
            "line_points_min": args.min_points_per_line,
            "line_families": {
                "count": len(DEFAULT_DIRECTIONS),
                "directions": [list(v) for v in DEFAULT_DIRECTIONS],
            },
        },
        "scan": lines_scanned,
    }
    out["runtime_sec"] = round(float(subprocess.check_output(["date", "+%s"], universal_newlines=True).strip()) - t0, 3)

    write_reports(out, Path(args.out_json), Path(args.out_md))

    print(json.dumps(
        {
            "done": True,
            "target_signature": target_sig,
            "line_count": len(built_lines),
            "passing_masks": lines_scanned["passing_count"],
            "minimal_count": lines_scanned["minimal_count"],
            "fingerprint": lines_scanned["denominator_fingerprint"]["digest"],
            "outputs": {
                "json": str(args.out_json),
                "md": str(args.out_md),
                "cache": str(args.cache),
            },
        },
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
