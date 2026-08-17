#!/usr/bin/env python3
"""PI round-3 denominator hunt v2: robust, multi-line, rich candidate set.

For several sumFree-constant on-shell lines (so all omega_i are polynomials in t),
exact-rational-interpolate A_6(t)=N(t)/D(t), find the minimal denominator degree,
then identify the irreducible factors of D(t) by testing divisibility against a
RICH candidate library of omega-level polynomials evaluated along the line:
  - linear (omega_i +/- omega_j) and single legs omega_i
  - sum-of-squares (omega_i^2 + omega_j^2), Q
  - propagator denominators (omega_S^2 - |k_S|) for every subset S
The union of identified factors across lines maps out the true denominator.
Self-contained; my own ./bg only.
"""
import subprocess, re
from fractions import Fraction as F
from itertools import combinations

BG = "./bg"; SIG = [-1, -1, -1, 1, 1, 1]

def onshell(freeW):
    s0 = SIG[0]; sF = sum(freeW)
    sS = sum(SIG[i + 1] * freeW[i] ** 2 for i in range(4))
    wn = -(s0 * sF ** 2 + sS) / (2 * s0 * sF); w1 = -(sF + wn)
    W = [w1] + list(freeW) + [wn]; K = [SIG[i] * W[i] ** 2 for i in range(6)]
    return W, K

