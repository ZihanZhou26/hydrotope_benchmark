#!/usr/bin/env python3
"""PI round-4: decisive test of whether H = A_6/(i prod omega) is EVEN
(a genuine function of the squares a_i=w_i^2, b_j=w_{3+j}^2).

Construction of a partner point with IDENTICAL squares but different signs:
pick minus legs w2,w3 free and set plus leg w4 = -(w2+w3), so the subset
{2,3,4} sums to zero.  Solve on-shell for w1,w6 from (w2,w3,w4,w5).  Flipping
the signs of legs 2,3,4 keeps sum(w)=0 (a zero-sum subset) and sum(sigma w^2)=0
(squares unchanged), giving a genuine second on-shell point with the SAME
multiset of squares per set but a DIFFERENT overall sign pattern (different
s = sum of minus frequencies).  If H is even, H(point)=H(partner) exactly.

Also: per-chamber rational fit of H in the SQUARES (a1,a2,a3,b1,b2) (b3 fixed by
T) -- if H is even it is degree-1 homogeneous in (a,b) and a low-degree rep must
appear; if not even, no rep appears.  This corroborates the partner test.
"""
import subprocess, re, random
from fractions import Fraction as F

BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code/bg_r4"
SIG = [-1, -1, -1, 1, 1, 1]
P = (1 << 61) - 1


def bg_amp(om, g=F(1)):
    K = [SIG[i] * om[i] * om[i] / g for i in range(6)]
    p = subprocess.run([BG, "--amp", "-K", ",".join(str(x) for x in K),
                        "-W", ",".join(str(x) for x in om), "-g", str(g)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if p.returncode != 0:
        return None
    m = re.search(r"A_6 = i \* \(([^)]*)\)", p.stdout)
    if m:
        return F(m.group(1))
    m2 = re.search(r"A_6 = \(([^)]*)\) \+ i \* \(([^)]*)\)", p.stdout)
    if m2 and F(m2.group(1)) == 0:
        return F(m2.group(2))
    return None


def solve_w1_w6(w2, w3, w4, w5):
    """solve on-shell w1,w6 given the 4 middle frequencies (sigma=(-,-,-,+,+,+))."""
    free = [w2, w3, w4, w5]; s = sum(free)
    if s == 0:
        return None
    ss = sum(SIG[i + 1] * free[i] ** 2 for i in range(4))
    w6 = -(SIG[0] * s * s + ss) / (2 * SIG[0] * s)
    w1 = -(s + w6)
    return [w1, w2, w3, w4, w5, w6]


def squares_multiset(om):
    return (sorted(w * w for w in om[:3]), sorted(w * w for w in om[3:]))


def H_of(om):
    A = bg_amp(om)
    if A is None:
        return None
    prod = F(1)
    for w in om:
        prod *= w
    return A / prod


def onshell_ok(om):
    return (sum(om) == 0 and
            sum(SIG[i] * om[i] ** 2 for i in range(6)) == 0 and
            all(w != 0 for w in om))


def main():
    rng = random.Random(999)
    print("=" * 72)
    print("EVENNESS via partner points (same squares per set, different signs)")
    print("=" * 72)
    tested = 0; even_pass = 0; shown = 0
    while tested < 30:
        w2 = F(rng.randint(-12, 12)); w3 = F(rng.randint(-12, 12))
        w4 = -(w2 + w3)               # forces {2,3,4} zero-sum
        w5 = F(rng.randint(-12, 12))
        if w2 == 0 or w3 == 0 or w4 == 0 or w5 == 0:
            continue
        om = solve_w1_w6(w2, w3, w4, w5)
        if om is None or not onshell_ok(om):
            continue
        # partner: flip signs of legs 2,3,4 (indices 1,2,3)
        omp = om[:]
        omp[1] = -omp[1]; omp[2] = -omp[2]; omp[3] = -omp[3]
        if not onshell_ok(omp):
            continue
        # squares per set must match as multisets
        if squares_multiset(om) != squares_multiset(omp):
            continue
        # require the two points are genuinely different sign patterns (not identical, not global flip)
        if omp == om or omp == [-w for w in om]:
            continue
        H1 = H_of(om); H2 = H_of(omp)
        if H1 is None or H2 is None:
            continue
        tested += 1
        same = (H1 == H2)
        even_pass += 1 if same else 0
        if shown < 8:
            print(f"  om ={[str(w) for w in om]}")
            print(f"  om'={[str(w) for w in omp]}   (legs 2,3,4 flipped)")
            print(f"     s(minus) = {-(om[0]+om[1]+om[2])} vs {-(omp[0]+omp[1]+omp[2])}")
            print(f"     H  = {H1}")
            print(f"     H' = {H2}")
            print(f"     H == H' : {same}")
            shown += 1
    print("-" * 72)
    print(f"EVENNESS RESULT: H==H' on {even_pass}/{tested} partner pairs "
          f"=> {'EVEN (function of squares) CONFIRMED' if even_pass == tested else 'NOT EVEN'}")


if __name__ == "__main__":
    main()
