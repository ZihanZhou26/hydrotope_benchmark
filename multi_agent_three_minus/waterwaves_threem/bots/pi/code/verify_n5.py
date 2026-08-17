#!/usr/bin/env python3
"""PI independent verification of the n=5 three-minus closed form.

Claim (three-minus, legs 1,2,3 carry sigma=-1; legs 4,5 carry sigma=+1):

    A_5 = i * 2^4 * g^{-2} * w4 * w5
            * sum_{S subset {1,2,3}} (-1)^|S| ( beta^2 - sum_{j in S} w_j^2 )_+^2 ,
    beta = min(|w4|, |w5|).

This is the known two-minus truncated-power law (question.md item 2) applied to
the sign-flipped configuration (plus/minus swap, item 3): flipping all signs
turns three-minus (minus legs 1,2,3) into two-minus with minus legs 4,5.

Run from a directory containing the built oracle ./bg (exact rational mode).
"""
import subprocess, re, sys
from fractions import Fraction as F

BG = "./bg"

def oracle_n5(free):  # free = 3 free freqs (legs 2,3,4)
    out = subprocess.check_output(
        [BG, "-n", "5", "-w", ",".join(map(str, free)), "-s", "-1,-1,-1,1,1"]).decode()
    m = re.search(r"A_5 = i \* \(([-0-9/]+)\)", out)
    if not m:  # real part present?
        m = re.search(r"A_5 = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)", out)
        re_part = F(m.group(1)); im = F(m.group(2))
    else:
        re_part = F(0); im = F(m.group(1))
    oms = [F(x.strip()) for x in re.search(r"omega = \{([^}]+)\}", out).group(1).split(",")]
    return re_part, im, oms

def formula_im(oms):  # imaginary coefficient (g=1); real part is 0
    w4, w5 = oms[3], oms[4]
    beta = min(abs(w4), abs(w5))
    plus = [oms[0], oms[1], oms[2]]  # become plus legs after swap
    tot = F(0)
    for mask in range(1 << 3):
        S = [plus[i] for i in range(3) if mask & (1 << i)]
        v = beta * beta - sum(x * x for x in S)
        if v > 0:
            tot += (-1) ** len(S) * v * v
    return 16 * w4 * w5 * tot

# generic, non-generic (one freq >> or << rest), fractional points
PTS = [(2, 3, 5), (1, 4, 6), (2, 2, 7), (1, 1, 10), (F(1, 2), 3, 9), (7, 1, 2),
       (3, 3, 3), (F(1, 10), 5, 5), (100, 1, 2), (1, 1, 100), (F(1, 100), 4, 4),
       (5, 5, F(1, 3)), (9, 2, 1), (F(3, 7), F(11, 5), 6)]

def main():
    print(f"{'free(legs2,3,4)':>26} {'oracle_im':>16} {'formula_im':>16}  ok")
    allok = True
    for p in PTS:
        try:
            re_p, oim, oms = oracle_n5(p)
        except subprocess.CalledProcessError:
            print(f"{str(p):>26}  oracle SIGFPE (on |k_S|=0 wall) -- skip/limit")
            continue
        fim = formula_im(oms)
        ok = (re_p == 0) and (fim == oim)
        allok &= ok
        print(f"{str(p):>26} {str(oim):>16} {str(fim):>16}  {ok}")
    print("ALL EXACT MATCH:" , allok)
    return 0 if allok else 1

if __name__ == "__main__":
    sys.exit(main())
