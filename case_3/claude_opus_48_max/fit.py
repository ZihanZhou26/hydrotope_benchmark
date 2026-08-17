#!/usr/bin/env python3
"""Fit A_n = -i R_n in the two-minus sector as a symmetric polynomial.
Variables: minus group {w0,w1}, plus group {w2..w_{n-1}} (0-indexed).
Generators (after using constraints sum w=0, sum sigma w^2=0):
  m1 = w0+w1, m2 = w0^2+w1^2, P3..P_{n-2} = power sums of plus group.
R_n is homogeneous of degree 2n-4.
"""
import sys, re
from fractions import Fraction as Fr
from itertools import product
import sympy as sp

def parse(path):
    rows = []
    for line in open(path):
        line = line.strip()
        if not line or '|' not in line:
            continue
        n_s, w_s, a_s = [x.strip() for x in line.split('|')]
        n = int(n_s)
        ws = [Fr(x) for x in re.findall(r'-?\d+(?:/\d+)?', w_s)]
        # amplitude like  -3328*I  or  (-58880*I)/13
        a_clean = a_s.replace('*I','').replace('I','')
        a_clean = a_clean.replace('(', '').replace(')', '')
        # now like -3328  or -58880/13
        coeffI = Fr(a_clean) if a_clean not in ('','-','+') else Fr(1)
        rows.append((n, ws, coeffI))   # A = coeffI * I
    return rows

def generators(n, ws):
    """Return dict of generator value: m1,m2,P3..P_{n-2}."""
    minus = ws[:2]; plus = ws[2:]
    g = {}
    g['m1'] = sum(minus)
    g['m2'] = sum(x*x for x in minus)
    for j in range(3, n-1):  # P3 .. P_{n-2}
        g['P%d'%j] = sum(x**j for x in plus)
    return g

def gen_degrees(n):
    d = {'m1':1, 'm2':2}
    for j in range(3, n-1):
        d['P%d'%j] = j
    return d

def basis_exponents(n, total_deg):
    """All monomials (exponent tuples over generators) of given total degree."""
    degs = gen_degrees(n)
    names = list(degs.keys())
    dlist = [degs[k] for k in names]
    # bounded search
    maxes = [total_deg//d for d in dlist]
    res = []
    for combo in product(*[range(m+1) for m in maxes]):
        if sum(e*d for e,d in zip(combo, dlist)) == total_deg:
            res.append(combo)
    return names, res

def fit_n(rows, n, verbose=True):
    data = [(ws,c) for (nn,ws,c) in rows if nn==n]
    if not data:
        return None
    deg = 2*n-4
    names, exps = basis_exponents(n, deg)
    if verbose:
        print(f"--- n={n}: {len(data)} points, {len(exps)} basis monomials (deg {deg}) ---")
    # Build matrix M (points x monomials) and vector b
    M = []; b = []
    for ws,c in data:
        g = generators(n, ws)
        gv = [g[name] for name in names]
        row = []
        for e in exps:
            val = sp.Integer(1)
            for gi, ei in zip(gv, e):
                val *= sp.Rational(gi.numerator, gi.denominator)**ei
            row.append(val)
        M.append(row)
        b.append(sp.Rational(c.numerator, c.denominator))
    Mm = sp.Matrix(M); bb = sp.Matrix(b)
    # solve least-norm exact: use Mm.T Mm? Better: solve exactly if consistent.
    aug = Mm.row_join(bb)
    # Find a particular solution via reduced row echelon on transposed system
    # Solve Mm x = bb (overdetermined). Check consistency.
    sol = None
    try:
        # Use sympy linsolve
        syms = sp.symbols('c0:%d'%len(exps))
        eqs = [sum(Mm[i,j]*syms[j] for j in range(len(exps))) - bb[i] for i in range(len(data))]
        solset = sp.linsolve(eqs, syms)
        if solset:
            sol = list(solset)[0]
    except Exception as ex:
        print("solve err", ex)
    if sol is None:
        print(f"  n={n}: NO consistent polynomial solution found.")
        return None
    # Check it's fully determined (no free params) and verify
    free = [s for s in sol if s.free_symbols]
    coeffs = {}
    for name_e, val in zip(exps, sol):
        if val != 0:
            coeffs[name_e] = val
    # verify on all points
    ok = True
    for ws,c in data:
        g = generators(n, ws)
        gv = {name:sp.Rational(g[name].numerator,g[name].denominator) for name in names}
        tot = sp.Integer(0)
        for e,val in zip(exps, sol):
            term = val
            for nm,ei in zip(names,e):
                term *= gv[nm]**ei
            tot += term
        if sp.simplify(tot - sp.Rational(c.numerator,c.denominator)) != 0:
            ok = False
    print(f"  n={n}: consistent={sol is not None}, free params={len(free)>0 and 'YES' or 'no'}, verifies={ok}")
    print(f"  nonzero coeffs ({len([v for v in sol if v!=0])}):")
    for e,val in zip(exps, sol):
        if val != 0:
            mon = '*'.join('%s^%d'%(nm,ei) for nm,ei in zip(names,e) if ei>0) or '1'
            print(f"      {val}   *  {mon}")
    return names, exps, sol

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv)>1 else 'data.txt'
    rows = parse(path)
    print("total rows:", len(rows))
    from collections import Counter
    print("per n:", dict(Counter(n for n,_,_ in rows)))
    for n in sorted(set(n for n,_,_ in rows)):
        fit_n(rows, n)
        print()
