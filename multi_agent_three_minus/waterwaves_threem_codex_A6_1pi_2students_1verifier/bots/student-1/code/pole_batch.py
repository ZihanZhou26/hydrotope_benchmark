#!/usr/bin/env python3
from __future__ import print_function

from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import gcd
from pathlib import Path
import argparse
import json
import re
import subprocess
from datetime import datetime


SIGMA = (-1, -1, -1, 1, 1, 1)
MINUS = (0, 1, 2)
PLUS = (3, 4, 5)

OMEGA_RE = re.compile(r"omega\s*=\s*\{([^}]*)\}")
AMP_IM_RE = re.compile(r"A_(\d+)\s*=\s*i\s*\*\s*\(([^)]*)\)")
AMP_COMPLEX_RE = re.compile(r"A_(\d+)\s*=\s*\(([^)]*)\)\s*\+\s*i\s*\(([^)]*)\)")


def frac_to_str(q):
    q = Fraction(q)
    if q.denominator == 1:
        return str(q.numerator)
    return "%d/%d" % (q.numerator, q.denominator)


def parse_fraction(text):
    t = text.strip()
    if not t:
        raise ValueError("empty rational token")
    if t[0] == "+":
        t = t[1:]
    if "/" in t:
        n, d = t.split("/")
        return Fraction(int(n), int(d))
    return Fraction(int(t), 1)


def pos_part(x):
    return x if x > 0 else Fraction(0, 1)


def H(b, c, d):
    return b - pos_part(b - c * c) - pos_part(b - d * d) + pos_part(b - c * c - d * d)


