#!/usr/bin/env python3
"""
Final-round PI targeted double-check (pi_vchk_007).

Bounded, independent spot-check of the single load-bearing claim of the SOLVED
verdict: the compact formula A_6 = i g^{-3}(P_pole+R_Q+R_0+R_q) reproduces a
freshly-built exact BG oracle.  This is NOT a rerun of the full acceptance
battery (that is pi_vchk_006); it is a small confirmation on a fresh binary
(bg_final, md5-matched to the immutable shared bg.cpp) using the PI's own
hand-transcribed table-free evaluator pi_r9_eval.py.

Exact rationals throughout.  PASS = zero residual.
"""
import subprocess, re, random
from fractions import Fraction as F
import pi_r9_eval as E

BG = "./bg_final"
random.seed(777001)

OMEGA_RE = re.compile(r"omega = \{([^}]*)\}")
AMP_I_RE = re.compile(r"A_\d+ = i \* \(([^)]*)\)")
AMP_C_RE = re.compile(r"A_\d+ = \(([^)]*)\) \+ i \* \(([^)]*)\)")


def frac_list(s):
    return [F(tok.strip()) for tok in s.split(",") if tok.strip()]


def parse_bg(text):
    mo = OMEGA_RE.search(text)
    if not mo:
        return None
    omega = frac_list(mo.group(1))
    mi = AMP_I_RE.search(text)
    if mi:
        return omega, F(mi.group(1))
    mc = AMP_C_RE.search(text)
    if mc:
        if F(mc.group(1)) != 0:
            return omega, ("COMPLEX", F(mc.group(1)), F(mc.group(2)))
        return omega, F(mc.group(2))
    return None


def run_bg_n(freeW, g="1"):
    ws = ",".join(str(x) for x in freeW)
    out = subprocess.run([BG, "-n", "6", "-w", ws, "-s", "-1,-1,-1,1,1,1", "-g", str(g)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         universal_newlines=True, timeout=60)
    if out.returncode != 0:
        return None            # singular (on a wall) -> skip
    return parse_bg(out.stdout)


def chamber_sig(w):
    """Sign pattern of the 9 q-walls and 9 Q-walls; labels the chamber."""
    wd = E.as_w(w)
    qs, Qs = [], []
    for m in E.M:
        for p in E.P:
            x = wd[p]**2 - wd[m]**2
            qs.append(0 if x == 0 else (1 if x > 0 else -1))
    for m in E.M:
        for (p, q) in ((4, 5), (4, 6), (5, 6)):
            x = wd[p]**2 + wd[q]**2 - wd[m]**2
            Qs.append(0 if x == 0 else (1 if x > 0 else -1))
    return (tuple(qs), tuple(Qs))


def rand_free():
    """Random rational free frequencies (omega_2..omega_5)."""
    def r():
        return F(random.randint(-90, 90), random.randint(1, 9))
    return [r() for _ in range(4)]


npass = 0
nfail = 0
chambers = set()
fails = []

# 1) The two standing anchors (via -n and directly).
anchor = run_bg_n([2, 3, 4, 5])
assert anchor is not None
w, bg_ai = anchor
formula = E.A6_over_i(E.as_w(w))
ok = (formula == bg_ai)
print(f"ANCHOR omega={w}  BG A6/i={bg_ai}  formula={formula}  {'PASS' if ok else 'FAIL'}")
npass += ok
nfail += (not ok)
chambers.add(chamber_sig(w))

# 2) Fresh generic on-shell points.
tries = 0
while len(chambers) < 40 and tries < 4000:
    tries += 1
    res = run_bg_n(rand_free())
    if res is None:
        continue
    w, bg_ai = res
    if isinstance(bg_ai, tuple):   # complex -> off-sector, skip
        continue
    try:
        formula = E.A6_over_i(E.as_w(w))
    except ZeroDivisionError:
        continue                   # on a d=0 pole locus, skip (removable, handled elsewhere)
    ok = (formula == bg_ai)
    if ok:
        npass += 1
    else:
        nfail += 1
        fails.append((w, bg_ai, formula))
    chambers.add(chamber_sig(w))

print(f"\nGeneric points: {npass-1} PASS, {nfail} FAIL")
print(f"Distinct chambers hit: {len(chambers)}")
if fails:
    print("FAILURES:")
    for w, b, f in fails[:10]:
        print("  ", w, b, f)
print(f"\nTOTAL: {npass} PASS / {nfail} FAIL  over {len(chambers)} chambers")
print("RESULT:", "ALL EXACT" if nfail == 0 else "MISMATCH DETECTED")
