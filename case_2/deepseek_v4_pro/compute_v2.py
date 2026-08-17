"""
Compute BG amplitudes for two-minus sector at various n and kinematic points.
Uses fractions for exact arithmetic. Simplified version with caching.
"""
from fractions import Fraction
from itertools import permutations, combinations
import math, time, sys

def mag(k): return abs(k)

# Global caches
_EK = {}
_FK = {}

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
        if q1 * q2 == 0:
            result = Fraction(0)
        else:
            result = -1 - Fraction(p1 * p2, q1 * q2)
    else:
        p1, p2 = ps[0], ps[1]
        rest = list(ps[2:])
        qp1, qp2 = mag(p1), mag(p2)
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
        if omega == 0:
            raise ValueError("Propagator: both omega=0 and k=0 (ambiguous)")
        return Fraction(0)
    denom = omega * omega / mk - g
    return Fraction(-1, denom)

def _subsets_of_size_range(items, min_size, max_size):
    for sz in range(min_size, max_size+1):
        for combo in combinations(items, sz):
            yield list(combo)

def set_partitions(S, k):
    if k == 1:
        return [[list(S)]]
    if k > len(S):
        return []
    S = list(S)
    mn = min(S)
    rest = [x for x in S if x != mn]
    result = []
    for sub in _subsets_of_size_range(rest, 0, len(S) - k):
        fp = [mn] + sub
        rem = [x for x in S if x not in fp]
        if len(rem) >= k - 1:
            for sp in set_partitions(rem, k-1):
                result.append([fp] + sp)
    return result

class BGContext:
    def __init__(self, momenta, omegas, g):
        self.kList = momenta
        self.wList = omegas
        self.gVal = g
        self._cache = {}
        
    def BGCurrent(self, S):
        key = tuple(sorted(S))
        if key in self._cache:
            return self._cache[key]
        Sl = list(S)
        if len(Sl) == 1:
            self._cache[key] = Fraction(1)
            return Fraction(1)
        
        omegaS = sum(self.wList[i-1] for i in Sl)
        kS = sum(self.kList[i-1] for i in Sl)
        result = Fraction(0)
        for m in range(2, len(Sl)+1):
            for part in set_partitions(Sl, m):
                sMoms = [sum(self.kList[j-1] for j in subset) for subset in part]
                sOmegas = [sum(self.wList[j-1] for j in subset) for subset in part]
                vMoms = [-kS] + sMoms
                vOmegas = [-omegaS] + sOmegas
                prod = Fraction(1)
                for j in range(m):
                    prod *= self.BGCurrent(tuple(part[j]))
                result += Vertex(m+1, vMoms, vOmegas) * prod
        result *= Propagator(omegaS, kS, self.gVal)
        self._cache[key] = result
        return result

def BGAmplitude(momenta, omegas, g):
    global _EK, _FK
    _EK.clear(); _FK.clear()
    n = len(momenta)
    ctx = BGContext(momenta, omegas, g)
    rest = list(range(2, n+1))
    result = Fraction(0)
    for m in range(2, n):
        for part in set_partitions(rest, m):
            sMoms = [sum(momenta[j-1] for j in subset) for subset in part]
            sOmegas = [sum(omegas[j-1] for j in subset) for subset in part]
            vMoms = [momenta[0]] + sMoms
            vOmegas = [omegas[0]] + sOmegas
            prod = Fraction(1)
            for j in range(m):
                prod *= ctx.BGCurrent(tuple(part[j]))
            result += Vertex(m+1, vMoms, vOmegas) * prod
    return result


def solve_two_minus(n, freeW3toN, g=1):
    """
    Solve for the two minus sector. 
    Input: freeW3toN = [w3, w4, ..., wn] (the positive-sigma legs, n-2 values)
    These are the free parameters. We solve for w1 and w2 (the two minus legs).
    
    Conservation:
      w1 + w2 + S = 0  =>  w2 = -w1 - S
      -w1^2 - w2^2 + Q = 0  =>  w1^2 + w2^2 = Q
    where S = sum_{i=3}^n wi, Q = sum_{i=3}^n wi^2
    
    Substituting: w1^2 + (w1+S)^2 = Q
    => 2w1^2 + 2w1 S + S^2 - Q = 0
    => w1 = [-S ± sqrt(2Q - S^2)] / 2
    
    Note: 2Q - S^2 ≥ 0 by Cauchy-Schwarz (since we have n-2 numbers, 
    (sum)^2 ≤ (n-2)*sum(w^2), so S^2 ≤ (n-2)Q < 2Q for n≥4).
    """
    if len(freeW3toN) != n - 2:
        raise ValueError(f"Need {n-2} free frequencies, got {len(freeW3toN)}")
    
    S = sum(freeW3toN)
    Q = sum(w*w for w in freeW3toN)
    
    disc = 2*Q - S*S  # always positive for n>=4 with distinct wi
    
    # Use exact rational if possible, otherwise approximate
    sqrt_disc = math.sqrt(float(disc))
    
    # Pick the + branch (arbitrary choice, the two branches are symmetric)
    w1_float = (float(-S) + sqrt_disc) / 2
    w2_float = -float(w1_float) - float(S)
    
    # Convert to Fraction (approximate)
    # Use exact rational: we need to solve exactly with rational numbers
    # But if disc is not a perfect square, w1 and w2 are irrational.
    # Use floating point for now, convert back using fractions.
    
    # For exact rational kinematics, pick the free wi such that 2Q - S^2 is a perfect square
    # Let me just use the exact formula and return Fraction approximations
    
    return None  # We'll use a different approach


