#!/usr/bin/env python3
"""PI round-5: identify the surviving denominator of H = A_6/(i prod omega).

Motivation (structural, from s1_013/pi_v_013): the ONLY BG inverse-propagator
factors are the SAME-SIGN ones -- same-sign pair h=2 w_i w_j and same-sign
triple h=2p -- plus mixed factors that DO vanish on factorization surfaces
(mixed-triple h) and hence are removable (pi_v_006) and cancel; the mixed-PAIR
apparent (w_i+w_j) factor CANCELS identically.  The cross-sum a_i+b_j is NOT a
BG propagator factor at all, which is exactly why student s1_015 found no
subproduct of {a_i+b_j} clears H.  So the surviving sign-definite (never-zero)
denominator of H must be a product of the same-sign propagators
{w_i w_j (same-sign pairs), p}, possibly with the mixed-triple quadratics.

Test: in ONE fixed 18-wall chamber, for a candidate denominator Q(omega) we ask
whether H*Q is a POLYNOMIAL of degree d = deg Q + 2 (H is degree-2 homogeneous).
Along an affine line f(t)=f0+t v in the 4 free freqs, with U=sum(f) and omega_1,
omega_6 rational with denominator U, a degree-d polynomial in omega equals
(poly of degree <= 2d in t)/U^d.  So Y(t)=H(t) Q(t) U(t)^d must be a univariate
polynomial of degree <= 2d.  We build Y EXACTLY (fresh bg_r5, GMP rational),
reduce mod P, Lagrange-interpolate the first 2d+1 samples, and check >=8 holdouts.

Controls: (a) Q=prod(a_i+b_j) must FAIL (reconfirms s1_015 independently);
          (b) each candidate is tested on several independent lines.
"""
import subprocess, re, random, sys
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


def wall_sig(om):
    a = [om[i] ** 2 for i in range(3)]; b = [om[3 + j] ** 2 for j in range(3)]
    T = sum(a); s = []
    for i in range(3):
        for j in range(3):
            v = a[i] - b[j]; s.append(1 if v > 0 else -1 if v < 0 else 0)
    for i in range(3):
        for j in range(3):
            v = a[i] + b[j] - T; s.append(1 if v > 0 else -1 if v < 0 else 0)
    return tuple(s)


def generic(om):
    sq = sorted(w * w for w in om)
    return all(sq[i] != sq[i + 1] for i in range(5))


def to_mod(fr):
    return (fr.numerator % P) * pow(fr.denominator % P, P - 2, P) % P


# ---- candidate denominators Q(om) -> (Fraction value, degree) --------------
def cand_factors(om, chamber_branch):
    w = om
    a = [w[i] ** 2 for i in range(3)]
    b = [w[3 + j] ** 2 for j in range(3)]
    T = sum(a)
    p = w[0]*w[1] + w[0]*w[2] + w[1]*w[2]                       # = e2 minus = e2 plus
    Rm = w[0]*w[1]*w[2]; Tt = w[3]*w[4]*w[5]
    Rm2 = Rm*Rm; Tt2 = Tt*Tt
    apb = F(1)
    for i in range(3):
        for j in range(3):
            apb *= (a[i] + b[j])
    # SAME-SET square sums |k_S| for same-sign subsets S (sign-definite sums of squares)
    aa = (a[0]+a[1])*(a[0]+a[2])*(a[1]+a[2])                    # minus pairs, deg 6
    bb = (b[0]+b[1])*(b[0]+b[2])*(b[1]+b[2])                    # plus pairs,  deg 6
    # mixed-triple h_lj on the chamber's fixed S_lj branch (degree 2 each)
    hprod = F(1)
    for l in range(3):
        mm = [k for k in range(3) if k != l]
        x, y = w[mm[0]], w[mm[1]]
        for j in range(3):
            z = w[3 + j]
            if chamber_branch[(l, j)] < 0:      # S_lj<0 -> 2(x+z)(y+z)
                hprod *= 2*(x+z)*(y+z)
            else:                                # S_lj>0 -> irreducible quadratic
                hprod *= 2*(x*x + y*y + x*y + z*(x+y))
    return {
        "T        (d4)":              (T,               2),
        "T^2      (d6)":              (T*T,             4),
        "aa       (d8)":              (aa,              6),
        "aa_bb    (d14)":             (aa*bb,           12),
        "aa_bb_T  (d16)":             (aa*bb*T,         14),
        "aa_bb_T2 (d18)":             (aa*bb*T*T,       16),
        "prod_h_lj(d20)":             (hprod,           18),
        "CTRL apb (d20)":             (apb,             18),
    }


def branch_of(om):
    a = [om[i]**2 for i in range(3)]; b = [om[3+j]**2 for j in range(3)]
    T = sum(a); br = {}
    for l in range(3):
        for j in range(3):
            br[(l, j)] = 1 if a[l] + b[j] - T > 0 else -1
    return br


