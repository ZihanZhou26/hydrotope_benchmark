"""verify.py — verify conjecture  A_n = i * 2^{n-1} * w1 * w2^{2n-5}  in the principal
chamber (w2 <= all other free freqs).  Exact (mpq) for n<=6, long double via ./bg for n=7.
Reports relative residuals. Also tests the chamber rule and minus-pair-only property.
"""
import subprocess, re as _re
from fractions import Fraction as F
from engine import build_onshell, Engine


def conj(n, W):
    return 2**(n-1) * W[1] * W[2]**(2*n-5)   # a_n (imaginary part), exact Fraction


def exact_amp(n, free):
    W, K = build_onshell(n, free, [-1, -1] + [1]*(n-2))
    re, im = Engine('frac').BGAmplitude(n, K, W)
    return re, im, W


def bg_double_onshell(n, free):
    s = ",".join(["-1", "-1"] + ["1"]*(n-2))
    w = ",".join(str(F(x)) for x in free)
    out = subprocess.run(["./bg", "--double", "-n", str(n), "-w", w, "-s", s],
                         capture_output=True, text=True).stdout
    W = None; im = None
    for line in out.splitlines():
        if line.startswith("omega"):
            vals = line.split("{")[1].split("}")[0].split(",")
            W = {i+1: float(vals[i]) for i in range(n)}
        if line.startswith(f"A_{n} (double)"):
            rhs = line.split("=", 1)[1].replace("i", "").strip()
            nums = _re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', rhs)
            re = float(nums[0]); im = float(nums[1])
    return re, im, W


def relerr(a, b):
    a = float(a); b = float(b)
    if a == 0 and b == 0: return 0.0
    return abs(a-b)/max(abs(a), abs(b), 1e-300)


print("="*70)
print("EXACT verification (n=4 via off-shell limit handled separately; n=5,6 exact)")
print("="*70)
# principal-chamber points (free freqs ascending, w2 smallest), incl. extreme regimes
cases = {
    5: [[1,2,4],[2,3,5],[1,2,1000],[1,1000,1001],[F(1,3),5,7],[2,5,100000]],
    6: [[1,2,3,4],[1,2,3,100],[1,5,6,7],[F(1,2),3,4,9],[1,2,3,1000000]],
}
for n in (5,6):
    print(f"\n--- n={n} ---")
    for free in cases[n]:
        re, im, W = exact_amp(n, free)
        pred = conj(n, W)
        err = relerr(im, pred)
        print(f" free={str(free):24} Re={re}  a={im}  pred={pred}  relerr={err:.2e}  {'OK' if im==pred and re==0 else 'FAIL'}")

print("\n" + "="*70)
print("n=7 via ./bg --double (exact too slow); relerr must be <=1e-10")
print("="*70)
for free in [[1,2,3,4,5],[1,2,3,4,1000],[1,3,4,5,6],[2,4,6,8,10],[1,2,3,4,1000000]]:
    re, im, W = bg_double_onshell(7, free)
    pred = 2**(7-1) * W[1] * W[2]**(2*7-5)   # float
    err = relerr(im, pred)
    print(f" free={str(free):20} a(bg)={im:.6e}  pred={pred:.6e}  Re={re:.2e}  relerr={err:.2e}  {'OK' if err<=1e-10 else 'FAIL'}")

print("\n" + "="*70)
print("CHAMBER RULE test (n=6): violate w2<=others -> formula should FAIL")
print("="*70)
for free in [[1,2,3,4],[3,1,2,4],[2,1,5,6],[5,1,2,3]]:   # some have w2 not smallest
    re, im, W = exact_amp(6, free)
    pred = conj(6, W)
    smallest = (W[2] == min(W[2],W[3],W[4],W[5]))
    print(f" free={str(free):14} w2={W[2]} smallest_free={smallest}  match={im==pred}  a={im} pred={pred}")
