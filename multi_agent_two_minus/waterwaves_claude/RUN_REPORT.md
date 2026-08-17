# Waterwaves run — what happened and what was found

*A human-readable account of the PI + 2-students run on the two-minus water-wave
amplitude benchmark (2026-06-23), the formula the group found, and the independent
verification done afterward.*

---

## 1. The question

Find a **closed-form formula** for the tree-level n-point on-shell scattering
amplitude `A_n` of 1D deep-water surface waves in the **two-minus sector**
(`σ = (−1,−1,+1,…,+1)` — legs 1,2 carry sign −1, the rest +1), valid for all
`n ≥ 4` and arbitrary in-sector kinematics. A supplied C++ "oracle" (`bg.cpp`, a
Berends–Giele evaluator, exact rational + fast double) computes the true amplitude
at any kinematic point. A formula passes only if it agrees with the oracle to
≤ 10⁻¹⁰ relative error at `n = 4,5,6,7` across multiple points, including
non-generic kinematics.

The bots were given **only** the task and the oracle, with a hard rule: **no web,
no literature, no external AI** — derive everything from the prompt, the code, and
data they generate. They ran on **Opus 4.8 (1M context) at xhigh effort**.

The team: a **PI** (orchestrator/verifier, does no original research) and two
identical **students** assigned tasks blindly by the PI each round. The run was
configured for 8 rounds but **stopped early after round 2** when the PI accepted a
verified formula.

---

## 2. What the group did, round by round

### Round 1 — PI orientation (post_001)

The PI built its own copy of the oracle and ran "orientation probes" to map the
terrain (shared as objective facts, not as a method to follow):

1. **`A_n` is purely imaginary** — `Re A_n = 0` everywhere, so write `A_n = i·a_n`
   with `a_n` real (rational at rational kinematics).
2. **Frequency scaling** — under `ω_i → λ ω_i`, `A_n → λ^{2n−4} A_n`; any formula
   must have homogeneity degree `2n−4`.
3. **n = 4 is singular in the oracle** — at n=4 the two on-shell constraints
   *force* `ω_1=−ω_3`, `ω_4=−ω_2`, which makes an internal Berends–Giele current a
   literal `0/0`. The oracle SIGFPEs (exact) / returns NaN (double) at the exact
   point. The value is finite and recovered by a **δ→0 limit**. This is the only
   way n=4 enters the pass bar.
4. Non-generic regimes (one frequency ≫ or ≪ the rest) are evaluable.
5. n=7 exact-rational is slow; `--double` is needed for speed.

The PI then assigned **two complementary tasks**: student-1 the *empirical/dataset*
path, student-2 the *analytic-derivation* path — both to converge on a single
testable closed form.

### Round 1 — student-2, the derivation path (post_002)

Ported the recursion to Python (exact rational + sympy symbolic), validated it
against `./bg`, and ran the Berends–Giele recursion **symbolically** at n=4 and n=5.
Results:

- **Principal-chamber formula:** `a_n = 2^{n−1} · ω_1 · ω_2^{2n−5}` — i.e.
  `a_4 = 8 ω_1 ω_2³`, `a_5 = 16 ω_1 ω_2⁵`. Striking feature: it depends *only* on
  the two minus-leg frequencies (with `ω_2` the smallest free frequency).
- **Derived** *why* `A_n` is purely imaginary (an i-parity argument: every current
  carries an even number of `i`'s; the lone root vertex contributes the single
  factor of `i`), and *why* n=4 is finite (the would-be pole cancels against a
  vanishing numerator — the off-shell amplitude is a polynomial).
- Flagged the gap: the true amplitude is **piecewise** (the `|k_S|` absolute values
  in the recursion create "chambers"); the monomial above is only the
  **principal chamber** (valid when the free minus leg is the smallest frequency).

### Round 1 — student-1, the empirical path (post_003)

Built a large exact-rational dataset and mined it. Local single-chamber fits at n=5
gave `16 ω_1 ω_2 ×` (degree-2 polynomial); the cross-chamber pattern then resolved
into a **truncated inclusion–exclusion** over subsets of the plus legs, with the
exponent confirmed as `n−3` (a cube at n=6, 4th power at n=7). The result — valid
in **every chamber**:

> `a_n = 2^{n−1} · ω_1 ω_2 · Σ_{S ⊆ {3..n}} (−1)^{|S|} · max(0, P − Σ_{j∈S} ω_j²)^{n−3}`,  with `P = min(ω_1², ω_2²)`.

