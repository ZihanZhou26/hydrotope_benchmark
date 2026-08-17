"""
Compute BG amplitudes for two-minus sector at various n and kinematic points.
Uses fractions for exact arithmetic.
"""
from fractions import Fraction
from itertools import permutations, combinations
import math, sys

def mag(k): return abs(k)

EK_cache = {}
def EKernel(n, ps):
    key = (n, tuple(ps))
    if key in EK_cache:
        return EK_cache[key]
    if n == 3:
        p1, p2 = ps[0], ps[1]
        result = -Fraction(1, 2) * (mag(p1) * mag(p2) + p1 * p2)
    else:
        p1, p2 = ps[0], ps[1]
        rest = list(ps[2:])
        qp2 = mag(p2)
        result = qp2 ** (n - 3) * EKernel(3, [p1, p2, sum(rest)]) / math.factorial(n - 2)
        for m in range(1, n - 2):
            new_ps = [p1, p2 + sum(rest[:m])] + rest[m:]
            result -= (qp2 ** m) / math.factorial(m) * EKernel(n - m, new_ps)
    EK_cache[key] = result
    return result

FK_cache = {}
def FKernel(n, ps):
    key = (n, tuple(ps))
    if key in FK_cache:
        return FK_cache[key]
    if n == 3:
        p1, p2 = ps[0], ps[1]
        q1, q2 = mag(p1), mag(p2)
        denom = q1 * q2
        if denom == 0:
            result = Fraction(0)
        else:
            result = -1 - Fraction(p1 * p2, denom)
    else:
        p1, p2 = ps[0], ps[1]
        rest = list(ps[2:])
        qp1, qp2 = mag(p1), mag(p2)
        result = 2 * EKernel(n, ps) / qp1
        for m in range(1, n - 2):
            sigM = p2 + sum(rest[:m])
            ek = EKernel(m + 2, [-sigM, p2] + rest[:m])
            fk = FKernel(n - m, [p1, sigM] + rest[m:])
            result -= 2 * ek * fk
        result = result / qp2
    FK_cache[key] = result
    return result

def Vertex(n, moms, omegas):
    result = Fraction(0)
    for p in permutations(range(n)):
        perm_moms = [moms[i] for i in p]
        perm_omegas = [omegas[i] for i in p]
        result += perm_omegas[0] * perm_omegas[1] * FKernel(n, perm_moms)
    return Fraction(-1, 2) * result

def Propagator(omega, k, g):
    mk = mag(k)
    if mk == 0:
        # k=0: dispersion is omega^2 = 0, so omega=0 is the only on-shell case
        if omega == 0:
            raise ValueError("Propagator: both omega=0 and k=0 (ambiguous)")
        # omega != 0, k=0: omega^2/0 -> infinity, propagator -> 0
        return Fraction(0)
    denom = omega * omega / mk - g
    return Fraction(-1, denom)

def _subsets_of_size_range(items, min_size, max_size):
    for sz in range(min_size, max_size + 1):
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
            for sp in set_partitions(rem, k - 1):
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
        S_list = list(S)
        if len(S_list) == 1:
            result = Fraction(1)
            self._cache[key] = result
            return result
        omegaS = sum(self.wList[i - 1] for i in S_list)
        kS = sum(self.kList[i - 1] for i in S_list)
        result = Fraction(0)
        for m in range(2, len(S_list) + 1):
            for part in set_partitions(S_list, m):
                sMoms = [sum(self.kList[j - 1] for j in subset) for subset in part]
                sOmegas = [sum(self.wList[j - 1] for j in subset) for subset in part]
                vMoms = [-kS] + sMoms
                vOmegas = [-omegaS] + sOmegas
                prod = Fraction(1)
                for j in range(m):
                    prod *= self.BGCurrent(tuple(part[j]))
                result += Vertex(m + 1, vMoms, vOmegas) * prod
        result *= Propagator(omegaS, kS, self.gVal)
        self._cache[key] = result
        return result

def BGAmplitude(momenta, omegas, g):
    global EK_cache, FK_cache
    EK_cache.clear()
    FK_cache.clear()
    n = len(momenta)
    ctx = BGContext(momenta, omegas, g)
    rest = list(range(2, n + 1))
    result = Fraction(0)
    for m in range(2, n):
        for part in set_partitions(rest, m):
            sMoms = [sum(momenta[j - 1] for j in subset) for subset in part]
            sOmegas = [sum(omegas[j - 1] for j in subset) for subset in part]
            vMoms = [momenta[0]] + sMoms
            vOmegas = [omegas[0]] + sOmegas
            prod = Fraction(1)
            for j in range(m):
                prod *= ctx.BGCurrent(tuple(part[j]))
            result += Vertex(m + 1, vMoms, vOmegas) * prod
    return result


