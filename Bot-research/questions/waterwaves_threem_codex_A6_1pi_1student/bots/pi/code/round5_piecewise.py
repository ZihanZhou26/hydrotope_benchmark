#!/usr/bin/env python3
"""PI round-5 CRUX RE-TEST: is A_6 piecewise-POLYNOMIAL or genuinely RATIONAL?

pi_v_008/009 concluded "rational, not piecewise polynomial" from a local 1e-6
ball failing a degree-8 polynomial fit by ONE (rank 285 vs 286).  That one-unit
gap is exactly what a ball STRADDLING a finer wall would produce: two polynomial
pieces cannot be fit by a single polynomial.  The 18-wall signature does NOT
track the factorization surfaces h_S = omega_S^2 - |k_S| = 0 (35 of them) -- so a
"single 18-wall chamber" ball can still cross several true pieces.

Clean test: build a short affine line, then keep the maximal contiguous run of
points on which EVERY sign is constant -- all 18 momentum walls AND all 35
factorization surfaces h_S.  That run lies in ONE genuine piece.  On it, test:
  (poly)  Is (A_6/i) * U^8 a univariate polynomial of degree <= 16 in t?
          [A_6/i is degree-8 homogeneous; om_1,om_6 have denominator U=sum(f).]
If YES on several independent single-piece runs => A_6 is PIECEWISE POLYNOMIAL
(box spline revived; pi_v_008 was a straddling artifact).  If NO => genuinely
rational within a single piece.

Exact: fresh bg_r5 (GMP), reduced mod P=2^61-1.
"""
import subprocess, re, random, sys
from itertools import combinations
from fractions import Fraction as F

BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code/bg_r5"
SIG = [-1, -1, -1, 1, 1, 1]
P = (1 << 61) - 1


