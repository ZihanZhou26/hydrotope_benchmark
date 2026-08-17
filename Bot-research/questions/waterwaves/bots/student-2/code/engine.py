"""
engine.py — faithful Python port of bg.cpp (Berends-Giele water-wave oracle).

Two uses:
  * field='frac'  : exact arithmetic with fractions.Fraction (validate vs ./bg, generate data)
  * field='sympy' : symbolic; abs(.) of momentum partial-sums resolved by the sign
                    at a reference numeric point (a 'chamber'), giving the exact
                    rational function of the omega_i valid in that chamber.

Conventions mirror bg.cpp exactly:
  K[i] = sigma_i * omega_i^2 / g   (g=1 default),  W[i] = omega_i,  1-indexed.
  i enters only via Vertex (-i/2) and Propagator (-i).
"""
from fractions import Fraction
from itertools import permutations
from functools import lru_cache
import sympy as sp


# ---------- set partitions of a list S into exactly k nonempty blocks ----------
def set_partitions(S, k):
    S = list(S)
    n = len(S)
    if k == 1:
        yield [list(S)]
        return
    if k > n:
        return
    first, rest = S[0], S[1:]
    # put `first` in a block; choose the other members of its block from rest, the
    # remaining elements partition into k-1 blocks.
    from itertools import combinations
    m = len(rest)
    for r in range(0, m - (k - 1) + 1):       # size of first-block minus 1
        for comb in combinations(range(m), r):
            blk = [first] + [rest[j] for j in comb]
            remaining = [rest[j] for j in range(m) if j not in set(comb)]
            for sub in set_partitions(remaining, k - 1):
                yield [blk] + sub


