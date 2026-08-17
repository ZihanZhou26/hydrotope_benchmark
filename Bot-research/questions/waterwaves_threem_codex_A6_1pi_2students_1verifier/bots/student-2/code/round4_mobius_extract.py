#!/usr/bin/env python3
"""Möbius-style extraction for full-sorted six-point remainder cells."""

import json
from fractions import Fraction
from pathlib import Path

import sympy as sp

from round3_bottomup import DATA, reduce_w5, poly_from_coeff
from round3_assemble_candidate import H_minus_beta, H_plus_beta

W_ALL = sp.symbols("w1:7")
W5 = sp.symbols("w1:6")
W6 = W_ALL


def parse_fraction(x):
    return Fraction(str(x))


def reduce_expr(expr):
    expr = sp.expand(expr)
    expr = expr.subs({W6[5]: -sum(W6[:5])})
    return reduce_w5(expr, W5).as_expr()


def to_poly(expr):
    if isinstance(expr, sp.Poly):
        expr = expr.as_expr()
    return sp.Poly(reduce_expr(expr), *W5, domain=sp.QQ)


def layout(word):
    out = {}
    minus = []
    plus = []
    for i, ch in enumerate(word):
        if ch == "-":
            minus.append(i)
        else:
            plus.append(i)
    for j, pos in enumerate(minus):
        out[pos] = j + 1
    for j, pos in enumerate(plus):
        out[pos] = 4 + j
    return out, minus, plus


def swapped_pair(word, pos):
    layout_map, _, _ = layout(word)
    a = layout_map[pos]
    b = layout_map[pos + 1]
    if a <= 3 and b >= 4:
        return a, b
    if b <= 3 and a >= 4:
        return b, a
    raise ValueError("not a minus-plus swap: %s %d" % (word, pos))


def canonical_omega_from_cell(cell):
    samples = cell.get("samples", [])
    holdouts = cell.get("holdouts", [])
    if samples:
        rec = samples[0]
    else:
        rec = holdouts[0]
    return [parse_fraction(x) for x in rec["canonical_omega"]]


def load_cells(path):
    payload = json.loads(Path(path).read_text())
    cells = payload["cells"] if isinstance(payload["cells"], dict) else {x["word"]: x for x in payload["cells"]}
    return payload, cells


def build_cell_polys(cells):
    out = {}
    basis = None
    for word, rec in cells.items():
        if basis is None:
            basis = [tuple(x) for x in rec["coefficients_basis"]]
        coeff = [parse_fraction(x) for x in rec["coefficients"]]
        out[word] = poly_from_coeff(coeff, basis, W5)
    return out, basis


def q_expr(minus_label, plus_label):
    idx_m = minus_label - 1
    idx_p = plus_label - 1
    wm = W6[idx_m]
    wp = W6[idx_p]
    expr = wp ** 2 - wm ** 2
    return reduce_expr(expr)


def q_val(point_vals, minus_label, plus_label):
    return point_vals[plus_label - 1] ** 2 - point_vals[minus_label - 1] ** 2


def pair_list():
    minus = [1, 2, 3]
    plus = [4, 5, 6]
    return [(m, p) for m in minus for p in plus]


def wall_beta_label(sample_vals, minus_label, plus_label):
    candidates = [i for i in (1, 2, 3, 4, 5, 6) if i not in (minus_label, plus_label)]
    best = min(candidates, key=lambda j: (abs(sample_vals[j - 1]), -j))
    btype = "minus" if best <= 3 else "plus"
    return best, btype


def compact_candidate_for_edge(sample_vals, minus_label, plus_label):
    beta, btype = wall_beta_label(sample_vals, minus_label, plus_label)
    others_minus = [i for i in (1, 2, 3) if i not in (minus_label,)]
    a = W6[minus_label - 1]
    p = W6[plus_label - 1]
    if btype == "minus":
        x, y = others_minus
        if y != beta:
            x, y = y, x
        formula = H_minus_beta(a, p, W6[x - 1], W6[y - 1])
    else:
        x, y = others_minus
        formula = H_plus_beta(a, p, W6[x - 1], W6[y - 1], W6[beta - 1])
    return reduce_expr(formula), beta, btype


