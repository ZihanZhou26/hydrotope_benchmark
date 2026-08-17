"""
Exact implementation of the Berends-Giele recursion from OnShellBG.m
for 1D water wave amplitudes. Uses fractions for exact arithmetic.
"""
from fractions import Fraction
from itertools import permutations, combinations
import math

# ================================================================
# I. INTERACTION KERNELS (exact)
# ================================================================

def mag(k):
    return abs(k)

def EKernel(n, ps):
    """Energy kernel, exact rational."""
    if n == 3:
        p1, p2 = ps[0], ps[1]
        return -Fraction(1, 2) * (mag(p1) * mag(p2) + p1 * p2)
    else:
        p1, p2 = ps[0], ps[1]
        rest = list(ps[2:])
        qp2 = mag(p2)
        result = qp2 ** (n - 3) * EKernel(3, [p1, p2, sum(rest)]) / math.factorial(n - 2)
        for m in range(1, n - 2):  # m from 1 to n-3
            new_ps = [p1, p2 + sum(rest[:m])] + rest[m:]
            result -= (qp2 ** m) / math.factorial(m) * EKernel(n - m, new_ps)
        return result


def FKernel(n, ps):
    """F kernel, exact rational."""
    if n == 3:
        p1, p2 = ps[0], ps[1]
        q1, q2 = mag(p1), mag(p2)
        denom = q1 * q2
        if denom == 0:
            return Fraction(0)
        return -1 - Fraction(p1 * p2, denom)
    else:
        p1, p2 = ps[0], ps[1]
        rest = list(ps[2:])
        qp1, qp2 = mag(p1), mag(p2)
        result = 2 * EKernel(n, ps) / qp1
        for m in range(1, n - 2):  # m from 1 to n-3
            sigM = p2 + sum(rest[:m])
            ek = EKernel(m + 2, [-sigM, p2] + rest[:m])
            fk = FKernel(n - m, [p1, sigM] + rest[m:])
            result -= 2 * ek * fk
        return result / qp2


# ================================================================
# II. VERTEX AND PROPAGATOR
# ================================================================

def Vertex(n, moms, omegas):
    """Vertex function: sum over permutations of FKernel * omega_i * omega_j."""
    # moms and omegas are lists of length n
    # Mathematica: Vertex[n_Integer, moms_List, omegas_List] := Module[{result = 0},
    #   Do[result += omegas[[p[[1]]]]*omegas[[p[[2]]]]*FKernel[n, moms[[p]]],
    #     {p, Permutations[Range[n]]}];
    #   (-I/2)*result]
    result = Fraction(0)
    for p in permutations(range(n)):
        perm_moms = [moms[i] for i in p]
        perm_omegas = [omegas[i] for i in p]
        result += perm_omegas[0] * perm_omegas[1] * FKernel(n, perm_moms)
    # Factor (-I/2) - we'll keep it as complex
    return Fraction(-1, 2) * result  # will be multiplied by I later


def Propagator(omega, k, g):
    """Propagator: -I/(omega^2/|k| - g)."""
    denom = omega * omega / mag(k) - g
    return Fraction(-1, denom)  # will be multiplied by I later


# ================================================================
# III. SET PARTITIONS (for BG recursion)
# ================================================================

def set_partitions(S, k):
    """Partition set S into exactly k non-empty subsets.
    Mathematica: uses fixed-point algorithm. Python: standard recursion."""
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


def _subsets_of_size_range(items, min_size, max_size):
    """Generate all subsets of items with size in [min_size, max_size]."""
    for sz in range(min_size, max_size + 1):
        for combo in combinations(items, sz):
            yield list(combo)


# ================================================================
# IV. BERENDS-GIELE RECURSION
# ================================================================

class BGContext:
    """Context for BG recursion with global state (kList, wList, gVal)."""
    
    def __init__(self, momenta, omegas, g):
        self.kList = momenta
        self.wList = omegas
        self.gVal = g
        self._cache = {}  # memoization for BGCurrent
        
    def BGCurrent(self, S):
        """BG current for set S (tuple of leg indices, 1-based)."""
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
                # sMoms: total momentum of each subset
                sMoms = [sum(self.kList[j - 1] for j in subset) for subset in part]
                sOmegas = [sum(self.wList[j - 1] for j in subset) for subset in part]
                # vMoms = {-kS, sMoms[0], ..., sMoms[m-1]}
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
    """Full n-point BG amplitude.
    Note: This returns the amplitude up to the overall I factors.
    The actual amplitude is result * I^(appropriate power).
    We track this separately.
    """
    n = len(momenta)
    ctx = BGContext(momenta, omegas, g)
    
    rest = list(range(2, n + 1))  # 1-based indices
    
    result_real = Fraction(0)
    
    for m in range(2, n):
        for part in set_partitions(rest, m):
            sMoms = [sum(momenta[j - 1] for j in subset) for subset in part]
            sOmegas = [sum(omegas[j - 1] for j in subset) for subset in part]
            vMoms = [momenta[0]] + sMoms  # k_1 first
            vOmegas = [omegas[0]] + sOmegas  # ω_1 first
            
            prod = Fraction(1)
            for j in range(m):
                prod *= ctx.BGCurrent(tuple(part[j]))
            
            result_real += Vertex(m + 1, vMoms, vOmegas) * prod
    
    return result_real


