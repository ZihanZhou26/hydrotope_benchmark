# TRAJECTORY.md — chronological log of main steps

1. Read prompt.md, OnShellBG.m, scaffold.md. Task: closed-form A_n in the
   two-minus sector σ=(-1,-1,+1,...,+1), all n≥4, verified vs BGAmplitude.
2. Built wolframscript oracle harness (`scripts/bg_oracle.wls`) from the verbatim
   OnShellBG.m definitions + a two-minus driver printing exact amplitudes.
3. Ran anchors. Found: (F0) A_n is purely imaginary (A_n = i·a_n); (F1) n=4 is
   intrinsically degenerate (forced w4=-w2, w1=-w3 ⇒ 0/0 propagator). Got exact
   values a_5{2,5/2,3}=-2304, a_5{1,2,3}=-64, a_6{3/2,2,5/2,3}=-11907/4.
4. Ported BG to Python exact complex-rational (`scripts/bg.py`), memoized kernels.
   Validated: reproduces all finite anchors EXACTLY, agrees n=4 degenerate, ~12×
   faster. Cross-checked vs wolframscript at n=7 (−7302393 i/400). Working oracle.
5. Invariants (`explore.py`): a_n homogeneous degree 2n−4; symmetric in minus legs
   and in plus legs; A_n purely imaginary.
6. C1 candidate: a_5 = degree-6 symmetric polynomial in (e₁,e₂,P₃). Exact fit
   INCONSISTENT (`fit_poly.py`) ⇒ a_n not polynomial. **Policy v0→v1** (rule 6:
   characterize analytic structure first).
7. Rational interpolation (`scan.py`): a_5 along a line = −16(t²+3t+6)/(t+3); only
   pole is the solver point ⇒ dependence carried by the minus pair.
8. Built high-precision mpmath port (`bg_float.py`); P3-independence test
   (`test_P3.py`) → a_5 PIECEWISE: constant when plus legs interleave the minus legs.
9. Region map (`explore2.py`,`explore3.py`): in the interleaving region a_n=F_n(e₁,e₂);
   F_{n+1}/F_n = 2·min(ω₁²,ω₂²), F_5 = 16·ω₁·(smaller minus)⁵.
10. C2/C3 formula: A_n = i·2^(n−1)·ω₁ω₂·(min(ω₁²,ω₂²)/g)^(n−3). Matches all 6 exact
    anchors. g-power = g^(−(n−3)) (`explore4.py`).
11. Domain (`verify1a.py`,`verify_final.py`): EXACT dichotomy — passes ALL
    interleaving points, fails ALL non-interleaving; 48/48 across g∈{1,2,3,1/2}.
12. n=4 (`verify_n4.py`): ε→0 limit confirms a_4 = 8 ω₁ω₂ min(ω₁²,ω₂²)/g.
13. n=8 (`verify_final.py`, float): −1572864 = formula, relerr ~1e-37.
14. Non-interleaving probe (`explore5/6.py`): each region structured (one-soft depends
    on minus+s²) but no simple universal form; explore6 self-contradiction →
    **Policy v1→v2** (rule 7: validate numeric backend). Cross-check
    (`crosscheck_float.py`): bg_float matches exact to <3e-13; artifact was an
    un-reset mpmath cache; correct one-soft value −18944.
15. FINAL held-out (`verify_holdout.py`, fresh seed): 48/48 interleaving (g∈{1,3}),
    all anchors re-confirmed, n=4 fresh pair (−9,4) → −4608 (ε-limit confirms).

## Held-out results (fresh seed 31337)
- n=5,6,7 interleaving, g∈{1,3}: 48/48 EXACT PASS.
- All 6 prior anchors: re-confirmed exact.
- n=4 (−9,4): formula −4608; ε=1e−6 limit −4607.9987 → −4608.

## Decision
Reported the clean interleaving-region formula as THE closed-form analytic answer;
documented the piecewise (non-analytic) nature of the full sector and the exact
out-of-domain failures (SCOPE.md, FAILED_TESTS.md). Narrowing justified by the
prompt's word "analytic".
