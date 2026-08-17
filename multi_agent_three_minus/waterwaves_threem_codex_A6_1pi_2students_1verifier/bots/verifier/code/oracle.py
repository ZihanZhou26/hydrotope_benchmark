#!/usr/bin/env python3
"""Independent verifier oracle wrapper around a freshly built bg binary.

We NEVER import a student's evaluator. We only shell out to our own bg
(built from an md5-verified copy of the shared bg.cpp) and parse its exact
rational output. All auxiliary arithmetic on the verifier side uses
fractions.Fraction so every check is exact.
"""
import subprocess, re, os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BG = os.path.join(HERE, "bg")

_re_i   = re.compile(r"A_\d+ = i \* \(([^)]*)\)")
_re_cpx = re.compile(r"A_\d+ = \(([^)]*)\) \+ i \* \(([^)]*)\)")
_re_om  = re.compile(r"omega = \{([^}]*)\}")

def _pf(s):
    s = s.strip()
    return F(s) if s else F(0)

def amp_raw(K, W, g=1):
    """Raw BGAmplitude at explicit momenta K and frequencies W (exact).
    Returns (re, im) as Fractions."""
    Ks = ",".join(str(F(x)) for x in K)
    Ws = ",".join(str(F(x)) for x in W)
    out = subprocess.run([BG, "--amp", "-K", Ks, "-W", Ws, "-g", str(F(g))],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True).stdout
    m = _re_i.search(out)
    if m:
        return F(0), _pf(m.group(1))
    m = _re_cpx.search(out)
    if m:
        return _pf(m.group(1)), _pf(m.group(2))
    raise RuntimeError("cannot parse:\n"+out)

def amp_onshell(freeW, sigma, g=1):
    """On-shell mode (bg -n N -w ... -s ...). Returns (omega_list, re, im)."""
    N = len(sigma)
    ws = ",".join(str(F(x)) for x in freeW)
    ss = ",".join(str(int(s)) for s in sigma)
    out = subprocess.run([BG, "-n", str(N), "-w", ws, "-s", ss, "-g", str(F(g))],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True).stdout
    om = [_pf(x) for x in _re_om.search(out).group(1).split(",")]
    m = _re_i.search(out)
    if m:
        return om, F(0), _pf(m.group(1))
    m = _re_cpx.search(out)
    if m:
        return om, _pf(m.group(1)), _pf(m.group(2))
    raise RuntimeError("cannot parse:\n"+out)

def amp_from_omega_sigma(omega, sigma, g=1):
    """Given full omega vector and sign vector, build K and call raw amp."""
    K = [F(sigma[i]) * F(omega[i])**2 / F(g) for i in range(len(omega))]
    return amp_raw(K, omega, g)

if __name__ == "__main__":
    # smoke test: anchor 1
    om, re_, im_ = amp_onshell([2,3,4,5], [-1,-1,-1,1,1,1])
    print("anchor1 omega:", om)
    print("anchor1 A_6/i:", im_, " (expect -9190656/7 =", F(-9190656,7), ")")
    assert im_ == F(-9190656,7), "anchor mismatch"
    print("OK")
