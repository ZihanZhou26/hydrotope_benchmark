#!/usr/bin/env python3
"""PI round-7 INDEPENDENT verification of student s1_018/s1_019.

Claim under test (student round 6, post_011, derivations/round6_compact_two_chambers.md):
  With the chart eliminating legs 1,6, (u,v,r,s)=(w2,w3,w4,w5),
    m1=u+v, m2=uv, p1=r+s, p2=rs, Om=u+v+r+s,
    L=(u+r)(u+s)(v+r)(v+s),
    B_M=e2(u,v,r,s)+u^2+v^2, B_P=e2(u,v,r,s)+r^2+s^2,
  and F the transcribed 31-term weighted-degree-9 polynomial below, then
    H_A = -32 rs Om F(m1,p1,m2,p2)/(uv L B_M B_P)   [piece A: (-7,9,-8,-3,-4,13)]
    H_B = -32 uv Om F(p1,m1,p2,m2)/(rs L B_M B_P)   [piece B: (-13,4,3,8,7,-9)]
  with H = A_6/(i prod_l w_l), i.e.  A6_im = (prod_l w_l) * H.

Everything here is transcribed independently by the PI from the written derivation;
BG is a FRESH copy (bg_r7) built from the immutable root bg.cpp this round.
All arithmetic exact (fractions.Fraction).
"""
import subprocess, re, sys
from fractions import Fraction as F

BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code/bg_r7"
SIG = [-1, -1, -1, 1, 1, 1]