# ================================================================
# V. KINEMATIC SOLVER for two-minus sector
# ================================================================

def make_kinematics_two_minus(n, freeW, g=1):
    """
    Solve kinematics for the two-minus sector: sigma = {-1, -1, +1, ..., +1}.
    Legs 1 and 2 have sigma=-1, legs 3..n have sigma=+1.
    
    Returns (momenta, omegas).
    """
    # Using the method from MakeKinematics but adapted:
    # We know ω_1 is the second solved variable.
    # Conservation: sum ω_i = 0, sum σ_i ω_i^2 = 0
    # We'll solve for ω_1 and ω_2 (the two minus legs) given ω_3, ..., ω_n.
    
    # Actually, the original MakeKinematics solves for w_1 and w_n given w_2..w_{n-1}
    # and requires sigma_1 + sigma_n = 0.
    # In our setup, if we reorder so that one minus is at position 1 and the other
    # at position n (by convention), we can use the same approach.
    # But we want legs 1 and 2 to be the minus ones. So let's just solve directly.
    
    # Let freeW be the free frequencies for legs 3..n (positive sigma).
    # We need to find w1, w2 such that:
    #   w1 + w2 + sum(freeW) = 0  =>  w1 + w2 = -sumFree
    #   -w1^2 - w2^2 + sum(freeW^2) = 0  =>  w1^2 + w2^2 = sumSqFree
    
    # Let S = sumFree, Q = sumSqFree.
    # w1 + w2 = -S
    # w1^2 + w2^2 = Q
    
    # (w1 + w2)^2 = w1^2 + w2^2 + 2w1w2
    # S^2 = Q + 2w1w2
    # w1w2 = (S^2 - Q)/2
    
    # w1 and w2 are roots of t^2 + St + (S^2-Q)/2 = 0
    # t = (-S ± sqrt(S^2 - 2(S^2-Q)))/2 = (-S ± sqrt(2Q - S^2))/2
    
    # Since both w1 and w2 can be positive or negative (depending on kinematics),
    # we have a chamber structure based on the sign of (2Q - S^2) and the signs of w1, w2.
    
    sumFree = sum(freeW)
    sumSqFree = sum(w * w for w in freeW)
    
    S = sumFree
    Q_val = sumSqFree
    
    disc = 2 * Q_val - S * S
    
    if disc < 0:
        # No real solution
        return None
    
    sqrt_disc = math.sqrt(float(disc))
    
    # Two solutions: (w1, w2) and (w2, w1)
    w1_val = Fraction(-S) + Fraction(sqrt_disc).limit_denominator(1000000) if sqrt_disc > 0 else Fraction(-S)
    w2_val = Fraction(-S) - Fraction(sqrt_disc).limit_denominator(1000000) if sqrt_disc > 0 else Fraction(-S)
    
    # Actually, let me be more careful with the fractions
    # w1 = (-S + sqrt(2Q - S^2)) / 2
    # w2 = (-S - sqrt(2Q - S^2)) / 2
    
    # So w1 + w2 = -S (correct), and w1*w2 = (S^2 - (2Q-S^2))/4 = (2S^2 - 2Q)/4 = (S^2 - Q)/2 ✓
    
    w1 = (Fraction(-S) + Fraction(sqrt_disc).limit_denominator(10**12)) / 2
    w2 = (Fraction(-S) - Fraction(sqrt_disc).limit_denominator(10**12)) / 2
    
    # Normalize: make w1 the more positive one
    # Actually let's keep as-is for now
    
    allW = [w1, w2] + list(freeW)
    allK = [Fraction(-1) * w * w / g for w in [w1, w2]]  # sigma=-1 for first two
    allK += [Fraction(1) * w * w / g for w in freeW]      # sigma=+1 for rest
    
    # Sanity check
    # sum(allW) should be 0, sum(allK) should be 0
    # But with fractions and floating sqrt, there will be some error
    
    return allK, allW


