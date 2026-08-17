"""n=5 closed form as 3 sorted-leg cases (covers ALL kinematics). Exact check vs BG.
Let m1=|w1|,m2=|w2| (minus legs); among the 3 plus legs let p=softest plus.
 Sort all 5 legs by |w|; let (t1, t2) be types of the two softest:
   t1 = minus:          A = 16 w1 w2 (min(w1^2,w2^2))^2
   t1=plus, t2=minus:   A = 16 w1 w2 * p^2 (2*mm^2 - p^2)      [p=softest plus, mm=softest minus]
   t1=plus, t2=plus:    A = 32 w1 w2 * p1^2 p2^2               [p1,p2 = two softest plus]
"""
from bg import amp_two_minus
from fractions import Fraction as Q
import itertools, random

def predict5(w):
    w2=[v*v for v in w]
    typ=['m','m','p','p','p']
    order=sorted(range(5), key=lambda i: w2[i])
    t1,t2=typ[order[0]],typ[order[1]]
    softmin_minus=min(w[0]*w[0], w[1]*w[1])   # softest minus^2
    plus_sorted=sorted([w[2],w[3],w[4]], key=lambda v:v*v)
    p1,p2=plus_sorted[0],plus_sorted[1]
    if t1=='m':
        return 16*w[0]*w[1]*softmin_minus**2
    elif t2=='m':   # t1='p'
        return 16*w[0]*w[1]*(p1*p1)*(2*softmin_minus - p1*p1)
    else:           # t1='p', t2='p'
        return 32*w[0]*w[1]*(p1*p1)*(p2*p2)

rng=random.Random(7)
ok=0;tested=0
for _ in range(6000):
    free=[Q(rng.randint(-30,30),rng.randint(1,9)) for _ in range(3)]
    if any(x==0 for x in free): continue
    try: A,kL,wL=amp_two_minus(5,free)
    except Exception: continue
    if any(v==0 for v in wL): continue
    tested+=1
    if A.im==predict5(tuple(wL)): ok+=1
    elif ok+5>tested: print("MISMATCH", [str(v) for v in wL], A.im, predict5(tuple(wL)))
    if tested>=1500: break
print(f"n=5 sorted-case formula: {ok}/{tested} exact matches (all chambers)")
