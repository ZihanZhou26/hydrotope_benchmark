#!/usr/bin/env python3
"""PI round-5 DECISIVE: is s1_015 (a_i+b_j denom excluded) an ARTIFACT of lines
crossing FACTORIZATION surfaces (true-piece boundaries)?

s1_015 and my round5_denom both tested denominator candidates on affine lines
that stayed in one 18-WALL chamber but did NOT hold the 35 factorization-surface
signs h_S constant.  round5_piecewise shows those lines DO cross h_S=0 surfaces.
If h_S=0 surfaces are true-piece boundaries, H changes rational form across them,
so NO fixed denominator could clear H on such a line -- the negatives would be
artifacts, and a low-degree denominator (even a_i+b_j) could be revived.

Here we hold ALL 53 signs constant (single TRUE piece) and re-test whether
H*Q is a polynomial of degree deg Q + 2, for the a_i+b_j family and controls.

  clears on true piece but not on 18-wall line  => h_S are piece boundaries;
                                                   prior negatives are artifacts.
  fails even on a true piece                     => genuine exclusion stands.

Exact: fresh bg_r5 (GMP), mod P=2^61-1.
"""
import subprocess, re, random, sys
from itertools import combinations
from fractions import Fraction as F

BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code/bg_r5"
SIG = [-1, -1, -1, 1, 1, 1]
P = (1 << 61) - 1