def make_kinematics_exact(n, freeW, g=1):
    """
    Generate exact rational kinematics for the two-minus sector.
    We pick w1 and w2 to satisfy conservation exactly with rational numbers.
    An easy way: pick w3..wn freely, pick w1 freely, compute w2 = -(w1 + sumFree).
    Then momentum conservation is automatically satisfied if we set up sigma correctly? 
    No, momentum gives -w1^2 - w2^2 + sum(freeW^2) = 0, which is a constraint.
    
    Alternative: use MakeKinematics approach from OnShellBG.m:
    Put the two minus legs at positions 1 and n (or 1 and 2 with special handling).
    
    Actually, let's think: the original code uses:
    sigma_1 + sigma_n = 0 for linear solution.
    
    For the two-minus sector with sigma = {-1, -1, +1, ..., +1}:
    If we set sigma_1 = -1, sigma_n = +1, the condition is satisfied.
    The "free" frequencies are for legs 2..n-1, with sigma_2 = -1, sigma_3..sigma_{n-1} = +1.
    
    So the code solves:
    w1 = -(w2 + ... + wn-1 + wn)  [energy conservation]
    And wn from the linear equation (since sigma_1 + sigma_n = 0):
    sigma_1 * w1^2 + sigma_2 w2^2 + ... + sigma_{n-1} w_{n-1}^2 + sigma_n wn^2 = 0
    
    Substituting w1 and sigma_1 = -sigma_n:
    -sigma_n*(sumFree + wn)^2 + sigma_2 w2^2 + ... + sigma_{n-1} w_{n-1}^2 + sigma_n wn^2 = 0
    -sigma_n*(sumFree^2 + 2*sumFree*wn + wn^2) + sigma_2 w2^2 + ... + wn^2*sigma_n = 0
    -sigma_n*sumFree^2 - 2*sigma_n*sumFree*wn + sigma_2 w2^2 + ... = 0
    wn = -(sigma_n*sumFree^2 + sigma_2 w2^2 + ...)/(2*sigma_n*sumFree)
    
    With sigma_n = +1:
    wn = -(sumFree^2 + sigma_2 w2^2 + sigma_3 w3^2 + ...)/(2*sumFree)
    where sumFree = w2 + w3 + ... + w_{n-1}
    
    This is what the original code does: 
    wn = -(sigma_1 * sumFree^2 + sum_{i=2}^{n-1} sigma_i wi^2) / (2*sigma_1*sumFree)
    
    With sigma_1 = -1:
    wn = -(-sumFree^2 + sigma_2 w2^2 + ...)/(2*(-1)*sumFree)
       = (sumFree^2 - sigma_2 w2^2 - sigma_3 w3^2 - ...)/(2*sumFree)
    
    Wait, let me re-derive:
    sigma_1 = -1, sigma_n = +1.
    
    -w1^2 + sigma_2 w2^2 + ... + sigma_{n-1} w_{n-1}^2 + wn^2 = 0
    w1 = -(w2 + ... + wn)
    w1^2 = (sumFree + wn)^2 = sumFree^2 + 2*sumFree*wn + wn^2
    
    -sumFree^2 - 2*sumFree*wn - wn^2 + sigma_2 w2^2 + ... + sigma_{n-1} w_{n-1}^2 + wn^2 = 0
    -sumFree^2 - 2*sumFree*wn + sigma_2 w2^2 + ... + sigma_{n-1} w_{n-1}^2 = 0
    wn = (-sumFree^2 + sigma_2 w2^2 + ... + sigma_{n-1} w_{n-1}^2) / (2*sumFree)
    
    OR from the code formula:
    wn = -(sigma_1 * sumFree^2 + sum_{i=2}^{n-1} sigma_i*wi^2) / (2*sigma_1*sumFree)
       = -(-1*sumFree^2 + sigma_2 w2^2 + ...) / (2*(-1)*sumFree)
       = (sumFree^2 - sigma_2 w2^2 - ...) / (2*sumFree)
    
    Hmm, these give opposite signs. Let me re-check the code:
    
    sumFree = Total[freeW];  (* w2 + ... + w_{n-1} *)
    sigmaFree = sigmas[[2 ;; n - 1]];
    sumSigmaW2 = Total[sigmaFree*freeW^2];  (* sum sigma_i*wi^2, i=2..n-1 *)
    
    wn = -(sigmas[[1]]*sumFree^2 + sumSigmaW2)/(2*sigmas[[1]]*sumFree);
    
    sigmas[[1]] = sigma_1 = -1.
    wn = -((-1)*sumFree^2 + sumSigmaW2) / (2*(-1)*sumFree)
       = -(-sumFree^2 + sumSigmaW2) / (-2*sumFree)
       = (sumSigmaW2 - sumFree^2) / (2*sumFree)
    
    Hmm, let me be more careful:
    wn = -(sigma_1*sumFree^2 + sumSigmaW2) / (2*sigma_1*sumFree)
       = -(-1*sumFree^2 + sumSigmaW2) / (2*(-1)*sumFree)
       = -(-sumFree^2 + sumSigmaW2) / (-2*sumFree)
       = (sumSigmaW2 - sumFree^2) / (2*sumFree)
    
    Now from my derivation:
    -sumFree^2 - 2*sumFree*wn + sumSigmaW2 = 0
    -2*sumFree*wn = sumFree^2 - sumSigmaW2
    wn = -(sumFree^2 - sumSigmaW2)/(2*sumFree) = (sumSigmaW2 - sumFree^2)/(2*sumFree)
    
    OK, these match. Good.
    
    So for the two-minus sector: sigma_2 = -1, sigma_3 = ... = sigma_{n-1} = +1.
    sumSigmaW2 = (-1)*w2^2 + w3^2 + ... + w_{n-1}^2
    sumFree = w2 + ... + w_{n-1}
    wn = (sumSigmaW2 - sumFree^2) / (2*sumFree)
    w1 = -(sumFree + wn)
    
    This is the correct approach. Let me implement this properly.
    """
    if len(freeW) != n - 2:
        raise ValueError(f"Need n-2={n-2} free frequencies, got {len(freeW)}")
    
    # freeW corresponds to legs 2, 3, ..., n-1
    # sigma_2 = -1, sigma_3 = ... = sigma_{n-1} = +1
    
    freeW = list(freeW)
    sumFree = sum(freeW)  # w2 + ... + w_{n-1}
    
    # sigma_i * w_i^2 for i=2..n-1
    sumSigmaW2 = -freeW[0]**2 + sum(w**2 for w in freeW[1:])
    
    # wn = (sumSigmaW2 - sumFree^2) / (2*sumFree)
    wn = (sumSigmaW2 - sumFree**2) / (2 * sumFree)
    
    # w1 = -(sumFree + wn)
    w1 = -(sumFree + wn)
    
    # Build full arrays
    allW = [w1] + list(freeW) + [wn]
    
    # momenta: sigma_i * wi^2 / g
    # sigma_1 = -1, sigma_2 = -1, sigma_3..n = +1
    allK = [-w1**2 / g, -freeW[0]**2 / g]
    allK += [w**2 / g for w in freeW[1:]]
    allK += [wn**2 / g]
    
    return allK, allW