def bg_amp_from_free(free):
    """free = [w2,w3,w4,w5] (Fractions); returns (omega6tuple, A6_im) exact, or None."""
    w = ",".join(str(x) for x in free)
    p = subprocess.run([BG, "-n", "6", "-w", w, "-s", "-1,-1,-1,1,1,1", "-g", "1"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       universal_newlines=True)
    if p.returncode != 0:
        return None
    mom = re.search(r"omega = \{([^}]*)\}", p.stdout)
    om = tuple(F(t.strip()) for t in mom.group(1).split(",")) if mom else None
    m = re.search(r"A_6 = i \* \(([^)]*)\)", p.stdout)
    if m:
        return om, F(m.group(1))
    m2 = re.search(r"A_6 = \(([^)]*)\) \+ i \* \(([^)]*)\)", p.stdout)
    if m2 and F(m2.group(1)) == 0:
        return om, F(m2.group(2))
    return None


def e2(vals):
    s = F(0)
    for i in range(len(vals)):
        for j in range(i + 1, len(vals)):
            s += vals[i] * vals[j]
    return s


def Fpoly(m1, p1, m2, p2):
    """31-term weighted-deg-9 core, transcribed from round6_compact_two_chambers.md."""
    return (
        2*m1**4*p1**3*p2 - 4*m1**4*p1*p2**2
        + 3*m1**3*p1**4*m2 + 4*m1**3*p1**4*p2 - 7*m1**3*p1**2*m2*p2
        - 10*m1**3*p1**2*p2**2 + 4*m1**3*p2**3
        + 6*m1**2*p1**5*m2 + 2*m1**2*p1**5*p2 + 3*m1**2*p1**3*m2**2
        - 22*m1**2*p1**3*m2*p2 - 4*m1**2*p1**3*p2**2 - 7*m1**2*p1*m2**2*p2
        + 17*m1**2*p1*m2*p2**2
        + 3*m1*p1**6*m2 - 13*m1*p1**4*m2*p2 + 2*m1*p1**4*p2**2
        - m1*p1**2*m2**2*p2 + 15*m1*p1**2*m2*p2**2 - 6*m1*p1**2*p2**3
        + 2*m1*m2**2*p2**2 - 6*m1*m2*p2**3 + 4*m1*p2**4
        - 3*p1**5*m2**2 + 2*p1**5*m2*p2 - 3*p1**3*m2**3
        + 14*p1**3*m2**2*p2 - 9*p1**3*m2*p2**2
        + 7*p1*m2**3*p2 - 16*p1*m2**2*p2**2 + 9*p1*m2*p2**3
    )


def blocks(om):
    """om = full 6-tuple; free legs u,v,r,s = w2,w3,w4,w5."""
    u, v, r, s = om[1], om[2], om[3], om[4]
    m1, m2 = u + v, u * v
    p1, p2 = r + s, r * s
    Om = u + v + r + s
    L = (u + r) * (u + s) * (v + r) * (v + s)
    ee = e2([u, v, r, s])
    B_M = ee + u**2 + v**2
    B_P = ee + r**2 + s**2
    return dict(u=u, v=v, r=r, s=s, m1=m1, m2=m2, p1=p1, p2=p2,
                Om=Om, L=L, B_M=B_M, B_P=B_P)


def H_A(om):
    b = blocks(om)
    num = -32 * b["r"] * b["s"] * b["Om"] * Fpoly(b["m1"], b["p1"], b["m2"], b["p2"])
    den = b["u"] * b["v"] * b["L"] * b["B_M"] * b["B_P"]
    return num / den


def H_B(om):
    b = blocks(om)
    num = -32 * b["u"] * b["v"] * b["Om"] * Fpoly(b["p1"], b["m1"], b["p2"], b["m2"])
    den = b["r"] * b["s"] * b["L"] * b["B_M"] * b["B_P"]
    return num / den


def prod_all(om):
    p = F(1)
    for w in om:
        p *= w
    return p


def sign_vector(om):
    """53-sign vector: 18 momentum walls (a_i-b_j, a_i+b_j-T) + 35 factorization
    surfaces h_S. Used to confirm perturbed points stay in the SAME true piece."""
    a = [om[i]**2 for i in range(3)]
    b = [om[3 + j]**2 for j in range(3)]
    T = sum(a)
    sv = []
    for i in range(3):
        for j in range(3):
            sv.append(1 if a[i] - b[j] > 0 else -1)
    for i in range(3):
        for j in range(3):
            sv.append(1 if a[i] + b[j] - T > 0 else -1)
    # factorization surfaces h_S = w_S^2 - |k_S| for all subsets |S|=2,3 (up to compl.)
    from itertools import combinations
    idx = range(6)
    seen = set()
    for sz in (2, 3):
        for S in combinations(idx, sz):
            key = frozenset(S)
            comp = frozenset(set(idx) - set(S))
            if comp in seen:
                continue
            seen.add(key)
            wS = sum(om[i] for i in S)
            kS = sum(SIG[i] * om[i]**2 for i in S)
            hS = wS**2 - abs(kS)
            sv.append(1 if hS > 0 else (-1 if hS < 0 else 0))
    return tuple(sv)


def run_piece(name, base_free, Hfun, npert=40):
    base = bg_amp_from_free([F(x) for x in base_free])
    if base is None:
        print(f"[{name}] BASE bg FAILED"); return (0, 0)
    om0, _ = base
    sv0 = sign_vector(om0)
    ok = bad = skipped = 0
    # deterministic rational perturbations, varied per index, no RNG
    for t in range(npert):
        d = [F(1 + t, 1000), F(-3 - 2*t, 1000), F(2 + t, 1000), F(-1 - 3*t, 1000)]
        free = [F(base_free[0]) + d[0], F(base_free[1]) + d[1],
                F(base_free[2]) + d[2], F(base_free[3]) + d[3]]
        res = bg_amp_from_free(free)
        if res is None:
            skipped += 1; continue
        om, a6im = res
        # only test points genuinely in the same true piece
        if sign_vector(om) != sv0:
            skipped += 1; continue
        pred = prod_all(om) * Hfun(om)
        if pred == a6im:
            ok += 1
        else:
            bad += 1
            if bad <= 3:
                print(f"[{name}] MISMATCH free={free} bg={a6im} pred={pred}")
    print(f"[{name}] exact-match {ok}/{ok+bad} in-piece  (skipped {skipped} off-piece/fail)")
    return ok, bad


if __name__ == "__main__":
    print("PI round-7 independent check of s1_018 (fresh bg_r7, exact Fraction)\n")
    # base A: (-7,9,-8,-3,-4,13) -> free (w2..w5) = (9,-8,-3,-4)
    a_ok, a_bad = run_piece("piece A / H_A", [9, -8, -3, -4], H_A)
    # base B: (-13,4,3,8,7,-9) -> free (w2..w5) = (4,3,8,7)
    b_ok, b_bad = run_piece("piece B / H_B", [4, 3, 8, 7], H_B)
    print(f"\nTOTAL exact matches: A={a_ok} B={b_ok}; mismatches: A={a_bad} B={b_bad}")
    sys.exit(0 if (a_bad == 0 and b_bad == 0 and a_ok > 0 and b_ok > 0) else 1)