def bg_amp(om, g=F(1)):
    K = [SIG[i] * om[i] * om[i] / g for i in range(6)]
    p = subprocess.run([BG, "--amp", "-K", ",".join(str(x) for x in K),
                        "-W", ",".join(str(x) for x in om), "-g", str(g)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if p.returncode != 0:
        return None
    m = re.search(r"A_6 = i \* \(([^)]*)\)", p.stdout)
    if m:
        return F(m.group(1))
    m2 = re.search(r"A_6 = \(([^)]*)\) \+ i \* \(([^)]*)\)", p.stdout)
    if m2 and F(m2.group(1)) == 0:
        return F(m2.group(2))
    return None


def solve_onshell(free):
    fr = [F(x) for x in free]; s = sum(fr)
    if s == 0:
        return None
    ss = sum(SIG[i + 1] * fr[i] ** 2 for i in range(4))
    wn = -(SIG[0] * s * s + ss) / (2 * SIG[0] * s)
    return [-(s + wn), fr[0], fr[1], fr[2], fr[3], wn]


def generic(om):
    sq = sorted(w * w for w in om)
    return all(sq[i] != sq[i + 1] for i in range(5))


def full_sign(om):
    """18 momentum walls + 35 factorization surfaces h_S.  Returns tuple of signs."""
    a = [om[i] ** 2 for i in range(3)]; b = [om[3 + j] ** 2 for j in range(3)]
    T = sum(a); sg = []
    for i in range(3):
        for j in range(3):
            v = a[i] - b[j]; sg.append(1 if v > 0 else -1 if v < 0 else 0)
    for i in range(3):
        for j in range(3):
            v = a[i] + b[j] - T; sg.append(1 if v > 0 else -1 if v < 0 else 0)
    # factorization surfaces h_S = omega_S^2 - |k_S|, |S| = 2,3  (g=1)
    for r in (2, 3):
        for S in combinations(range(6), r):
            wS = sum(om[i] for i in S)
            kS = sum(SIG[i] * om[i] ** 2 for i in S)
            h = wS * wS - (kS if kS >= 0 else -kS)
            sg.append(1 if h > 0 else -1 if h < 0 else 0)
    return tuple(sg)


def to_mod(fr):
    return (fr.numerator % P) * pow(fr.denominator % P, P - 2, P) % P


def lagrange_check(samples, dmax, nhold=8):
    seen = {}; pts = []
    for t, y in samples:
        if t not in seen:
            seen[t] = y; pts.append((t, y))
    if len(pts) < dmax + 1 + nhold:
        return None
    nodes = pts[:dmax + 1]; hold = pts[dmax + 1:]
    xs = [t for t, _ in nodes]; ys = [y for _, y in nodes]
    w = []
    for i in range(len(xs)):
        d = 1
        for j in range(len(xs)):
            if j != i:
                d = d * ((xs[i] - xs[j]) % P) % P
        w.append(pow(d, P - 2, P))
    for th, yh in hold:
        num = 0; den = 0
        for i in range(len(xs)):
            diff = (th - xs[i]) % P
            if diff == 0:
                num = ys[i]; den = 1; break
            c = w[i] * pow(diff, P - 2, P) % P
            num = (num + c * ys[i]) % P
            den = (den + c) % P
        if num * pow(den, P - 2, P) % P != yh:
            return False
    return True


def single_piece_run(rng):
    """return a list of >= 30 exact points sharing ONE full sign vector on a line."""
    for _ in range(6000):
        f0 = [F(rng.randint(-8, 8)) + F(rng.randint(-5, 5), 7) for _ in range(4)]
        v = [F(rng.randint(-3, 3)) for _ in range(4)]
        if all(x == 0 for x in v):
            continue
        seq = []
        for k in range(-200, 201):
            t = F(k, 400)                      # very fine, tiny span -> stays in one piece
            f = [f0[i] + t * v[i] for i in range(4)]
            if any(x == 0 for x in f) or sum(f) == 0:
                continue
            om = solve_onshell(f)
            if om is None or any(x == 0 for x in om) or not generic(om):
                continue
            seq.append((t, om, sum(f), full_sign(om)))
        if len(seq) < 40:
            continue
        # longest contiguous run with identical full sign vector and no zero
        best = []
        i = 0
        while i < len(seq):
            j = i
            sg = seq[i][3]
            if 0 in sg:
                i += 1; continue
            while j < len(seq) and seq[j][3] == sg:
                j += 1
            if j - i > len(best):
                best = seq[i:j]
            i = j
        if len(best) >= 30:
            return best
    return None


def main():
    rng = random.Random(7777)
    ok_runs = 0; poly_pass = 0; details = []
    for run_id in range(6):
        best = single_piece_run(rng)
        if best is None:
            print(f"run {run_id}: no single-piece run of >=30 points found"); continue
        # compute (A_6/i)*U^8 at each point
        samples = []
        for (t, om, U, sg) in best:
            A = bg_amp(om)
            if A is None:
                continue
            Y = A * (U ** 8)
            samples.append((to_mod(t), to_mod(Y)))
        res = lagrange_check(samples, 16, nhold=8)
        ok_runs += 1
        tag = "POLYNOMIAL(deg<=16)" if res else ("NOT polynomial" if res is False else "insufficient")
        if res:
            poly_pass += 1
        print(f"run {run_id}: single-piece points={len(best)} amps={len(samples)} "
              f"=> (A_6/i)*U^8 {tag}")
        details.append((len(best), res))
        sys.stdout.flush()
    print("=" * 72)
    print(f"single-piece runs tested: {ok_runs}   (A_6/i)*U^8 polynomial: {poly_pass}")
    if ok_runs and poly_pass == ok_runs:
        print("VERDICT: A_6 is PIECEWISE POLYNOMIAL (finer pieces than 18-wall) -- "
              "pi_v_008 'rational' was a wall-straddling artifact.")
    elif poly_pass == 0 and ok_runs:
        print("VERDICT: A_6 is genuinely RATIONAL within a single true piece "
              "(NOT piecewise polynomial). pi_v_008 stands.")
    else:
        print("VERDICT: MIXED/INCONCLUSIVE -- inspect per-run.")


if __name__ == "__main__":
    main()