def make_kinematics_random(n, g=1):
    """
    Generate valid kinematics by randomly picking w3..wn and solving w1,w2.
    We handle irrational cases by using floating point.
    Returns (ks, ws) as floats or None if no real solution.
    """
    import random
    random.seed(42 + n * 100)
    
    max_attempts = 100
    for _ in range(max_attempts):
        # Pick random positive integers for w3..wn
        freeW = [random.randint(1, 10) for _ in range(n - 2)]
        
        S = sum(freeW)
        Q = sum(w*w for w in freeW)
        disc = 2*Q - S*S
        
        if disc <= 0:
            continue
        
        sqrt_disc = math.sqrt(disc)
        w1 = (-S + sqrt_disc) / 2
        w2 = -w1 - S
        
        # w1 and w2 are the minus legs
        # They could be positive or negative, doesn't matter for sigma
        
        allW = [w1, w2] + freeW
        allK = [-w1*w1/g, -w2*w2/g] + [w*w/g for w in freeW]
        
        # Shuffle so the minus legs aren't always in positions 1,2
        # Actually, the BGAmplitude expects leg 1 to be the first minus leg,
        # and legs 2..n to be the rest. Let's keep leg 1 as minus and leg 2 as the
        # other minus, but we can shuffle the rest.
        
        # Check conservation
        sumW = sum(allW)
        sumK = sum(allK)
        if abs(sumW) > 1e-10 or abs(sumK) > 1e-10:
            continue
        
        # Check for poles in proper subsets of {2..n}
        has_pole = False
        for sz in range(2, n-1):  # proper subsets only
            for combo in combinations(range(1, n), sz):  # 0-based, legs 2..n
                wS = sum(allW[i] for i in combo)
                kS = sum(allK[i] for i in combo)
                if abs(kS) > 1e-12:
                    denom = wS*wS/abs(kS) - g
                    if abs(denom) < 1e-10:
                        has_pole = True
                        break
            if has_pole:
                break
        
        if not has_pole:
            return allK, allW, freeW
    
    return None


def make_kinematics_exact(n, g=1):
    """
    Generate kinematics where 2Q - S^2 is a perfect square.
    This gives exact rational w1 and w2.
    
    We need: S = sum_{i=3}^n wi, Q = sum_{i=3}^n wi^2
    and 2Q - S^2 = R^2 for some rational R.
    
    Use the identity: 2∑w_i^2 - (∑w_i)^2 = ∑(w_i - w_j)^2 / (n-2) * ... 
    Actually: 2∑w_i^2 - (∑w_i)^2 = (1/(n-2)) * ∑_{i<j} (w_i - w_j)^2 * 2?? 
    
    Let me just find known triples/quads where this works.
    
    For n-2=2 (n=4): 2(w3^2+w4^2) - (w3+w4)^2 = w3^2 + w4^2 - 2w3w4 = (w3-w4)^2 ✓
    So R = |w3-w4|. w1 = (-(w3+w4) + |w3-w4|)/2 = max(-w3, -w4)
    
    For n-2=3 (n=5): 2(w3^2+w4^2+w5^2) - (w3+w4+w5)^2 
    = w3^2+w4^2+w5^2 - 2w3w4 - 2w3w5 - 2w4w5
    This is not a perfect square in general.
    
    For special cases: pick w3, w4, w5 such that the discriminant is a perfect square.
    """
    if n == 4:
        # n=4: pick w3 != w4
        w3, w4 = Fraction(1), Fraction(3)
        S = w3 + w4
        Q = w3*w3 + w4*w4
        disc = 2*Q - S*S  # = (w3-w4)^2
        R = abs(w3 - w4)
        w1 = (-S + R) / 2
        w2 = (-S - R) / 2
        allW = [w1, w2, w3, w4]
        allK = [-w1*w1/g, -w2*w2/g, w3*w3/g, w4*w4/g]
        return allK, allW
    
    if n == 5:
        # For n=5, 2(w3^2+w4^2+w5^2) - (w3+w4+w5)^2 must be a perfect square.
        # Try some known Pythagorean-like triples
        # If (w3,w4,w5) = (a,b,c) where a+b=c, then S=a+b+c=2c, Q=a^2+b^2+c^2
        # 2Q - S^2 = 2(a^2+b^2+c^2) - 4c^2 = 2(a^2+b^2) - 2c^2 = 2(a^2+b^2-c^2)
        # If a^2+b^2 = c^2 (Pythagorean triple), then 2Q-S^2 = 0. Not good (degenerate).
        # Try other patterns.
        
        # Let's just use floating point and convert back.
        pass
    
    return make_kinematics_random(n, g)


