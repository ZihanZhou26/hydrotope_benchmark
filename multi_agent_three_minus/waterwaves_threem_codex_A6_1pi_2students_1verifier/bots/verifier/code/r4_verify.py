#!/usr/bin/env python3
"""Round-4 independent verifier harness.

Everything here is reimplemented from the WRITTEN derivations (logic.yaml F9,
group_meeting_notes.md), never imported from a student evaluator. Amplitudes
come only from my own freshly built oracle bg_r4 (md5-matched shared bg.cpp),
in exact rational mode. All auxiliary arithmetic uses fractions.Fraction.
"""
import subprocess, itertools, re
from fractions import Fraction as F

BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_2students_1verifier/bots/verifier/code/bg_r4"
SIG = [-1, -1, -1, 1, 1, 1]          # minus legs 1,2,3 ; plus legs 4,5,6
M = [0, 1, 2]                        # 0-indexed minus legs
P = [3, 4, 5]                        # 0-indexed plus legs

def _fmt(x):
    x = F(x)
    return f"{x.numerator}/{x.denominator}" if x.denominator != 1 else str(x.numerator)

def amp_from_omega(omega):
    """Full 6-vector of exact frequencies -> A_6/i as a Fraction, via --amp.
    Requires omega on-shell (caller guarantees). k_i = sigma_i * omega_i^2."""
    omega = [F(w) for w in omega]
    K = [SIG[i]*omega[i]*omega[i] for i in range(6)]
    ks = ",".join(_fmt(k) for k in K)
    ws = ",".join(_fmt(w) for w in omega)
    out = subprocess.run([BG, "--amp", "-K", ks, "-W", ws, "-g", "1"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"bg failed rc={out.returncode}: {out.stderr}\n{out.stdout}")
    txt = out.stdout
    m = re.search(r"A_6 = i \* \(([-0-9/]+)\)", txt)
    if m:
        return F(m.group(1))
    m = re.search(r"A_6 = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)", txt)
    if m:
        re_part = F(m.group(1))
        if re_part != 0:
            raise RuntimeError(f"A_6 has nonzero real part {re_part}:\n{txt}")
        return F(m.group(2))
    raise RuntimeError(f"could not parse:\n{txt}")

def solve_onshell(w2, w3, w4, w5):
    """Solve omega_1, omega_6 from the two conservation laws, matching bg.cpp
    (free legs are 2,3,4,5 with signs -1,-1,1,1; leg1 minus, leg6 plus)."""
    free = [F(w2), F(w3), F(w4), F(w5)]
    sig_free = [-1, -1, 1, 1]         # signs of legs 2,3,4,5
    s0 = SIG[0]                        # sign of leg 1 = -1
    sumFree = sum(free)
    sumSig = sum(sig_free[i]*free[i]*free[i] for i in range(4))
    wn = -(s0*sumFree*sumFree + sumSig)/(2*s0*sumFree)   # omega_6
    w1 = -(sumFree + wn)
    return [w1, free[0], free[1], free[2], free[3], wn]

# ---------- table-free P_pole from written formula F9 ----------
def pos(x):
    x = F(x)
    return x if x > 0 else F(0)

def Hblock(b, c, d, omega):
    """H(b; c, d) = sum_{S subset {c,d}} (-1)^|S| (b - omega_S^2)_+ .
    c,d are 0-indexed leg labels; uses omega_c^2, omega_d^2."""
    wc2 = omega[c]*omega[c]
    wd2 = omega[d]*omega[d]
    return pos(b) - pos(b - wc2) - pos(b - wd2) + pos(b - wc2 - wd2)

def P_pole(omega):
    """-64 * sum_{T:Q_T>0} omega_m omega_pbar Q_T^2 / d_T
              * H(min(omega_m^2,Q_T); p,q) * H(min(omega_pbar^2,Q_T); m',m'').
    Channels T=(m;{p,q}), m in M, {p,q} subset P, pbar=omitted plus leg,
    {m',m''}=M\\{m}. Table-free."""
    omega = [F(w) for w in omega]
    total = F(0)
    for m in M:
        mp = [x for x in M if x != m]          # {m', m''}
        for pq in itertools.combinations(P, 2):
            p, q = pq
            pbar = [x for x in P if x not in pq][0]
            Q_T = omega[p]**2 + omega[q]**2 - omega[m]**2
            if Q_T <= 0:
                continue
            d_T = 2*(omega[m]+omega[p])*(omega[m]+omega[q])
            b1 = min(omega[m]**2, Q_T)
            b2 = min(omega[pbar]**2, Q_T)
            H1 = Hblock(b1, p, q, omega)
            H2 = Hblock(b2, mp[0], mp[1], omega)
            total += omega[m]*omega[pbar]*Q_T*Q_T/d_T * H1 * H2
    return -64*total

def R_spline(omega):
    return amp_from_omega(omega) - P_pole(omega)

if __name__ == "__main__":
    # ---- anchors ----
    a1 = solve_onshell(2,3,4,5)
    print("anchor1 omega:", [_fmt(x) for x in a1])
    A1 = amp_from_omega(a1)
    print("  A6/i =", _fmt(A1), " expect -9190656/7 =", _fmt(F(-9190656,7)))
    print("  P_pole =", _fmt(P_pole(a1)), " expect 42588288/7 =", _fmt(F(42588288,7)))
    print("  R_spline =", _fmt(R_spline(a1)), " expect -7396992")

    # ---- student-2 witness (s2_009 sec 3) ----
    w = [F(21,2), -8, 1, -7, -6, F(19,2)]
    # sanity: on-shell?
    print("\nwitness on-shell check: sum omega =", _fmt(sum(w)),
          " sum sigma omega^2 =", _fmt(sum(SIG[i]*w[i]*w[i] for i in range(6))))
    print("witness omega:", [_fmt(x) for x in w])
    print("  A6/i     =", _fmt(amp_from_omega(w)))
    print("  P_pole   =", _fmt(P_pole(w)))
    print("  R_spline =", _fmt(R_spline(w)), " student-2 claims -49008548")
