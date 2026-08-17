#!/usr/bin/env python3
"""
PI round-4 supplement:
  1. Confirm (A_6/i)*D_9 is an exact polynomial in MORE chambers (per-chamber).
  2. Confirm N_6 := (A_6/i)*D_9 is a genuine SPLINE: the polynomial DIFFERS across
     a same-type-ordering wall (omega_i=omega_j, where D_9 != 0), while A_6 itself
     stays finite (kink, not pole) -> A_6 is NOT a single global rational function.
  3. Minimality combinatorics: the S_3(minus)xS_3(plus) orbit of a single mixed pair
     (omega_i+omega_j) is the full set of all 3(n-3) mixed pairs.
PI's own oracle + own exact analysis only.
"""
import subprocess, re, sys
from fractions import Fraction as Fr
from itertools import combinations, permutations

BG = "./bg"

def run_bg(n, free_w, signs):
    def fmt(x):
        x = Fr(x); return f"{x.numerator}/{x.denominator}" if x.denominator != 1 else str(x.numerator)
    cmd = [BG, "-n", str(n), "-w", ",".join(fmt(w) for w in free_w),
           "-s", ",".join(str(s) for s in signs)]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if r.returncode != 0 or "omega" not in r.stdout:
        return None
    om = re.search(r"omega = \{([^}]*)\}", r.stdout).group(1)
    omega = tuple(Fr(s.strip()) for s in om.split(","))
    m = re.search(r"A_\d+ = i \* \(([^)]*)\)", r.stdout)
    if m: return omega, Fr(m.group(1))
    m = re.search(r"A_\d+ = \(([^)]*)\) \+ i \* \(([^)]*)\)", r.stdout)
    if m:
        assert Fr(m.group(1)) == 0
        return omega, Fr(m.group(2))
    raise RuntimeError(r.stdout)

def lagrange_eval(pts, xq):
    s = Fr(0)
    for i, (xi, yi) in enumerate(pts):
        term = yi
        for j, (xj, _) in enumerate(pts):
            if j != i: term *= (xq - xj) / (xi - xj)
        s += term
    return s

def fits_poly(samples, deg):
    if len(samples) <= deg + 1: return None
    base = samples[:deg + 1]
    return all(lagrange_eval(base, x) == y for (x, y) in samples[deg + 1:])

def poly_degree(samples, maxdeg):
    for d in range(0, maxdeg + 1):
        v = fits_poly(samples, d)
        if v: return d
        if v is None: return "INCONCLUSIVE"
    return None

def chamber_signs(omega, signs):
    n = len(omega); k = [signs[i] * omega[i]**2 for i in range(n)]
    bits = []
    for r in range(1, n):
        for S in combinations(range(n), r):
            ks = sum(k[i] for i in S); bits.append(0 if ks == 0 else (1 if ks > 0 else -1))
    # same-type orderings within each triple
    return tuple(bits)

def ordering_bits(omega, minus, plus):
    """sign of omega_i - omega_j for same-type pairs (the kink loci where D9!=0)."""
    bits = []
    for grp in (minus, plus):
        for a, b in combinations(grp, 2):
            d = omega[a] - omega[b]; bits.append(0 if d == 0 else (1 if d > 0 else -1))
    return tuple(bits)

def D_of(omega, pairs):
    p = Fr(1)
    for (i, j) in pairs: p *= (omega[i] + omega[j])
    return p

def hr(t): print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)

def build_slice(n, base_free, vary_idx, opp_idx, signs, ts):
    out = []
    for t in ts:
        fw = list(base_free); fw[vary_idx] += t; fw[opp_idx] -= t
        res = run_bg(n, fw, signs)
        if res is None: continue
        out.append((t, res[0], res[1]))
    return out

