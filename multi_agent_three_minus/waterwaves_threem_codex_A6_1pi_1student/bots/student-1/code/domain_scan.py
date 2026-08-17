import json
import random
from fractions import Fraction
from itertools import permutations
from pathlib import Path

import common
import exact_oracle

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PERMS3 = [tuple(p) for p in permutations(range(3))]


def _sample_pool(rng):
    vals = []
    for n in range(-9, 10):
        if n == 0:
            continue
        vals.append(Fraction(n, 1))
        vals.append(Fraction(n, 2))
        vals.append(Fraction(n, 3))
        vals.append(Fraction(n, 5))
    return list({v for v in vals})


def _candidate_free(rng, pool, scale=1):
    while True:
        vals = [rng.choice(pool) for _ in range(4)]
        if any(v > 0 for v in vals) and any(v < 0 for v in vals):
            vals[0] *= scale
            return vals


def _signature_payload(omega, wall_catalog):
    raw_signs = common.wall_sign_map(omega, wall_catalog)
    if 0 in raw_signs.values():
        return None

    wall_sig_noswap, wall_sig_noswap_ser = common.canonicalize_wall_signatures(
        omega,
        wall_catalog,
        (0, 1, 2),
        (3, 4, 5),
        allow_swap=False,
    )
    wall_sig_swap, wall_sig_swap_ser = common.canonicalize_wall_signatures(
        omega,
        wall_catalog,
        (0, 1, 2),
        (3, 4, 5),
        allow_swap=True,
    )

    qvals = {}
    for item in wall_catalog:
        q = common.wall_value([w * w for w in omega], item)
        qvals[str(item["id"])] = common.frac_to_str(q)

    raw_signature = common.serialize_signs(raw_signs, wall_catalog)

    return {
        "raw_signs": raw_signs,
        "raw_signature": raw_signature,
        "wall_signature": wall_sig_noswap_ser,
        "wall_signature_swap": wall_sig_swap_ser,
        "wall_signs_noswap": wall_sig_noswap,
        "wall_signs_swap": wall_sig_swap,
        "q_values": qvals,
    }


def _add_rep(bucket, sample_id, free_w, omega):
    if len(bucket["representatives"]) >= 3:
        return
    bucket["representatives"].append(
        {
            "sample_id": sample_id,
            "free_w": [common.frac_to_str(x) for x in free_w],
            "omega": [common.frac_to_str(x) for x in omega],
        }
    )


def _make_record(records, sigs, sample_id, base_id, free_w, omega, wall_catalog, seen):
    if any(w == 0 for w in omega):
        return None

    key = tuple(common.frac_to_str(w) for w in omega)
    if key in seen:
        return None

    payload = _signature_payload(omega, wall_catalog)
    if payload is None:
        return None

    try:
        out = exact_oracle.evaluate_omega(omega, sample_id, wall_catalog)
    except Exception:
        return None

    rec = {
        "sample_id": sample_id,
        "base_id": base_id,
        "free_w": [common.frac_to_str(x) for x in free_w],
        "omega": [common.frac_to_str(x) for x in omega],
        "A_re": common.frac_to_str(out.A_re),
        "A_im": common.frac_to_str(out.A_im),
        "min_abs_candidate_pole_numerator": out.min_abs_pole_numerator,
        "wall_signs": payload["raw_signs"],
        "wall_signature_raw": payload["raw_signature"],
        "wall_signature": payload["wall_signature"],
        "wall_signature_swap": payload["wall_signature_swap"],
        "wall_signs_noswap": payload["wall_signs_noswap"],
        "wall_signs_swap": payload["wall_signs_swap"],
        "q_values": payload["q_values"],
    }

    seen.add(key)

    for mode, sig in (("no_swap", rec["wall_signature"]), ("with_swap", rec["wall_signature_swap"])):
        bucket = sigs.setdefault(mode, {}).setdefault(sig, {"count": 0, "representatives": []})
        bucket["count"] += 1
        if "wall_signs" not in bucket:
            bucket["wall_signs"] = payload["wall_signs_noswap"] if mode == "no_swap" else payload["wall_signs_swap"]
        _add_rep(bucket, sample_id, free_w, omega)

    return rec


def _build_selection_rule():
    return (
        "Nondegenerate walls for chamber signatures are the 18 explicit formulas: 9 differences a_i-a_{3+j}=0 and "
        "9 sums a_i + b_j - T = 0 with T=sum_M a = -(sum_P b) under the same index convention. "
        "Six boundary/external degeneracies are listed separately under external_boundaries."
    )


def _make_sampler(base_points, rng):
    for free in base_points:
        yield free

    for t in [Fraction(1, 1), Fraction(1, 2), Fraction(2, 1), Fraction(-1, 1)]:
        yield [Fraction(1, 1) * t, Fraction(-2, 1) * t, Fraction(3, 2) * t, Fraction(-3, 1) * t]

    for _ in range(3000):
        yield _candidate_free(rng, pool=_sample_pool(rng), scale=rng.choice([1, 2, 3, 4, 5]))


