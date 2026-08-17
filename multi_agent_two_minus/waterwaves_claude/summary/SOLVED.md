# SOLVED — closed-form A_n in the two-minus sector (1D deep-water surface waves)

**Status:** ACCEPTED by the PI after independent re-verification.
**Accepted:** 2026-06-23T23:37:56 (UTC), round 2.
**Produced by:** student-1, session `bots/student-1/sessions/2026-06-23T22-30-52.json`
(board post `post_003`), the empirical/dataset path. It generalizes student-2's
principal-chamber derivation (`post_002`, `bots/student-2/.../2026-06-23T22-08-53.json`),
which is the deepest-chamber special case of this formula and corroborates it.

---

## (a) The formula

Conventions (sector σ = (−1,−1,+1,…,+1), g = 1):
- Legs **1, 2 are the minus legs** (σ = −1); legs **3,…,n are the plus legs** (σ = +1).
- t_j ≡ ω_j² (= |k_j| at g = 1).
- **P ≡ min(ω_1², ω_2²)** — the squared magnitude of the *smaller* minus leg.

Then `A_n = i · a_n` with a_n real, and

> **a_n = 2^{n−1} · ω_1 · ω_2 · Σ_{S ⊆ {3,…,n}} (−1)^{|S|} · [ max(0, P − Σ_{j∈S} ω_j²) ]^{n−3}**

The sum runs over all subsets S of the plus legs; the truncation `max(0,·)` is
essential (terms with Σ_{j∈S} ω_j² ≥ P contribute 0). Equivalently, with the shift
operator (T_t f)(x) = f(x−t),

> a_n = 2^{n−1} ω_1 ω_2 · [ Π_{j=3}^{n} (1 − T_{ω_j²}) · (x)_+^{\,n−3} ] |_{x=P}

i.e. the (n−2)-fold finite difference (a univariate B-spline / divided difference)
of the truncated power (x)_+^{n−3} at nodes {ω_3²,…,ω_n²}, evaluated at x = P.

**Properties (all confirmed):** purely imaginary; homogeneity degree 2n−4 in ω;
invariant under S₂ (swap minus legs 1↔2) × S_{n−2} (permute plus legs); piecewise-
polynomial across chambers (chamber walls = |ω_plus| = |ω_minus| crossings),
continuous across walls. **Deepest-chamber special case** (smaller minus is the
globally smallest magnitude, all ω_j² ≥ P): every S ≠ ∅ truncates to 0 and
a_n = 2^{n−1} ω_1 ω_2 · P^{n−3} = 2^{n−1} ω_1 ω_2^{2n−5} — student-2's derived form.

---

## (b) PI independent verification

The PI verified this with code written from scratch — its own freshly-built oracle
(`bots/pi/code/bg`, identical to the canonical `bg.cpp`, rebuilt with the documented
line), its own exact-rational subprocess driver/parser, and its own formula
evaluator (`bots/pi/code/pi_round2_verify.py`; no student code imported). n = 4 was
obtained by an **independent δ→0 limit** (raw `--amp` continuation along Σω = 0 with
the square constraint relaxed by δ, then exact Neville extrapolation to δ = 0).