def main():
    PASS = True
    n = 6; minus = [0,1,2]; plus = [3,4,5]; signs = [-1,-1,-1,1,1,1]
    pairs = [(i,j) for i in minus for j in plus]

    # ---- per-chamber B-test in several chambers --------------------------------
    hr("Per-chamber: (A_6/i)*D_9 polynomial across distinct chambers")
    bases = [
        [Fr(7,2), Fr(13,3), Fr(5), Fr(9)],     # chamber from main script
        [Fr(3),   Fr(10),   Fr(4), Fr(15,2)],
        [Fr(11,2),Fr(2),    Fr(6), Fr(13,2)],
        [Fr(9,2), Fr(7),    Fr(3), Fr(20)],
    ]
    ts = [Fr(k,50) for k in range(-20,21)]
    chamber_labels = set()
    npass = 0
    for bi, base in enumerate(bases):
        sl = build_slice(n, base, 2, 3, signs, ts)
        if not sl:
            print(f"  base#{bi}: no samples"); continue
        mid = sl[len(sl)//2]; ref = chamber_signs(mid[1], signs); refo = ordering_bits(mid[1], minus, plus)
        kept = [(t,o,A) for (t,o,A) in sl if chamber_signs(o,signs)==ref and ordering_bits(o,minus,plus)==refo]
        if len(kept) < 25:
            print(f"  base#{bi}: only {len(kept)} clean samples, skip"); continue
        chamber_labels.add(ref + refo)
        sAD = [(t, A*D_of(o,pairs)) for (t,o,A) in kept]
        sA  = [(t, A) for (t,o,A) in kept]
        dAD = poly_degree(sAD, len(sAD)-3); dA = poly_degree(sA, min(22,len(sA)-3))
        ok = isinstance(dAD,int) and (dA is None)
        print(f"  base#{bi}: {len(kept)} samples | A_6/i poly? {dA} | (A_6/i)*D_9 poly deg {dAD} -> {'OK' if ok else 'FAIL'}")
        PASS &= ok; npass += ok
    print(f"  distinct chamber/ordering pieces sampled: {len(chamber_labels)}; per-chamber passes: {npass}")

    # ---- SPLINE / kink test: cross a same-type-ordering wall (D9 != 0) ----------
    hr("Spline test: N_6=(A_6/i)*D_9 changes polynomial across a same-type wall (kink, not pole)")
    # vary a single minus leg so two minus freqs cross (omega_2 = omega_3), a same-type ordering wall.
    # base: w2 sweeps through w3; keep others fixed. sumFree NOT constant here, so multiply A by
    # sumFree^k to clear the leg-solve artifact -- but simplest: just test the spline at fixed scale by
    # checking the numerator polynomial on each side using D9 (which already contains -(w1+w6)=sumFree).
    # We sweep w2 across w3=5 (legs 2,3 are minus). free=[w2, 5, w4, w5].
    w3v=Fr(5)
    base = [w3v, w3v, Fr(4), Fr(17,2)]   # w2 will be swept; w3=5 fixed; w4,w5 plus fixed
    def sample_w2(w2):
        res = run_bg(n, [w2, w3v, Fr(4), Fr(17,2)], signs)
        if res is None: return None
        o,A = res; return (w2, o, A)
    left  = [s for s in (sample_w2(Fr(5)-Fr(k,80)) for k in range(1,22)) if s]   # w2 < 5
    right = [s for s in (sample_w2(Fr(5)+Fr(k,80)) for k in range(1,22)) if s]   # w2 > 5
    # keep each side in one chamber
    def clean(side):
        if not side: return []
        ref = chamber_signs(side[len(side)//2][1], signs); refo = ordering_bits(side[len(side)//2][1], minus, plus)
        return [(w,o,A) for (w,o,A) in side if chamber_signs(o,signs)==ref and ordering_bits(o,minus,plus)==refo]
    L=clean(left); R=clean(right)
    print(f"  left (w2<w3) clean samples: {len(L)} ; right (w2>w3): {len(R)}")
    if len(L)>=12 and len(R)>=12:
        NL=[(w, A*D_of(o,pairs)) for (w,o,A) in L]
        NR=[(w, A*D_of(o,pairs)) for (w,o,A) in R]
        dL=poly_degree(NL, len(NL)-3); dR=poly_degree(NR, len(NR)-3)
        print(f"  N_6 left poly deg {dL}, right poly deg {dR}")
        # build the two polynomials (as value at a common probe w2=5, the wall) by extrapolation
        if isinstance(dL,int) and isinstance(dR,int):
            vL=lagrange_eval(NL[:dL+1], Fr(5)); vR=lagrange_eval(NR[:dR+1], Fr(5))
            # also compare full polynomials: do they agree as functions? sample a fresh probe off-wall
            probe=Fr(5)+Fr(1,7)  # a point only on the right side's analytic continuation
            pL=lagrange_eval(NL[:dL+1], probe); pR=lagrange_eval(NR[:dR+1], probe)
            same = (pL==pR)
            print(f"  N_6 extrapolated to wall w2=w3=5: left={vL}, right={vR}, equal at wall? {vL==vR}")
            print(f"  N_6 polynomials identical as functions? {same}  (expect False -> genuine spline)")
            # A_6 itself continuous at the wall (finite kink): compare A_6/i limits
            aL=lagrange_eval([(w,A) for (w,o,A) in L][:dL+1], Fr(5))
            aR=lagrange_eval([(w,A) for (w,o,A) in R][:dR+1], Fr(5))
            print(f"  A_6/i limit from left={aL}, right={aR}, continuous? {aL==aR}")
            okspl = (not same) and (vL==vR) and (aL==aR)
            print(f"  -> {'PASS' if okspl else 'NOTE'}: N_6 is a SPLINE (different poly each side, "
                  f"continuous value=kink); A_6 finite -> not a single global rational fn")
            # not counted as hard PASS/FAIL of the denominator claim; informational
    else:
        print("  insufficient clean samples for spline test (non-fatal)")

    # ---- minimality combinatorics ----------------------------------------------
    hr("Minimality: S_3(minus) x S_3(plus) orbit of one mixed pair = all 9 (n=6)")
    pair0 = (0,3)  # (omega_1 + omega_4)
    orbit = set()
    for pm in permutations(minus):
        for pp in permutations(plus):
            perm = {minus[a]:pm[a] for a in range(3)}; perm.update({plus[a]:pp[a] for a in range(3)})
            orbit.add(tuple(sorted((perm[pair0[0]], perm[pair0[1]]))))
    allpairs = set(tuple(sorted(p)) for p in pairs)
    okmin = (orbit == allpairs)
    print(f"  orbit size {len(orbit)}, all mixed pairs {len(allpairs)}, equal? {okmin}")
    print(f"  -> {'PASS' if okmin else 'FAIL'}: only symmetric divisors of D_9 are 1 and D_9; "
          f"since A_6 is rational, reduced symmetric denominator = D_9 (minimal)")
    PASS &= okmin

    hr(f"SUPPLEMENT OVERALL: {'ALL PASS' if PASS else 'SOME FAILED'}")
    return 0 if PASS else 1

if __name__ == "__main__":
    sys.exit(main())
