"""final_verify.py — definitive verification of the conjecture

    A_n = i * a_n,   a_n = 2^{n-1} * w1 * w2^{2n-5}

valid in the PRINCIPAL CHAMBER (w2 = the smallest free frequency; legs 1,2 are the
sigma=-1 legs; w1,wn fixed by Sum w=0, Sum sigma w^2=0). a_n depends only on the
minus pair (w1,w2). n=4 is singular on-shell -> verified by a delta->0 limit.

Exact rational throughout (n=7 exact ~2s/pt). Reports relative residuals.
"""
import time
from fractions import Fraction as F
from engine import build_onshell, Engine


def conj(n, W):
    return 2**(n-1) * W[1] * W[2]**(2*n-5)


def exact(n, free):
    W, K = build_onshell(n, free, [-1, -1] + [1]*(n-2))
    re, im = Engine('frac').BGAmplitude(n, K, W)
    return re, im, W


def rel(a, b):
    a, b = F(a), F(b)
    if a == 0 and b == 0: return 0.0
    return float(abs(a-b)) / max(float(abs(a)), float(abs(b)), 1e-300)


def n4_limit(w2, w3):
    """A_4 at on-shell branch (w1=-w3, w4=-w2) via desingularizing eps-limit.
    direction d=(-1,1,0,0) lifts the singular {2,4} pair; Richardson in eps."""
    w1, w4 = -w3, -w2
    base = [F(w1), F(w2), F(w3), F(w4)]
    d = [F(-1), F(1), F(0), F(0)]
    sig = [-1, -1, 1, 1]
    vals = []
    for k in range(1, 6):
        eps = F(1, 10**k)
        Wl = [base[i] + eps*d[i] for i in range(4)]
        W = {i+1: Wl[i] for i in range(4)}
        K = {i+1: F(sig[i])*Wl[i]*Wl[i] for i in range(4)}
        re, im = Engine('frac').BGAmplitude(4, K, W)
        vals.append((eps, im))
    # the value is affine in eps near 0; Richardson: a0 = a(eps) - eps*a'(approx)
    (e1, v1), (e2, v2) = vals[-2], vals[-1]
    a0 = v2 + (v2 - v1)*e2/(e1 - e2)   # linear extrapolation to eps=0
    return a0, vals


print("="*78)
print("n=4  (on-shell singular -> delta->0 limit; formula a4 = 8 w1 w2^3)")
print("="*78)
for (w2, w3) in [(1, 3), (2, 5), (1, 10), (3, 7)]:
    w1 = -w3
    pred = 8 * F(w1) * F(w2)**3
    a0, vals = n4_limit(w2, w3)
    print(f" omega=({-w3},{w2},{w3},{-w2})  pred={pred}  limit~={float(a0):.6f}  "
          f"(eps=1e-5 -> {float(vals[-1][1]):.6f})  rel(1e-5)={rel(vals[-1][1], pred):.2e}")

print("\n" + "="*78)
print("n=5,6,7  EXACT principal-chamber points (incl. extreme + shuffled plus legs)")
print("="*78)
cases = {
 5: [[1,2,4],[2,3,5],[1,2,1000],[2,5,100000],[F(1,3),5,7],[1,1000,1001]],
 6: [[1,2,3,4],[1,2,3,1000000],[1,5,2,8],[1,100,2,3],[F(1,2),3,9,4]],
 7: [[1,2,3,4,5],[1,3,4,5,6],[1,2,3,4,1000],[1,9,2,8,3]],
}
allok = True
for n in (5,6,7):
    print(f"\n--- n={n} ---")
    for free in cases[n]:
        t=time.time(); re, im, W = exact(n, free); pred = conj(n, W)
        ok = (re == 0 and im == pred); allok &= ok
        w2min = (W[2] == min(W[i] for i in range(2, n)))
        print(f" free={str(free):22} w2min={int(w2min)} Re={re} relerr={rel(im,pred):.1e} {'OK' if ok else 'FAIL'}  a={im}")

print("\n" + "="*78)
print("CHAMBER RULE: w2=min(free) => formula holds; else different piece")
print("="*78)
for free in [[1,5,2,8],[1,9,2,8,3],   # w2 smallest, plus shuffled -> should hold
             [5,1,2,8],[2,1,9,3]]:    # w2 NOT smallest -> should differ
    n = len(free)+2
    re, im, W = exact(n, free); pred = conj(n, W)
    w2min = (W[2] == min(W[i] for i in range(2, n)))
    print(f" n={n} free={str(free):16} w2=min? {int(w2min)}  match={im==pred}")

print("\nALL PRINCIPAL-CHAMBER EXACT CHECKS:", "PASS" if allok else "FAIL")
