#!/usr/bin/env python3
"""Compare exact q24 bricks in two adjacent wall environments."""

import json
from fractions import Fraction
from pathlib import Path

import sympy as sp

from round3_bottomup import ROOT, BOT, DATA, R2, fstr, reduce_w5


def load_poly(path, key):
    payload = json.loads(Path(path).read_text())
    coeffs = payload["brick"][key]
    w = sp.symbols("w1:6")
    expr = 0
    for raw_mon, raw_coeff in coeffs.items():
        mon = tuple(int(x) for x in raw_mon.split(","))
        coeff = sp.Rational(raw_coeff)
        expr += coeff * sp.prod(w[i] ** mon[i] for i in range(5))
    return payload, sp.Poly(expr, *w, domain=sp.QQ)


def eval_poly(poly, values):
    return sp.Rational(poly.as_expr().subs(dict(zip(poly.gens, values))))


def main():
    path_a = DATA / "round3_context_a.json"
    path_b = DATA / "round3_context_b.json"
    path_c = DATA / "round3_context_c.json"
    pa, Ha = load_poly(path_a, "H24_coefficients")
    pb, Hb = load_poly(path_b, "H24_coefficients")
    pc, Hc = load_poly(path_c, "H24_coefficients")
    keys = pa["left"]["signature_keys"]
    sa = pa["left"]["signature"]
    sb = pb["left"]["signature"]
    diffs = [
        {"wall": key, "a": a, "b": b}
        for key, a, b in zip(keys, sa, sb)
        if a != b
    ]

    w1, w2, w3, w4, w5 = Ha.gens
    q25 = sp.Poly(w5**2 - w2**2, *Ha.gens, domain=sp.QQ)
    # Context A has q25<0 and context B q25>0, so the positive-part
    # convention predicts Hb-Ha=q25*K on analytic continuations.
    diff = Hb - Ha
    K, rem = sp.div(diff, q25)
    factor = sp.factor(K.as_expr())
    factor_list = sp.factor_list(K.as_expr())

    # Exact codimension-two witness: q24=q25=0 at B=6,c=2,e=3.
    wall = R2.SixPoint(Fraction(3), Fraction(2), Fraction(3), Fraction(3))
    wall_values = [sp.Rational(x.numerator, x.denominator)
                   for x in wall.omega[:5]]
    K_wall = eval_poly(K, wall_values)

    # Two off-intersection q24-wall limits, one in each environment.
    witnesses = []
    for B in (Fraction(599, 100), Fraction(601, 100)):
        point = R2.SixPoint(B/2, Fraction(2), B/2, Fraction(3))
        vals = [sp.Rational(x.numerator, x.denominator)
                for x in point.omega[:5]]
        q = vals[4]**2 - vals[1]**2
        lhs = eval_poly(diff, vals)
        rhs = q * eval_poly(K, vals)
        witnesses.append({
            "B": fstr(B),
            "omega": [str(x) for x in vals] + [
                str(sp.Rational(point.omega[5].numerator,
                                point.omega[5].denominator))
            ],
            "q25": str(q),
            "H_b_minus_H_a": str(lhs),
            "q25_times_K": str(rhs),
            "residual": str(lhs-rhs),
        })

    # Relabel 1<->2 to the requested H14 convention.  Under this swap,
    # the finer q25 wall becomes q15.
    H14a = sp.Poly(Ha.as_expr().xreplace({w1: w2, w2: w1}),
                   *Ha.gens, domain=sp.QQ)
    H14b = sp.Poly(Hb.as_expr().xreplace({w1: w2, w2: w1}),
                   *Ha.gens, domain=sp.QQ)
    K14 = sp.Poly(K.as_expr().xreplace({w1: w2, w2: w1}),
                  *Ha.gens, domain=sp.QQ)
    q15 = sp.Poly(w5**2-w1**2, *Ha.gens, domain=sp.QQ)
    relabeled_rem = sp.div(H14b-H14a, q15)[1]

    # Compact intrinsic traces on the two components q14=0.  In this
    # environment w3 is the smaller of the two non-primary minus legs.
    a, x, y = w1, w2, w3
    sxy = x+y
    vxy = x*y
    Fplus = (
        4*a**4 + 6*a**3*sxy + 2*a**2*(sxy**2+vxy)
        + (a*sxy+vxy)*(sxy**2-2*vxy)
    )
    Fminus = a*sxy**3 + vxy*(sxy**2-2*vxy)
    trace_plus = sp.Poly(H14a.as_expr().subs(w4, w1),
                         w1, w2, w3, w5, domain=sp.QQ)
    trace_minus = sp.Poly(H14a.as_expr().subs(w4, -w1),
                          w1, w2, w3, w5, domain=sp.QQ)
    trace_plus_residual = sp.expand(trace_plus.as_expr()+32*y**2*Fplus)
    trace_minus_residual = sp.expand(trace_minus.as_expr()+32*y**2*Fminus)

    # A short exact off-wall form for context A (where beta=|y|).
    q14_expr = w4**2-w1**2
    Dblock = 2*a**3+3*a**2*sxy+a*(sxy**2+vxy)-sxy*vxy
    Lblock = (
        3*a**2+2*a*(sxy+w4)-vxy+w4*(2*x+y)
    )
    H14a_compact = (
        -32*y**2*(Fminus+(a+w4)*Dblock)
        -32*q14_expr*y**2*Lblock
        +32*x*w4*q14_expr**2
    )
    H14a_compact_residual = sp.Poly(
        sp.expand(H14a.as_expr()-H14a_compact),
        *Ha.gens, domain=sp.QQ,
    )

    # The second isolated adjacent environment differs only at Q_{1;45}
    # after q24 and energy signs are removed.  The normalized brick is again
    # unchanged, so neither isolated wall supplies the missing nesting.
    sig_diffs_ac = [
        {"wall": key, "a": a, "c": c}
        for key, a, c in zip(
            pa["left"]["signature_keys"],
            pa["left"]["signature"],
            pc["left"]["signature"],
        )
        if a != c and not key.startswith("omega_") and key != "q_2_4"
    ]
    Q145 = sp.Poly(w4**2+w5**2-w1**2, *Ha.gens, domain=sp.QQ)
    Kq, remq = sp.div(Hc-Ha, Q145)

    # A symmetry-related physical q24-wall context is obtained by swapping
    # the two non-primary minus legs 1<->3.  Dual S3 covariance fixes its
    # intrinsic brick without another fit.  Its exact inequality context is
    # different and its polynomial is provably unequal.
    Hsym = sp.Poly(Ha.as_expr().xreplace({w1: w3, w3: w1}),
                   *Ha.gens, domain=sp.QQ)
    symmetry_difference = Hsym-Ha
    symmetry_factor = sp.factor(symmetry_difference.as_expr())
    symmetry_coeff_witness = None
    if not symmetry_difference.is_zero:
        mon, coeff = symmetry_difference.terms()[0]
        symmetry_coeff_witness = {
            "monomial": list(mon),
            "coefficient": str(coeff),
        }
    eps = Fraction(1, 10000)
    base = R2.SixPoint(Fraction(5)-eps, Fraction(2),
                       Fraction(5)+eps, Fraction(3))
    sw = list(base.omega)
    sw[0], sw[2] = sw[2], sw[0]
    swapped = R2.SixPoint(sw[1], sw[2], sw[3], sw[4])
    ps0, ts0 = base.sign_maps()
    ps1, ts1 = swapped.sign_maps()
    d0 = dict(ps0)
    d0.update(ts0)
    d1 = dict(ps1)
    d1.update(ts1)
    symmetry_context_diffs = [
        {"wall": key, "base": d0[key], "swapped": d1[key]}
        for key in sorted(d0)
        if key != "q_2_4" and d0[key] != d1[key]
    ]

    payload = {
        "inputs": [str(path_a), str(path_b), str(path_c)],
        "environment_signature_differences": diffs,
        "H24_identical": Ha == Hb,
        "H24_difference_terms": len(diff.terms()),
        "q25_division": {
            "orientation": "H24_context_b - H24_context_a = q25*K24",
            "remainder_zero": rem.is_zero,
            "K24_degree": K.total_degree(),
            "K24_terms": len(K.terms()),
            "K24": str(K.as_expr()),
            "K24_factor": str(factor),
            "K24_factor_list": [
                [str(base), int(power)] for base, power in factor_list[1]
            ],
        },
        "relabeled_H14_q15_division_remainder_zero": relabeled_rem.is_zero,
        "K14": str(K14.as_expr()),
        "compact_H14_wall_traces": {
            "convention": "a=w1 primary minus, x=w2 larger remaining minus, y=w3 smaller remaining minus",
            "s": "x+y",
            "v": "x*y",
            "same_energy_component": {
                "wall": "w4=w1=a",
                "formula": "H14=-32*y^2*(4*a^4+6*a^3*s+2*a^2*(s^2+v)+(a*s+v)*(s^2-2*v))",
                "exact_residual": str(trace_plus_residual),
            },
            "opposite_energy_component": {
                "wall": "w4=-w1=-a",
                "formula": "H14=-32*y^2*(a*s^3+v*(s^2-2*v))",
                "exact_residual": str(trace_minus_residual),
            },
        },
        "compact_H14_context_a_off_wall": {
            "definitions": {
                "a": "w1",
                "x": "w2",
                "y": "w3 (the beta leg in this cell)",
                "p": "w4",
                "s": "x+y",
                "v": "x*y",
                "q": "p^2-a^2",
                "Fminus": "a*s^3+v*(s^2-2*v)",
                "D": "2*a^3+3*a^2*s+a*(s^2+v)-s*v",
                "L": "3*a^2+2*a*(s+p)-v+p*(2*x+y)",
            },
            "formula": "H14=-32*y^2*(Fminus+(a+p)*D)-32*q*y^2*L+32*x*p*q^2",
            "exact_residual_zero": H14a_compact_residual.is_zero,
        },
        "q1_45_adjacent_environment": {
            "environment_signature_differences": sig_diffs_ac,
            "H24_context_c_equals_context_a": Hc == Ha,
            "division_remainder_zero": remq.is_zero,
            "quotient": str(Kq.as_expr()),
        },
        "symmetry_related_environment": {
            "permutation": "minus legs 1<->3, fixing primary wall q24",
            "base_omega": [fstr(x) for x in base.omega],
            "swapped_omega": [fstr(x) for x in swapped.omega],
            "finer_wall_signature_differences": symmetry_context_diffs,
            "H24_equal": Hsym == Ha,
            "difference_terms": len(symmetry_difference.terms()),
            "difference_factor": str(symmetry_factor),
            "coefficient_witness": symmetry_coeff_witness,
        },
        "codimension_two_witness": {
            "free": ["3", "2", "3", "3"],
            "omega": [str(x) for x in wall_values] + [
                str(sp.Rational(wall.omega[5].numerator,
                                wall.omega[5].denominator))
            ],
            "K24": str(K_wall),
            "nonzero": K_wall != 0,
        },
        "two_sided_wall_limit_witnesses": witnesses,
    }
    out = DATA / "round3_context_comparison.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True))
    report = DATA / "round3_context_comparison_report.md"
    report.write_text("\n".join([
        "# Exact comparison of adjacent q24-wall environments",
        "",
        "- environment differences: `%s`" % diffs,
        "- H24 identical: `%s`" % (Ha == Hb),
        "- exact nested division: `H24_B-H24_A=q25 K24`: `%s`"
          % rem.is_zero,
        "- relabeled identity: `H14_B-H14_A=q15 K14`: `%s`"
          % relabeled_rem.is_zero,
        "- K24: degree `%d`, terms `%d`" % (K.total_degree(), len(K.terms())),
        "- K24 factorization: `%s`" % factor,
        "- compact wall traces: same-energy residual `%s`; opposite-energy "
        "residual `%s`" % (trace_plus_residual, trace_minus_residual),
        "- compact context-A off-wall H14 residual: `%s`"
          % H14a_compact_residual.as_expr(),
        "- adjacent `Q_{1;45}` context: H24 unchanged `%s`; only finer-wall "
        "difference `%s`" % (Hc == Ha, sig_diffs_ac),
        "- symmetry-related physical context: H24 unchanged `%s`; difference "
        "terms `%d`; coefficient witness `%s`"
          % (Hsym == Ha, len(symmetry_difference.terms()),
             symmetry_coeff_witness),
        "- codimension-two value: `K24=%s` (nonzero `%s`)"
          % (K_wall, K_wall != 0),
        "- two-sided algebraic residuals: `%s`"
          % [x["residual"] for x in witnesses],
        "",
        "Full exact witnesses: `%s`." % out,
    ]))
    print(out)
    print(report)


if __name__ == "__main__":
    main()