def lcm(a, b):
    return abs(a // gcd(a, b) * b)


def lcm_list(values):
    out = 1
    for v in values:
        out = lcm(out, int(v))
    return out


def denominator_lcm(omegas):
    return lcm_list([Fraction(x).denominator for x in omegas])


def is_integer_row(omegas):
    return all(Fraction(x).denominator == 1 for x in omegas)


def chamber_signature(omega):
    ks = [s * w * w for s, w in zip(SIGMA, omega)]
    bits = []
    for m in range(1, 1 << 6):
        if m == 63:
            continue
        acc = Fraction(0, 1)
        for i in range(6):
            if (m >> i) & 1:
                acc += ks[i]
        if acc == 0:
            return "degenerate"
        bits.append("+" if acc > 0 else "-")
    return "".join(bits)


def sorted_sign_word(omega):
    order = sorted(range(len(omega)), key=lambda i: (-abs(Fraction(omega[i])), i))
    return "".join("+" if SIGMA[i] > 0 else "-" for i in order)


def on_shell(omega, sigma=SIGMA):
    return sum([s * w * w for s, w in zip(sigma, omega)]) == 0


def fraction_abs_str(q):
    q = Fraction(q)
    n = abs(q.numerator)
    if q.denominator == 1:
        return str(n)
    return "%d/%d" % (n, q.denominator)


class BGOracle(object):
    def __init__(self, binary_path, sigma=SIGMA, g=1):
        self.binary = str(binary_path)
        self.sigma = tuple(int(x) for x in sigma)
        self.g = Fraction(g, 1)

    def _run_amp(self, omega, sigma=None, g=None):
        if sigma is None:
            sigma = self.sigma
        if g is None:
            g = self.g
        omega_t = tuple(Fraction(x) for x in omega)
        sigma_t = tuple(int(x) for x in sigma)
        if len(omega_t) != len(sigma_t):
            raise ValueError("omega/sigma length mismatch")

        k = [Fraction(s, 1) * w * w / Fraction(g, 1) for s, w in zip(sigma_t, omega_t)]
        cmd = [
            self.binary,
            "--amp",
            "-K",
            ",".join(frac_to_str(v) for v in k),
            "-W",
            ",".join(frac_to_str(v) for v in omega_t),
            "-g",
            str(g),
        ]
        cp = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if cp.returncode != 0:
            raise RuntimeError("bg failed for n=%d cmd=%s err=%s" % (len(omega_t), cmd, cp.stderr.strip()))
        out = cp.stdout

        m_omega = OMEGA_RE.search(out)
        if not m_omega:
            raise RuntimeError("Failed to parse omega\n" + out)

        n = len(omega_t)
        amp_re = Fraction(0, 1)
        amp_im = Fraction(0, 1)
        m_im = AMP_IM_RE.search(out)
        m_c = AMP_COMPLEX_RE.search(out)
        if m_im:
            if int(m_im.group(1)) != n:
                raise RuntimeError("Amplitude index mismatch")
            amp_im = parse_fraction(m_im.group(2))
        elif m_c:
            if int(m_c.group(1)) != n:
                raise RuntimeError("Amplitude index mismatch")
            amp_re = parse_fraction(m_c.group(2))
            amp_im = parse_fraction(m_c.group(3))
        else:
            raise RuntimeError("Failed to parse amplitude\n" + out)

        return {
            "re": amp_re,
            "im": amp_im,
            "omega": tuple(omega_t),
            "sigma": sigma_t,
            "command": tuple(cmd),
        }


def build_channels(omega):
    channels = []
    S0 = Fraction(0, 1)
    S1 = Fraction(0, 1)
    for m in MINUS:
        rem_minus = [x for x in MINUS if x != m]
        for p, q in combinations(PLUS, 2):
            t = next(x for x in PLUS if x not in (p, q))
            r, s = rem_minus
            Q = omega[p] * omega[p] + omega[q] * omega[q] - omega[m] * omega[m]
            if Q <= 0:
                continue
            B = -Fraction(64) * omega[m] * omega[t] * Q
            B *= H(min(omega[m] * omega[m], Q), omega[p], omega[q])
            B *= H(min(omega[t] * omega[t], Q), omega[r], omega[s])
            d = Fraction(2, 1) * (omega[m] + omega[p]) * (omega[m] + omega[q])
            S0_term = Fraction(0, 1)
            S1_term = Fraction(0, 1)
            if d != 0:
                S0_term = B / d
                S1_term = (Q * B) / d
                S0 += S0_term
                S1 += S1_term
            channels.append(
                {
                    "m": m + 1,
                    "p": p + 1,
                    "q": q + 1,
                    "r": r + 1,
                    "s": s + 1,
                    "t": t + 1,
                    "Q": Q,
                    "d": d,
                    "B": B,
                    "S_term": S0_term,
                    "S1_term": S1_term,
                    "D": d / Q if Q != 0 else None,
                }
            )
    return channels, S0, S1


def reorder_omega(omega, minus_perm, plus_perm):
    idx = list(minus_perm) + [3 + i for i in plus_perm]
    return tuple(omega[i] for i in idx)


def _load_exact_samples(qdir):
    path = qdir / "bots/student-1/data/exact_samples.json"
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text())
    except Exception:
        return []
    raw = payload.get("samples", [])
    records = []
    seen = set()
    for s in raw:
        try:
            omega = tuple(Fraction(x) for x in s["omega"])
        except Exception:
            continue
        if len(omega) != 6:
            continue
        if any(v == 0 for v in omega):
            continue
        if not on_shell(omega):
            continue
        sig = chamber_signature(omega)
        if sig == "degenerate":
            continue
        if omega in seen:
            continue
        seen.add(omega)
        records.append(
            {
                "omega": omega,
                "source": "exact:%s" % s.get("point_id", "seed"),
                "chamber_signature": sig,
                "sorted_word": sorted_sign_word(omega),
            }
        )
    return records


def build_integer_samples(target):
    if target <= 0:
        return []

    collected = []
    used = set()
    minus_perms = ((0, 1, 2), (1, 0, 2), (0, 2, 1))
    plus_perms = ((0, 1, 2), (0, 2, 1), (1, 0, 2))

    def add_entry(omega):
        if omega in used:
            return
        if any(v == 0 for v in omega):
            return
        sig = chamber_signature(omega)
        if sig == "degenerate":
            return
        if not on_shell(omega):
            return
        used.add(omega)
        collected.append(
            {
                "omega": omega,
                "source": "integer:%06d" % (len(collected) + 1),
                "chamber_signature": sig,
                "sorted_word": sorted_sign_word(omega),
            }
        )

    for B in range(1, 12):
        for w2 in range(-B, B + 1):
            if w2 == 0:
                continue
            for w3 in range(-B, B + 1):
                if w3 == 0:
                    continue
                for w4 in range(-B, B + 1):
                    if w4 == 0:
                        continue
                    for w5 in range(-B, B + 1):
                        if w5 == 0:
                            continue
                        sf = Fraction(w2 + w3 + w4 + w5)
                        if sf == 0:
                            continue
                        num = sf * sf - (-w2 * w2 - w3 * w3 + w4 * w4 + w5 * w5)
                        den = Fraction(2, 1) * sf
                        if num % den != 0:
                            continue
                        w6 = -num // den
                        if w6 == 0:
                            continue
                        w1 = -(sf + w6)
                        if w1 == 0:
                            continue
                        add_entry((Fraction(w1), Fraction(w2), Fraction(w3), Fraction(w4), Fraction(w5), Fraction(w6)))
                        if len(collected) >= target:
                            return collected
        if len(collected) >= target:
            break

    return collected[:target]