def edge_records(cells):
    words = list(cells.keys())
    wordset = set(words)
    edges = []
    seen = set()
    for w in words:
        for pos in range(5):
            ch1, ch2 = w[pos], w[pos + 1]
            if ch1 == ch2:
                continue
            sw = w[:pos] + ch2 + ch1 + w[pos + 2 :]
            if sw not in wordset:
                continue
            m, p = swapped_pair(w, pos)
            key = tuple(sorted([w, sw])) + (pos, m, p)
            if key in seen:
                continue
            seen.add(key)
            edges.append((w, sw, pos, m, p))
    return edges


def factor_summary(expr):
    poly = to_poly(expr)
    term_count = len(poly.terms())
    factor = str(sp.factor(poly.as_expr()))
    factor_list = [[str(b), int(e)] for b, e in sp.factor_list(poly.as_expr())[1]]

    candidate_exprs = {}
    names = []
    for i in range(1, 7):
        for j in range(i + 1, 7):
            names.append(("w%d-w%d" % (i, j), W6[i - 1] - W6[j - 1]))
            names.append(("w%d+w%d" % (i, j), W6[i - 1] + W6[j - 1]))

    C = reduce_expr(W6[0] * W6[1] * W6[2] + W6[3] * W6[4] * W6[5])
    names.append(("C", C))

    linear = {}
    for name, cand in names:
        cand = reduce_expr(cand)
        cp = sp.Poly(cand, *W5, domain=sp.QQ)
        quo, rem = sp.div(poly, cp)
        linear[name] = {
            "divides": (len(rem.terms()) == 0),
            "quotient_terms": (len(quo.terms()) if rem == 0 else None),
        }

    return {
        "term_count": term_count,
        "factor": factor,
        "factor_list": factor_list,
        "linear_factor_tests": linear,
    }


def sym_permute_average(expr):
    minus_perms = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
    plus_perms = [(3, 4, 5), (3, 5, 4), (4, 3, 5), (4, 5, 3), (5, 3, 4), (5, 4, 3)]
    total = 0
    for pmin in minus_perms:
        for ppl in plus_perms:
            mapping = {
                W6[0]: W6[pmin[0]],
                W6[1]: W6[pmin[1]],
                W6[2]: W6[pmin[2]],
                W6[3]: W6[ppl[0]],
                W6[4]: W6[ppl[1]],
                W6[5]: W6[ppl[2]],
            }
            total += expr.xreplace(mapping)
    return sp.expand(total / 36)


def invariant_basis_degree8():
    w1, w2, w3, w4, w5, w6 = W6
    e2m = w1 * w2 + w1 * w3 + w2 * w3
    e2p = w4 * w5 + w4 * w6 + w5 * w6
    e3m = w1 * w2 * w3
    e3p = w4 * w5 * w6
    e1m = w1 + w2 + w3
    basis = []
    for a in range(0, 6):
        for b in range(0, 4):
            for c in range(0, 5):
                for d in range(0, 4):
                    for e in range(0, 9):
                        if 2 * a + 3 * b + 2 * c + 3 * d + e == 8:
                            expr = (e2m ** a) * (e3m ** b) * (e2p ** c) * (e3p ** d) * (e1m ** e)
                            expr = reduce_expr(expr.subs({e2p: e2m}))
                            basis.append(sp.expand(expr))
    # Deduplicate symbolic duplicates from substitutions.
    uniq = []
    seen = set()
    for b in basis:
        k = sp.expand(b)
        ks = str(k)
        if ks in seen:
            continue
        seen.add(ks)
        uniq.append(k)
    return uniq


def solve_invariant_fit(poly_expr, samples):
    basis = invariant_basis_degree8()
    if not samples:
        return {
            "success": False,
            "residual_terms": None,
            "coefficients": [],
            "message": "no sample points",
        }

    rows = []
    vals = []
    seen = set()

    def independent_add(row, rhs):
        cand = rows + [row]
        candm = sp.Matrix(cand)
        rhsm = sp.Matrix(vals + [rhs])
        if candm.rank() > sp.Matrix(rows).rank() if rows else 1:
            rows.append(row)
            vals.append(rhs)
            return True
        return False

    for sample in samples:
        ws = [parse_fraction(x) for x in sample["canonical_omega"]]
        mapping = {W6[i]: ws[i] for i in range(6)}
        target = sp.Rational(poly_expr.subs(mapping))
        row = [sp.Rational(expr.subs(mapping)) for expr in basis]
        if independent_add(row, target):
            if len(rows) == len(basis):
                break

    if len(rows) < len(basis):
        return {
            "success": False,
            "residual_terms": None,
            "coefficients": [],
            "message": "insufficient independent rows: %d/%d" % (len(rows), len(basis)),
        }

    M = sp.Matrix(rows)
    y = sp.Matrix(vals)
    try:
        solved = M.LUsolve(y)
    except Exception as exc:
        return {"success": False, "residual_terms": None, "coefficients": [], "message": str(exc)}

    pred = sum(c * b for c, b in zip(solved, basis))
    pred = sp.expand(pred)
    residual = sp.expand(poly_expr - pred)
    return {
        "success": residual == 0,
        "residual_terms": len(to_poly(residual).terms()) if residual != 0 else 0,
        "coefficients": {str(i): str(solved[i]) for i in range(len(solved))},
        "basis": [str(x) for x in basis],
        "residual": str(residual),
    }


