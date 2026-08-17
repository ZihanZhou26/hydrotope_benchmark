#!/usr/bin/env python3
"""Generate exact H samples, probe rational denominator relations, and run diagnostics."""

import argparse
import json
import re
import shutil
import subprocess
import time
import random
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import sympy as sp

import common

ROOT = Path(__file__).resolve().parents[3]
QUESTION_DIR = ROOT
CODE_DIR = QUESTION_DIR / "bots/student-1/code"
ROOT_BG_CPP = QUESTION_DIR / "bg.cpp"
BG_CPP = CODE_DIR / "bg_round3.cpp"
BG_BIN = CODE_DIR / "bg_round3"
DATA_DIR = QUESTION_DIR / "bots/student-1/data"
WALL_CATALOG = common.build_wall_catalog()
SIG_FULL = common.SIG_FULL
PRIMES = (1_000_003, 1_000_033, 1_000_037)


def utc_timestamp() -> str:
    return subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%S"], universal_newlines=True).strip()


class ProbeRow:
    __slots__ = ("sample_id", "free", "omega", "raw_wall_signature", "split", "A_im", "A_re", "H")

    def __init__(
        self,
        sample_id,
        free,
        omega,
        raw_wall_signature,
        split,
        A_im,
        A_re,
        H,
    ):
        self.sample_id = sample_id
        self.free = list(free)
        self.omega = list(omega)
        self.raw_wall_signature = raw_wall_signature
        self.split = split
        self.A_im = A_im
        self.A_re = A_re
        self.H = H


def frac_to_str(v: Fraction) -> str:
    return common.frac_to_str(v)


def parse_fraction(v: str) -> Fraction:
    return common.parse_fraction(v)


def wall_signature(omega: Sequence[Fraction]) -> str:
    return common.serialize_signs(common.wall_sign_map(omega, WALL_CATALOG), WALL_CATALOG)


def sort_by_groups(omega: Sequence[Fraction]) -> List[Fraction]:
    minus = sorted(range(3), key=lambda i: (omega[i] * omega[i], omega[i]))
    plus = sorted(range(3, 6), key=lambda i: (omega[i] * omega[i], omega[i]))
    return [omega[i] for i in minus] + [omega[i] for i in plus]


