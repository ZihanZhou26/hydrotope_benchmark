#!/usr/bin/env python3
"""PI round-10 FINAL-SUMMARY independent verification (fresh bg_r10).

This re-runs, against my OWN freshly built binary bg_r10 (byte-identical source
to the immutable root bg.cpp, md5 41715c4a..., sha256 bd1afe67...), every
load-bearing claim of the final summary, PLUS the required 5-point calibration.

Parts:
  0. CALIBRATION : three-minus A_5 == sign-flipped two-minus formula (exact),
                   plus the two-minus n=5 self-check.  Validates the BG harness.
  1. SYMBOLIC    : four-block H_A == PI's own 31-term core (BG-independent).
  2. NUMERIC     : four-block H_A,H_B reproduce fresh bg_r10 EXACTLY (Fraction)
                   on in-piece points of the two OPPOSITE chambers A, B.
  3. BOUNDARY    : both H_A and H_B FAIL at the higher-degree chamber 12ea165a03
                   (base + deterministic in-piece perturbations).
  4. OBSTRUCTION : equal-bound cone rank scan on chamber 12ea165a03 with points
                   I collect MYSELF using bg_r10.  d=12 full rank reconfirms
                   deg Q_hom > 10 (pi_v_025); d=13 full rank => deg Q_hom >= 12.
"""
import sys, os, json, subprocess, re
from fractions import Fraction as F
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import round7_verify_compact as r7
import round8_verify_fourblock as r8
import round6_reconstruct as R

BG10 = os.path.join(HERE, "bg_r10")
r7.BG = BG10        # H_A/H_B numeric harness + run_piece + bg_amp_from_free
R.BG = BG10         # cone point collector
SIG = [-1, -1, -1, 1, 1, 1]
P31b = 2147483629   # second prime for the rank scan


# ----------------------------------------------------------------------------
# PART 0 : five-point calibration (BG harness validity), all exact
# ----------------------------------------------------------------------------
def run_bg_n5(freeW, sig):
    cmd = [BG10, "-n", "5", "-w", ",".join(freeW), "-s", ",".join(sig), "-g", "1"]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       universal_newlines=True)
    if p.returncode != 0:
        return None
    out = p.stdout
    om = re.search(r"omega = \{([^}]*)\}", out).group(1)
    omega = [F(t.strip()) for t in om.split(",")]
    m = re.search(r"A_5 = i \* \(([^)]*)\)", out)
    if m:
        return omega, F(0), F(m.group(1))
    m2 = re.search(r"A_5 = \(([^)]*)\) \+ i \* \(([^)]*)\)", out)
    return omega, F(m2.group(1)), F(m2.group(2))


def two_minus_formula(omega, minus_legs, g=F(1)):
    n = len(omega)
    a, b = minus_legs
    plus = [i for i in range(n) if i not in minus_legs]
    beta = min(abs(omega[a]), abs(omega[b]))
    b2 = beta * beta
    tot = F(0)
    for rr in range(len(plus) + 1):
        for S in combinations(plus, rr):
            arg = b2 - sum(omega[j] * omega[j] for j in S)
            if arg > 0:
                tot += F((-1) ** rr) * arg ** (n - 3)
    return F(2) ** (n - 1) * g ** (3 - n) * omega[a] * omega[b] * tot


def part0_calibration():
    print("== PART 0: five-point calibration (exact) ==")
    cases = [
        ("n=5 two-minus {1,2}", ["2", "3", "5"], ["-1", "-1", "1", "1", "1"], (0, 1)),
        ("n=5 two-minus b {1,2}", ["7", "2", "13"], ["-1", "-1", "1", "1", "1"], (0, 1)),
        ("n=5 THREE-minus vs two{4,5}", ["2", "3", "5"], ["-1", "-1", "-1", "1", "1"], (3, 4)),
        ("n=5 THREE-minus b", ["4", "7", "2"], ["-1", "-1", "-1", "1", "1"], (3, 4)),
        ("n=5 THREE-minus c", ["11", "3", "8"], ["-1", "-1", "-1", "1", "1"], (3, 4)),
        ("n=5 THREE-minus d", ["6", "13", "4"], ["-1", "-1", "-1", "1", "1"], (3, 4)),
    ]
    allok = True
    for label, freeW, sig, ml in cases:
        res = run_bg_n5(freeW, sig)
        if res is None:
            print(f"  [SKIP] {label} (wall/pole)"); continue
        omega, A_re, A_im = res
        pred = two_minus_formula(omega, ml)
        ok = (A_re == 0) and (A_im == pred)
        allok &= ok
        print(f"  [{'OK' if ok else 'FAIL'}] {label}: bg={A_im}  formula={pred}")
    print("  => calibration:", "PASS" if allok else "FAIL")
    return allok


# ----------------------------------------------------------------------------
# PART 1-3 : reuse round-8/round-7 formula code, all bg calls -> bg_r10
# ----------------------------------------------------------------------------
def part1_symbolic():
    print("\n== PART 1: SYMBOLIC four-block == PI's 31-term core (BG-independent) ==")
    ok = r8.symbolic_check()
    print("  => symbolic identity:", "PASS" if ok else "FAIL")
    return ok


def part2_numeric():
    print("\n== PART 2: NUMERIC four-block vs FRESH bg_r10 (exact Fraction, in-piece) ==")
    a_ok, a_bad = r7.run_piece("A / fourblock_H_A", [9, -8, -3, -4], r8.fourblock_H_A)
    b_ok, b_bad = r7.run_piece("B / fourblock_H_B", [4, 3, 8, 7], r8.fourblock_H_B)
    ok = a_bad == 0 and b_bad == 0 and a_ok > 0 and b_ok > 0
    print(f"  => numeric A={a_ok}/{a_ok+a_bad}  B={b_ok}/{b_ok+b_bad}:",
          "PASS" if ok else "FAIL")
    return ok


