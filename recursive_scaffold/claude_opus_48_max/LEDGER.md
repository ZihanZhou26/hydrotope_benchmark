# LEDGER.md — candidates, tests, passes, fails

Every candidate formula and every test point. Failing entries are NEVER deleted.

Convention: kinematic points are described by `(n, freeW)` where `freeW = {w2,...,w_{n-1}}`
and the sector is two-minus `σ = (-1,-1,+1,...,+1)`; ω1, ωn are solved by MakeKinematics.
g = 1 unless stated.

---

## Structural facts (oracle-derived, exact)

- **F0**: `A_n` is purely imaginary: `A_n = i * a_n`, `a_n ∈ Q`. (Every BG current
  is real; every vertex & propagator is purely imaginary.) Work with `a_n = Im(A_n)`.
- **F1**: n=4 two-minus is intrinsically DEGENERATE. The on-shell solver forces
  `w4=-w2, w1=-w3`, so sub-channel {2,4} (and {1,3}) has `w_S=0` AND `k_S=0` →
  propagator `0/0`. Oracle returns `Indeterminate`; Python port hits 0/0. n=4
  needs a limit/regularization (deferred).
- **F2**: a_n is HOMOGENEOUS of degree 2n-4 in the frequencies (verified n=5,6,7
  with λ=2,3, exact).
- **F3**: a_n is symmetric in the two minus legs {ω1,ω2} and (separately) in the
  plus legs {ω3..ωn} (verified n=5,6 by relabeling).
- **F4**: conservation ⇒ e1:=ω1+ω2 = -(ω3+..+ωn), and ω1²+ω2² = ω3²+..+ωn².
  Surface coords: e1(deg1), e2=ω1ω2(deg2), and plus power sums P3..P_{n-2}
  (P1=-e1, P2=e1²-2e2 fixed). #free params = n-2.

## Anchor / oracle values (g=1, exact)

| n | freeW | a_n = Im(A_n) |
|---|-------|---------------|
| 5 | {2,5/2,3}      | -2304        |
| 5 | {1,2,3}        | -64          |
| 6 | {3/2,2,5/2,3}  | -11907/4     |

Python port reproduces all three EXACTLY (and agrees n=4 degenerate). Port trusted.

## Candidates

- **C1** (step 5): a_5 = homogeneous degree-6 symmetric polynomial in (e1,e2,P3).
  **FAILED**: exact linear fit over 32 points is INCONSISTENT (no solution).
  Implies a_n is RATIONAL (BG propagator denominators) or non-analytic via |k_S|.
  → triggered policy v0→v1.

## Candidate C3 (step 13) — full formula with g
**A_n = i · 2^(n-1) · ω1 ω2 · [min(ω1²,ω2²)/g]^(n-3)**
g-power confirmed: n=5→-2, n=6→-3, n=7→-4 ⇒ g^-(n-3); min(ω1²,ω2²)/g = min(|k1|,|k2|).
Valid in the interleaving region. n=4 limit (ε→0) confirms a_4 = 8 ω1ω2 min(ω1²,ω2²)/g.

## Candidate C2 (step 10) — MATCHES ALL EXACT ANCHORS (g=1)
**a_n = 2^(n-1) · (ω1 ω2) · [min(ω1²,ω2²)]^(n-3)**, A_n = i·a_n (g=1).
Derived from interleaving-region data: c=F_{n+1}/F_n=2·w2² (w2 smaller minus),
F_5=16·w1·w2^5. Exact match at n=5 (4 pts), n=6, n=7 anchors. Depends ONLY on
the two minus-leg frequencies. Valid (so far) in the interleaving region.
Open: domain (full sector vs interleaving), g-dependence, n=4.

## Observations
- a_5/e2 sampled: {1,2,3}→16, {1,3,5}→16, {2,5/2,3}→256, {2,3,7}→256.
  (16=2^4, 256=2^8.) a_5/e2 is degree-4 homogeneous; not constant. Since a_5 is
  NOT a polynomial, e2 is likely a DENOMINATOR factor (channel {1,2}:
  D_{12}=ω_S²-|k_S|=e1²-(e1²-2e2)=2e2, always analytic since k_{12}<0).

- **F5 (BIG)**: a_n is PIECEWISE in the plus-leg configuration (non-analytic via
  |k_S| in kernels). At fixed minus pair (w1,w2)=(-4,1), varying plus config:
  a_5 = -64 (CONSTANT) for plus legs with all |ω_plus| between |ω2| and |ω1|;
  different values when a plus |ω| leaves that interval. Region boundaries are
  |ω_plus| = |ω_minus| (a minus+plus channel momentum -ω_m²+ω_p² crossing 0).
  → In the "interleaving" region, a_n depends ONLY on (e1,e2)=(ω1+ω2, ω1ω2),
    NOT on the plus distribution. This also explains the C1 failure (mixed regions).

## C2 domain (step 11) — exact dichotomy
- g-dependence: a_n(g)/a_n(1) = 1/g² at n=5 (g=2→1/4, g=3→1/9, g=1/2→4). Need n-dep check.
- C2 vs oracle on random MakeKinematics points: n=5 interleaving 12/12 PASS, non-int 0/28;
  n=6 int 10/10, non-int 0/30; n=7 int 11/11, non-int 0/29. CLEAN: C2 ⟺ interleaving.
- Hierarchical: fw=[2,3,50]→interleaving→OK; [2,3,1/50]→non-int→DIFF; [1/100,2,3]→int→OK;
  [50,2,3]→non-int→DIFF. So "one freq large" can stay interleaving; "soft plus leg" breaks it.
- Interleaving ⟺ both minus legs are the global min & max |ω| (all plus |ω| between them).
- IMPLICATION: amplitude is PIECEWISE (non-analytic). Need full structure or justified narrowing.

## C3 final verification (steps 12,14)
- n=4: ε→0 limit confirms a_4 = 8 ω1ω2 min(ω1²,ω2²)/g (4 minus pairs).
- n=5,6,7: 48/48 EXACT pass at g∈{1,2,3,1/2} on interleaving points.
- n=8 (float, cache-reset): -1572864 = cand, relerr ~1e-37 (3 points).
- Required hierarchical regimes (in-domain): all PASS exact (one plus huge; minus tiny).
- Non-interleaving (EXACT, bg.py): C3 ≠ oracle (well-defined but different rationals).
- Float port bg_float validated vs exact (relerr<3e-13) incl. non-interleaving WHEN
  caches reset; without reset, accumulated mpmath cache corrupts soft-leg evals
  (explore6 artifact; explore5/clean value -18944 is correct).
- One-soft region (1 plus |ω|<|ω2|): a_n depends only on (minus pair, soft s²),
  even in s, → interleaving value as s²→ω2². Coefficients messy (no clean universal form).

## Test log

- Port vs wolframscript: PASS (exact) at the 3 finite anchors AND at n=7
  ({3/2,2,5/2,3,7/2} → -7302393*I/400). Port trusted through n=7.
- C1 polynomial fit n=5: FAIL (inconsistent) — a_n not polynomial (piecewise/rational).
- C2/C3 interleaving: PASS exact, all n=4(limit),5,6,7,8 and g∈{1,2,3,1/2}.
- C2/C3 non-interleaving: FAIL (by design; amplitude is piecewise). Examples in FAILED_TESTS.md.
