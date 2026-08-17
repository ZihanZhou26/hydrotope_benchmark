import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

from kinematics import BGOracle


def run_step(command, cwd):
    proc = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def oracle_anchor_check(oracle: BGOracle):
    sigma = (-1, -1, -1, 1, 1, 1)

    checks = {}
    # exact 6-point anchors from student-2 task
    anchors = [
        {
            "label": "a1",
            "omega": (Fraction(-8), Fraction(2), Fraction(3), Fraction(4), Fraction(5), Fraction(-6)),
            "expected_im": Fraction(-9190656, 7),
        },
        {
            "label": "a2",
            "omega": (Fraction(-154, 17), Fraction(3), Fraction(5), Fraction(2), Fraction(7), Fraction(-135, 17)),
            "expected_im": Fraction(-641893056, 85),
        },
    ]

    fails = []
    for a in anchors:
        res = oracle.eval_with_omega(a["omega"], sigma=sigma)
        ok = (res.amp_re == 0 and res.amp_im == a["expected_im"])
        checks[a["label"]] = {
            "n": res.n,
            "omega": [str(x) for x in a["omega"]],
            "amp_im": str(res.amp_im),
            "amp_re": str(res.amp_re),
            "expected_im": str(a["expected_im"]),
            "ok": ok,
        }
        if not ok:
            fails.append(a["label"])

    return checks, fails


def run_chamber_scan(check_dir: Path):
    rc, out, err = run_step(["python3", "bots/student-2/code/chamber_scan.py"], check_dir)
    if rc != 0:
        return {"status": "failed", "stderr": err, "stdout": out}, ["chamber_scan_crash"]

    p = check_dir / "bots/student-2/data/chamber_scan.json"
    payload = json.loads(p.read_text())
    observed = payload.get("observed_words", [])
    all20 = set(payload.get("all_20_words", []))
    expected = set(payload.get("expected_reference_words", []))
    fail = []
    if not observed:
        fail.append("chamber_scan_no_words")
    if not all((w in all20) for w in observed):
        fail.append("chamber_non_3plus3")
    if payload.get("stabilization", {}).get("stable") is False:
        fail.append("chamber_not_stable")
    if payload.get("pair_triple_checks", {}).get("a>d", 0) == 0 or payload.get("pair_triple_checks", {}).get("f>b", 0) == 0:
        fail.append("chamber_missing_param_checks")

    status = {
        "status": "ok" if not fail else "fail",
        "observed_word_count": len(observed),
        "observed_words": observed,
        "extras": payload.get("extras_against_expected", []),
        "missing_expected": payload.get("missing_expected", []),
        "stabilized": payload.get("stabilization", {}).get("stable", False),
    }
    return status, fail


def run_wall_probe(check_dir: Path):
    rc, out, err = run_step(["python3", "bots/student-2/code/wall_probe.py"], check_dir)
    if rc != 0:
        return {"status": "failed", "stderr": err, "stdout": out}, ["wall_probe_crash"]
    p = check_dir / "bots/student-2/data/wall_probe.json"
    payload = json.loads(p.read_text())

    fails = []
    status = {
        "pair": payload.get("pair_wall", {}),
        "triple": payload.get("triple_wall", {}),
        "af": payload.get("af_wall", {}),
    }

    if payload.get("pair_wall", {}).get("status") != "not_found" and not payload.get("pair_wall", {}).get("left_count"):
        fails.append("pair_wall_samples")
    if payload.get("pair_wall", {}).get("status") == "not_found":
        fails.append("pair_wall_missing")
    if payload.get("triple_wall", {}).get("status") == "not_found":
        fails.append("triple_wall_missing")
    if payload.get("pair_wall", {}).get("left_count", 0) < 1 or payload.get("pair_wall", {}).get("right_count", 0) < 1:
        fails.append("pair_wall_branch_empty")
    if payload.get("triple_wall", {}).get("left_count", 0) < 1 or payload.get("triple_wall", {}).get("right_count", 0) < 1:
        fails.append("triple_wall_branch_empty")

    return status, fails


def run_pole_probe(check_dir: Path):
    rc, out, err = run_step(["python3", "bots/student-2/code/pole_probe.py"], check_dir)
    if rc != 0:
        return {"status": "failed", "stderr": err, "stdout": out}, ["pole_probe_crash"]
    p = check_dir / "bots/student-2/data/pole_probe.json"
    payload = json.loads(p.read_text())
    fails = []

    cons = payload.get("conservation", {})
    if not cons.get("all_sum_omega_ok", False) or not cons.get("all_sum_momentum_ok", False):
        fails.append("pole_non_conserving")
    if len(payload.get("samples", [])) < 4:
        fails.append("pole_few_samples")
    status = {
        "samples": len(payload.get("samples", [])),
        "conservation": cons,
    }
    return status, fails


def main():
    qdir = Path(".").resolve()
    oracle = BGOracle(qdir / "bots/student-2/bg")

    fail_flags = []
    report = {
        "oracle": {}
    }

    # anchors
    anchor_results, anchor_fails = oracle_anchor_check(oracle)
    report["anchor_checks"] = anchor_results
    fail_flags.extend(["anchor:" + f for f in anchor_fails])

    # chamber
    chamber_status, chamber_fails = run_chamber_scan(qdir)
    report["chamber_scan"] = chamber_status
    fail_flags.extend(chamber_fails)

    # wall
    wall_status, wall_fails = run_wall_probe(qdir)
    report["wall_probe"] = wall_status
    fail_flags.extend(["wall:" + f for f in wall_fails])

    # pole
    pole_status, pole_fails = run_pole_probe(qdir)
    report["pole_probe"] = pole_status
    fail_flags.extend(["pole:" + f for f in pole_fails])

    # write summary text and exit status
    out = qdir / "bots/student-2/data/verify_round1.txt"
    lines = []
    if fail_flags:
        lines.append("PASS/FAIL: FAIL")
    else:
        lines.append("PASS/FAIL: PASS")
    lines.append("")
    lines.append(f"failed_items={len(fail_flags)}")
    for f in fail_flags:
        lines.append(f"FAIL: {f}")
    lines.append("")
    lines.append(json.dumps(report, indent=2, sort_keys=True))

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))

    print("bots/student-2/data/verify_round1.txt")
    if fail_flags:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
