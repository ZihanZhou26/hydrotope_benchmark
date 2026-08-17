#!/usr/bin/env python3
"""Exact scan of the compact intrinsic H24 trace on q24=0."""

import json
import random
import subprocess
from fractions import Fraction
from pathlib import Path

import sympy as sp

from round3_bottomup import (
    BOT, DATA, R2, build_fresh_oracle, fstr, generic_oracle_point, signature,
)


class FastBGOracle(R2.BGOracle):
    """Same exact parser with a short per-point timeout for scan robustness."""

    def run(self, args):
        proc = subprocess.run(
            [str(self.binary), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=4,
        )
        if proc.returncode != 0:
            raise RuntimeError("bg failed: %s" % proc.stderr.strip())
        return R2.parse_bg_output(proc.stdout, self._extract_n(args))


def wall_environment(point):
    pair, triple = point.sign_maps()
    ans = []
    for key in sorted(pair):
        if key != "q_2_4":
            ans.append((key, pair[key]))
    for key in sorted(triple):
        ans.append((key, triple[key]))
    return tuple(ans)


def compact_same_energy_trace(point):
    """H24 on w4=w2, sorting the two non-primary minus legs by magnitude."""
    a = point.omega[1]
    others = [point.omega[0], point.omega[2]]
    if abs(others[0]) == abs(others[1]):
        raise ValueError("ambiguous remaining-minus ordering")
    x, y = sorted(others, key=lambda z: abs(z), reverse=True)
    s = x+y
    v = x*y
    F = 4*a**4 + 6*a**3*s + 2*a**2*(s*s+v) + (a*s+v)*(s*s-2*v)
    return -32*y*y*F, x, y


def compact_trace_with_order(point, x, y):
    a = point.omega[1]
    s = x+y
    v = x*y
    F = 4*a**4 + 6*a**3*s + 2*a**2*(s*s+v) + (a*s+v)*(s*s-2*v)
    return -32*y*y*F


def exact_branch_trace(oracle, B, c, e):
    t = sp.Symbol("t")
    t0 = Fraction(B, 2)
    samples = []
    base_environment = None
    # Nine interpolation points and three holdouts on each side.
    offsets = [Fraction(k, 1200) for k in range(1, 13)]
    for delta in [-x for x in offsets] + offsets:
        tv = t0+delta
        point = R2.SixPoint(tv, c, Fraction(B)-tv, e)
        if not generic_oracle_point(point):
            raise ValueError("nongeneric nearby point")
        env = wall_environment(point)
        if base_environment is None:
            base_environment = env
        elif env != base_environment:
            raise ValueError("non-primary wall changed")
        result, err = R2.safe_on_shell(
            oracle, 6, [point.b, point.c, point.d, point.e]
        )
        if result is None:
            raise ValueError("BG failed: %s" % err)
        _, re_part, im_part = result
        if re_part != 0:
            raise ValueError("non-imaginary oracle value")
        remainder = R2.wall_pole_subtracted(point, im_part)[0]
        q24 = point.pair_q["q_2_4"]
        samples.append((tv, q24, remainder, point))

    positive = [x for x in samples if x[1] > 0]
    negative = [x for x in samples if x[1] < 0]
    if len(positive) != 12 or len(negative) != 12:
        raise ValueError("bad side counts")

    def fit(side):
        train = [
            (sp.Rational(x[0].numerator, x[0].denominator),
             sp.Rational(x[2].numerator, x[2].denominator))
            for x in side[:9]
        ]
        expr = sp.expand(sp.interpolate(train, t))
        poly = sp.Poly(expr, t, domain=sp.QQ)
        hold = []
        for tv, qv, obs, point in side[9:]:
            pred = poly.eval(sp.Rational(tv.numerator, tv.denominator))
            residual = pred-sp.Rational(obs.numerator, obs.denominator)
            hold.append({
                "t": fstr(tv),
                "observed": fstr(obs),
                "predicted": str(pred),
                "residual": str(residual),
            })
        return poly, hold

    plus_poly, plus_hold = fit(positive)
    minus_poly, minus_hold = fit(negative)
    qexpr = sp.expand((sp.Rational(B)-t)**2-t**2)
    Hexpr = sp.cancel((plus_poly.as_expr()-minus_poly.as_expr())/qexpr)
    Hnum, Hden = sp.together(Hexpr).as_numer_denom()
    if sp.Poly(Hden, t).degree() != 0:
        raise ValueError("non-polynomial H quotient")
    Hwall = sp.cancel(Hexpr.subs(t, sp.Rational(t0.numerator, t0.denominator)))

    wall = R2.SixPoint(t0, c, t0, e)
    predicted, x, y = compact_same_energy_trace(wall)
    predicted_sp = sp.Rational(predicted.numerator, predicted.denominator)
    swapped_prediction = compact_trace_with_order(wall, y, x)
    swapped_sp = sp.Rational(
        swapped_prediction.numerator, swapped_prediction.denominator
    )
    a = wall.omega[1]
    s = wall.omega[0]+wall.omega[2]
    v = wall.omega[0]*wall.omega[2]
    F = 4*a**4+6*a**3*s+2*a**2*(s*s+v)+(a*s+v)*(s*s-2*v)
    other_indices = (0, 2, 4, 5)
    beta_index = min(other_indices, key=lambda i: abs(wall.omega[i]))
    beta = abs(wall.omega[beta_index])
    beta_prediction = -32*beta*beta*F
    beta_sp = sp.Rational(beta_prediction.numerator, beta_prediction.denominator)
    return {
        "seed": {"B": fstr(B), "c": fstr(c), "e": fstr(e)},
        "wall_omega": [fstr(xv) for xv in wall.omega],
        "wall_word_limit": wall.sorted_word()[0],
        "remaining_minus_large_x": fstr(x),
        "remaining_minus_small_y": fstr(y),
        "environment": list(base_environment),
        "plus_degree": plus_poly.degree(),
        "minus_degree": minus_poly.degree(),
        "H_quotient_degree": sp.Poly(Hexpr, t).degree(),
        "H_wall_observed": str(Hwall),
        "H_wall_compact_formula": str(predicted_sp),
        "residual": str(Hwall-predicted_sp),
        "H_wall_swapped_order_formula": str(swapped_sp),
        "swapped_order_residual": str(Hwall-swapped_sp),
        "beta": fstr(beta),
        "beta_leg": beta_index+1,
        "H_wall_beta_formula": str(beta_sp),
        "beta_formula_residual": str(Hwall-beta_sp),
        "plus_holdouts": plus_hold,
        "minus_holdouts": minus_hold,
        "holdout_zero_count": sum(
            h["residual"] == "0" for h in plus_hold+minus_hold
        ),
    }


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    built_oracle, build_cmd = build_fresh_oracle()
    oracle = FastBGOracle(built_oracle.binary)
    rng = random.Random(2026072602)
    curated = [
        (10, 2, 3), (5, 2, 3), (-30, 4, -5),
        (4, -8, -4), (4, -8, 1), (4, -4, -8),
        (4, -4, -5), (4, -4, 1), (4, 3, -4),
        (4, 4, 1), (4, 6, 3), (5, -8, 6),
        (5, -5, 2), (5, -3, -4), (7, 3, 4),
    ]
    candidates = [
        tuple(Fraction(x) for x in seed) for seed in curated
    ]
    fallback = []
    for B in list(range(4, 31)) + list(range(-4, -31, -1)):
        for c in range(-12, 13):
            for e in range(-12, 13):
                if c and e:
                    fallback.append((Fraction(B), Fraction(c), Fraction(e)))
    rng.shuffle(fallback)
    candidates.extend(fallback)
    results = []
    counterexamples = []
    seen_env = set()
    seen_category = set()
    rejected = {}
    for B, c, e in candidates:
        if len(results)+len(counterexamples) >= 17:
            break
        try:
            wall = R2.SixPoint(B/2, c, B/2, e)
            compact, x, y = compact_same_energy_trace(wall)
            # Cheap local isolation before any oracle calls.
            probe = R2.SixPoint(B/2-Fraction(1, 1200), c,
                                B/2+Fraction(1, 1200), e)
            env = wall_environment(probe)
            if env in seen_env:
                continue
            category = (
                0 if abs(wall.omega[0]) > abs(wall.omega[2]) else 2,
                tuple("+" if z > 0 else "-" for z in wall.omega),
            )
            # Encourage coverage, but allow repeats after ten contexts.
            if category in seen_category and len(results) < 10:
                continue
            record = exact_branch_trace(oracle, B, c, e)
            if record["holdout_zero_count"] != 6:
                rejected["nonzero_branch_holdout"] = rejected.get("nonzero_branch_holdout", 0)+1
                continue
            if record["beta_formula_residual"] == "0":
                results.append(record)
            else:
                counterexamples.append(record)
            seen_env.add(env)
            seen_category.add(category)
        except Exception as exc:
            key = type(exc).__name__ + ":" + str(exc)[:80]
            rejected[key] = rejected.get(key, 0)+1

    payload = {
        "meta": {
            "build_command": " ".join(build_cmd),
            "requested_environments": 12,
            "successful_environments": len(results),
            "compact_formula": (
                "H24=-32*beta^2*(4*a^4+6*a^3*s+2*a^2*(s^2+v)"
                "+(a*s+v)*(s^2-2*v)); a=w2=w4, "
                "s=w1+w3, v=w1*w3, "
                "beta=min(|w1|,|w3|,|w5|,|w6|)"
            ),
            "rejected": rejected,
        },
        "results": results,
        "counterexamples": counterexamples,
        "counts": {
            "zero_formula_residuals": sum(x["beta_formula_residual"] == "0" for x in results),
            "zero_branch_holdouts": sum(x["holdout_zero_count"] for x in results),
            "total_branch_holdouts": 6*len(results),
            "distinct_environments": len({
                tuple(tuple(z) for z in x["environment"]) for x in results
            }),
            "small_remaining_minus_label_1": sum(
                abs(Fraction(x["wall_omega"][0])) <
                abs(Fraction(x["wall_omega"][2])) for x in results
            ),
            "small_remaining_minus_label_3": sum(
                abs(Fraction(x["wall_omega"][2])) <
                abs(Fraction(x["wall_omega"][0])) for x in results
            ),
            "compact_formula_counterexamples": len(counterexamples),
            "smaller_minus_selector_counterexamples": sum(
                x["residual"] != "0" for x in results+counterexamples
            ),
        },
    }
    out = DATA / "round3_wall_trace_scan.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True))
    report = DATA / "round3_wall_trace_scan_report.md"
    report.write_text("\n".join([
        "# Exact compact q24-wall trace scan",
        "",
        "- distinct wall environments: `%d`" % payload["counts"]["distinct_environments"],
        "- compact-formula zero residuals: `%d/%d`"
          % (payload["counts"]["zero_formula_residuals"], len(results)),
        "- counterexamples to the corrected beta selector: `%d`"
          % payload["counts"]["compact_formula_counterexamples"],
        "- exact counterexamples to the earlier smaller-minus selector: `%d`"
          % payload["counts"]["smaller_minus_selector_counterexamples"],
        "- branch-fit exact holdouts: `%d/%d`"
          % (payload["counts"]["zero_branch_holdouts"],
             payload["counts"]["total_branch_holdouts"]),
        "- smaller remaining-minus label 1 / label 3: `%d/%d`"
          % (payload["counts"]["small_remaining_minus_label_1"],
             payload["counts"]["small_remaining_minus_label_3"]),
        "- formula: `%s`" % payload["meta"]["compact_formula"],
        "",
        "Full exact witnesses: `%s`." % out,
    ]))
    print(out)
    print(report)


if __name__ == "__main__":
    main()
