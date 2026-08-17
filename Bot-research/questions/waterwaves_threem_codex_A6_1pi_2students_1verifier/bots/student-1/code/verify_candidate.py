from fractions import Fraction
from pathlib import Path
import argparse
import json

from bg_oracle import BGOracle, fraction_to_str
import h1_batch


class Candidate(object):
    __slots__ = ("kind", "em", "ep", "coef")

    def __init__(self, kind, em, ep, coef):
        self.kind = kind
        self.em = em
        self.ep = ep
        self.coef = coef


def _to_fraction(v):
    if v is None:
        return None
    if isinstance(v, Fraction):
        return v
    return Fraction(v)


def _load_results(path: Path) -> dict:
    text = path.read_text()
    return json.loads(text)


def _parse_candidate(data: dict):
    h1 = data.get("h1", {})
    sel = h1.get("selected_candidate", {}) if isinstance(h1, dict) else {}
    if not sel or sel.get("type") in {None, "none"}:
        return None
    typ = sel.get("type")
    em, ep = int(sel.get("em", 0)), int(sel.get("ep", 0))
    if typ == "common":
        c = _to_fraction(sel.get("coef"))
        return Candidate(typ, em, ep, c)
    if typ == "pair":
        c = tuple(_to_fraction(x) for x in sel.get("coef", ()))
        return Candidate(typ, em, ep, c)
    if typ == "feature":
        # fallback feature candidates are not hard-coded for reuse safely in this stage
        return None
    return None


def _predict(candidate: Candidate, sample: h1_batch.ExactSample) -> Fraction:
    if candidate.kind == "common":
        return candidate.coef * h1_batch.sum_phi_pairs(sample.omega, candidate.em, candidate.ep)
    if candidate.kind == "pair":
        c01, c02, c12 = candidate.coef
        ph = h1_batch.pair_phi_map(sample.omega, candidate.em, candidate.ep)
        return c01 * ph["01"] + c02 * ph["02"] + c12 * ph["12"]
    raise ValueError("unknown candidate type")


def run_fresh_test(
    result_path: Path,
    qdir: Path,
    count: int,
    regenerate: bool,
) -> None:
    data = _load_results(result_path)
    cand = _parse_candidate(data)
    if cand is None:
        if regenerate:
            h1_batch.run_all(
                sample_target=max(60, count),
                train_frac=0.8,
                qdir=qdir,
                bg_binary=(qdir / "bots/student-1/bg").resolve(),
                data_dir=qdir / "bots/student-1/data",
                deriv_dir=qdir / "bots/student-1/derivations",
            )
            data = _load_results(result_path)
            cand = _parse_candidate(data)
        if cand is None:
            print("NO VERIFIED CANDIDATE")
            return

    oracle = BGOracle(binary_path=str(qdir / "bots/student-1/bg"))
    samples, _ = h1_batch.build_samples(
        oracle,
        target=count,
        sigma=h1_batch.DEFAULT_SIGMA,
    )
    # use first `count` accepted fresh points deterministically
    samples = samples[:count]
    pass_count = 0
    bad = []
    for s in samples:
        pred = _predict(cand, s)
        if pred == s.amp_im:
            pass_count += 1
        else:
            bad.append((s.point_id, str(pred), fraction_to_str(s.amp_im)))
    if bad:
        print(f"CANDIDATE FAIL: {pass_count}/{len(samples)}")
        print("residual mismatches:")
        for item in bad[:5]:
            print(f"  {item[0]} pred={item[1]} target={item[2]}")
    else:
        print(f"CANDIDATE VERIFIED: {pass_count}/{len(samples)}")
        print(f"candidate= {cand.kind} e_m={cand.em} e_p={cand.ep} coef={cand.coef}")


def main():
    parser = argparse.ArgumentParser(description="Verify saved H1 candidate")
    parser.add_argument("--results", type=Path, default=Path("bots/student-1/data/h1_results.json"))
    parser.add_argument("--qdir", type=Path, default=Path("."))
    parser.add_argument("--test-h1", action="store_true", help="run fresh candidate verification")
    parser.add_argument("--fresh-count", type=int, default=20)
    parser.add_argument("--generate-samples", action="store_true")
    args = parser.parse_args()

    qdir = args.qdir.resolve()
    result_path = args.results
    if not result_path.is_absolute():
        result_path = qdir / result_path

    if args.generate_samples:
        h1_batch.run_all(
            sample_target=max(60, args.fresh_count),
            train_frac=0.8,
            qdir=qdir,
            data_dir=qdir / "bots/student-1/data",
            deriv_dir=qdir / "bots/student-1/derivations",
            bg_binary=(qdir / "bots/student-1/bg").resolve(),
        )

    if args.test_h1:
        run_fresh_test(result_path, qdir, args.fresh_count, regenerate=False)
    else:
        data = _load_results(result_path)
        cand = _parse_candidate(data)
        if cand is None:
            print("NO VERIFIED CANDIDATE")
            return
        print("Saved candidate:")
        print(f"type={cand.kind} e_m={cand.em} e_p={cand.ep} coef={cand.coef}")


if __name__ == "__main__":
    main()
