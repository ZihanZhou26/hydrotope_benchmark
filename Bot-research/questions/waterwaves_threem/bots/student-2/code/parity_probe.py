#!/usr/bin/env python3
"""Determine the per-leg parity / odd-prefactor structure of the three-minus
amplitude, and verify the probabilistic (B-spline density) reading of the
two-minus law.

Parity: in raw --amp mode K and W are independent inputs. The amplitude is a
polynomial in the W_i at fixed momenta K (vertices contribute omega_a omega_b;
propagators omega_S^2). Flipping the sign of one W_i at fixed K reveals the
parity of the amplitude polynomial in that frequency. (We test the RAW
amplitude; on-shell parity is inherited since it is a restriction.)
"""
import subprocess, re, os, itertools
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BG = os.path.join(HERE, "bg")


def amp_raw(K, W):
    cmd = [BG, "--amp", "-K", ",".join(str(x) for x in K),
           "-W", ",".join(str(x) for x in W)]
    out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
    m = re.search(r"A_\d+ = i \* \(([-0-9/]+)\)", out)
    if m:
        return F(0), F(m.group(1))
    m = re.search(r"A_\d+ = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)", out)
    return F(m.group(1)), F(m.group(2))


def parity_in_leg(W0, sigmas, leg):
    """leg is 1-indexed. Returns (A0, A_flipped, relation)."""
    K = [F(sigmas[i]) * W0[i] ** 2 for i in range(len(W0))]
    re0, A0 = amp_raw(K, W0)
    Wf = list(W0); Wf[leg - 1] = -Wf[leg - 1]
    ref, Af = amp_raw(K, Wf)  # K unchanged (k = sigma w^2)
    rel = "EVEN" if Af == A0 else ("ODD" if Af == -A0 else "mixed")
    return A0, Af, rel


if __name__ == "__main__":
    sig6 = [-1, -1, -1, 1, 1, 1]
    # generic off-shell W (parity is a polynomial property, on/off shell same)
    W0 = [F(2), F(3), F(5), F(7), F(4), F(6)]
    print("=== n=6 three-minus: per-leg parity of the raw amplitude ===")
    for leg in range(1, 7):
        A0, Af, rel = parity_in_leg(W0, sig6, leg)
        print(f" flip leg {leg} (sigma={sig6[leg-1]:+d}):  A0={A0}  ->  {Af}   [{rel}]")

    print("\n flip a PAIR (two legs together):")
    for (a, b) in [(4, 5), (1, 2), (1, 4), (4, 6)]:
        K = [F(sig6[i]) * W0[i] ** 2 for i in range(6)]
        re0, A0 = amp_raw(K, W0)
        Wf = list(W0); Wf[a-1] = -Wf[a-1]; Wf[b-1] = -Wf[b-1]
        ref, Af = amp_raw(K, Wf)
        rel = "EVEN" if Af == A0 else ("ODD" if Af == -A0 else "mixed")
        print(f"  flip legs {a},{b}: {A0} -> {Af}  [{rel}]")

    # Also at n=5 to confirm the known omega4 omega5 odd structure
    print("\n=== n=5 three-minus: per-leg parity (expect even in 1,2,3; odd in 4,5) ===")
    sig5 = [-1, -1, -1, 1, 1]
    W5 = [F(2), F(3), F(5), F(7), F(4)]
    for leg in range(1, 6):
        A0, Af, rel = parity_in_leg(W5, sig5, leg)
        print(f" flip leg {leg} (sigma={sig5[leg-1]:+d}):  [{rel}]")