class Engine:
    def __init__(self, field='frac', absf=None, G=1):
        self.field = field
        if field == 'frac':
            self.G = Fraction(G)
            self.absf = lambda x: abs(x)
            self.zero = Fraction(0); self.one = Fraction(1)
        else:  # sympy
            self.G = sp.Integer(G) if not hasattr(G, 'free_symbols') else G
            assert absf is not None, "sympy mode needs an absf(expr)->expr resolver"
            self.absf = absf
            self.zero = sp.Integer(0); self.one = sp.Integer(1)
        self.Em = {}
        self.Fm = {}
        self.BGm = {}

    # complex helpers: represent as (re, im) tuples in the field
    def cadd(self, a, b): return (a[0] + b[0], a[1] + b[1])
    def cmul(self, a, b): return (a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0])

    def fact(self, k):
        r = self.one
        for i in range(2, k+1):
            r = r * i
        return r

    def _key(self, n, ps):
        if self.field == 'frac':
            return (n,) + tuple(ps)
        return (n,) + tuple(sp.srepr(sp.expand(p)) for p in ps)

    def EKernel(self, n, ps):
        if n == 3:
            return (self.zero - self.one)/2 * (self.absf(ps[0])*self.absf(ps[1]) + ps[0]*ps[1])
        key = self._key(n, ps)
        if key in self.Em: return self.Em[key]
        p1, p2 = ps[0], ps[1]; rest = list(ps[2:])
        qp2 = self.absf(p2); rs = self.zero
        for r in rest: rs = rs + r
        res = qp2**(n-3) * self.EKernel(3, [p1, p2, rs]) / self.fact(n-2)
        for m in range(1, n-3+1):
            part = self.zero
            for j in range(m): part = part + rest[j]
            nl = [p1, p2+part] + rest[m:]
            res = res - qp2**m/self.fact(m) * self.EKernel(n-m, nl)
        if self.field == 'sympy': res = sp.expand(res)   # EKernel is polynomial
        self.Em[key] = res
        return res

    def FKernel(self, n, ps):
        if n == 3:
            return self.zero - self.one - ps[0]*ps[1]/(self.absf(ps[0])*self.absf(ps[1]))
        key = self._key(n, ps)
        if key in self.Fm: return self.Fm[key]
        p1, p2 = ps[0], ps[1]; rest = list(ps[2:])
        qp1 = self.absf(p1); qp2 = self.absf(p2)
        res = 2*self.EKernel(n, ps)/qp1
        for m in range(1, n-3+1):
            part = self.zero
            for j in range(m): part = part + rest[j]
            sigM = p2 + part
            el = [-sigM, p2] + rest[:m]
            fl = [p1, sigM] + rest[m:]
            res = res - 2*self.EKernel(m+2, el)*self.FKernel(n-m, fl)
        res = res/qp2
        if self.field == 'sympy': res = sp.cancel(res)
        self.Fm[key] = res
        return res

    def Vertex(self, n, moms, om):
        acc = self.zero
        idx = list(range(n))
        for p in permutations(idx):
            pm = [moms[i] for i in p]
            acc = acc + om[p[0]]*om[p[1]]*self.FKernel(n, pm)
        if self.field == 'sympy': acc = sp.cancel(acc)
        return (self.zero, -acc/2)   # (-i/2)*acc

    def Propagator(self, wS, kS):
        D = wS*wS/self.absf(kS) - self.G
        return (self.zero, -self.one/D)   # -i/D

    def BGCurrent(self, S, K, W):
        S = tuple(sorted(S))
        if len(S) == 1:
            return (self.one, self.zero)
        if S in self.BGm: return self.BGm[S]
        wS = self.zero; kS = self.zero
        for i in S: wS = wS + W[i]; kS = kS + K[i]
        result = (self.zero, self.zero)
        for m in range(2, len(S)+1):
            for part in set_partitions(S, m):
                vM = [-kS]; vO = [-wS]
                for blk in part:
                    km = self.zero; om = self.zero
                    for i in blk: km = km + K[i]; om = om + W[i]
                    vM.append(km); vO.append(om)
                v = self.Vertex(m+1, vM, vO)
                prod = (self.one, self.zero)
                for blk in part:
                    prod = self.cmul(prod, self.BGCurrent(blk, K, W))
                result = self.cadd(result, self.cmul(v, prod))
        result = self.cmul(result, self.Propagator(wS, kS))
        if self.field == 'sympy':
            result = (sp.cancel(result[0]), sp.cancel(result[1]))
        self.BGm[S] = result
        return result

    def BGAmplitude(self, N, K, W):
        # K, W are dicts/lists 1-indexed: K[1..N], W[1..N]
        self.Em.clear(); self.Fm.clear(); self.BGm.clear()
        rest = list(range(2, N+1))
        result = (self.zero, self.zero)
        for m in range(2, N-1+1):
            for part in set_partitions(rest, m):
                vM = [K[1]]; vO = [W[1]]
                for blk in part:
                    km = self.zero; om = self.zero
                    for i in blk: km = km + K[i]; om = om + W[i]
                    vM.append(km); vO.append(om)
                v = self.Vertex(m+1, vM, vO)
                prod = (self.one, self.zero)
                for blk in part:
                    prod = self.cmul(prod, self.BGCurrent(blk, K, W))
                result = self.cadd(result, self.cmul(v, prod))
        if self.field == 'sympy':
            result = (sp.cancel(result[0]), sp.cancel(result[1]))
        return result


# ---------- on-shell kinematics builder (mirrors runMode -n/-w/-s) ----------
def build_onshell(N, free_w, sigma, g=Fraction(1)):
    """free_w: list of N-2 free freqs (fills omega_2..omega_{N-1}); sigma: list of N signs.
    Returns (W, K) as 1-indexed dicts with Fraction entries."""
    free_w = [Fraction(x) for x in free_w]
    sigma = [Fraction(s) for s in sigma]
    g = Fraction(g)
    sumFree = sum(free_w)
    sumSig = sum(sigma[i+1]*free_w[i]**2 for i in range(N-2))
    wn = -(sigma[0]*sumFree*sumFree + sumSig)/(2*sigma[0]*sumFree)
    w1 = -(sumFree + wn)
    W = {1: w1}
    for i in range(N-2): W[i+2] = free_w[i]
    W[N] = wn
    K = {i: sigma[i-1]*W[i]*W[i]/g for i in range(1, N+1)}
    return W, K


def amp_onshell_frac(N, free_w, sigma, g=Fraction(1)):
    W, K = build_onshell(N, free_w, sigma, g)
    E = Engine('frac', G=g)
    re, im = E.BGAmplitude(N, K, W)
    return re, im, W, K
