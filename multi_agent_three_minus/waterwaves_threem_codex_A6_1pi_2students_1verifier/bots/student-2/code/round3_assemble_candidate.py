#!/usr/bin/env python3
"""Exact integrability test for the naive sum of compact intrinsic bricks."""

import json
from pathlib import Path

import sympy as sp

from round3_bottomup import (
    DATA, R2, homogeneous_basis, parse_fraction, poly_from_coeff, reduce_w5,
)
from round3_compare import load_poly


W = sp.symbols("w1:7")
ZVARS = W[:5]
W6SUB = -sum(ZVARS)


def reduce_on_shell(expr):
    return reduce_w5(sp.expand(expr.subs(W[5], W6SUB)), ZVARS)


def H_minus_beta(a, p, x, y):
    """Intrinsic H piece when beta=|y| is another minus leg."""
    S = x+y
    V = x*y
    q = p*p-a*a
    Fminus = a*S**3+V*(S*S-2*V)
    D = 2*a**3+3*a*a*S+a*(S*S+V)-S*V
    L = 3*a*a+2*a*(S+p)-V+p*(2*x+y)
    return (
        -32*y*y*(Fminus+(a+p)*D)
        -32*q*y*y*L+32*x*p*q*q
    )


def H_plus_beta(a, p, x, y, z):
    """Intrinsic H piece when beta=|z| is another plus leg."""
    S = x+y
    V = x*y
    q = p*p-a*a
    Fminus = a*S**3+V*(S*S-2*V)
    D = 2*a**3+3*a*a*S+a*(S*S+V)-S*V
    K = (
        a**4+4*a**3*p+4*a**3*z+4*a*a*p*p+6*a*a*p*z
        +a*p**3+2*a*p*p*z
        +S*(4*a**3+8*a*a*p+7*a*a*z+5*a*p*p+7*a*p*z
            +p**3+p*p*z)
        +S*S*(3*a*a+4*a*p+3*a*z+p*p+p*z)
        +V*(3*a*a+2*a*p+a*z)+S*V*(3*a+p)
    )
    return -32*z*z*(Fminus+(a+p)*D)+32*q*K


def first_coefficient_witness(poly):
    if poly.is_zero:
        return None
    mon, coeff = poly.terms()[0]
    return {"monomial": list(mon), "coefficient": str(coeff)}


def selected_intrinsic_sum(point):
    total = 0
    selectors = []
    omega = point.omega
    for mi in range(3):
        for pi in range(3, 6):
            qval = omega[pi]**2-omega[mi]**2
            if qval <= 0:
                continue
            other_minus = [j for j in range(3) if j != mi]
            other_plus = [j for j in range(3, 6) if j != pi]
            beta_idx = min(
                other_minus+other_plus, key=lambda j: abs(omega[j])
            )
            a = W[mi]
            p = W[pi]
            if beta_idx in other_minus:
                y = W[beta_idx]
                x = W[[j for j in other_minus if j != beta_idx][0]]
                H = H_minus_beta(a, p, x, y)
                beta_type = "minus"
            else:
                x, y = [W[j] for j in other_minus]
                H = H_plus_beta(a, p, x, y, W[beta_idx])
                beta_type = "plus"
            total += (p*p-a*a)*H
            selectors.append({
                "pair": [mi+1, pi+1],
                "beta_leg": beta_idx+1,
                "beta_type": beta_type,
            })
    return reduce_on_shell(total), selectors


def main():
    basis8 = homogeneous_basis(8)

    # First verify the two compact intrinsic H types against independently
    # reconstructed polynomial pieces.
    _, H14a = load_poly(DATA/"round3_context_a.json", "H14_coefficients")
    _, H14b = load_poly(DATA/"round3_context_b.json", "H14_coefficients")
    _, H14c = load_poly(DATA/"round3_context_c.json", "H14_coefficients")
    _, H14d = load_poly(DATA/"round3_context_d.json", "H14_coefficients")
    HM = reduce_on_shell(H_minus_beta(W[0], W[3], W[1], W[2]))
    HP = reduce_on_shell(H_plus_beta(W[0], W[3], W[1], W[2], W[4]))
    piece_checks = {
        "minus_beta_equals_context_a": (HM-H14a).is_zero,
        "minus_beta_equals_context_b": (HM-H14b).is_zero,
        "minus_beta_equals_context_c": (HM-H14c).is_zero,
        "plus_beta_equals_context_d": (HP-H14d).is_zero,
        "minus_beta_terms": len(HM.terms()),
        "plus_beta_terms": len(HP.terms()),
    }

    cell_records = []
    r0_polys = []
    for tag in "abcd":
        payload = json.loads((DATA/("round3_context_%s.json" % tag)).read_text())
        for side in ("left", "right"):
            coeff = [parse_fraction(x) for x in payload[side]["coefficients"]]
            R = poly_from_coeff(coeff, basis8, ZVARS)
            free = [
                parse_fraction(x)
                for x in payload[side]["samples"][0]["free"]
            ]
            point = R2.SixPoint(*free)
            integrated, selectors = selected_intrinsic_sum(point)
            R0 = R-integrated
            r0_polys.append(R0)
            cell_records.append({
                "context": tag,
                "side": side,
                "sample_omega": [str(x) for x in point.omega],
                "R_terms": len(R.terms()),
                "integrated_terms": len(integrated.terms()),
                "R0_candidate_terms": len(R0.terms()),
                "selectors": selectors,
            })

    base = r0_polys[0]
    comparisons = []
    for record, R0 in zip(cell_records, r0_polys):
        difference = R0-base
        comparisons.append({
            "context": record["context"],
            "side": record["side"],
            "equals_context_a_left": difference.is_zero,
            "difference_terms": len(difference.terms()),
            "coefficient_witness": first_coefficient_witness(difference),
        })

    payload = {
        "candidate": (
            "R0_cell=R_cell-sum_{q_mp>0} q_mp H_mp(beta), using the "
            "compact intrinsic minus-beta/plus-beta pieces"
        ),
        "piece_checks": piece_checks,
        "cells": cell_records,
        "R0_comparisons": comparisons,
        "counts": {
            "intrinsic_piece_exact_checks": sum(
                bool(v) for k, v in piece_checks.items()
                if k.startswith("minus_beta_equals")
                or k.startswith("plus_beta_equals")
            ),
            "intrinsic_piece_check_total": 4,
            "R0_equal_cells": sum(x["equals_context_a_left"]
                                  for x in comparisons),
            "R0_cell_total": len(comparisons),
        },
        "interpretation": (
            "The compact H pieces are exact, but their naive independent "
            "positive-part sum is not integrable to one R0. Coupled beta "
            "selector changes in other pair bricks occur on a primary wall, "
            "so Möbius/inclusion-exclusion assembly is still required."
        ),
    }
    out = DATA/"round3_assemble_candidate.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True))
    report = DATA/"round3_assemble_candidate_report.md"
    report.write_text("\n".join([
        "# Exact assembly test of the compact intrinsic bricks",
        "",
        "- intrinsic compact-piece checks: `%d/%d`"
          % (payload["counts"]["intrinsic_piece_exact_checks"],
             payload["counts"]["intrinsic_piece_check_total"]),
        "- candidate R0 agreement: `%d/%d` cells"
          % (payload["counts"]["R0_equal_cells"],
             payload["counts"]["R0_cell_total"]),
        "- conclusion: the independent positive-part sum fails; coupled "
        "Möbius/inclusion-exclusion assembly remains necessary.",
        "",
        "Full exact coefficient witnesses: `%s`." % out,
    ]))
    print(out)
    print(report)


if __name__ == "__main__":
    main()
