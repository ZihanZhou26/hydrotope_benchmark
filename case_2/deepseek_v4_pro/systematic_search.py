"""
Systematic data generation for two-minus sector.
Focus on finding the polynomial formula.
"""
from fractions import Fraction
from itertools import permutations, combinations
import math, time

# ====== All the BG functions (same as before) ======
def mag(k): return abs(k)

_EK = {}; _FK = {}

def EKernel(n, ps):
    key = (n, tuple(ps))
    if key in _EK: return _EK[key]
    if n == 3:
        p1, p2 = ps[0], ps[1]
        result = -Fraction(1, 2) * (mag(p1) * mag(p2) + p1 * p2)
    else:
        p1, p2 = ps[0], ps[1]
        rest = list(ps[2:])
        qp2 = mag(p2)
        if qp2 == 0:
            _EK[key] = Fraction(0)
            return Fraction(0)
        result = qp2**(n-3) * EKernel(3, [p1, p2, sum(rest)]) / math.factorial(n-2)
        for m in range(1, n-2):
            new_ps = [p1, p2 + sum(rest[:m])] + rest[m:]
            result -= (qp2**m) / math.factorial(m) * EKernel(n-m, new_ps)
    _EK[key] = result
    return result

def FKernel(n, ps):
    key = (n, tuple(ps))
    if key in _FK: return _FK[key]
    if n == 3:
        p1, p2 = ps[0], ps[1]
        q1, q2 = mag(p1), mag(p2)
        if q1 * q2 == 0: result = Fraction(0)
        else: result = -1 - Fraction(p1 * p2, q1 * q2)
    else:
        p1, p2 = ps[0], ps[1]
        rest = list(ps[2:])
        qp1, qp2 = mag(p1), mag(p2)
        if qp1 == 0 or qp2 == 0:
            _FK[key] = Fraction(0)
            return Fraction(0)
        result = 2 * EKernel(n, ps) / qp1
        for m in range(1, n-2):
            sigM = p2 + sum(rest[:m])
            ek = EKernel(m+2, [-sigM, p2] + rest[:m])
            fk = FKernel(n-m, [p1, sigM] + rest[m:])
            result -= 2 * ek * fk
        result = result / qp2
    _FK[key] = result
    return result

def Vertex(n, moms, omegas):
    result = Fraction(0)
    for p in permutations(range(n)):
        pm = [moms[i] for i in p]
        po = [omegas[i] for i in p]
        result += po[0] * po[1] * FKernel(n, pm)
    return Fraction(-1, 2) * result

def Propagator(omega, k, g):
    mk = mag(k)
    if mk == 0:
        if omega == 0: return None
        return Fraction(0)
    denom = omega * omega / mk - g
    if float(abs(denom)) < 1e-15: return None
    return Fraction(-1, denom)

def _subsets_of_size_range(items, mi, ma):
    for sz in range(mi, ma+1):
        for combo in combinations(items, sz):
            yield list(combo)

def set_partitions(S, k):
    if k == 1: return [[list(S)]]
    if k > len(S): return []
    S = list(S); mn = min(S)
    rest = [x for x in S if x != mn]
    result = []
    for sub in _subsets_of_size_range(rest, 0, len(S) - k):
        fp = [mn] + sub
        rem = [x for x in S if x not in fp]
        if len(rem) >= k - 1:
            for sp in set_partitions(rem, k-1):
                result.append([fp] + sp)
    return result

def BGAmplitude_safe(momenta, omegas, g):
    global _EK, _FK; _EK.clear(); _FK.clear()
    n = len(momenta)
    cache = {}
    
    def BGCurrent(S):
        key = tuple(sorted(S))
        if key in cache: return cache[key]
        Sl = list(S)
        if len(Sl) == 1:
            cache[key] = Fraction(1)
            return Fraction(1)
        omegaS = sum(omegas[i-1] for i in Sl)
        kS = sum(momenta[i-1] for i in Sl)
        result = Fraction(0)
        for m in range(2, len(Sl)+1):
            for part in set_partitions(Sl, m):
                sM = [sum(momenta[j-1] for j in s) for s in part]
                sO = [sum(omegas[j-1] for j in s) for s in part]
                vM = [-kS] + sM; vO = [-omegaS] + sO
                prod = Fraction(1)
                for j in range(m):
                    bc = BGCurrent(tuple(part[j]))
                    if bc is None: prod = None; break
                    prod *= bc
                if prod is None: continue
                result += Vertex(m+1, vM, vO) * prod
        prop = Propagator(omegaS, kS, g)
        if prop is None: return None
        result *= prop
        cache[key] = result
        return result
    
    rest = list(range(2, n+1))
    result = Fraction(0)
    for m in range(2, n):
        for part in set_partitions(rest, m):
            sM = [sum(momenta[j-1] for j in s) for s in part]
            sO = [sum(omegas[j-1] for j in s) for s in part]
            vM = [momenta[0]] + sM; vO = [omegas[0]] + sO
            prod = Fraction(1)
            for j in range(m):
                bc = BGCurrent(tuple(part[j]))
                if bc is None: prod = None; break
                prod *= bc
            if prod is None: continue
            result += Vertex(m+1, vM, vO) * prod
    return result


