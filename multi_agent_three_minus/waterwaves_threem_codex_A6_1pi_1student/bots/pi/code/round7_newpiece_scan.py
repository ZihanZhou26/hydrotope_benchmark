#!/usr/bin/env python3
"""PI round-7: cone reconstruction DEGREE SCAN in a NEW realized piece.

Uses the same dehomogenize-by-omega_2 cone trick as round6_reconstruct.py (which
WORKED where the fixed-den ansatz failed), but with the base FIXED to one of the
three new realized pieces from job r6_piece_20260726T173931Z, to learn the
in-piece rational degree d_min (deg P) there. Fresh bg_r7 (built this round).
"""
import sys, random, json
from fractions import Fraction as F
sys.path.insert(0, "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code")
import round6_reconstruct as R

# point round6 helpers at the fresh round-7 BG
R.BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code/bg_r7"

NEW = {
    "12ea165a03": [F(9), F(8), F(2), F(-5)],     # compmat [[1,1],[1,1]], h16>0  (A-like compmat)
    "7608cb858a": [F(-4), F(9), F(6), F(-7)],     # compmat [[-1,-1],[1,1]]
    "a2fa6ab8af": [F(7), F(2), F(-3), F(-5)],     # compmat [[1,1],[-1,-1]]
}


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "12ea165a03"
    need = int(sys.argv[2]) if len(sys.argv) > 2 else 700
    dmax = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    base_f = NEW[name]
    om0 = R.solve_onshell(base_f)
    base_sg, margin = R.full_sign_and_margin(om0)
    print(f"piece {name}: base free={[str(x) for x in base_f]} om0={[str(x) for x in om0]}")
    print(f"margin={float(margin):.4f}  (0 in sig: {0 in base_sg})")
    pts, tries = R.collect(base_f, base_sg, need, seed=4242)
    print(f"collected {len(pts)} in-piece points (tries={tries})")
    with open(f"round7_pts_{name}.json", "w") as fh:
        json.dump({"base_f": [str(x) for x in base_f], "base_sg": list(base_sg),
                   "pts": [[str(a) for a in pt] for pt in pts]}, fh)
    print("-" * 72)
    dmin = None
    for d in range(3, dmax + 1):
        mon = R.monos_upto(d); nm = len(mon); ncol = 2 * nm
        if len(pts) < ncol + 12:
            print(f"d={d}: cols={ncol} pts={len(pts)} -> need more pts"); break
        X = R.build_rows_np(pts, mon, R.P31)
        rank = R.rank_mod_np(X, R.P31)
        nulldim = ncol - rank
        tag = "REP EXISTS" if nulldim > 0 else "no rep"
        print(f"d={d}: |M|={nm} cols={ncol} pts={len(pts)} rank={rank} nulldim={nulldim} => {tag}")
        sys.stdout.flush()
        if nulldim > 0:
            dmin = d; break
    print()
    if dmin is None:
        print(f"==> no rational rep up to d={dmax} in piece {name}")
    else:
        print(f"==> piece {name}: d_min={dmin} (deg Q={dmin-2}, deg P={dmin})")


if __name__ == "__main__":
    main()
