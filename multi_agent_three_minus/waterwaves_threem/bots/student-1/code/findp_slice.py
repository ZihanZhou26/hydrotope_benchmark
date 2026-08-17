#!/usr/bin/env python3
"""Find the sumFree-denominator power p of A_6 via a 1D slice staying in RAW0.
A_6 * sumFree^p = univariate polynomial of degree 8+p in the slice parameter t.
Exact rational; cheap."""
from fractions import Fraction as F
import harness as h, chambers_n6 as cn
from exactfit import exact_solve
import modfit as mf

SIG = [-1, -1, -1, 1, 1, 1]


def slice_pts(base, dirn, krange, step):
    rawsig = cn.wall_signs([w * w for w in cn.solve_squares(base)])
    pts = []
    for k in range(-krange, krange + 1):
        t = F(k, step)
        free = tuple(base[i] + t * dirn[i] for i in range(4))
        if any(x == 0 for x in free):
            continue
        oms = cn.solve_squares(free)
        if oms is None or any(w == 0 for w in oms):
            continue
        sq = [w * w for w in oms]
        ws = cn.wall_signs(sq)
        if ws is None or ws != rawsig:
            continue
        try:
            im, _, _ = h.on_shell(list(free), SIG)
        except Exception:
            continue
        pts.append((t, sum(free), im))
    return pts


def find_base_dir():
    """Find a base in RAW0 and a direction giving many in-chamber slice points."""
    import random
    rnd = random.Random(123)
    best = None
    for _ in range(4000):
        free = tuple(F(rnd.randint(-60, 60), 10) for _ in range(4))
        if any(x == 0 for x in free):
            continue
        oms = cn.solve_squares(free)
        if oms is None or any(w == 0 for w in oms):
            continue
        sq = [w * w for w in oms]
        ws = cn.wall_signs(sq)
        if ws != mf.RAW0:
            continue
        # try a few directions
        for dirn in [(F(1), F(0), F(0), F(0)), (F(0), F(1), F(0), F(0)),
                     (F(0), F(0), F(1), F(0)), (F(0), F(0), F(0), F(1)),
                     (F(1), F(-1), F(1), F(-1)), (F(1), F(1), F(-1), F(-1))]:
            pts = slice_pts(free, dirn, 60, 60)
            if best is None or len(pts) > best[2]:
                best = (free, dirn, len(pts), pts)
        if best and best[2] >= 40:
            break
    return best


if __name__ == "__main__":
    base, dirn, npt, pts = find_base_dir()
    print(f"base={[str(x) for x in base]} dir={[str(x) for x in dirn]} in-chamber pts={npt}")
    for p in range(0, 9):
        deg = 8 + p
        if len(pts) < deg + 4:
            print(f"p={p}: not enough pts ({len(pts)})")
            continue
        rows = [[t ** k for k in range(deg + 1)] for (t, sF, im) in pts]
        ys = [im * sF ** p for (t, sF, im) in pts]
        ntr = deg + 1
        sol = exact_solve(rows[:ntr], ys[:ntr])
        if sol is None:
            print(f"p={p}: INCONSISTENT")
            continue
        ok = bad = 0
        for row, y in zip(rows[ntr:], ys[ntr:]):
            pred = sum(c * v for c, v in zip(sol, row))
            if pred == y:
                ok += 1
            else:
                bad += 1
        print(f"p={p}: deg{deg} held-out {ok}/{ok+bad}{'  <<< FOUND p='+str(p) if bad==0 and ok>0 else ''}")
