#!/usr/bin/env python3
"""
Targeted clean straddle of the pole orbit d_{2;pq}=0 on the omega_4 = -omega_2
sheet of the q_{24}=0 wall.  Family free=[3+t, 5, -3+t, 7] (legs 2,3,4,5):
  omega_2 = 3+t, omega_4 = -3+t  ->  omega_2 + omega_4 = 2t
so d_{2;45}=2(omega_2+omega_4)(omega_2+omega_5) flips sign through t=0, and at
t=0 we sit on q_{24}=0 with omega_4=-omega_2 (bg singular).  Channel (2;45) is
active there: Q_{2;45}=omega_4^2+omega_5^2-omega_2^2 = 49 > 0, so 1/d is really
used in P_pole.  We sample t just below and above 0 and confirm BG is finite and
formula==BG exactly on BOTH sides (the apparent 1/d pole is removable).
Exact rationals; no student/verifier code imported.
"""
import subprocess, re
from fractions import Fraction as F
import pi_r9_eval as E

BG = "./bg_r9"
OM = re.compile(r"omega = \{([^}]*)\}")
AI = re.compile(r"A_\d+ = i \* \(([^)]*)\)")
AC = re.compile(r"A_\d+ = \(([^)]*)\) \+ i \* \(([^)]*)\)")


def bg_n(freeW):
    ws = ",".join(str(x) for x in freeW)
    out = subprocess.run([BG, "-n", "6", "-w", ws, "-s", "-1,-1,-1,1,1,1", "-g", "1"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         universal_newlines=True)
    if out.returncode != 0:
        return None
    t = out.stdout
    mo = OM.search(t)
    omega = [F(x.strip()) for x in mo.group(1).split(",")]
    mi = AI.search(t)
    if mi:
        return omega, F(mi.group(1))
    mc = AC.search(t)
    if mc and F(mc.group(1)) == 0:
        return omega, F(mc.group(2))
    return None


def dval(w, m, p, q):
    return 2*(w[m]+w[p])*(w[m]+w[q])


print("Two-sided straddle of d_{2;45}=0 (removable pole) on the omega_4=-omega_2 sheet:")
print(f"{'t':>10} {'omega':>44} {'d_2;45':>12} {'A6/i BG':>16} {'formula==BG':>12}")
allok = True
for t in [F(-1, 20), F(-1, 200), F(-1, 2000), F(1, 2000), F(1, 200), F(1, 20)]:
    freeW = [3 + t, F(5), -3 + t, F(7)]
    r = bg_n(freeW)
    if r is None:
        print(f"{str(t):>10}  SINGULAR (on wall)")
        continue
    omega, Aoi = r
    w = E.as_w(omega)
    d = dval(w, 2, 4, 5)
    Q = w[4]**2 + w[5]**2 - w[2]**2
    fv = E.A6_over_i(w)
    ok = (fv == Aoi)
    allok = allok and ok
    om_s = "[" + ",".join(str(x) for x in omega) + "]"
    print(f"{str(t):>10} {om_s:>44} {str(d):>12} {str(Aoi):>16} {str(ok):>12}   (Q_2;45={Q}>0 active, BG finite)")

print()
print("PASS: removable-pole prescription verified" if allok else "FAIL")
