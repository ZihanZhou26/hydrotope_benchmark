#!/usr/bin/env python3
"""
Round-2 (student-2): verify the g-RESTORED closed form against ./bg.

Open item from SOLVED.md / derivation.md: all prior verification was at g=1.
By homogeneity of the BG engine (see derivations/round2_telescoping.md),
A_n scales as g^{3-n} at fixed omega, because on-shell K_i = sigma_i omega_i^2/g
and the only g in Propagator is D = wS^2/|kS| - g.

g-restored formula (sector sigma=(-1,-1,+1..+1)):
    A_n = i * a_n,
    a_n = g^{3-n} * 2^{n-1} * w1 * w2 * sum_{S subset of plus legs}
              (-1)^|S| * max(0, P - sum_{j in S} w_j^2)^{n-3},
    P   = min(w1^2, w2^2),  legs 1,2 minus, legs 3..n plus.

This script:
  (A) drives our own ./bg (exact rational) on-shell at n=5,6,7 for g in {1,2,3}
      over principal / non-principal / extreme points and checks residual == 0;
  (B) does the n=4 delta->0 limit at g=1 and g=2 (the on-shell point SIGFPEs),
      via exact-rational Richardson extrapolation, and checks the g^{-1} scaling.
All arithmetic is exact (fractions.Fraction); residuals are reported.
"""
import subprocess, re, sys
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path

BG = str(Path(__file__).with_name("bg"))

# ---------- the g-restored closed form (student-1 all-chamber + my g^{3-n}) ----------
def a_formula(omega, sigma, g):
    """omega: list of Fraction (leg order). sigma: list of +-1. g: Fraction."""
    minus = [i for i,s in enumerate(sigma) if s < 0]
    plus  = [i for i,s in enumerate(sigma) if s > 0]
    assert len(minus) == 2
    w1, w2 = omega[minus[0]], omega[minus[1]]
    P = min(w1*w1, w2*w2)
    t = [omega[j]*omega[j] for j in plus]
    m = len(omega) - 3                      # exponent n-3
    tot = F(0)
    for r in range(len(plus)+1):
        for S in combinations(range(len(plus)), r):
            x = P - sum(t[j] for j in S)
            if x > 0:
                tot += (-1)**r * x**m
    n = len(omega)
    return g**(3-n) * F(2)**(n-1) * w1 * w2 * tot

# ---------- oracle drivers ----------
def bg_onshell(n, free, signs, g):
    """return Fraction a_n from ./bg -n .. -w .. -s .. -g .. (exact rational)."""
    out = subprocess.run(
        [BG, "-n", str(n), "-w", ",".join(map(str, free)),
         "-s", ",".join(map(str, signs)), "-g", str(g)],
        capture_output=True, text=True, timeout=600).stdout
    mom = re.search(r"omega = \{([^}]*)\}", out)
    omega = [F(x.strip()) for x in mom.group(1).split(",")]
    mim = re.search(r"A_\d+ = i \* \(([^)]*)\)", out)
    if not mim:
        raise RuntimeError("no imaginary-only amplitude:\n"+out)
    return F(mim.group(1)), omega

def bg_amp(K, W, g):
    """raw BGAmplitude via --amp; returns (re,im) as Fractions."""
    out = subprocess.run(
        [BG, "--amp", "-K", ",".join(map(str,K)), "-W", ",".join(map(str,W)),
         "-g", str(g)], capture_output=True, text=True, timeout=600).stdout
    m = re.search(r"A_\d+ = i \* \(([^)]*)\)", out)
    if m: return F(0), F(m.group(1))
    m = re.search(r"A_\d+ = \(([^)]*)\) \+ i \* \(([^)]*)\)", out)
    return F(m.group(1)), F(m.group(2))

def rel(a, b):
    if a == b: return F(0)
    if b == 0: return abs(a)
    return abs(a-b)/abs(b)