def main():
    wall_catalog = common.build_wall_catalog()
    external_boundaries = common.build_external_wall_catalog()
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    (DATA_DIR / "wall_catalog.json").write_text(
        json.dumps(
            {
                "count": len(wall_catalog),
                "nondegenerate_count": len(wall_catalog),
                "external_boundary_count": len(external_boundaries),
                "selection_rule": _build_selection_rule(),
                "walls": wall_catalog,
                "external_boundaries": external_boundaries,
            },
            indent=2,
        )
    )

    sigs = {"no_swap": {}, "with_swap": {}}
    records = []
    seen = set()

    base_points = [
        [Fraction(2, 1), Fraction(-1, 1), Fraction(3, 1), Fraction(1, 1)],
        [Fraction(3, 2), Fraction(-5, 2), Fraction(4, 1), Fraction(-2, 1)],
        [Fraction(-3, 1), Fraction(7, 2), Fraction(2, 1), Fraction(-1, 1)],
        [Fraction(5, 3), Fraction(-4, 3), Fraction(1, 1), Fraction(-2, 3)],
        [Fraction(7, 4), Fraction(-1, 2), Fraction(3, 2), Fraction(-8, 3)],
        [Fraction(11, 5), Fraction(-13, 5), Fraction(7, 3), Fraction(-4, 1)],
        [Fraction(17, 4), Fraction(-9, 2), Fraction(5, 3), Fraction(-1, 1)],
        [Fraction(13, 6), Fraction(-7, 6), Fraction(1, 1), Fraction(-5, 2)],
    ]

    rng = random.Random(20260101)
    sample_idx = 0
    target_records = 80

    for base_id, free in enumerate(_make_sampler(base_points, rng)):
        if len(records) >= 160:
            break
        try:
            omega = list(common.solve_from_free(free, common.SIG_FULL))
        except Exception:
            continue

        # record canonicalized representative by sorted-in-group ordering
        m_order = sorted(range(3), key=lambda i: (omega[i] * omega[i], omega[i]))
        p_order = sorted(range(3), key=lambda i: (omega[3 + i] * omega[3 + i], omega[3 + i]))
        omega_local = [omega[m_order[i]] for i in range(3)] + [omega[3 + p_order[i]] for i in range(3)]

        rec = _make_record(
            records,
            sigs,
            f"base-{base_id}",
            f"base-{base_id}",
            free,
            omega_local,
            wall_catalog,
            seen,
        )
        if rec is not None:
            records.append(rec)
            if base_id < 10:
                for pm in PERMS3:
                    for pp in PERMS3:
                        omega_perm = [
                            omega_local[pm[0]],
                            omega_local[pm[1]],
                            omega_local[pm[2]],
                            omega_local[3 + pp[0]],
                            omega_local[3 + pp[1]],
                            omega_local[3 + pp[2]],
                        ]
                        r2 = _make_record(
                            records,
                            sigs,
                            f"perm-b{base_id}-{pm}-{pp}",
                            f"base-{base_id}",
                            free,
                            omega_perm,
                            wall_catalog,
                            seen,
                        )
                        if r2 is not None:
                            records.append(r2)

    while len(records) < target_records:
        free = _candidate_free(rng, _sample_pool(rng), scale=rng.choice([1, 2, 3, 4, 5]))
        try:
            omega = list(common.solve_from_free(free, common.SIG_FULL))
        except Exception:
            sample_idx += 1
            if sample_idx > 5000:
                break
            continue

        rec = _make_record(
            records,
            sigs,
            f"rand-{sample_idx}",
            f"rand-{sample_idx}",
            free,
            omega,
            wall_catalog,
            seen,
        )
        sample_idx += 1
        if rec is not None:
            records.append(rec)
        if sample_idx > 6000:
            break

    # deterministic affine family extras
    for a in [Fraction(1, 1), Fraction(2, 1), Fraction(3, 1)]:
        for b in [Fraction(-1, 1), Fraction(-2, 1), Fraction(-3, 1)]:
            for t in [Fraction(1, 8), Fraction(1, 4), Fraction(1, 2), Fraction(1, 1), Fraction(3, 2)]:
                free = [a + t, b - t, Fraction(1, 3), Fraction(-1, 2) * t]
                try:
                    omega = list(common.solve_from_free(free, common.SIG_FULL))
                except Exception:
                    continue
                rec = _make_record(
                    records,
                    sigs,
                    f"aff-{a}-{b}-{t}",
                    f"aff-{a}-{b}-{t}",
                    free,
                    omega,
                    wall_catalog,
                    seen,
                )
                if rec is not None:
                    records.append(rec)

    with (DATA_DIR / "oracle_samples.jsonl").open("w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")

    sigs_no = [
        {
            "signature": k,
            "count": v["count"],
            "representatives": v["representatives"],
        }
        for k, v in sorted(sigs["no_swap"].items(), key=lambda kv: kv[0])
    ]
    sigs_swap = [
        {
            "signature": k,
            "count": v["count"],
            "representatives": v["representatives"],
        }
        for k, v in sorted(sigs["with_swap"].items(), key=lambda kv: kv[0])
    ]

    (DATA_DIR / "domain_signatures.json").write_text(
        json.dumps(
            {
                "selection_rule": _build_selection_rule(),
                "signature_count_no_swap": len(sigs_no),
                "signature_count_with_swap": len(sigs_swap),
                "signatures_no_swap": sigs_no,
                "signatures_with_swap": sigs_swap,
                "total_samples": len(records),
            },
            indent=2,
        )
    )

    chamber_words = []
    for entry in sigs_no:
        sig = entry["signature"]
        first = sigs["no_swap"][sig]["representatives"][0]
        chamber_words.append(
            {
                "signature": sig,
                "count": entry["count"],
                "wall_signs": sigs["no_swap"][sig].get("wall_signs", {}),
                "exact_representative": first,
            }
        )

    (DATA_DIR / "chamber_words.json").write_text(
        json.dumps(
            {
                "selection_rule": _build_selection_rule(),
                "count": len(chamber_words),
                "words": chamber_words,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
