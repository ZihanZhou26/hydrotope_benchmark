
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product, combinations
from pathlib import Path
import json
from typing import Dict, List, Tuple

from kinematics import KinematicsPoint, all_20_words_3plus3, expected_pairwall_words, fraction_to_str


def grid_values(bound: int, include_halves: bool = False) -> List[Fraction]:
    vals = [Fraction(i, 1) for i in range(1, bound + 1)]
    if include_halves:
        vals.extend([Fraction(1, 2), Fraction(3, 2), Fraction(5, 2), Fraction(2, 3), Fraction(3, 4)])
    return vals


def build_records(values: List[Fraction], max_reps: int = 3) -> Dict:
    word_points: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    word_counts = Counter()
    pair_pattern_counts: Dict[str, Counter] = defaultdict(Counter)
    triple_pattern_counts: Dict[str, Counter] = defaultdict(Counter)
    pair_triple_checks = {
        "a>d": 0,
        "a<=d": 0,
        "f>b": 0,
        "f<=b": 0,
    }
    all_points = []
    generic_points = 0

    for b, c, d, e in product(values, repeat=4):
        kp = KinematicsPoint(b, c, d, e)
        checks = kp.conservation_checks()
        pair_signs, pair_keys = kp.pair_sign_pattern()
        triple_signs, triple_keys = kp.triple_sign_pattern()

        point_record = kp.as_json_record()
        all_points.append(point_record)

        if kp.is_generic():
            generic_points += 1
        if checks["sum_omega_ok"] and checks["sum_momentum_ok"]:
            word, strict, _ = kp.sorted_magnitude_word()
            if strict and all(v != 0 for v in pair_signs) and all(v != 0 for v in triple_signs):
                word_counts[word] += 1
                key_pair = "|".join(pair_signs)
                key_triple = "|".join(triple_signs)
                pair_pattern_counts[word][key_pair] += 1
                triple_pattern_counts[word][key_triple] += 1
                if len(word_points[word]) < max_reps:
                    word_points[word].append(point_record)
                point_record["pair_key"] = key_pair
                point_record["triple_key"] = key_triple
                point_record["is_generic"] = True
            else:
                point_record["is_generic"] = False
        else:
            point_record["is_generic"] = False

        if kp.a > kp.d:
            pair_triple_checks["a>d"] += 1
            point_record["a_gt_d"] = True
        else:
            pair_triple_checks["a<=d"] += 1
            point_record["a_gt_d"] = False
        if kp.f > kp.b:
            pair_triple_checks["f>b"] += 1
            point_record["f_gt_b"] = True
        else:
            pair_triple_checks["f<=b"] += 1
            point_record["f_gt_b"] = False

    pair_patterns = {}
    for word, ctr in pair_pattern_counts.items():
        pair_patterns[word] = dict(ctr)
    triple_patterns = {}
    for word, ctr in triple_pattern_counts.items():
        triple_patterns[word] = dict(ctr)

    return {
        "values": [fraction_to_str(v) for v in values],
        "generic_points": generic_points,
        "total_points": len(all_points),
        "pair_triple_checks": pair_triple_checks,
        "word_counts": {k: len(v) for k, v in word_points.items()},
        "word_examples": word_points,
        "pair_patterns": pair_patterns,
        "triple_patterns": triple_patterns,
    }


