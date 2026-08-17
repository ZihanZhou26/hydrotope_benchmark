#!/usr/bin/env python3
"""Round-2 student-2 headline verifications (exact, own oracle ./bg).

(A) SOFT THEOREM (new): as any leg omega_i -> 0 on the three-minus n=6 manifold,
    A_6 -> 2(n-3) * omega_i^2 * A_5(surviving 5 legs), with 2(n-3)=6 at n=6.
      - soft PLUS leg  -> A_5 in the THREE-minus sector (known closed form)
      - soft MINUS leg -> A_5 in the TWO-minus sector  (known closed form)
    Verified by exact rational Richardson extrapolation: lim A_6/(i w^2 A_5) = 6.
(B) Structural facts: e2(minus)=e2(plus) on-shell; homogeneous degree 2n-4=8.
(C) Ruled-out closed-form families (see batch1/batch2/chamber_fit2/extract_even):
    even-in-omega^2, prod(omega)*linear, e2*poly(omega^2), double-subset resonance
    spline (exp 2/3/4, ()_+ and |.|), same-type and mixed-type pair sums -- ALL FAIL.
Run: python3 verify_r2.py
"""
from fractions import Fraction as F
import sympy as sp, itertools
import harness as h

SIG6=[-1,-1,-1,1,1,1]


def A5_three(w1,w2,w3,w4,w5):
    m=min(w4**2,w5**2); tot=F(0); L=[w1,w2,w3]
    for r in range(4):
        for S in itertools.combinations(range(3),r):
            v=m-sum(L[i]**2 for i in S)
            if v>0: tot+=F((-1)**r)*v**2
    return 16*w4*w5*tot


def A5_two(wa,wb,plus):
    b2=min(wa**2,wb**2); tot=F(0)
    for r in range(4):
        for S in itertools.combinations(range(3),r):
            v=b2-sum(plus[i]**2 for i in S)
            if v>0: tot+=F((-1)**r)*v**2
    return 16*wa*wb*tot


def richardson_limit(seq):
    X=sp.Symbol('e')
    pts=[(sp.Rational(e.numerator,e.denominator), sp.Rational(v.numerator,v.denominator)) for e,v in seq]
    return sp.expand(sp.interpolate(pts,X)).subs(X,0)


def soft_plus():
    base=[F(3),F(5),F(4)]  # legs 2,3,4 ; leg5=eps
    seq=[]
    for k in range(3,11):
        eps=F(1,2**k)
        im6,om6,_=h.on_shell([base[0],base[1],base[2],eps],SIG6)
        w=[F(o) for o in om6]
        a5=A5_three(w[0],w[1],w[2],w[3],w[5])  # plus legs 4,6 (leg5->0)
        seq.append((eps, F(im6,1)/(eps**2*a5)))
    return richardson_limit(seq)


def soft_minus():
    base=[F(5),F(4),F(6)]  # legs 3,4,5 ; leg2=eps
    seq=[]
    for k in range(3,11):
        eps=F(1,2**k)
        im6,om6,_=h.on_shell([eps,base[0],base[1],base[2]],SIG6)
        w=[F(o) for o in om6]
        a5=A5_two(w[0],w[2],[w[3],w[4],w[5]])  # minus legs 1,3 ; plus 4,5,6
        seq.append((eps, F(im6,1)/(eps**2*a5)))
    return richardson_limit(seq)


def e2(v): return sum(v[i]*v[j] for i,j in itertools.combinations(range(len(v)),2))


if __name__=="__main__":
    print("=== (A) SOFT THEOREM ===")
    cp=soft_plus();  print(f" soft PLUS  leg: lim A_6/(i w^2 A5_3minus) = {cp}  (expect 2(n-3)=6)")
    cm=soft_minus(); print(f" soft MINUS leg: lim A_6/(i w^2 A5_2minus) = {cm}  (expect 2(n-3)=6)")
    print("\n=== (B) structural ===")
    import random; random.seed(1); oke=okd=N=0
    for _ in range(12):
        free=[F(random.randint(1,9),random.choice([1,2,3])) for _ in range(4)]
        try:
            om=h.solve_legs_1n(free,SIG6); im,_,_=h.on_shell(free,SIG6)
            im2,_,_=h.on_shell([2*x for x in free],SIG6)
        except Exception: continue
        N+=1
        oke+= (e2(om[0:3])==e2(om[3:6]))
        okd+= (im2==256*im)
    print(f" e2(minus)=e2(plus): {oke}/{N};  A(2w)=2^8 A(w): {okd}/{N}")
    print("\n(C) ruled-out families: see batch1.py, batch2.py, chamber_fit2.py, extract_even.py")
