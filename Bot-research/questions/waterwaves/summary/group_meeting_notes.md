# Group meeting notes — waterwaves (two-minus sector A_n)

## Round 1 — 2026-06-23T21:27:36 (PI kickoff)

This is the opening session. No prior student work existed. The PI built its own
copy of the oracle (`bots/pi/code/bg.cpp`, built with the documented line) and ran
a set of orientation probes. The facts below are **objective measurements from the
oracle**, reproducible by anyone; they are shared so we don't each rediscover them.
They are NOT the answer and NOT a prescribed method — just the lay of the land.

### Verified empirical facts (two-minus sector, σ = (−1,−1,+1,…,+1))

1. **A_n is purely imaginary.** At every in-sector point tested (n = 5,6,7 exact
   rational; n = 4 by limit), `Re A_n = 0` exactly. Write `A_n = i · a_n` with
   `a_n` real (rational at rational kinematics). So the real target is the rational
   function `a_n({ω})`.

2. **Overall frequency scaling dimension = 2n − 4.** Under `ω_i → λ ω_i` (all
   legs), `A_n → λ^{2n−4} A_n`. Verified: n=5 scales as λ⁶ (factor 64 at λ=2),
   n=6 as λ⁸ (factor 256 at λ=2). With g=1 fixed this is the homogeneity degree;
   any candidate must have this degree in the ω's. (Note g carries dimension too —
   `ω² = g|k|` — so worth checking g-dependence separately if you vary `-g`.)

3. **n = 4 is finite but the oracle cannot evaluate it at the on-shell point.**
   The two on-shell constraints (Σω=0, Σσω²=0) at n=4 two-minus *force*
   `ω_1 = −ω_3` and `ω_4 = −ω_2` (unique, proven algebraically — it's the whole
   2-parameter solution variety). That makes the internal Berends–Giele current on
   the subset {2,4} hit `wS = 0`, `kS = 0` simultaneously → a literal `0/0` in
   `Propagator`. Result: exact mode **SIGFPEs (exit 136)** and `--double` returns
   **NaN** at the exact point. BUT the value is finite: approaching along Σω=0 with
   the square-constraint relaxed by δ gives a clean limit.
   - Reference: ω = (−5, 2, 5, −2) → **A_4 = −320 i**.
   - Reference: ω = (−3, 1, 3, −1) → **A_4 = −24 i**.
   To get n=4 numbers: pick ω_2, ω_3, set ω_1=−ω_3, ω_4=−ω_2, perturb
   ω_4 → −ω_2+δ and ω_1 → −(ω_2+ω_3+ω_4) (keeps Σω=0), evaluate via
   `./bg --amp [--double] -K <σ_i ω_i²> -W <ω_i>` for several small δ, and
   extrapolate δ→0 (Richardson / rational δ both work). **A correct closed-form
   A_n should reproduce these n=4 values directly** — that is how n=4 enters the
   pass bar.

4. **Non-generic regimes are evaluable** (no singularity when one freq ≫/≪ rest):
   e.g. n=5 `-w 1,2,1000` → A_5 = −16048096/1003 · i (finite). Use these for the
   "one frequency ≫ or ≪ the others" pass-bar points.

### Reference values (exact rational, A_n = i · a_n) — verification targets

| n | `-w` (free freqs) | full ω (in order) | a_n |
|---|---|---|---|
| 4 | 1,3 (limit) | (−3, 1, 3, −1) | −24 |
| 4 | 2,5 (limit) | (−5, 2, 5, −2) | −320 |
| 5 | 1,2,4 | (−34/7, 1, 2, 4, −15/7) | −544/7 |
| 5 | 2,3,5 | (−13/2, 2, 3, 5, −7/2) | −3328 |
| 6 | 1,2,3,4 | (−32/5, 1, 2, 3, 4, −18/5) | −1024/5 |

Caveat on the `-w` parametrization: free freqs fill ω_2 … ω_{n−1}; ω_1 and ω_n are
solved from the constraints. **ω_2 is a minus leg** (σ_2 = −1), so reordering the
`-w` list is NOT a pure plus-leg permutation — it changes which leg is minus and
changes the amplitude. Treat symmetry carefully.

### Oracle / verification protocol
- Build (your own copy): `g++ -O2 -std=c++17 -I/opt/homebrew/include
  -L/opt/homebrew/lib -o bg bg.cpp -lgmpxx -lgmp`.
- Exact rational is feasible and fast through n ≈ 6; **n = 7 exact is slow** — use
  `--double` (long double) for n=7, which comfortably reaches ≤ 10⁻¹⁰ relative
  error. Report relative residuals, not absolute.
- Any candidate formula must be checked vs `./bg` at n = 4 (via limit), 5, 6, 7,
  multiple points each, including a ≫/≪ regime, to ≤ 10⁻¹⁰.

## Round 2 — 2026-06-23T23:37:56 (PI: SOLVED)

Both round-1 candidates landed and converged. **student-2** derived the
principal-chamber form `a_n = 2^{n−1} ω₁ ω₂^{2n−5}` from the BG recursion (valid
when the free minus leg is the smallest free frequency). **student-1** generalized
it empirically to the **all-chamber** closed form

> `A_n = i · 2^{n−1} · ω₁ ω₂ · Σ_{S⊆{3..n}} (−1)^{|S|} · max(0, P − Σ_{j∈S} ω_j²)^{n−3}`,  `P = min(ω₁²,ω₂²)`,

which reduces to student-2's monomial in the deepest chamber.

**PI independently verified and ACCEPTED student-1's universal formula.** Own
oracle (`bots/pi/code/bg`, identical to canonical `bg.cpp`), own exact-rational
driver + formula evaluator (`bots/pi/code/pi_round2_verify.py`, no student code
imported), own δ→0 limit for n=4 (raw `--amp` + exact Neville extrapolation →
exact −24, −320, −1512, −40). **142/142 points bit-exact (residual ≡ 0)** across
n = 4(limit),5,6,7 (+ n=8 spot-checks); **95 points in non-principal chambers**
where the truncation fires, so the new all-chamber content was exercised. Used
exact rational throughout (`./bg --double` loses ~10⁻⁵ at extreme n=7 freqs). See
`summary/SOLVED.md`, `bots/pi/code/pi_verification_output.txt`, `board.json`
post_004. **Run complete — no further tasks assigned.**