def make_kinematics_two_minus(n, freeW, g=1):
    """
    Solve kinematics for two-minus sector using MakeKinematics approach.
    sigma = {-1, -1, +1, ..., +1}
    Leg 1 solved from energy cons, leg n solved from momentum cons.
    
    freeW = [w2, w3, ..., w_{n-1}]
    sigma_2 = -1, sigma_3 = ... = sigma_{n-1} = +1
    sigma_1 = -1, sigma_n = +1 (satisfies sigma_1 + sigma_n = 0)
    """
    freeW = list(freeW)
    n_free = len(freeW)
    if n_free != n - 2:
        raise ValueError(f"Need {n-2} free frequencies, got {n_free}")
    
    sumFree = sum(freeW)
    sumSigmaW2 = -freeW[0]**2 + sum(w**2 for w in freeW[1:])
    
    wn = (sumSigmaW2 - sumFree**2) / (2 * sumFree)
    w1 = -(sumFree + wn)
    
    allW = [w1] + list(freeW) + [wn]
    
    # momenta: sigma_i * wi^2 / g
    allK = [-w1**2 / g, -freeW[0]**2 / g]
    allK += [w**2 / g for w in freeW[1:]]
    allK += [wn**2 / g]
    
    return allK, allW


def check_propagator_poles(allW, allK, g=1):
    """Check if any subset has a zero propagator denominator."""
    n = len(allW)
    for sz in range(2, n):
        for combo in combinations(range(n), sz):
            wS = sum(allW[i] for i in combo)
            kS = sum(allK[i] for i in combo)
            if kS != 0:
                denom = wS * wS / abs(kS) - g
                if abs(float(denom)) < 1e-12:
                    return True, combo
    return False, None


if __name__ == "__main__":
    gVal = 1
    
    # Generate data for n=4,5,6,7
    # Use integer or rational free frequencies
    
    test_points = {
        4: [
            [Fraction(3), Fraction(5)],       # w2=-σ (leg 2, σ=-1), w3=+σ (leg 3, σ=+1)
            [Fraction(2), Fraction(7)],
            [Fraction(1), Fraction(3)],
        ],
        5: [
            [Fraction(3), Fraction(5,2), Fraction(4)],
            [Fraction(1), Fraction(2), Fraction(7)],
            [Fraction(2), Fraction(7,2), Fraction(5)],
        ],
        6: [
            [Fraction(3), Fraction(5,2), Fraction(4), Fraction(7,2)],
            [Fraction(1), Fraction(2), Fraction(3), Fraction(7)],
            [Fraction(2), Fraction(5,2), Fraction(3), Fraction(11,2)],
        ],
        7: [
            [Fraction(3), Fraction(5,2), Fraction(4), Fraction(7,2), Fraction(5)],
            [Fraction(1), Fraction(2), Fraction(3), Fraction(4), Fraction(7)],
            [Fraction(2), Fraction(5,2), Fraction(3), Fraction(7,2), Fraction(11,2)],
        ],
    }
    
    import time
    
    for n in [4, 5, 6, 7]:
        print(f"\n{'='*60}")
        print(f"  n = {n}")
        print(f"{'='*60}")
        
        for freeW in test_points[n]:
            allK, allW = make_kinematics_two_minus(n, freeW, gVal)
            
            has_pole, subset = check_propagator_poles(allW, allK, gVal)
            
            w_str = ', '.join(str(w) for w in allW)
            
            if has_pole:
                print(f"\n  freeW = {[str(w) for w in freeW]}")
                print(f"  SKIP: pole at subset {[s+1 for s in subset]}")
                continue
            
            start = time.time()
            amp = BGAmplitude(allK, allW, gVal)
            elapsed = time.time() - start
            
            # The amplitude from BG code is real (all I factors multiply to a real)
            amp_val = float(amp)
            
            print(f"\n  freeW = {[str(w) for w in freeW]}")
            print(f"  w = [{w_str}]")
            print(f"  A_{n} = {amp_val:.15f}")
            print(f"  Time: {elapsed:.3f}s")