def compute_n5_exact(freeW):
    """Compute A5 for two-minus sector with given freeW = [w2, w3, w4]."""
    g = 1
    freeWf = [Fraction(w) for w in freeW]
    sumFree = sum(freeWf)
    sumSigmaW2 = -freeWf[0]**2 + sum(w**2 for w in freeWf[1:])
    wn = (sumSigmaW2 - sumFree**2) / (2 * sumFree)
    w1 = -(sumFree + wn)
    allW = [w1, freeWf[0], freeWf[1], freeWf[2], wn]
    allK = [-w1**2, -freeWf[0]**2, freeWf[1]**2, freeWf[2]**2, wn**2]
    
    amp = BGAmplitude_safe(allK, allW, g)
    if amp is None:
        return None
    return allW, allK, amp


print("=== Generating systematic n=5 data ===")

# Generate data for many integer w2, w3, w4 values
results = []
for w2 in range(1, 9):
    for w3 in range(1, 9):
        for w4 in range(1, 9):
            if w2 == w3 == w4:
                continue
            res = compute_n5_exact([w2, w3, w4])
            if res is None:
                continue
            allW, allK, amp = res
            wf = [float(w) for w in allW]
            af = float(amp)
            
            # Compute theoretical candidates
            w2v, w3v, w4v = float(allW[1]), float(allW[2]), float(allW[3])
            w1v, w5v = wf[0], wf[4]
            
            results.append({
                'w': wf, 'w_exact': allW, 'amp': af
            })

print(f"Generated {len(results)} data points")

# Try to find the formula
# Based on FKernel property, the amplitude might be proportional to:
# P * (product of ω_i) where P is a polynomial
# Or something like (ω_1 ω_2 - ω_3 ω_4 ω_5 ...)

# Let me try: is A_n proportional to ω_1 * ω_2 * (some symmetric function)?
# And is the sign determined by ordering?

import numpy as np

# For each point, compute various candidate expressions
print("\n=== Testing candidate formulas ===")

# Candidate 1: A_n = C * (ω_1 * ω_2)^(n-3) * (symmetric polynomial in all ω)?
# Let's just print some data for analysis
for r in results[:20]:
    wf = r['w']
    amp = r['amp']
    
    w_prod = wf[0]*wf[1]*wf[2]*wf[3]*wf[4]
    w12 = wf[0]*wf[1]
    w345 = wf[2]*wf[3]*wf[4]
    
    # Try dividing by various monomials
    print(f"w={[f'{x:.2f}' for x in wf]}, A={amp:.2f}")
    print(f"  A/prod = {amp/w_prod:.4f}, A/(w1*w2^3*w3) = {amp/(wf[0]*wf[1]**3*wf[2]):.4f}")
    
    # The amplitude might be proportional to (w3^2 + w4^2 + w5^2 - w1^2 - w2^2) or similar
    sum_sq_plus = wf[2]**2 + wf[3]**2 + wf[4]**2
    sum_sq_minus = wf[0]**2 + wf[1]**2
    # Actually, from momentum conservation: w1^2 + w2^2 = w3^2 + w4^2 + w5^2
    # So sum_sq_plus - sum_sq_minus = 0 by conservation!

print("\n=== Looking for sign pattern ===")
# The sign might depend on the ordering of |w2| vs |w3|, |w4|
for r in results:
    wf = r['w']
    amp = r['amp']
    w2, w3, w4 = abs(wf[1]), abs(wf[2]), abs(wf[3])
    
    # Sign of intermediate momenta
    # k_{2,3} = -w2^2 + w3^2, sign is sign(w3 - w2)
    k23_sign = 1 if w3 > w2 else (-1 if w3 < w2 else 0)
    k24_sign = 1 if w4 > w2 else (-1 if w4 < w2 else 0)
    k234_sign = 1 if (w3**2 + w4**2) > w2**2 else (-1 if (w3**2 + w4**2) < w2**2 else 0)
    
    sign_pattern = (k23_sign, k24_sign, k234_sign)
    
    print(f"  w2={w2:.1f}, w3={w3:.1f}, w4={w4:.1f}, sign(k23,k24,k234)={sign_pattern}, A={amp:.2f}")
