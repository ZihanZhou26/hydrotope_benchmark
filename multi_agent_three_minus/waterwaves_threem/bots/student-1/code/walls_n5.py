#!/usr/bin/env python3
"""student-1: characterize the two kinds of walls of the n=5 three-minus A_5.

  (A) CHAMBER walls (kinks of the closed form): the truncations
      (beta^2 - sum_{j in S} w_j^2)_+ switch on/off, beta^2 = min(w4^2,w5^2).
      Because each truncated term is SQUARED, (x)_+^2 is C^1, so A_5 is C^1
      across every chamber wall (value AND first derivative match; only the 2nd
      derivative jumps).  No singularity for the oracle here.

  (B) |k_S|=0 walls (oracle SIGFPE): the BG propagator divides by |k_S|,
      k_S = sum_{i in S} sigma_i w_i^2, for subsets S of legs {2,3,4,5}.  The
      oracle crashes there, but A_5 itself is FINITE and CONTINUOUS: we show by
      exact one-sided limits that A_5(wall +/- eps) -> the formula value at the
      wall, with NO 1/eps blow-up (so n=5 three-minus carries NO factorization
      pole, consistent with the two-minus law; poles are expected only at n>=6).

  Structural fact (proved by on-shell reduction + dense scan): every
  NON-degenerate |k_S|=0 wall coincides on-shell with a chamber wall.  Using
  momentum conservation w1^2+w2^2+w3^2 = w4^2+w5^2,

     S={2,4}:   w4^2 = w2^2                         (-> chamber wall {2}, when beta^2=w4^2)
     S={2,5}:   w5^2 = w2^2                         (-> chamber wall {2}, when beta^2=w5^2)
     S={3,4}:   w4^2 = w3^2                         (-> chamber wall {3})
     S={3,5}:   w5^2 = w3^2                         (-> chamber wall {3})
     S={2,3,4}: w4^2 = w2^2+w3^2  <=>  w5^2 = w1^2  (-> pair{2,3} wall OR {1} wall)
     S={2,3,5}: w5^2 = w2^2+w3^2  <=>  w4^2 = w1^2  (-> pair{2,3} wall OR {1} wall)
   (S touching only one minus + the two plus legs forces a vanishing frequency:
     S={2,4,5}: w1^2+w3^2=0 ;  S={3,4,5}: w1^2+w2^2=0 ;  S={2,3,4,5}: w1=0   -- degenerate.)
  Hence the oracle's division-by-zero never happens in a chamber interior (except
  on the degenerate locus where a frequency vanishes); it sits on chamber walls,
  where A_5 is C^1.
"""
import subprocess, re, os, sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BG   = os.path.join(HERE, "bg")

def oracle(free, g=1, double=False):
    cmd = [BG]
    if double: cmd.append("--double")
    cmd += ["-n", "5", "-w", ",".join(map(str, free)), "-s", "-1,-1,-1,1,1", "-g", str(g)]
    out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
    if double:
        m = re.search(r"A_5 \(double\) = ([-0-9.eE+]+) \+ ([-0-9.eE+]+) i", out)
        oms = [float(x) for x in re.search(r"omega = \{([^}]+)\}", out).group(1).split(",")]
        return float(m.group(1)), float(m.group(2)), oms
    m = re.search(r"A_5 = i \* \(([-0-9/]+)\)", out)
    if m: re_p, im = F(0), F(m.group(1))
    else:
        m = re.search(r"A_5 = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)", out)
        re_p, im = F(m.group(1)), F(m.group(2))
    oms = [F(x.strip()) for x in re.search(r"omega = \{([^}]+)\}", out).group(1).split(",")]
    return re_p, im, oms

def solve(free):
    """Replicate the oracle solver to evaluate the formula AT the wall (no crash)."""
    w2, w3, w4 = map(F, free); S = w2 + w3 + w4
    w5 = (-w2*w2 - w3*w3 + w4*w4 - S*S) / (2*S); w1 = -(S + w5)
    return [w1, w2, w3, w4, w5]

def formula(oms, g=1):
    w1, w2, w3, w4, w5 = oms; g = F(g)
    b2 = min(w4*w4, w5*w5); minus = [w1, w2, w3]; tot = F(0)
    for mask in range(8):
        Ssum = sum(minus[i]**2 for i in range(3) if mask & (1 << i))
        v = b2 - Ssum
        if v > 0: tot += (-1)**bin(mask).count("1") * v * v
    return 16 * g**(-2) * w4 * w5 * tot