def bg_amp(om, g=F(1)):
    K = [SIG[i] * om[i] * om[i] / g for i in range(6)]
    p = subprocess.run([BG, "--amp", "-K", ",".join(str(x) for x in K),
                        "-W", ",".join(str(x) for x in om), "-g", str(g)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if p.returncode != 0:
        return None
    m = re.search(r"A_6 = i \* \(([^)]*)\)", p.stdout)
    if m:
        return F(m.group(1))
    m2 = re.search(r"A_6 = \(([^)]*)\) \+ i \* \(([^)]*)\)", p.stdout)
    if m2 and F(m2.group(1)) == 0:
        return F(m2.group(2))
    return None


def solve_onshell(free):
    fr = [F(x) for x in free]; s = sum(fr)
    if s == 0:
        return None
    ss = sum(SIG[i + 1] * fr[i] ** 2 for i in range(4))
    wn = -(SIG[0] * s * s + ss) / (2 * SIG[0] * s)
    return [-(s + wn), fr[0], fr[1], fr[2], fr[3], wn]


def generic(om):
    sq = sorted(w * w for w in om)
    return all(sq[i] != sq[i + 1] for i in range(5))


def full_sign(om):
    a = [om[i] ** 2 for i in range(3)]; b = [om[3 + j] ** 2 for j in range(3)]
    T = sum(a); sg = []
    for i in range(3):
        for j in range(3):
            v = a[i] - b[j]; sg.append(1 if v > 0 else -1 if v < 0 else 0)
    for i in range(3):
        for j in range(3):
            v = a[i] + b[j] - T; sg.append(1 if v > 0 else -1 if v < 0 else 0)
    for r in (2, 3):
        for S in combinations(range(6), r):
            wS = sum(om[i] for i in S)
            kS = sum(SIG[i] * om[i] ** 2 for i in S)
            h = wS * wS - (kS if kS >= 0 else -kS)
            sg.append(1 if h > 0 else -1 if h < 0 else 0)
    return tuple(sg)


def to_mod(fr):
    return (fr.numerator % P) * pow(fr.denominator % P, P - 2, P) % P


def lagrange_check(samples, dmax, nhold=8):
    seen = {}; pts = []
    for t, y in samples:
        if t not in seen:
            seen[t] = y; pts.append((t, y))
    if len(pts) < dmax + 1 + nhold:
        return None
    nodes = pts[:dmax + 1]; hold = pts[dmax + 1:]
    xs = [t for t, _ in nodes]; ys = [y for _, y in nodes]
    w = []
    for i in range(len(xs)):
        d = 1
        for j in range(len(xs)):
            if j != i:
                d = d * ((xs[i] - xs[j]) % P) % P
        w.append(pow(d, P - 2, P))
    for th, yh in hold:
        num = 0; den = 0
        for i in range(len(xs)):
            diff = (th - xs[i]) % P
            if diff == 0:
                num = ys[i]; den = 1; break
            c = w[i] * pow(diff, P - 2, P) % P
            num = (num + c * ys[i]) % P
            den = (den + c) % P
        if num * pow(den, P - 2, P) % P != yh:
            return False
    return True


def cands(om):
    w = om
    a = [w[i] ** 2 for i in range(3)]; b = [w[3 + j] ** 2 for j in range(3)]
    T = sum(a)
    p = w[0]*w[1] + w[0]*w[2] + w[1]*w[2]
    apb = F(1)
    for i in range(3):
        for j in range(3):
            apb *= (a[i] + b[j])
    aa = (a[0]+a[1])*(a[0]+a[2])*(a[1]+a[2])
    bb = (b[0]+b[1])*(b[0]+b[2])*(b[1]+b[2])
    Rm2 = (w[0]*w[1]*w[2])**2; Tt2 = (w[3]*w[4]*w[5])**2
    return {
        "p         (d4)":   (p,          2),
        "apb_full  (d20)":  (apb,        18),   # student's family, full product
        "aa_bb_T2  (d18)":  (aa*bb*T*T,  16),
        "Rm2Tt2p2  (d18)":  (Rm2*Tt2*p*p, 16),
    }


def single_piece_run(rng, minpts):
    for _ in range(8000):
        f0 = [F(rng.randint(-8, 8)) + F(rng.randint(-5, 5), 7) for _ in range(4)]
        v = [F(rng.randint(-3, 3)) for _ in range(4)]
        if all(x == 0 for x in v):
            continue
        seq = []
        for k in range(-260, 261):
            t = F(k, 500)
            f = [f0[i] + t * v[i] for i in range(4)]
            if any(x == 0 for x in f) or sum(f) == 0:
                continue
            om = solve_onshell(f)
            if om is None or any(x == 0 for x in om) or not generic(om):
                continue
            seq.append((t, om, sum(f), full_sign(om)))
        if len(seq) < minpts:
            continue
        best = []; i = 0
        while i < len(seq):
            j = i; sg = seq[i][3]
            if 0 in sg:
                i += 1; continue
            while j < len(seq) and seq[j][3] == sg:
                j += 1
            if j - i > len(best):
                best = seq[i:j]
            i = j
        if len(best) >= minpts:
            return best
    return None


def main():
    rng = random.Random(2024)
    MINPTS = 55   # enough for d=20 -> Y deg<=40 -> need 41+8
    results = {}
    nruns = 0
    for run_id in range(6):
        best = single_piece_run(rng, MINPTS)
        if best is None:
            print(f"run {run_id}: no single-piece run >= {MINPTS} pts"); continue
        data = []
        for (t, om, U, sg) in best:
            A = bg_amp(om)
            if A is None:
                continue
            prod = F(1)
            for wv in om:
                prod *= wv
            data.append((t, om, U, A / prod))
        c0 = cands(data[0][1])
        line = []
        for name, (_v, dQ) in c0.items():
            d = dQ + 2
            samples = [(to_mod(t), to_mod(H * cands(om)[name][0] * (U ** d)))
                       for (t, om, U, H) in data]
            r = lagrange_check(samples, 2 * d, nhold=8)
            results.setdefault(name, []).append(r)
            line.append(f"{name.split()[0]}={'P' if r else ('-' if r is None else 'F')}")
        nruns += 1
        print(f"run {run_id}: TRUE-piece pts={len(data)}  " + "  ".join(line))
        sys.stdout.flush()
    print("=" * 72)
    print(f"true single-piece runs: {nruns}")
    for name, res in results.items():
        np_ = sum(1 for r in res if r is True); nf = sum(1 for r in res if r is False)
        print(f"  {name:16s}: pass={np_} fail={nf}  => "
              + ("CLEARS H on true piece" if (np_ >= 2 and nf == 0) else "does NOT clear H"))


if __name__ == "__main__":
    main()
