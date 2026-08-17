"""
Comprehensive polynomial fitting to find closed-form A_n in two-minus sector.
"""
from fractions import Fraction as F
from itertools import permutations, combinations
import math, time
import numpy as np

def mag(k): return abs(k)
_EK = {}; _FK = {}

def EKernel(n, ps):
    key = (n, tuple(ps))
    if key in _EK: return _EK[key]
    if n == 3:
        p1, p2 = ps[0], ps[1]
        result = -F(1, 2) * (mag(p1) * mag(p2) + p1 * p2)
    else:
        p1, p2 = ps[0], ps[1]
        rest = list(ps[2:])
        qp2 = mag(p2)
        if qp2 == 0: _EK[key]=F(0); return F(0)
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
        if q1 * q2 == 0: result = F(0)
        else: result = -1 - F(p1 * p2, q1 * q2)
    else:
        p1, p2 = ps[0], ps[1]
        rest = list(ps[2:])
        qp1, qp2 = mag(p1), mag(p2)
        if qp1 == 0 or qp2 == 0: _FK[key]=F(0); return F(0)
        result = 2 * EKernel(n, ps) / qp1
        for m in range(1, n-2):
            sigM = p2 + sum(rest[:m])
            if mag(sigM) == 0: continue
            ek = EKernel(m+2, [-sigM, p2] + rest[:m])
            fk = FKernel(n-m, [p1, sigM] + rest[m:])
            result -= 2 * ek * fk
        result = result / qp2
    _FK[key] = result
    return result

def Vertex(n, moms, omegas):
    result = F(0)
    for p in permutations(range(n)):
        pm = [moms[i] for i in p]
        po = [omegas[i] for i in p]
        result += po[0] * po[1] * FKernel(n, pm)
    return F(-1, 2) * result

def Propagator(omega, k, g):
    mk = mag(k)
    if mk == 0: return None
    denom = omega * omega / mk - g
    if denom == 0: return None
    return F(-1, denom)

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

def BGAmplitude_robust(momenta, omegas, g):
    global _EK, _FK
    _EK.clear(); _FK.clear()
    n = len(momenta)
    cache = {}
    def BGCurrent(S):
        key_ = tuple(sorted(S))
        if key_ in cache: return cache[key_]
        Sl = list(S)
        if len(Sl) == 1:
            cache[key_] = F(1)
            return F(1)
        omegaS = sum(omegas[i-1] for i in Sl)
        kS = sum(momenta[i-1] for i in Sl)
        prop = Propagator(omegaS, kS, g)
        if prop is None:
            cache[key_] = None
            return None
        result = F(0)
        has_contrib = False
        for m in range(2, len(Sl)+1):
            for part in set_partitions(Sl, m):
                sM = [sum(momenta[j-1] for j in subset) for subset in part]
                sO = [sum(omegas[j-1] for j in subset) for subset in part]
                vM = [-kS] + sM; vO = [-omegaS] + sO
                prod = F(1)
                ok = True
                for j in range(m):
                    bc = BGCurrent(tuple(part[j]))
                    if bc is None: ok = False; break
                    prod *= bc
                if ok:
                    result += Vertex(m+1, vM, vO) * prod
                    has_contrib = True
        if not has_contrib:
            cache[key_] = None
            return None
        result *= prop
        cache[key_] = result
        return result
    rest = list(range(2, n+1))
    result = F(0)
    for m in range(2, n):
        for part in set_partitions(rest, m):
            sM = [sum(momenta[j-1] for j in subset) for subset in part]
            sO = [sum(omegas[j-1] for j in subset) for subset in part]
            vM = [momenta[0]] + sM; vO = [omegas[0]] + sO
            prod = F(1)
            ok = True
            for j in range(m):
                bc = BGCurrent(tuple(part[j]))
                if bc is None: ok = False; break
                prod *= bc
            if ok:
                result += Vertex(m+1, vM, vO) * prod
    return result

def make_kinematics(n, freeW, g=1):
    freeW = list(freeW)
    if len(freeW) != n-2: return None
    sumFree = sum(freeW)
    if float(abs(sumFree)) < 1e-12: return None
    sumSigmaW2 = -freeW[0]**2 + sum(w**2 for w in freeW[1:])
    wn = (sumSigmaW2 - sumFree**2) / (2 * sumFree)
    w1 = -(sumFree + wn)
    allW = [w1] + freeW + [wn]
    allK = [-w1**2/g, -freeW[0]**2/g] + [w**2/g for w in freeW[1:]] + [wn**2/g]
    return list(allK), list(allW)

# ============ Analysis ============
print("=== ANALYZING A_n STRUCTURE ===")

# Key insight from FKernel: for permutations where two minus legs are first,
# FKernel[n, {k1,k2,k3,...,kn}] depends on the signs of partial sums
# k2+k3, k2+k3+k4, ..., k2+...+k_{n-1}

# The "maximally negative" chamber: ALL partial sums negative
# Corresponds to w2^2 > w3^2 + w4^2 + ... + w_{n-1}^2
# In this chamber, all intermediate states keep the same sign as k2

# Let me compute A_n in this specific chamber for n=5,6,7

