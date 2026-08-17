#!/usr/bin/env python3
"""Round-2 exact computation batch for student-2."""

import json
import random
import re
import shutil
import subprocess
from fractions import Fraction
from itertools import combinations, permutations, product
from math import gcd
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import sympy as sp

SIGMA = (-1, -1, -1, 1, 1, 1)
MINUS_IDX = (0, 1, 2)
PLUS_IDX = (3, 4, 5)
KNOWN_WORDS = {
    "+-+--+",
    "+--++-",
    "+--+-+",
    "+---++",
    "-+++--",
    "-++-+-",
    "-++--+",
    "-+-++-",
}


def frac_to_str(v: Fraction) -> str:
    if v.denominator == 1:
        return str(v.numerator)
    return f"{v.numerator}/{v.denominator}"


def str_to_frac(v: str) -> Fraction:
    s = v.strip()
    if "/" in s:
        a, b = s.split("/")
        return Fraction(int(a), int(b))
    return Fraction(int(s), 1)


def sign_of(v: Fraction) -> str:
    if v > 0:
        return "+"
    if v < 0:
        return "-"
    return "0"


def lcm(a: int, b: int) -> int:
    return abs(a) // gcd(a, b) * abs(b) if a and b else abs(a or b)


def parse_fraction(text: str) -> Fraction:
    t = text.strip()
    if "/" in t:
        n, d = t.split("/")
        return Fraction(int(n), int(d))
    return Fraction(int(t), 1)


def parse_bg_output(text: str, n: int):
    omega_m = re.search(r"omega\s*=\s*\{([^}]*)\}", text)
    if not omega_m:
        raise RuntimeError("failed to parse omega")
    raw_omega = [part.strip() for part in omega_m.group(1).split(",") if part.strip()]
    if len(raw_omega) != n:
        raise RuntimeError(f"expected {n} omegas, got {len(raw_omega)}")
    omega = [parse_fraction(x) for x in raw_omega]

    amp_complex = re.search(r"A_\d+\s*=\s*\(([^)]*)\)\s*\+\s*i\s*\(([^)]*)\)", text)
    amp_pure = re.search(r"A_\d+\s*=\s*i\s*\*\s*\(([^)]*)\)", text)
    if amp_complex:
        re_val = parse_fraction(amp_complex.group(1))
        im_val = parse_fraction(amp_complex.group(2))
    elif amp_pure:
        re_val = Fraction(0, 1)
        im_val = parse_fraction(amp_pure.group(1))
    else:
        raise RuntimeError("failed to parse amplitude")
    return omega, re_val, im_val


