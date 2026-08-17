#!/usr/bin/env python3
"""Modular (F_p) port of the BG amplitude recursion (bg.cpp / pybg.py).

WHY: exact GMP at n=7 blows up (~23 s/eval); ./bg --batch ~1 s/eval. Both too slow for a
deg-22 fit (1000+ pts). KEY OBSERVATION: every abs()/sign in the BG recursion applies ONLY to
EXTERNAL-derived momenta (sums of the external k_i, which are small rationals), NEVER to kernel
VALUES. So we keep momenta/frequencies as exact Fractions (for abs, powers, memo keys) and carry
the blow-up KERNEL VALUES (E,F,Vertex,BGCurrent,amplitude) mod a large prime p. This is EXACT in
F_p (no float!), so a modular fit + rational reconstruction is rigorous -- the team's own method.

Validated == ./bg (reduced mod p) at n=5,6,7 below.  ~ms/eval.
"""
from fractions import Fraction as F
from math import factorial
import itertools

P = 2**61 - 1
def fp(fr):
    """Fraction -> residue mod P (raises if denominator divisible by P)."""
    if isinstance(fr, int):
        return fr % P
    n, d = fr.numerator % P, fr.denominator % P
    if d == 0:
        raise ZeroDivisionError("denominator divisible by P")
    return (n * pow(d, P-2, P)) % P

class MBG:
    def __init__(self, K, W, G=F(1), p=P):
        # K,W: 1-indexed Fraction lists (index 0 unused). G: Fraction.
        self.K = K; self.W = W; self.G = G; self.p = p
        self.Em = {}; self.Fm = {}; self.BGm = {}
        self.gfp = fp(G)
    # ---- kernels return residues mod p; momentum args ps stay Fractions ----
    def EKernel(self, n, ps):
        if n == 3:
            a = abs(ps[0])*abs(ps[1]) + ps[0]*ps[1]
            return (fp(F(-1, 2)) * fp(a)) % P
        key = (n, ps); v = self.Em.get(key)
        if v is not None: return v
        p1, p2, rest = ps[0], ps[1], ps[2:]
        qp2 = abs(p2); rs = sum(rest, F(0))
        # qp2^(n-3) * E3(p1,p2,rs) / (n-2)!
        res = (fp(qp2**(n-3)) * self.EKernel(3, (p1, p2, rs))) % P
        res = (res * pow(factorial(n-2), P-2, P)) % P
        for m in range(1, n-2):
            part = sum(rest[:m], F(0))
            nl = (p1, p2+part) + tuple(rest[m:])
            term = (fp(qp2**m) * pow(factorial(m), P-2, P)) % P
            term = (term * self.EKernel(n-m, nl)) % P
            res = (res - term) % P
        self.Em[key] = res; return res
    def FKernel(self, n, ps):
        if n == 3:
            # -1 - p0 p1/(|p0||p1|) = -1 - sign(p0)sign(p1)  (exact integer 0 or -2)
            s0 = 0 if ps[0] == 0 else (1 if ps[0] > 0 else -1)
            s1 = 0 if ps[1] == 0 else (1 if ps[1] > 0 else -1)
            return (-1 - s0*s1) % P
        key = (n, ps); v = self.Fm.get(key)
        if v is not None: return v
        p1, p2, rest = ps[0], ps[1], ps[2:]
        qp1, qp2 = abs(p1), abs(p2)
        res = (2 * self.EKernel(n, ps)) % P
        res = (res * fp(F(1,1)/qp1)) % P
        for m in range(1, n-2):
            part = sum(rest[:m], F(0)); sigM = p2 + part
            el = (-sigM, p2) + tuple(rest[:m])
            fl = (p1, sigM) + tuple(rest[m:])
            term = (2 * self.EKernel(m+2, el)) % P
            term = (term * self.FKernel(n-m, fl)) % P
            res = (res - term) % P
        res = (res * fp(F(1,1)/qp2)) % P
        self.Fm[key] = res; return res
    def Vertex(self, n, moms, om):
        acc = 0
        omfp = [fp(x) for x in om]
        for perm in itertools.permutations(range(n)):
            pm = tuple(moms[i] for i in perm)
            t = (omfp[perm[0]] * omfp[perm[1]]) % P
            t = (t * self.FKernel(n, pm)) % P
            acc = (acc + t) % P
        # imaginary part only: Vertex = (0, -acc/2)
        return (-acc * pow(2, P-2, P)) % P
    def Propagator(self, wS, kS):
        D = wS*wS/abs(kS) - self.G            # Fraction
        return (-fp(F(1,1)/D)) % P            # imaginary coeff -1/D
    def BGCurrent(self, S):
        # returns imaginary residue mod p (re part is 0 for these currents on-shell);
        # we track full complex via (re,im) mod p.
        if len(S) == 1: return (1, 0)
        mask = 0
        for i in S: mask |= (1 << i)
        v = self.BGm.get(mask)
        if v is not None: return v
        wS = sum(self.W[i] for i in S); kS = sum(self.K[i] for i in S)
        re, im = 0, 0
        for m in range(2, len(S)+1):
            for part in setpartitions(S, m):
                vM = [-kS]; vO = [-wS]
                for blk in part:
                    vM.append(sum(self.K[i] for i in blk)); vO.append(sum(self.W[i] for i in blk))
                vx_im = self.Vertex(m+1, vM, vO)         # (0, vx_im)
                pr_re, pr_im = 1, 0
                for blk in part:
                    bre, bim = self.BGCurrent(blk)
                    pr_re, pr_im = (pr_re*bre - pr_im*bim) % P, (pr_re*bim + pr_im*bre) % P
                # (0,vx_im)*(pr_re,pr_im) = (-vx_im*pr_im, vx_im*pr_re)
                re = (re - vx_im*pr_im) % P
                im = (im + vx_im*pr_re) % P
        prop_im = self.Propagator(wS, kS)                # (0, prop_im)
        # (re,im)*(0,prop_im) = (-im*prop_im, re*prop_im)
        nre = (-im*prop_im) % P; nim = (re*prop_im) % P
        self.BGm[mask] = (nre, nim); return (nre, nim)
    def amplitude(self, N):
        self.BGm = {}; self.Em = {}; self.Fm = {}
        rest = list(range(2, N+1)); re, im = 0, 0
        for m in range(2, N):
            for part in setpartitions(rest, m):
                vM = [self.K[1]]; vO = [self.W[1]]
                for blk in part:
                    vM.append(sum(self.K[i] for i in blk)); vO.append(sum(self.W[i] for i in blk))
                vx_im = self.Vertex(m+1, vM, vO)
                pr_re, pr_im = 1, 0
                for blk in part:
                    bre, bim = self.BGCurrent(blk)
                    pr_re, pr_im = (pr_re*bre - pr_im*bim) % P, (pr_re*bim + pr_im*bre) % P
                re = (re - vx_im*pr_im) % P
                im = (im + vx_im*pr_re) % P
        return (re, im)

