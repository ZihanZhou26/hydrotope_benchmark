"""fit.py — fit a_n on-shell to a SYMMETRIC polynomial in the natural building blocks:
   s   = omega_1+omega_2        (minus-pair power sum, deg 1)
   p   = omega_1*omega_2        (minus-pair product,   deg 2)
   E3..E_{n-2} = elementary symmetric polys of the plus legs {omega_3..omega_n} (deg k)
On-shell, E1(plus) = -s and E2(plus) = p are forced, so the independent blocks are
{s, p, E3,...,E_{n-2}}.  a_n is homogeneous of degree 2n-4.
"""
import sys, itertools, random
from fractions import Fraction as F
import sympy as sp
from engine import build_onshell, Engine


def elem_sym(vals, k):
    if k == 0: return F(1)
    return sum((F(1)*__import__('math').prod(c) for c in itertools.combinations(vals, k)), F(0))


def plus_elems(omega, N):
    plus = [omega[i] for i in range(3, N+1)]   # legs 3..N
    return plus


def basis_degrees(N):
    # variable degrees: s:1, p:2, E3:3,...,E_{N-2}:(N-2)
    degs = [1, 2] + list(range(3, (N-2)+1))   # for N=4 -> [1,2]; N=5 -> [1,2,3]
    names = ['s', 'p'] + [f'E{k}' for k in range(3, (N-2)+1)]
    return degs, names


def monomials(N):
    degs, names = basis_degrees(N)
    D = 2*N - 4
    mons = []
    # exponents e_i >=0 with sum e_i*deg_i = D
    ranges = [range(0, D//degs[i] + 1) for i in range(len(degs))]
    for exps in itertools.product(*ranges):
        if sum(exps[i]*degs[i] for i in range(len(degs))) == D:
            mons.append(exps)
    return mons, degs, names


def eval_blocks(N, omega):
    s = omega[1] + omega[2]
    p = omega[1] * omega[2]
    plus = [omega[i] for i in range(3, N+1)]
    Es = [elem_sym(plus, k) for k in range(3, (N-2)+1)]
    return [s, p] + Es


def amp_value(N, free_w):
    sigma = [-1, -1] + [1]*(N-2)
    W, K = build_onshell(N, free_w, sigma)
    E = Engine('frac')
    re, im = E.BGAmplitude(N, K, W)
    assert re == 0
    omega = {i: W[i] for i in range(1, N+1)}
    return im, omega


def random_freevec(N, rng):
    # N-2 free freqs; keep them distinct positive-ish rationals, generic
    out = []
    used = set()
    while len(out) < N-2:
        num = rng.randint(1, 30); den = rng.randint(1, 7)
        v = F(num, den)
        if v not in used and v != 0:
            used.add(v); out.append(v)
    return out


def run_fit(N, npts=None, seed=12345):
    mons, degs, names = monomials(N)
    nb = len(mons)
    if npts is None: npts = nb + 8
    rng = random.Random(seed)
    rows = []; rhs = []; pts = []
    tries = 0
    while len(rows) < npts and tries < 4000:
        tries += 1
        fw = random_freevec(N, rng)
        try:
            a, omega = amp_value(N, fw)
        except Exception:
            continue
        blocks = eval_blocks(N, omega)  # [s,p,E3,...]
        row = []
        for exps in mons:
            term = F(1)
            for i, e in enumerate(exps):
                term *= blocks[i]**e
            row.append(term)
        rows.append(row); rhs.append(a); pts.append((fw, omega, a))
    # solve least-squares exact via sympy rational linear solve (use first nb independent rows)
    Mt = sp.Matrix([[sp.Rational(x.numerator, x.denominator) for x in r] for r in rows])
    bt = sp.Matrix([sp.Rational(x.numerator, x.denominator) for x in rhs])
    # solve Mt c = bt in least squares / exact sense
    sol, params = Mt.gauss_jordan_solve(bt)
    coeffs = {}
    for i, exps in enumerate(mons):
        c = sol[i]
        if c != 0:
            coeffs[exps] = c
    return coeffs, names, degs, mons, pts


def pretty(coeffs, names):
    syms = sp.symbols(names)
    expr = 0
    for exps, c in coeffs.items():
        term = c
        for i, e in enumerate(exps):
            term *= syms[i]**e
        expr += term
    return sp.expand(expr), syms


if __name__ == '__main__':
    N = int(sys.argv[1])
    coeffs, names, degs, mons, pts = run_fit(N)
    expr, syms = pretty(coeffs, names)
    print(f"n={N}: fitted symmetric a_n in blocks {names} (degrees {degs}), target degree {2*N-4}")
    print("  #basis monomials:", len(mons), " #points:", len(pts))
    print("\na_n =")
    sp.pprint(expr)
    print("\nas string:", expr)
    # verify on a few held-out random points
    rng = random.Random(999)
    print("\nhold-out verification:")
    ok = True
    for _ in range(6):
        fw = random_freevec(N, rng)
        a, omega = amp_value(N, fw)
        blocks = eval_blocks(N, omega)
        val = expr.subs({syms[i]: sp.Rational(blocks[i].numerator, blocks[i].denominator) for i in range(len(syms))})
        match = (sp.Rational(a.numerator, a.denominator) == val)
        ok = ok and match
        print(f"  fw={fw}: oracle={a}  fit={val}  {'OK' if match else 'MISMATCH'}")
    print("ALL OK" if ok else "SOME MISMATCH")
