"""Verify the explicit n=5 global formula  A = P0 + sum P|k_muj|  against BGAmplitude
at many fresh random points spanning ALL chambers. Exact rational comparison + float rel-err."""
import pickle
from fractions import Fraction as Q
from fit_kabs import P0_basis_vals, PEXPS, kabs_basis_vals
from bg import amp_two_minus
import itertools, random

with open("kabs_sol5.pkl","rb") as f:
    sol=[Q(s) for s in pickle.load(f)]
nb0=len(P0_basis_vals((Q(1),Q(2),Q(3),Q(4),Q(5))))
nbk=len(PEXPS); nb=nb0+nbk

def formula(w):
    vals=P0_basis_vals(w)+kabs_basis_vals(w)
    return sum(sol[j]*vals[j] for j in range(nb))

rng=random.Random(2024)
def randq():
    return Q(rng.randint(-40,40), rng.randint(1,9))

# 1) exact check on fresh random points (all chambers)
ntest=0; bad=0; maxrel=0.0
chambers=set()
for _ in range(4000):
    free=[randq() for _ in range(3)]
    if any(x==0 for x in free): continue
    try:
        A,kL,wL=amp_two_minus(5,free)
    except Exception:
        continue
    if any(v==0 for v in wL): continue
    pred=formula(tuple(wL))
    ntest+=1
    if pred!=A.im:
        bad+=1
        if bad<=5: print("MISMATCH", [str(x) for x in wL], "BG", A.im, "formula", pred)
    else:
        if A.im!=0:
            rel=abs(float(pred-A.im))/abs(float(A.im))
            maxrel=max(maxrel,rel)
    # record chamber signature (which leg is softest, sign pattern coarse)
    w2=[v*v for v in wL]; chambers.add(w2.index(min(w2)))
    if ntest>=800: break

print(f"\nn=5 global formula vs BGAmplitude: {ntest} random points, {bad} mismatches")
print(f"softest-leg index seen: {sorted(chambers)} (0,1=minus legs; 2,3,4=plus legs)")
print(f"max float rel-err on matches: {maxrel:.2e}")
print("EXACT agreement everywhere" if bad==0 else "FAILURES PRESENT")
