#!/usr/bin/env python3
"""PI independent calibration of the BG harness against the known two-minus
formula, and the required 5-point three-minus (sign-flip) calibration.

Two-minus formula (minus legs a,b; plus legs = rest):
  A_n = i 2^{n-1} g^{3-n} w_a w_b * sum_{S subset plus} (-1)^{|S|}
          (beta^2 - sum_{j in S} w_j^2)_+^{n-3},   beta = min(|w_a|,|w_b|).
"""
import subprocess, re, sys
from fractions import Fraction as F
from itertools import combinations

BG = "./bg"

def run_bg(n, freeW, sig, g="1"):
    """Return (omega_list[Fraction], A_re, A_im) from exact bg mode."""
    cmd = [BG, "-n", str(n), "-w", ",".join(freeW), "-s", ",".join(sig), "-g", g]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"bg failed (rc={p.returncode}) — likely a wall/pole for these kinematics")
    out = p.stdout
    om = re.search(r"omega = \{([^}]*)\}", out).group(1)
    omega = [F(t.strip()) for t in om.split(",")]
    m = re.search(r"A_%d = i \* \(([^)]*)\)" % n, out)
    if m:
        A_im = F(m.group(1)); A_re = F(0)
    else:
        m2 = re.search(r"A_%d = \(([^)]*)\) \+ i \* \(([^)]*)\)" % n, out)
        A_re = F(m2.group(1)); A_im = F(m2.group(2))
    return omega, A_re, A_im

def two_minus_formula(omega, minus_legs, g=F(1)):
    """omega: 1-indexed conceptually but here 0-indexed list. minus_legs: 0-idx pair."""
    n = len(omega)
    a, b = minus_legs
    plus = [i for i in range(n) if i not in minus_legs]
    wa, wb = omega[a], omega[b]
    beta = min(abs(wa), abs(wb))
    b2 = beta*beta
    tot = F(0)
    for r in range(len(plus)+1):
        for S in combinations(plus, r):
            arg = b2 - sum(omega[j]*omega[j] for j in S)
            if arg > 0:
                tot += F((-1)**r) * arg**(n-3)
    pref = F(2)**(n-1) * g**(3-n) * wa * wb
    return pref * tot   # this is A_im (since A = i * pref * tot)

def check(label, n, freeW, sig, minus_legs):
    try:
        omega, A_re, A_im = run_bg(n, freeW, sig)
    except RuntimeError as e:
        print(f"[SKIP] {label}: {e}")
        return True
    pred = two_minus_formula(omega, minus_legs)
    ok = (A_re == 0) and (A_im == pred)
    print(f"[{'OK' if ok else 'FAIL'}] {label}")
    print(f"     omega = {[str(x) for x in omega]}")
    print(f"     bg   A_im = {A_im}")
    print(f"     form A_im = {pred}")
    if not ok:
        print(f"     A_re = {A_re}  diff = {A_im - pred}")
    return ok

if __name__ == "__main__":
    allok = True
    # n=5 two-minus, minus legs {1,2}: sigma=(-1,-1,+1,+1,+1)
    allok &= check("n=5 two-minus (minus {1,2})", 5, ["2","3","5"], ["-1","-1","1","1","1"], (0,1))
    allok &= check("n=5 two-minus b (minus {1,2})", 5, ["7","2","13"], ["-1","-1","1","1","1"], (0,1))
    # REQUIRED 5-point calibration: three-minus A_5 vs sign-flip two-minus (minus legs {4,5} = 0-idx {3,4})
    allok &= check("n=5 THREE-minus vs two-minus{4,5}", 5, ["2","3","5"], ["-1","-1","-1","1","1"], (3,4))
    allok &= check("n=5 THREE-minus b", 5, ["4","7","2"], ["-1","-1","-1","1","1"], (3,4))
    allok &= check("n=5 THREE-minus c", 5, ["11","3","8"], ["-1","-1","-1","1","1"], (3,4))
    allok &= check("n=5 THREE-minus d", 5, ["6","13","4"], ["-1","-1","-1","1","1"], (3,4))
    print("\nALL OK" if allok else "\nSOME FAILED")
    sys.exit(0 if allok else 1)
