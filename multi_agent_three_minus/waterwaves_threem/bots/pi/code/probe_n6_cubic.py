#!/usr/bin/env python3
"""Test cubic-block ansatze for A_6 three-minus.
n=5 three-minus (original vars): A_5 = i*2^4*g^{-2}* e2(plus){=w4 w5} * P_minus^(2)(min plus^2),
  P_minus^(d)(t) = sum_{S subseteq {1,2,3}} (-1)^|S| (t - sum_S w_j^2)_+^d.
n=6 degree counting forces exponent d = n-3 = 3 and a degree-2 prefactor.
Candidates (all times i*2^5*g^{-3}, g=1 so 2^5=32):
  T1 = e2(plus)  * P_minus^(3)(beta_plus^2),   beta_plus^2 = min(w4^2,w5^2,w6^2)
  T2 = e2(minus) * P_plus^(3)(beta_minus^2),   beta_minus^2= min(w1^2,w2^2,w3^2)
Compare A_6/i/32 to T1, T2, T1+T2, (T1+T2)/2.
"""
import subprocess, re, itertools
from fractions import Fraction as F

BG="./bg"; SIG="-1,-1,-1,1,1,1"
def run_onshell(freeW):
    ws=",".join(str(F(w)) for w in freeW)
    out=subprocess.run([BG,"-n","6","-w",ws,"-s",SIG],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    if out.returncode!=0: return None
    m=re.search(r"A_6 = i \* \(([-0-9/]+)\)",out.stdout)
    mo=re.search(r"omega = \{([^}]*)\}",out.stdout)
    om=[F(x.strip()) for x in mo.group(1).split(",")]
    return (F(m.group(1)), om) if m else None

def pos(x): return x if x>0 else F(0)
def Pblock(triple_sq, t, d):
    """sum_{S subseteq triple} (-1)^|S| (t - sum_S)_+^d ; triple_sq = the 3 squared freqs."""
    s=F(0)
    for mask in range(8):
        c=F(0); k=0
        for b in range(3):
            if mask&(1<<b): c+=triple_sq[b]; k+=1
        s += ((-1)**k) * pos(t-c)**d
    return s
def e2(vals):
    return sum(vals[i]*vals[j] for i,j in itertools.combinations(range(len(vals)),2))

pts=[(F(2),F(3),F(5),F(7)),(F(3),F(5),F(2),F(4)),(F(1),F(4),F(6),F(3)),
     (F(5),F(2),F(7),F(3)),(F(1),F(2),F(3),F(5)),(F(2),F(5),F(3),F(8))]
print(f"{'pt':>20} {'A/i/32':>16} {'T1':>14} {'T2':>14} {'T1+T2':>14} {'matchT1':>7} {'mT2':>5} {'mSum':>5}")
for fw in pts:
    r=run_onshell(fw)
    if r is None: print(f"{str(fw):>20}  skip"); continue
    A,om=r
    sq=[x*x for x in om]
    minus=sq[0:3]; plus=sq[3:6]
    target=A/F(32)
    T1=e2(om[3:6])*Pblock(minus, min(plus), 3)
    T2=e2(om[0:3])*Pblock(plus, min(minus), 3)
    print(f"{str(fw):>20} {str(target):>16} {str(T1):>14} {str(T2):>14} {str(T1+T2):>14} "
          f"{str(target==T1):>7} {str(target==T2):>5} {str(target==T1+T2):>5}")
    # also show ratios in case off by a clean factor
    if T1!=0: print(f"        ratio A/(i32 T1)={target/T1}   A/(i32 T2)={target/T2 if T2!=0 else None}   A/(i32 (T1+T2))={target/(T1+T2) if (T1+T2)!=0 else None}")