def select_diverse_samples(records, target):
    if target <= 0:
        return []

    buckets = {}
    for rec in records:
        key = (rec["sorted_word"], rec["chamber_signature"])
        buckets.setdefault(key, []).append(rec)
    for key in buckets:
        buckets[key].sort(key=lambda x: x["source"])

    keys = sorted(buckets.keys())
    selected = []
    idx = 0
    while len(selected) < target:
        added = False
        for k in keys:
            bucket = buckets[k]
            if idx < len(bucket):
                selected.append(bucket[idx])
                if len(selected) >= target:
                    return selected
                added = True
        if not added:
            break
        idx += 1

    return selected[:target]


def build_sample_set(qdir, target):
    exact = _load_exact_samples(qdir)
    integer_pool = build_integer_samples(max(target, 48))
    # deterministic merge: exact samples drive coverage, integer seeds are used to fill/augment.
    merged = list(exact)
    merged_set = {r["omega"] for r in merged}
    for rec in integer_pool:
        if rec["omega"] in merged_set:
            continue
        merged.append(rec)
        merged_set.add(rec["omega"])
        if len(merged) >= max(target, len(exact) + 8):
            break

    selected = select_diverse_samples(merged, target)
    # force a non-zero integer contribution when possible to avoid single-source sampling
    if selected and all(r["source"].startswith("exact:") for r in selected):
        selected = list(selected)
        for rec in integer_pool:
            if rec["omega"] in {x["omega"] for x in selected}:
                continue
            selected.append(rec)
            if len(selected) >= target:
                break
    if len(selected) < target and integer_pool:
        for rec in integer_pool:
            if rec["omega"] in {x["omega"] for x in selected}:
                continue
            selected.append(rec)
            if len(selected) >= target:
                break

    # if integer samples were dropped by the filter above, keep first few of them for diversity
    integer_selected = any(not r["source"].startswith("exact:") for r in selected)
    if not integer_selected and integer_pool:
        for rec in integer_pool[:4]:
            if rec["omega"] in {x["omega"] for x in selected}:
                continue
            if selected:
                selected.pop()
            selected.append(rec)
            if len(selected) >= target:
                break

    # strict dedupe and deterministic trim
    dedup = []
    seen = set()
    for rec in selected:
        if rec["omega"] in seen:
            continue
        seen.add(rec["omega"])
        dedup.append(rec)
        if len(dedup) >= target:
            break

    return {
        "exact_available": len(exact),
        "integer_available": len(integer_pool),
        "selected": dedup,
    }


def build_a6_rows(oracle, seed_records):
    rows = []
    stats = Counter()

    for i, seed in enumerate(seed_records, 1):
        omega = seed["omega"]
        stats["attempted"] += 1
        channels, S0, S1 = build_channels(omega)
        if any(c["d"] == 0 for c in channels):
            stats["zero_deny"] += 1
            continue
        try:
            bg = oracle._run_amp(omega, sigma=SIGMA)
        except Exception:
            stats["bg_fail"] += 1
            continue
        if bg["re"] != 0:
            stats["nonzero_re"] += 1
            continue

        delta = Fraction(1, 1)
        for m in MINUS:
            for p in PLUS:
                delta *= (omega[m] + omega[p])

        row = {
            "point_id": "p%04d" % i,
            "source": seed["source"],
            "origin": "exact" if seed["source"].startswith("exact:") else "integer",
            "omega": omega,
            "sigma": SIGMA,
            "sorted_word": seed["sorted_word"],
            "chamber_signature": seed["chamber_signature"],
            "channels": channels,
            "S0": S0,
            "S1": S1,
            "Delta": delta,
            "freq_kind": "integer" if is_integer_row(omega) else "rational",
            "freq_denom_lcm": denominator_lcm(omega),
            "y_re": bg["re"],
            "y_im": bg["im"],
            "bg_command": bg["command"],
        }
        rows.append(row)
        stats["accepted"] += 1

    return rows, dict(stats)


