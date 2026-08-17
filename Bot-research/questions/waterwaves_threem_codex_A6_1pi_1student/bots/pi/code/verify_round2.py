#!/usr/bin/env python3
"""PI independent verification, round 2.

Reproduces the load-bearing round-1 student claims with the PI's own code and a
fresh bg.cpp copy (bots/pi/code/bg).  No student code or data is imported.

  A. Wall structure (s1_002): derive momentum-subset walls k_S=0 from scratch,
     reduce to a normal form modulo total-momentum (Sum a = Sum b), confirm the
     nondegenerate set is exactly {a_i - b_j = 0} U {a_i + b_j - T = 0} (18 walls,
     two S3xS3 orbits) plus 6 external-degeneracy boundaries.  Numeric check that
     bg divides by zero on a wall point.
  B. Reality/conservation/homogeneity/symmetry (s1_005, F3, F4): >=25 generic
     on-shell three-minus points; A_6 = i*rational, both conservation laws,
     homogeneity degree 8, S3xS3 leg symmetry and minus<->plus swap.
  C. Chamber polynomiality (strengthens s1_003): inside one fixed chamber, fit
     A_6/i to a degree-8 S3xS3-symmetric polynomial in the signed omega_i and
     cross-validate on held-out chamber points (exact arithmetic in a prime
     field Z/p, p = 2^61-1).  Success => no genuine poles in that chamber; A_6 is
     piecewise-polynomial.
  D. H1 negative (s1_004): independent rank test that a plus-leg-only
     truncated-power family cannot reproduce A_6.
"""
import subprocess, re, random
from fractions import Fraction as F
from itertools import combinations, permutations

BG = "/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student/bots/pi/code/bg"
SIG = [-1, -1, -1, 1, 1, 1]  # positions 1-3 minus, 4-6 plus
P = (1 << 61) - 1            # Mersenne prime for the modular fit


# ---------- bg driver (exact rational) ----------