def setpartitions(S, k):
    S = tuple(S)
    if k == 1: return [[list(S)]]
    if k > len(S): return []
    mn = min(S); X = [x for x in S if x != mn]; xs = len(X); Ln = len(S); out = []
    for mask in range(1 << xs):
        if bin(mask).count('1') > Ln-k: continue
        fp_ = [mn]+[X[b] for b in range(xs) if mask & (1 << b)]
        fps = set(fp_); fp_ = sorted(fp_)
        rem = [v for v in S if v not in fps]
        if len(rem) >= k-1:
            for spp in setpartitions(rem, k-1):
                out.append([fp_]+spp)
    return out

def amp_onshell_modp(free, signs, g=F(1)):
    """Returns im(A_n) mod P (matching pybg's im, reduced mod P)."""
    free = [F(x) for x in free]; signs = [F(s) for s in signs]; N = len(signs)
    s1 = signs[0]; sumFree = sum(free)
    sumSig = sum(signs[i+1]*free[i]*free[i] for i in range(N-2))
    wn = -(s1*sumFree*sumFree + sumSig)/(2*s1*sumFree)
    w1 = -(sumFree + wn)
    W = [F(0)]*(N+1); K = [F(0)]*(N+1)
    W[1] = w1
    for i in range(N-2): W[i+2] = free[i]
    W[N] = wn
    for i in range(1, N+1): K[i] = signs[i-1]*W[i]*W[i]/g
    mbg = MBG(K, W, g)
    re, im = mbg.amplitude(N)
    return im, [W[i] for i in range(1, N+1)]

if __name__ == "__main__":
    import time, pybg, n7lib as L
    print("validate modbg == pybg (== ./bg) reduced mod P, n=5,6,7")
    tests = [
        ([F(2),F(3),F(5)], [-1,-1,-1,1,1]),
        ([F(2),F(3),F(5),F(7)], [-1,-1,-1,1,1,1]),
        ([F(11,3),F(-7,2),F(9,5),F(13,4)], [-1,-1,-1,1,1,1]),
        ([F(2),F(3),F(5),F(7),F(11,2)], [-1,-1,-1,1,1,1,1]),
        ([F(-13,7),F(5,2),F(8,3),F(7),F(11,2)], [-1,-1,-1,1,1,1,1]),
    ]
    allok = True
    for free, sig in tests:
        im_p, oms = pybg.amp_onshell(free, sig)[0], pybg.amp_onshell(free, sig)[1]
        im_m, _ = amp_onshell_modp(free, sig)
        ok = (fp(im_p) == im_m); allok = allok and ok
        print(f"  n={len(sig)}: pybg%P={fp(im_p)}  modbg={im_m}  match={ok}")
    print("ALL MATCH:", allok)
    free = [F(2),F(3),F(5),F(7),F(11,2)]; sig = [-1,-1,-1,1,1,1,1]
    t0 = time.time()
    for _ in range(20): amp_onshell_modp(free, sig)
    print(f"modbg n=7: {(time.time()-t0)/20*1000:.1f} ms/eval")
