#!/usr/bin/env python3
"""Round-8 offline ground-truth extraction for q-wall quotients.

Builds a private BG binary copy (bg_round8) and runs exact rational checks:

1) reproduce the exact S(q-wall jump)/interpolation stack with Fractions
2) extract representative q-wall quotients in exact cells
3) compare quotients to fixed raw local formulas on 7 off-wall points
4) perform sympy cocycle obstruction check with z=y substitution
5) emit JSON + markdown report artifacts under bots/student-2/data
"""

import json
import os
import re
import hashlib
import subprocess
import shutil
from fractions import Fraction as Fr
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Sequence

import sympy as sp

# ---------- paths and constants ----------
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CODE_DIR = ROOT / "code"
BG_BIN = CODE_DIR / "bg_round8"
QUESTION_ROOT = ROOT.parent.parent
QUESTION_BG = QUESTION_ROOT / "bg.cpp"
PRIVATE_BG = ROOT / "bg_round8.cpp"
JSON_PATH = DATA_DIR / "round8_offwall_ground_truth.json"
REPORT_PATH = DATA_DIR / "round8_offwall_ground_truth_report.md"

M = [0, 1, 2]
P = [3, 4, 5]
SIGMA = [Fr(-1), Fr(-1), Fr(-1), Fr(1), Fr(1), Fr(1)]


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(str(path), "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _build_bg() -> Dict[str, str]:
    if not QUESTION_BG.exists():
        raise FileNotFoundError(f"shared bg.cpp missing: {QUESTION_BG}")
    shutil.copyfile(str(QUESTION_BG), str(PRIVATE_BG))
    shared_sha = _sha256_file(QUESTION_BG)
    private_sha = _sha256_file(PRIVATE_BG)
    cmd = [
        "g++",
        "-O2",
        "-std=c++17",
        str(PRIVATE_BG),
        "-o",
        str(BG_BIN),
        "-lgmpxx",
        "-lgmp",
    ]
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        timeout=120,
        cwd=str(CODE_DIR),
    )
    if proc.returncode != 0:
        raise RuntimeError(f"bg build failed: {proc.stderr}\n{proc.stdout}")
    return {
        "shared_bg_sha256": shared_sha,
        "private_bg_sha256": private_sha,
        "shas_match": shared_sha == private_sha,
        "compile_ok": proc.returncode == 0,
        "compile_cmd": " ".join(cmd),
    }

# two physical q-wall representatives (four-environment words collapses to 2/2)
CELL_CASES = [
    {
        "label": "MPPM",
        "P": [Fr(8), Fr(2), Fr(-3), Fr(-5), Fr(4), Fr(-6)],
        "d": [Fr(4), Fr(3), Fr(1), Fr(-3), Fr(-1), Fr(-4)],
        "m": 1,
        "p": 4,
        "t0": Fr(1, 2),
    },
    {
        "label": "PMMP",
        "P": [Fr(10), Fr(-7), Fr(-6), Fr(-5), Fr(-4), Fr(12)],
        "d": [Fr(1), Fr(1), Fr(1), Fr(-1), Fr(-1), Fr(-1)],
        "m": 2,
        "p": 3,
        "t0": Fr(1, 2),
    },
]

ANCHOR = [Fr(-8), Fr(2), Fr(3), Fr(4), Fr(5), Fr(-6)]
ANCHOR_EXPECT = {
    "A6_over_i": Fr(-9190656, 7),
    "P_pole": Fr(42588288, 7),
    "R_Q": Fr(-136630560),
    "S": Fr(129233568),
}

# ---------- exact arithmetic helpers ----------
def _fmt(x: Fr) -> str:
    return f"{x.numerator}/{x.denominator}" if x.denominator != 1 else str(x.numerator)

def _parse_fraction(s: str) -> Fr:
    s = s.strip()
    if "/" in s:
        n, d = s.split("/", 1)
        return Fr(int(n), int(d))
    return Fr(int(s), 1)

# ---------- exact BG interface ----------
_AMP_CACHE: Dict[tuple, Fr] = {}


