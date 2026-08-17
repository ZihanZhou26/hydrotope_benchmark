#!/usr/bin/env python3
"""Test FACTORIZATION of the simple-pole residue of A_6.

A_6/i has a simple pole at the perfect-matching locus e3m+e3p=0. On an F-const slice
the chamber's analytic form A_6/i = Num(t)/Den(t) is reconstructed exactly; each real
root r of Den is a matching point where a full matching {w_i + w_{sigma(i)} = 0} holds.
The residue there, Res = Num(r)/Den'(r), is compared to candidate factorizations:
  - A_4^{2-} on the 4 legs left after removing ONE matched pair (i,j);
  - products over the matched pairs.
We tabulate residue and ratios to find the structure.
"""
from fractions import Fraction as F
import itertools
import harness as h

SIG = [-1, -1, -1, 1, 1, 1]
MINUS = (1, 2, 3); PLUS = (4, 5, 6)


# ---------- exact rational-function reconstruction (Pade), ported clean ----------
def solve_exact(A, b):
    n = len(A)
    M = [[F(A[i][j]) for j in range(n)] + [F(b[i])] for i in range(n)]
    for col in range(n):
        piv = next((r for r in range(col, n) if M[r][col] != 0), None)
        if piv is None:
            return None
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]; M[col] = [x / pv for x in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col]; M[r] = [M[r][k] - f * M[col][k] for k in range(n + 1)]
    return [M[i][n] for i in range(n)]


def reconstruct(pts, cap=24):
    nP = len(pts)
    for total in range(cap):
        for dD in range(total + 1):
            dN = total - dD
            nun = (dN + 1) + dD
            if nP < nun + 4:
                continue
            rows, rhs = [], []
            for (x, G) in pts[:nun]:
                rows.append([x ** j for j in range(dN + 1)] + [-G * x ** k for k in range(1, dD + 1)])
                rhs.append(G)
            sol = solve_exact(rows, rhs)
            if sol is None:
                continue
            Nc = sol[:dN + 1]; Dc = [F(1)] + sol[dN + 1:]
            ok = True
            for (x, G) in pts[nun:]:
                dval = sum(c * x ** k for k, c in enumerate(Dc))
                nval = sum(c * x ** j for j, c in enumerate(Nc))
                if dval == 0 or nval != G * dval:
                    ok = False; break
            if ok:
                return dN, dD, Nc, Dc
    return None


def two_minus_over_i(omega, minus, plus, g=F(1)):
    """A_m^{2-}/i for given minus pair, plus legs; omega is dict leg->Fraction."""
    a, b = minus
    m = len(omega)
    beta2 = min(omega[a] ** 2, omega[b] ** 2)
    tot = F(0)
    P = list(plus)
    for r in range(len(P) + 1):
        for S in itertools.combinations(P, r):
            v = beta2 - sum(omega[j] ** 2 for j in S)
            if v > 0:
                tot += F((-1) ** r) * v ** (m - 3)
    return F(2 ** (m - 1)) * g ** (3 - m) * omega[a] * omega[b] * tot


def slice_data(w2, w3, a, b, step=F(1, 40), maxk=60):
    """F-const slice w4=a+t,w5=b-t; sample contiguous in-chamber A_6/i(t)."""
    def sig(oms):
        w = {i + 1: oms[i] for i in range(6)}
        tg = []
        for i in MINUS:
            for j in PLUS:
                tg.append(1 if w[j] ** 2 - w[i] ** 2 > 0 else -1)
        return tuple(tg)
    pts = []
    s0 = None
    for direction in (1, -1):
        for k in range(0 if direction == 1 else 1, maxk):
            tv = direction * step * k
            free = [F(w2), F(w3), F(a) + tv, F(b) - tv]
            if sum(free) == 0:
                continue
            try:
                im, oms, re_p = h.on_shell(free, SIG)
            except Exception:
                break
            oms = [F(o) for o in oms]
            s = sig(oms)
            if s0 is None:
                s0 = s
            if s != s0:
                break
            pts.append((F(tv), F(im)))
    return pts


def matching_of(w):
    """Return sigma: minus-leg -> plus-leg if a perfect matching w_i+w_j=0 holds."""
    m = {}
    used = set()
    for i in MINUS:
        for j in PLUS:
            if j not in used and w[i] + w[j] == 0:
                m[i] = j; used.add(j); break
    return m if len(m) == 3 else None


def analyze(w2, w3, a, b):
    pts = slice_data(w2, w3, a, b)
    if len(pts) < 14:
        return []
    rec = reconstruct(pts)
    if rec is None:
        return []
    dN, dD, Nc, Dc = rec
    # find real rational roots of Den
    import sympy as sp
    t = sp.Symbol('t')
    Dpoly = sum(sp.Rational(c.numerator, c.denominator) * t ** k for k, c in enumerate(Dc))
    Npoly = sum(sp.Rational(c.numerator, c.denominator) * t ** j for j, c in enumerate(Nc))
    Dprime = sp.diff(Dpoly, t)
    out = []
    for r, mult in sp.roots(Dpoly).items():
        if not r.is_rational:
            continue
        rr = F(int(sp.fraction(r)[0]), int(sp.fraction(r)[1]))
        # omega at t=r
        free = [F(w2), F(w3), F(a) + rr, F(b) - rr]
        oms = h.solve_legs_1n([str(x) for x in free], SIG) if False else None
        # use harness solve
        import r4lib
        from harness import solve_legs_1n
        omv = solve_legs_1n(free, SIG)
        w = {i + 1: F(omv[i]) for i in range(6)}
        match = matching_of(w)
        res = sp.Rational(Npoly.subs(t, r) / Dprime.subs(t, r))
        res = F(int(sp.fraction(res)[0]), int(sp.fraction(res)[1]))
        out.append((w, match, res))
    return out


if __name__ == "__main__":
    slices = [(2, 3, 5, 7), (2, 3, 4, 9), (1, 4, 5, 8), (3, 5, 6, 10), (1, 6, 7, 9),
              (2, 5, 6, 11), (3, 4, 7, 8), (1, 2, 8, 9)]
    rows = []
    for sl in slices:
        for (w, match, res) in analyze(*sl):
            if match is None:
                continue
            # remove one matched pair (i=minus, j=match[i]); A_4^{2-} on the other 4 legs
            for i in MINUS:
                j = match[i]
                rem_minus = tuple(x for x in MINUS if x != i)
                rem_plus = tuple(x for x in PLUS if x != j)
                wd = {leg: w[leg] for leg in rem_minus + rem_plus}
                A4 = two_minus_over_i(wd, rem_minus, rem_plus)
                ratio = res / A4 if A4 != 0 else None
                rows.append((tuple(sorted((abs(w[k]) for k in MINUS))),
                             i, j, w[i], w[j], res, A4, ratio))
            break_after = True
    # print
    print(f"{'|w_minus| sorted':28} {'pair(i,j)':10} {'wi':>6} {'wj':>6} {'residue':>14} {'A4_2m':>12} {'ratio':>14}")
    seen = set()
    for (wm, i, j, wi, wj, res, A4, ratio) in rows:
        key = (wm, i, j, res)
        if key in seen:
            continue
        seen.add(key)
        print(f"{str(wm):28} ({i},{j})     {str(wi):>6} {str(wj):>6} {str(res):>14} {str(A4):>12} {str(ratio):>14}")