class BGOracle:
    def __init__(self, binary: Path):
        self.binary = Path(binary)

    def run(self, args: Sequence[str]) -> Tuple[List[Fraction], Fraction, Fraction]:
        proc = subprocess.run(
            [str(self.binary), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=60,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"bg failed: {proc.stderr.strip()}")
        n = self._extract_n(args)
        return parse_bg_output(proc.stdout, n)

    @staticmethod
    def _extract_n(args: Sequence[str]) -> int:
        for i, a in enumerate(args):
            if a == "-n" and i + 1 < len(args):
                return int(args[i + 1])
        if "--amp" in args:
            k_i = args.index("-W")
            w_raw = args[k_i + 1]
            return len([x for x in w_raw.split(",") if x.strip()])
        raise RuntimeError("missing n")

    def solve_on_shell(self, n: int, free_w: Sequence[Fraction], sigma: Sequence[int] = SIGMA, g: int = 1):
        args = [
            "-n",
            str(n),
            "-w",
            ",".join(frac_to_str(Fraction(x)) for x in free_w),
            "-s",
            ",".join(str(int(x)) for x in sigma),
            "-g",
            str(g),
        ]
        return self.run(args)

    def solve_raw(self, k: Sequence[Fraction], w: Sequence[Fraction], g: int = 1):
        args = [
            "--amp",
            "-K",
            ",".join(frac_to_str(Fraction(x)) for x in k),
            "-W",
            ",".join(frac_to_str(Fraction(x)) for x in w),
            "-g",
            str(g),
        ]
        return self.run(args)


def safe_on_shell(oracle, n, free, sigma=SIGMA, g=1):
    try:
        return oracle.solve_on_shell(n, free, sigma=sigma, g=g), None
    except Exception as exc:
        return None, str(exc)

def safe_raw(oracle, k, w, g=1):
    try:
        return oracle.solve_raw(k, w, g=g), None
    except Exception as exc:
        return None, str(exc)


class SixPoint:
    def __init__(self, b, c, d, e):
        self.b = Fraction(b)
        self.c = Fraction(c)
        self.d = Fraction(d)
        self.e = Fraction(e)

        S = self.b + self.c + self.d + self.e
        if S == 0:
            raise ValueError("S=0")
        r = self.b * self.c - self.d * self.e

        a = self.d + self.e + r / S
        f = self.b + self.c - r / S
        omega = (-a, self.b, self.c, self.d, self.e, -f)
        self.omega = tuple(omega)

        C = self.omega[0] * self.omega[1] * self.omega[2] + self.omega[3] * self.omega[4] * self.omega[5]
        Delta = Fraction(1, 1)
        pair_q = {}
        for m in MINUS_IDX:
            for p in PLUS_IDX:
                qv = self.omega[p] ** 2 - self.omega[m] ** 2
                pair_q["q_%d_%d" % (m + 1, p + 1)] = qv
                Delta *= (self.omega[m] + self.omega[p])
        triple_q = {}
        for m in MINUS_IDX:
            for p, q in combinations(PLUS_IDX, 2):
                triple_q["q_%d_%d%d" % (m + 1, p + 1, q + 1)] = self.omega[p] ** 2 + self.omega[q] ** 2 - self.omega[m] ** 2

        self.pair_q = pair_q
        self.triple_q = triple_q
        self.C = C
        self.Delta = Delta

    def conservation(self):
        sum_omega = sum(self.omega)
        sum_mom = sum(s * (w * w) for s, w in zip(SIGMA, self.omega))
        return {
            "sum_omega": sum_omega,
            "sum_omega_ok": sum_omega == 0,
            "sum_momentum": sum_mom,
            "sum_momentum_ok": sum_mom == 0,
        }

    def sorted_word(self):
        entries = [(i, self.omega[i] * self.omega[i]) for i in range(6)]
        orded = sorted(entries, key=lambda it: (abs(it[1]), it[0]), reverse=True)
        order = [i for i, _ in orded]
        strict = all(orded[i][1] != orded[i + 1][1] for i in range(5))
        word = "".join("+" if SIGMA[i] > 0 else "-" for i in order)
        return word, strict, order

    def sign_maps(self):
        return (
            {k: sign_of(v) for k, v in self.pair_q.items()},
            {k: sign_of(v) for k, v in self.triple_q.items()},
        )

    def is_generic(self):
        chk = self.conservation()
        if not (chk["sum_omega_ok"] and chk["sum_momentum_ok"]):
            return False
        if any(v == 0 for v in self.pair_q.values()):
            return False
        if any(v == 0 for v in self.triple_q.values()):
            return False
        return True

    def primitive_scale(self) -> Tuple[List[int], Fraction]:
        nums = [x.numerator for x in self.omega]
        dens = [x.denominator for x in self.omega]
        l = 1
        for d in dens:
            l = lcm(l, d)
        scaled = [n * (l // d) for n, d in zip(nums, dens)]
        g = 0
        for x in scaled:
            g = gcd(g, abs(x))
        if g == 0:
            g = 1
        primitive = [x // g for x in scaled]
        return primitive, Fraction(l, g)


def build_bg(question_root: Path, log: Dict[str, object]) -> Path:
    src = question_root / "bg.cpp"
    dst = question_root / "bots" / "student-2" / "bg.cpp"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

    cmd = [
        "g++",
        "-O2",
        "-std=c++17",
        "-o",
        str(question_root / "bots" / "student-2" / "bg"),
        str(dst),
        "-lgmpxx",
        "-lgmp",
    ]
    ver = subprocess.run(["g++", "--version"], stdout=subprocess.PIPE, universal_newlines=True).stdout.splitlines()[0]
    log["build"] = {
        "binary": str(question_root / "bots" / "student-2" / "bg"),
        "command": " ".join(cmd),
        "compiler_version": ver,
    }
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if proc.returncode != 0:
        log["build_error"] = proc.stderr.strip()
        raise RuntimeError(proc.stderr)
    log["build_ok"] = True
    return question_root / "bots" / "student-2" / "bg"


def rational_poly_fit(points: Sequence[Tuple[Fraction, Fraction]], tvar: sp.Symbol, deg_max: int) -> Dict[str, object]:
    if len(points) < 2:
        return {"status": "insufficient", "count": len(points)}
    interp_pts = [(sp.Rational(p.numerator, p.denominator), sp.Rational(y.numerator, y.denominator)) for p, y in points]
    expr = sp.interpolate(interp_pts, tvar)
    poly = sp.Poly(sp.expand(expr), tvar, domain="QQ")
    deg = int(poly.degree())
    return {
        "status": "ok" if deg <= deg_max else "degree_exceeded",
        "deg": deg,
        "count": len(points),
        "expr": str(poly.as_expr()),
        "poly": poly,
    }


def poly_residuals(poly: sp.Poly, tvar: sp.Symbol, points: Sequence[Tuple[Fraction, Fraction]]) -> List[Dict[str, str]]:
    out = []
    for t, y in points:
        xv = sp.Rational(t.numerator, t.denominator)
        pred = sp.together(poly.eval(xv))
        p = Fraction(int(pred.as_numer_denom()[0]), int(pred.as_numer_denom()[1]))
        out.append({"t": frac_to_str(t), "obs": frac_to_str(y), "pred": frac_to_str(p), "res": frac_to_str(p - y)})
    return out


def symbolic_C_poly(b0: Fraction, d0: Fraction, c0: Fraction, e0: Fraction) -> sp.Poly:
    t = sp.Symbol("t")
    b = sp.Rational(b0.numerator, b0.denominator) + t
    d = sp.Rational(d0.numerator, d0.denominator) - t
    c = sp.Rational(c0.numerator, c0.denominator)
    e = sp.Rational(e0.numerator, e0.denominator)
    S = b + c + d + e
    r = b * c - d * e
    a = d + e + r / S
    f = b + c - r / S
    C = sp.expand((-a) * b * c + d * e * (-f))
    return sp.Poly(sp.expand(C), t)


def point_record(point: SixPoint, omega: Sequence[Fraction], ar, ai) -> Dict[str, object]:
    chk = point.conservation()
    pair_sign, triple_sign = point.sign_maps()
    word, strict, order = point.sorted_word()
    F = ai * point.C
    return {
        "b": frac_to_str(point.b),
        "c": frac_to_str(point.c),
        "d": frac_to_str(point.d),
        "e": frac_to_str(point.e),
        "omega": [frac_to_str(x) for x in omega],
        "sum_omega_ok": chk["sum_omega_ok"],
        "sum_momentum_ok": chk["sum_momentum_ok"],
        "sum_omega": frac_to_str(chk["sum_omega"]),
        "sum_momentum": frac_to_str(chk["sum_momentum"]),
        "pair_signs": pair_sign,
        "triple_signs": triple_sign,
        "sorted_word": word,
        "sorted_word_strict": strict,
        "sorted_order": order,
        "C": frac_to_str(point.C),
        "Delta": frac_to_str(point.Delta),
        "Delta_eq_C3": point.Delta == point.C ** 3,
        "amp_re": frac_to_str(ar),
        "amp_im": frac_to_str(ai),
        "pure_im": ar == 0,
        "C_times_amp_im": frac_to_str(F),
    }


def pos_frac(v: Fraction) -> Fraction:
    return v if v > 0 else Fraction(0, 1)


def compact_H(x: Fraction, a: Fraction, b: Fraction) -> Fraction:
    return x - pos_frac(x - a * a) - pos_frac(x - b * b) + pos_frac(x - a * a - b * b)


def wall_pole_subtracted(point: SixPoint, amp_im: Fraction):
    total = Fraction(0, 1)
    terms = []
    for m in MINUS_IDX:
        for pair in combinations(PLUS_IDX, 2):
            p, q = pair
            t = [x for x in PLUS_IDX if x not in pair][0]
            r, s = [x for x in MINUS_IDX if x != m]
            w_m = point.omega[m]
            w_p = point.omega[p]
            w_q = point.omega[q]
            w_t = point.omega[t]
            w_r = point.omega[r]
            w_s = point.omega[s]
            Q = w_p * w_p + w_q * w_q - w_m * w_m
            if Q <= 0:
                continue
            d = Fraction(2, 1) * (w_m + w_p) * (w_m + w_q)
            if d == 0:
                continue
            x_left = min(w_m * w_m, Q)
            x_right = min(w_t * w_t, Q)
            H1 = compact_H(x_left, w_p, w_q)
            H2 = compact_H(x_right, w_r, w_s)
            pole = -Fraction(64, 1) * w_m * w_t * (Q * Q) * H1 * H2 / d
            total += pole
            terms.append({
                "m": m,
                "p": p,
                "q": q,
                "t": t,
                "r": r,
                "s": s,
                "Q": frac_to_str(Q),
                "d": frac_to_str(d),
                "x_left": frac_to_str(x_left),
                "x_right": frac_to_str(x_right),
                "H1": frac_to_str(H1),
                "H2": frac_to_str(H2),
                "P_T": frac_to_str(pole),
            })
    return amp_im - total, total, terms


def section1(oracle: BGOracle, known_words: set):
    vals = [Fraction(v) for v in (-8, -6, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6)]
    samples = []
    seen_words = set()
    seen_exact = []
    attempts = 0

    for b in vals:
        for c in vals:
            for d in vals:
                for e in vals:
                    attempts += 1
                    try:
                        p = SixPoint(b, c, d, e)
                    except Exception:
                        continue
                    if not p.is_generic():
                        continue
                    res, ferr = safe_on_shell(oracle, 6, [p.b, p.c, p.d, p.e])
                    if res is None:
                        continue
                    omega, ar, ai = res
                    rec = point_record(p, omega, ar, ai)
                    samples.append(rec)
                    seen_words.add(rec["sorted_word"])
                    if rec["sorted_word"] not in known_words and len(seen_exact) < 1:
                        seen_exact.append(rec["sorted_word"])
                    if len(samples) >= 48 and seen_words.issuperset(known_words):
                        break
                if len(samples) >= 48 and seen_words.issuperset(known_words):
                    break
            if len(samples) >= 48 and seen_words.issuperset(known_words):
                break
        if len(samples) >= 48 and seen_words.issuperset(known_words):
            break

    # fallback for diversity if needed
    rng = random.Random(1337)
    while len(samples) < 48:
        b = rng.choice([Fraction(-6, 1), Fraction(-4, 1), Fraction(-2, 1), Fraction(1, 1), Fraction(2, 1), Fraction(5, 2)])
        c = rng.choice([Fraction(-6, 1), Fraction(-4, 1), Fraction(-2, 1), Fraction(1, 1), Fraction(2, 1), Fraction(5, 2)])
        d = rng.choice([Fraction(-6, 1), Fraction(-4, 1), Fraction(-2, 1), Fraction(1, 1), Fraction(2, 1), Fraction(5, 2)])
        e = rng.choice([Fraction(-6, 1), Fraction(-4, 1), Fraction(-2, 1), Fraction(1, 1), Fraction(2, 1), Fraction(5, 2)])
        try:
            p = SixPoint(b, c, d, e)
        except Exception:
            continue
        if not p.is_generic():
            continue
        res, ferr = safe_on_shell(oracle, 6, [p.b, p.c, p.d, p.e])
        if res is None:
            continue
        omega, ar, ai = res
        rec = point_record(p, omega, ar, ai)
        samples.append(rec)

    denom_checks = []
    for rec in samples:
        p = SixPoint(*[str_to_frac(rec[k]) for k in ("b", "c", "d", "e")])
        _, scale = p.primitive_scale()
        F = str_to_frac(rec["C_times_amp_im"])
        A = str_to_frac(rec["amp_im"])
        R, pole_sub, _ = wall_pole_subtracted(p, A)
        den0 = F.denominator
        den11 = (F * (scale ** 11)).denominator
        delta_A = A * p.Delta
        den_delta17 = (delta_A * (scale ** 17)).denominator
        den_R8 = (R * (scale ** 8)).denominator
        denom_checks.append({
            "bcd e": [rec["b"], rec["c"], rec["d"], rec["e"]],
            "primitive_scale": scale,
            "den_Camp": den0,
            "den_Camp_at_primitive_integer_point": den11,
            "den_Delta_amp_at_primitive_integer_point": den_delta17,
            "pole_subtracted_im": frac_to_str(R),
            "pole_contrib_total": frac_to_str(pole_sub),
            "den_pole_subtracted_im_at_primitive_scale8": den_R8,
            "pole_subtracted_im_scaled8_integral": den_R8 == 1,
        })

    rel_checks = 0
    rel_hits = 0
    rel_fails = []
    for rec in samples:
        p = SixPoint(*[str_to_frac(rec[k]) for k in ("b", "c", "d", "e")])
        w = p.omega
        for m in MINUS_IDX:
            for pair in combinations(PLUS_IDX, 2):
                pidx, qidx = pair
                ridx = [x for x in PLUS_IDX if x not in pair][0]
                qT_key = f"q_{m+1}_{pidx+1}{qidx+1}"
                qT = p.triple_q[qT_key]
                if qT <= 0:
                    continue
                rel_checks += 1
                dT = Fraction(2, 1) * (w[m] + w[pidx]) * (w[m] + w[qidx])
                C_expected = (w[m] + w[PLUS_IDX[0]]) * (w[m] + w[PLUS_IDX[1]]) * (w[m] + w[PLUS_IDX[2]])
                C_ok = C_expected == p.C
                inv_ok = False
                omitted_factor = w[m] + w[ridx]
                if dT != 0 and omitted_factor != 0:
                    inv_ok = (Fraction(1, 1) / dT) == (omitted_factor / (2 * p.C))
                hit = C_ok and inv_ok
                if hit:
                    rel_hits += 1
                else:
                    rel_fails.append({
                        "omega": [frac_to_str(x) for x in p.omega],
                        "m": m + 1,
                        "p": pidx + 1,
                        "q": qidx + 1,
                        "r": ridx + 1,
                        "qT": frac_to_str(qT),
                        "dT": frac_to_str(dT),
                        "C": frac_to_str(p.C),
                    })

    return {
        "samples": samples,
        "counts": {
            "attempts": attempts,
            "selected": len(samples),
            "unique_words": len(seen_words),
            "delta_eq_C3": sum(1 for r in samples if r["Delta_eq_C3"]),
            "relation_checks": rel_checks,
            "relation_hits": rel_hits,
            "relation_failures": len(rel_fails),
        },
        "denominator_checks": denom_checks,
        "relation_failures": rel_fails,
        "counterexample_words": seen_exact,
    }


def section2_and_paths(oracle: BGOracle):
    t = sp.Symbol("t")
    def gather_candidates():
        candidates = []
        for b0 in [1, 2, 3, 4, 5, 6, 7, 8]:
            for c0 in [1, 2, 3, 4]:
                for d0 in [2, 3, 4, 5, 6]:
                    for e0 in [1, 2, 3, 4]:
                        candidates.append((Fraction(b0), Fraction(c0), Fraction(d0), Fraction(e0)))
                        candidates.append((Fraction(b0, 1), Fraction(-c0, 1), Fraction(d0, 1), Fraction(e0, 1)))
        # extra deterministic seed to include fractional offsets and larger values
        for b0 in [2, 3, 4, 5, 6, 7]:
            for c0 in [Fraction(1, 2), Fraction(3, 2), Fraction(5, 2)]:
                for d0 in [3, 4, 5]:
                    for e0 in [1, 2, 3]:
                        candidates.append((Fraction(b0, 1), c0, Fraction(d0, 1), Fraction(e0, 1)))
        rng = random.Random(2027)
        while len(candidates) < 320:
            base = [Fraction(rng.randint(-6, 12), 1), Fraction(rng.randint(-2, 6), 1)]
            candidates.append((base[0], base[1], Fraction(rng.randint(1, 12), 1), Fraction(rng.randint(1, 6), 1)))
            candidates.append((base[0], -base[1], Fraction(rng.randint(1, 12), 1), Fraction(rng.randint(1, 6), 1)))
            candidates.append((base[0], base[1], Fraction(rng.randint(-4, 12), 1), -Fraction(rng.randint(1, 6), 1)))
        return candidates

    def collect_paths(test_t):
        chosen = []
        for path in candidates:
            b0, c0, d0, e0 = path
            base_sig = None
            ok = True
            for tv in test_t:
                try:
                    p = SixPoint(b0 + tv, c0, d0 - tv, e0)
                except Exception:
                    ok = False
                    break
                if not p.is_generic():
                    ok = False
                    break
                if any(v == 0 for v in p.pair_q.values()) or any(v == 0 for v in p.triple_q.values()):
                    ok = False
                    break
                res, ferr = safe_on_shell(oracle, 6, [p.b, p.c, p.d, p.e])
                if res is None:
                    ok = False
                    break
                pair_sign, triple_sign = p.sign_maps()
                sig = (tuple(pair_sign.items()), tuple(triple_sign.items()))
                if base_sig is None:
                    base_sig = sig
                elif sig != base_sig:
                    ok = False
                    break
            if ok:
                chosen.append(path)
            if len(chosen) >= 3:
                break
        return chosen

    candidates = gather_candidates()

    # The fit and holdout grids must lie in the same sign cell that was tested.
    test_t = [Fraction(v, 20) for v in range(-7, 8)]
    chosen = collect_paths(test_t)

    # Fallback to an even smaller neighborhood for candidates close to a wall.
    if len(chosen) < 3:
        test_t = [Fraction(v, 40) for v in range(-7, 8)]
        chosen = collect_paths(test_t)

    path_outputs = []

    selected = len(chosen)
    path_status = "ok" if selected >= 3 else "insufficient_single_cell_paths"
    if selected < 3:
        chosen = chosen[:]

    for pid, path in enumerate(chosen[:3]):
        b0, c0, d0, e0 = path
        fit_t = test_t[:12]
        hold_t = test_t[12:15]
        fit_samples = []
        path_ok = True
        for tv in fit_t[:12]:
            p = SixPoint(b0 + tv, c0, d0 - tv, e0)
            res, ferr = safe_on_shell(oracle, 6, [p.b, p.c, p.d, p.e])
            if res is None:
                path_ok = False
                break
            omega, ar, ai = res
            fit_samples.append((tv, ai * p.C, ai, p))

        hold_samples = []
        if not path_ok:
            path_outputs.append({
                "path_id": pid,
                "path": {"b0": frac_to_str(b0), "c0": frac_to_str(c0), "d0": frac_to_str(d0), "e0": frac_to_str(e0)},
                "status": "path_rejected_bg_fail_fit",
            })
            continue
        for tv in hold_t:
            p = SixPoint(b0 + tv, c0, d0 - tv, e0)
            res, ferr = safe_on_shell(oracle, 6, [p.b, p.c, p.d, p.e])
            if res is None:
                path_ok = False
                break
            omega, ar, ai = res
            hold_samples.append((tv, ai * p.C, ai))
        if not path_ok:
            path_outputs.append({
                "path_id": pid,
                "path": {"b0": frac_to_str(b0), "c0": frac_to_str(c0), "d0": frac_to_str(d0), "e0": frac_to_str(e0)},
                "status": "path_rejected_bg_fail_hold",
            })
            continue

        bfit = rational_poly_fit([(t0, y) for t0, y, _, _ in fit_samples], t, 11)
        afit = rational_poly_fit([(t0, a) for t0, _, a, _ in fit_samples], t, 8)

        bres = poly_residuals(bfit["poly"], t, [(tv, bv) for tv, bv, _ in hold_samples]) if bfit["status"] == "ok" else []
        ares = poly_residuals(afit["poly"], t, [(tv, av) for tv, _, av in hold_samples]) if afit["status"] == "ok" else []

        C_poly = symbolic_C_poly(b0, d0, c0, e0).as_expr()
        C_poly_s = sp.Poly(C_poly, t)
        B_poly = bfit["poly"].as_expr()
        g = sp.gcd(sp.Poly(B_poly, t), C_poly_s)
        try:
            g_expr = g.as_expr()
            reduced_denom = sp.simplify(C_poly / g_expr)
        except Exception:
            g_expr = "1"
            reduced_denom = str(C_poly)

        path_outputs.append({
            "path_id": pid,
            "path": {"b0": frac_to_str(b0), "c0": frac_to_str(c0), "d0": frac_to_str(d0), "e0": frac_to_str(e0)},
            "B_poly_fit": {
                "status": bfit["status"],
                "deg": bfit.get("deg"),
                "expr": bfit.get("expr"),
                "residuals": bres,
            },
            "amp_poly_fit": {
                "status": afit["status"],
                "deg": afit.get("deg"),
                "expr": afit.get("expr"),
                "residuals": ares,
            },
            "C_poly": str(C_poly),
            "C_gcd_with_B": str(g_expr),
            "reduced_denom": str(reduced_denom),
        })

    return {
        "status": path_status,
        "candidates_examined": len(candidates),
        "paths_selected": len(chosen[:3]),
        "paths": path_outputs,
    }


def section3_pair_walls(oracle: BGOracle):
    t = sp.Symbol("t")
    base_choices = [
        (Fraction(10, 1), Fraction(2, 1), Fraction(3, 1)),
        (Fraction(12, 1), Fraction(1, 1), Fraction(4, 1)),
        (Fraction(14, 1), Fraction(3, 1), Fraction(2, 1)),
        (Fraction(16, 1), Fraction(2, 1), Fraction(5, 1)),
    ]

    def wall_attempts():
        for item in base_choices:
            yield item
        for B in range(8, 28):
            for c in [Fraction(1, 1), Fraction(2, 1), Fraction(3, 1), Fraction(4, 1)]:
                for e in [Fraction(1, 1), Fraction(2, 1), Fraction(3, 1), Fraction(4, 1)]:
                    yield (Fraction(B, 1), c, e)

    def sample_wall_side(ts, B, c, e):
        points = []
        base_sig = None
        for tv in ts:
            try:
                p = SixPoint(tv, c, B - tv, e)
            except Exception:
                return None, "nonsolution"
            if not p.is_generic():
                return None, "nonsolution"
            ps, tsig = p.sign_maps()
            sig = (tuple(ps.items()), tuple(tsig.items()))
            if base_sig is None:
                base_sig = sig
            elif sig != base_sig:
                return None, "cell_flip"
            res, ferr = safe_on_shell(oracle, 6, [p.b, p.c, p.d, p.e])
            if res is None:
                return None, "oracle_fail"
            _, _, ai = res
            R, _, _ = wall_pole_subtracted(p, ai)
            points.append((tv, ai * p.C, ai, p, R))
        return points, None

    def poly_multiplicity(expr, qexpr):
        if expr == 0:
            return 0
        if qexpr == 0:
            return 0
        p = sp.Poly(sp.expand(expr), t, domain="QQ")
        q = sp.Poly(sp.expand(qexpr), t, domain="QQ")
        if p.is_zero:
            return 0
        cnt = 0
        while True:
            qout, qrem = sp.div(p, q)
            if qrem.is_zero:
                cnt += 1
                p = qout
                if p.degree() < q.degree():
                    break
            else:
                break
        return cnt

    def q24_multiplicity_numden(num_expr, den_expr, qexpr):
        return poly_multiplicity(num_expr, qexpr) - poly_multiplicity(den_expr, qexpr)

    def factor_pairs(expr):
        try:
            return [[str(base), int(exp)] for base, exp in sp.factor_list(expr)[1]]
        except Exception:
            return []

    outputs = []
    seen = set()

    for B, c, e in wall_attempts():
        key = (str(B), str(c), str(e))
        if key in seen:
            continue
        seen.add(key)
        t0 = B / 2
        left_t = [t0 - Fraction(k, 120) for k in range(1, 13)]
        right_t = [t0 + Fraction(k, 120) for k in range(1, 13)]
        lpt, lerr = sample_wall_side(left_t, B, c, e)
        rpt, rerr = sample_wall_side(right_t, B, c, e)
        if lpt is None or rpt is None:
            outputs.append({
                "wall": {"B": frac_to_str(B), "c": frac_to_str(c), "e": frac_to_str(e)},
                "status": "rejected_cell_criterion",
                "error": lerr or rerr,
            })
            if len([x for x in outputs if x.get("status") == "ok"]) >= 3:
                break
            continue

        left_pair, left_triple = dict(lpt[0][3].sign_maps()[0]), dict(lpt[0][3].sign_maps()[1])
        right_pair, right_triple = dict(rpt[0][3].sign_maps()[0]), dict(rpt[0][3].sign_maps()[1])

        if "q_2_4" in left_pair and "q_2_4" in right_pair and left_pair["q_2_4"] == right_pair["q_2_4"]:
            outputs.append({
                "wall": {"B": frac_to_str(B), "c": frac_to_str(c), "e": frac_to_str(e)},
                "status": "wall_isolation_failed",
                "reason": "q24 sign did not flip",
            })
            continue

        pair_ok = True
        for k, lv in left_pair.items():
            if k != "q_2_4" and right_pair.get(k, lv) != lv:
                pair_ok = False
                break
        tri_ok = True
        for k, lv in left_triple.items():
            if right_triple.get(k, lv) != lv:
                tri_ok = False
                break
        if not pair_ok or not tri_ok:
            outputs.append({
                "wall": {"B": frac_to_str(B), "c": frac_to_str(c), "e": frac_to_str(e)},
                "status": "wall_isolation_failed",
                "reason": "sign drift",
            })
            continue

        lf = rational_poly_fit([(x[0], x[1]) for x in lpt], t, 11)
        rf = rational_poly_fit([(x[0], x[1]) for x in rpt], t, 11)
        if lf["status"] != "ok" or rf["status"] != "ok":
            outputs.append({
                "wall": {"B": frac_to_str(B), "c": frac_to_str(c), "e": frac_to_str(e)},
                "status": "fit_failed",
                "left": lf.get("status"),
                "right": rf.get("status"),
            })
            continue

        Bleft = lf["poly"].as_expr()
        Bright = rf["poly"].as_expr()
        D_B = sp.expand(Bleft - Bright)
        C_poly = symbolic_C_poly(Fraction(0), B, c, e).as_expr()
        quotient, rem = sp.div(D_B, C_poly)
        divisible = sp.expand(rem) == 0
        J = sp.cancel(D_B / C_poly)
        num, den = sp.together(J).as_numer_denom()
        fac = sp.factor_list(num)
        q24 = sp.expand((B - t) ** 2 - t ** 2)
        q24_mult = q24_multiplicity_numden(num, den, q24)

        try:
            H0 = str(sp.limit(J / (q24 ** q24_mult), t, t0))
        except Exception:
            H0 = None

        hold_t = [
            t0 - Fraction(1, 240),
            t0 - Fraction(1, 210),
            t0 - Fraction(1, 180),
            t0 + Fraction(1, 180),
            t0 + Fraction(1, 210),
            t0 + Fraction(1, 240),
        ]
        hold_unsub = []
        ok_hold_unsub = True
        for tv in hold_t:
            p = SixPoint(tv, c, B - tv, e)
            res, ferr = safe_on_shell(oracle, 6, [p.b, p.c, p.d, p.e])
            if res is None:
                ok_hold_unsub = False
                break
            _, _, ai = res
            obs = ai * p.C
            pl = lf["poly"].eval(sp.Rational(tv.numerator, tv.denominator))
            pr = rf["poly"].eval(sp.Rational(tv.numerator, tv.denominator))
            plv = Fraction(int(pl.as_numer_denom()[0]), int(pl.as_numer_denom()[1]))
            prv = Fraction(int(pr.as_numer_denom()[0]), int(pr.as_numer_denom()[1]))
            hold_unsub.append({
                "t": frac_to_str(tv),
                "obs_B": frac_to_str(obs),
                "pred_left_B": frac_to_str(plv),
                "pred_right_B": frac_to_str(prv),
                "res_left_B": frac_to_str(plv - obs),
                "res_right_B": frac_to_str(prv - obs),
            })

        rlf = rational_poly_fit([(x[0], x[4]) for x in lpt[:9]], t, 8)
        rrf = rational_poly_fit([(x[0], x[4]) for x in rpt[:9]], t, 8)
        if rlf["status"] != "ok" or rrf["status"] != "ok":
            outputs.append({
                "wall": {"B": frac_to_str(B), "c": frac_to_str(c), "e": frac_to_str(e)},
                "t0": frac_to_str(t0),
                "status": "subtracted_fit_failed",
                "left": rlf.get("status"),
                "right": rrf.get("status"),
                "unsubtracted": {
                    "left_fit": {"deg": lf["deg"], "expr": lf["expr"]},
                    "right_fit": {"deg": rf["deg"], "expr": rf["expr"]},
                    "C_poly": str(C_poly),
                    "divisible_by_C": divisible,
                    "J": str(J),
                    "J_factorization": str(sp.factor(num)),
                    "J_factor_list": [[str(f), int(e)] for f, e in fac[1]],
                    "q24_multiplicity": q24_mult,
                    "holdout": hold_unsub,
                    "quotient": str(sp.expand(quotient)),
                    "remainder": str(sp.expand(rem)),
                    "reason": "r_subtracted_fit_failed",
                },
            })
            if ok_hold_unsub is False:
                outputs[-1]["status"] = "holdout_eval_failed"
            continue

        if not ok_hold_unsub:
            outputs.append({
                "wall": {"B": frac_to_str(B), "c": frac_to_str(c), "e": frac_to_str(e)},
                "t0": frac_to_str(t0),
                "status": "holdout_eval_failed",
                "reason": "unsubtracted_holdout",
                "unsubtracted": {
                    "left_fit": {"deg": lf["deg"], "expr": lf["expr"]},
                    "right_fit": {"deg": rf["deg"], "expr": rf["expr"]},
                    "C_poly": str(C_poly),
                }
            })
            continue

        JR = rlf["poly"].as_expr() - rrf["poly"].as_expr()
        JR_num, JR_den = sp.together(JR).as_numer_denom()
        fac_num = sp.factor_list(JR_num)[1] if JR_num != 0 else []
        fac_den = sp.factor_list(JR_den)[1] if JR_den != 0 else []
        q24_R_mult = q24_multiplicity_numden(JR_num, JR_den, q24)

        hold_R = []
        for tv in hold_t:
            p = SixPoint(tv, c, B - tv, e)
            res, ferr = safe_on_shell(oracle, 6, [p.b, p.c, p.d, p.e])
            if res is None:
                hold_R.append({
                    "t": frac_to_str(tv),
                    "obs_R": None,
                    "pred_left_R": None,
                    "pred_right_R": None,
                    "res_left_R": None,
                    "res_right_R": None,
                })
                continue
            _, _, ai = res
            obs_r = wall_pole_subtracted(p, ai)[0]
            pl = rlf["poly"].eval(sp.Rational(tv.numerator, tv.denominator))
            pr = rrf["poly"].eval(sp.Rational(tv.numerator, tv.denominator))
            plv = Fraction(int(pl.as_numer_denom()[0]), int(pl.as_numer_denom()[1]))
            prv = Fraction(int(pr.as_numer_denom()[0]), int(pr.as_numer_denom()[1]))
            hold_R.append({
                "t": frac_to_str(tv),
                "obs_R": frac_to_str(obs_r),
                "pred_left_R": frac_to_str(plv),
                "pred_right_R": frac_to_str(prv),
                "res_left_R": frac_to_str(plv - obs_r),
                "res_right_R": frac_to_str(prv - obs_r),
            })

        try:
            HR = str(sp.limit(sp.together(JR / (q24 ** q24_R_mult)), t, t0))
        except Exception:
            HR = None
        try:
            JRr = sp.cancel(JR / (q24 ** q24_R_mult))
            numr, denr = sp.together(JRr).as_numer_denom()
            if sp.Poly(sp.expand(denr), t, domain="QQ").degree() == 0:
                quotient_degree = sp.Poly(sp.expand(numr), t, domain="QQ").degree()
            else:
                quotient_degree = None
            quotient_expr = str(sp.expand(JRr))
            remainder_expr = "0" if denr == 1 else str(sp.together(JRr))
        except Exception:
            quotient_degree = None
            quotient_expr = str(JR)
            remainder_expr = "0"

        outputs.append({
            "wall": {"B": frac_to_str(B), "c": frac_to_str(c), "e": frac_to_str(e)},
            "t0": frac_to_str(t0),
            "status": "ok",
            "left_fit": {"deg": lf["deg"], "expr": lf["expr"]},
            "right_fit": {"deg": rf["deg"], "expr": rf["expr"]},
            "C_poly": str(C_poly),
            "divisible_by_C": divisible,
            "J": str(J),
            "J_factorization": str(sp.factor(num)),
            "J_factor_list": [[str(f), int(e)] for f, e in fac[1]],
            "q24_multiplicity": q24_mult,
            "H0": H0,
            "quotient": str(sp.expand(quotient)),
            "remainder": str(sp.expand(rem)),
            "holdout": hold_unsub,
            "subtracted": {
                "left_fit": {"deg": rlf["deg"], "expr": rlf["expr"]},
                "right_fit": {"deg": rrf["deg"], "expr": rrf["expr"]},
                "J_R": str(JR),
                "J_R_factorization_num": factor_pairs(JR_num),
                "J_R_factorization_den": factor_pairs(JR_den),
                "q24_multiplicity": q24_R_mult,
                "q24_expr": str(q24),
                "H0_R": HR,
                "quotient_degree": quotient_degree,
                "quotient": quotient_expr,
                "remainder": remainder_expr,
                "holdout": hold_R,
                "holdout_pass_count": sum(
                    1
                    for idx, x in enumerate(hold_R)
                    if x["res_left_R"] is not None
                    and ((idx < 3 and x["res_left_R"] == "0")
                         or (idx >= 3 and x["res_right_R"] == "0"))
                ),
                "left_residual_points": poly_residuals(rlf["poly"], t, [(x[0], x[4]) for x in lpt[9:12]]),
                "right_residual_points": poly_residuals(rrf["poly"], t, [(x[0], x[4]) for x in rpt[9:12]]),
            },
        })

        if len([x for x in outputs if x.get("status") == "ok"]) >= 3:
            break

    return {
        "wall_results": outputs,
        "wall_attempted": len(outputs),
        "wall_success": len([x for x in outputs if x.get("status") == "ok"]),
        "wall_replace_if_needed": len(outputs) > len(base_choices),
    }



def section4_coverage(oracle: BGOracle):
    word_counts = {}
    words_seen = set()
    sample_count = 0
    counterexample = None

    for b, c, d, e in product(range(-8, 9), repeat=4):
        if 0 in (b, c, d, e):
            continue
        try:
            p = SixPoint(Fraction(b), Fraction(c), Fraction(d), Fraction(e))
        except Exception:
            continue
        if not p.is_generic():
            continue
        sample_count += 1
        word, strict, _ = p.sorted_word()
        words_seen.add(word)
        word_counts[word] = word_counts.get(word, 0) + 1
        if counterexample is None and word not in KNOWN_WORDS:
            counterexample = {"word": word, "b": frac_to_str(p.b), "c": frac_to_str(p.c), "d": frac_to_str(p.d), "e": frac_to_str(p.e)}

    rng = random.Random(4242)
    random_words = []
    for _ in range(12):
        b, c, d, e = [Fraction(rng.choice(list(range(-12, 13))), 1) for __ in range(4)]
        if 0 in (b, c, d, e):
            continue
        p = SixPoint(b, c, d, e)
        if not p.is_generic():
            continue
        random_words.append({"b": frac_to_str(b), "c": frac_to_str(c), "d": frac_to_str(d), "e": frac_to_str(e), "word": p.sorted_word()[0]})

    return {
        "sample_count": sample_count,
        "words_observed": sorted(words_seen),
        "word_counts": word_counts,
        "counterexample": counterexample,
        "contains_++---+": "++---+" in words_seen,
        "contains_--+++-": "--+++-" in words_seen,
        "random_probe": random_words,
    }


def five_point_formula(omega: Sequence[Fraction]) -> Fraction:
    beta = min(abs(omega[0]), abs(omega[1]))
    acc = Fraction(0, 1)
    for mask in range(1 << 3):
        s = Fraction(0, 1)
        for j in range(3):
            if mask & (1 << j):
                s += omega[2 + j] ** 2
        term = beta * beta - s
        if term > 0:
            parity = bin(mask).count("1")
            acc += (Fraction(-1, 1) if (parity % 2) else Fraction(1, 1)) * (term ** 2)
    return Fraction(16, 1) * omega[0] * omega[1] * acc


def section5_5pt(oracle: BGOracle):
    vals = [Fraction(v) for v in (-3, -2, -1, 1, 2, 3)]
    samples = []
    for w2 in vals:
        for w3 in vals:
            for w4 in vals:
                if len(samples) >= 3:
                    break
                res, ferr = safe_on_shell(oracle, 5, [w2, w3, w4], sigma=(-1, -1, 1, 1, 1))
                if res is None:
                    continue
                omega, ar, ai = res
                formula = five_point_formula(omega)
                samples.append({
                    "free": [frac_to_str(w2), frac_to_str(w3), frac_to_str(w4)],
                    "omega": [frac_to_str(x) for x in omega],
                    "amp_im": frac_to_str(ai),
                    "amp_re": frac_to_str(ar),
                    "formula": frac_to_str(formula),
                    "residual": frac_to_str(ai - formula),
                    "pure_im": ar == 0,
                })
                if len(samples) >= 3:
                    break
        if len(samples) >= 3:
            break

    return {
        "samples": samples,
        "pass_count": sum(1 for s in samples if s["residual"] == "0"),
    }


def section3_invariance_checks(oracle: BGOracle, base: List[Dict[str, object]]):
    # 6+ permutations within minus and plus labels
    checks = []
    minus_perms = list(permutations(MINUS_IDX))
    plus_perms = list(permutations(PLUS_IDX))
    need = 6

    for rec in base[:3]:
        if len(checks) >= need:
            break
        omega = tuple(str_to_frac(x) for x in rec["omega"])
        base_ai = str_to_frac(rec["amp_im"])
        for pm, pp in product(minus_perms, plus_perms):
            if len(checks) >= need:
                break
            perm_omega = (
                omega[pm[0]],
                omega[pm[1]],
                omega[pm[2]],
                omega[pp[0]],
                omega[pp[1]],
                omega[pp[2]],
            )
            k = [Fraction(SIGMA[i], 1) * perm_omega[i] * perm_omega[i] for i in range(6)]
            res, ferr = safe_raw(oracle, k, perm_omega)
            if res is None:
                continue
            _, ar, ai = res
            checks.append({
                "base_word": rec["sorted_word"],
                "perm_minus": list(pm),
                "perm_plus": list(pp),
                "base_amp_im": frac_to_str(base_ai),
                "perm_amp_im": frac_to_str(ai),
                "residual": frac_to_str(ai - base_ai),
                "pure_im": ar == 0,
            })

    return {
        "checks": checks,
        "passed": sum(1 for x in checks if x["residual"] == "0"),
        "attempted": len(checks),
    }


def jsonable(d):
    return json.loads(json.dumps(d, default=str))


def main():
    root = Path(__file__).resolve().parents[3]
    log = {}
    binary = build_bg(root, log)
    oracle = BGOracle(binary)

    sec1 = section1(oracle, KNOWN_WORDS)
    sec2 = section2_and_paths(oracle)
    sec3 = section3_pair_walls(oracle)
    sec3_inv = section3_invariance_checks(oracle, sec1["samples"][:4])
    sec3["permutation_checks"] = sec3_inv
    sec4 = section4_coverage(oracle)
    sec5 = section5_5pt(oracle)

    out_json = root / "bots" / "student-2" / "data" / "round2_exact.json"
    out_md = root / "bots" / "student-2" / "data" / "round2_exact_report.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "meta": log,
        "section1_oracle_checks": sec1,
        "section2_reductions": sec2,
        "section3_wall_jumps": sec3,
        "section4_sheet_coverage": sec4,
        "section5_five_point": sec5,
    }
    out_json.write_text(json.dumps(jsonable(payload), indent=2, sort_keys=True))

    sec1_denom_ok = len([x for x in sec1["denominator_checks"] if x.get("pole_subtracted_im_scaled8_integral")])
    md = [
        "# Round-2 exact batch",
        "",
        f"- bg.cpp copied to `bots/student-2/bg.cpp`",
        f"- bg binary: `bots/student-2/bg`",
        f"- compiler: {log.get('build', {}).get('compiler_version', 'unknown')}",
        f"- build command: `{log.get('build', {}).get('command', '')}`",
        "",
        "## Pass counts",
        f"- section1 samples: {sec1['counts']['selected']} (delta=C^3: {sec1['counts']['delta_eq_C3']})",
        f"- section1 unique words: {sec1['counts']['unique_words']}",
        f"- section1 relation checks: {sec1['counts']['relation_hits']} / {sec1['counts']['relation_checks']}",
        f"- section1 pole-subtracted primitive degree-8 integrality checks: {sec1_denom_ok} / {len(sec1['denominator_checks'])}",
        f"- section2 path outputs: {len(sec2['paths'])}",
        f"- section3 wall outputs: {sec3['wall_attempted']} attempted, {sec3['wall_success']} successful",
        f"- section3 q24 multiplicities (unsubtracted / subtracted): "
        f"{', '.join([str(x.get('q24_multiplicity')) + ' / ' + str(x.get('subtracted', {}).get('q24_multiplicity', 'na')) for x in sec3['wall_results'] if x.get('status') == 'ok'])}",
        f"- section4 words observed: {len(sec4['words_observed'])} over {sec4['sample_count']} samples",
        f"- section4 counterexample: {json.dumps(sec4['counterexample'])}",
        f"- section5 five-point zero residuals: {sec5['pass_count']} / {len(sec5['samples'])}",
        f"- section3 permutations: {sec3_inv['passed']} / {sec3_inv['attempted']}",
        f"- wall replacements needed: {sec3['wall_replace_if_needed']}",
    ]
    out_md.write_text("\n".join(md))

    print(out_json)
    print(out_md)


if __name__ == "__main__":
    main()
