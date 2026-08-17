"""
Generate data for two-minus sector and try to infer the formula.
"""
from fractions import Fraction
from itertools import permutations, combinations
import math, time, sys

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
        if omega == 0: raise ValueError('0/0')
        return Fraction(0)
    denom = omega * omega / mk - g
    return Fraction(-1, denom)

def _subsets_of_size_range(items, min_size, max_size):
    for sz in range(min_size, max_size+1):
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

class BGContext:
    def __init__(self, momenta, omegas, g):
        self.kList = momenta; self.wList = omegas; self.gVal = g; self._cache = {}
    def BGCurrent(self, S):
        key = tuple(sorted(S))
        if key in self._cache: return self._cache[key]
        Sl = list(S)
        if len(Sl) == 1: self._cache[key] = Fraction(1); return Fraction(1)
        omegaS = sum(self.wList[i-1] for i in Sl)
        kS = sum(self.kList[i-1] for i in Sl)
        result = Fraction(0)
        for m in range(2, len(Sl)+1):
            for part in set_partitions(Sl, m):
                sMoms = [sum(self.kList[j-1] for j in s) for s in part]
                sOmegas = [sum(self.wList[j-1] for j in s) for s in part]
                vM = [-kS] + sMoms; vO = [-omegaS] + sOmegas
                prod = Fraction(1)
                for j in range(m): prod *= self.BGCurrent(tuple(part[j]))
                result += Vertex(m+1, vM, vO) * prod
        result *= Propagator(omegaS, kS, self.gVal)
        self._cache[key] = result
        return result

def BGAmplitude(momenta, omegas, g):
    global _EK, _FK; _EK.clear(); _FK.clear()
    n = len(momenta)
    ctx = BGContext(momenta, omegas, g)
    rest = list(range(2, n+1))
    result = Fraction(0)
    for m in range(2, n):
        for part in set_partitions(rest, m):
            sMoms = [sum(momenta[j-1] for j in s) for s in part]
            sOmegas = [sum(omegas[j-1] for j in s) for s in part]
            vM = [momenta[0]] + sMoms; vO = [omegas[0]] + sOmegas
            prod = Fraction(1)
            for j in range(m): prod *= ctx.BGCurrent(tuple(part[j]))
            result += Vertex(m+1, vM, vO) * prod
    return result


def generate_n4_data():
    """For n=4 two-minus, w1=-w3, w4=-w2. Free params: w2, w3."""
    data = []
    g = 1
    for w2 in [1, 2, 3, 5, 7]:
        for w3 in [1, 2, 3, 5, 7]:
            if w2 == w3: continue  # avoid degenerate (w1=w4 then same as w2 etc)
            w2f = Fraction(w2); w3f = Fraction(w3)
            w1f = -w3f; w4f = -w2f
            allW = [w1f, w2f, w3f, w4f]
            allK = [-w1f*w1f, -w2f*w2f, w3f*w3f, w4f*w4f]
            try:
                amp = float(BGAmplitude(allK, allW, g))
                data.append({
                    'n': 4, 'w': [w1f, w2f, w3f, w4f],
                    'w_float': [float(w) for w in allW],
                    'amp': amp
                })
            except Exception as e:
                pass
    return data


def generate_n5_data():
    """For n=5, use the MakeKinematics approach."""
    data = []
    g = 1
    # Try various freeW combinations
    for freeW in [
        [3, 5, 2], [1, 2, 3], [2, 5, 3],
        [3, 4, 5], [1, 3, 5], [2, 7, 3],
        [5, 2, 3], [7, 3, 5],
    ]:
        freeWf = [Fraction(w) for w in freeW]
        sumFree = sum(freeWf)
        # sigma: leg2=-1, leg3=+1, leg4=+1
        sumSigmaW2 = -freeWf[0]**2 + sum(w**2 for w in freeWf[1:])
        wn = (sumSigmaW2 - sumFree**2) / (2 * sumFree)
        w1 = -(sumFree + wn)
        allW = [w1, freeWf[0], freeWf[1], freeWf[2], wn]
        allK = [-w1**2, -freeWf[0]**2, freeWf[1]**2, freeWf[2]**2, wn**2]
        
        # Check no poles in proper subsets of {2,3,4,5}
        ok = True
        for sz in range(2, 4):
            for combo in combinations([1,2,3,4], sz):
                wS = sum(allW[i] for i in combo)
                kS = sum(allK[i] for i in combo)
                if float(abs(kS)) > 1e-12:
                    d = float(wS*wS/abs(kS) - g)
                    if abs(d) < 1e-10:
                        ok = False
        if not ok:
            continue
        
        try:
            t0 = time.time()
            amp = float(BGAmplitude(allK, allW, g))
            dt = time.time() - t0
            data.append({
                'n': 5, 'w': allW,
                'w_float': [float(w) for w in allW],
                'amp': amp, 'time': dt
            })
        except Exception as e:
            pass
    return data


if __name__ == "__main__":
    print("Generating n=4 data...")
    d4 = generate_n4_data()
    for d in d4:
        wf = d['w_float']
        print(f"  w=[{wf[0]:.1f},{wf[1]:.1f},{wf[2]:.1f},{wf[3]:.1f}], A4={d['amp']:.6f}")
        # Let's try to guess the formula
        # For two-minus A4, the kinematics is w1=-w3, w4=-w2
        # Try A4 = c * w2^a * w3^b * (w2+w3)^d * (w2-w3)^e
        w2, w3 = wf[1], wf[2]  # w2 > 0, w3 > 0
        # Try ratio with w2^2 * w3^2
        ratio = d['amp'] / (w2*w2 * w3*w3)
        print(f"    amp/(w2^2*w3^2) = {ratio:.6f}")
        # Try ratio with w1*w2*w3*w4 = (-w3)*w2*w3*(-w2) = w2^2*w3^2 (same)
    
    print("\nGenerating n=5 data...")
    d5 = generate_n5_data()
    for d in d5:
        wf = d['w_float']
        print(f"  w={[f'{x:.3f}' for x in wf]}, A5={d['amp']:.6f}")
        # Try various product combinations
        w1, w2, w3, w4, w5 = d['w']
        # Product of all omega_i squared divided by something
        prod_all = float(w1*w2*w3*w4*w5)
        print(f"    amp/prod = {d['amp']/prod_all:.6f}")
        prod_sq = float(w1*w1*w2*w2*w3*w3*w4*w4*w5*w5)
        print(f"    amp/prod_sq = {d['amp']/prod_sq:.10f}")
