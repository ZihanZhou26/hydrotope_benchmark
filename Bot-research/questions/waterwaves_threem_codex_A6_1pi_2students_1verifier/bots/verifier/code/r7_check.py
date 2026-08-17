"""
r7_check.py -- ROUND 7 independent verifier audit.

Newest load-bearing candidate: student-2's symmetric q-brick B^sym (s2_013,
post_027), which student-2 itself flagged as REFUTED using a *reuse* of my
round-6 harness. Here I transcribe B^sym from the WRITTEN formula (s2_013) into
MY OWN code and rerun the decisive cure test against a FRESHLY BUILT oracle
(bg_r7), importing no student evaluator and not trusting their stored JSON.

Decomposition (verifier/PI-confirmed): S = R_spline - R_Q = R_0 + R_q, an
order-1 spline over the 9 q_{mp}=0 walls. A correct R_q = sum (q_mp)_+ B_mp must
make T = S - R_q SMOOTH across every isolated q-wall (R_0 is smooth and cancels
from any jump). If T still JUMPS, the candidate B is wrong.

B^sym (s2_013, boxed):
  a=w_m, b=w_p, q=b^2-a^2 ; x,y = other two MINUS freqs ; s=x+y, v=x*y
  F = a s^3 + v(s^2-2v)
  D = 2a^3 + 3a^2 s + a(s^2+v) - s v
  E = F + (a+b) D
  beta^2 = min_{j notin {m,p}} w_j^2   (over the FOUR environment legs)
  B^sym_mp = -32 beta^2 E
             -16 q ( [3a^2+2a(s+b)-v](s^2-2v) + b s (s^2-v) )
             +16 b s q^2
  R_q^sym = sum_{m in M, p in P} (q_mp)_+ B^sym_mp
"""
from fractions import Fraction as Fr
from itertools import combinations
import os, sys
import r6_core as C
# point the independent pipeline at the FRESH round-7 oracle
C.BG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bg_r7")
C._AMP_CACHE.clear()
from r5_core import line, poly_interp, poly_eval, SingularError
from r6_walls import wall_crossings
from r6_checkA import null_dirs, onshell_pt, esign

M, P = [0, 1, 2], [3, 4, 5]

def Bsym(om, m, p):
    """student-2 s2_013 boxed symmetric brick, transcribed from the WRITTEN formula."""
    a = om[m]; b = om[p]; q = b*b - a*a
    other_minus = [i for i in M if i != m]
    x = om[other_minus[0]]; y = om[other_minus[1]]
    s = x + y; v = x*y
    F = a*s**3 + v*(s*s - 2*v)
    D = 2*a**3 + 3*a*a*s + a*(s*s + v) - s*v
    E = F + (a+b)*D
    # beta^2 = min over the four environment legs (2 other minus + 2 other plus)
    env = [i for i in range(6) if i not in (m, p)]
    beta2 = min(om[j]*om[j] for j in env)
    corr1 = (3*a*a + 2*a*(s+b) - v)*(s*s - 2*v) + b*s*(s*s - v)
    return -32*beta2*E - 16*q*corr1 + 16*b*s*q*q

def Rq_sym(om):
    tot = Fr(0)
    for m in M:
        for p in P:
            q = om[p]**2 - om[m]**2
            if q > 0:
                tot += q * Bsym(om, m, p)
    return tot

def T_val(om):
    return C.S_resid(om) - Rq_sym(om)

# ---- on-wall trace guard: B^sym|_{q=0} must equal -32 beta^2 E ----
def onwall_trace_guard():
    """At any point with w_p^2 = w_m^2 (q=0) the two corrections vanish by
    construction, so B^sym = -32 beta^2 E. Confirm symbolically-numerically."""
    import random
    rng = random.Random(7)
    ok = 0; tot = 0
    for _ in range(30):
        # build a random point, then force |w_p|=|w_m| for a chosen pair
        om = [Fr(rng.randint(-9, 9)) for _ in range(6)]
        if any(x == 0 for x in om):
            continue
        m, p = 0, 3
        om[p] = abs(om[m]) * (1 if rng.random() < 0.5 else -1)  # |w_p|=|w_m|
        a = om[m]; b = om[p]
        other_minus = [i for i in M if i != m]
        x = om[other_minus[0]]; y = om[other_minus[1]]
        s = x+y; v = x*y
        F = a*s**3 + v*(s*s-2*v); D = 2*a**3+3*a*a*s+a*(s*s+v)-s*v; E = F+(a+b)*D
        env = [i for i in range(6) if i not in (m, p)]
        beta2 = min(om[j]*om[j] for j in env)
        tot += 1
        if Bsym(om, m, p) == -32*beta2*E:
            ok += 1
    return ok, tot