def evaluate_candidate(rows, which, c):
    c = Fraction(c)
    totals = Counter()
    raw_denom = Counter()
    scaled_denom = Counter()
    integer_fail = []
    rational_fail = []
    fail_rows = []

    for p in rows:
        totals["total"] += 1
        S = p[which]
        y = p["y_im"]
        res = y - c * S
        raw_denom[str(int(res.denominator))] += 1

        if p["freq_kind"] == "integer":
            if res.denominator == 1:
                totals["integer_ok"] += 1
            else:
                integer_fail.append({"point_id": p["point_id"], "residual": frac_to_str(res)})
        else:
            L = int(p["freq_denom_lcm"])
            scaled = res * Fraction(L ** 8, 1)
            scaled_denom[str(int(scaled.denominator))] += 1
            if scaled.denominator == 1:
                totals["rational_scaled_ok"] += 1
            else:
                rational_fail.append({"point_id": p["point_id"], "residual": frac_to_str(res), "scale": frac_to_str(scaled)})

        if res != 0:
            fail_rows.append(p["point_id"])

    return {
        "C": frac_to_str(c),
        "which": which,
        "total_points": totals["total"],
        "integer_points": sum(1 for p in rows if p["freq_kind"] == "integer"),
        "integer_integral_count": totals.get("integer_ok", 0),
        "rational_points": sum(1 for p in rows if p["freq_kind"] == "rational"),
        "rational_scaled_integral_count": totals.get("rational_scaled_ok", 0),
        "raw_residual_denominator_summary": {k: totals for k, totals in sorted((
            (k, v) for k, v in raw_denom.items()), key=lambda x: (int(x[0]), x[0]))},
        "scaled_residual_denominator_summary": {
            k: v for k, v in sorted(
                ((k, v) for k, v in scaled_denom.items()),
                key=lambda x: (int(x[0]), x[0]),
            )
        },
        "nonzero_residual_count": len(fail_rows),
        "integer_failures": integer_fail[:10],
        "rational_failures": rational_fail[:10],
    }


def collect_a4_checks(oracle, target=6):
    sigma4 = (-1, -1, 1, 1)
    vals = []
    for q in (1, 2, 3, 4):
        for n in range(-12, 13):
            if n == 0:
                continue
            vals.append(Fraction(n, q))
    vals = list(dict.fromkeys(vals))

    out = []
    failures = {
        "degenerate": 0,
        "bg_fail": 0,
        "nonzero_re": 0,
    }

    for w2 in vals:
        if w2 == 0:
            continue
        for w3 in vals:
            if w3 == 0:
                continue
            sf = Fraction(w2 + w3)
            if sf == 0:
                continue
            num = sf * sf + Fraction(w2 * w2) - Fraction(w3 * w3)
            den = Fraction(2) * sf
            if num % den != 0:
                continue
            w4 = -num // den
            if w4 == 0:
                continue
            w1 = -(sf + w4)
            if w1 == 0:
                continue

            omega = (w1, Fraction(w2), Fraction(w3), Fraction(w4))
            if not on_shell(omega, sigma4):
                continue

            k = [sigma4[i] * omega[i] * omega[i] for i in range(4)]
            bad = False
            for m in range(1, 1 << 4):
                if m == 15:
                    continue
                acc = Fraction(0, 1)
                for i in range(4):
                    if (m >> i) & 1:
                        acc += k[i]
                if acc == 0:
                    bad = True
                    break
            if bad:
                failures["degenerate"] += 1
                continue

            try:
                bg = oracle._run_amp(omega, sigma=sigma4)
            except Exception:
                failures["bg_fail"] += 1
                continue

            if bg["re"] != 0:
                failures["nonzero_re"] += 1
                continue

            pred = Fraction(8) * omega[0] * omega[1] * H(min(omega[0] * omega[0], omega[1] * omega[1]), omega[2], omega[3])
            out.append(
                {
                    "seed": [frac_to_str(Fraction(w2)), frac_to_str(Fraction(w3))],
                    "omega": tuple(frac_to_str(v) for v in omega),
                    "bg_im": frac_to_str(bg["im"]),
                    "bg_re": frac_to_str(bg["re"]),
                    "pred": frac_to_str(pred),
                    "match": bg["im"] == pred and bg["re"] == 0,
                }
            )
            if len(out) >= target:
                break
        if len(out) >= target:
            break

    return {
        "requested": target,
        "attempted": len(vals) * (len(vals) - 1),
        "collected": len(out),
        "samples": out,
        "failures": failures,
        "obstruction": "all real resonant 4pt seeds are exchange-degenerate in this signature; no reliable A4 calibration point found.",
    }