**Result: 142/142 tested points pass, all BIT-EXACT (relative residual ≡ 0, well
inside the ≤ 10⁻¹⁰ bar). 95 of these lie in non-principal chambers where the
truncated inclusion–exclusion genuinely fires** (so the all-chamber content — not
just student-2's principal monomial — was exercised). Full log:
`bots/pi/code/pi_verification_output.txt`.

Representative checked points (a_n; A_n = i·a_n):

| n | full ω (in leg order) | a_n (oracle = formula) | residual |
|---|---|---|---|
| 4 | (−3, 1, 3, −1) [δ-limit] | −24 | 0 (exact) |
| 4 | (−5, 2, 5, −2) [δ-limit] | −320 | 0 (exact) |
| 4 | (−7, 3, 7, −3) [δ-limit] | −1512 | 0 (exact) |
| 4 | (−5, 1, 5, −1) [δ-limit] | −40 | 0 (exact) |
| 5 | (−34/7, 1, 2, 4, −15/7) | −544/7 | 0 (exact) |
| 5 | (−13/2, 2, 3, 5, −7/2) | −3328 | 0 (exact) |
| 5 | (..., 1, 2, 1000, ...) [one plus ≫] | −16048096/1003 | 0 (exact) |
| 5 | -w (1, 2, 1/1000) [one plus ≪], chamber b1m2h0 | −12005995996999/187562500000000000 | 0 (exact) |
| 5 | -w (6, 1, 2) [non-principal b2m0h1] | −6400/3 | 0 (exact) |
| 6 | (−32/5, 1, 2, 3, 4, −18/5) | −1024/5 | 0 (exact) |
| 6 | -w (7, 1, 2, 3) [non-principal b3m0h1] | −3241728/13 | 0 (exact) |
| 7 | (−139/15, 1, 2, 3, 4, 5, −86/15) | −8896/15 | 0 (exact) |
| 7 | -w (1, 2, 3, 4, 1000) [one plus ≫] | −32322048/505 | 0 (exact) |
| 7 | -w (8, 1, 2, 3, 4) [non-principal b4m0h1] | −57016320 | 0 (exact) |
| 7 | -w (1, 2, 3, 4, 1/500) [one plus ≪, b1m4h0] | −1000306560640629984994999/152618408203125000000000000 | 0 (exact) |

Coverage:
- **n = 4** (δ-limit): 4 points — exact.
- **n = 5** (exact rational): 2 refs + 3 non-generic regimes + 50 random
  all-chamber points (chambers b0m3h0, b1m2h0, b2m0h1, b2m1h0) — 50/50 exact, 33 non-principal.
- **n = 6** (exact rational): 1 ref + 2 non-generic + 40 random (b0m4h0, b1m3h0,
  b2m2h0, b3m0h1, b3m1h0) — 40/40 exact, 31 non-principal.
- **n = 7** (exact rational, ~0.5 s/pt): 2 refs + 2 non-generic + 30 random
  (b0m5h0, b1m4h0, b2m3h0, b3m2h0, b4m0h1, b4m1h0) — 30/30 exact, 23 non-principal.
- **n = 8** (beyond the required range, exact rational ~7.6 s/pt): principal
  (−33920/21) and a non-principal b5m0h1 point (−22809600000) — both bit-exact.

Note on tooling (consistent with both students): exact rational is the right tool;
`./bg --double` loses up to ~10⁻⁵ at small/extreme n=7 frequencies (long-double
round-off in the BG recursion, not a formula error). The PI used exact rational
throughout. The oracle SIGFPEs (exit 136 / rc −8) at isolated singular on-shell
points (the n=4 on-shell point, and one n=8 point) where an internal current hits
0/0; these are removable and handled by the δ-limit — they are oracle-evaluation
artifacts, not failures of the formula.

---

## (c) How it was arrived at

- **student-2** (BG-recursion derivation): symbolic recursion at n=4,5 gave
  a_4 = 8 ω_1 ω_2³, a_5 = 16 ω_1 ω_2⁵ ⇒ principal-chamber a_n = 2^{n−1} ω_1 ω_2^{2n−5};
  also derived Re A_n = 0 (every BGCurrent carries an even number of i's; the lone
  root vertex makes A_n = i·real) and the n=4 finiteness (the {2,4} 1/D pole is
  killed by a vanishing numerator, leaving a polynomial).
- **student-1** (empirical/dataset): local single-chamber rational fits at n=5
  (16 ω_1 ω_2 × degree-2 poly), then the cross-chamber pattern resolved to a
  **truncated-power inclusion–exclusion** = finite-difference / B-spline of order
  n−2, exponent confirmed n−3 at n=6 (cube) and n=7 (4th power). This extends
  student-2's principal monomial to all chambers; only the *smaller* minus square P
  enters (the larger minus appears only through the prefactor ω_1 ω_2).

**Open (not required for acceptance):** a first-principles proof that the BG
recursion telescopes to this B-spline form, and an explicit g-dependence check
(verification here is at g = 1, matching the question's reference points).

The run is complete; no further tasks are assigned.
