#!/usr/bin/env python3
"""5-point calibration on the FRESH build: three-minus A_5 vs the known
sign-flipped two-minus formula (definition-of-done requirement). Independent."""
import sys, os
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from oracle import amp_onshell

def pos(x): return x if x>0 else F(0)

def A5_two_minus(w, aidx, bidx, others):
    """Two-minus A_n formula at n=5 for minus legs aidx,bidx (the sign-flipped
    image of three-minus A_5). A_n=i 2^{n-1} g^{3-n} wa wb sum_S (-1)^|S|
    (beta^2 - w_S^2)_+^{n-3}, beta=min(|wa|,|wb|). n=5 -> exponent 2, prefactor 16."""
    wa,wb=w[aidx],w[bidx]; beta=min(abs(wa),abs(wb))
    import itertools
    tot=F(0)
    for k in range(len(others)+1):
        for S in itertools.combinations(others,k):
            wS2=sum(w[j]**2 for j in S)
            tot += F(-1)**len(S) * pos(beta**2 - wS2)**2
    return 16*wa*wb*tot   # this is A_5/i

# Build three-minus A_5 via global sign flip <-> two-minus. sigma3m=(-1,-1,-1,+1,+1)
# The known map: three-minus A_5 = sign-flipped two-minus. We compare BG's A_5/i
# (three-minus) against the two-minus formula on the sign-flipped kinematics.
pts=[[F(-14,3),F(2),F(3),F(4),F(-13,3)],
     [F(-7,2),F(3),F(5),F(2),F(-13,2)],
     [F(-70,11),F(1),F(4),F(6),F(-51,11)],
     [F(-13,3),F(5,2),F(3),F(7,2),F(-14,3)]]
sig3m=[-1,-1,-1,1,1]
print("5-point calibration (three-minus A_5 vs sign-flipped two-minus):")
allok=True
for free in [p[1:4] for p in pts]:   # n=5 -> 3 free freqs (w2,w3,w4)
    om,re,im=amp_onshell(free, sig3m)   # BG three-minus A_5
    # sign flip: k_i->-k_i is sigma_i->-sigma_i. three-minus (-,-,-,+,+) -> (+,+,+,-,-)
    # = two-minus (legs 4,5 are the minus legs) at same omega.
    wflip=list(om)
    form = A5_two_minus(wflip, 3, 4, [0,1,2])   # minus legs = indices 3,4
    ok=(re==0 and im==form)
    allok=allok and ok
    print(f"  omega={om}  BG A5/i={im}  formula={form}  match={ok}")
print("CALIB:", "PASS" if allok else "CHECK")
