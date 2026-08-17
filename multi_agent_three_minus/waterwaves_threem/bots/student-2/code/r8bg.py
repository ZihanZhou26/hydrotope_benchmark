#!/usr/bin/env python3
"""Fast wrapper around my own ./bg --batch (exact GMP or --double).
Sector helpers for three-minus. All in one subprocess call."""
import subprocess, os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BG = os.path.join(HERE, "bg")

def signs3m(n):
    return [-1,-1,-1] + [1]*(n-3)

def batch(free_list, n, double=False):
    """free_list: list of (n-2)-tuples of frequencies. Returns list of A_n/i
       (Fraction if exact, float if double) or None on wall/ERR.  re assumed 0."""
    sig = ",".join(str(s) for s in signs3m(n))
    lines = []
    for fr in free_list:
        lines.append(f"{n}|" + ",".join(str(F(x)) for x in fr) + f"|{sig}")
    cmd = [BG, "--batch"] + (["--double"] if double else [])
    out = subprocess.run(cmd, input="\n".join(lines).encode(),
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode()
    res = []
    for ln in out.strip("\n").split("\n"):
        if ln == "ERR" or ln == "":
            res.append(None); continue
        re_s, im_s = ln.split(";")
        if double:
            res.append(float(im_s))
        else:
            res.append(F(im_s))
    return res

def solve_legs(free, n):
    """Return full omega list (Fractions) for three-minus on-shell."""
    free = [F(x) for x in free]
    s1 = F(-1)
    sumFree = sum(free)
    sumSig = sum(F(signs3m(n)[i+1]) * free[i]**2 for i in range(n-2))
    wn = -(s1*sumFree**2 + sumSig)/(2*s1*sumFree)
    w1 = -(sumFree + wn)
    return [w1] + free + [wn]

def amp_one(free, n, double=False):
    return batch([free], n, double)[0]

if __name__ == "__main__":
    # cross-check exact vs ./bg single-call and the known values
    print("n=6:", amp_one([2,3,5,7], 6), "(expect -29948208/17)")
    print("n=7:", amp_one([2,3,5,7,11], 7))
    print("n=7 double:", amp_one([2,3,5,7,11], 7, double=True))
    oms = solve_legs([2,3,5,7], 6)
    print("solve_legs n=6:", [str(x) for x in oms])