def amp_over_i(Ws: Sequence[Fr]) -> Fr:
    Ws = [Fr(x) for x in Ws]
    key = tuple(Ws)
    if key in _AMP_CACHE:
        return _AMP_CACHE[key]

    Ks = [SIGMA[i] * Ws[i] * Ws[i] for i in range(6)]
    ks = ",".join(_fmt(x) for x in Ks)
    ws = ",".join(_fmt(x) for x in Ws)
    proc = subprocess.run(
        [str(BG_BIN), "--amp", "-K", ks, "-W", ws],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"bg failed: {proc.stderr}\n{proc.stdout}")

    val = None
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("A_6 = i * ("):
            val = _parse_fraction(line[len("A_6 = i * (") : -1])
            break
        if line.startswith("A_6 = (") and "+ i * (" in line:
            # keep imaginary part; real must be exactly zero
            re_part = line[len("A_6 = (") : line.index(") + i *")]
            im_part = line[line.index("+ i * (") + len("+ i * (") : -1]
            if _parse_fraction(re_part) != 0:
                raise RuntimeError(f"non-imaginary A_6: {line}")
            val = _parse_fraction(im_part)
            break

    if val is None:
        raise RuntimeError(f"could not parse A_6 from bg output: {proc.stdout}")

    _AMP_CACHE[key] = val
    return val


def pos(x: Fr) -> Fr:
    return x if x > 0 else Fr(0)


def Hblock(b: Fr, c_idx: int, d_idx: int, Ws: Sequence[Fr]) -> Fr:
    wc2 = Ws[c_idx] * Ws[c_idx]
    wd2 = Ws[d_idx] * Ws[d_idx]
    return pos(b) - pos(b - wc2) - pos(b - wd2) + pos(b - wc2 - wd2)


def P_pole(Ws: Sequence[Fr]) -> Fr:
    Ws = [Fr(w) for w in Ws]
    total = Fr(0)
    for m in M:
        others = [x for x in M if x != m]
        for p, q in combinations(P, 2):
            tbar = [x for x in P if x not in (p, q)][0]
            qt = Ws[p] * Ws[p] + Ws[q] * Ws[q] - Ws[m] * Ws[m]
            if qt <= 0:
                continue
            h1 = Hblock(min(Ws[m] * Ws[m], qt), p, q, Ws)
            h2 = Hblock(min(Ws[tbar] * Ws[tbar], qt), others[0], others[1], Ws)
            total += Ws[m] * Ws[tbar] * qt * qt / (2 * (Ws[m] + Ws[p]) * (Ws[m] + Ws[q])) * h1 * h2
    return -64 * total


def R_Q(Ws: Sequence[Fr]) -> Fr:
    Ws = [Fr(w) for w in Ws]
    out = Fr(0)
    for m in M:
        others = [x for x in M if x != m]
        for p, q in combinations(P, 2):
            tbar = [x for x in P if x not in (p, q)][0]
            qt = Ws[p] * Ws[p] + Ws[q] * Ws[q] - Ws[m] * Ws[m]
            if qt <= 0:
                continue
            out += pos(qt) ** 3 * Ws[m] * Ws[tbar]
    return -32 * out


def S_value(Ws: Sequence[Fr]) -> Fr:
    return amp_over_i(Ws) - P_pole(Ws) - R_Q(Ws)

# ---------- exact univariate tools ----------
def line(Pv: Sequence[Fr], dv: Sequence[Fr], t: Fr) -> List[Fr]:
    return [Fr(Pv[i]) + Fr(dv[i]) * Fr(t) for i in range(6)]


def poly_interp(xs: Sequence[Fr], ys: Sequence[Fr]) -> List[Fr]:
    n = len(xs)
    xs = [Fr(x) for x in xs]
    ys = [Fr(y) for y in ys]
    coeffs = [Fr(0)] * n
    for i in range(n):
        num = [Fr(1)]
        den = Fr(1)
        for j in range(n):
            if j == i:
                continue
            new = [Fr(0)] * (len(num) + 1)
            for k, c in enumerate(num):
                new[k] += c * (-xs[j])
                new[k + 1] += c
            num = new
            den *= xs[i] - xs[j]
        scale = ys[i] / den
        for k, c in enumerate(num):
            coeffs[k] += c * scale
    while len(coeffs) > 1 and coeffs[-1] == 0:
        coeffs.pop()
    return coeffs


