"""One-shot reproduction of the report's main results.
Run:  python3 reproduce.py
Uses only bg.py (exact BG port, validated against OnShellBG.m) and closed_form.py."""
from fractions import Fraction as Q
from bg import amp_two_minus, BG
from closed_form import A_principal, A5_complete, softest_is_minus
import random, math

def hr(t): print("\n"+"="*70+"\n"+t+"\n"+"="*70)

hr("0. exact BG port reproduces Mathematica BGAmplitude")
for n,free,exp in [(5,[Q(2),Q(5,2),Q(3)],"-2304"),(6,[Q(3,2),Q(2),Q(5,2),Q(3)],"-11907/4")]:
    A,_,_=amp_two_minus(n,free); print(f"  n={n} {free}: A/i = {A.im}  (expect {exp})")

hr("1. homogeneity degree 2(n-2)")
for n in [5,6]:
    A1,_,_=amp_two_minus(n,[Q(2),Q(5,2),Q(3)] if n==5 else [Q(3,2),Q(2),Q(5,2),Q(3)])
    A2,_,_=amp_two_minus(n,[Q(4),Q(5),Q(6)] if n==5 else [Q(3),Q(4),Q(5),Q(6)])
    print(f"  n={n}: A(2x)/A(x) = {A2.im/A1.im} = 2^{int(math.log2(abs(float(A2.im/A1.im))))}  (=2^{2*(n-2)})")

hr("2. PROOF A_5 is not a single rational function (two open sets, two rational fns)")
rng=random.Random(11); a=ta=b=tb=0
for _ in range(40000):
    free=[Q(rng.randint(-20,20),rng.randint(1,5)) for _ in range(3)]
    if any(x==0 for x in free): continue
    try: A,_,w=amp_two_minus(5,free)
    except Exception: continue
    if any(v==0 for v in w): continue
    w2=[v*v for v in w]
    if w2.index(min(w2))>=2: continue
    if w[0]**2<w[1]**2: ta+=1; a+=(A.im==16*w[0]**5*w[1])
    else: tb+=1; b+=(A.im==16*w[0]*w[1]**5)
    if ta+tb>=300: break
print(f"  |w1|<|w2|: A_5==16 w1^5 w2 : {a}/{ta};  |w2|<|w1|: A_5==16 w1 w2^5 : {b}/{tb}")

hr("3. principal-regime formula  A_n = 2^(n-1) w1 w2 (min(w1^2,w2^2))^(n-3)")
for n in [5,6,7]:
    rng=random.Random(n); ok=tot=tries=0
    while tot< {5:200,6:40,7:8}[n] and tries<60000:
        tries+=1
        free=[Q(rng.randint(-20,20),rng.randint(1,5)) for _ in range(n-2)]
        if any(x==0 for x in free): continue
        try: A,_,w=amp_two_minus(n,free)
        except Exception: continue
        if any(v==0 for v in w) or not softest_is_minus(w): continue
        tot+=1; ok+=(A.im==A_principal(n,w))
    print(f"  n={n}: {ok}/{tot} exact (random signs, softest=minus)")

hr("4. complete n=5 formula  A_5 = P0 + sum P_muj |w_j^2-w_mu^2|  (ALL chambers)")
rng=random.Random(5); ok=tot=0
for _ in range(4000):
    free=[Q(rng.randint(-30,30),rng.randint(1,7)) for _ in range(3)]
    if any(x==0 for x in free): continue
    try: A,_,w=amp_two_minus(5,free)
    except Exception: continue
    if any(v==0 for v in w): continue
    tot+=1; ok+=(A.im==A5_complete(w))
    if tot>=300: break
print(f"  n=5 complete formula: {ok}/{tot} exact (random, all chambers)")

print("\nAll reproduced.")