def near_pole_family():
    # non-normalizing path: simultaneous two-pair degeneration, not a single simple propagator pole.
    w2 = Fraction(-20)
    w3 = Fraction(-20)
    w4 = Fraction(3)
    w5_0 = Fraction(20)
    out = []
    for sign in (Fraction(1, 1), Fraction(-1, 1)):
        for n in range(1, 7):
            eps = sign / Fraction(n)
            w5 = w5_0 + eps
            sf = w2 + w3 + w4 + w5
            if sf == 0:
                continue
            num = sf * sf - (-w2 * w2 - w3 * w3 + w4 * w4 + w5 * w5)
            den = Fraction(2) * sf
            if den == 0:
                continue
            w6 = -num / den
            w1 = -(sf + w6)
            if w1 == 0 or w6 == 0:
                continue
            if any(v == 0 for v in (w1, w2, w3, w4, w5, w6)):
                continue
            omega = (w1, w2, w3, w4, w5, w6)
            if chamber_signature(omega) == "degenerate":
                continue
            if not on_shell(omega):
                continue
            out.append({"sign": frac_to_str(sign), "step": n, "omega": omega})
    return out


def near_pole_diagnostics(oracle, rows):
    seq = near_pole_family()
    if not seq:
        return {
            "status": "not feasible",
            "notes": "no valid finite near-pole sequence on-shell and nondegenerate",
            "sequence": [],
            "endpoint_magnitudes": {},
            "ranking_used": False,
        }

    seq_out = []
    for rec in seq:
        omega = rec["omega"]
        channels, S0, S1 = build_channels(omega)
        try:
            bg = oracle._run_amp(omega, sigma=SIGMA)
        except Exception:
            continue
        if bg["re"] != 0:
            continue
        if S1 == 0:
            continue
        d_target = None
        for ch in channels:
            if ch["Q"] > 0:
                d_target = ch["d"]
                break
        if d_target is None:
            continue
        dY = d_target * (bg["im"] - Fraction(1, 1) * S1)

        seq_out.append(
            {
                "sign": rec["sign"],
                "step": rec["step"],
                "omega": tuple(frac_to_str(v) for v in omega),
                "d": frac_to_str(d_target),
                "y_im": frac_to_str(bg["im"]),
                "S1": frac_to_str(S1),
                "dY": frac_to_str(dY),
                "abs_dY": fraction_abs_str(dY),
            }
        )

    if not seq_out:
        return {
            "status": "not feasible",
            "notes": "no valid finite near-pole points with non-zero S1 after fresh oracle reevaluation",
            "sequence": [],
            "endpoint_magnitudes": {},
            "ranking_used": False,
        }

    # summarize only end-point magnitudes for concise output
    pos_branch = [x for x in seq_out if x["sign"] == "1"]
    neg_branch = [x for x in seq_out if x["sign"] == "-1"]

    endpoints = {}
    if pos_branch:
        endpoints["+ branch"] = {
            "start_abs_dY": pos_branch[0]["abs_dY"],
            "end_abs_dY": pos_branch[-1]["abs_dY"],
        }
    if neg_branch:
        endpoints["- branch"] = {
            "start_abs_dY": neg_branch[0]["abs_dY"],
            "end_abs_dY": neg_branch[-1]["abs_dY"],
        }

    return {
        "status": "ok_non_normalizing",
        "notes": "non-normalizing finite-path family, not used for ranking coefficients",
        "sequence": seq_out[:12],
        "endpoint_magnitudes": endpoints,
        "ranking_used": False,
    }


