#!/usr/bin/env python3
"""PI round-6 phase 2: extract & FACTOR the in-piece denominator Q of
h = H/omega2^2 = P(x,y,z)/Q(x,y,z), from the points collected by
round6_reconstruct.py, at the minimal degree d found by the rank scan.

Steps:
  1. load round6_points.json (exact Fractions x,y,z,h).
  2. at degree d, build [M_{<=d} | -h M_{<=d}] mod P=2^61-1 over ncol+extra rows;
     compute the null space; require nulldim==1 (unique reduced rep).
  3. rational-reconstruct P,Q coefficients from the modular null vector.
  4. EXACT VALIDATION: on all remaining (held-out) points, check h == P/Q with
     exact Fraction arithmetic.  Only then trust it.
  5. sympy.factor(Q) and factor(P); print building blocks.
Usage: round6_extract.py <d> [rows]
"""
import json, sys
from fractions import Fraction as F
import sympy as sp

P = (1 << 61) - 1


def monos_upto(d):
    out = []
    for a in range(d + 1):
        for b in range(d + 1 - a):
            for c in range(d + 1 - a - b):
                out.append((a, b, c))
    return out


def to_mod(fr):
    return (fr.numerator % P) * pow(fr.denominator % P, P - 2, P) % P


def rat_recon(u, p, bound=None):
    """recover num/den with |num|,den <= sqrt(p/2) and num == u*den (mod p)."""
    if bound is None:
        bound = int((p // 2) ** 0.5)
    r0, r1 = p, u % p
    s0, s1 = 0, 1
    while r1 > bound:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
    num, den = r1, s1
    if den < 0:
        num, den = -num, -den
    if den == 0 or den > bound:
        return None
    return F(num, den)


def nullspace_mod(rows, ncol):
    R = [r[:] for r in rows]
    m = len(R)
    pivcol = {}
    rank = 0
    for col in range(ncol):
        pr = None
        for r in range(rank, m):
            if R[r][col] % P:
                pr = r; break
        if pr is None:
            continue
        R[rank], R[pr] = R[pr], R[rank]
        inv = pow(R[rank][col], P - 2, P)
        R[rank] = [(x * inv) % P for x in R[rank]]
        for r in range(m):
            if r != rank and R[r][col] % P:
                fac = R[r][col]
                R[r] = [(R[r][c] - fac * R[rank][c]) % P for c in range(ncol)]
        pivcol[col] = rank
        rank += 1
        if rank == m:
            break
    free = [c for c in range(ncol) if c not in pivcol]
    basis = []
    for fc in free:
        vec = [0] * ncol
        vec[fc] = 1
        for col, r in pivcol.items():
            vec[col] = (-R[r][fc]) % P
        basis.append(vec)
    return basis, rank, free


def main():
    d = int(sys.argv[1])
    extra_rows = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    data = json.load(open("round6_points.json"))
    pts = [tuple(F(a) for a in row) for row in data["pts"]]
    mon = monos_upto(d); nm = len(mon); ncol = 2 * nm
    print(f"d={d}, |mon|={nm}, ncol={ncol}, points={len(pts)}")

    nfit = min(len(pts), ncol + extra_rows)
    fit_pts = pts[:nfit]; hold_pts = pts[nfit:]

    rows = []
    for (x, y, z, h) in fit_pts:
        xm, ym, zm, hm = to_mod(x), to_mod(y), to_mod(z), to_mod(h)
        mv = [pow(xm, a, P) * pow(ym, b, P) % P * pow(zm, c, P) % P for (a, b, c) in mon]
        rows.append(mv + [(-hm * v) % P for v in mv])

    basis, rank, free = nullspace_mod(rows, ncol)
    print(f"nullspace dim = {len(basis)} (rank {rank}/{ncol})")
    if len(basis) == 0:
        print("NO null vector at this degree/rows; increase d."); return
    if len(basis) > 1:
        print(f"WARNING nulldim={len(basis)}>1; taking first, but rep may be non-reduced.")

    vec = basis[0]
    # split into Q (denominator) and P (numerator) coefficient residues
    pc = vec[:nm]; qc = vec[nm:]
    # normalize by first nonzero q coefficient
    piv = next(i for i, v in enumerate(qc) if v % P)
    inv = pow(qc[piv], P - 2, P)
    pc = [(v * inv) % P for v in pc]
    qc = [(v * inv) % P for v in qc]

    def recon_list(cs):
        out = []
        for v in cs:
            fr = rat_recon(v, P)
            if fr is None:
                return None
            out.append(fr)
        return out

    Pc = recon_list(pc); Qc = recon_list(qc)
    if Pc is None or Qc is None:
        print("rational reconstruction FAILED (coeff height too large); "
              "need CRT over more primes."); return

    x, y, z = sp.symbols('x y z')
    def build(coeffs):
        e = sp.Integer(0)
        for cf, (a, b, c) in zip(coeffs, mon):
            if cf != 0:
                e += sp.Rational(cf.numerator, cf.denominator) * x**a * y**b * z**c
        return sp.expand(e)
    Ppoly = build(Pc); Qpoly = build(Qc)

    # EXACT validation on held-out points
    Pl = sp.lambdify((x, y, z), Ppoly, 'sympy')
    Ql = sp.lambdify((x, y, z), Qpoly, 'sympy')
    bad = 0; checked = 0
    for (xx, yy, zz, hh) in hold_pts:
        qv = Ql(sp.Rational(xx.numerator, xx.denominator),
                sp.Rational(yy.numerator, yy.denominator),
                sp.Rational(zz.numerator, zz.denominator))
        pv = Pl(sp.Rational(xx.numerator, xx.denominator),
                sp.Rational(yy.numerator, yy.denominator),
                sp.Rational(zz.numerator, zz.denominator))
        if qv == 0:
            continue
        checked += 1
        if sp.Rational(pv, qv) != sp.Rational(hh.numerator, hh.denominator):
            bad += 1
    print(f"EXACT holdout validation: {checked-bad}/{checked} pass "
          f"(0 bad required); bad={bad}")

    print("\n=== deg Q =", sp.total_degree(Qpoly), ", deg P =", sp.total_degree(Ppoly), "===")
    print("\n--- factor(Q) ---")
    print(sp.factor(Qpoly))
    print("\n--- factor(P) ---")
    print(sp.factor(Ppoly))
    with open("round6_QP.txt", "w") as fh:
        fh.write("Q = " + str(Qpoly) + "\n\nfactor(Q) = " + str(sp.factor(Qpoly)) +
                 "\n\nP = " + str(Ppoly) + "\n\nfactor(P) = " + str(sp.factor(Ppoly)) + "\n")
    print("\nwrote round6_QP.txt")


if __name__ == "__main__":
    main()
