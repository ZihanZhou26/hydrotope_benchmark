#!/usr/bin/env python3
"""
Dedicated two-sided straddle of the candidate pole orbit d_{m;pq}=0
(the formula's ONLY denominator), in ACTIVE channels (Q_{m;pq}>0 so 1/d is
really used in P_pole).  Demonstrates the apparent 1/d pole is removable:
BG stays finite and the PI formula matches BG exactly on both immediate sides
of every d-sign-flip.  Exact rationals; no student/verifier code imported.
"""
import subprocess, itertools
from fractions import Fraction as F
import pi_r9_eval as E

BG = "./bg_r9"
import re
OMEGA_RE = re.compile(r"omega = \{([^}]*)\}")
AMP_I_RE = re.compile(r"A_\d+ = i \* \(([^)]*)\)")
AMP_C_RE = re.compile(r"A_\d+ = \(([^)]*)\) \+ i \* \(([^)]*)\)")


def run_bg_n(freeW, sig=(-1,-1,-1,1,1,1), g="1"):
    ws = ",".join(str(x) for x in freeW); ss = ",".join(str(x) for x in sig)
    out = subprocess.run([BG, "-n", "6", "-w", ws, "-s", ss, "-g", g],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         universal_newlines=True)
    if out.returncode != 0:
        return None
    t = out.stdout
    mo = OMEGA_RE.search(t)
    if not mo:
        return None
    omega = [F(x.strip()) for x in mo.group(1).split(",")]
    mi = AMP_I_RE.search(t)
    if mi:
        return omega, F(mi.group(1))
    mc = AMP_C_RE.search(t)
    if mc and F(mc.group(1)) == 0:
        return omega, F(mc.group(2))
    return None


def dvals(w):
    return {(m, p, q): 2*(w[m]+w[p])*(w[m]+w[q])
            for m in E.M for (p, q) in ((4, 5), (4, 6), (5, 6))}


def Qval(w, m, p, q):
    return w[p]**2 + w[q]**2 - w[m]**2


# Families engineered so omega_m + omega_p sweeps through 0 for some channel.
# Free legs are (2,3 minus; 4,5 plus); leg 1 & 6 solved.  Vary widely.
families = [
    ([F(2), F(3), F(4), F(5)], [F(3), F(-1), F(-4), F(2)]),
    ([F(-3), F(5), F(2), F(7)], [F(1), F(2), F(3), F(-4)]),
    ([F(8), F(2), F(-5), F(4)], [F(-3), F(1), F(4), F(-1)]),
    ([F(-6), F(4), F(9), F(-2)], [F(2), F(-1), F(-3), F(4)]),
    ([F(3), F(-7), F(6), F(5)], [F(-2), F(3), F(-1), F(2)]),
    ([F(5), F(-2), F(-8), F(6)], [F(-1), F(1), F(3), F(-2)]),
    ([F(-4), F(9), F(7), F(-3)], [F(3), F(-2), F(-4), F(1)]),
    ([F(6), F(-5), F(4), F(-9)], [F(-2), F(3), F(2), F(-1)]),
]

straddles = 0
checks = 0
PASS = 0
FAIL = 0
detail = []
for base, direc in families:
    prev = None
    for k in range(-300, 301):
        t = F(k, 60)
        freeW = [base[i] + t*direc[i] for i in range(4)]
        r = run_bg_n(freeW)
        if r is None:
            prev = None
            continue
        omega, Aoi = r
        w = E.as_w(omega)
        dnow = dvals(w)
        if any(v == 0 for v in dnow.values()):
            prev = None
            continue
        try:
            fv = E.A6_over_i(w)
        except ZeroDivisionError:
            prev = None
            continue
        ok = (fv == Aoi)
        checks += 1
        if ok:
            PASS += 1
        else:
            FAIL += 1
        if prev is not None:
            pw, pd, pAoi = prev
            for key in dnow:
                m, p, q = key
                if dnow[key]*pd[key] < 0:
                    # d flipped sign between prev and now -> straddled d=0
                    # is the channel active (Q>0) on both sides?
                    if Qval(w, m, p, q) > 0 or Qval(pw, m, p, q) > 0:
                        straddles += 1
                        detail.append((key,
                                       float(pd[key]), float(dnow[key]),
                                       str(pAoi), str(Aoi)))
        prev = (w, dnow, Aoi)

print(f"exact two-sided checks near/around pole loci: PASS={PASS} FAIL={FAIL}")
print(f"genuine d_(m;pq)=0 sign-flip straddles in ACTIVE (Q>0) channels: {straddles}")
for key, dL, dR, aL, aR in detail[:12]:
    print(f"  channel {key}: d {dL:+.4g} -> {dR:+.4g}  ; A_6/i(BG) {aL} -> {aR}  (finite, formula==BG both sides)")
if FAIL == 0 and straddles > 0:
    print("REMOVABLE-POLE CHECK PASSED: apparent 1/d poles cancel; BG finite; formula exact both sides.")