def compare_edge_formulas(edge, polys):
    w1 = edge["from"]
    w2 = edge["to"]
    pA = polys[w1].as_expr()
    pB = polys[w2].as_expr()

    m, p = edge["minus_label"], edge["plus_label"]
    qa = q_expr(m, p)
    qpoly = to_poly(qa)

    if edge["from_orientation"][0] == w1:
        delta = pB - pA
    else:
        delta = pA - pB
    dpoly = to_poly(delta)
    kpoly, rem = sp.div(dpoly, qpoly)
    rem_zero = len(rem.terms()) == 0

    sample = edge["sample"]
    sample_vals = [parse_fraction(x) for x in sample["canonical_omega"]]
    compact, compact_beta, compact_type = compact_candidate_for_edge(sample_vals, m, p)

    return {
        "m": m,
        "p": p,
        "from": w1,
        "to": w2,
        "orientation": "from=%s to=%s" % (edge["from_orientation"][0], edge["from_orientation"][1]),
        "q_expr": str(qa),
        "q_sign_sample": "+" if q_val(sample_vals, m, p) > 0 else "-",
        "q_division_remainder_zero": rem_zero,
        "q_division_remainder": str(rem),
        "edge_quotient_term_count": len(kpoly.terms()),
        "edge_quotient_factor": str(sp.factor(kpoly.as_expr())),
        "compact_beta_label": compact_beta,
        "compact_beta_type": compact_type,
        "compact_formula_residual": str(sp.expand(kpoly.as_expr() - compact)),
        "compact_formula_zero": (sp.expand(kpoly.as_expr() - compact) == 0),
        "compact_formula_terms": len(to_poly(kpoly.as_expr() - compact).terms()),
        "factors": factor_summary(kpoly),
    }, kpoly, qa


def spanning_trees(polys, edge_items):
    by_word = {w: [] for w in polys}
    for rec in edge_items:
        by_word[rec["from"]].append(rec)
        by_word[rec["to"]].append(rec)

    all_words = sorted(polys)
    root_results = []

    for root in all_words:
        parent = {root: None}
        tree_inc = {}
        order = [root]
        qidx = 0
        while qidx < len(order):
            u = order[qidx]
            qidx += 1
            for rec in sorted(by_word[u], key=lambda x: x["to"] + x["from"]):
                v = rec["to"] if rec["from"] == u else rec["from"]
                if v in parent:
                    continue
                parent[v] = u
                tree_inc[(u, v)] = rec
                order.append(v)

        # tree must touch all nodes in this connected graph.
        if len(parent) != len(all_words):
            continue

        predicted = {root: polys[root].as_expr()}
        # Build predicted values by traversing parent links.
        for node in order[1:]:
            p = parent[node]
            rec = tree_inc[(p, node)] if (p, node) in tree_inc else tree_inc[(node, p)]
            qk = rec["quotient_expr"] * (to_poly(q_expr(rec["minus_label"], rec["plus_label"])).as_expr())
            if rec["from_orientation"] == (p, node):
                predicted[node] = sp.expand(predicted[p] + qk)
            else:
                predicted[node] = sp.expand(predicted[p] - qk)

        miss = []
        for w, pred in predicted.items():
            mismatch = sp.expand(pred - polys[w].as_expr())
            miss.append({"word": w, "residual": str(mismatch), "zero": mismatch == 0})

        cycle_checks = []
        tree_edge_set = {tuple(sorted((a, b)) for a, b in tree_inc)}
        for rec in edge_items:
            e = tuple(sorted((rec["from"], rec["to"])))
            if e in tree_edge_set:
                continue
            qk = rec["quotient_expr"] * q_expr(rec["minus_label"], rec["plus_label"])
            if rec["from_orientation"] == (rec["from"], rec["to"]):
                rel = sp.expand(polys[rec["to"]].as_expr() - polys[rec["from"]].as_expr() - qk.as_expr())
            else:
                rel = sp.expand(polys[rec["from"]].as_expr() - polys[rec["to"]].as_expr() - qk.as_expr())
            cycle_checks.append({
                "edge": [rec["from"], rec["to"]],
                "residual": str(rel),
                "zero": rel == 0,
            })

        total_qk_terms = sum(
            x["edge_quotient_term_count"]
            for x in edge_items
            if tuple(sorted((x["from"], x["to"]))) in tree_edge_set
        )
        root_results.append({
            "root": root,
            "reconstruct_ok": all(x["zero"] for x in miss),
            "node_checks": miss,
            "cycle_checks": cycle_checks,
            "tree_edge_count": len(tree_inc),
            "tree_term_sum": int(total_qk_terms),
        })

    good = sorted(root_results, key=lambda r: (len([x for x in r["node_checks"] if not x["zero"]]), r["tree_term_sum"]))
    return good[0] if good else {"error": "no valid root"}