# ================================================================
# VI. TESTING
# ================================================================

def test_amplitude():
    """Run the original tests from OnShellBG.m."""
    gVal = Fraction(1)
    
    # Test cases from the original code
    testCases = [
        (5, [Fraction(3, 2), Fraction(2), Fraction(5, 2)]),
        (6, [Fraction(3, 2), Fraction(2), Fraction(5, 2), Fraction(3)]),
        (7, [Fraction(3, 2), Fraction(2), Fraction(5, 2), Fraction(3), Fraction(7, 2)]),
        (8, [Fraction(1), Fraction(2), Fraction(3), Fraction(4), Fraction(5), Fraction(6)]),
    ]
    
    print("=" * 64)
    print("  On-Shell BG: Vanishing of A_n for sigma = {-1,+1,...,+1}")
    print("=" * 64)
    
    for n, freeW in testCases:
        # sigma = {-1, +1, ..., +1} (not two-minus, just one-minus)
        # Use the original approach
        sigmas = [Fraction(-1)] + [Fraction(1)] * (n - 1)
        
        # Solve kinematics using the original method
        freeW_for_solver = freeW  # w2..w_{n-1}
        sumFree = sum(freeW_for_solver)
        
        # sigma_i for i=2..n-1 are all +1
        sumSigmaW2 = sum(w**2 for w in freeW_for_solver)
        
        wn = -(Fraction(-1) * sumFree**2 + sumSigmaW2) / (2 * Fraction(-1) * sumFree)
        w1 = -(sumFree + wn)
        
        allW = [w1] + list(freeW_for_solver) + [wn]
        allK = [-w1**2 / gVal]  # sigma_1 = -1
        allK += [w**2 / gVal for w in freeW_for_solver]  # sigma_2..n-1 = +1
        allK += [wn**2 / gVal]  # sigma_n = +1
        
        import time
        start = time.time()
        amp = BGAmplitude(allK, allW, gVal)
        elapsed = time.time() - start
        
        print(f"\n--- n = {n} ---")
        print(f"  sigma  = [{', '.join(str(s) for s in sigmas)}]")
        print(f"  free w = [{', '.join(str(w) for w in freeW)}]")
        print(f"  A_{n} = {_simplify_fraction(amp)}")
        print(f"  Time: {elapsed:.1f} sec")


def _simplify_fraction(f):
    """Try to simplify and represent a fraction nicely."""
    if isinstance(f, Fraction):
        if f.denominator == 1:
            return str(f.numerator)
        return f"{f.numerator}/{f.denominator}"
    return str(f)


if __name__ == "__main__":
    test_amplitude()
