"""
Polynomial fitting to find the closed-form formula for A_n in the two-minus sector.
"""
from fractions import Fraction
from itertools import permutations, combinations, combinations_with_replacement
import math, time
import numpy as np

# ===== BG functions =====
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
        if qp2 == 0: _EK[key]=Fraction(0); return Fraction(0)
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
        if qp1 == 0 or qp2 == 0: _FK[key]=Fraction(0); return Fraction(0)
        result = 2 * EKernel(n, ps) / qp1
        for m in range(1, n-2):
            sigM = p2 + sum(rest[:m])
            result -= 2 * EKernel(m+2, [-sigM, p2] + rest[:m]) * FKernel(n-m, [p1, sigM] + rest[m:])
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
        if len(Sl) == 1: cache[key]=Fraction(1); return Fraction(1)
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
                    if bc is None: prod=None; break
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
                if bc is None: prod=None; break
                prod *= bc
            if prod is None: continue
            result += Vertex(m+1, vM, vO) * prod
    return result


def compute_n5(w2v, w3v, w4v):
    """Compute A_5 exactly."""
    freeWf = [Fraction(w2v), Fraction(w3v), Fraction(w4v)]
    sumFree = sum(freeWf)
    sumSigmaW2 = -freeWf[0]**2 + sum(w**2 for w in freeWf[1:])
    wn = (sumSigmaW2 - sumFree**2) / (2 * sumFree)
    w1 = -(sumFree + wn)
    allW = [w1, freeWf[0], freeWf[1], freeWf[2], wn]
    allK = [-w1**2, -freeWf[0]**2, freeWf[1]**2, freeWf[2]**2, wn**2]
    
    amp = BGAmplitude_safe(allK, allW, 1)
    if amp is None: return None
    return [float(w) for w in allW], float(amp), allW


# Generate data for polynomial fitting
print("Generating training data...")
data = []
for w2 in range(1, 8):
    for w3 in range(1, 7):
        for w4 in range(1, 7):
            if w2 == w3 == w4: continue
            res = compute_n5(w2, w3, w4)
            if res is None: continue
            data.append(res)
            
print(f"Generated {len(data)} data points")

# Build monomial basis for degree-6 polynomial symmetric in (w1,w2) and (w3,w4,w5)
# Use power sums for simplicity
def build_features(w):
    w1, w2, w3, w4, w5 = w
    
    # Elementary symmetric polynomials in the plus legs
    e1_plus = w3 + w4 + w5
    e2_plus = w3*w4 + w3*w5 + w4*w5
    e3_plus = w3*w4*w5
    
    # For the minus legs
    e1_minus = w1 + w2
    e2_minus = w1 * w2
    
    # Degree-6 homogeneous monomials (total degree 6):
    # Using basis: e1_minus^a * e2_minus^b * e1_plus^c * e2_plus^d * e3_plus^e
    # with a + 2b + c + 2d + 3e = 6
    
    features = {}
    for a in range(7):
        for b in range(4):
            if a + 2*b > 6: continue
            for c in range(7):
                if a + 2*b + c > 6: continue
                for d in range(4):
                    if a + 2*b + c + 2*d > 6: continue
                    for e in range(3):
                        deg = a + 2*b + c + 2*d + 3*e
                        if deg == 6:
                            key = (a, b, c, d, e)
                            val = (e1_minus**a) * (e2_minus**b) * (e1_plus**c) * (e2_plus**d) * (e3_plus**e)
                            features[key] = val
    return features

# Build data matrix
X_list = []
y_list = []
feature_keys = None

for w_float, amp_float, w_exact in data:
    features = build_features(w_float)
    if feature_keys is None:
        feature_keys = sorted(features.keys())
    
    row = [features[k] for k in feature_keys]
    X_list.append(row)
    y_list.append(amp_float)

X = np.array(X_list)
y = np.array(y_list)

print(f"Feature dimension: {len(feature_keys)}")
print(f"Condition number of X: {np.linalg.cond(X):.2e}")

# Solve linear system X @ coeffs = y
# Use numpy lstsq for robustness
coeffs, residuals, rank, sv = np.linalg.lstsq(X, y, rcond=None)
print(f"Rank: {rank}, Residuals norm: {np.linalg.norm(residuals) if len(residuals) > 0 else 'N/A'}")

# Check fit quality
y_pred = X @ coeffs
max_error = np.max(np.abs(y - y_pred))
print(f"Max fit error: {max_error:.2e}")

if max_error < 1e-6:
    print("\nPerfect fit! The formula is:")
    formula_parts = []
    for (a,b,c,d,e), coef in zip(feature_keys, coeffs):
        if abs(coef) > 1e-8:
            formula_parts.append(f"  {coef:.6f} * (w1+w2)^{a} * (w1*w2)^{b} * (w3+w4+w5)^{c} * (w3*w4+w3*w5+w4*w5)^{d} * (w3*w4*w5)^{e}")
    for p in formula_parts:
        print(p)
    
    # Simplify: convert coefficients to rational numbers
    from fractions import Fraction as Frac
    print("\nRational coefficients:")
    for (a,b,c,d,e), coef in zip(feature_keys, coeffs):
        if abs(coef) > 1e-8:
            frac = Frac(coef).limit_denominator(100000)
            print(f"  ({a},{b},{c},{d},{e}): {frac} = {float(frac):.10f}")
else:
    print("\nNo exact fit. Max error too large.")