Student-1 explicitly **cross-checked against student-2**: in the deepest (principal)
chamber every non-empty subset truncates to 0, and the formula collapses to
`2^{n−1} ω_1 ω_2 · P^{n−3} = 2^{n−1} ω_1 ω_2^{2n−5}` — *identical* to student-2's
derived monomial. So the two paths agreed, with student-1's form the general one.

### Round 2 — PI verifies and accepts (post_004, SOLVED.md)

The PI re-derived nothing on trust: it rebuilt its own oracle, wrote its own
exact-rational driver and formula evaluator (no student code imported), and did its
own δ→0 limit for n=4 (Neville extrapolation → exact −24, −320, −1512, −40).
Result: **142/142 points bit-exact** (residual identically 0), across
n = 4(limit),5,6,7 plus n=8 spot-checks — and crucially **95 of those points sit in
non-principal chambers** where the truncation actually fires, so the genuinely-new
all-chamber content was exercised. The PI wrote `summary/SOLVED.md` and stopped the
run.

### Round 2 — student-2, bonus theory (post_005)

With the question already solved, student-2 closed the two "open, not required"
items: (1) **g-dependence** — restoring gravity, `a_n(g) = g^{3−n} a_n(1)` (the ω's
and the formula structure are g-independent; verified bit-exact for g ∈ {1,2,3}),
derived by homogeneity counting of the engine; (2) **structure** — recognized the
subset sum as `[∏_j (1 − T_{t_j})] (x)_+^{n−3} |_{x=P}`, the (n−2)-fold finite
difference of a truncated power, i.e. a **univariate B-spline / divided difference**
of order `n−2`, and used that to prove (symbolically, n=4..7) the properties round 1
had only observed numerically.

---

## 3. The formula

With the sector `σ = (−1,−1,+1,…,+1)`, `g = 1`, legs 1,2 the minus legs, legs
3..n the plus legs, and `P = min(ω_1², ω_2²)`:

```
A_n = i · a_n
a_n = 2^(n−1) · ω_1 · ω_2 · Σ_{S ⊆ {3,…,n}} (−1)^|S| · [ max(0, P − Σ_{j∈S} ω_j²) ]^(n−3)
```

**Reading it:**
- It is **purely imaginary**, homogeneous of degree `2n−4` in the frequencies.
- The subset sum is the **(n−2)-fold finite difference of the truncated power
  `(x)_+^{n−3}`** at nodes `{ω_3²,…,ω_n²}`, evaluated at `x = P` — a B-spline.
- It is **piecewise-polynomial**: the `max(0,·)` truncation switches terms on/off as
  kinematics cross "chamber" walls; the formula is continuous across them.
- Only the **smaller** minus-leg square `P` enters the sum; the larger minus leg
  appears solely through the `ω_1 ω_2` prefactor.
- **Principal/deepest chamber** (smaller minus is the globally smallest magnitude):
  every non-empty subset truncates to 0 and `a_n = 2^{n−1} ω_1 ω_2^{2n−5}`.
- With gravity restored, multiply by `g^{3−n}`.

---

## 4. Independent verification (done separately, after the run)

I did **not** take the PI's "142/142" on trust. I re-verified from scratch:

- **Fresh oracle.** Compiled `bg` from the pristine canonical `bg.cpp` in an
  isolated scratch directory (not the bots' copies).
- **Fresh formula evaluator.** Re-implemented the formula in Python using exact
  rationals (`fractions.Fraction`), with no student/PI code imported.
- **Method.** For each test point I ran the oracle's on-shell solver
  (`./bg -n N -w … -s …`), parsed the full ω vector and `A_n` as exact rationals,
  computed `a_n` from the formula on that same ω, and required `Re A_n = 0` **and**
  `Im A_n == a_n` exactly (not just within 10⁻¹⁰).

**Results — n = 5, 6, 7: 15/15 exact matches** (relative residual identically 0),
covering generic points, **11 non-principal-chamber points** (where the truncation
genuinely fires), and extreme kinematics (a plus leg = 1000, and = 1/1000). Several
reproduced the PI's own reported values exactly, e.g. n=5 `[6,1,2] → −6400/3`,
n=6 `[7,1,2,3] → −3241728/13`, n=7 `[8,1,2,3,4] → −57016320`.

**n = 4.** As the PI noted, the oracle SIGFPEs at the exact on-shell point (a
genuine *removable* singularity — an internal current hits 0/0). I confirmed this,
then ran **my own δ→0 limit** with the raw `--amp` mode (perturbing so `Σω = 0` is
kept while the square constraint is relaxed by δ):

| δ-parameter ε | oracle Im(A₄) |
|---|---|
| 1/10   | −23.8821 |
| 1/100  | −23.99880 |
| 1/1000 | −23.999988 |
| 1/10000| −23.99999988 |

→ converges cleanly to **−24**, the formula's value. The formula also reproduces
all four of the PI's n=4 table values exactly (−24, −320, −1512, −40).

### Why I concluded the formula is correct

1. **Exactness, not tolerance.** Agreement is *bit-exact* in rational arithmetic at
   every n=5,6,7 point — the 10⁻¹⁰ bar is never even approached; the residual is
   literally 0. Floating-point coincidence is ruled out.
2. **The hard part was exercised.** The non-trivial content of the formula is the
   chamber structure (the truncated inclusion–exclusion). I tested points in
   **multiple non-principal chambers** where most subsets contribute non-zero —
   not just the easy principal-chamber monomial.
3. **Extreme kinematics pass.** Points with a frequency 1000× larger or smaller than
   the others — exactly where a wrong ansatz tends to break — match exactly.
4. **n=4 is consistent.** The oracle can't evaluate it directly, but my independent
   limit converges unambiguously to the formula's value, and the formula matches the
   PI's δ-limit table.
5. **Two independent derivations agree.** The analytic principal-chamber result
   (student-2, from the recursion) is exactly the principal-chamber limit of the
   empirical all-chamber form (student-1) — an internal cross-check the bots did and
   I re-confirmed.

### Honest caveats

- **n=4 rests on a limit**, not a direct oracle call (the on-shell point is singular
  in the oracle). The limit is clean, but it is a continuation.
- **No first-principles proof.** This is a *verified conjecture*: fit + structural
  reasoning + exhaustive exact numerical agreement. Student-2 derived the
  principal-chamber monomial from the recursion and proved the B-spline *properties*
  for n=4..7, but nobody proved the full recursion telescopes to this B-spline form
  for general n. For this benchmark's pass criterion that is a pass; it is not yet a
  theorem.

---

## 5. Ground-truth comparison (added after §1–4 were written)

Sections 1–4 above were written from the bots' own artifacts and my independent
re-verification — the latter done in earlier turns, before the benchmark answer key
was ever consulted. Only then did I open the benchmark key
(`waterhedron-benchmark/KEY.md`). The official ground truth:

```
A_n = i · w1 · w2 · 2^(n−1) · Σ_{S ⊆ {3..n}} (−1)^|S| · max(0, β² − Σ_{i∈S} w_i²)^(n−3),   β = min(|w1|, |w2|)
```

This is **term-for-term identical** to the formula the group found and I verified:
`β² = min(|w1|,|w2|)² = min(w1², w2²) = P`. So the group recovered the exact
"waterhedron" closed form. **Correct.**

Two notes from the key worth recording:

- **The run was the "no-hint" condition.** Our `question.md` gave the task and the
  oracle with *no* structural guidance (no mention of chambers, piecewise structure,
  or poles). The key confirms this corresponds to the benchmark's neutral/no-hint
  case — the group discovered the chamber/piecewise structure entirely on its own.
- **The group did the opposite of the benchmark's "anti-hint" trap.** One benchmark
  condition deliberately steers agents toward a *wrong* picture — "A_n is a single
  global rational function with poles, no chambers, not a polynomial; fit one global
  ansatz on generic points and avoid hierarchical regimes." Our bots, unprompted,
  found the chambers, recognized it as piecewise-polynomial (not a global rational),
  and specifically stress-tested the hierarchical/non-generic regimes the anti-hint
  says to avoid — exactly the right instincts.

---

## 6. Cost and compute

The run was **Opus 4.8 (1M context) at xhigh effort**. Per-session **durations**
come from the `Starting…`/`exited…` timestamps the runner already wrote to each
`logs/<bot>/<ts>.log`. Token usage was *not* logged at the time, but Claude Code
keeps full per-session transcripts, so the **token** numbers below were recovered
from those and priced at current Opus 4.8 list rates. (The runner now logs both
automatically — see the end of this section.)

### What the four token types mean

Every API turn is billed in four buckets, each at a different rate:

| Token type | What it is | Rate (Opus 4.8) |
|---|---|---|
| **Output** | Tokens the model *generates* — its reasoning, text, and tool calls. The expensive one. | $25 / million |
| **Input (uncached)** | Fresh tokens the model *reads* that aren't already cached — e.g. a brand-new prompt. Full price. | $5 / million |
| **Cache write** | The first time a chunk of prompt is sent, it's stored in a short-lived cache so later turns don't re-pay full price. A one-time ~1.25× surcharge. | $6.25 / million |
| **Cache read** | On every later turn, the unchanged earlier prompt is served *from* that cache at a 90%-discount. | $0.50 / million |

Opus 4.8 has **no long-context premium** — these flat rates apply across the
entire 1M-token window.

### Why cache-read is 33 million tokens when the window is only 1 million

This is the part that looks paradoxical, and it's worth understanding. The API
is **stateless**: it has no memory between turns, so on *every* turn the entire
conversation-so-far is re-sent as input. A session with hundreds of turns
re-sends the growing transcript hundreds of times.

Prompt caching is what makes that affordable: the repeated prefix is served as
**cache-read** (at 1/10th the price) instead of being re-charged at full input
rate. Crucially, **`cache_read` is a running total across all turns, not a
snapshot of how big the context is.** It sums every re-read of the cached prefix
over the whole session.

Concretely, student-1's Round 1 ran **219 turns** and logged **33.2M** cache-read
tokens — that's `33.2M ÷ 219 ≈ 151,000` tokens re-read per turn. So the context
grew to about 150K tokens (well under the 1M window) and was re-read ~219 times.
No single request came close to the window limit; the 33M is 219 cheap re-reads
of a ~150K context, not one impossibly-large prompt.

### Per-session timing and cost

| Round | Bot | Duration | Turns | Output | Cache-read | Cache-write | Uncached in | Cost (≈) |
|---|---|--:|--:|--:|--:|--:|--:|--:|
| 1 | PI | 7.0 min | 58 | 88,232 | 2,529,603 | 162,524 | 26,352 | $4.62 |
| 1 | student-1 | **58.0 min** | 219 | 639,207 | 33,159,174 | 756,702 | 23,658 | **$37.41** |
| 1 | student-2 | 37.7 min | 141 | 469,002 | 17,590,662 | 658,500 | 15,240 | $24.71 |
| 2 | PI | 7.8 min | 67 | 82,841 | 4,084,475 | 293,076 | 20,672 | $6.05 |
| 2 | student-1 | 1.8 min | 19 | 26,911 | 484,694 | 116,851 | 18,872 | $1.74 |
| 2 | student-2 | 13.0 min | 72 | 165,514 | 5,415,184 | 291,595 | 13,947 | $8.74 |
| | **Total** | **125 min (sum)** | **576** | **1,471,707** | **63,263,792** | **2,279,248** | **118,741** | **≈ $83.26** |

### Timing (wall-clock)

The run started **2026-06-23 21:27 UTC** and finished around **23:53 UTC** —
about **2h 26m end-to-end**, but most of that is the fixed 60-minute sleep
between rounds, not compute. Each round runs the **PI first, then the two
students in parallel**, so a round's wall-clock is `PI + max(student-1,
student-2)`, not the sum:

- **Round 1:** PI 7.0 min, then students in parallel → gated by student-1 at
  **58 min** ≈ **65 min** of compute.
- **60-minute sleep** between rounds.
- **Round 2:** PI 7.8 min, then students in parallel → gated by student-2 at
  13 min ≈ **21 min** of compute.

So ~86 min was actual model work and ~60 min was the idle interval. The "125 min
(sum)" in the table adds up all six sessions and therefore double-counts the
parallel student time — the real compute wall-clock is ~86 min. Note also the
rough correlation between duration, turn count, and cost: student-1's 58-minute /
219-turn Round 1 is both the longest session and the most expensive, because each
of those turns re-read the growing context (the cache-read effect above).

Where the ~$83 went: **$36.79** output · **$31.63** cache-read · **$14.25**
cache-write · **$0.59** uncached input. Two observations: (1) the long, iterative
student-1 Round 1 session dominates the bill (and is where the formula was
actually discovered); (2) cache-read, despite being the cheapest per-token rate,
is the second-largest line item purely because of its 63M volume — the cost of
running many turns over a large shared context.

> **Caveat:** this is the *equivalent API list-price cost*. These runs went
> through a Claude subscription via `claude -p`, so the out-of-pocket cost may
> differ from the dollar figure above.

### Recording this automatically going forward

`run_bot.sh` now launches each bot with `--output-format json` and writes a
per-session `logs/<bot>/<timestamp>.json` plus a `[usage] cost_usd=… in=… out=…
cache_read=… cache_write=…` line into the log — so future runs report their own
cost and tokens without needing to reconstruct from transcripts.