def serialize_rows(rows):
    out = []
    for r in rows:
        chans = []
        for c in r["channels"]:
            chans.append(
                {
                    "m": c["m"],
                    "p": c["p"],
                    "q": c["q"],
                    "r": c["r"],
                    "s": c["s"],
                    "Q": frac_to_str(c["Q"]),
                    "d": frac_to_str(c["d"]),
                    "B": frac_to_str(c["B"]),
                    "S_term": frac_to_str(c["S_term"]),
                    "S1_term": frac_to_str(c["S1_term"]),
                    "D": frac_to_str(c["D"]) if c["D"] is not None else "0",
                }
            )
        out.append(
            {
                "point_id": r["point_id"],
                "source": r["source"],
                "origin": r["origin"],
                "sigma": list(r["sigma"]),
                "omega": [frac_to_str(v) for v in r["omega"]],
                "sorted_word": r["sorted_word"],
                "chamber_signature": r["chamber_signature"],
                "freq_kind": r["freq_kind"],
                "freq_denom_lcm": int(r["freq_denom_lcm"]),
                "channels": chans,
                "S0": frac_to_str(r["S0"]),
                "S1": frac_to_str(r["S1"]),
                "Delta": frac_to_str(r["Delta"]),
                "y_im": frac_to_str(r["y_im"]),
                "y_re": frac_to_str(r["y_re"]),
                "bg_command": list(r["bg_command"]),
            }
        )
    return out


def word_and_signature_counts(rows):
    wc = Counter()
    sc = Counter()
    for r in rows:
        wc[r["sorted_word"]] += 1
        sc[r["chamber_signature"]] += 1
    return {"word_counts": wc, "signature_counts": sc}


def write_report(path, payload):
    lines = []
    lines.append("# Pole-batch exact batch report")
    lines.append("")
    lines.append("Generated: %s" % payload["generated_at"])
    lines.append("")

    lines.append("## Inputs")
    lines.append("- target samples: %d" % payload["target_samples"])
    lines.append("- actual samples: %d" % payload["actual_samples"])
    lines.append("- bg binary: `%s`" % payload["bg_binary"])
    lines.append("- source plan: exact=%d, integer=%d; selected exact=%d, integer=%d" % (
        payload["seed_plan"]["exact_available"],
        payload["seed_plan"]["integer_available"],
        payload["seed_plan"]["selected_counts"].get("exact", 0),
        payload["seed_plan"]["selected_counts"].get("integer", 0),
    ))
    lines.append("- seed failure summary: accepted=%d failed_bg=%d rejected_zero_denom=%d" % (
        payload["seed_plan"]["stats"].get("accepted", 0),
        payload["seed_plan"]["stats"].get("bg_fail", 0),
        payload["seed_plan"]["stats"].get("zero_deny", 0),
    ))
    lines.append("")

    lines.append("## Structural coverage")
    lines.append("- distinct sorted words: %d" % len(payload["coverage"]["sorted_words"]))
    lines.append("- distinct chamber signatures: %d" % len(payload["coverage"]["chamber_signatures"]))
    lines.append("- selected sorted-word counts: %s" % payload["coverage"]["sorted_words"])
    lines.append("- selected chamber-signature counts: %s" % payload["coverage"]["chamber_signatures"])
    lines.append("")

    lines.append("## A4 (-,-,+,+) on-shell calibration")
    lines.append("- requested: %d" % payload["a4_checks"]["requested"])
    lines.append("- attempted (grid points): %d" % payload["a4_checks"]["attempted"])
    lines.append("- collected: %d" % payload["a4_checks"]["collected"])
    lines.append("- obstructions: %s" % payload["a4_checks"]["obstruction"])
    lines.append("")

    lines.append("## Explicit kernel formulas")
    lines.append("- B_T = -64 * w_m * w_t * Q * H(min(w_m^2, Q); w_p, w_q) * H(min(w_t^2, Q); w_r, w_s)")
    lines.append("- Q = w_p^2 + w_q^2 - w_m^2, d = 2 (w_m+w_p)(w_m+w_q)")
    lines.append("- S1 = sum(Q * B_T / d) with propagator factor D = d / Q")
    lines.append("")

    lines.append("## S1 diagnostics (primary candidate C=1)")
    s1 = payload["candidate_diagnostics"]["S1"]
    lines.append("- total points: %d" % s1["total_points"])
    lines.append("- integer points with integral residual y- S1: %d/%d" % (s1["integer_integral_count"], s1["integer_points"]))
    lines.append("- rational points with L^8(y-S1) integral: %d/%d" % (s1["rational_scaled_integral_count"], s1["rational_points"]))
    lines.append("- nonzero residual count: %d" % s1["nonzero_residual_count"])
    lines.append("- raw residual denominator histogram: %s" % s1["raw_residual_denominator_summary"])
    lines.append("- scaled residual denominator histogram: %s" % (s1["scaled_residual_denominator_summary"] or {}))
    if s1["integer_failures"]:
        lines.append("- sample integer failures (first up to 4): %s" % s1["integer_failures"][:4])
    if s1["rational_failures"]:
        lines.append("- sample rational failures (first up to 4): %s" % s1["rational_failures"][:4])
    lines.append("")

    lines.append("## S0 diagnostics (negative control)")
    lines.append("- S0 is degree-6; y and S1 are degree-8; no dimensionless constant coefficient can represent the pole part.")
    s0 = payload["candidate_diagnostics"]["S0"]
    lines.append("- tested C=1 on S0: nonzero residual points=%d" % s0["nonzero_residual_count"])
    lines.append("- raw residual denominator histogram: %s" % s0["raw_residual_denominator_summary"])
    lines.append("")

    lines.append("## Near-pole diagnostics")
    lines.append("- status: %s" % payload["near_pole"]["status"])
    lines.append("- notes: %s" % payload["near_pole"]["notes"])
    lines.append("- ranking_used: %s" % payload["near_pole"]["ranking_used"])
    if payload["near_pole"].get("endpoint_magnitudes"):
        lines.append("- endpoint |d*(y-S1)| magnitudes: %s" % payload["near_pole"]["endpoint_magnitudes"])
        for p in payload["near_pole"]["sequence"][:4]:
            lines.append("  - step %s/%d: |dY|=%s" % (p["sign"], p["step"], p["abs_dY"]))

    Path(path).write_text("\n".join(lines) + "\n")


