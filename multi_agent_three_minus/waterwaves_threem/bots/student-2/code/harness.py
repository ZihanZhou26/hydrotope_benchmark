#!/usr/bin/env python3
"""Fast harness wrapping the BG oracle ./bg for the three-minus sector.

Two evaluation modes:
  - on_shell(free, signs, double): uses ./bg -n N -w <free> -s <signs>, where
    <free> is the n-2 middle frequencies (legs 2..n-1); legs 1 and n are solved.
  - amp(K, W, double): uses ./bg --amp -K <momenta> -W <freqs> for arbitrary
    kinematics you build yourself (you must enforce dispersion + conservation).

Returns purely-imaginary amplitudes as a single value (re is 0 in this sector;
we assert that and return the imaginary coefficient).

Exact mode returns a fractions.Fraction; --double returns a float.
"""
import subprocess, re, os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BG = os.path.join(HERE, "bg")


def _parse(out, n, double):
    """Return (re, im, omegas) from oracle stdout."""
    if double:
        m = re.search(rf"A_{n} \(double\) = ([-0-9.eE+]+) \+ ([-0-9.eE+]+) i", out)
        re_p = float(m.group(1)); im = float(m.group(2))
        oms = [float(x) for x in re.search(r"omega = \{([^}]+)\}", out).group(1).split(",")]
        return re_p, im, oms
    # exact rational
    m = re.search(rf"A_{n} = i \* \(([-0-9/]+)\)", out)
    if m:
        re_p = F(0); im = F(m.group(1))
    else:
        m = re.search(rf"A_{n} = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)", out)
        re_p = F(m.group(1)); im = F(m.group(2))
    oms = [F(x.strip()) for x in re.search(r"omega = \{([^}]+)\}", out).group(1).split(",")]
    return re_p, im, oms


def on_shell(free, signs, double=False, g=1):
    """free = list of n-2 free freqs (legs 2..n-1). signs = list of n signs.
    Returns (im_coeff, omegas). Raises CalledProcessError on |k_S|=0 SIGFPE."""
    n = len(signs)
    cmd = [BG] + (["--double"] if double else []) + [
        "-n", str(n), "-w", ",".join(map(str, free)),
        "-s", ",".join(str(int(s)) for s in signs), "-g", str(g)]
    out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
    re_p, im, oms = _parse(out, n, double)
    return im, oms, re_p


def amp(K, W, double=False, g=1):
    """Raw BGAmplitude for arbitrary kinematics. K, W length-n lists.
    Returns (im_coeff, re_coeff)."""
    n = len(W)
    cmd = [BG] + (["--double"] if double else []) + [
        "--amp", "-K", ",".join(map(str, K)), "-W", ",".join(map(str, W)),
        "-g", str(g)]
    out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
    re_p, im, oms = _parse(out, n, double)
    return im, re_p


def solve_legs_1n(free, signs, g=1):
    """Reproduce the oracle's on-shell solve for legs 1 and n (exact).
    free = n-2 free freqs (legs 2..n-1, 0-indexed positions 1..n-2).
    Returns full omega list [w1, free..., wn] as Fractions."""
    free = [F(x) for x in free]
    n = len(signs)
    s1 = F(signs[0]);
    sumFree = sum(free)
    sumSig = sum(F(signs[i+1]) * free[i] * free[i] for i in range(n-2))
    wn = -(s1 * sumFree * sumFree + sumSig) / (2 * s1 * sumFree)
    w1 = -(sumFree + wn)
    return [w1] + free + [wn]


if __name__ == "__main__":
    # smoke test
    im, oms, re_p = on_shell([2, 3, 5, 7], [-1, -1, -1, 1, 1, 1])
    print("n=6 exact:", im, "re=", re_p, "omega=", oms)
    im_d, oms_d, _ = on_shell([2, 3, 5, 7], [-1, -1, -1, 1, 1, 1], double=True)
    print("n=6 double:", im_d)
    print("solve check:", solve_legs_1n([2, 3, 5, 7], [-1, -1, -1, 1, 1, 1]))
