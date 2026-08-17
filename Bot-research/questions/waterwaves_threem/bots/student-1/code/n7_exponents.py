#!/usr/bin/env python3
"""ROBUST single-wall jump-exponent measurement, n=6 (control) and n=7 (target).
Multiple base points per wall orbit; enforce sign-diff=1; require >= deg+6 in-chamber
points per side; EXACT rational. Reports the jump order = truncated-power exponent.

Wall orbit naming (p minus = q plus), reduced mod complement:
  n=6 (minus {1,2,3}, plus {4,5,6}): (1=1), (1=2)[==(2=1)]
  n=7 (minus {1,2,3}, plus {4,5,6,7}): (1=1), (1=2)[==(2=2)], (1=3)[==(2=1)]
"""
from fractions import Fraction as F
import sympy as sp, itertools, subprocess, os
import r5lib as RL

t = sp.Symbol('t')
HERE = os.path.dirname(os.path.abspath(__file__)); BG = os.path.join(HERE, "bg")

def solve(free, n):
    free = [F(x) for x in free]; s1 = F(-1); sumFree = sum(free)
    if sumFree == 0: return None
    sg = [-1, -1] + [1]*(n-4)   # legs 2..(n-1) signs (legs 2,3 minus; rest plus)
    sumSig = sum(sg[i]*free[i]**2 for i in range(n-2))
    wn = -(s1*sumFree**2 + sumSig)/(2*s1*sumFree)
    w1 = -(sumFree + wn)
    return [w1] + free + [wn]

