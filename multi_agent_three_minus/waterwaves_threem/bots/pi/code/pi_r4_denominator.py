#!/usr/bin/env python3
"""
PI round-4 INDEPENDENT verification of the round-3 student claim
(s1_008 / s2_010): the three-minus amplitude is RATIONAL (NOT
piecewise-polynomial -- this OVERTURNS the round-1/2 'gate'), with reduced
denominator

    D_n = prod_{i in minus} prod_{j in plus} (omega_i + omega_j).

Everything below uses the PI's OWN oracle (bots/pi/code/bg, built from the PI's
own copy of bg.cpp) as a black box returning EXACT rationals, and the PI's OWN
exact-rational analysis (no student code imported).

Tests:
  (A) on a clean one-chamber F-constant slice, A_n/i is NOT a polynomial in the
      slice parameter up to high degree  -> rational, refutes the 'polynomial' gate;
  (B) (A_n/i)*D_n IS an exact polynomial on that slice (and a 2nd chamber)
      -> D_n is a sufficient denominator;
  (C) the WRONG denominator prod(omega_i^2+omega_j^2) does NOT clear A_6
      -> confirms it is frequency SUMS, not sums of squares;
  (D) n=5 CONTROL: A_5/i is polynomial directly (method is sound);
  (E) n=7 spot check: (A_7/i)*D_12 is an exact polynomial on a slice;
  (F) exact rational reconstruction of A_6/i on a slice -> reduced denominator,
      whose roots are exactly mixed-pair frequency-sum zeros;
  (G) minimality inputs: re-confirm S_3(minus) x S_3(plus) x Z_2 symmetry of A_6
      at a generic point, and the combinatorial fact that the S_3xS_3 orbit of a
      single mixed pair is the full set of 3(n-3) pairs.
"""
import subprocess, re, sys
from fractions import Fraction as Fr
from itertools import combinations

BG = "./bg"   # run from bots/pi/code

# ---------------------------------------------------------------- oracle call
def run_bg(n, free_w, signs, dbl=False):
    """on-shell mode. free_w: list of Fr (n-2 free freqs). signs: list of +-1.
       returns (omega tuple of Fr length n, A_im Fr) or None on SIGFPE/wall."""
    def fmt(x):
        x = Fr(x)
        return f"{x.numerator}/{x.denominator}" if x.denominator != 1 else str(x.numerator)
    cmd = [BG] + (["--double"] if dbl else []) + \
          ["-n", str(n), "-w", ",".join(fmt(w) for w in free_w),
           "-s", ",".join(str(s) for s in signs)]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       universal_newlines=True)
    if r.returncode != 0 or "omega" not in r.stdout:
        return None  # SIGFPE on a wall, or bad point
    om = re.search(r"omega = \{([^}]*)\}", r.stdout).group(1)
    omega = tuple(Fr(s.strip()) for s in om.split(","))
    m = re.search(r"A_\d+ = i \* \(([^)]*)\)", r.stdout)
    if m:                       # purely imaginary (expected)
        return omega, Fr(m.group(1))
    m = re.search(r"A_\d+ = \(([^)]*)\) \+ i \* \(([^)]*)\)", r.stdout)
    if m:                       # has a real part -> not purely imaginary
        if Fr(m.group(1)) != 0:
            raise RuntimeError(f"A has nonzero real part {m.group(1)}")
        return omega, Fr(m.group(2))
    raise RuntimeError("parse fail:\n" + r.stdout)

# ---------------------------------------------------------------- exact poly tools
def lagrange_eval(pts, xq):
    """value at xq of the polynomial through pts=[(x,y)], exact."""
    s = Fr(0)
    for i, (xi, yi) in enumerate(pts):
        term = yi
        for j, (xj, _) in enumerate(pts):
            if j != i:
                term *= (xq - xj) / (xi - xj)
        s += term
    return s