def bg_amp(omega, g=F(1)):
    K = [SIG[i] * omega[i] * omega[i] / g for i in range(6)]
    Ks = ",".join(str(x) for x in K)
    Ws = ",".join(str(x) for x in omega)
    p = subprocess.run([BG, "--amp", "-K", Ks, "-W", Ws, "-g", str(g)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if p.returncode != 0:
        return None
    out = p.stdout
    m = re.search(r"A_6 = i \* \(([^)]*)\)", out)
    if m:
        return F(0), F(m.group(1))
    m2 = re.search(r"A_6 = \(([^)]*)\) \+ i \* \(([^)]*)\)", out)
    if m2:
        return F(m2.group(1)), F(m2.group(2))
    return None


def solve_onshell(free, sig=SIG):
    fr = [F(x) for x in free]
    s = sum(fr)
    if s == 0:
        return None
    sum_sig = sum(sig[i + 1] * fr[i] * fr[i] for i in range(4))
    sig0 = F(sig[0])
    wn = -(sig0 * s * s + sum_sig) / (2 * sig0 * s)
    w1 = -(s + wn)
    return [w1, fr[0], fr[1], fr[2], fr[3], wn]


# ---------- A. wall derivation via reduced normal form ----------

def reduce_form(c):
    """c = coeff vector over (a1,a2,a3,b1,b2,b3). Eliminate b3 using the relation
    R = a1+a2+a3-b1-b2-b3 = 0 (so b3 = a1+a2+a3-b1-b2). Return sign-normalised
    tuple over (a1,a2,a3,b1,b2)."""
    c = list(c)
    t = c[5]                       # zero out b3 by adding t*R with R[5]=-1
    c = [c[k] + t * (1 if k < 3 else -1) for k in range(6)]
    v = tuple(c[:5])               # c[5] now 0
    # sign normalise: first nonzero positive
    for x in v:
        if x != 0:
            if x < 0:
                v = tuple(-y for y in v)
            break
    return v


def wall_form(I, J):
    """diff/subset wall for minus subset I, plus subset J: g k_S = -sum_I a + sum_J b."""
    c = [0] * 6
    for i in I:
        c[i] += -1
    for j in J:
        c[3 + j] += 1
    return reduce_form(c)


def ref_diff():
    return {reduce_form([( +1 if k == i else 0) for k in range(3)] +
                        [(-1 if k == j else 0) for k in range(3)]): ("diff", i, j)
            for i in range(3) for j in range(3)}


def ref_sum():
    # a_i + b_j - T,  T = a1+a2+a3
    out = {}
    for i in range(3):
        for j in range(3):
            c = [(-1) for _ in range(3)]
            c[i] += 1
            c += [0, 0, 0]
            c[3 + j] += 1
            out[reduce_form(c)] = ("sum", i, j)
    return out


def check_A():
    print("=" * 70)
    print("A. Wall structure (independent derivation)")
    diff, summ = ref_diff(), ref_sum()
    ref18 = {}
    ref18.update(diff); ref18.update(summ)
    # external degeneracy forms: a_i = T (-> a_j+a_k=0) and b_j = T (-> b_k+b_l=0)
    ext = set()
    for i in range(3):
        c = [(-1) for _ in range(3)]; c[i] += 1; c += [0, 0, 0]
        ext.add(reduce_form(c))                                   # a_i = T
    for j in range(3):
        c = [(-1) for _ in range(3)] + [0, 0, 0]; c[3 + j] += 1
        ext.add(reduce_form(c))                                   # b_j = T
    # enumerate every proper nonempty subset, collect distinct reduced wall forms
    forms = {}
    for r in range(1, 6):
        for S in combinations(range(6), r):
            I = [i for i in S if i < 3]
            J = [i - 3 for i in S if i >= 3]
            c = [0] * 6
            for i in I:
                c[i] += -1
            for j in J:
                c[3 + j] += 1
            f = reduce_form(c)
            if all(x == 0 for x in f):
                continue
            forms.setdefault(f, 0)
            forms[f] += 1
    nondeg = [f for f in forms if f in ref18]
    extfound = [f for f in forms if f in ext]
    unknown = [f for f in forms if f not in ref18 and f not in ext]
    got_diff = sum(1 for f in nondeg if diff.get(f, ("",))[0] == "diff")
    got_sum = sum(1 for f in nondeg if summ.get(f, ("",))[0] == "sum")
    print(f"    distinct reduced wall forms from all subsets: {len(forms)}")
    print(f"    matched nondegenerate (18 expected): {len(nondeg)}  "
          f"(diff={got_diff}, sum={got_sum})")
    print(f"    matched external-degeneracy boundaries: {len(extfound)} of {len(ext)}")
    print(f"    unrecognised forms: {len(unknown)}  {unknown if unknown else ''}")
    ok = (len(nondeg) == 18 and got_diff == 9 and got_sum == 9 and len(unknown) == 0)
    # numeric: on-shell wall point omega=(2,3,5,-2,-3,-5) (every {i,i+3} has k=0)
    wall_om = [F(2), F(3), F(5), F(-2), F(-3), F(-5)]
    c1 = sum(wall_om); c2 = sum(SIG[i] * wall_om[i] ** 2 for i in range(6))
    r = bg_amp(wall_om)
    print(f"    on-shell wall pt (2,3,5,-2,-3,-5): conservation sum={c1}, sigsum={c2}; "
          f"bg -> {'FAILS (|k_S|=0, expected)' if r is None else 'returned '+str(r)}")
    ok = ok and (c1 == 0 and c2 == 0 and r is None)
    print(f"  => {'PASS' if ok else 'FAIL'}")
    return ok


# ---------- B. reality/conservation/homogeneity/symmetry ----------

def rand_onshell(rng, lo=-9, hi=9):
    for _ in range(500):
        free = [F(rng.randint(lo, hi)) for _ in range(4)]
        if any(x == 0 for x in free):
            continue
        om = solve_onshell(free)
        if om is None or any(x == 0 for x in om):
            continue
        r = bg_amp(om)
        if r is not None:
            return om, r
    return None, None


def check_B(npts=28):
    print("=" * 70)
    print("B. Reality / conservation / homogeneity / symmetry")
    rng = random.Random(20260726)
    ok = True
    pts = []
    while len(pts) < npts:
        om, r = rand_onshell(rng)
        if om is None:
            continue
        pts.append((om, r))
    for om, (Are, Aim) in pts:
        if not (Are == 0 and sum(om) == 0 and sum(SIG[i] * om[i] ** 2 for i in range(6)) == 0):
            print(f"    FAIL reality/conservation at {om}")
            ok = False
    print(f"    reality (A_re=0) & both conservation laws on {len(pts)} pts: {'PASS' if ok else 'FAIL'}")
    om0, (_, Aim0) = pts[0]
    lam = F(3, 2)
    r1 = bg_amp([lam * x for x in om0])
    homok = (r1 is not None and r1[1] == lam ** 8 * Aim0)
    print(f"    homogeneity degree 8 (scale 3/2): {'PASS' if homok else 'FAIL'}")
    ok &= homok
    symok = True
    for om, (_, Aim) in pts[:12]:
        for pm in permutations(range(3)):
            for pp in permutations(range(3)):
                q = [om[pm[0]], om[pm[1]], om[pm[2]], om[3 + pp[0]], om[3 + pp[1]], om[3 + pp[2]]]
                rq = bg_amp(q)
                if rq is None or rq[1] != Aim or rq[0] != 0:
                    print(f"    FAIL S3xS3 at {om} {pm},{pp}: {rq}"); symok = False; break
            if not symok:
                break
        sw = [om[3], om[4], om[5], om[0], om[1], om[2]]
        rs = bg_amp(sw)
        if rs is None or rs[1] != Aim or rs[0] != 0:
            print(f"    FAIL swap at {om}: {rs}"); symok = False
        if not symok:
            break
    print(f"    S3xS3 leg symmetry + minus<->plus swap: {'PASS' if symok else 'FAIL'}")
    ok &= symok
    print(f"  => {'PASS' if ok else 'FAIL'}")
    return ok


# ---------- chamber signature ----------

def wall_signature(om):
    a = [om[i] ** 2 for i in range(3)]
    b = [om[3 + j] ** 2 for j in range(3)]
    T = a[0] + a[1] + a[2]
    sig = []
    for i in range(3):
        for j in range(3):
            v = a[i] - b[j]
            sig.append(1 if v > 0 else -1 if v < 0 else 0)
    for i in range(3):
        for j in range(3):
            v = a[i] + b[j] - T
            sig.append(1 if v > 0 else -1 if v < 0 else 0)
    return tuple(sig)


# ---------- symmetric degree-8 basis + modular fit ----------

def compositions(n, k):
    if k == 1:
        yield (n,); return
    for i in range(n + 1):
        for rest in compositions(n - i, k - 1):
            yield (i,) + rest


def sym_basis(deg=8):
    reps = set()
    for ax in range(deg + 1):
        ay = deg - ax
        for ex in compositions(ax, 3):
            for ey in compositions(ay, 3):
                reps.add(tuple(sorted(ex, reverse=True)) + tuple(sorted(ey, reverse=True)))
    return sorted(reps)


def to_mod(fr):
    return (fr.numerator % P) * pow(fr.denominator % P, P - 2, P) % P


def orbit_value_mod(exps, omv):
    """omv: tuple of 6 residues. Sum over S3xS3 images of monomial omv^exps mod P."""
    ex = exps[:3]; ey = exps[3:]
    tot = 0
    seen = set()
    for pm in permutations(range(3)):
        for pp in permutations(range(3)):
            e = (ex[pm[0]], ex[pm[1]], ex[pm[2]], ey[pp[0]], ey[pp[1]], ey[pp[2]])
            if e in seen:
                continue
            seen.add(e)
            m = 1
            for v in range(6):
                if e[v]:
                    m = m * pow(omv[v], e[v], P) % P
            tot = (tot + m) % P
    return tot


def rref_mod(rows, ncol):
    R = [r[:] for r in rows]
    m = len(R)
    rank = 0
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


def check_C():
    print("=" * 70)
    print("C. Chamber polynomiality: degree-8 symmetric fit + cross-validation (Z/p, p=2^61-1)")
    rng = random.Random(4242)
    buckets = {}
    tries = 0
    reps = sym_basis(8)
    need = len(reps) + 40
    while tries < 20000 and (not buckets or max(len(v) for v in buckets.values()) < need):
        tries += 1
        free = [F(rng.randint(-14, 14), rng.randint(1, 4)) for _ in range(4)]
        if any(x == 0 for x in free):
            continue
        om = solve_onshell(free)
        if om is None or any(x == 0 for x in om):
            continue
        sig = wall_signature(om)
        if 0 in sig:
            continue
        r = bg_amp(om)
        if r is None or r[0] != 0:
            continue
        buckets.setdefault(sig, []).append((om, r[1]))
    sig_best = max(buckets, key=lambda s: len(buckets[s]))
    pts = buckets[sig_best]
    print(f"    distinct chambers sampled: {len(buckets)};  most-populated has {len(pts)} pts")
    print(f"    degree-8 S3xS3 symmetric basis functions: {len(reps)}")
    nfit = min(len(pts) - 25, len(reps) + 15)
    fit = pts[:nfit]; hold = pts[nfit:nfit + 25]
    omv = [tuple(to_mod(x) for x in om) for (om, _) in fit]
    A = [[orbit_value_mod(e, omv[i]) for e in reps] for i in range(len(fit))]
    y = [to_mod(val) for (_, val) in fit]
    base_R, base_rank = rref_mod(A, len(reps))
    aug_R, aug_rank = rref_mod([A[i] + [y[i]] for i in range(len(A))], len(reps) + 1)
    print(f"    fit points={len(fit)}  rank(F)={base_rank}  rank[F|y]={aug_rank}")
    consistent = (base_rank == aug_rank)
    xok = None
    if consistent:
        # solve for coefficients from reduced augmented system
        M, _ = rref_mod([A[i] + [y[i]] for i in range(len(A))], len(reps) + 1)
        coeff = [0] * len(reps)
        for row in M:
            # find pivot col
            pc = next((c for c in range(len(reps)) if row[c] % P), None)
            if pc is not None:
                coeff[pc] = row[len(reps)] % P
        xok = True
        for (om, val) in hold:
            ov = tuple(to_mod(x) for x in om)
            pred = 0
            for k in range(len(reps)):
                if coeff[k]:
                    pred = (pred + coeff[k] * orbit_value_mod(reps[k], ov)) % P
            if pred != to_mod(val) % P:
                xok = False
                print(f"    XVAL FAIL at {om}")
                break
        nz = sum(1 for x in coeff if x)
        print(f"    cross-validation on {len(hold)} held-out chamber pts: {'PASS' if xok else 'FAIL'}")
        print(f"    nonzero fitted coefficients: {nz}/{len(reps)}")
    ok = consistent and (xok is True)
    print(f"  => {'PASS' if ok else 'FAIL'}: A_6/i is a degree-8 symmetric polynomial in this chamber "
          f"(propagator poles removable here)")
    return ok


# ---------- D. reproduce H1 negative ----------

def trunc(x):
    return x ** 3 if x > 0 else F(0)


def check_D():
    print("=" * 70)
    print("D. H1 negative: plus-leg-only truncated-power family is rank-deficient")
    rng = random.Random(99)
    pts = []
    while len(pts) < 40:
        free = [F(rng.randint(-9, 9)) for _ in range(4)]
        if any(x == 0 for x in free):
            continue
        om = solve_onshell(free)
        if om is None or any(x == 0 for x in om):
            continue
        r = bg_amp(om)
        if r is None or r[0] != 0:
            continue
        pts.append((om, r[1]))

    def feats(om):
        xs = om[:3]; ys = om[3:]
        th2 = min(abs(x) for x in xs) ** 2
        B = F(0)
        for r in range(4):
            for S in combinations(range(3), r):
                B += F((-1) ** r) * trunc(th2 - sum(ys[j] ** 2 for j in S))
        return [xs[0] * xs[1] * xs[2] * B,
                (xs[0] ** 2 + xs[1] ** 2 + xs[2] ** 2) * B,
                ys[0] * ys[1] * ys[2] * B,
                (ys[0] ** 2 + ys[1] ** 2 + ys[2] ** 2) * B]
    A = [feats(om) + [val] for (om, val) in pts]
    Amod = [[to_mod(x) for x in row] for row in A]
    _, base = rref_mod([r[:4] for r in Amod], 4)
    _, aug = rref_mod(Amod, 5)
    print(f"    features=4  rank(F)={base}  rank[F|y]={aug}")
    ok = aug > base
    print(f"  => {'PASS (H1 family cannot represent A_6)' if ok else 'INCONCLUSIVE'}")
    return ok


if __name__ == "__main__":
    rA = check_A()
    rB = check_B()
    rC = check_C()
    rD = check_D()
    print("=" * 70)
    print(f"SUMMARY: A(walls)={rA}  B(reality/sym)={rB}  C(chamber-poly)={rC}  D(H1-neg)={rD}")
