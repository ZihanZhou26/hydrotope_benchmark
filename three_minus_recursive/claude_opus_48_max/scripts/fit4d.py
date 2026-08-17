"""Full canonical-chamber fit: P = B * D_param as symmetric polynomial in
e1=w2+w3, e2=w2*w3, f1=w4+w5, f2=w4*w5. D_param = s*(w2+w4)(w2+w5)(w3+w4)(w3+w5)."""
import sympy as sp
from fractions import Fraction as Fr
import harness, chamber
sigma = [-1, -1, -1, 1, 1, 1]


def Bval(fw):
    return harness.onshell(6, fw, sigma)['A_im']


def Dparam(w2, w3, w4, w5):
    s = w2 + w3 + w4 + w5
    return s * (w2 + w4) * (w2 + w5) * (w3 + w4) * (w3 + w5)


def solve_exact(A, b):
    rows = [row[:] + [b[i]] for i, row in enumerate(A)]
    m = len(A[0])
    piv = []
    r = 0
    for c in range(m):
        sel = next((i for i in range(r, len(rows)) if rows[i][c] != 0), None)
        if sel is None:
            continue
        rows[r], rows[sel] = rows[sel], rows[r]
        inv = Fr(1) / rows[r][c]
        rows[r] = [v * inv for v in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c] != 0:
                f = rows[i][c]
                rows[i] = [a - f * b2 for a, b2 in zip(rows[i], rows[r])]
        piv.append(c)
        r += 1
        if r == m:
            break
    for i in range(r, len(rows)):
        if rows[i][m] != 0 and all(v == 0 for v in rows[i][:m]):
            return None, 'inconsistent'
    sol = {c: rows[i][m] for i, c in enumerate(piv)}
    return [sol.get(c, Fr(0)) for c in range(m)], 'ok'


# find single-chamber 4-var box around (2,3,5,4)
center = [Fr(2), Fr(3), Fr(5), Fr(4)]
half = None
for h in [Fr(2, 10), Fr(15, 100), Fr(1, 10), Fr(1, 20)]:
    ok, sgn, pts = chamber.box_single_chamber(center, [0, 1, 2, 3], h, 3)
    if ok:
        half = h
        break
print("single-chamber 4-var box half =", float(half) if half else None)

# sample points in the box (rational grid), staying single chamber
import itertools
axes = [[center[d] - half + 2 * half * Fr(k, 6) for k in range(7)] for d in range(4)]
pts = []
rng_pts = list(itertools.product(*axes))
for combo in rng_pts:
    fw = list(combo)
    # keep ordering distinct to avoid accidental walls
    try:
        om = chamber.onshell_omega(fw)
        if 0 in chamber.signature(om):
            continue
        B = Bval(fw)
        pts.append((fw, B))
    except Exception:
        pass
print("sample points:", len(pts))

# symmetric monomial basis in (e1,e2,f1,f2), weighted degree 13
e1, e2, f1, f2 = sp.symbols('e1 e2 f1 f2')
monos = []
for b in range(7):
    for d in range(7):
        rem = 13 - 2 * b - 2 * d
        if rem < 0:
            continue
        for a in range(rem + 1):
            c = rem - a
            monos.append((a, b, c, d))
print("monomials:", len(monos))

A = []
bb = []
for (fw, B) in pts:
    w2, w3, w4, w5 = fw
    E1, E2, F1, F2 = w2 + w3, w2 * w3, w4 + w5, w4 * w5
    P = B * Dparam(w2, w3, w4, w5)
    A.append([E1 ** a * E2 ** b * F1 ** c * F2 ** d for (a, b, c, d) in monos])
    bb.append(P)
sol, stat = solve_exact(A[:len(monos) + 5], bb[:len(monos) + 5])
print("fit status:", stat)
if sol:
    P = sum(sol[k] * e1 ** monos[k][0] * e2 ** monos[k][1] * f1 ** monos[k][2] * f2 ** monos[k][3]
            for k in range(len(monos)))
    # validate on all points
    bad = 0
    for (fw, B) in pts:
        w2, w3, w4, w5 = fw
        subs = {e1: w2 + w3, e2: w2 * w3, f1: w4 + w5, f2: w4 * w5}
        Pv = Fr(int(sp.Integer(sp.nsimplify(P.subs(subs))))) if False else P.subs(subs)
        if sp.nsimplify(Pv) != sp.Rational(Fr(B * Dparam(w2, w3, w4, w5)).numerator,
                                            Fr(B * Dparam(w2, w3, w4, w5)).denominator):
            bad += 1
    print("validation mismatches:", bad, "/", len(pts))
    print("P(e1,e2,f1,f2) =")
    sp.pprint(sp.factor(P))
