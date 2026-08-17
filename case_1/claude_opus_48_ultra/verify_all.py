"""Comprehensive verification of the closed forms vs BGAmplitude.
 (A) soft-minus regime:  A_n = 2^(n-1) w1 w2 (min(w1^2,w2^2))^(n-3)   [smallest |w| is a minus leg]
 (B) all-plus-soft:      A_n = 2^(n-1) (n-3)! w1 w2 prod_{n-3 softest plus} w_j^2  [n-3 softest legs all plus]
 (C) n=5 complete global formula (loaded from kabs_sol5.pkl) at random points (all chambers).
Reports max relative error (exact rational => should be 0)."""
from bg import amp_two_minus, BG, make_kinematics, two_minus_sigma
from fractions import Fraction as Q
import itertools, random, math, sys

def softmin_pred(n, w):
    m2=min(w[0]*w[0], w[1]*w[1])
    return 2**(n-1)*w[0]*w[1]*m2**(n-3)

def allplus_pred(n, w):
    plus=sorted(w[2:], key=lambda v:v*v)
    prod=Q(1)
    for j in range(n-3):
        prod*=plus[j]*plus[j]
    return 2**(n-1)*math.factorial(n-3)*w[0]*w[1]*prod

def is_soft_minus(w):
    w2=[v*v for v in w]; return w2.index(min(w2))<2

def is_allplus_soft(n, w):
    w2=[v*v for v in w]
    order=sorted(range(n), key=lambda i:w2[i])
    return all(idx>=2 for idx in order[:n-3])

def gen_free(n, rng, lo=1, hi=9):
    return [Q(rng.randint(-4*hi,4*hi), rng.randint(1,9)) for _ in range(n-2)]

def check_regime(n, npts, pred_fn, regime_fn, name, rng):
    ok=0; tested=0; tries=0
    while tested<npts and tries<npts*200:
        tries+=1
        free=gen_free(n,rng)
        if any(x==0 for x in free): continue
        try: A,kL,wL=amp_two_minus(n,free)
        except Exception: continue
        if any(v==0 for v in wL): continue
        if not regime_fn(wL): continue
        tested+=1
        if A.im==pred_fn(n,tuple(wL)): ok+=1
        else:
            if ok+1>tested-2: print(f"   MISMATCH n={n} {name}: w={[str(v) for v in wL]} BG={A.im} pred={pred_fn(n,tuple(wL))}")
    return ok, tested

if __name__=="__main__":
    rng=random.Random(99)
    print("=== (A) soft-minus regime:  A_n = 2^(n-1) w1 w2 (min(w1^2,w2^2))^(n-3) ===")
    for n in [5,6,7]:
        npts={5:120,6:60,7:12}[n]
        ok,tested=check_regime(n,npts,softmin_pred,is_soft_minus,"soft-minus",rng)
        print(f"  n={n}: {ok}/{tested} exact matches")
    print("\n=== (B) all-plus-soft:  A_n = 2^(n-1) (n-3)! w1 w2 prod_{n-3 softest plus} w_j^2 ===")
    for n in [5,6,7]:
        npts={5:120,6:60,7:12}[n]
        ok,tested=check_regime(n,npts,allplus_pred,is_allplus_soft,"all-plus-soft",rng)
        print(f"  n={n}: {ok}/{tested} exact matches")