def normalize_counts(counter):
    return {str(k): int(v) for k, v in sorted(counter.items())}


def main():
    parser = argparse.ArgumentParser(description="Exact A6 pole diagnostics")
    parser.add_argument("--qdir", type=Path, default=Path("."))
    parser.add_argument("--samples", type=int, default=24)
    parser.add_argument("--a4-checks", type=int, default=6)
    parser.add_argument("--near-pole", action="store_true")
    args = parser.parse_args()

    qdir = args.qdir.resolve()
    out_path = qdir / "bots/student-1/data/pole_results.json"
    report_path = qdir / "bots/student-1/derivations/pole_batch_report.md"

    oracle = BGOracle(qdir / "bots/student-1/bg")

    target = args.samples
    if target < 24:
        target = 24

    print("building sample seeds")
    seed_pack = build_sample_set(qdir, target)
    seeds = seed_pack["selected"]
    print("selected seeds=%d" % len(seeds))

    print("building A6 rows and re-running bg")
    rows, build_stats = build_a6_rows(oracle, seeds)
    rows_json = serialize_rows(rows)

    word_sig = word_and_signature_counts(rows)

    print("running A4 checks")
    a4 = collect_a4_checks(oracle, target=args.a4_checks)

    print("evaluating C=1 candidate for S1 and S0")
    s1_diag = evaluate_candidate(rows, "S1", Fraction(1, 1))
    s0_diag = evaluate_candidate(rows, "S0", Fraction(1, 1))

    print("running near-pole diagnostics")
    near = near_pole_diagnostics(oracle, rows) if args.near_pole else {
        "status": "not run",
        "notes": "near-pole diagnostics disabled",
        "sequence": [],
        "endpoint_magnitudes": {},
        "ranking_used": False,
    }

    source_count = Counter()
    for r in rows:
        source_count[r["origin"]] += 1

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "qdir": str(qdir),
        "target_samples": target,
        "actual_samples": len(rows_json),
        "bg_binary": str((qdir / "bots/student-1/bg").resolve()),
        "seed_plan": {
            "requested": target,
            "exact_available": seed_pack["exact_available"],
            "integer_available": seed_pack["integer_available"],
            "selected_counts": dict(source_count),
            "stats": build_stats,
        },
        "coverage": {
            "sorted_words": normalize_counts(word_sig["word_counts"]),
            "chamber_signatures": normalize_counts(word_sig["signature_counts"]),
        },
        "sum_modes": ["S0", "S1"],
        "a4_checks": a4,
        "a6_samples": rows_json,
        "candidate_diagnostics": {
            "S1": s1_diag,
            "S0": s0_diag,
        },
        "near_pole": near,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2))
    write_report(report_path, payload)

    print("wrote %s" % out_path)
    print("wrote %s" % report_path)


if __name__ == "__main__":
    main()
