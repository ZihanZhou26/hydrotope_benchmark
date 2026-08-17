#!/usr/bin/env python3
"""student-1 independent verification of the n=5 THREE-minus closed form.

Task r1-student-1: lock down and fully document the n=5 three-minus closed form
with its chamber decomposition.  This script is SELF-CONTAINED: it builds its OWN
copy of bg.cpp (bots/student-1/code/bg.cpp) and checks the formula against ./bg in
EXACT RATIONAL mode at >= 20 kinematic points (generic, fractional, non-generic),
reporting the exact residual at each point and classifying the chamber.

----------------------------------------------------------------------------------
The formula (legs 1,2,3 carry sigma=-1; legs 4,5 carry sigma=+1), g general:

    A_5 = i * 2^4 * g^{-2} * w4 * w5
            * sum_{S subset {1,2,3}} (-1)^|S| ( beta^2 - sum_{j in S} w_j^2 )_+^2 ,
    beta = min(|w4|, |w5|),   (x)_+ = max(x, 0).

DERIVATION (plus/minus swap, question.md items 2+3):
  The all-momentum sign flip k_i -> -k_i (equiv. sigma_i -> -sigma_i) at fixed
  frequencies leaves A_n invariant and maps the k-minus sector to the (n-k)-minus
  sector.  For n=5 three-minus (minus legs 1,2,3), flipping gives a TWO-minus
  configuration whose minus legs are 4,5.  Applying the known two-minus
  truncated-power law (question.md item 2)
      A_n = i 2^{n-1} g^{3-n} W_a W_b sum_{S subset plus} (-1)^|S|(B^2-sum_S w^2)_+^{n-3}
  with minus legs {a,b}={4,5}, plus legs {3..n}->{1,2,3}, B=min(|w4|,|w5|), n=5
  yields exactly the boxed formula above.  See derivations/n5_derivation.md.
----------------------------------------------------------------------------------
"""
import subprocess, re, sys, os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BG   = os.path.join(HERE, "bg")
SRC  = os.path.join(HERE, "bg.cpp")

# --------------------------------------------------------------------------- #
#  oracle plumbing
# --------------------------------------------------------------------------- #
def ensure_bg():
    if os.path.exists(BG):
        return
    print("[build] compiling own copy of bg.cpp ...")
    subprocess.check_call(["g++", "-O2", "-std=c++17", "-o", BG, SRC,
                           "-lgmpxx", "-lgmp"])

def oracle_onshell(free, g=1):
    """Run ./bg -n 5 -w <free> -s -1,-1,-1,1,1 in exact mode.
    free = (w2,w3,w4).  Returns (re, im, [w1..w5]) as exact Fractions, or
    raises subprocess.CalledProcessError on an |k_S|=0 SIGFPE wall."""
    out = subprocess.check_output(
        [BG, "-n", "5", "-w", ",".join(map(str, free)),
         "-s", "-1,-1,-1,1,1", "-g", str(g)],
        stderr=subprocess.DEVNULL).decode()
    return _parse(out)

def oracle_amp(K, W, g=1):
    """Run ./bg --amp -K <K> -W <W> (raw BGAmplitude, exact mode)."""
    out = subprocess.check_output(
        [BG, "--amp", "-K", ",".join(map(str, K)),
         "-W", ",".join(map(str, W)), "-g", str(g)],
        stderr=subprocess.DEVNULL).decode()
    return _parse(out)

def _parse(out):
    m = re.search(r"A_\d+ = i \* \(([-0-9/]+)\)", out)
    if m:
        re_p, im = F(0), F(m.group(1))
    else:
        m = re.search(r"A_\d+ = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)", out)
        re_p, im = F(m.group(1)), F(m.group(2))
    oms = [F(x.strip()) for x in
           re.search(r"omega = \{([^}]+)\}", out).group(1).split(",")]
    return re_p, im, oms

# --------------------------------------------------------------------------- #
#  the closed form (exact)
# --------------------------------------------------------------------------- #
def formula(oms, g=1):
    """Exact (re, im) of A_5 from the boxed formula. Real part is always 0."""
    w1, w2, w3, w4, w5 = oms
    g = F(g)
    beta2 = min(w4 * w4, w5 * w5)
    minus = [w1, w2, w3]
    tot = F(0)
    for mask in range(8):
        S = [minus[i] for i in range(3) if mask & (1 << i)]
        val = beta2 - sum(x * x for x in S)
        if val > 0:
            tot += (-1) ** len(S) * val * val
    im = 16 * g**(-2) * w4 * w5 * tot
    return F(0), im

# --------------------------------------------------------------------------- #
#  chamber classification (down-set of active minus-subsets)
# --------------------------------------------------------------------------- #
def active_subsets(oms):
    """Return the frozenset of active minus-subsets S subset {1,2,3}
    (those with sum_{j in S} w_j^2 < beta^2). S encoded as frozenset of leg ids."""
    w1, w2, w3, w4, w5 = oms
    beta2 = min(w4 * w4, w5 * w5)
    sq = {1: w1 * w1, 2: w2 * w2, 3: w3 * w3}
    act = set()
    for mask in range(8):
        S = frozenset(i for i in (1, 2, 3) if mask & (1 << (i - 1)))
        if sum(sq[j] for j in S) < beta2:        # empty set: 0 < beta2 -> active
            act.add(S)
    return frozenset(act)

