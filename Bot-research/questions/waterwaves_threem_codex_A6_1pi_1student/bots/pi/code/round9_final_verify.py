#!/usr/bin/env python3
"""PI round-9 FINAL-SUMMARY independent verification.

Fresh bg_r9 (byte-identical source to immutable root bg.cpp, md5 41715c4a...).
Re-banks the load-bearing results one last time and independently pushes the
higher-degree obstruction one rung beyond my round-7 pi_v_025.

Parts:
  1. SYMBOLIC : four-block H_A == PI's own 31-term core (BG-independent).
  2. NUMERIC  : four-block H_A,H_B reproduce fresh bg_r9 EXACTLY (Fraction) on
                in-piece points of the two OPPOSITE chambers A, B.
  3. BOUNDARY : both H_A and H_B FAIL at the higher-degree chamber 12ea165a03
                (base + deterministic in-piece perturbations).
  4. OBSTRUCTION (independent): equal-bound cone rank scan on chamber 12ea165a03,
                d=12 and d=13, over two primes.  d=12 nulldim=0 reconfirms
                pi_v_025 (deg Q_hom>10); d=13 nulldim=0 => d_eq>=14 =>
                deg Q_hom>=12, my own independent step toward the student's
                s1_022 (deg Q_hom>=13).  Points: the 1050 I collected myself in
                round 7 (round7_pts_12ea165a03.json), topped up with fresh bg_r9.
"""
import sys, os, json
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import round7_verify_compact as r7
import round8_verify_fourblock as r8
import round6_reconstruct as R

BG9 = os.path.join(HERE, "bg_r9")
r7.BG = BG9        # H_A/H_B numeric harness + run_piece
R.BG = BG9         # cone point collector
ROOT = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student"
PTS12 = os.path.join(ROOT, "round7_pts_12ea165a03.json")

# second prime for the rank scan (student used 2147483629 as the 2nd)
P31b = 2147483629


def part1_symbolic():
    print("== PART 1: SYMBOLIC four-block == PI's 31-term core (BG-independent) ==")
    ok = r8.symbolic_check()
    print("  => symbolic identity:", "PASS" if ok else "FAIL")
    return ok


def part2_numeric():
    print("\n== PART 2: NUMERIC four-block vs FRESH bg_r9 (exact Fraction, in-piece) ==")
    a_ok, a_bad = r7.run_piece("A / fourblock_H_A", [9, -8, -3, -4], r8.fourblock_H_A)
    b_ok, b_bad = r7.run_piece("B / fourblock_H_B", [4, 3, 8, 7], r8.fourblock_H_B)
    ok = a_bad == 0 and b_bad == 0 and a_ok > 0 and b_ok > 0
    print(f"  => numeric A={a_ok}/{a_ok+a_bad}  B={b_ok}/{b_ok+b_bad}:",
          "PASS" if ok else "FAIL")
    return ok


def part3_boundary():
    print("\n== PART 3: BOUNDARY — two-chamber formula FAILS at 12ea165a03 ==")
    # base free for 12ea165a03 (higher-degree chamber)
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
    # a few in-piece perturbations, confirm neither formula ever matches here
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


def load_and_topup_12ea(target):
    d = json.load(open(PTS12))
    base_f = [F(x) for x in d["base_f"]]
    base_sg = tuple(d["base_sg"])
    pts = [tuple(F(a) for a in pt) for pt in d["pts"]]
    print(f"  loaded {len(pts)} round-7 points (my own harness), base_f={d['base_f']}")
    if len(pts) < target:
        need = target - len(pts)
        print(f"  collecting {need} more with fresh bg_r9 ...")
        more, tries = R.collect(base_f, base_sg, need, seed=9091)
        pts.extend(more)
        print(f"  now {len(pts)} points (tries={tries})")
    return pts


def part4_obstruction():
    print("\n== PART 4: independent equal-bound cone rank scan on 12ea165a03 ==")
    # d=13 equal-bound needs 2*C(16,3)=1120 cols; collect a safe margin
    pts = load_and_topup_12ea(1260)
    import numpy as np
    results = {}
    allok = True
    for d in (12, 13):
        mon = R.monos_upto(d); nm = len(mon); ncol = 2 * nm
        if len(pts) < ncol + 12:
            print(f"  d={d}: cols={ncol} pts={len(pts)} -> NOT ENOUGH PTS"); allok = False; continue
        nulls = []
        for p in (R.P31, P31b):
            X = R.build_rows_np(pts, mon, p)
            rank = R.rank_mod_np(X, p)
            nulls.append(ncol - rank)
        tag = "REP EXISTS" if any(n > 0 for n in nulls) else "no rep (full rank)"
        print(f"  d={d}: |M|={nm} cols={ncol} pts={len(pts)} nullity(p1,p2)={tuple(nulls)} => {tag}")
        results[d] = nulls
        if any(n > 0 for n in nulls):
            allok = False
    # interpretation
    d12ok = results.get(12) == [0, 0]
    d13ok = results.get(13) == [0, 0]
    print(f"  => d=12 full rank (reconfirms pi_v_025 deg Q_hom>10): {'PASS' if d12ok else 'FAIL'}")
    print(f"  => d=13 full rank (my independent step: d_eq>=14 => deg Q_hom>=12): "
          f"{'PASS' if d13ok else 'FAIL'}")
    return d12ok and d13ok, results


if __name__ == "__main__":
    print("PI round-9 FINAL verification, fresh bg_r9\n")
    import subprocess
    md5 = subprocess.run(["md5sum", os.path.join(HERE, "bg_r9.cpp")],
                         stdout=subprocess.PIPE, universal_newlines=True).stdout.split()[0]
    print("bg_r9.cpp md5:", md5, "\n")
    p1 = part1_symbolic()
    p2 = part2_numeric()
    p3 = part3_boundary()
    p4, r4 = part4_obstruction()
    print("\n=== SUMMARY ===")
    print(f"  P1 symbolic four-block identity : {'PASS' if p1 else 'FAIL'}")
    print(f"  P2 numeric four-block vs bg_r9  : {'PASS' if p2 else 'FAIL'}")
    print(f"  P3 boundary (12ea fails)        : {'PASS' if p3 else 'FAIL'}")
    print(f"  P4 higher-degree obstruction    : {'PASS' if p4 else 'FAIL'}  {r4}")
    sys.exit(0 if (p1 and p2 and p3 and p4) else 1)
