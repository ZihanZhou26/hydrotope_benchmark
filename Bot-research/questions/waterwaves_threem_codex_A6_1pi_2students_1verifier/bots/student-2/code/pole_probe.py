import json
from fractions import Fraction
from itertools import combinations
from math import gcd
from pathlib import Path

from kinematics import KinematicsPoint, BGOracle, fraction_to_str


def point_triple_numerators(omega):
    data = {}
    for r in range(1, 1 << len(omega)):
        if r.bit_count() != 3:
            continue
        idxs = [i for i in range(len(omega)) if r & (1 << i)]
        wsum = sum(omega[i] for i in idxs)
        qsum = sum(((-1 if i < 3 else 1) * omega[i] * omega[i]) for i in idxs)
        dT = wsum * wsum - abs(qsum)
        key = "".join("1" if i in idxs else "0" for i in range(len(omega)))
        data[key] = {
            "indices": idxs,
            "dT": fraction_to_str(dT),
            "den": dT.denominator,
            "num": dT.numerator,
        }
    return data


def scaled_sequences(data, max_p=10):
    out = {}
    for p in range(max_p + 1):
        seq = []
        valid = True
        for t, amp in data:
            if t == 0:
                continue
            val = amp * (Fraction(1, 1) / (t ** p))
            seq.append(fraction_to_str(val))
        out[str(p)] = seq
    return out


def valuation_heuristic(seqs):
    # raw heuristic: choose first p where scaled magnitudes appear bounded and non-trivial
    score = {}
    for k, seq in seqs.items():
        if not seq:
            score[k] = {"count": 0}
            continue
        vals = [abs(Fraction(s)) for s in seq]
        if not vals:
            score[k] = {"count": 0}
            continue
        base = vals[0]
        growth = max(v.denominator * base.numerator + base.denominator * v.numerator for v in vals)
        score[k] = {"count": len(vals), "base": str(base)}
    return score


def main():
    qdir = Path(".").resolve()
    oracle = BGOracle(qdir / "bots/student-2/bg")
    out = qdir / "bots/student-2/data/pole_probe.json"

    # pair-cancellation point from user sample tuple (-2,-3,-5,2,3,5)
    # achieved by free freqs (-3,-5,2,3) with the fixed sigma tuple.
    base = {
        "label": "w2=-3,w3=-5,w4=2,w5=3",
        "b0": Fraction(-3),
        "c0": Fraction(-5),
        "d0": Fraction(2),
        "e0": Fraction(3),
    }

    def params_at_t(t):
        # one-parameter approach through the pair-cancellation point.
        return (base["b0"] + t, base["c0"], base["d0"], base["e0"] - t)

    t_values = [Fraction(-1, 5), Fraction(-1, 6), Fraction(-1, 7), Fraction(-1, 8), Fraction(-1, 12),
                Fraction(1, 12), Fraction(1, 8), Fraction(1, 7), Fraction(1, 6), Fraction(1, 5)]

    side_minus = []
    side_plus = []
    raw_samples = []
    for t in t_values:
        b, c, d, e = params_at_t(t)
        point = KinematicsPoint(b, c, d, e)
        checks = point.conservation_checks()
        amp = oracle.solve_on_shell((b, c, d, e), n=6)
        dTs = point_triple_numerators(point.omega)
        delta = point.delta

        sample = {
            "t": str(t),
            "params": {
                "b": fraction_to_str(b),
                "c": fraction_to_str(c),
                "d": fraction_to_str(d),
                "e": fraction_to_str(e),
            },
            "omega": [fraction_to_str(x) for x in point.omega],
            "word": point.sorted_magnitude_word()[0],
            "sum_omega_ok": checks["sum_omega_ok"],
            "sum_momentum_ok": checks["sum_momentum_ok"],
            "amp_im": fraction_to_str(amp.amp_im),
            "amp_im_rat": fraction_to_str(amp.amp_im),
            "delta": fraction_to_str(delta),
            "delta_den": delta.denominator,
            "triple_numerators": dTs,
            "denominator_to_delta": {
                "delta_den": delta.denominator,
                "relation": {
                    k: {
                        "dT_num": v["num"],
                        "dT_den": v["den"],
                        "gcd": str(gcd(v["den"], delta.denominator)),
                    }
                    for k, v in dTs.items()
                },
            },
            "pair_signs": {k: ("+" if v > 0 else "-" if v < 0 else "0") for k, v in point.pair_q.items()},
            "triple_signs": {k: ("+" if v > 0 else "-" if v < 0 else "0") for k, v in point.triple_q.items()},
            "is_generic": point.is_generic(),
        }
        raw_samples.append(sample)
        if t < 0:
            side_minus.append((t, amp.amp_im))
        elif t > 0:
            side_plus.append((t, amp.amp_im))

    side_minus_valued = [(t, amp) for t, amp in side_minus if t != 0]
    side_plus_valued = [(t, amp) for t, amp in side_plus if t != 0]

    valuation = {
        "amp_im": {
            "t_negative": scaled_sequences(side_minus_valued, max_p=10),
            "t_positive": scaled_sequences(side_plus_valued, max_p=10),
        },
    }

    out_data = {
        "base_point": base,
        "path": "b=b0+t, c=c0, d=d0, e=e0-t",
        "samples": raw_samples,
        "conservation": {
            "count": len(raw_samples),
            "all_sum_omega_ok": all(x["sum_omega_ok"] for x in raw_samples),
            "all_sum_momentum_ok": all(x["sum_momentum_ok"] for x in raw_samples),
        },
        "valuation": valuation,
        "valuation_heuristic": {
            "negative": valuation_heuristic(valuation["amp_im"]["t_negative"]["0"] if isinstance(valuation["amp_im"]["t_negative"]["0"], list) else []),
            "positive": valuation_heuristic(valuation["amp_im"]["t_positive"]["0"] if isinstance(valuation["amp_im"]["t_positive"]["0"], list) else []),
        },
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(out_data, indent=2, sort_keys=True))
    print(out)


if __name__ == "__main__":
    main()