def chamber_type(oms):
    """Classify the realizable chamber type A/B/C/D/E (see derivation)."""
    act = active_subsets(oms)
    singles = sorted(len(S) == 1 for S in act).count(True)
    pairs   = sum(1 for S in act if len(S) == 2)
    triple  = any(len(S) == 3 for S in act)
    if triple:
        return "X(triple-active: should never happen on-shell)"
    if pairs == 1:
        return "E"
    if pairs > 1:
        return "X(>1 pair active: should never happen on-shell)"
    return {0: "A", 1: "B", 2: "C", 3: "D"}[singles]

# --------------------------------------------------------------------------- #
#  test point catalogue  (free freqs = (w2, w3, w4))
# --------------------------------------------------------------------------- #
CURATED = [
    # generic integers
    (2, 3, 5), (1, 4, 6), (3, 5, 7), (2, 7, 4), (4, 2, 9), (5, 1, 3),
    # fractional
    (F(1, 2), 3, 9), (F(3, 7), F(11, 5), 6), (F(5, 2), F(7, 3), 4),
    (F(1, 3), F(1, 5), 2), (F(9, 4), F(2, 3), F(13, 5)),
    # non-generic: one freq >> the rest
    (100, 1, 2), (1, 1, 100), (1, 100, 2), (2, 3, 100), (1, 2, 200),
    # non-generic: one freq << the rest
    (F(1, 100), 4, 4), (F(1, 1000), 5, 2), (5, F(1, 100), 3),
    (4, 4, F(1, 50)), (F(1, 100), F(1, 100), 7),
    # explicit off-wall representatives of each realizable chamber type A,B,C,E
    (-1, -1, F(-1, 2)),   # chamber A (empty: F=beta^4)
    (-1, -1, F(1, 2)),    # chamber B (one minus singleton active)
    (-1, -1, F(-4, 3)),   # chamber C (two singletons, no pair active)
    (-1, -1, -2),         # chamber E (one pair active: F=2 w_i^2 w_j^2)
]

def main():
    ensure_bg()
    # ---- 1. residual table over the curated catalogue ------------------- #
    print("=" * 92)
    print("n=5 THREE-minus : formula vs ./bg  (EXACT rational mode, g=1)")
    print("=" * 92)
    hdr = f"{'#':>2} {'free(w2,w3,w4)':>22} {'chamber':>7} {'A_5 (oracle, im)':>20} {'residual':>10}"
    print(hdr); print("-" * 92)
    allok, n_ok, n_tot, seen_chambers = True, 0, 0, {}
    for i, p in enumerate(CURATED, 1):
        try:
            re_o, im_o, oms = oracle_onshell(p)
        except subprocess.CalledProcessError:
            print(f"{i:>2} {str(p):>22}   --- oracle SIGFPE on |k_S|=0 wall (skip; see walls_n5.py)")
            continue
        re_f, im_f = formula(oms)
        ch = chamber_type(oms)
        seen_chambers.setdefault(ch, 0)
        seen_chambers[ch] += 1
        resid = (re_o - re_f, im_o - im_f)
        ok = (resid == (F(0), F(0)))
        allok &= ok; n_tot += 1; n_ok += ok
        rstr = "0 (EXACT)" if ok else f"RE {resid[0]} IM {resid[1]}"
        print(f"{i:>2} {str(p):>22} {ch:>7} {str(im_o):>20} {rstr:>10}")
    print("-" * 92)
    print(f"EXACT MATCHES: {n_ok}/{n_tot}    chamber coverage: {dict(sorted(seen_chambers.items()))}")
    print()

    # ---- 2. plus/minus swap invariance, directly via --amp -------------- #
    print("=" * 92)
    print("Plus/minus swap invariance (raw --amp): flip every K_i -> -K_i, A_5 unchanged")
    print("=" * 92)
    swap_ok = True
    for p in [(2, 3, 5), (1, 4, 6), (F(1, 2), 3, 9), (100, 1, 2)]:
        _, _, oms = oracle_onshell(p)
        w1, w2, w3, w4, w5 = oms
        K = [-w1*w1, -w2*w2, -w3*w3, w4*w4, w5*w5]   # three-minus momenta
        _, im_3m, _ = oracle_amp(K, oms)
        _, im_2m, _ = oracle_amp([-k for k in K], oms)  # flip -> two-minus(4,5)
        ok = (im_3m == im_2m); swap_ok &= ok
        print(f"  free={str(p):>16}: A(3-minus)={im_3m}  A(flip)={im_2m}  equal={ok}")
    print(f"SWAP INVARIANCE HOLDS: {swap_ok}")
    print()

    ok_all = allok and swap_ok
    print("=" * 92)
    print(f"OVERALL: {'ALL EXACT / PASS' if ok_all else 'FAILURE'}")
    print("=" * 92)
    return 0 if ok_all else 1

if __name__ == "__main__":
    sys.exit(main())
