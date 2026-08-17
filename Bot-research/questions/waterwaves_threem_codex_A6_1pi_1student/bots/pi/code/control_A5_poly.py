#!/usr/bin/env python3
"""CONTROL for the A_6 non-polynomiality finding.

The known two-minus A_5 formula is a genuine (piecewise) POLYNOMIAL: once the
beta=min chamber and plus-subset walls are fixed, A_5/i is a degree-6 polynomial
in the omega_i.  Run the SAME polynomiality machinery used for A_6 on A_5.  It
MUST report PASS (polynomial detected).  A PASS here validates that the A_6 FAIL
(aug rank 286 > full poly dim 285) is a genuine non-polynomiality, not a bug.
"""
import subprocess, re, random
from fractions import Fraction as F
from itertools import combinations_with_replacement

BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code/bg"
SIG5 = [-1, -1, 1, 1, 1]   # two-minus at n=5: minus legs 1,2 ; plus legs 3,4,5
P = (1 << 61) - 1


def bg_amp5(free):  # free = (w2,w3,w4)
    p = subprocess.run([BG, "-n", "5", "-w", ",".join(str(x) for x in free),
                        "-s", "-1,-1,1,1,1", "-g", "1"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if p.returncode != 0:
        return None, None
    m = re.search(r"omega = \{([^}]*)\}", p.stdout)
    om = [F(t.strip()) for t in m.group(1).split(",")]
    mm = re.search(r"A_5 = i \* \(([^)]*)\)", p.stdout)
    if mm:
        return om, F(mm.group(1))
    m2 = re.search(r"A_5 = \(([^)]*)\) \+ i \* \(([^)]*)\)", p.stdout)
    return (om, F(m2.group(2))) if m2 else (om, None)


def to_mod(fr):
    return (fr.numerator % P) * pow(fr.denominator % P, P - 2, P) % P


VARS = 4   # eliminate omega_1 via sum omega = 0 -> fit in omega_2..omega_5
DEG = 6
MONS = [tuple(c.count(v) for v in range(VARS))
        for c in combinations_with_replacement(range(VARS), DEG)]


def feats(om):
    vv = [to_mod(x) for x in om[1:]]
    pw = [[1] * (DEG + 1) for _ in range(VARS)]
    for v in range(VARS):
        for e in range(1, DEG + 1):
            pw[v][e] = pw[v][e - 1] * vv[v] % P
    out = []
    for mon in MONS:
        m = 1
        for v in range(VARS):
            if mon[v]:
                m = m * pw[v][mon[v]] % P
        out.append(m)
    return out


def wall_sig5(om):
    # momentum subset sums g k_S = sum sigma_i omega_i^2 ; sign vector over all subsets
    ksq = [SIG5[i] * om[i] ** 2 for i in range(5)]
    sig = []
    for r in range(1, 5):
        from itertools import combinations
        for S in combinations(range(5), r):
            v = sum(ksq[i] for i in S)
            sig.append(1 if v > 0 else -1 if v < 0 else 0)
    return tuple(sig)


def sort_legs5(om):
    m = sorted(om[:2], key=lambda w: (w * w, w))
    p = sorted(om[2:], key=lambda w: (w * w, w))
    return m + p


def rref_mod(rows, ncol):
    R = [r[:] for r in rows]; m = len(R); rank = 0
    for col in range(ncol):
        piv = None
        for r in range(rank, m):
            if R[r][col] % P:
                piv = r; break
        if piv is None:
            continue
        R[rank], R[piv] = R[piv], R[rank]
        inv = pow(R[rank][col], P - 2, P)
        R[rank] = [(x * inv) % P for x in R[rank]]
        for r in range(m):
            if r != rank and R[r][col] % P:
                f = R[r][col]
                R[r] = [(R[r][c] - f * R[rank][c]) % P for c in range(len(R[r]))]
        rank += 1
        if rank == m:
            break
    return R, rank


def main():
    print(f"A_5 two-minus control: degree-{DEG} monomials in {VARS} vars = {len(MONS)}")
    rng = random.Random(11)
    buckets = {}
    for _ in range(40000):
        free = [F(rng.randint(-14, 14), rng.randint(1, 4)) for _ in range(3)]
        if any(x == 0 for x in free):
            continue
        om, A = bg_amp5(free)
        if om is None or A is None or any(x == 0 for x in om):
            continue
        om2 = sort_legs5(om)
        a = [om2[i] ** 2 for i in range(2)]; b = [om2[2 + j] ** 2 for j in range(3)]
        if a[0] == a[1] or len(set(b)) < 3:
            continue
        sig = wall_sig5(om2)
        if 0 in sig:
            continue
        buckets.setdefault(sig, []).append((om2, A))
        if len(buckets[sig]) >= 90 and _ > 2000:
            break
    sig_best = max(buckets, key=lambda s: len(buckets[s]))
    pts = buckets[sig_best]
    print(f"refined regions={len(buckets)}, biggest={len(pts)} pts")
    nfit = min(len(pts) - 15, 80)
    fit = pts[:nfit]; hold = pts[nfit:nfit + 15]
    A = [feats(om) for (om, _) in fit]
    y = [to_mod(v) for (_, v) in fit]
    _, base = rref_mod(A, len(MONS))
    M, aug = rref_mod([A[i] + [y[i]] for i in range(len(A))], len(MONS) + 1)
    print(f"fit pts={len(fit)}  rank(F)={base}  rank[F|y]={aug}")
    consistent = base == aug
    xok = None
    if consistent and hold:
        coeff = [0] * len(MONS)
        for row in M:
            pc = next((c for c in range(len(MONS)) if row[c] % P), None)
            if pc is not None:
                coeff[pc] = row[len(MONS)] % P
        xok = True
        for (om, v) in hold:
            f = feats(om); pred = 0
            for k in range(len(MONS)):
                if coeff[k]:
                    pred = (pred + coeff[k] * f[k]) % P
            if pred != to_mod(v) % P:
                xok = False; break
        print(f"cross-validation on {len(hold)} pts: {'PASS' if xok else 'FAIL'}")
    ok = consistent and xok
    print("=" * 55)
    print(f"CONTROL RESULT: {'PASS (A_5 is polynomial -> machinery correct)' if ok else 'FAIL (unexpected!)'}")


if __name__ == "__main__":
    main()