def second_order_terms(polys, cells):
    pairs = pair_list()
    results = {}
    common_residuals = {}

    for word, rec in cells.items():
        sample_vals = canonical_omega_from_cell(rec)
        poly = polys[word].as_expr()

        # Precompute K_{a|b} for all ordered disjoint pairs.
        Kmap = {}
        for a_minus, a_plus in pairs:
            others = [i for i in (1, 2, 3) if i != a_minus]
            x, y = others
            for b_minus, b_plus in pairs:
                if b_minus == a_minus or b_plus == a_plus:
                    continue
                Hm = H_minus_beta(W6[a_minus - 1], W6[a_plus - 1], W6[x - 1], W6[b_minus - 1])
                Hp = H_plus_beta(W6[a_minus - 1], W6[a_plus - 1], W6[x - 1], W6[b_minus - 1], W6[b_plus - 1])
                diff = reduce_expr(Hm - Hp)
                qden = to_poly(q_expr(b_minus, b_plus))
                k, rem = sp.div(to_poly(diff), qden)
                Kmap[(a_minus, a_plus, b_minus, b_plus)] = {
                    "K": k,
                    "remainder": rem,
                    "remainder_zero": len(rem.terms()) == 0,
                    "term_count": len(k.terms())
                }

        S1 = 0
        S2 = 0
        for a_minus, a_plus in pairs:
            qa = q_expr(a_minus, a_plus)
            qa_s = q_val(sample_vals, a_minus, a_plus)
            if not qa_s > 0:
                continue
            nonprimary = [i for i in (1, 2, 3, 4, 5, 6) if i not in (a_minus, a_plus)]
            beta = min(nonprimary, key=lambda j: (abs(sample_vals[j - 1]), -j))
            other_minus = [j for j in (1, 2, 3) if j != a_minus]
            x, y = other_minus
            if beta <= 3:
                if y != beta:
                    x, y = y, x
                H = H_minus_beta(W6[a_minus - 1], W6[a_plus - 1], W6[x - 1], W6[y - 1])
            else:
                H = H_plus_beta(W6[a_minus - 1], W6[a_plus - 1], W6[x - 1], W6[y - 1], W6[beta - 1])
            S1 += to_poly(qa).as_expr() * to_poly(reduce_expr(H)).as_expr()

            for b_minus, b_plus in pairs:
                if b_minus == a_minus or b_plus == a_plus:
                    continue
                if beta != b_minus:
                    continue
                qb = q_val(sample_vals, b_minus, b_plus)
                if not qb > 0:
                    continue
                data = Kmap[(a_minus, a_plus, b_minus, b_plus)]
                k = data["K"]
                S2 -= to_poly(qa).as_expr() * to_poly(q_expr(b_minus, b_plus)).as_expr() * k.as_expr()

        residual = sp.expand(poly - (S1 + S2))
        residual = reduce_expr(residual)
        results[word] = {
            "S1_terms": len(to_poly(S1).terms()) if S1 else 0,
            "S2_terms": len(to_poly(S2).terms()) if S2 else 0,
            "residual_terms": len(to_poly(residual).terms()),
            "residual": str(residual),
            "zero": residual == 0,
            "K_terms": {
                "%s|%s" % (a, b): data["term_count"] for (a, b, _, _), data in Kmap.items()
            },
        }
        common_residuals.setdefault(str(to_poly(residual)), []).append(word)

    return {
        "per_cell": results,
        "residual_signature": {
            expr: words for expr, words in common_residuals.items()
        },
        "common_residual": len(common_residuals) == 1,
    }


