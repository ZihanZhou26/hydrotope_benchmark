#!/usr/bin/env python3
"""Size the n=7 fit: count symmetry-reduced template dimensions ON THE MANIFOLD
for each piece of the candidate spline. No oracle needed.

Pieces (deg N_7 = 22, odd under w->-w, S_3(minus) x S_4(plus) symmetric):
  base B            : G'-sym odd deg-22 poly in invariants (e1,e2,e3m,e3p,e4p)
  single (1=1)      : (b_j-a_i)_+^1  * P,  deg P = 20, stab S_2(minus)xS_3(plus)
  (1=2)             : (a_i-b_j-b_k)_+^4 * Q, deg Q = 14, stab S_2(minus)xS_2(plus j,k)xS_2(plus l,m)
  (1=3)             : (a_i-b_j-b_k-b_l)_+^4 * R, deg R = 14, stab S_2(minus)xS_3(plus jkl)
The independent-dimension on the manifold (mod the on-shell ideal) is what matters
for the fit; we estimate it by numerical rank over random manifold points (mod p).
"""
from fractions import Fraction as F
import itertools, random
import n7lib as L
PR = 2**61-1
def minv(a): return pow(a % PR, PR-2, PR)
def fm(fr): return (fr.numerator % PR)*minv(fr.denominator % PR) % PR

def manifold_pts(npts, seed):
    rnd = random.Random(seed); pts = []
    while len(pts) < npts:
        free = [F(rnd.randint(-90, 90), 10) for _ in range(5)]
        if 0 in free: continue
        o = L.solve_squares(free)
        if o is None or any(w == 0 for w in o): continue
        pts.append(o)
    return pts

def rank_modp(rows):
    """rank of a list of row-vectors over F_p."""
    rows = [r[:] for r in rows]; nr = len(rows); nc = len(rows[0]) if rows else 0
    r = 0
    for c in range(nc):
        piv = next((i for i in range(r, nr) if rows[i][c] % PR != 0), None)
        if piv is None: continue
        rows[r], rows[piv] = rows[piv], rows[r]
        iv = minv(rows[r][c]); rows[r] = [(x*iv) % PR for x in rows[r]]
        for i in range(nr):
            if i != r and rows[i][c] % PR != 0:
                f = rows[i][c]; rows[i] = [(rows[i][k]-f*rows[r][k]) % PR for k in range(nc)]
        r += 1
        if r == nr: break
    return r

# ---- invariant base (smooth, G'-symmetric, odd) ----
def invs(o):
    m = [o[0], o[1], o[2]]; p = [o[3], o[4], o[5], o[6]]
    e1 = sum(p)
    e2 = sum(p[i]*p[j] for i, j in itertools.combinations(range(4), 2))
    e3p = sum(p[i]*p[j]*p[k] for i, j, k in itertools.combinations(range(4), 3))
    e4p = p[0]*p[1]*p[2]*p[3]
    e3m = m[0]*m[1]*m[2]
    return (e1, e2, e3m, e3p, e4p)  # degrees 1,2,3,3,4

def base_monos():
    """odd weighted-deg-22 monomials in (e1[1],e2[2],e3m[3],e3p[3],e4p[4]); parity odd: a+c+d odd."""
    out = []
    for a in range(0, 23):
        for b in range(0, 12):
            for c in range(0, 8):
                for d in range(0, 8):
                    for e in range(0, 6):
                        # N_7 is EVEN under w->-w (a+c+d even; automatic at even weighted-degree 22)
                        if a + 2*b + 3*c + 3*d + 4*e == 22 and (a + c + d) % 2 == 0:
                            out.append((a, b, c, d, e))
    return out

def eval_base(mono, o):
    e = invs(o); a, b, c, d, ee = mono
    return (e[0]**a)*(e[1]**b)*(e[2]**c)*(e[3]**d)*(e[4]**ee)

if __name__ == "__main__":
    pts = manifold_pts(400, seed=11)
    bm = base_monos()
    print(f"base: raw odd wdeg-22 monomials in 5 invariants = {len(bm)}")
    rows = [[fm(eval_base(m, o)) for m in bm] for o in pts]
    print(f"base: INDEPENDENT dim on manifold = {rank_modp(rows)}")