def compute_chamber_amplitude(n, w2_val, plus_vals, g=1):
    """Compute amplitude with given w2 and plus leg values."""
    freeW = [F(w2_val)] + [F(v) for v in plus_vals]
    res = make_kinematics(n, freeW, g)
    if res is None: return None
    allK, allW = res
    # Check that ALL partial sums k2+k3, k2+k3+k4, ..., k2+...+k_{n-1} are negative
    # This ensures we're in the "maximally negative" chamber
    ks = allK
    for j in range(2, n):
        partial = sum(float(ks[i]) for i in range(1, j+1))
        if partial > -1e-10:  # not sufficiently negative
            return None
    amp = BGAmplitude_robust(allK, allW, g)
    if amp is None: return None
    return [float(x) for x in allW], float(amp), [float(x) for x in allK]

# Find a point in the "maximally negative" chamber for n=5
# Need w2^2 > w3^2 + w4^2
for w2 in [4,5,6,7]:
    for w3 in [1,2]:
        for w4 in [1,2]:
            if w2*w2 <= w3*w3 + w4*w4: continue
            result = compute_chamber_amplitude(5, w2, [w3, w4])
            if result is not None:
                wf, af, kf = result
                D = wf[1]**2 - wf[2]**2 - wf[3]**2
                # Verify all partial sums are negative
                ok = True
                for j in range(2, 5):
                    part_k = sum(kf[i] for i in range(1, j+1))
                    if part_k > -1e-10:
                        ok = False
                if ok:
                    print(f"\nn=5 max-neg chamber: w2={w2}, w3={w3}, w4={w4}")
                    print(f"  w = {[f'{x:.4f}' for x in wf]}")
                    print(f"  A5 = {af:.4f}")
                    print(f"  D = {D:.4f}")
                    # Try to see the polynomial structure
                    w1,w2v,w3v,w4v,w5v = wf
                    # w1*w2 = ?
                    w12 = w1*w2v
                    # Σ w_i^2 for plus legs
                    S2plus = w3v**2 + w4v**2 + w5v**2
                    print(f"  w1*w2 = {w12:.4f}")
                    print(f"  S2plus = {S2plus:.4f}")
                    print(f"  A5/(w1*w2) = {af/w12:.4f}")
                    print(f"  A5/(w1*w2*S2plus) = {af/(w12*S2plus):.4f}")
                    print(f"  A5/(w1*w2*S2plus^2) = {af/(w12*S2plus**2):.4f}")
                    # Also try (w1^2 + w2^2):
                    S2minus = w1**2 + w2v**2
                    print(f"  S2minus = {S2minus:.4f}")
                    print(f"  A5/(w1*w2*(S2plus - S2minus)) = {af/(w12*(S2plus-S2minus)):.4f}")
                    break
        else:
            continue
        break

# Now try n=6
print("\n--- n=6 ---")
for w2 in [5,6,7,8]:
    for w3 in [1]:
        for w4 in [1]:
            for w5f in [1]:
                if w2*w2 <= w3*w3 + w4*w4 + w5f*w5f: continue
                result = compute_chamber_amplitude(6, w2, [w3, w4, w5f])
                if result is not None:
                    wf, af, kf = result
                    # verify chamber
                    ok = True
                    for j in range(2, 6):
                        part_k = sum(kf[i] for i in range(1, j+1))
                        if part_k > -1e-10:
                            ok = False
                    if ok:
                        print(f"n=6: w2={w2}, plus=[{w3},{w4},{w5f}]")
                        w1,w2v,w3v,w4v,w5v,w6v = wf
                        w12 = w1*w2v
                        S2plus = w3v**2 + w4v**2 + w5v**2 + w6v**2
                        print(f"  w = {[f'{x:.4f}' for x in wf]}")
                        print(f"  A6 = {af:.4f}")
                        print(f"  w1*w2 = {w12:.4f}, S2plus = {S2plus:.4f}")
                        print(f"  A6/(w1*w2) = {af/w12:.4f}")
                        print(f"  A6/(w1*w2*S2plus) = {af/(w12*S2plus):.4f}")
                        print(f"  A6/(w1*w2*S2plus^2) = {af/(w12*S2plus**2):.4f}")
                        print(f"  A6/(w1*w2*S2plus^3) = {af/(w12*S2plus**3):.4f}")
                        break
        else:
            continue
        break

# Also try the "maximally positive" chamber
# Where w2^2 is very small relative to the plus legs
print("\n=== Opposite chamber (w2 small, plus large) ===")
for w2 in [1]:
    for w3 in [3,4]:
        for w4 in [3,4]:
            result = compute_chamber_amplitude(5, w2, [w3, w4])
            if result is not None:
                wf, af, kf = result
                # Check that k2+k3 > 0 and k2+k3+k4 > 0
                k23 = kf[1] + kf[2]
                k234 = kf[1] + kf[2] + kf[3]
                if k23 > 1e-10 and k234 > 1e-10:
                    w1,w2v,w3v,w4v,w5v = wf
                    print(f"n=5 small-w2: w2={w2}, plus=[{w3},{w4}]")
                    print(f"  w = {[f'{x:.4f}' for x in wf]}")
                    print(f"  A5 = {af:.4f}")
                    w12 = w1*w2v
                    S2plus = w3v**2 + w4v**2 + w5v**2
                    print(f"  w1*w2 = {w12:.4f}, S2plus = {S2plus:.4f}")
                    print(f"  A5/(|w1*w2|*S2plus^2) = {af/(abs(w12)*S2plus**2):.4f}")
                    break

