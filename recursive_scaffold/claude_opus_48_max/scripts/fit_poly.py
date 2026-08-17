"""
Fit a_n = Im(A_n) as a homogeneous symmetric polynomial in surface coordinates
  e1 = w1+w2 (deg1), e2 = w1*w2 (deg2)  [minus pair]
  P3..P_{n-2} = plus power sums (deg j)   [independent plus invariants]
total weighted degree D = 2n-4.  Exact rational linear algebra, held-out validation.
"""
import sys, random
from fractions import Fraction as F
import sympy as sp
from bg import amp_two_minus, DegenerateKinematics


def surface_coords(n, allW):
    """Return dict of coordinate values: e1,e2,P3..P_{n-2} (as Fractions)."""
    w1, w2 = allW[0], allW[1]
    plus = allW[2:]
    coords = {"e1": w1 + w2, "e2": w1 * w2}
    for j in range(3, n - 1):  # P3 .. P_{n-2}
        coords[f"P{j}"] = sum(w ** j for w in plus)
    return coords


def var_list(n):
    """variable names with weighted degrees: e1=1,e2=2,P3=3,...,P_{n-2}=n-2."""
    vs = [("e1", 1), ("e2", 2)]
    for j in range(3, n - 1):
        vs.append((f"P{j}", j))
    return vs


def monomials(n):
    """All exponent tuples over var_list(n) with weighted degree = 2n-4."""
    vs = var_list(n)
    D = 2 * n - 4
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


def gen_free(n, rng, scale=6):
    """Random rational free-frequency vector of length n-2."""
    out = []
    for _ in range(n - 2):
        num = rng.randint(-scale, scale)
        den = rng.randint(1, 3)
        if num == 0:
            num = 1
        out.append(F(num, den))
    return out


def collect(n, npts, rng, scale=6):
    pts = []
    tries = 0
    while len(pts) < npts and tries < npts * 50:
        tries += 1
        fw = gen_free(n, rng, scale)
        try:
            A, allW, allK = amp_two_minus(n, fw)
        except (DegenerateKinematics, ZeroDivisionError):
            continue
        if A.re != 0:
            continue
        c = surface_coords(n, allW)
        pts.append((fw, allW, A.im, c))
    return pts


def fit(n, seed=1):
    rng = random.Random(seed)
    vs, monos = monomials(n)
    nmono = len(monos)
    print(f"n={n}: D={2*n-4}, vars={[v for v,_ in vs]}, #monomials={nmono}")
    # collect more than enough points
    pts = collect(n, nmono + 25, rng)
    print(f"  collected {len(pts)} non-degenerate points")
    varnames = [v for v, _ in vs]

    def row(coords):
        r = []
        for mexp in monos:
            val = F(1)
            for (vn, _), e in zip(vs, mexp):
                if e:
                    val *= coords[vn] ** e
            r.append(val)
        return r

    # build full design matrix and rhs
    M = sp.Matrix([[sp.Rational(x.numerator, x.denominator) for x in row(c)]
                   for (_, _, _, c) in pts])
    b = sp.Matrix([sp.Rational(a.numerator, a.denominator) for (_, _, a, _) in pts])
    # solve least-squares exactly via normal equations on a full-rank subset
    sol, params = M.gauss_jordan_solve(b)
    if params.shape[0] != 0:
        print("  WARNING: solution not unique (free params). Using particular solution.")
    coeffs = list(sol)
    # verify residual on ALL collected points
    resid = M * sp.Matrix(coeffs) - b
    allzero = all(r == 0 for r in resid)
    print(f"  residual all-zero on {len(pts)} fit points: {allzero}")

    # pretty print
    print("  fitted a_n =")
    terms = []
    for mexp, cf in zip(monos, coeffs):
        if cf == 0:
            continue
        mon = "*".join(f"{vn}^{e}" if e > 1 else vn
                        for (vn, _), e in zip(vs, mexp) if e)
        mon = mon if mon else "1"
        terms.append(f"({cf})*{mon}")
    print("    " + " + ".join(terms))
    return vs, monos, coeffs, allzero


def validate(n, vs, monos, coeffs, seed=999, npts=25):
    rng = random.Random(seed)
    pts = collect(n, npts, rng, scale=9)
    ok = 0
    for (fw, allW, a, c) in pts:
        val = F(0)
        for mexp, cf in zip(monos, coeffs):
            term = F(cf.p, cf.q)
            for (vn, _), e in zip(vs, mexp):
                if e:
                    term *= c[vn] ** e
            val += term
        if val == a:
            ok += 1
        else:
            print(f"  MISMATCH fw={[str(x) for x in fw]}: fit={val} oracle={a}")
    print(f"  held-out validation: {ok}/{len(pts)} exact matches")
    return ok == len(pts)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    vs, monos, coeffs, ok = fit(n)
    if ok:
        validate(n, vs, monos, coeffs)