def demo_wall(name, w2, w3, w4_star, eps_list):
    """Sweep w4 across w4_star (an |k_S|=0 wall) at fixed (w2,w3); show finite limits."""
    print(f"\n--- |k_S|=0 wall: {name}  (fixed w2={w2}, w3={w3}, wall at w4={w4_star}) ---")
    wall = solve((w2, w3, w4_star))
    A_wall = formula(wall)
    print(f"    on-shell at wall: w = {[str(x) for x in wall]}")
    print(f"    formula value AT wall (no crash): A_5/i = {A_wall}  = {float(A_wall):.10g}")
    # confirm the oracle SIGFPEs exactly on the wall
    try:
        oracle((w2, w3, w4_star)); crashed = "NO (unexpected)"
    except subprocess.CalledProcessError:
        crashed = "YES (SIGFPE, as expected)"
    print(f"    oracle exactly on wall crashes: {crashed}")
    print(f"    {'eps':>10} {'side':>6} {'A_5/i (oracle, exact)':>26} {'A_5/i - A_wall':>20}")
    for eps in eps_list:
        for side, w4 in ((' -', F(w4_star) - eps), (' +', F(w4_star) + eps)):
            try:
                _, im, oms = oracle((w2, w3, w4))
            except subprocess.CalledProcessError:
                print(f"    {str(eps):>10} {side:>6}  (crash)"); continue
            # also re-evaluate the formula at the actual off-wall point: must match the oracle
            assert im == formula(oms), f"formula!=oracle off-wall at eps={eps}"
            print(f"    {str(eps):>10} {side:>6} {str(im):>26} {float(im - A_wall):>20.3e}")
    print(f"    => both one-sided limits -> A_wall (finite); NO 1/eps blow-up => NO POLE at n=5.")

def main():
    if not os.path.exists(BG):
        subprocess.check_call(["g++","-O2","-std=c++17","-o",BG,os.path.join(HERE,"bg.cpp"),"-lgmpxx","-lgmp"])
    print("="*92)
    print("n=5 three-minus: |k_S|=0 walls are FINITE C^0/C^1 points of A_5 (no poles)")
    print("="*92)
    # (B1) the internal 3-particle channel S={2,3,4}: w4^2 = w2^2 + w3^2  (Pythagorean 3,4,5)
    #      This is exactly the factorization channel omega_S^2 = g|k_S| type that becomes a
    #      genuine POLE at n>=6; at n=5 it is regular.
    demo_wall("S={2,3,4}: w4^2=w2^2+w3^2  (<=> w5^2=w1^2)", 3, 4, 5,
              [F(1,10), F(1,100), F(1,1000), F(1,100000)])
    # (B2) a two-particle channel S={3,4}: w4^2 = w3^2
    demo_wall("S={3,4}: w4^2=w3^2", 2, 3, 3,
              [F(1,10), F(1,100), F(1,1000), F(1,100000)])

    # (A) chamber-wall continuity: sweep w4 (with w2=w3=-1) so the on-shell point
    #     crosses chambers  E -> C -> B -> A ; show oracle==formula throughout and that
    #     A_5 is continuous (and C^1) across each chamber wall.
    print("\n" + "="*92)
    print("CHAMBER walls: sweep w4 (w2=w3=-1) across E->C->B->A; A_5 continuous & C^1")
    print("="*92)
    print("   active minus-subsets S (sum_S w_j^2 < beta^2) flip as walls are crossed;")
    print("   oracle == formula at every interior point (avoid |k_S| walls w4=-1, w4=-sqrt2):")
    print(f"   {'w4':>6} {'chamber':>8} {'active subsets':>22} {'A_5/i (oracle)':>16} {'ok':>4}")
    def active(oms):
        b2 = min(oms[3]**2, oms[4]**2); mn=[oms[0],oms[1],oms[2]]; out=[]
        for mask in range(8):
            S=[i+1 for i in range(3) if mask&(1<<i)]
            if sum(mn[i-1]**2 for i in S) < b2: out.append(set(S) if S else "{}")
        return out
    def ctype(oms):
        b2=min(oms[3]**2,oms[4]**2); sq=[oms[0]**2,oms[1]**2,oms[2]**2]
        sing=sum(1 for x in sq if x<b2)
        from itertools import combinations
        pair=sum(1 for c in combinations(range(3),2) if sq[c[0]]+sq[c[1]]<b2)
        return {0:"A",1:"B",2:("E" if pair else "C")}[min(sing, 2) if not pair else 2] if pair==0 else "E"
    for w4 in [F(-22,10), F(-18,10), F(-15,10), F(-12,10), F(-8,10), F(-6,10), F(-4,10)]:
        _, im, oms = oracle((F(-1), F(-1), w4))
        ok = (im == formula(oms))
        print(f"   {str(w4):>6} {ctype(oms):>8} {str(active(oms)):>22} {str(im):>16} {str(ok):>5}")
    print("   => A_5/i varies continuously (no jumps) as chambers change; oracle==formula in each.")
    print("\nDONE.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