def corrected_wall_trace_copy():
    src = DATA / "round3_wall_trace_scan.json"
    dst = DATA / "round3_wall_trace_scan_corrected.json"
    if not src.exists():
        return None
    payload = json.loads(src.read_text())
    for rec in payload.get("results", []):
        if "H_wall_compact_formula" in rec:
            rec["deprecated_H_wall_compact_formula_stale"] = rec.pop("H_wall_compact_formula")
    if "deprecation_note" not in payload:
        payload["deprecation_note"] = "For wall entries, H_wall_beta_formula is authoritative."
    dst.write_text(json.dumps(payload, indent=2, sort_keys=True))
    return str(dst)


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    full_path = DATA / "round4_full_sort.json"
    _, cells = load_cells(full_path)

    polys, basis = build_cell_polys(cells)

    edges_raw = edge_records(cells)
    edges = []
    for w1, w2, pos, m, p in sorted(edges_raw):
        rec = {
            "from": w1,
            "to": w2,
            "minus_label": m,
            "plus_label": p,
            "swap_pos": pos,
        }
        sample1 = canonical_omega_from_cell(cells[w1])
        sample2 = canonical_omega_from_cell(cells[w2])
        q1 = q_val(sample1, m, p)
        q2 = q_val(sample2, m, p)
        if q1 < 0 < q2:
            neg, posw = w1, w2
        elif q2 < 0 < q1:
            neg, posw = w2, w1
        else:
            # skip degenerate orientation (should not happen)
            continue
        rec["from_orientation"] = (neg, posw)
        rec["sample"] = {"canonical_omega": [str(x) for x in canonical_omega_from_cell(cells[neg])]}
        rec["comparison"], quotient_expr, qpoly = compare_edge_formulas(rec, polys)
        rec["quotient_expr"] = quotient_expr
        rec["q_expr"] = sp.expand(qpoly.as_expr())
        edges.append(rec)

    # Branch diagnostics
    branch_records = {}
    for w, poly in polys.items():
        sample = canonical_omega_from_cell(cells[w])
        branch_records[w] = {
            "word": w,
            "terms": len(poly.terms()),
            "factor": factor_summary(poly.as_expr()),
            "average_over_S3xS3": str(sym_permute_average(poly.as_expr())),
            "symmetrized": str(sym_permute_average(poly.as_expr())),
            "symmetry_residual": str(reduce_expr(poly.as_expr() - sym_permute_average(poly.as_expr()))),
            "invariant_fit": solve_invariant_fit(poly.as_expr(), cells[w].get("samples", []) + cells[w].get("holdouts", [])),
        }

    tree_info = spanning_trees(polys, edges)
    second = second_order_terms(polys, cells)
    corrected = corrected_wall_trace_copy()

    out = {
        "basis_size": len(basis),
        "adjacent_edges": {
            "count": len(edges),
            "records": [
                {
                    "from": e["from"],
                    "to": e["to"],
                    "m": e["minus_label"],
                    "p": e["plus_label"],
                    "swap_pos": e["swap_pos"],
                    "from_orientation": e["from_orientation"],
                    "q_expr": e["q_expr"],
                    **e["comparison"],
                }
                for e in edges
            ],
        },
        "branch_reports": branch_records,
        "spanning_tree": tree_info,
        "second_order": second,
        "wall_trace_scan_corrected": corrected,
        "counts": {
            "branch_zero_factors": sum(1 for x in branch_records.values() if x["invariant_fit"].get("success")),
            "edge_zero_compact": sum(1 for e in edges if e["comparison"]["compact_formula_zero"]),
            "edge_zero_div": sum(1 for e in edges if e["comparison"]["q_division_remainder_zero"]),
        },
    }

    out_path = DATA / "round4_mobius_extract.json"
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True))
    print(out_path)


if __name__ == "__main__":
    main()