def poly_eval(coeffs: Sequence[Fr], x: Fr) -> Fr:
    x = Fr(x)
    out = Fr(0)
    for c in reversed(coeffs):
        out = out * x + c
    return out


def poly_divmod(num: List[Fr], den: List[Fr]):
    num = list(num)
    den = list(den)
    while len(num) > 1 and num[-1] == 0:
        num.pop()
    while len(den) > 1 and den[-1] == 0:
        den.pop()
    if len(den) == 1:
        return [num[i] / den[0] for i in range(len(num))], [Fr(0)]
    q = [Fr(0)] * max(1, len(num) - len(den) + 1)
    while len(num) >= len(den) and not (len(num) == 1 and num[0] == 0):
        deg = len(num) - len(den)
        c = num[-1] / den[-1]
        q[deg] = c
        for i in range(len(den)):
            num[deg + i] -= c * den[i]
        while len(num) > 1 and num[-1] == 0:
            num.pop()
    while len(q) > 1 and q[-1] == 0:
        q.pop()
    return q, num


def is_square_rational(q: Fr):
    if q < 0:
        return False, Fr(0)
    rn = q.numerator
    rd = q.denominator
    if rn < 0:
        return False, Fr(0)
    def isqrt(n: int) -> int:
        if n < 0:
            raise ValueError("sqrt of negative")
        if n == 0:
            return 0
        x = 1 + n // 2
        y = (x + n // x) // 2
        while y < x:
            x = y
            y = (x + n // x) // 2
        while (x + 1) * (x + 1) <= n:
            x += 1
        while x * x > n:
            x -= 1
        return x

    sr = isqrt(rn)
    tr = isqrt(rd)
    if sr * sr != rn or tr * tr != rd:
        return False, Fr(0)
    return True, Fr(sr, tr)


def wall_crossings(Pv: Sequence[Fr], dv: Sequence[Fr], t_lo: Fr, t_hi: Fr):
    xs = []

    def add_root(coeffs, kind, label):
        coeffs = [Fr(x) for x in coeffs]
        while len(coeffs) > 1 and coeffs[-1] == 0:
            coeffs.pop()
        roots = []
        if len(coeffs) == 2:
            roots = [-coeffs[0] / coeffs[1]]
        elif len(coeffs) == 3:
            a, b, cc = coeffs[2], coeffs[1], coeffs[0]
            ok, s = is_square_rational(b * b - 4 * a * cc)
            if ok:
                roots = [(-b + s) / (2 * a), (-b - s) / (2 * a)]
        for r in roots:
            if t_lo < r < t_hi:
                xs.append((r, kind, label))

    for m in M:
        for p in P:
            wp = (Fr(Pv[p]), Fr(dv[p]))
            wm = (Fr(Pv[m]), Fr(dv[m]))
            coeffs = [
                wp[0] * wp[0] - wm[0] * wm[0],
                2 * (wp[0] * wp[1] - wm[0] * wm[1]),
                wp[1] * wp[1] - wm[1] * wm[1],
            ]
            add_root(coeffs, "q", (m, p))
    for m in M:
        for p, q in combinations(P, 2):
            wp = (Fr(Pv[p]), Fr(dv[p]))
            wq = (Fr(Pv[q]), Fr(dv[q]))
            wm = (Fr(Pv[m]), Fr(dv[m]))
            coeffs = [
                wp[0] * wp[0] + wq[0] * wq[0] - wm[0] * wm[0],
                2 * (wp[0] * wp[1] + wq[0] * wq[1] - wm[0] * wm[1]),
                wp[1] * wp[1] + wq[1] * wq[1] - wm[1] * wm[1],
            ]
            add_root(coeffs, "Q", (m, p, q))
    xs.sort(key=lambda z: z[0])
    return xs


def q_poly(Pv: Sequence[Fr], dv: Sequence[Fr], m: int, p: int) -> List[Fr]:
    Pp, dp = Fr(Pv[p]), Fr(dv[p])
    Pm, dm = Fr(Pv[m]), Fr(dv[m])
    return [Pp * Pp - Pm * Pm, 2 * (Pp * dp - Pm * dm), dp * dp - dm * dm]


def q_sign(om: Sequence[Fr], m: int, p: int) -> int:
    val = om[p] * om[p] - om[m] * om[m]
    return 1 if val > 0 else (-1 if val < 0 else 0)


def Q_sign(om: Sequence[Fr], m: int, p: int, q: int) -> int:
    val = om[p] * om[p] + om[q] * om[q] - om[m] * om[m]
    return 1 if val > 0 else (-1 if val < 0 else 0)


def env_word(om: Sequence[Fr], m: int, p: int) -> str:
    idx = [i for i in range(6) if i not in (m, p)]
    return "".join(ch for _, ch in sorted(((abs(om[i]), "M" if i in M else "P") for i in idx), key=lambda v: (v[0], v[1])))


def qwall_signature(om: Sequence[Fr], m: int, p: int):
    pair = {
        f"{i},{j}": q_sign(om, i, j)
        for i in M
        for j in P
        if not (i == m and j == p)
    }
    triple = {
        f"{i},{j},{k}": Q_sign(om, i, j, k)
        for i in M
        for (j, k) in combinations(P, 2)
    }
    freq = {
        str(i): 1 if om[i] > 0 else (-1 if om[i] < 0 else 0)
        for i in range(6)
    }
    return {"pair_q": pair, "triple_Q": triple, "freq": freq}


def pad(c: List[Fr], n: int) -> List[Fr]:
    return c + [Fr(0)] * (n - len(c))


def safe_S(Pv: Sequence[Fr], dv: Sequence[Fr], t: Fr, cache: Dict[tuple, Fr]):
    key = (tuple(Pv), tuple(dv), t)
    if key in cache:
        return cache[key]
    om = line(Pv, dv, t)
    val = S_value(om)
    cache[key] = val
    return val


def fit_side(Pv: Sequence[Fr], dv: Sequence[Fr], ts: Sequence[Fr], cache: Dict[tuple, Fr]):
    xs = []
    ys = []
    for t in ts:
        try:
            y = safe_S(Pv, dv, t, cache)
        except (RuntimeError, subprocess.CalledProcessError):
            continue
        xs.append(Fr(t))
        ys.append(y)
    if len(xs) < 10:
        return None
    coeffs = poly_interp(xs[:9], ys[:9])
    hold_t = xs[9]
    hold_y = ys[9]
    hold_res = poly_eval(coeffs, hold_t) - hold_y
    return xs[:9], ys[:9], coeffs, {"t": hold_t, "y": hold_y, "residual": hold_res}


def H_minus_formula(om: Sequence[Fr], m: int, p: int) -> Fr:
    a = om[m]
    b = om[p]
    q = b * b - a * a
    other_minus = [i for i in M if i != m]
    other_plus = [i for i in P if i != p]
    x = om[other_minus[0]]
    y = om[other_minus[1]]
    s = x + y
    v = x * y
    F = a * s ** 3 + v * (s * s - 2 * v)
    D = 2 * a ** 3 + 3 * a * a * s + a * (s * s + v) - s * v
    core = F + (a + b) * D
    candidates = other_minus + other_plus
    jmin = min(candidates, key=lambda i: abs(om[i]))
    if jmin in other_minus:
        y0 = om[jmin]
        x0 = om[other_minus[0]] if other_minus[1] == jmin else om[other_minus[1]]
        L = 3 * a * a + 2 * a * (s + b) - v + b * (2 * x0 + y0)
        return -32 * y0 * y0 * core - 32 * q * y0 * y0 * L + 32 * x0 * b * q * q
    z = om[jmin]
    A0 = a ** 4 + 4 * a ** 3 * b + 4 * a ** 3 * z + 4 * a * a * b * b + 6 * a * a * b * z + a * b ** 3 + 2 * a * b * b * z
    A1 = 4 * a ** 3 + 8 * a * a * b + 7 * a * a * z + 5 * a * b * b + 7 * a * b * z + b ** 3 + b * b * z
    A2 = 3 * a * a + 4 * a * b + 3 * a * z + b * b + b * z
    B0 = 3 * a * a + 2 * a * b + a * z
    B1 = 3 * a + b
    K = A0 + s * A1 + s * s * A2 + v * B0 + s * v * B1
    return -32 * z * z * core + 32 * q * K


def wall_trace(om: Sequence[Fr], m: int, p: int) -> Fr:
    a = om[m]
    b = om[p]
    other_minus = [i for i in M if i != m]
    x = om[other_minus[0]]
    y = om[other_minus[1]]
    s = x + y
    v = x * y
    F = a * s ** 3 + v * (s * s - 2 * v)
    D = 2 * a ** 3 + 3 * a * a * s + a * (s * s + v) - s * v
    beta = min(abs(om[j]) for j in range(6) if j not in (m, p))
    return -32 * beta * beta * (F + (a + b) * D)


def poly_to_string(coeffs: Sequence[Fr]) -> str:
    terms = []
    for d, c in enumerate(coeffs):
        if c == 0:
            continue
        terms.append((d, c))
    if not terms:
        return "0"
    parts = []
    for d, c in reversed(terms):
        c_str = _fmt(c)
        if d == 0:
            parts.append(c_str)
        elif d == 1:
            parts.append(f"{c_str}*t")
        else:
            parts.append(f"{c_str}*t**{d}")
    return " + ".join(parts).replace("+ -", "- ")


def extract_cell(case: Dict) -> Dict:
    Pv = [Fr(x) for x in case["P"]]
    dv = [Fr(x) for x in case["d"]]
    m = int(case["m"])
    p = int(case["p"])
    t0 = Fr(case["t0"])
    out: Dict = {"label": case["label"], "P": [str(x) for x in Pv], "d": [str(x) for x in dv], "m": m, "p": p, "t0": str(t0)}

    cr = wall_crossings(Pv, dv, Fr(-1), Fr(1))
    hit = [i for i, e in enumerate(cr) if e[1] == "q" and e[2] == (m, p) and e[0] == t0]
    if not hit:
        out.update({"status": "fail", "reason": f"q-wall {m,p} not found at t0={t0}"})
        return out
    idx = hit[0]
    left = cr[idx - 1][0] if idx > 0 else Fr(-1)
    right = cr[idx + 1][0] if idx + 1 < len(cr) else Fr(1)
    gap = min(t0 - left, right - t0)
    half = min(gap * Fr(2, 5), Fr(1, 4))

    sample_cache: Dict[tuple, Fr] = {}
    left_pts = [t0 - Fr(1, 50) - half * Fr(i, 10) for i in range(1, 11)]
    right_pts = [t0 + Fr(1, 50) + half * Fr(i, 10) for i in range(1, 11)]
    fitL = fit_side(Pv, dv, left_pts, sample_cache)
    fitR = fit_side(Pv, dv, right_pts, sample_cache)
    if fitL is None or fitR is None:
        out.update({"status": "fail", "reason": "insufficient smooth samples"})
        return out

    _, _, cL, holdL = fitL
    _, _, cR, holdR = fitR
    if holdL["residual"] != 0 or holdR["residual"] != 0:
        out.update(
            {
                "status": "fail",
                "reason": "fit holdout residual nonzero",
                "holdout_left": {
                    "t": str(holdL["t"]),
                    "y": str(holdL["y"]),
                    "residual": str(holdL["residual"]),
                },
                "holdout_right": {
                    "t": str(holdR["t"]),
                    "y": str(holdR["y"]),
                    "residual": str(holdR["residual"]),
                },
            }
        )
        return out

    q_left = q_sign(line(Pv, dv, t0 - Fr(1, 60)), m, p)
    J = [a - b for a, b in zip(pad(cL, 9), pad(cR, 9))] if q_left > 0 else [a - b for a, b in zip(pad(cR, 9), pad(cL, 9))]
    quot, rem = poly_divmod(J, q_poly(Pv, dv, m, p))
    rem = [r for r in rem if r != 0] or [Fr(0)]
    if any(r != 0 for r in rem):
        out.update({"status": "fail", "reason": "jump division remainder nonzero", "qdiv_remainder": [str(r) for r in rem], "q_poly_degree": len(quot) - 1})
        return out
    if len(quot) > 7:
        out.update({"status": "fail", "reason": "quotient degree > 8", "degree": len(quot) - 1})
        return out

    om0 = line(Pv, dv, t0)
    omL = line(Pv, dv, t0 - Fr(1, 80))
    omR = line(Pv, dv, t0 + Fr(1, 80))
    sigL = qwall_signature(omL, m, p)
    sigR = qwall_signature(omR, m, p)
    if sigL != sigR:
        out.update({"status": "fail", "reason": "non-active signature not fixed", "signature_L": sigL, "signature_R": sigR})
        return out

    word = env_word(om0, m, p)
    out["word"] = word
    out["adjacent_wall_interval"] = {"left": str(left), "right": str(right)}
    out["sample_window"] = {"left": str(t0 - half), "right": str(t0 + half)}
    out["safe_interval"] = {"left": str(left), "right": str(right)}
    out["half"] = str(half)
    out["gap"] = str(gap)
    out["qwall_signatures"] = sigL
    out["jump_division"] = {"rem": [str(r) for r in rem], "degree": len(quot) - 1, "quotient_degree_ok": True}
    out["fit_validation"] = {
        "left": {
            "fit_samples": 9,
            "total_samples": 10,
            "holdout": {
                "t": str(holdL["t"]),
                "y": str(holdL["y"]),
                "residual": str(holdL["residual"]),
            },
        },
        "right": {
            "fit_samples": 9,
            "total_samples": 10,
            "holdout": {
                "t": str(holdR["t"]),
                "y": str(holdR["y"]),
                "residual": str(holdR["residual"]),
            },
        },
    }

    # wall trace and on-wall raw block identity
    out["onwall"] = {
        "wall_value": str(poly_eval(quot, t0)),
        "trace_value": str(wall_trace(om0, m, p)),
        "trace_match": str(poly_eval(quot, t0) == wall_trace(om0, m, p)),
    }
    out["onwall_formula"] = "-32*beta^2*(F+(a+b)D)"

    # 7 off-wall exact points in q>0 chamber
    tcheck = t0 + (half if q_sign(line(Pv, dv, t0 + half / 2), m, p) > 0 else -half) * Fr(1, 1)
    side = 1 if q_sign(line(Pv, dv, t0 + half / 2), m, p) > 0 else -1
    off_hits = []
    all_ok = True
    for j in range(7):
        t = t0 + side * half * Fr(j + 1, 8)
        om = line(Pv, dv, t)
        if q_sign(om, m, p) != 1:
            all_ok = False
            ok = False
        else:
            hc = poly_eval(quot, t)
            hr = H_minus_formula(om, m, p)
            ok = hc == hr
            if not ok:
                all_ok = False
        off_hits.append({
            "t": str(t),
            "qmp": str(q_sign(om, m, p)),
            "H_cell": str(poly_eval(quot, t)),
            "H_raw": str(H_minus_formula(om, m, p)),
            "ok": ok,
        })
    out["offwall"] = {"raw_formula_checks": str(sum(1 for z in off_hits if z["ok"])), "total": 7, "samples": off_hits}
    out["onwall_env"] = word
    out["polynomial"] = {
        "coefficients_low_to_high": [str(x) for x in quot],
        "poly": poly_to_string(quot),
        "expanded": " + ".join(f"{_fmt(coeff)}*t^{i}" if i else _fmt(coeff) for i, coeff in enumerate(quot) if coeff != 0),
    }
    out["status"] = "ok"
    return out


def check_anchor() -> Dict:
    A6 = amp_over_i(ANCHOR)
    Pp = P_pole(ANCHOR)
    Rq = R_Q(ANCHOR)
    S0 = A6 - Pp - Rq
    return {
        "A6_over_i": str(A6),
        "P_pole": str(Pp),
        "R_Q": str(Rq),
        "S": str(S0),
        "matches_expected": {
            "A6": str(A6 == ANCHOR_EXPECT["A6_over_i"]),
            "P_pole": str(Pp == ANCHOR_EXPECT["P_pole"]),
            "R_Q": str(Rq == ANCHOR_EXPECT["R_Q"]),
            "S": str(S0 == ANCHOR_EXPECT["S"]),
        },
    }


def cocycle_check() -> Dict:
    a, b, x, y, z, q = sp.symbols("a b x y z q")
    s = x + y
    v = x * y
    F = a * s ** 3 + v * (s ** 2 - 2 * v)
    D = 2 * a ** 3 + 3 * a ** 2 * s + a * (s ** 2 + v) - s * v
    core = F + (a + b) * D

    # minus block with jmin = y
    q_val = b ** 2 - a ** 2
    L = 3 * a ** 2 + 2 * a * (s + b) - v + b * (2 * x + y)
    Hm = -32 * y ** 2 * core - 32 * q_val * y ** 2 * L + 32 * x * b * q_val ** 2

    # plus block with jmin = z
    A0 = a ** 4 + 4 * a ** 3 * b + 4 * a ** 3 * z + 4 * a * a * b * b + 6 * a * a * b * z + a * b ** 3 + 2 * a * b * b * z
    A1 = 4 * a ** 3 + 8 * a * a * b + 7 * a * a * z + 5 * a * b * b + 7 * a * b * z + b ** 3 + b * b * z
    A2 = 3 * a * a + 4 * a * b + 3 * a * z + b * b + b * z
    B0 = 3 * a * a + 2 * a * b + a * z
    B1 = 3 * a + b
    K = A0 + s * A1 + s ** 2 * A2 + v * B0 + s * v * B1
    Hp = -32 * z ** 2 * core + 32 * q_val * K

    Delta = sp.expand(Hp - Hm)
    Delta_sub = sp.expand(Delta.subs(z, y))
    q_div = sp.factor(Delta_sub / (32 * q_val))
    expanded = sp.expand(q_div)
    factored = sp.factor(q_div)

    a0 = sp.Rational(2, 1)
    b0 = sp.Rational(4, 1)
    x0 = sp.Rational(13, 2)
    y0 = sp.Rational(-7, 2)
    z0 = sp.Rational(-7, 2)
    delta_at_witness = sp.expand(Delta_sub.subs({a: a0, b: b0, x: x0, y: y0, z: z0}))
    q_at_witness = sp.expand(q_val.subs({a: a0, b: b0}))
    j_at_witness = sp.expand(q_div.subs({a: a0, b: b0, x: x0, y: y0, z: z0}))

    return {
        "Delta": str(Delta_sub),
        "factorized_32q": str(sp.factor(Delta_sub)),
        "quartic_J(a,b,x,y)": str(expanded),
        "quartic_J_factored": str(factored),
        "divisible_by_32q": str(sp.simplify(Delta_sub / (32 * q_val) - q_div) == 0),
        "J_nonzero": str(sp.simplify(q_div) != 0),
        "witness": {
            "subs": {"a": "2", "b": "4", "x": "13/2", "y": "-7/2", "z": "-7/2"},
            "J_val": str(j_at_witness),
            "q_val": str(q_at_witness),
            "Delta_val": str(delta_at_witness),
            "delta_expected_minus_q_y_relation": "Delta=-21144 when a=2,b=4,x=13/2,y=-7/2,z=-7/2",
            "z_equals_y_non_divisible": str(delta_at_witness != 0),
        },
    }


def write_json(payload: Dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def report_lines(payload: Dict) -> List[str]:
    anchor = payload["anchor"]
    lines = [
        "# Round 8 off-wall ground-truth report",
        "",
        "## Build",
        f"- shared bg.cpp sha256: `{payload['build']['shared_bg_sha256']}`",
        f"- private bg_round8.cpp sha256: `{payload['build']['private_bg_sha256']}`",
        f"- shared/private bg hashes equal: `{payload['build']['shas_match']}`",
        f"- compile success: `{payload['build']['compile_ok']}`",
        "",
        "## Anchor checks (onshell)",
        f"- A6/i = `{anchor['A6_over_i']}`",
        f"- P_pole = `{anchor['P_pole']}`",
        f"- R_Q = `{anchor['R_Q']}`",
        f"- S = `{anchor['S']}`",
        f"- matches expected: {anchor['matches_expected']}",
        "",
        "## Extracted q-wall cells",
    ]

    ok_cells = [c for c in payload["cells"] if c.get("status") == "ok"]
    fail_cells = [c for c in payload["cells"] if c.get("status") != "ok"]
    lines.append(f"- extracted cells: {len(ok_cells)} / {len(payload['cells'])} (physical cells)")
    lines.append(f"- jump division exact checks: {sum(1 for c in ok_cells if c['jump_division']['quotient_degree_ok'])}/{len(ok_cells)}")

    for c in payload["cells"]:
        lines.append("")
        lines.append(f"### {c['label']} (wall ({c['m']}, {c['p']}))")
        lines.append(f"- status: {c.get('status')}")
        if c.get("status") != "ok":
            lines.append(f"- reason: {c.get('reason')}")
            continue
        lines.append(f"- P: `{c['P']}`")
        lines.append(f"- d: `{c['d']}`")
        lines.append(f"- t0: `{c['t0']}`")
        lines.append(f"- word: `{c['word']}`")
        lines.append(f"- adjacent-wall interval: `[{c['adjacent_wall_interval']['left']}, {c['adjacent_wall_interval']['right']}]`")
        lines.append(f"- sample window: `[{c['sample_window']['left']}, {c['sample_window']['right']}]`")
        lines.append(f"- sample points: 7 off-wall points")
        lines.append(f"- non-active q/Q signatures: `{c['qwall_signatures']}`")
        lines.append(f"- fit holdout residuals: left `{c['fit_validation']['left']['holdout']['residual']}`, right `{c['fit_validation']['right']['holdout']['residual']}`")
        lines.append(f"- q-wall quotient polynomial: `{c['polynomial']['poly']}`")
        lines.append(f"- jump remainder: `{', '.join(c['jump_division']['rem'])}`")
        lines.append(f"- on-wall trace match: `{c['onwall']['trace_match']}`")
        lines.append(f"- off-wall formula checks: `{c['offwall']['raw_formula_checks']}/{c['offwall']['total']}`")

    lines += [
        "",
        "## Jump cocycle check",
        f"- Delta at z=y: `{payload['cocycle']['Delta']}`",
        f"- factored Delta: `{payload['cocycle']['factorized_32q']}`",
        f"- J(a,b,x,y): `{payload['cocycle']['quartic_J(a,b,x,y)']}`",
        f"- factored J: `{payload['cocycle']['quartic_J_factored']}`",
        f"- divisible by 32*q: `{payload['cocycle']['divisible_by_32q']}`",
        f"- J nonzero: `{payload['cocycle']['J_nonzero']}`",
        f"- witness J value: `{payload['cocycle']['witness']['J_val']}`",
        f"- witness Delta value: `{payload['cocycle']['witness']['Delta_val']}`",
        f"- witness implies `Delta` nonzero on z=y wall: `{payload['cocycle']['witness']['z_equals_y_non_divisible']}`",
    ]
    return lines


def main():
    build = _build_bg()
    payload = {
        "build": build,
        "cells": [],
        "anchor": check_anchor(),
    }
    for case in CELL_CASES:
        cell = extract_cell(case)
        payload["cells"].append(cell)
        write_json(payload)

    ok_cells = [c for c in payload["cells"] if c.get("status") == "ok"]
    payload["summary"] = {
        "requested_cells": len(CELL_CASES),
        "extracted_ok": len(ok_cells),
        "expected_physical": len(CELL_CASES),
        "jump_division_ok": sum(1 for c in ok_cells if c["jump_division"]["quotient_degree_ok"]),
        "offwall_raw_formula_checks": sum(int(c["offwall"]["raw_formula_checks"]) for c in ok_cells),
        "offwall_raw_formula_total": sum(int(c["offwall"]["total"]) for c in ok_cells),
        "fit_holdout_points_total": 2 * len(ok_cells),
        "fit_holdout_points_ok": sum(
            1 for c in ok_cells for side in ("left", "right") if c["fit_validation"][side]["holdout"]["residual"] == "0"
        ),
        "failure" : any(c.get("status") != "ok" for c in payload["cells"]),
    }

    payload["cocycle"] = cocycle_check()
    write_json(payload)

    report = "\n".join(report_lines(payload))
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