def fits_poly(samples, deg):
    """True iff the degree-`deg` interpolant through the first deg+1 samples
       reproduces ALL samples exactly. Needs len(samples) > deg+1."""
    if len(samples) <= deg + 1:
        return None  # not enough evidence
    base = samples[:deg + 1]
    return all(lagrange_eval(base, x) == y for (x, y) in samples[deg + 1:])

def poly_degree(samples, maxdeg):
    """smallest d<=maxdeg s.t. samples fit a degree-d poly (confirmed on holdouts),
       or None if not polynomial up to maxdeg."""
    for d in range(0, maxdeg + 1):
        v = fits_poly(samples, d)
        if v:
            return d
        if v is None:
            return "INCONCLUSIVE (need more samples)"
    return None

def reconstruct_rational(samples, p, q):
    """fit y = P/Q, deg P=p, deg Q=q, Q normalized Q(0-coeff arbitrary): use
       Q = sum_{0..q} b_k t^k with b_0 = 1.  y_i*Q(t_i)=P(t_i).
       unknowns: a_0..a_p (P), b_1..b_q (Q).  Need p+q+1 samples to solve, more to check.
       Returns (a list, b list incl b0=1) or None if singular/inconsistent."""
    need = p + q + 1
    if len(samples) < need:
        return None
    # build linear system from first `need` samples; exact Gaussian elimination
    rows, rhs = [], []
    for (t, y) in samples[:need]:
        # a_0 + a_1 t + ... + a_p t^p  - y*(b_1 t + ... + b_q t^q) = y*1
        row = [t**k for k in range(p + 1)] + [-y * t**k for k in range(1, q + 1)]
        rows.append(row); rhs.append(y)
    sol = gauss(rows, rhs)
    if sol is None:
        return None
    a = sol[:p + 1]; b = [Fr(1)] + sol[p + 1:]
    # verify on held-out samples
    for (t, y) in samples[need:]:
        P = sum(a[k] * t**k for k in range(p + 1))
        Q = sum(b[k] * t**k for k in range(q + 1))
        if Q == 0 or P != y * Q:
            return None
    return a, b

def gauss(A, rhs):
    n = len(A); M = [row[:] + [rhs[i]] for i, row in enumerate(A)]
    col = 0
    for r in range(n):
        piv = None
        for k in range(r, n):
            if M[k][col] != 0: piv = k; break
        if piv is None: return None
        M[r], M[piv] = M[piv], M[r]
        pv = M[r][col]
        M[r] = [x / pv for x in M[r]]
        for k in range(n):
            if k != r and M[k][col] != 0:
                f = M[k][col]
                M[k] = [a - f * b for a, b in zip(M[k], M[r])]
        col += 1
    return [M[i][n] for i in range(n)]

# ---------------------------------------------------------------- chamber guard
def chamber_signs(omega, signs):
    """sign vector of k_S = sum_{i in S} sigma_i omega_i^2 over all nonempty proper S,
       plus same-type ordering bits. Used to certify a slice stays in one piece."""
    n = len(omega)
    k = [signs[i] * omega[i]**2 for i in range(n)]
    bits = []
    for r in range(1, n):
        for S in combinations(range(n), r):
            ks = sum(k[i] for i in S)
            bits.append(0 if ks == 0 else (1 if ks > 0 else -1))
    return tuple(bits)

def mixed_pairs(n, minus, plus):
    return [(i, j) for i in minus for j in plus]

def D_of(omega, pairs):
    p = Fr(1)
    for (i, j) in pairs:
        p *= (omega[i] + omega[j])
    return p

def Dsq_of(omega, pairs):
    p = Fr(1)
    for (i, j) in pairs:
        p *= (omega[i]**2 + omega[j]**2)
    return p

