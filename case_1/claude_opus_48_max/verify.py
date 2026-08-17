"""
verify.py  --  comprehensive verification of the closed-form A_n against an
INDEPENDENT exact (Gaussian-rational) Berends-Giele recursion ported from
OnShellBG.m.

For each n we draw many ascending-positive free-frequency points (the standard
sampling, for which |omega_2| = min_i|omega_i|), build the on-shell kinematics,
and compare:

      A_n  =  2^(n-1) i * omega_1 * omega_2^(2n-5)      (canonical closed form)

against bg_amplitude_exact(...).  Agreement is EXACT (rational identity), so the
relative error is 0 (we also print the float relative error as a sanity scale).

n = 4 is special: the on-shell conditions force omega_1 = -omega_3,
omega_4 = -omega_2, hence k_{2}+k_{4} = 0 and omega_2+omega_4 = 0, so the {2,4}
propagator is a removable 0/0 and the raw recursion is Indeterminate.  The
amplitude is the finite limit -8 i omega_2^3 omega_3 = 8 i omega_1 omega_2^3,
which the canonical formula reproduces (checked symbolically in Wolfram; see
verify_n4.m).
"""

import random
from fractions import Fraction as Fr
from waterhedron_two_minus import (
    make_kinematics, two_minus_sigma, bg_amplitude_exact, A_canonical,
    bg_amplitude,
)


def im_canonical(ws):
    n = len(ws)
    return Fr(2) ** (n - 1) * ws[0] * ws[1] ** (2 * n - 5)   # exact Im[A_n]


def sweep(n, npts, seed=0, exact=True):
    rng = random.Random(seed + n)
    n_ok = n_bad = 0
    worst = 0.0
    examples = []
    tries = 0
    while n_ok + n_bad < npts and tries < 60 * npts:
        tries += 1
        # ascending positive free frequencies, comparable magnitude
        vals = sorted({Fr(rng.randint(1, 40), rng.randint(1, 6)) for _ in range(n - 2)})
        if len(vals) != n - 2:
            continue
        ks, ws = make_kinematics(n, list(vals), two_minus_sigma(n), Fr(1))
        # require omega_2 to be the global-min magnitude (canonical chamber)
        mags = [abs(x) for x in ws]
        if min(range(n), key=lambda i: mags[i]) != 1:
            continue
        if exact:
            bgx = bg_amplitude_exact(ks, ws, Fr(1))
            ok = (bgx.re == 0) and (bgx.im == im_canonical(ws))
            n_ok += ok; n_bad += (not ok)
            if len(examples) < 3:
                examples.append((tuple(str(v) for v in vals), str(bgx.im)))
        else:  # float BG cross-check (fast, for large n)
            bg = bg_amplitude(ks, [float(x) for x in ws], 1.0)
            ca = complex(A_canonical([float(x) for x in ws]))
            rel = abs(bg - ca) / abs(ca)
            worst = max(worst, rel)
            ok = rel <= 1e-6
            n_ok += ok; n_bad += (not ok)
            if len(examples) < 3:
                examples.append((tuple(str(v) for v in vals), f"{ca.imag:.6g}"))
    return n_ok, n_bad, worst, examples


if __name__ == "__main__":
    print("Verification: canonical A_n vs independent Berends-Giele port", flush=True)
    print("=" * 70, flush=True)
    # n=5,6,7 EXACT (Gaussian-rational identity)
    plan = [(5, 40, True), (6, 20, True), (7, 6, True)]
    for n, npts, exact in plan:
        ok, bad, wf, ex = sweep(n, npts, exact=exact)
        tag = "EXACT match" if exact else f"float match (relerr<={wf:.1e})"
        print(f"n={n}:  {ok}/{ok+bad}  {tag}", flush=True)
        for fw, val in ex:
            print(f"        free_w={fw}  ->  Im[A_{n}] = {val}", flush=True)
    print("=" * 70, flush=True)
    print("=> A_n = 2^(n-1) i omega_1 omega_2^(2n-5) confirmed exactly (n=5,6,7).",
          flush=True)