def compute_amplitude_float(allK, allW, g=1):
    """Compute BG amplitude using the recursion (as Fraction, then convert to float)."""
    ks = [Fraction(k).limit_denominator(1000000) if not isinstance(k, Fraction) else k for k in allK]
    ws = [Fraction(w).limit_denominator(1000000) if not isinstance(w, Fraction) else w for w in allW]
    return float(BGAmplitude(ks, ws, g))


if __name__ == "__main__":
    # Try to compute for n=4 (the simplest case with exact rational kinematics)
    print("=== n=4 exact rational kinematics ===")
    for (w3, w4) in [(1,3), (1,5), (2,5), (1,7), (3,7)]:
        w3f, w4f = Fraction(w3), Fraction(w4)
        S = w3f + w4f
        Q = w3f*w3f + w4f*w4f
        disc = 2*Q - S*S
        R = abs(w3f - w4f)
        w1 = (-S + R) / 2
        w2 = (-S - R) / 2
        allW = [w1, w2, w3f, w4f]
        allK = [-w1*w1, -w2*w2, w3f*w3f, w4f*w4f]
        
        t0 = time.time()
        amp = float(BGAmplitude(allK, allW, 1))
        dt = time.time() - t0
        print(f"  w3={w3}, w4={w4}: w=[{', '.join(str(float(w)) for w in allW)}], A4={amp:.10f}, t={dt:.3f}s")
    
    print("\n=== n=5 exact rational kinematics (searching) ===")
    # For n=5, need 2(w3^2+w4^2+w5^2) - (w3+w4+w5)^2 to be a perfect square
    # This is: w3^2+w4^2+w5^2 - 2w3w4 - 2w3w5 - 2w4w5
    # = (w3^2+w4^2-2w3w4) + w5^2 - 2w5(w3+w4)
    # = (w3-w4)^2 + w5^2 - 2w5(w3+w4)
    # Hmm, this rarely gives a perfect square.
    
    # Alternative: pick w1, w2, w3, w4 freely and solve for w5
    # w5 = -(w1+w2+w3+w4) from energy conservation
    # -w1^2 - w2^2 + w3^2 + w4^2 + w5^2 = 0 from momentum
    # So: w5^2 = w1^2 + w2^2 - w3^2 - w4^2
    # And w5 = -(w1+w2+w3+w4)
    # Combining: (w1+w2+w3+w4)^2 = w1^2 + w2^2 - w3^2 - w4^2
    
    # Let's solve: pick w1, w2, w3 and solve for w4
    # w4 = -(w1+w2+w3+w5)... this gets circular.
    
    # Better: use the original MakeKinematics but with a different setup.
    # Put the minus legs at 1 and 2 (σ=-1), and solve for leg n (σ=+1) and leg 3.
    # Actually, let's use sympy or just try to find integer solutions by brute force.
    
    print("  Searching for n=5 with perfect square discriminant...")
    found = False
    for a in range(1, 10):
        for b in range(1, 10):
            for c in range(1, 10):
                S = a + b + c
                Q = a*a + b*b + c*c
                disc = 2*Q - S*S
                if disc > 0:
                    sd = int(math.isqrt(disc))
                    if sd*sd == disc:
                        w3, w4, w5 = Fraction(a), Fraction(b), Fraction(c)
                        Sf = w3 + w4 + w5
                        R = Fraction(sd)
                        w1 = (-Sf + R) / 2
                        w2 = (-Sf - R) / 2
                        allW = [w1, w2, w3, w4, w5]
                        allK = [-w1*w1, -w2*w2, w3*w3, w4*w4, w5*w5]
                        
                        # Check no poles
                        ok = True
                        for sz in range(2, 4):
                            for combo in combinations([1,2,3,4], sz):
                                wi = sum(float(allW[i]) for i in combo)
                                ki = sum(float(allK[i]) for i in combo)
                                if abs(ki) > 1e-12:
                                    d = wi*wi/abs(ki) - 1
                                    if abs(d) < 1e-10:
                                        ok = False
                        if ok:
                            t0 = time.time()
                            amp = float(BGAmplitude(allK, allW, 1))
                            dt = time.time() - t0
                            print(f"  (a,b,c)=({a},{b},{c}): w=[{', '.join(str(float(w)) for w in allW)}], A5={amp:.10f}, t={dt:.3f}s")
                            found = True
        if found: break
    if not found:
        print("  No valid kinematics found with brute force.")
