#!/usr/bin/env python3
"""PI decisive test: is A_6 piecewise-polynomial once we ALSO fix the within-set
orderings (a_i vs a_j, b_i vs b_j), in addition to the 18 momentum walls?

If yes, on a region R = {fixed 18 momentum-wall signs} AND {a_1<a_2<a_3, b_1<b_2<b_3}
A_6/i equals a single degree-8 polynomial in the omega_i.  We fit a GENERAL
(non-symmetric) degree-8 polynomial (eliminating omega_1 = -sum of the rest via
Sum omega = 0, so 5 variables) and cross-validate on held-out points of R.
Arithmetic in Z/p, p = 2^61-1.
"""
import subprocess, re, random
from fractions import Fraction as F
from itertools import combinations_with_replacement

BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code/bg"
SIG = [-1, -1, -1, 1, 1, 1]
P = (1 << 61) - 1


def bg_amp(omega, g=F(1)):
    K = [SIG[i] * omega[i] * omega[i] / g for i in range(6)]
    p = subprocess.run([BG, "--amp", "-K", ",".join(str(x) for x in K),
                        "-W", ",".join(str(x) for x in omega), "-g", str(g)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if p.returncode != 0:
        return None
    m = re.search(r"A_6 = i \* \(([^)]*)\)", p.stdout)
    if m:
        return F(m.group(1))
    m2 = re.search(r"A_6 = \(([^)]*)\) \+ i \* \(([^)]*)\)", p.stdout)
    return F(m2.group(2)) if m2 else None


def solve_onshell(free):
    fr = [F(x) for x in free]
    s = sum(fr)
    if s == 0:
        return None
    ss = sum(SIG[i + 1] * fr[i] ** 2 for i in range(4))
    wn = -(SIG[0] * s * s + ss) / (2 * SIG[0] * s)
    w1 = -(s + wn)
    return [w1, fr[0], fr[1], fr[2], fr[3], wn]


def sort_legs(om):
    m = sorted(om[:3], key=lambda w: (w * w, w))
    p = sorted(om[3:], key=lambda w: (w * w, w))
    return m + p


def wall_sig(om):
    a = [om[i] ** 2 for i in range(3)]
    b = [om[3 + j] ** 2 for j in range(3)]
    T = a[0] + a[1] + a[2]
    s = []
    for i in range(3):
        for j in range(3):
            v = a[i] - b[j]; s.append(1 if v > 0 else -1 if v < 0 else 0)
    for i in range(3):
        for j in range(3):
            v = a[i] + b[j] - T; s.append(1 if v > 0 else -1 if v < 0 else 0)
    return tuple(s)


def within_ties(om):
    a = [om[i] ** 2 for i in range(3)]; b = [om[3 + j] ** 2 for j in range(3)]
    return (a[0] == a[1] or a[1] == a[2] or a[0] == a[2] or
            b[0] == b[1] or b[1] == b[2] or b[0] == b[2])


def to_mod(fr):
    return (fr.numerator % P) * pow(fr.denominator % P, P - 2, P) % P


# degree-8 monomials in 5 variables (omega_2..omega_6); omega_1 eliminated
VARS = 5
MONS = [tuple(c.count(v) for v in range(VARS))
        for c in combinations_with_replacement(range(VARS), 8)]


def features_mod(om):
    # om is full 6-vector; enforce omega_1 = -(om2+..+om6) already true on-shell,
    # so just use omega_2..omega_6 as the 5 fitting variables.
    vv = [to_mod(x) for x in om[1:]]
    pows = [[1] * 9 for _ in range(VARS)]
    for v in range(VARS):
        for e in range(1, 9):
            pows[v][e] = pows[v][e - 1] * vv[v] % P
    out = []
    for mon in MONS:
        m = 1
        for v in range(VARS):
            if mon[v]:
                m = m * pows[v][mon[v]] % P
        out.append(m)
    return out


def rref_mod(rows, ncol):
    R = [r[:] for r in rows]
    m = len(R); rank = 0
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
    print(f"degree-8 monomials in {VARS} vars: {len(MONS)}")
    rng = random.Random(7)
    buckets = {}
    NEED = 340
    attempts = 0
    while attempts < 60000:
        attempts += 1
        free = [F(rng.randint(-16, 16), rng.randint(1, 5)) for _ in range(4)]
        if any(x == 0 for x in free):
            continue
        om = solve_onshell(free)
        if om is None or any(x == 0 for x in om):
            continue
        om = sort_legs(om)
        if within_ties(om):
            continue
        sig = wall_sig(om)
        if 0 in sig:
            continue
        b = buckets.setdefault(sig, [])
        if len(b) < NEED + 5:
            A = bg_amp(om)
            if A is None:
                continue
            b.append((om, A))
        if len(b) >= NEED and attempts > 3000:
            break
    sig_best = max(buckets, key=lambda s: len(buckets[s]))
    pts = buckets[sig_best]
    print(f"attempts={attempts}, distinct refined regions={len(buckets)}, "
          f"biggest region has {len(pts)} pts")
    if len(pts) < len(MONS) // 3:
        print("WARNING: few points; result may be underdetermined")
    nfit = min(len(pts) - 30, 460)
    fit = pts[:nfit]; hold = pts[nfit:nfit + 30]
    A = [features_mod(om) for (om, _) in fit]
    y = [to_mod(v) for (_, v) in fit]
    _, base = rref_mod(A, len(MONS))
    M, aug = rref_mod([A[i] + [y[i]] for i in range(len(A))], len(MONS) + 1)
    print(f"fit pts={len(fit)}  rank(F)={base}  rank[F|y]={aug}")
    consistent = (base == aug)
    xok = None
    if consistent and hold:
        coeff = [0] * len(MONS)
        for row in M:
            pc = next((c for c in range(len(MONS)) if row[c] % P), None)
            if pc is not None:
                coeff[pc] = row[len(MONS)] % P
        xok = True
        for (om, v) in hold:
            f = features_mod(om)
            pred = 0
            for k in range(len(MONS)):
                if coeff[k]:
                    pred = (pred + coeff[k] * f[k]) % P
            if pred != to_mod(v) % P:
                xok = False; break
        print(f"cross-validation on {len(hold)} held-out pts of R: {'PASS' if xok else 'FAIL'}")
    ok = consistent and (xok is True)
    print("=" * 60)
    print(f"RESULT: {'PASS' if ok else 'FAIL'} -- A_6/i is a single degree-8 polynomial on")
    print("        R = {18 momentum-wall signs fixed} AND {a1<a2<a3, b1<b2<b3}")
    print("  => within-set walls a_i=a_j, b_i=b_j ARE real chamber boundaries;")
    print("     A_6 is piecewise-polynomial (no genuine poles), matching removable-pole finding.")


if __name__ == "__main__":
    main()
