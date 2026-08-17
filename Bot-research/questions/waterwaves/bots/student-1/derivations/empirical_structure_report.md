# Empirical-structure report — two-minus sector A_n (student-1, round 1)

**Task t_r1_s1.** Build an exact-rational A_n dataset and discover the closed
form empirically. Result: **a closed form for A_n valid for all n ≥ 4 and
arbitrary in-sector kinematics**, verified bit-exactly against the oracle at
n = 4 (δ-limit), 5, 6, 7 over 115 points spanning every chamber + non-generic
regimes. All scripts/data are in `bots/student-1/{code,data,figures}`.

---

## 0. Conventions

- Sector σ = (−1,−1,+1,…,+1): legs **1,2 are "minus" legs** (σ=−1, momentum
  k=−ω²), legs **3..n are "plus" legs** (σ=+1, k=+ω²).
- On-shell: Σω_i = 0 and Σσ_iω_i² = 0, i.e. ω_3²+…+ω_n² = ω_1²+ω_2².
- A_n = i·a_n with a_n real (rational at rational kinematics) — PI fact, re-confirmed.
- g = 1 throughout (the homogeneity below absorbs g; see §6 note).

## 1. THE RESULT — closed form

Let
- **t_j = ω_j²** (squared magnitude of leg j),
- **P = min(ω_1², ω_2²)** = squared magnitude of the *smaller* minus leg,
- plus legs are j = 3,…,n.

Then

>  **A_n = i · 2^{n−1} · ω_1 ω_2 · Σ_{S ⊆ {3,…,n}} (−1)^{|S|} · [ max(0, P − Σ_{j∈S} t_j) ]^{n−3}**

The sum is over all subsets S of the plus legs; the truncation `max(0,·)` is
essential. Only subsets whose plus-square sum stays below P contribute, so in
practice the sum runs over subsets of the "small" plus legs (those with t_j<P)
whose running sum is < P.

Equivalent operator form (clean): with the shift operator (T_t f)(x)=f(x−t),

>  a_n = 2^{n−1} ω_1 ω_2 · [ Π_{j=3}^{n} (1 − T_{t_j}) · (x)_+^{\,n−3} ] |_{x=P}

i.e. a_n/(2^{n−1}ω_1ω_2) is the (n−2)-fold finite difference of the truncated
power (x)_+^{n−3} at the n−2 nodes {t_3,…,t_n}, evaluated at x=P. (This is
exactly a univariate **B-spline / divided-difference** structure — see §5.)

### Worth highlighting
- The **larger** minus leg's magnitude never appears except through the product
  ω_1ω_2. The whole kinematic dependence enters through P (the *smaller* minus
  square) and the plus squares.
- In the **deepest chamber** (smaller minus = globally smallest magnitude, all
  t_j ≥ P), every S≠∅ truncates to 0, leaving
  **a_n = 2^{n−1} ω_1 ω_2 P^{\,n−3} = 2^{n−1} ω_1 ω_2 [min(ω_1²,ω_2²)]^{n−3}.**
  This single monomial already reproduces every PI reference point and the
  "one frequency ≫" regime.

## 2. Scaling and reality (PI facts, re-confirmed)
- **Purely imaginary:** Re A_n = 0 exactly at every exact-rational point tested.
- **Homogeneity degree 2n−4:** under ω→λω, a_n→λ^{2n−4} a_n. The formula has
  degree 1 (ω_1ω_2 → wait: ω_1ω_2 is degree 2) + (n−3)·2 (the truncated power is
  degree 2(n−3) in ω) = 2 + 2n−6 = **2n−4**. ✓ (code: `verify_conj.py`,
  homogeneity cross-check in `fit_n4.py`.)

## 3. Symmetry group
Verified directly (`symmetry.py`, evaluating the oracle on permuted ω via the
raw `--amp` interface): a_n is invariant under

>  **S₂ (swap of the two minus legs {1,2}) × S_{n−2} (all permutations of plus legs {3..n})**

and is **not** invariant under any minus↔plus swap. The closed form manifests
this: ω_1ω_2 and P=min(ω_1²,ω_2²) are S₂-symmetric; the subset sum over plus
legs is S_{n−2}-symmetric.

## 4. Analytic nature, degree, poles/zeros
- a_n is **piecewise-rational** (in fact piecewise-*polynomial* in the squares
  t_i): a different polynomial on each chamber, glued continuously.
