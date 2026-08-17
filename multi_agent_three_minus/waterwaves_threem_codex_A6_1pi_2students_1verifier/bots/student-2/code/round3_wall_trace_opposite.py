#!/usr/bin/env python3
"""Exact scan of the compact H24 trace on the component w4=-w2."""

import json
import random
from fractions import Fraction

import sympy as sp

from round3_bottomup import DATA, R2, build_fresh_oracle, fstr, generic_oracle_point
from round3_wall_trace_scan import FastBGOracle, wall_environment


def predicted_trace(point):
    a = point.omega[1]
    x, y = point.omega[0], point.omega[2]
    s = x+y
    v = x*y
    beta = min(abs(point.omega[i]) for i in (0, 2, 4, 5))
    return -32*beta*beta*(a*s**3+v*(s*s-2*v)), beta


def trace_one(oracle, B, c, e):
    t = sp.Symbol("t")
    t0 = Fraction(B, 2)
    offsets = [Fraction(1, k) for k in range(50, 70)]
    samples = []
    env0 = None
    for delta in [-x for x in offsets] + offsets:
        tv = t0+delta
        point = R2.SixPoint(tv, c, tv-Fraction(B), e)
        if not generic_oracle_point(point):
            raise ValueError("nongeneric nearby point")
        env = wall_environment(point)
        if env0 is None:
            env0 = env
        elif env != env0:
            raise ValueError("non-primary wall changed")
        result, err = R2.safe_on_shell(
            oracle, 6, [point.b, point.c, point.d, point.e]
        )
        if result is None:
            raise ValueError("BG failed: %s" % err)
        _, re_part, im_part = result
        if re_part != 0:
            raise ValueError("non-imaginary amplitude")
        R = R2.wall_pole_subtracted(point, im_part)[0]
        Sfree = point.b+point.c+point.d+point.e
        scaled = R*Sfree**8
        samples.append((tv, point.pair_q["q_2_4"], scaled, Sfree))
    positive = [x for x in samples if x[1] > 0]
    negative = [x for x in samples if x[1] < 0]
    if len(positive) != 20 or len(negative) != 20:
        raise ValueError("bad side count")

    def fit(side):
        train = [
            (sp.Rational(x[0].numerator, x[0].denominator),
             sp.Rational(x[2].numerator, x[2].denominator))
            for x in side[:17]
        ]
        poly = sp.Poly(sp.expand(sp.interpolate(train, t)), t, domain=sp.QQ)
        hold = []
        for tv, q, obs, Sfree in side[17:]:
            pred = poly.eval(sp.Rational(tv.numerator, tv.denominator))
            residual = pred-sp.Rational(obs.numerator, obs.denominator)
            hold.append({"t": fstr(tv), "residual": str(residual)})
        return poly, hold

    plus, hp = fit(positive)
    minus, hm = fit(negative)
    qexpr = sp.expand((t-sp.Rational(B))**2-t**2)
    Sexpr = 2*t-sp.Rational(B)+sp.Rational(c)+sp.Rational(e)
    Hexpr = sp.cancel((plus.as_expr()-minus.as_expr())/(qexpr*Sexpr**8))
    Hwall = sp.cancel(Hexpr.subs(t, sp.Rational(t0.numerator, t0.denominator)))
    wall = R2.SixPoint(t0, c, -t0, e)
    predicted, beta = predicted_trace(wall)
    predsp = sp.Rational(predicted.numerator, predicted.denominator)
    return {
        "seed": {"B": fstr(B), "c": fstr(c), "e": fstr(e)},
        "wall_omega": [fstr(x) for x in wall.omega],
        "wall_word_limit": wall.sorted_word()[0],
        "beta": fstr(beta),
        "environment": list(env0),
        "scaled_plus_degree": plus.degree(),
        "scaled_minus_degree": minus.degree(),
        "H_wall_observed": str(Hwall),
        "H_wall_compact_formula": str(predsp),
        "residual": str(Hwall-predsp),
        "holdouts": hp+hm,
        "holdout_zero_count": sum(x["residual"] == "0" for x in hp+hm),
    }


def main():
    built, build_cmd = build_fresh_oracle()
    oracle = FastBGOracle(built.binary)
    rng = random.Random(2026072603)
    curated = [
        (6, 2, 3), (8, -3, 5), (-6, 4, -3), (-10, -3, 4),
        (4, -8, 1), (4, -4, -8), (4, 3, -4), (5, -5, 2),
    ]
    candidates = curated
    results = []
    counterexamples = []
    seen = set()
    rejected = {}
    for raw in candidates:
        if len(results)+len(counterexamples) >= 1:
            break
        B, c, e = map(Fraction, raw)
        try:
            probe = R2.SixPoint(B/2-Fraction(1, 60), c,
                                -B/2-Fraction(1, 60), e)
            env = wall_environment(probe)
            if env in seen:
                continue
            record = trace_one(oracle, B, c, e)
            if record["holdout_zero_count"] != 6:
                rejected["holdout"] = rejected.get("holdout", 0)+1
                continue
            seen.add(env)
            if record["residual"] == "0":
                results.append(record)
            else:
                counterexamples.append(record)
        except Exception as exc:
            key = type(exc).__name__+":"+str(exc)[:80]
            rejected[key] = rejected.get(key, 0)+1
        # Do not grind in a region if the candidate fails globally.
        if len(results)+len(counterexamples) >= 1:
            break

    payload = {
        "meta": {
            "build_command": " ".join(build_cmd),
            "formula": (
                "H24=-32*beta^2*(a*s^3+v*(s^2-2*v)); "
                "a=w2=-w4, s=w1+w3, v=w1*w3, "
                "beta=min(|w1|,|w3|,|w5|,|w6|)"
            ),
            "rejected": rejected,
        },
        "results": results,
        "counterexamples": counterexamples,
        "counts": {
            "distinct_success_environments": len(results),
            "zero_formula_residuals": sum(x["residual"] == "0" for x in results),
            "formula_counterexamples": len(counterexamples),
            "zero_holdouts": sum(x["holdout_zero_count"] for x in results+counterexamples),
            "total_holdouts": 6*len(results+counterexamples),
        },
    }
    out = DATA/"round3_wall_trace_opposite.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True))
    report = DATA/"round3_wall_trace_opposite_report.md"
    report.write_text("\n".join([
        "# Exact compact opposite-energy q24-wall trace scan",
        "",
        "- success environments: `%d`" % len(results),
        "- compact-formula zero residuals: `%d/%d`"
          % (payload["counts"]["zero_formula_residuals"], len(results)),
        "- counterexamples: `%d`" % len(counterexamples),
        "- branch-fit exact holdouts: `%d/%d`"
          % (payload["counts"]["zero_holdouts"], payload["counts"]["total_holdouts"]),
        "- formula: `%s`" % payload["meta"]["formula"],
        "",
        "Full exact witnesses: `%s`." % out,
    ]))
    print(out)
    print(report)


if __name__ == "__main__":
    main()