def scan_paths_for_adjacency() -> List[Dict[str, object]]:
    candidates: List[Dict[str, object]] = []

    # deterministic one-parameter affine families with fixed offsets
    families = [
        ("vary_b", lambda t: (Fraction(3, 2) + t, Fraction(2, 1), Fraction(5, 2), Fraction(2, 1))),
        ("vary_c", lambda t: (Fraction(2, 1), Fraction(3, 2) + t, Fraction(2, 1), Fraction(3, 1))),
        ("vary_d", lambda t: (Fraction(2, 1), Fraction(3, 1), Fraction(3, 2) + t, Fraction(2, 1))),
        ("vary_e", lambda t: (Fraction(3, 1), Fraction(2, 1), Fraction(2, 1), Fraction(3, 2) + t)),
    ]

    ts = [Fraction(-2, 1), Fraction(-1, 1), Fraction(-Fraction(1, 2)), Fraction(-Fraction(1, 4)), Fraction(Fraction(1, 4)), Fraction(Fraction(1, 2)), Fraction(1, 1), Fraction(2, 1)]

    for name, fn in families:
        samples = []
        for t in ts:
            b, c, d, e = fn(t)
            if b <= 0 or c <= 0 or d <= 0 or e <= 0:
                continue
            kp = KinematicsPoint(b, c, d, e)
            word, strict, order = kp.sorted_magnitude_word()
            pair_signs, _ = kp.pair_sign_pattern()
            triple_signs, _ = kp.triple_sign_pattern()
            if not kp.is_generic():
                continue
            samples.append((t, kp, word, pair_signs, triple_signs))

        if len(samples) < 2:
            continue
        samples.sort(key=lambda x: x[0])
        for left, right in zip(samples, samples[1:]):
            t0, kp0, w0, p0, tr0 = left
            t1, kp1, w1, p1, tr1 = right
            if w0 == w1:
                continue
            pair_delta = tuple(i for i in range(len(p0)) if p0[i] != p1[i])
            triple_delta = tuple(i for i in range(len(tr0)) if tr0[i] != tr1[i])
            candidates.append(
                {
                    "path": name,
                    "from_t": str(t0),
                    "to_t": str(t1),
                    "from_word": w0,
                    "to_word": w1,
                    "pair_delta_indices": list(pair_delta),
                    "triple_delta_indices": list(triple_delta),
                    "from": {
                        "b": fraction_to_str(kp0.b),
                        "c": fraction_to_str(kp0.c),
                        "d": fraction_to_str(kp0.d),
                        "e": fraction_to_str(kp0.e),
                    },
                    "to": {
                        "b": fraction_to_str(kp1.b),
                        "c": fraction_to_str(kp1.c),
                        "d": fraction_to_str(kp1.d),
                        "e": fraction_to_str(kp1.e),
                    },
                }
            )

    return candidates


def stabilization_report() -> Dict[str, object]:
    observed = []
    new_words = []
    for bound in [3, 4, 5, 6]:
        vals = grid_values(bound, include_halves=False)
        rec = build_records(vals, max_reps=0)
        words = sorted(rec["word_counts"].keys())
        observed.append(words)
        if len(observed) > 1 and set(words) == set(observed[-2]):
            pass
        if len(observed) > 2 and set(observed[-1]) == set(observed[-2]) == set(observed[-3]):
            return {"stable": True, "at_bound": bound, "observed_words": words, "history": observed}
    words_last = observed[-1] if observed else []
    return {"stable": False, "at_bound": 6, "observed_words": words_last, "history": observed}


def main():
    base_dir = Path(".").resolve()
    out_path = base_dir / "bots/student-2/data/chamber_scan.json"

    # primary high-resolution scan for representative points and pair/triple pattern tables
    scan_vals = grid_values(5, include_halves=True)
    scan = build_records(scan_vals, max_reps=3)

    # confirm if observed words stabilize with bound growth
    stab = stabilization_report()

    observed_words = sorted(scan["word_counts"].keys())
    all_words = all_20_words_3plus3()
    expected_words = expected_pairwall_words()
    extras = [w for w in observed_words if w not in expected_words]
    missing_expected = [w for w in expected_words if w not in observed_words]
    excluded = [w for w in all_words if w not in observed_words]

    adjacency = scan_paths_for_adjacency()

    # compress pair/triple pattern structures to include sign pattern IDs per word
    pair_patterns = {}
    for word, patterns in scan["pair_patterns"].items():
        ranked = sorted(patterns.items(), key=lambda kv: kv[1], reverse=True)
        pair_patterns[word] = {"top_patterns": ranked[:5], "all_count": len(patterns)}

    triple_patterns = {}
    for word, patterns in scan["triple_patterns"].items():
        ranked = sorted(patterns.items(), key=lambda kv: kv[1], reverse=True)
        triple_patterns[word] = {"top_patterns": ranked[:5], "all_count": len(patterns)}

    # keep only a compact list of representative tuples and required aggregate checks
    payload = {
        "scan_grid_values": scan["values"],
        "total_points": scan["total_points"],
        "generic_points": scan["generic_points"],
        "observed_words": observed_words,
        "observed_word_count": len(observed_words),
        "expected_reference_words": expected_words,
        "expected_count": len(expected_words),
        "extras_against_expected": extras,
        "missing_expected": missing_expected,
        "stabilization": stab,
        "all_20_words": all_words,
        "excluded_words_20": excluded,
        "word_examples": scan["word_examples"],
        "pair_triple_checks": scan["pair_triple_checks"],
        "pair_sign_patterns": pair_patterns,
        "triple_sign_patterns": triple_patterns,
        "pair_counts_by_word": scan["word_counts"],
        "adjacency_candidates": adjacency,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(out_path)


if __name__ == "__main__":
    main()