def part3_boundary():
    print("\n== PART 3: BOUNDARY -- two-chamber formula FAILS at 12ea165a03 ==")
    base_free = [F(9), F(8), F(2), F(-5)]
    res = r7.bg_amp_from_free(base_free)
    om0, a6 = res
    sv0 = r7.sign_vector(om0)
    predA = r7.prod_all(om0) * r7.H_A(om0)
    predB = r7.prod_all(om0) * r7.H_B(om0)
    print(f"  base om={[str(x) for x in om0]}  A6_im={a6}")
    print(f"  H_A pred={predA}  match={predA==a6}")
    print(f"  H_B pred={predB}  match={predB==a6}")
    failA = predA != a6
    failB = predB != a6
    matches = 0; tested = 0
    for t in range(30):
        d = [F(1 + t, 1000), F(-3 - 2*t, 1000), F(2 + t, 1000), F(-1 - 3*t, 1000)]
        free = [base_free[i] + d[i] for i in range(4)]
        r = r7.bg_amp_from_free(free)
        if r is None:
            continue
        om, a = r
        if r7.sign_vector(om) != sv0:
            continue
        tested += 1
        if r7.prod_all(om)*r7.H_A(om) == a or r7.prod_all(om)*r7.H_B(om) == a:
            matches += 1
    print(f"  in-piece perturbations: {matches}/{tested} matched either formula")
    ok = failA and failB and matches == 0
    print("  => boundary (neither formula holds in 12ea165a03):",
          "PASS" if ok else "FAIL")
    return ok


# ----------------------------------------------------------------------------
# PART 4 : obstruction rank scan on FRESH bg_r10 points (my own)
# ----------------------------------------------------------------------------
def part4_obstruction(nfresh):
    print(f"\n== PART 4: equal-bound cone rank scan on 12ea165a03 (FRESH bg_r10 pts) ==")
    base_f = [F(9), F(8), F(2), F(-5)]
    om0 = R.solve_onshell(base_f)
    base_sg, _ = R.full_sign_and_margin(om0)
    print(f"  base_f={[str(x) for x in base_f]}  collecting {nfresh} FRESH in-piece pts ...")
    pts, tries = R.collect(base_f, base_sg, nfresh, seed=101010)
    print(f"  collected {len(pts)} points myself with bg_r10 (tries={tries})")
    # persist my own points
    outpath = os.path.join(HERE, "round10_pts_12ea165a03.json")
    with open(outpath, "w") as fh:
        json.dump({"base_f": [str(x) for x in base_f], "base_sg": list(base_sg),
                   "pts": [[str(a) for a in pt] for pt in pts]}, fh)
    print(f"  persisted -> {outpath}")

    import numpy as np
    results = {}
    for d in (12, 13):
        mon = R.monos_upto(d); nm = len(mon); ncol = 2 * nm
        if len(pts) < ncol + 12:
            print(f"  d={d}: cols={ncol} pts={len(pts)} -> NOT ENOUGH PTS")
            results[d] = None; continue
        nulls = []
        for p in (R.P31, P31b):
            X = R.build_rows_np(pts, mon, p)
            rank = R.rank_mod_np(X, p)
            nulls.append(ncol - rank)
        tag = "REP EXISTS" if any(n > 0 for n in nulls) else "no rep (full rank)"
        print(f"  d={d}: |M|={nm} cols={ncol} pts={len(pts)} nullity(p1,p2)={tuple(nulls)} => {tag}")
        results[d] = nulls
    d12ok = results.get(12) == [0, 0]
    d13ok = results.get(13) == [0, 0]
    print(f"  => d=12 full rank (reconfirms deg Q_hom>10): {'PASS' if d12ok else 'FAIL'}")
    print(f"  => d=13 full rank (deg Q_hom>=12):          {'PASS' if d13ok else 'FAIL'}")
    return d12ok and d13ok, results


if __name__ == "__main__":
    print("PI round-10 FINAL verification, fresh bg_r10\n")
    md5 = subprocess.run(["md5sum", os.path.join(HERE, "bg_r10.cpp")],
                         stdout=subprocess.PIPE, universal_newlines=True).stdout.split()[0]
    print("bg_r10.cpp md5:", md5)
    canon = subprocess.run([BG10, "-n", "6", "-w", "2,3,5,7", "-s", "-1,-1,-1,1,1,1"],
                           stdout=subprocess.PIPE, universal_newlines=True).stdout
    print("canonical A_6:", re.search(r"A_6 = i \* \(([^)]*)\)", canon).group(1), "\n")
    nfresh = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
    p0 = part0_calibration()
    p1 = part1_symbolic()
    p2 = part2_numeric()
    p3 = part3_boundary()
    p4, r4 = part4_obstruction(nfresh)
    print("\n=== SUMMARY ===")
    print(f"  P0 five-point calibration       : {'PASS' if p0 else 'FAIL'}")
    print(f"  P1 symbolic four-block identity : {'PASS' if p1 else 'FAIL'}")
    print(f"  P2 numeric four-block vs bg_r10 : {'PASS' if p2 else 'FAIL'}")
    print(f"  P3 boundary (12ea fails)        : {'PASS' if p3 else 'FAIL'}")
    print(f"  P4 higher-degree obstruction    : {'PASS' if p4 else 'FAIL'}  {r4}")
    sys.exit(0 if (p0 and p1 and p2 and p3 and p4) else 1)