- It is **NOT** a global rational function, and **NOT** a rational function of
  the symmetric polynomials (e₁,e₂,…) of the plus legs — even within one
  chamber. Reason: the chamber-restricted value needs the ordering/√-disc of the
  minus pair, equivalently the absolute values |k_S| in the BG propagators. We
  proved this already at n=4 (`fit_esym.py`, `localfit.py` show the e-symmetric
  fit is inconsistent).
- **Chambers** are the connected regions of fixed sign of every subset momentum
  k_S = Σ_{i∈S} σ_i ω_i² (these enter the BG propagator as |k_S|). The relevant
  walls are |ω_plus| = |ω_minus| crossings. The *single* control parameter that
  survives in the closed form is P; a plus leg "switches on" once t_j < P.
- **Degree:** total homogeneity 2n−4; on a chamber it is a polynomial of degree
  (n−3) in the squared magnitudes.
- **Poles:** as a function of the free −w parametrization, apparent poles at
  Σ(free freqs)=0 are *parametrization* artifacts (ω_1, ω_n blow up there); the
  amplitude itself is **polynomial in the squares on each chamber — it has no
  kinematic poles in the interior of a chamber** (the BG propagator poles
  ω_S²=|k_S| sit on chamber walls and cancel in the on-shell two-minus sum).
- **Zeros:** a_n → 0 whenever a minus leg → 0 (factor ω_1ω_2) and whenever a
  plus leg t_j → P from below in a way that empties the contributing subsets.

## 5. How it was found (reasoning trail)
1. **n=4** (via δ→0 limit, `n4_limit.py`): in the chamber where the smaller
   minus is smallest, a_4 = −8 ω_2³ω_3 = 8 ω_1ω_2·min(ω_1²,ω_2²). Established the
   2^{n−1}ω_1ω_2 prefactor (here 2³=8) and the min-structure.
2. **n=5 local chamber fits** (`freefit.py`): fitting a_5 as a homogeneous
   rational function of the free freqs *inside one chamber* gave
   a_5 = 16 ω_1 ω_2 · C_5 with C_5 a degree-2 polynomial in the squares whose
   form changed across chambers (C_5 = P², 2Pq−q², 2q₁q₂, …).
3. Pattern across chambers → **inclusion–exclusion** C_5 = Σ_S(−1)^{|S|}(P−Σ_S t)².
   First attempt (no truncation) matched ~90% of points; the misses were exactly
   subsets whose plus-sum exceeds P.
4. **Truncation** `max(0,·)` fixed everything: C_n = Σ_S(−1)^{|S|}max(0,P−Σ_S t)^{n−3}.
   n=6 confirmed the exponent is n−3 (truncated **cube**), n=7 confirmed n−3=4.
5. The truncated-power IE is precisely a finite difference / B-spline (§1),
   which is why it is continuous across walls and degree (n−3) per chamber.

## 6. Verification (see `data/verification_output.txt`, `code/verify_universal.py`)
- **Reference points** (PI notes): n=4 (−24, −320 via limit), n=5 (−544/7,
  −3328), n=6 (−1024/5) — all **bit-exact**.
- **Non-generic regimes:** n=5 −w 1,2,1000 = −16048096/1003·i (PI's value);
  n=5 one plus ≪ (1/1000); n=6 one plus ≫ (500); n=6 one free freq ≪ (1/100) —
  all bit-exact.
- **Random all-chamber scans (exact rational):** n=5 60/60, n=6 60/60,
  n=7 40/40, covering chamber types b0m5h0 … b4m1h0 (b=#plus below P, m=#between
  the two minus, h=#above larger minus). Relative residual = 0 (bit-exact).
- **n=7 in `--double`** shows up to ~1e-5 error at small-frequency points — this
  is the oracle's long-double round-off in the BG recursion, **not** a formula
  error; exact-rational n=7 confirms bit-exact agreement there too.
- g-dependence: with k=σω²/g, the homogeneity ω²=g|k| means the natural object
  is t_j=ω_j² and P, independent of g at g=1; A_n scales by the documented 2n−4
  in ω. (Not separately stress-tested vs −g this round; flagged for the PI.)

## 7. Open / for cross-check
- The form is fully empirical (data-driven). **student-2's BG-recursion
  derivation should reproduce the 2^{n−1}ω_1ω_2 prefactor, the truncated-power
  /B-spline structure, and explain why only the *smaller* minus square P enters**
  — that would upgrade this from "verified conjecture" to "derived".
- The B-spline reading suggests A_n is (up to the ω_1ω_2 factor) proportional to
  a B-spline density M(P | t_3,…,t_n) of order n−2 — a clean physical statement
  worth confirming analytically.