def amp(K, W):
    Ks = ",".join(str(F(k)) for k in K); Ws = ",".join(str(F(w)) for w in W)
    o = subprocess.run([BG, "--amp", "-K", Ks, "-W", Ws, "-g", "1"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if o.returncode != 0: return None
    m = re.search(r"A_\d+ = i \* \(([-0-9/]+)\)", o.stdout)
    if m: return F(m.group(1))
    m = re.search(r"A_\d+ = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)", o.stdout)
    if m: assert F(m.group(1)) == 0; return F(m.group(2))
    raise RuntimeError(o.stdout)

def nullvec(rows):
    M = [r[:] for r in rows]; nr = len(M); nc = len(M[0]); piv = []; r = 0
    for c in range(nc):
        pr = next((i for i in range(r, nr) if M[i][c] != 0), None)
        if pr is None: continue
        M[r], M[pr] = M[pr], M[r]; inv = M[r][c]; M[r] = [x / inv for x in M[r]]
        for i in range(nr):
            if i != r and M[i][c] != 0:
                f = M[i][c]; M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        piv.append(c); r += 1
        if r == nr: break
    fc = [c for c in range(nc) if c not in piv]
    if not fc: return None
    x = [F(0)] * nc; x[fc[0]] = F(1)
    for idx, c in enumerate(piv): x[c] = -M[idx][fc[0]]
    return x

def poly_eval(c, t): return sum(ci * t ** i for i, ci in enumerate(c))
def polytrim(c):
    c = c[:]
    while len(c) > 1 and c[-1] == 0: c.pop()
    return c
def divides(divisor, dividend):
    a = polytrim(dividend); b = polytrim(divisor)
    if len(b) == 1: return b[0] != 0
    while len(a) >= len(b):
        if a[-1] == 0: a.pop(); continue
        f = a[-1] / b[-1]; sh = len(a) - len(b)
        for i in range(len(b)): a[sh + i] -= f * b[i]
        a = polytrim(a)
        if a == [F(0)]: return True
    return a == [F(0)]

def rat_interp(ts, ys, dN, dD):
    rows = [[t ** i for i in range(dN + 1)] + [-y * t ** j for j in range(dD + 1)]
            for t, y in zip(ts, ys)]
    x = nullvec(rows)
    if x is None: return None
    N, D = x[:dN + 1], x[dN + 1:]
    if all(d == 0 for d in D): return None
    return N, D

def gather(base, direction, npts=70, denom=240):
    assert sum(direction) == 0
    pts = []; sig0 = None
    for k in range(-npts, npts + 1):
        t = F(k, denom); free = [base[i] + t * direction[i] for i in range(4)]
        W, K = onshell(free)
        if any(w == 0 for w in W): continue
        if any(sum(K[i] for i in S) == 0 for r in range(1, 6) for S in combinations(range(6), r)): continue
        cs = tuple(1 if sum(K[i] for i in S) > 0 else -1 for r in range(1, 6) for S in combinations(range(6), r)) \
             + tuple(1 if w > 0 else -1 for w in W)
        if sig0 is None: sig0 = cs
        if cs != sig0: continue
        a = amp(K, W)
        if a is None: continue
        pts.append((t, a))
    return pts

def cand_library(base, direction):
    """Return dict name -> polynomial-in-t coefficients (interpolated, exact)."""
    def freeof(t): return [base[i] + t * direction[i] for i in range(4)]
    def W_of(t): return onshell(freeof(t))[0]
    def K_of(t): return onshell(freeof(t))[1]
    def interp(fn, dmax=4):
        # find exact polynomial of minimal degree representing fn(t)
        for dg in range(0, dmax + 1):
            xs = [F(k, 240) for k in range(dg + 1)]
            A = [[x ** i for i in range(dg + 1)] for x in xs]; b = [fn(x) for x in xs]
            # gaussian solve
            M = [A[i][:] + [b[i]] for i in range(dg + 1)]
            ok = True
            for c in range(dg + 1):
                pr = next((i for i in range(c, dg + 1) if M[i][c] != 0), None)
                if pr is None: ok = False; break
                M[c], M[pr] = M[pr], M[c]; inv = M[c][c]; M[c] = [x / inv for x in M[c]]
                for i in range(dg + 1):
                    if i != c and M[i][c] != 0:
                        f = M[i][c]; M[i] = [u - f * v for u, v in zip(M[i], M[c])]
            if not ok: continue
            sol = [M[i][dg + 1] for i in range(dg + 1)]
            # verify at two extra points
            if all(poly_eval(sol, F(p, 240)) == fn(F(p, 240)) for p in (97, -53)):
                return polytrim(sol)
        return None
    lib = {}
    # linear omega_i +/- omega_j and single omega_i
    for i in range(6):
        lib[f"w{i+1}"] = interp(lambda t, i=i: W_of(t)[i])
    for i, j in combinations(range(6), 2):
        lib[f"w{i+1}+w{j+1}"] = interp(lambda t, i=i, j=j: W_of(t)[i] + W_of(t)[j])
        lib[f"w{i+1}-w{j+1}"] = interp(lambda t, i=i, j=j: W_of(t)[i] - W_of(t)[j])
    # sum of squares pairs (same type) and Q
    for i, j in [(3,4),(3,5),(4,5),(0,1),(0,2),(1,2)]:
        lib[f"w{i+1}^2+w{j+1}^2"] = interp(lambda t, i=i, j=j: W_of(t)[i]**2 + W_of(t)[j]**2)
    lib["Q"] = interp(lambda t: sum(W_of(t)[i]**2 for i in range(3, 6)))
    # propagator denominators for every subset 2<=|S|<=4
    for r in range(2, 5):
        for S in combinations(range(6), r):
            nm = "D_" + "".join(str(s+1) for s in S)
            lib[nm] = interp(lambda t, S=S: (sum(W_of(t)[s] for s in S))**2 - abs(sum(K_of(t)[s] for s in S)))
    return {k: v for k, v in lib.items() if v is not None and len(v) > 1}  # drop constants

def run_line(base, direction, tag):
    print("=" * 72)
    print(f"LINE {tag}: base={ [str(x) for x in base] }, dir={ [str(x) for x in direction] }, sumFree={sum(base)}")
    pts = gather(base, direction)
    print(f"  in-chamber points: {len(pts)}")
    if len(pts) < 30:
        print("  too few; skip"); return
    ts = [p[0] for p in pts]; ys = [p[1] for p in pts]
    found = None
    for dD in range(0, 14):
        dN = dD + 18; need = dN + dD + 2
        if len(pts) < need + 4: break
        res = rat_interp(ts[:need], ys[:need], dN, dD)
        if res is None: continue
        N, D = res
        if all(poly_eval(N, t) == y * poly_eval(D, t) for t, y in zip(ts[need:], ys[need:])):
            found = (N, D, dD, need); break
    if found is None:
        print("  no model found"); return
    N, D, dD, need = found
    Dt = polytrim(D)
    print(f"  minimal denominator degree dD = {dD}  (held-out verified on {len(pts)-need} pts)")
    lib = cand_library(base, direction)
    matched = []
    for nm, poly in sorted(lib.items()):
        if len(poly) - 1 <= dD and divides(poly, Dt):
            matched.append((nm, len(poly) - 1))
    print("  denominator factors identified (divide D(t)):")
    for nm, dg in matched:
        print(f"      {nm}   (deg {dg})")
    if not matched:
        print("      (none of the library matched -- denominator is something else)")
    # report leftover: divide D by all matched, see residual degree
    return Dt, matched

if __name__ == "__main__":
    lines = [
        ([F(2), F(3), F(5), F(7)],   [F(1), F(-1), F(1), F(-1)], "A"),
        ([F(2), F(3), F(5), F(7)],   [F(2), F(-1), F(-1), F(0)], "B"),
        ([F(3), F(11,2), F(4), F(9,2)], [F(1), F(1), F(-1), F(-1)], "C"),
        ([F(1), F(6), F(4), F(2)],   [F(0), F(1), F(0), F(-1)], "D"),
    ]
    for base, d, tag in lines:
        run_line(base, d, tag)