def ensure_bg_binary() -> None:
    need = not BG_BIN.exists() or not BG_CPP.exists() or BG_CPP.stat().st_mtime < ROOT_BG_CPP.stat().st_mtime
    if need:
        shutil.copy2(ROOT_BG_CPP, BG_CPP)
    if need or not BG_BIN.exists():
        proc = subprocess.run(
            ["g++", "-O2", "-std=c++17", "-o", str(BG_BIN), str(BG_CPP), "-lgmpxx", "-lgmp"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"bg_round3 compile failed: {proc.stderr or proc.stdout}")


def run_bg_round3(omega: Sequence[Fraction]) -> Tuple[Fraction, Fraction]:
    cmd = [
        str(BG_BIN),
        "--amp",
        "-K",
        ",".join(frac_to_str(SIG_FULL[i] * omega[i] * omega[i]) for i in range(6)),
        "-W",
        ",".join(frac_to_str(w) for w in omega),
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"bg failed: {proc.stderr.strip() or proc.stdout.strip()}")
    txt = proc.stdout
    m1 = re.search(r"A_6\s*=\s*\(\s*([^\)]*?)\s*\)\s*\+\s*i\s*\(\s*([^\)]*?)\s*\)", txt)
    if m1:
        return parse_fraction(m1.group(1)), parse_fraction(m1.group(2))
    m2 = re.search(r"A_6\s*=\s*i\s*\*?\s*\(?\s*([^)]*)\s*\)?", txt)
    if m2:
        return Fraction(0), parse_fraction(m2.group(1))
    raise ValueError(f"unparsed bg output: {txt}")


def safe_point(omega: Sequence[Fraction]) -> bool:
    if any(w == 0 for w in omega):
        return False
    if sum(omega) != 0:
        return False
    if sum(SIG_FULL[i] * omega[i] * omega[i] for i in range(6)) != 0:
        return False
    signs = common.wall_sign_map(omega, WALL_CATALOG)
    if any(v == 0 for v in signs.values()):
        return False
    for mask in common.internal_subset_bits(6):
        h, q = common.h_T(omega, mask, SIG_FULL)
        if h == 0 or q == 0:
            return False
    return True


def classify_signature_from_free(free: Sequence[Fraction], sid: str) -> ProbeRow:
    w_unsorted = common.solve_from_free(list(free), SIG_FULL)
    w = sort_by_groups(w_unsorted)
    if not safe_point(w):
        raise ValueError("unsafe")
    return ProbeRow(sid, list(free), list(w), wall_signature(w), "", Fraction(0), Fraction(0), Fraction(0))


def candidate_pool() -> List[Fraction]:
    vals = []
    for n in range(-8, 9):
        if n == 0:
            continue
        vals.extend([
            Fraction(n, 1),
            Fraction(n, 2),
            Fraction(n, 3),
            Fraction(n, 5),
            Fraction(-n, 1),
            Fraction(-n, 2),
            Fraction(-n, 3),
            Fraction(-n, 5),
        ])
    uniq = []
    seen = set()
    for v in vals:
        if v not in seen:
            seen.add(v)
            uniq.append(v)
    return uniq


def free_generator() -> Iterable[List[Fraction]]:
    pool = candidate_pool()
    seed = [
        [Fraction(2, 1), Fraction(-1, 1), Fraction(3, 1), Fraction(1, 1)],
        [Fraction(3, 2), Fraction(-5, 2), Fraction(4, 1), Fraction(-2, 1)],
        [Fraction(-3, 1), Fraction(7, 2), Fraction(2, 1), Fraction(-1, 1)],
        [Fraction(5, 3), Fraction(-4, 3), Fraction(1, 1), Fraction(-2, 3)],
        [Fraction(7, 4), Fraction(-1, 2), Fraction(3, 2), Fraction(-8, 3)],
        [Fraction(11, 5), Fraction(-13, 5), Fraction(7, 3), Fraction(-4, 1)],
        [Fraction(13, 6), Fraction(-7, 6), Fraction(1, 1), Fraction(-5, 2)],
    ]
    for s in seed:
        yield s
    rng = random.Random(1729)
    used = set()
    while True:
        a = rng.choice(pool)
        b = rng.choice(pool)
        c = rng.choice(pool)
        d = rng.choice(pool)
        key = (a, b, c, d)
        if key in used:
            continue
        used.add(key)
        yield [a, b, c, d]


def probe_from_free(free: Sequence[Fraction], sid: str) -> ProbeRow:
    w_unsorted = common.solve_from_free(list(free), SIG_FULL)
    w = sort_by_groups(w_unsorted)
    if not safe_point(w):
        raise ValueError("unsafe")
    a_re, a_im = run_bg_round3(w)
    if a_im == 0:
        raise ValueError("A_im_zero")
    prod = Fraction(1, 1)
    for x in w:
        prod *= x
    if prod == 0:
        raise ValueError("zero_omega_product")
    sig = wall_signature(w)
    return ProbeRow(sid, list(free), list(w), sig, "", a_im, a_re, a_im / prod)


def prescan_signatures(trials: int = 1500) -> Tuple[Dict[str, int], Dict[str, List[ProbeRow]]]:
    counts: Counter[str] = Counter()
    reps: Dict[str, List[ProbeRow]] = defaultdict(list)
    it = free_generator()
    for k in range(trials):
        try:
            row = classify_signature_from_free(next(it), f"pre-{k:04d}")
        except Exception:
            continue
        counts[row.raw_wall_signature] += 1
        if len(reps[row.raw_wall_signature]) < 16:
            reps[row.raw_wall_signature].append(row)
    return dict(counts), reps


def build_oracle(target_sig: str, total: int, train: int, holdout: int) -> List[ProbeRow]:
    out: List[ProbeRow] = []
    used = set()
    it = free_generator()
    attempts = 0
    while len(out) < total and attempts < 200000:
        attempts += 1
        free = next(it)
        try:
            row = probe_from_free(free, f"s{len(out):04d}")
        except Exception:
            continue
        if row.raw_wall_signature != target_sig:
            continue
        key = tuple(frac_to_str(x) for x in row.omega)
        if key in used:
            continue
        used.add(key)
        out.append(row)
    if len(out) < total:
        raise RuntimeError(f"could not build {total} samples in signature {target_sig}, only {len(out)}")

    out.sort(key=lambda r: tuple(frac_to_str(x) for x in r.omega))
    for i, r in enumerate(out):
        if i < train:
            r.split = "train"
        elif i < train + holdout:
            r.split = "holdout"
        else:
            r.split = "extra"
    return out


def write_oracle_jsonl(rows: Sequence[ProbeRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for r in rows:
            f.write(
                json.dumps(
                    {
                        "sample_id": r.sample_id,
                        "split": r.split,
                        "free_w": [frac_to_str(x) for x in r.free],
                        "omega": [frac_to_str(x) for x in r.omega],
                        "A_im": frac_to_str(r.A_im),
                        "A_re": frac_to_str(r.A_re),
                        "H": frac_to_str(r.H),
                        "wall_signature_raw": r.raw_wall_signature,
                    }
                )
                + "\n"
            )


def monomials_deg(d: int) -> List[Tuple[int, int, int, int, int]]:
    out = []
    for e0 in (0, 1):
        if e0 > d:
            continue
        r = d - e0
        for e1 in range(r + 1):
            for e2 in range(r - e1 + 1):
                for e3 in range(r - e1 - e2 + 1):
                    e4 = r - e1 - e2 - e3
                    out.append((e0, e1, e2, e3, e4))
    return out


def frac_mod(v: Fraction, p: int) -> int:
    return (v.numerator % p) * pow(v.denominator % p, p - 2, p) % p


def mono_eval(omega: Sequence[Fraction], e: Tuple[int, int, int, int, int]) -> Fraction:
    out = Fraction(1, 1)
    vars_x = list(omega)[1:6]
    for x, ep in zip(vars_x, e):
        if ep:
            out *= x ** ep
    return out


def mono_eval_mod(omega: Sequence[Fraction], e: Tuple[int, int, int, int, int], mod: int) -> int:
    out = 1
    vars_x = list(omega)[1:6]
    for x, ep in zip(vars_x, e):
        if not ep:
            continue
        xv = x.numerator % mod
        xv = xv * pow(x.denominator % mod, mod - 2, mod) % mod
        out = (out * pow(xv, ep, mod)) % mod
    return out


def rref_rank_nullspace_mod(mat: List[List[int]], mod: int):
    A = [row[:] for row in mat]
    m = len(A)
    n = len(A[0]) if m else 0
    row = 0
    pivots = []
    pivot_rows = []
    col = 0

    while row < m and col < n:
        pivot = row
        while pivot < m and A[pivot][col] % mod == 0:
            pivot += 1
        if pivot == m:
            col += 1
            continue
        A[row], A[pivot] = A[pivot], A[row]
        inv = pow(A[row][col], mod - 2, mod)
        for j in range(col, n):
            A[row][j] = (A[row][j] * inv) % mod
        for i in range(m):
            if i == row:
                continue
            fac = A[i][col]
            if fac == 0:
                continue
            for j in range(col, n):
                A[i][j] = (A[i][j] - fac * A[row][j]) % mod
        pivots.append(col)
        pivot_rows.append(row)
        row += 1
        col += 1

    rank = len(pivots)
    free = [c for c in range(n) if c not in pivots]

    basis = []
    if rank == n:
        return rank, basis

    for fcol in free:
        vec = [0] * n
        vec[fcol] = 1
        for pcol, prow in reversed(list(zip(pivots, pivot_rows))):
            vec[pcol] = (-A[prow][fcol]) % mod
        basis.append(vec)
    return rank, basis


def test_degree(rows: Sequence[ProbeRow], e: int) -> Dict:
    monP = monomials_deg(e + 2)
    monQ = monomials_deg(e)
    W = len(monP) + len(monQ)
    if len(rows) <= W:
        return {
            "e": e,
            "basis_P": len(monP),
            "basis_Q": len(monQ),
            "cols": W,
            "rows": len(rows),
            "status": "insufficient_rows",
            "prime_results": [],
        }

    prime_results = []
    best_qvec = []
    candidate_found = False

    for p in PRIMES[:2]:
        mat = []
        for r in rows:
            h = frac_mod(r.H, p)
            row = [mono_eval_mod(r.omega, e, p) for e in monP]
            for exp in monQ:
                row.append((-h * mono_eval_mod(r.omega, exp, p)) % p)
            mat.append(row)
        rank, ns = rref_rank_nullspace_mod(mat, p)
        nq = W - rank
        qvec = None
        for v in ns:
            if any(v[len(monP):]):
                qvec = v
                break
        prime_results.append({
            "prime": p,
            "rank": rank,
            "nullity": nq,
            "null_vectors": len(ns),
            "has_q_nonzero": qvec is not None,
        })
        if qvec is not None:
            candidate_found = True
            best_qvec = qvec
            # keep first q nonzero if needed
            if not best_qvec:
                best_qvec = qvec

    return {
        "e": e,
        "basis_P": len(monP),
        "basis_Q": len(monQ),
        "cols": W,
        "rows": len(rows),
        "prime_results": prime_results,
        "has_candidate": candidate_found,
        "qvec_example": best_qvec,
        "status": "ok" if candidate_found else "no_q_candidate",
    }


def reconstruct_candidate(rows: Sequence[ProbeRow], e: int):
    monP = monomials_deg(e + 2)
    monQ = monomials_deg(e)
    W = len(monP) + len(monQ)
    sample_count = min(len(rows), max(W + 10, 80))
    mat = []
    for r in rows[:sample_count]:
        h = r.H
        row = [mono_eval(r.omega, ex) for ex in monP]
        for ex in monQ:
            row.append(-h * mono_eval(r.omega, ex))
        mat.append(row)
    M = sp.Matrix(mat)
    ns = M.nullspace()
    if not ns:
        return None, None

    for vec in ns:
        vec = [sp.nsimplify(v) for v in vec]
        # normalize using first nonzero
        nz = next((i for i, v in enumerate(vec) if v != 0), None)
        if nz is None:
            continue
        scale = vec[nz]
        vec = [v / scale for v in vec]
        good = True
        coeff = []
        for v in vec:
            if isinstance(v, sp.Rational):
                coeff.append(Fraction(v.p, v.q))
            else:
                c = Fraction(v)
                coeff.append(c)
        # quick in/out checks
        # use train/holdout split from rows
        ok30 = []
        for r in rows[-30:]:
            P = Fraction(0, 1)
            Q = Fraction(0, 1)
            for c, ex in zip(coeff[: len(monP)], monP):
                P += c * mono_eval(r.omega, ex)
            for c, ex in zip(coeff[len(monP):], monQ):
                Q += c * mono_eval(r.omega, ex)
            if P != r.H * Q:
                ok30.append(r.sample_id)
                if len(ok30) > 6:
                    good = False
                    break
        if good:
            return coeff, (monP, monQ)

    return None, (monP, monQ)


def test_poly_mod(rows: Sequence[ProbeRow], coeffs: Sequence[Fraction], monP, monQ, p: int) -> int:
    monP = list(monP)
    monQ = list(monQ)
    fails = 0
    cQ = coeffs[len(monP):]
    cP = coeffs[: len(monP)]
    for r in rows:
        val = 0
        for c, e in zip(cP, monP):
            val = (val + frac_mod(c, p) * mono_eval_mod(r.omega, e, p)) % p
        vq = 0
        h = frac_mod(r.H, p)
        for c, e in zip(cQ, monQ):
            vq = (vq + frac_mod(c, p) * mono_eval_mod(r.omega, e, p)) % p
        rhs = (h * vq) % p
        if val != rhs:
            fails += 1
            if fails >= 10:
                break
    return fails


def factor_q(coeffs: Sequence[Fraction], monQ: Sequence[Tuple[int, int, int, int, int]]) -> str:
    syms = sp.symbols("w2 w3 w4 w5 w6")
    q = sp.Integer(0)
    for c, e in zip(coeffs, monQ):
        term = sp.Integer(c.numerator)
        if c.denominator != 1:
            term = sp.Rational(c.numerator, c.denominator)
        for sym, ep in zip(syms, e):
            if ep:
                term *= sym ** ep
        q += term
    try:
        return str(sp.factor(sp.expand(q)))
    except Exception:
        return "factorization_failed"


def parse_family_lines(seed: ProbeRow) -> List[Tuple[Tuple[Fraction, Fraction], ...]]:
    base = [Fraction(v) for v in seed.free]
    dirs = [
        (Fraction(1, 1), Fraction(-1, 1), Fraction(0, 1), Fraction(0, 1)),
        (Fraction(0, 1), Fraction(1, 1), Fraction(-1, 1), Fraction(0, 1)),
        (Fraction(0, 1), Fraction(0, 1), Fraction(1, 1), Fraction(-1, 1)),
    ]
    fams = []
    for d in dirs:
        fams.append(tuple((a, b) for a, b in zip(base, d)))
    return fams


def curve_from_family(fam: Tuple[Tuple[Fraction, Fraction], ...], t: Fraction):
    free = [a + b * t for a, b in fam]
    free_sum = sum(free)
    w = sort_by_groups(common.solve_from_free(free, SIG_FULL))
    return w, free_sum


def collect_curve_points(fam: Tuple[Tuple[Fraction, Fraction], ...], target_sig: str, max_points: int = 120):
    out = []
    seen = set()
    steps = 160
    for step in range(-steps, steps + 1):
        t = Fraction(step, 2 * steps + 1)
        try:
            w, free_sum = curve_from_family(fam, t)
        except Exception:
            continue
        if any(x == 0 for x in w):
            continue
        if wall_signature(w) != target_sig:
            continue
        if not safe_point(w):
            continue
        key = tuple(frac_to_str(x) for x in w)
        if key in seen:
            continue
        seen.add(key)
        try:
            _, a_im = run_bg_round3(w)
        except Exception:
            continue
        if a_im == 0:
            continue
        prod = Fraction(1, 1)
        for x in w:
            prod *= x
        if prod == 0:
                continue
        H = a_im / prod
        out.append({
            "t": t,
            "omega": w,
            "H": H,
            "free_sum": free_sum,
        })
        if len(out) >= max_points:
            break
    out.sort(key=lambda p: float(p["t"]))
    return out


def q_mask_value(mask: int, omega: Sequence[Fraction]) -> Fraction:
    a = [omega[i] ** 2 for i in range(3)]
    b = [omega[3 + i] ** 2 for i in range(3)]
    val = Fraction(1, 1)
    for i in range(3):
        for j in range(3):
            if (mask >> (3 * i + j)) & 1:
                val *= a[i] + b[j]
    return val

def mask_curve_ok(mask: int, pts: List[Dict], degree: int) -> Dict:
    d = 2 + 2 * degree
    need = 2 * d + 1
    if len(pts) < need + 3:
        return {"status": "insufficient_points", "got": len(pts), "need": need}

    ts = []
    vals = []
    for row in pts[: need + 3]:
        t = sp.Rational(row["t"].numerator, row["t"].denominator)
        H = sp.Rational(row["H"].numerator, row["H"].denominator)
        s = sp.Rational(row["free_sum"].numerator, row["free_sum"].denominator)
        Q = sp.Rational(q_mask_value(mask, row["omega"]).numerator, q_mask_value(mask, row["omega"]).denominator)
        vals.append(sp.expand(H * Q * (s ** d)))
        ts.append(t)

    z = sp.symbols("z")
    poly = sp.interpolate(list(zip(ts[: need], vals[: need])), z)
    poly = sp.expand(poly.as_poly(z).as_expr())
    if sp.Poly(poly, z).degree() > 2 * d:
        return {"status": "degree_fail", "poly_degree": int(sp.Poly(poly, z).degree()), "limit": 2 * d}

    # check extra
    for row in pts[need : need + 10]:
        t = sp.Rational(row["t"].numerator, row["t"].denominator)
        H = sp.Rational(row["H"].numerator, row["H"].denominator)
        s = sp.Rational(row["free_sum"].numerator, row["free_sum"].denominator)
        Q = sp.Rational(q_mask_value(mask, row["omega"]).numerator, q_mask_value(mask, row["omega"]).denominator)
        rhs = sp.expand(H * Q * (s ** d))
        if sp.expand(poly.subs(z, t)) != rhs:
            return {"status": "interpolate_fail", "poly_degree": int(sp.Poly(poly, z).degree()), "limit": 2 * d}

    return {"status": "pass", "poly_degree": int(sp.Poly(poly, z).degree()), "poly": str(poly)}


def denominator_family_scan(target_sig: str, seed_row: ProbeRow) -> Dict:
    fams = parse_family_lines(seed_row)
    curve_points = [collect_curve_points(f, target_sig, max_points=140) for f in fams]
    passing = []
    all_results = {}
    for mask in range(1 << 9):
        k = bin(mask).count("1")
        curve_ok = True
        for pts in curve_points:
            rpt = mask_curve_ok(mask, pts, k)
            if rpt["status"] != "pass":
                curve_ok = False
                break
        all_results[mask] = rpt if not curve_ok else {"status": "pass", "poly_degree": rpt["poly_degree"], "poly": rpt.get("poly", "")}
        if curve_ok:
            passing.append(mask)

    insufficient = [len(c) < 45 for c in curve_points]
    return {
        "curves": ["[" + ", ".join(f"({frac_to_str(a)},{frac_to_str(b)})" for a, b in fam) + "]" for fam in fams],
        "results": {format(mask, "09b"): all_results[mask] for mask in sorted(all_results)},
        "passing_masks": [format(m, "09b") for m in passing],
        "full_mask_pass": ("111111111" in [format(m, "09b") for m in passing]),
        "curve_sizes": [len(c) for c in curve_points],
        "curve_sufficient_points": [not b for b in insufficient],
    }


def generate_extra_signature_rows(target_sig: str, signature_counts: Dict[str, int], base_rows: List[ProbeRow], n: int = 40) -> List[ProbeRow]:
    if n <= 0:
        return []
    out = []
    if target_sig in signature_counts and signature_counts[target_sig] >= n:
        # if enough entries in prescan representation, sample from there if available in base rows
        for r in base_rows:
            if r.raw_wall_signature == target_sig:
                out.append(r)
                if len(out) >= n:
                    return out

    # fallback: rebuild targeted signature rows
    try:
        out.extend(build_oracle(target_sig, total=max(n, 30), train=0, holdout=0)[:n])
    except Exception:
        pass
    return out[:n]


def run_probe(train: int = 560, holdout: int = 160) -> Dict:
    t0 = time.time()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ensure_bg_binary()

    sig_counts, prescan = prescan_signatures(2500)
    if not sig_counts:
        raise RuntimeError("prescan failed")
    target_sig, target_count = max(sig_counts.items(), key=lambda kv: kv[1])

    rows = build_oracle(target_sig, total=train + holdout, train=train, holdout=holdout)
    json_path = DATA_DIR / "h_rational_probe_oracle.jsonl"
    write_oracle_jsonl(rows, json_path)

    train_rows = [r for r in rows if r.split == "train"]
    hold_rows = [r for r in rows if r.split == "holdout"]

    all_deg = []
    candidate = None
    for e in range(0, 8):
        dres = test_degree(rows, e)
        all_deg.append(dres)
        if dres["status"] == "ok" and dres.get("has_candidate"):
            candidate = dict(dres)
            candidate["e"] = e
            break

    recon = {"status": "none", "attempted": False}
    coeffs = None
    monP = monQ = []
    if candidate is not None:
        e = candidate["e"]
        coeffs, (monP, monQ) = reconstruct_candidate(rows, e)
        recon["attempted"] = True
        if coeffs is None:
            recon["status"] = "not_reconstructible"
        else:
            recon["status"] = "ok"
            recon["coeff_count"] = len(coeffs)
            fail_samples = []
            for r in hold_rows[:30]:
                lhs = sum(c * mono_eval(r.omega, ex) for c, ex in zip(coeffs[: len(monP)], monP))
                rhs = r.H * sum(c * mono_eval(r.omega, ex) for c, ex in zip(coeffs[len(monP):], monQ))
                if lhs != rhs:
                    fail_samples.append(r.sample_id)
                    if len(fail_samples) >= 20:
                        break
            recon["fail_sample"] = fail_samples
            recon["prime_check"] = {
                "prime": PRIMES[1],
                "fail_count": test_poly_mod(hold_rows[:50], coeffs, monP, monQ, PRIMES[1]),
            }
            recon["Q_factor"] = factor_q(coeffs[len(monP):], monQ)

    # same-Q cross-signature checks
    cross = []
    extra_sig = [(k, v) for k, v in sig_counts.items() if k != target_sig]
    extra_sig = sorted(extra_sig, key=lambda kv: kv[1], reverse=True)[:2]
    if coeffs is not None:
        for sig, count in extra_sig:
            try:
                other_rows = build_oracle(sig, total=min(40, max(30, train // 3)), train=0, holdout=0)
            except Exception:
                continue
            good = True
            fails = 0
            for r in other_rows:
                p = sum(c * mono_eval(r.omega, ex) for c, ex in zip(coeffs[: len(monP)], monP))
                qv = sum(c * mono_eval(r.omega, ex) for c, ex in zip(coeffs[len(monP):], monQ))
                if p != r.H * qv:
                    fails += 1
                    if fails > 2:
                        good = False
                        break
            cross.append({"signature": sig, "count": count, "checked": len(other_rows), "pass": good})

    seed_row = rows[0] if rows else next(iter(prescan.values()))[0]
    denom_scan = denominator_family_scan(target_sig, seed_row)

    # orbit-feature fit
    orbit_report = {"status": "skipped", "reason": "not_applicable"}
    if coeffs is not None and monP and len(monP[0]) == 5:
        degree = candidate["e"] + 2
        if degree % 2 == 0:
            ok_even = True
            for c, ex in zip(coeffs, monP + monQ):
                if c == 0:
                    continue
                if any(v & 1 for v in ex):
                    ok_even = False
                    break
            if ok_even:
                from h_building_blocks import run_orbit_feature_fit

                orbit_report = run_orbit_feature_fit(rows, coeffs[: len(monP)], coeffs[len(monP):], monP, monQ, degree, DATA_DIR)

    report = {
        "created_utc": utc_timestamp(),
        "commands": [
            f"cp {ROOT_BG_CPP} {BG_CPP}",
            f"g++ -O2 -std=c++17 -o {BG_BIN} {BG_CPP} -lgmpxx -lgmp",
            "python3 h_rational_probe.py",
        ],
        "environment": {
            "bg_source": str(ROOT_BG_CPP),
            "bg_binary": str(BG_BIN),
            "samples_total": len(rows),
            "train": len(train_rows),
            "holdout": len(hold_rows),
            "target_signature": target_sig,
            "target_signature_count": target_count,
        },
        "prescan_counts": sig_counts,
        "modular_denominator_scan": {
            "degrees": all_deg,
            "candidate": candidate,
            "reconstruction": recon,
            "runtime_sec": time.time() - t0,
        },
        "denominator_family_scan": denom_scan,
        "cross_signatures": cross,
        "orbit_feature_fit": orbit_report,
        "artifact_paths": {
            "oracle_jsonl": str(json_path),
            "report_json": str(DATA_DIR / "h_rational_probe_report.json"),
            "report_md": str(DATA_DIR / "h_rational_probe_report.md"),
        },
    }

    out_json = DATA_DIR / "h_rational_probe_report.json"
    with out_json.open("w") as f:
        json.dump(report, f, indent=2)

    md = [
        "# H-rational probe",
        f"- Target signature: `{target_sig}`",
        f"- Samples: {len(rows)} ({len(train_rows)} train, {len(hold_rows)} holdout)",
        f"- Candidate degree: {candidate['e'] if candidate else None}",
        f"- Reconstruction: {recon['status']}",
    ]
    if candidate is not None and isinstance(candidate.get("qvec_example"), list):
        md.append(f"- Q nonzero candidate exists at e={candidate['e']}")
    md.append(f"- Passing masks in denominator-family scan: {len(denom_scan['passing_masks'])}")
    md.append(f"- full nine-factor mask pass: {denom_scan['full_mask_pass']}")
    md.append(f"- Orbit fit status: {orbit_report.get('status')}")
    (DATA_DIR / "h_rational_probe_report.md").write_text("\n".join(md) + "\n")

    return report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--train", type=int, default=560)
    p.add_argument("--holdout", type=int, default=160)
    args = p.parse_args()

    report = run_probe(train=args.train, holdout=args.holdout)
    print(json.dumps({"done": True, "target_signature": report["environment"]["target_signature"], "candidate_e": (report["modular_denominator_scan"]["candidate"]["e"] if report["modular_denominator_scan"]["candidate"] else None)}, indent=2))


if __name__ == "__main__":
    main()