def lagrange_check(samples, dmax, nhold=8):
    """samples: list of (t_mod, y_mod). Fit poly of degree<=dmax on first dmax+1
    distinct nodes, verify on the rest.  Returns True iff all holdouts match."""
    # dedup by t
    seen = {}; pts = []
    for t, y in samples:
        if t not in seen:
            seen[t] = y; pts.append((t, y))
    if len(pts) < dmax + 1 + nhold:
        return None  # not enough points
    nodes = pts[:dmax + 1]
    hold = pts[dmax + 1:]
    xs = [t for t, _ in nodes]; ys = [y for _, y in nodes]
    # barycentric weights
    w = []
    for i in range(len(xs)):
        d = 1
        for j in range(len(xs)):
            if j != i:
                d = d * ((xs[i] - xs[j]) % P) % P
        w.append(pow(d, P - 2, P))
    ok = 0
    for th, yh in hold:
        num = 0; den = 0
        for i in range(len(xs)):
            diff = (th - xs[i]) % P
            if diff == 0:
                num = ys[i]; den = 1; break
            c = w[i] * pow(diff, P - 2, P) % P
            num = (num + c * ys[i]) % P
            den = (den + c) % P
        val = num * pow(den, P - 2, P) % P
        if val == yh:
            ok += 1
    return ok == len(hold)


def build_line(rng, target_sig, need):
    """return a list of exact-om points on one affine line within target_sig."""
    for _attempt in range(4000):
        f0 = [F(rng.randint(-14, 14), rng.randint(1, 3)) for _ in range(4)]
        v = [F(rng.randint(-3, 3)) for _ in range(4)]
        if all(x == 0 for x in v):
            continue
        pts = []
        seen_t = set()
        for k in range(-300, 301):
            t = F(k, 24)
            if t in seen_t:
                continue
            f = [f0[i] + t * v[i] for i in range(4)]
            if any(x == 0 for x in f) or sum(f) == 0:
                continue
            om = solve_onshell(f)
            if om is None or any(x == 0 for x in om):
                continue
            if not generic(om):
                continue
            if wall_sig(om) != target_sig:
                continue
            pts.append((t, om, sum(f)))
            seen_t.add(t)
            if len(pts) >= need:
                break
        if len(pts) >= need:
            return pts
    return None


def main():
    rng = random.Random(505)
    # find a generic interior chamber signature from a random point
    target = None
    while target is None:
        f = [F(rng.randint(-10, 10), rng.randint(1, 3)) for _ in range(4)]
        if any(x == 0 for x in f) or sum(f) == 0:
            continue
        om = solve_onshell(f)
        if om is None or any(x == 0 for x in om) or not generic(om):
            continue
        sg = wall_sig(om)
        if 0 in sg:
            continue
        target = sg
        branch = branch_of(om)
    print("target chamber sig:", target)
    print("mixed-triple branch (l,j)->sign(S_lj):", {f"{l}{j}": branch[(l, j)] for l in range(3) for j in range(3)})
    sys.stdout.flush()

    NEED = 60          # points per line (enough for d up to 18-20 => 2d+1+holdouts)
    NLINES = 6
    # candidate name -> per-line pass/fail
    results = {}
    lines_used = 0
    for li in range(NLINES):
        pts = build_line(rng, target, NEED)
        if pts is None:
            print(f"line {li}: could not fill {NEED} in-chamber points, skipping")
            continue
        lines_used += 1
        # compute H exactly at each point
        data = []  # (t, om, U, H)
        for (t, om, U) in pts:
            A = bg_amp(om)
            if A is None:
                continue
            prod = F(1)
            for wv in om:
                prod *= wv
            H = A / prod
            data.append((t, om, U, H))
        if not data:
            print(f"line {li}: no amplitudes"); continue
        # for each candidate, build Y(t)=H*Q*U^d and test
        cand0 = cand_factors(data[0][1], branch)
        for name, (_v, _dQ) in cand0.items():
            d = _dQ + 2   # deg(H*Q)
            samples = []
            for (t, om, U, H) in data:
                Qv, dQ = cand_factors(om, branch)[name]
                Y = H * Qv * (U ** d)
                samples.append((to_mod(t), to_mod(Y)))
            ok = lagrange_check(samples, 2 * d, nhold=8)
            results.setdefault(name, []).append(ok)
        print(f"line {li}: chamber-filled with {len(data)} exact points  "
              + "  ".join(f"{nm.split()[0]}={'P' if results[nm][-1] else ('-' if results[nm][-1] is None else 'F')}"
                          for nm in cand0))
        sys.stdout.flush()

    print("=" * 72)
    print(f"lines used: {lines_used}")
    for name, res in results.items():
        npass = sum(1 for r in res if r is True)
        nfail = sum(1 for r in res if r is False)
        nins = sum(1 for r in res if r is None)
        verdict = "POLYNOMIAL (clears H)" if (npass > 0 and nfail == 0 and npass >= 2) else \
                  "insufficient pts" if (npass == 0 and nfail == 0) else "NOT polynomial"
        print(f"  {name:18s}: pass={npass} fail={nfail} insuff={nins}  => {verdict}")


if __name__ == "__main__":
    main()
