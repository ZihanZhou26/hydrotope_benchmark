#!/usr/bin/env python3
"""PI round-7: two-sided WALL-LIMIT checks of s1_018, plus structural self-consistency
of the assembled formula (oddness, homogeneity). Uses only pi_r7_independent (PI's own
evaluator) and the PI's own ./bg. The oracle SIGFPEs exactly ON a wall; the closed form
must match it (finite, continuous) on BOTH sides as eps->0."""
import subprocess, re, os
from fractions import Fraction as F
from pi_r7_independent import A6_imag, solve_omega, oracle, BG, N6, invariants, chamber_label

EPS=[F(1,10),F(1,100),F(1,1000),F(1,10000)]

def check_slice(name, freefun, wall_desc):
    print(f"\n=== {name}  (wall: {wall_desc}) ===")
    allok=True
    for sgn in (+1,-1):
        side="+eps" if sgn>0 else "-eps"
        for e in EPS:
            t=sgn*e
            free=freefun(t)
            o=solve_omega(free)
            if o is None or any(x==0 for x in o):
                print(f"  {side} eps={e}: degenerate kinematics, skip"); continue
            if (o[0]*o[1]*o[2]+o[3]*o[4]*o[5])==0:
                print(f"  {side} eps={e}: on pole e3m+e3p=0, skip"); continue
            res=oracle(free)
            if res is None:
                print(f"  {side} eps={e}: oracle SIGFPE (on a wall), skip"); continue
            oom,Aim=res
            if any(a!=b for a,b in zip(o,oom)):
                print(f"  {side} eps={e}: KIN MISMATCH"); allok=False; continue
            f=A6_imag(o)
            match=(f==Aim)
            allok=allok and match
            print(f"  {side} eps={e}: match={match}  A6/i={Aim}")
    print(f"  --> {'ALL MATCH' if allok else 'FAILURE'}")
    return allok

if __name__=="__main__":
    print("="*78); print("PI round-7 WALL-LIMIT + structural checks of s1_018"); print("="*78)
    res=[]
    # (1=1) wall: plus leg w4 -> minus leg w2 (b3 = a1). base w2=3,w3=5,w5=7.
    res.append(check_slice("(1=1) wall  w4->w2",
        lambda t: (F(3),F(5),F(3)+t,F(7)), "omega_4^2 = omega_2^2  (single mixed wall)"))

    # (1=2) wall: minus free leg w2 with w2^2 -> w4^2+w5^2 (Pythagorean 3,4,5). a1 = b3+b4.
    res.append(check_slice("(1=2) wall  w2->sqrt(w4^2+w5^2)",
        lambda t: (F(5)+t,F(2),F(3),F(4)), "omega_2^2 = omega_4^2+omega_5^2  (single (1=2) wall)"))

    # matching corner: TWO (1=1) walls at once, w4->w2 and w5->w3 (forces a perfect matching).
    res.append(check_slice("matching corner  w4->w2 & w5->w3",
        lambda t: (F(3),F(5),F(3)+t,F(5)+t), "omega_4=omega_2 AND omega_5=omega_3 (matching)"))

    # ---- structural self-consistency of the FORMULA (no oracle) ----
    print("\n"+"="*78); print("Structural self-consistency of the assembled N_6 / A_6 (formula only)"); print("="*78)
    import random
    rnd=random.Random(7)
    odd_ok=hom_ok=cnt=0
    for _ in range(12):
        free=tuple(F(rnd.randint(-90,90),rnd.choice([1,2,5])) for _ in range(4))
        if any(x==0 for x in free): continue
        o=solve_omega(free)
        if o is None or any(x==0 for x in o): continue
        if (o[0]*o[1]*o[2]+o[3]*o[4]*o[5])==0: continue
        cnt+=1
        # oddness: N6(-w) == -N6(w)
        nm=N6([-x for x in o]); n=N6(o)
        odd_ok += (nm==-n)
        # homogeneity: A6_imag(2w)==256*A6_imag(w)  (deg 8)
        a=A6_imag(o); a2=A6_imag([2*x for x in o])
        hom_ok += (a2==256*a)
    print(f"  N_6 ODD under w->-w:                 {odd_ok}/{cnt}")
    print(f"  A_6 homogeneous degree 8 (256x at 2w): {hom_ok}/{cnt}")

    print("\n"+"="*78)
    print("WALL LIMITS:", "ALL PASS" if all(res) else "SOME FAIL")
    print("="*78)
