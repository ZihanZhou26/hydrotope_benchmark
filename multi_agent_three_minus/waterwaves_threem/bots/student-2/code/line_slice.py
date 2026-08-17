#!/usr/bin/env python3
"""Exact on-shell LINE slices: omega(t) = p + t v, all six frequencies linear in
t and exactly on-shell, so C_6(t) is an exact degree-<=8 polynomial.

Need: sum v = 0, q(v)=0 (q = sum sigma_i x_i^2), and <p,v>_q = 0 with p on-shell.
Then q(p+tv)=0 and sum=0 for all t. Sample C_6(t) via raw --amp and interpolate.
"""
import subprocess, re, os, itertools, random
from fractions import Fraction as F
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__)); BG = os.path.join(HERE, "bg")
SIG = [-1, -1, -1, 1, 1, 1]


def q(x):
    return sum(F(SIG[i]) * x[i] ** 2 for i in range(6))


def qbil(a, b):
    return sum(F(SIG[i]) * a[i] * b[i] for i in range(6))


def amp_raw(W):
    K = [F(SIG[i]) * W[i] ** 2 for i in range(6)]
    cmd = [BG, "--amp", "-K", ",".join(str(x) for x in K), "-W", ",".join(str(x) for x in W)]
    out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
    m = re.search(r"A_6 = i \* \(([-0-9/]+)\)", out)
    if m:
        return F(m.group(1))
    m = re.search(r"A_6 = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)", out)
    return F(m.group(2))  # imaginary part


def find_basepoint(v, rng=6, tries=200000):
    """Find rational p: sum p=0, q(p)=0, <p,v>_q=0 by structured search.
    Free: p1,p2,p4,p5 from two linear eqs solve p3,p6; then need q(p)=0."""
    # linear constraints: sum p = 0 ; <p,v>_q=0
    # choose p1,p2,p4,p5,p3 free-ish and solve. Easiest: random integer search.
    for _ in range(tries):
        p = [F(random.randint(-rng, rng)) for _ in range(6)]
        # enforce sum=0 by fixing p6 = -(sum others)
        p[5] = -sum(p[:5])
        # enforce <p,v>_q = 0 by adjusting p3 if v has p3 component, else skip
        # solve <p,v>_q=0 for p3 if v[2]!=0 else p6 already set; general: pick p2 to fix
        # Instead just check both constraints approx and require exact 0 via search:
        if q(p) == 0 and qbil(p, v) == 0 and sum(p) == 0 and all(x != 0 for x in p):
            return p
    return None


def construct_basepoint(v):
    """Deterministic construction: parametrize p, solve constraints with sympy."""
    a, b, c, d = sp.symbols("a b c d")
    # p = (a, b, c, d, e, f); sum=0 -> f = -(a+b+c+d+e); pick e free too -> use 5 syms
    e = sp.Symbol("e")
    f = -(a + b + c + d + e)
    p = [a, b, c, d, e, f]
    eq1 = sum(sp.Integer(SIG[i]) * p[i] * v[i] for i in range(6))   # <p,v>_q=0 (linear)
    eq2 = sum(sp.Integer(SIG[i]) * p[i] ** 2 for i in range(6))      # q(p)=0 (quadratic)
    # solve eq1 for e (linear), substitute, then eq2 for d (quadratic, pick rational root)
    sol_e = sp.solve(eq1, e)
    if not sol_e:
        return None
    esub = sol_e[0]
    eq2b = eq2.subs(e, esub)
    # set a,b,c to rationals, solve eq2b for d
    for (av, bv, cv) in [(1, 2, 3), (2, 1, 4), (1, 3, 2), (3, 1, 2), (2, 3, 1), (1, 2, 5)]:
        e2 = eq2b.subs({a: av, b: bv, c: cv})
        ds = sp.solve(e2, d)
        for dval in ds:
            if dval.is_rational:
                eval_ = esub.subs({a: av, b: bv, c: cv, d: dval})
                pp = [F(int(sp.numer(x)), int(sp.denom(x))) for x in
                      [sp.Rational(av), sp.Rational(bv), sp.Rational(cv), sp.Rational(dval),
                       sp.Rational(eval_), sp.Rational(-(av + bv + cv + dval + eval_))]]
                if q(pp) == 0 and qbil(pp, v) == 0 and sum(pp) == 0 and all(x != 0 for x in pp):
                    return pp
    return None


def slice_poly(p, v, ts):
    pts = []
    for t in ts:
        W = [p[i] + t * v[i] for i in range(6)]
        if any(w == 0 for w in W):
            continue
        try:
            A = amp_raw(W)
        except subprocess.CalledProcessError:
            continue  # hit a wall
        pts.append((t, F(A, 32)))   # C = A/i/32
    T = sp.Symbol("t")
    sp_pts = [(sp.Rational(t.numerator, t.denominator), sp.Rational(c.numerator, c.denominator)) for t, c in pts]
    poly = sp.expand(sp.interpolate(sp_pts, T))
    return poly, pts


def random_cone_dir(rng=5, tries=200000):
    """random integer v: sum v=0, q(v)=0, and no v_i = +-v_j across minus/plus
    (avoids lines lying identically on a |k_S|=0 wall)."""
    for _ in range(tries):
        v = [random.randint(-rng, rng) for _ in range(6)]
        if sum(v) != 0:
            continue
        if -v[0]**2 - v[1]**2 - v[2]**2 + v[3]**2 + v[4]**2 + v[5]**2 != 0:
            continue
        if any(v[i] == 0 for i in range(6)):
            # allow at most... actually allow zeros but require nondegeneracy below
            pass
        # reject obvious wall lines: minus leg identically +- plus leg
        bad = False
        for i in [0, 1, 2]:
            for j in [3, 4, 5]:
                if abs(v[i]) == abs(v[j]) and v[i] != 0:
                    bad = True
        if bad:
            continue
        if all(x == 0 for x in v):
            continue
        return [F(x) for x in v]
    return None


def line_ok(p, v, ts):
    """check the oracle works (no identical-wall) at >=6 of the ts."""
    good = 0
    for t in ts:
        W = [p[i] + t * v[i] for i in range(6)]
        if any(w == 0 for w in W):
            continue
        try:
            amp_raw(W); good += 1
        except subprocess.CalledProcessError:
            continue
    return good


if __name__ == "__main__":
    random.seed(7)
    ts = [F(k, 5) for k in range(-5, 7)]
    found = 0
    attempts = 0
    while found < 3 and attempts < 60:
        attempts += 1
        v = random_cone_dir()
        if v is None:
            break
        p = construct_basepoint(v)
        if p is None:
            continue
        if line_ok(p, v, ts) < 7:
            continue
        poly, pts = slice_poly(p, v, ts)
        T = sp.Symbol("t")
        deg = sp.degree(sp.Poly(poly, T)) if poly != 0 else 0
        print(f"\nv={[int(x) for x in v]}  p={[str(x) for x in p]}")
        print(f" usable pts={len(pts)}  deg={deg}")
        print(" C_6(t) =", poly)
        found += 1