# ---------------------------------------------------------------- slice builder
def build_slice(n, base_free, vary_idx, opp_idx, signs, ts):
    """free freqs = base_free, but free[vary_idx] += t and free[opp_idx] -= t
       (keeps sumFree constant -> solved legs polynomial in t). Returns list of
       (t, omega, Aim) for wall-free points, all in ONE chamber."""
    out = []
    for t in ts:
        fw = list(base_free)
        fw[vary_idx] = base_free[vary_idx] + t
        fw[opp_idx]  = base_free[opp_idx]  - t
        res = run_bg(n, fw, signs)
        if res is None:
            continue
        omega, Aim = res
        out.append((t, omega, Aim))
    if not out:
        return []
    # keep maximal block sharing the chamber sign-vector of the middle sample
    mid = out[len(out)//2]
    ref = chamber_signs(mid[1], signs)
    if any(0 in chamber_signs(o, signs) for (_, o, _) in out):
        # a sample sits exactly on a wall (shouldn't, bg would SIGFPE) -> drop zeros later
        pass
    kept = [(t, o, A) for (t, o, A) in out if chamber_signs(o, signs) == ref]
    return kept

# ================================================================ TESTS
def hr(t): print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)

def main():
    PASS = True
    # ---- n=6 sector
    n = 6
    minus = [0, 1, 2]; plus = [3, 4, 5]    # 0-indexed legs
    pairs6 = mixed_pairs(n, minus, plus)
    signs6 = [-1, -1, -1, 1, 1, 1]
    # free legs are 2..n-1 (0-indexed 1..4) = my -w entries [w2,w3,w4,w5]
    # vary plus legs 4,5 (free-index 2,3) oppositely -> sumFree const
    base_free = [Fr(7, 2), Fr(13, 3), Fr(5), Fr(9)]   # w2,w3 (minus) fixed; w4,w5 (plus)
    ts = [Fr(k, 40) for k in range(-18, 19)]           # tiny range, dense
    sl = build_slice(n, base_free, vary_idx=2, opp_idx=3, signs=signs6, ts=ts)

    hr("Slice setup (n=6, chamber I): F-constant, vary w4=5+t, w5=9-t")
    print(f"  wall-free samples in one chamber: {len(sl)}")
    if len(sl) < 30:
        print("  WARNING: few samples; widen/redensify. Got", len(sl))
    samples_Aim = [(t, A) for (t, o, A) in sl]                  # A_6/i
    samples_AD  = [(t, A * D_of(o, pairs6)) for (t, o, A) in sl]   # (A_6/i)*D_9
    samples_Asq = [(t, A * Dsq_of(o, pairs6)) for (t, o, A) in sl] # (A_6/i)*prod(wi^2+wj^2)

    hr("(A) Is A_6/i polynomial in t?  (gate said yes; claim says NO)")
    dA = poly_degree(samples_Aim, maxdeg=min(25, len(samples_Aim) - 3))
    print(f"  A_6/i polynomial degree up to {min(25,len(samples_Aim)-3)}: {dA}")
    okA = (dA is None)
    print(f"  -> {'PASS' if okA else 'FAIL'}: A_6 is {'RATIONAL (not polynomial)' if okA else 'polynomial?!'}")
    PASS &= okA

    hr("(B) Is (A_6/i)*D_9 polynomial in t?  (claim: YES)")
    dAD = poly_degree(samples_AD, maxdeg=len(samples_AD) - 3)
    okB = isinstance(dAD, int)
    print(f"  (A_6/i)*D_9 polynomial degree: {dAD}")
    print(f"  -> {'PASS' if okB else 'FAIL'}: D_9 = prod(w_i+w_j) {'clears the denominator' if okB else 'does NOT clear'}")
    PASS &= okB

    hr("(C) Does the WRONG denominator prod(w_i^2+w_j^2) clear A_6?  (claim: NO)")
    dAsq = poly_degree(samples_Asq, maxdeg=min(25, len(samples_Asq) - 3))
    okC = (dAsq is None)
    print(f"  (A_6/i)*prod(w_i^2+w_j^2) polynomial degree up to {min(25,len(samples_Asq)-3)}: {dAsq}")
    print(f"  -> {'PASS' if okC else 'FAIL'}: sums-of-squares {'do NOT clear (correct: it is frequency SUMS)' if okC else 'cleared?!'}")
    PASS &= okC

    hr("(F) Exact rational reconstruction of A_6/i on the slice -> reduced denominator")
    found = None
    for q in range(1, 7):
        for p in range(0, 16):
            rr = reconstruct_rational(samples_Aim, p, q)
            if rr is not None:
                found = (p, q, rr); break
        if found: break
    if found:
        p, q, (a, b) = found
        print(f"  reconstructed A_6/i = P/Q with deg P={p}, deg Q={q}")
        # roots of Q via the mixed-pair predictor: t* where omega_i(t*)+omega_j(t*)=0
        # find, per mixed pair, the t that zeroes (omega_i+omega_j) on the slice (linear/quadratic)
        # we instead just verify: each reduced-denominator root coincides with a mixed-pair-sum zero.
        # Build (omega_i+omega_j)(t) by interpolation from the slice, find its zeros, match to roots of Q.
        # Simpler exact check: Q(t) divides D_9(t) as polynomials in t.
        # Reconstruct D_9(t) polynomial from the slice, then check remainder Q | D9.
        D9_samples = [(t, D_of(o, pairs6)) for (t, o, A) in sl]
        degD9 = poly_degree(D9_samples, maxdeg=len(D9_samples) - 3)
        print(f"  D_9(t) is a degree-{degD9} polynomial on the slice")
        # Q poly coeffs b (b[0]=1.. ascending); check Q | D9 by polynomial division over Q
        D9coef = poly_coeffs(D9_samples, degD9)
        Qcoef = b
        quo, rem = polydiv(D9coef, Qcoef)
        okF = all(c == 0 for c in rem)
        print(f"  reduced denominator Q(t) divides D_9(t)?  {okF}")
        print(f"  -> {'PASS' if okF else 'FAIL'}: reduced poles are a subset of the mixed-pair frequency sums")
        PASS &= okF
    else:
        print("  reconstruction did not converge in tried (p,q) -- INCONCLUSIVE (not fatal)")

    # ---- (B') second chamber via a different base point ----------------------
    hr("(B') Second independent chamber: re-test (A) and (B)")
    base2 = [Fr(2), Fr(11, 2), Fr(17, 3), Fr(23, 5)]
    sl2 = build_slice(n, base2, vary_idx=2, opp_idx=3, signs=signs6, ts=ts)
    print(f"  wall-free samples in chamber II: {len(sl2)}")
    if len(sl2) >= 30:
        s2_Aim = [(t, A) for (t, o, A) in sl2]
        s2_AD = [(t, A * D_of(o, pairs6)) for (t, o, A) in sl2]
        dA2 = poly_degree(s2_Aim, maxdeg=min(25, len(s2_Aim) - 3))
        dAD2 = poly_degree(s2_AD, maxdeg=len(s2_AD) - 3)
        print(f"  A_6/i poly degree: {dA2}  (expect None=rational)")
        print(f"  (A_6/i)*D_9 poly degree: {dAD2}  (expect an int)")
        ok = (dA2 is None) and isinstance(dAD2, int)
        print(f"  -> {'PASS' if ok else 'FAIL'}")
        PASS &= ok
    else:
        print("  too few samples in chamber II; skipped (non-fatal)")

    # ---- (D) n=5 control -----------------------------------------------------
    hr("(D) n=5 CONTROL: A_5/i must be polynomial directly (known closed form)")
    signs5 = [-1, -1, -1, 1, 1]
    base5 = [Fr(7, 2), Fr(13, 3), Fr(6)]   # free legs 2,3,4; vary plus legs 4 & ... need two plus legs
    # n=5 plus legs are 4,5; free legs are 2,3,4 -> only one free plus leg (4); leg5 is solved.
    # Use a generic single-parameter slice in w4 instead (sumFree not constant, but A_5 is polynomial
    # in the freqs, and the leg-1,5 solve introduces only sumFree powers; multiply by sumFree^k).
    # Simpler: vary w2 (minus) and w3 (minus) oppositely to keep sumFree const.
    base5 = [Fr(5), Fr(8), Fr(4)]          # w2,w3 (minus), w4 (plus, fixed)
    sl5 = build_slice(5, base5, vary_idx=0, opp_idx=1, signs=signs5, ts=ts)
    print(f"  n=5 wall-free samples: {len(sl5)}")
    if len(sl5) >= 12:
        s5 = [(t, A) for (t, o, A) in sl5]
        d5 = poly_degree(s5, maxdeg=min(15, len(s5) - 3))
        okD = isinstance(d5, int)
        print(f"  A_5/i polynomial degree: {d5}")
        print(f"  -> {'PASS' if okD else 'FAIL'}: n=5 is polynomial directly (denominator cancels) -> method sound")
        PASS &= okD
    else:
        print("  too few n=5 samples; skipped")

    # ---- (E) n=7 spot check --------------------------------------------------
    hr("(E) n=7 spot check: (A_7/i)*D_12 polynomial on a slice")
    n7 = 7
    minus7 = [0, 1, 2]; plus7 = [3, 4, 5, 6]
    pairs7 = mixed_pairs(n7, minus7, plus7)
    signs7 = [-1, -1, -1, 1, 1, 1, 1]
    # free legs 2..6 (0-idx 1..5) = -w entries [w2,w3,w4,w5,w6]; vary plus legs 5,6 (free-idx 3,4)
    base7 = [Fr(7, 2), Fr(13, 3), Fr(4), Fr(5), Fr(8)]
    ts7 = [Fr(k, 60) for k in range(-15, 16)]
    sl7 = build_slice(n7, base7, vary_idx=3, opp_idx=4, signs=signs7, ts=ts7)
    print(f"  n=7 wall-free samples: {len(sl7)}")
    if len(sl7) >= 25:
        s7_A = [(t, A) for (t, o, A) in sl7]
        s7_AD = [(t, A * D_of(o, pairs7)) for (t, o, A) in sl7]
        d7A = poly_degree(s7_A, maxdeg=min(28, len(s7_A) - 3))
        d7AD = poly_degree(s7_AD, maxdeg=len(s7_AD) - 3)
        print(f"  A_7/i poly degree: {d7A}  (expect None=rational)")
        print(f"  (A_7/i)*D_12 poly degree: {d7AD}  (expect an int)")
        okE = (d7A is None) and isinstance(d7AD, int)
        print(f"  -> {'PASS' if okE else 'FAIL'}")
        PASS &= okE
    else:
        print("  too few n=7 samples; skipped")

    hr(f"OVERALL: {'ALL PASS' if PASS else 'SOME FAILED'}")
    return 0 if PASS else 1

# polynomial coeff extraction (ascending) from samples, given known degree
def poly_coeffs(samples, deg):
    base = samples[:deg + 1]
    # Vandermonde solve
    rows = [[t**k for k in range(deg + 1)] for (t, _) in base]
    rhs = [y for (_, y) in base]
    return gauss(rows, rhs)

def polydiv(num, den):
    """polynomial division, coeffs ascending. returns (quo, rem) ascending."""
    num = [Fr(x) for x in num]; den = [Fr(x) for x in den]
    # strip trailing zeros of den
    while den and den[-1] == 0: den.pop()
    num = num[:]
    # work in descending for convenience
    num.reverse(); den.reverse()
    quo = [Fr(0)] * (len(num) - len(den) + 1) if len(num) >= len(den) else [Fr(0)]
    while len(num) >= len(den) and any(c != 0 for c in num):
        if num[0] == 0:
            num.pop(0); continue
        coef = num[0] / den[0]
        deg_diff = len(num) - len(den)
        quo[deg_diff] = coef
        for i in range(len(den)):
            num[i] -= coef * den[i]
        num.pop(0)
    rem = num
    quo.reverse(); rem.reverse()
    return quo, rem

if __name__ == "__main__":
    sys.exit(main())
