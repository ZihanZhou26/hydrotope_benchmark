"""
Characterize analytic structure of a_5 (rule 6).
(A) Single-variable rational interpolation: fix w2=1,w3=2, vary w4=t; find N(t)/D(t).
(B) Test e2 = w1*w2 as denominator: is a_5*e2 a polynomial in (e1,e2,P3)?
"""
from fractions import Fraction as F
import sympy as sp
from bg import amp_two_minus, DegenerateKinematics

t = sp.symbols('t')


def a5_at_t(tt):
    fw = [F(1), F(2), F(tt)]  # w2=1, w3=2, w4=tt
    A, allW, allK = amp_two_minus(5, fw)
    assert A.re == 0
    return A.im, allW


print("=== (A) rational interpolation a_5(t), t=w4 ===")
# sample t in a sign-safe interval, rationals
samples = []
tt = F(5, 4)
while tt <= F(20, 4):
    try:
        a, allW = a5_at_t(tt)
        samples.append((tt, a))
    except (DegenerateKinematics, ZeroDivisionError):
        pass
    tt += F(1, 4)
print(f"  {len(samples)} samples for t in [5/4, 5]")


def rat_interp(samples, dN, dD):
    """Find N (deg dN), D (deg dD, D[0]=1) with a*D = N at all samples. Exact."""
    ncoef = (dN + 1) + dD  # N coeffs n0..ndN, D coeffs d1..ddD (d0=1)
    rows, rhs = [], []
    for (tt, a) in samples:
        ar = sp.Rational(a.numerator, a.denominator)
        tr = sp.Rational(tt.numerator, tt.denominator)
        # a*(1 + d1 t + ... ) = n0 + n1 t + ...
        # => n0 + n1 t + ... - a*d1 t - a*d2 t^2 - ... = a*1
        row = []
        for j in range(dN + 1):
            row.append(tr ** j)            # +n_j
        for j in range(1, dD + 1):
            row.append(-ar * tr ** j)      # -a d_j
        rows.append(row)
        rhs.append(ar)
    M = sp.Matrix(rows)
    b = sp.Matrix(rhs)
    try:
        sol, params = M.gauss_jordan_solve(b)
        if params.shape[0] != 0:
            return None  # underdetermined; need more constraints/diff degrees
        # verify
        if (M * sol - b) == sp.zeros(len(rhs), 1):
            Ncoef = list(sol[:dN + 1])
            Dcoef = [sp.Integer(1)] + list(sol[dN + 1:])
            return Ncoef, Dcoef
    except ValueError:
        return None
    return None


found = None
for total in range(2, 12):
    for dD in range(0, total + 1):
        dN = total - dD
        if len(samples) < (dN + 1) + dD + 2:
            continue
        # fit on all but last 3, verify on all
        res = rat_interp(samples, dN, dD)
        if res:
            Ncoef, Dcoef = res
            N = sum(c * t ** j for j, c in enumerate(Ncoef))
            D = sum(c * t ** j for j, c in enumerate(Dcoef))
            found = (dN, dD, sp.simplify(N), sp.simplify(D))
            break
    if found:
        break

if found:
    dN, dD, N, D = found
    print(f"  rational function found: degN={dN}, degD={dD}")
    print(f"  N(t) = {sp.factor(N)}")
    print(f"  D(t) = {sp.factor(D)}")
    print(f"  a_5(t) = [{sp.factor(N)}] / [{sp.factor(D)}]")
    print(f"  poles (roots of D): {sp.roots(D, t)}")
else:
    print("  no rational function up to degree 11 — possible non-analyticity in this window")

print("\n=== (B) is a_5 * e2 a polynomial of degree 8 in (e1,e2,P3)? ===")
import random
from fit_poly import surface_coords, var_list


def monomials_deg(n, D):
    vs = var_list(n)
    degs = [d for _, d in vs]
    res = []

    def rec(i, rem, cur):
        if i == len(degs):
            if rem == 0:
                res.append(tuple(cur))
            return
        d = degs[i]
        e = 0
        while d * e <= rem:
            rec(i + 1, rem - d * e, cur + [e])
            e += 1
    rec(0, D, [])
    return vs, res


def collect(n, npts, rng, scale=6):
    pts = []
    tries = 0
    while len(pts) < npts and tries < npts * 60:
        tries += 1
        fw = [F(rng.randint(-scale, scale) or 1, rng.randint(1, 3)) for _ in range(n - 2)]
        try:
            A, allW, allK = amp_two_minus(n, fw)
        except (DegenerateKinematics, ZeroDivisionError):
            continue
        if A.re != 0:
            continue
        pts.append((fw, allW, A.im, surface_coords(n, allW)))
    return pts


rng = random.Random(7)
vs, monos = monomials_deg(5, 8)
pts = collect(5, len(monos) + 20, rng)
rows, rhs = [], []
for (_, allW, a, c) in pts:
    e2 = c["e2"]
    b = a * e2  # a_5 * e2
    rows.append([sp.Rational((mv := __import__('functools').reduce(lambda x, ke: x * c[ke[0]] ** ke[1], [(vn, e) for (vn, _), e in zip(vs, mexp) if e], F(1))).numerator, mv.denominator) for mexp in monos])
    rhs.append(sp.Rational(b.numerator, b.denominator))
M = sp.Matrix(rows)
bb = sp.Matrix(rhs)
try:
    sol, params = M.gauss_jordan_solve(bb)
    consistent = (M * sol - bb) == sp.zeros(len(rhs), 1)
    print(f"  #monomials(deg8)={len(monos)}, points={len(pts)}, consistent={consistent}, free params={params.shape[0]}")
except ValueError:
    print(f"  a_5*e2 is NOT a degree-8 polynomial (inconsistent) -> e2 alone is not the denominator")
