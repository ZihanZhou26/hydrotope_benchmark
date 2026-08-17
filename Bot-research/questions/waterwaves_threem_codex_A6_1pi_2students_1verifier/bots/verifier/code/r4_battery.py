#!/usr/bin/env python3
"""Compact foundation re-check on the fresh oracle: decomposition denominator-free,
dual-S3 symmetry, hierarchical regime, chamber spread."""
from fractions import Fraction as F
from r4_verify import amp_from_omega, P_pole, R_spline, solve_onshell, SIG, _fmt
import itertools

def wordof(o):
    order=sorted(range(6),key=lambda i:abs(o[i]))
    return tuple(SIG[i] for i in order)

# generic integer-ish free params -> on-shell; R_spline must be integer (den-free)
pts=[(2,3,4,5),(3,5,2,7),(2,3,5,7),(4,7,3,5),(2,9,3,4),(5,8,2,3),(3,4,9,2),(6,11,2,5),
     (2,3,4,9),(7,3,2,11),(5,2,3,13),(2,15,3,4)]
print("chamber spread & denominator-free R_spline:")
words=set(); allint=True
for p in pts:
    o=solve_onshell(*p)
    A=amp_from_omega(o); R=R_spline(o)
    w=wordof(o); words.add(w)
    # R_spline integral? (for these, omega has denominators from solve; scale by lcm^8)
    from math import gcd
    dens=[x.denominator for x in o]; L=1
    for dd in dens: L=L*dd//gcd(L,dd)
    Rs=R*F(L)**8
    ok=(Rs.denominator==1)
    allint&=ok
    print(f"  free{p} word{w}: A6/i={_fmt(A):>16}  R_spline*L^8 integer={ok}")
print(f"distinct words hit: {len(words)}; all denominator-free: {allint}")

# dual-S3 symmetry: permute minus legs {0,1,2} and plus legs {3,4,5}; A6 invariant
o0=solve_onshell(2,3,5,7)
A0=amp_from_omega(o0)
print("\ndual-S3 symmetry (A6 invariant under minus-perm x plus-perm):")
bad=0
for pm in itertools.permutations([0,1,2]):
    for pp in itertools.permutations([3,4,5]):
        perm=list(pm)+list(pp)
        oo=[o0[perm[i]] for i in range(6)]
        # must stay on-shell (it does: same multiset within each sector)
        if amp_from_omega(oo)!=A0: bad+=1
print(f"  36 permutations checked; violations={bad}")

# hierarchical regime: one large frequency
oh=solve_onshell(2,3,4,100)
print("\nhierarchical (one large omega):")
print(f"  omega={[_fmt(x) for x in oh]}")
print(f"  A6/i={_fmt(amp_from_omega(oh))}  R_spline={_fmt(R_spline(oh))} (finite, denominator-free expected)")
Rh=R_spline(oh)
from math import gcd
dens=[x.denominator for x in oh]; L=1
for dd in dens: L=L*dd//gcd(L,dd)
print(f"  R_spline*L^8 integer={ (Rh*F(L)**8).denominator==1 }")