# ---------- (A) on-shell exact checks, g in {1,2,3} ----------
def run_onshell():
    print("="*72)
    print("(A) g-restored formula vs ./bg on-shell (exact rational), residual must be 0")
    print("="*72)
    cases = [
        # n, free freqs (-w), label
        (5, [1,2,4],        "principal"),
        (5, [6,1,2],        "non-principal (b2m0h1)"),
        (5, [1,2,1000],     "extreme (one plus >>)"),
        (6, [1,2,3,4],      "principal"),
        (6, [7,1,2,3],      "non-principal (b3m0h1)"),
        (7, [1,2,3,4,5],    "principal"),
        (7, [1,2,3,4,1000], "extreme (one plus >>)"),
    ]
    allzero = True
    for n, free, lab in cases:
        signs = [-1,-1] + [1]*(n-2)
        for g in (F(1), F(2), F(3)):
            a_or, omega = bg_onshell(n, free, signs, g)
            a_pr = a_formula(omega, signs, g)
            r = rel(a_pr, a_or)
            allzero &= (r == 0)
            tag = "OK " if r == 0 else "!!!"
            print(f"  [{tag}] n={n} g={g}  {lab:24s} oracle={str(a_or):>24s}  resid={r}")
    print("  ALL EXACT-ZERO:", allzero)
    return allzero

# ---------- (B) n=4 delta->0 limit at g=1 and g=2 ----------
def n4_limit(g, w2, w3):
    """A_4 by delta->0; branch w1=-w3, w4=-w2; relax w4 -> -w2 + delta, keep sum w =0.
       Exact-rational Richardson extrapolation in delta. Returns Fraction a_4 (im part)."""
    sig = [-1,-1,1,1]                       # legs: 1,2 minus ; 3,4 plus
    deltas = [F(1,d) for d in (10,20,40,80,160)]
    vals = []
    for dl in deltas:
        w4 = -F(w2) + dl
        w1 = -(F(w2)+F(w3)+w4)              # keep sum omega = 0
        W = [w1, F(w2), F(w3), w4]
        K = [sig[i]*W[i]*W[i]/F(g) for i in range(4)]
        re, im = bg_amp(K, W, F(g))
        assert re == 0, f"Re != 0 at delta={dl}: {re}"
        vals.append((dl, im))
    # Neville / Richardson extrapolation to delta=0 (exact rational)
    xs = [v[0] for v in vals]; ys = [v[1] for v in vals]
    k = len(xs)
    T = [yi for yi in ys]
    for col in range(1, k):
        newT = []
        for i in range(k-col):
            num = (F(0)-xs[i+col])*T[i] - (F(0)-xs[i])*T[i+1]
            den = xs[i] - xs[i+col]
            newT.append(num/den)
        T = newT
        xs2 = xs  # x-nodes unchanged for Neville at x=0
    return T[0]

def run_n4():
    print("="*72)
    print("(B) n=4 delta->0 limit: check g-scaling a_4(g)=a_4(1)/g")
    print("="*72)
    ok = True
    for (w2,w3,a1) in [(1,3,F(-24)), (2,5,F(-320)), (3,7,F(-1512)), (1,5,F(-40))]:
        v1 = n4_limit(1, w2, w3)
        v2 = n4_limit(2, w2, w3)
        # formula prediction at g=1: a4 = 8*w1*w2^3 with w1=-w3 -> 8*(-w3)*w2^3
        pred1 = F(8)*(-F(w3))*F(w2)**3
        pred2 = pred1/2
        r1, r2 = rel(v1, pred1), rel(v2, pred2)
        ok &= (r1 < F(1,10**10) and r2 < F(1,10**10))
        print(f"  (w2,w3)=({w2},{w3}): a4(g=1)={v1}  pred={pred1}  rel={float(r1):.2e}")
        print(f"                 a4(g=2)={v2}  pred={pred2}  rel={float(r2):.2e}  (g^-1 scaling)")
    print("  n=4 limits within 1e-10:", ok)
    return ok

if __name__ == "__main__":
    a = run_onshell()
    b = run_n4()
    print("\nRESULT:", "ALL PASS" if (a and b) else "FAILURE")
    sys.exit(0 if (a and b) else 1)