def _fit_side(fn, Pv, dv, ts):
    xs, ys = [], []
    for t in ts:
        om = line(Pv, dv, t)
        try:
            y = fn(om)
        except (SingularError, RuntimeError) as e:
            if "SIGFPE" in str(e) or "rc=" in str(e) or isinstance(e, SingularError):
                continue
            raise
        xs.append(t); ys.append(y)
    if len(xs) < 10:
        return None
    return poly_interp(xs[:9], ys[:9]), xs[9:], ys[9:]

def smooth_across(fn, Pv, dv, t0, half):
    L = _fit_side(fn, Pv, dv, [t0 - Fr(1, 50) - half*Fr(i, 12) for i in range(1, 12)])
    R = _fit_side(fn, Pv, dv, [t0 + Fr(1, 50) + half*Fr(i, 12) for i in range(1, 12)])
    if L is None or R is None:
        return None
    cLL = L[0]
    xR, yR = R[1], R[2]
    cross = max((abs(poly_eval(cLL, x) - y) for x, y in zip(xR, yR)), default=Fr(0))
    contin = abs(poly_eval(cLL, t0) - poly_eval(R[0], t0))
    return cross, contin

BASES = [[8, 2, -3, -5, 4, -6], [-8, 2, 3, 4, 5, -6], [10, -7, -6, -5, -4, 12],
         [1, -21, -18, 3, 9, 26], [-1, -28, -24, 4, 16, 33], [-8, -7, -3, 4, 5, 9],
         [-3, -14, -2, 8, 12, -1], [-1, -35, -10, -5, 25, 26]]

def main():
    import json
    g_ok, g_tot = onwall_trace_guard()
    print(f"Guard: B^sym == -32 beta^2 E on the wall q=0: {g_ok}/{g_tot}")

    anchor = [Fr(-8), Fr(2), Fr(3), Fr(4), Fr(5), Fr(-6)]
    print("anchor: A6/i =", C.amp_over_i(anchor), " S =", C.S_resid(anchor),
          " Rq_sym =", Rq_sym(anchor), " T =", T_val(anchor))

    results = []
    n = 0; S_jumps = 0; T_smooth = 0; T_contin_ok = 0
    for base in BASES:
        if not onshell_pt(base):
            continue
        for dv in null_dirs(base, 3):
            cr = wall_crossings(base, dv, Fr(-1), Fr(1))
            for i, (tc, kind, lab) in enumerate(cr):
                if kind != "q":
                    continue
                left = cr[i-1][0] if i > 0 else Fr(-1)
                right = cr[i+1][0] if i+1 < len(cr) else Fr(1)
                gap = min(tc - left, right - tc)
                if gap < Fr(1, 4):
                    continue
                half = min(gap*Fr(2, 5), Fr(1, 3))
                sres = smooth_across(C.S_resid, base, dv, tc, half)
                tres = smooth_across(T_val, base, dv, tc, half)
                if sres is None or tres is None:
                    continue
                n += 1
                sj = sres[0] != 0
                t_is_smooth = (tres[0] == 0 and tres[1] == 0)
                t_val_contin = (tres[1] == 0)
                if sj:
                    S_jumps += 1
                if t_is_smooth:
                    T_smooth += 1
                if t_val_contin:
                    T_contin_ok += 1
                results.append({"wall": lab, "t0": str(tc),
                                "S_jumps": sj, "T_smooth": t_is_smooth,
                                "T_value_continuous": t_val_contin,
                                "T_cross_resid": str(tres[0]), "T_contin": str(tres[1])})
                if n >= 18:
                    break
            if n >= 18:
                break
        if n >= 18:
            break

    print(f"\nIsolated q-wall crossings tested: {n}")
    print(f"  S jumps across the q-wall (control):            {S_jumps}/{n}")
    print(f"  T = S - Rq_sym C^0 value-continuous at wall:    {T_contin_ok}/{n}")
    print(f"  T = S - Rq_sym FULLY SMOOTH across the q-wall:  {T_smooth}/{n}")
    print("\nAll crossings (candidate WRONG where T not smooth):")
    for r in results:
        print(f"   wall {r['wall']} t0 {r['t0']:>10}  S_jumps {r['S_jumps']}  "
              f"T_C0 {r['T_value_continuous']}  T_smooth {r['T_smooth']}  "
              f"cross_resid {r['T_cross_resid']}")
    json.dump({"n": n, "S_jumps": S_jumps, "T_contin_ok": T_contin_ok,
               "T_smooth": T_smooth, "guard": [g_ok, g_tot], "results": results},
              open("../data/r7_check.json", "w"), indent=1)

if __name__ == "__main__":
    main()