def batch_amp(frees, n):
    sig = [-1, -1, -1] + [1]*(n-3)
    lines = [f"{n}|" + ",".join(str(F(x)) for x in fr) + "|" + ",".join(str(s) for s in sig) for fr in frees]
    out = subprocess.run([BG, "--batch"], input="\n".join(lines).encode(),
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode()
    res = []
    for ln in out.strip().split("\n"):
        if ln in ("ERR", ""): res.append(None); continue
        res.append(F(ln.split(";")[1]))
    return res

def Dmin_factors(oms, n):
    """full mixed-pair product (works as denominator for n>=7; for n=6 it's (e3m+e3p)^3
    but A*D is still polynomial)."""
    M = [0,1,2]; P = list(range(3, n))
    d = F(1)
    for i in M:
        for j in P: d *= (oms[i]+oms[j])
    return d

def Nval(oms, im, n):
    """N = A * D_full / (i 2^{n-1}); use the full mixed product so A*D is polynomial."""
    return F(im) * Dmin_factors(oms, n) / (2**(n-1))

def all_wall_signs(oms, n):
    """signs of all mixed subset-sum walls f = sum_plus b - sum_minus a (canonical reps);
    returns tuple or None if on a wall."""
    sq = [w*w for w in oms]; M = [0,1,2]; P = list(range(3, n))
    sgn = []
    for sm_size in (1, 2):
        for sm in itertools.combinations(M, sm_size):
            for sp_size in range(1, len(P)+1):
                for spp in itertools.combinations(P, sp_size):
                    v = sum(sq[j] for j in spp) - sum(sq[i] for i in sm)
                    if v == 0: return None
                    sgn.append(1 if v > 0 else -1)
    return tuple(sgn)

def chamber_sig(free, n):
    o = solve(free, n)
    if o is None or any(w == 0 for w in o): return None
    return all_wall_signs(o, n)

def collect(base, p, q, A, B, direction, step, maxn, ref, n):
    frees = []; omsl = []
    for k in range(1, maxn+1):
        fr = list(F(x) for x in base); fr[p] = F(A)+direction*step*k; fr[q] = F(B)-direction*step*k
        o = solve(fr, n)
        if o is None or any(w == 0 for w in o): break
        s = all_wall_signs(o, n)
        if s is None or s != ref: break
        frees.append((direction*step*k, fr)); omsl.append(o)
    if not frees: return []
    ims = batch_amp([fr for (_, fr) in frees], n)
    return [(tt, Nval(o, im, n)) for ((tt, _), o, im) in zip(frees, omsl, ims) if im is not None]

def measure(name, base, p, q, A, B, n, step=F(1,80), maxn=42, dmax=50):
    frL = list(F(x) for x in base); frL[p]=F(A)-step/4; frL[q]=F(B)+step/4
    frR = list(F(x) for x in base); frR[p]=F(A)+step/4; frR[q]=F(B)-step/4
    sL = chamber_sig(frL, n); sR = chamber_sig(frR, n)
    if sL is None or sR is None: print(f"  [{name}] degenerate"); return None
    sd = sum(1 for a, b in zip(sL, sR) if a != b)
    ptsL = collect(base, p, q, A, B, -1, step, maxn, sL, n)
    ptsR = collect(base, p, q, A, B, +1, step, maxn, sR, n)
    cL = RL.fit_poly(ptsL, dmax); cR = RL.fit_poly(ptsR, dmax)
    if cL is None or cR is None:
        print(f"  [{name}] sd={sd} FIT FAIL nL={len(ptsL)} nR={len(ptsR)} (polyL={cL is not None},polyR={cR is not None})")
        return None
    NL = sum(sp.Rational(c.numerator, c.denominator)*t**j for j, c in enumerate(cL))
    NR = sum(sp.Rational(c.numerator, c.denominator)*t**j for j, c in enumerate(cR))
    d = sp.expand(NR - NL)
    if d == 0:
        print(f"  [{name}] sd={sd} nL={len(ptsL)} nR={len(ptsR)} -> SMOOTH"); return (sd, 0)
    P = sp.Poly(d, t); order = 0; nn = P
    while nn.eval(0) == 0 and nn.degree() > 0: nn = nn.diff(t); order += 1
    flag = "" if sd == 1 else "  <-- NOT single-wall!"
    print(f"  [{name}] sd={sd} nL={len(ptsL)} nR={len(ptsR)} degs=({len(cL)-1},{len(cR)-1}) -> EXPONENT = {order}{flag}")
    return (sd, order)

if __name__ == "__main__":
    print("=== n=6 CONTROL (expect (1=1)->1, (1=2)->3) ===")
    # free=[w2,w3,w4,w5]; idx 0,1 minus; 2,3 plus
    measure("n6 (1=1) a2=b4", [F(3),F(5),F(3),F(15,2)], 2, 3, F(3), F(15,2), 6)
    measure("n6 (1=1) a2=b4 alt", [F(4),F(5),F(4),F(17,2)], 2, 3, F(4), F(17,2), 6)
    # (1=2): a2=b4+b5 -> w2^2=w4^2+w5^2 ; w4=3,w5=4->25,w2=5; vary w4, comp w3(minus,not in wall)
    measure("n6 (1=2) a2=b4+b5", [F(5),F(11,3),F(3),F(4)], 2, 1, F(3), F(11,3), 6)

    print("\n=== n=7 TARGET ===")
    # free=[w2,w3,w4,w5,w6]; idx 0,1 minus; 2,3,4 plus
    # (1=1) a2=b4: vary w4, comp w5
    measure("n7 (1=1) a2=b4", [F(3),F(5),F(3),F(8),F(11,2)], 2, 3, F(3), F(8), 7)
    measure("n7 (1=1) a3=b4 alt", [F(5),F(3),F(3),F(17,2),F(6)], 2, 4, F(3), F(6), 7)
    # (1=2) a2=b4+b5: w2^2=w4^2+w5^2; w4=3,w5=4,w2=5; vary w4, comp w6(plus,not in wall)
    measure("n7 (1=2) a2=b4+b5", [F(5),F(11,3),F(3),F(4),F(15,2)], 2, 4, F(3), F(15,2), 7)
    measure("n7 (1=2) a2=b4+b5 alt", [F(13,2),F(7,3),F(5),F(7,2),F(9)], 2, 4, F(5), F(9), 7)
    # (1=3) a2=b4+b5+b6: w2^2=w4^2+w5^2+w6^2; w4=2,w5=3,w6=6 ->49,w2=7; vary w2(minus), comp w3(minus,not in wall)
    measure("n7 (1=3) a2=b4+b5+b6", [F(7),F(9,2),F(2),F(3),F(6)], 0, 1, F(7), F(9,2), 7)
    measure("n7 (1=3) a2=b4+b5+b6 alt", [F(7),F(11,2),F(6),F(2),F(3)], 0, 1, F(7), F(11,2), 7)
