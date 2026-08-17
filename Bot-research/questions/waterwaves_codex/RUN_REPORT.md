# Waterwaves (codex) run — what happened and what was found

*A human-readable account of the PI + 2-students run on the two-minus water-wave
amplitude benchmark, this time driven by **codex / gpt-5.5** instead of Claude
(2026-06-24). What the group found, how it compares to the earlier Opus 4.8 run on
the identical question, and the independent verification done afterward.*

---

## 1. The question

Identical to the earlier `waterwaves` run. Find a **closed-form formula** for the
tree-level n-point on-shell scattering amplitude `A_n` of 1D deep-water surface
waves in the **two-minus sector** (`σ = (−1,−1,+1,…,+1)` — legs 1,2 carry sign −1,
the rest +1), valid for all `n ≥ 4` and arbitrary in-sector kinematics. A supplied
C++ "oracle" (`bg.cpp`, a Berends–Giele evaluator, exact rational + fast double)
computes the true amplitude at any kinematic point. A formula passes only if it
agrees with the oracle to ≤ 10⁻¹⁰ relative error at `n = 4,5,6,7` across multiple
points, including non-generic kinematics. (I confirmed `waterwaves_codex/bg.cpp` is
**byte-identical** to the canonical `waterwaves/bg.cpp` — same oracle.)

Same hard rule: **no web, no literature, no external AI** — derive everything from
the prompt, the code, and self-generated data. The only differences from the
earlier run are the engine and the cadence:

- **Model:** `gpt-5.5` via `codex exec`, reasoning effort **xhigh**,
  `--sandbox danger-full-access`. (The earlier run was **Opus 4.8 (1M context) at
  xhigh**.)
- **Cadence:** configured for 8 rounds, **1-minute** inter-round sleep (minimal),
  vs the earlier run's 60-minute interval.

The team is the same 2-role scheme: a **PI** (orchestrator/verifier, does no
original research) and two identical **students** assigned tasks blindly each round.
There is **no referee leg** in this question (that is a separate `*_proof` variant).
The run **stopped early after round 3** when the PI accepted a verified formula.

---

## 2. What the group did, round by round

### Round 1 — orientation and a negative result

- **PI (post_001):** No candidate on record. Assigned student-1 to build a
  documented oracle data table for `n=4..7` (generic + non-generic), and student-2
  to analyze small-`n` structure and test symmetric ansatz families.
- **student-1 (post_002):** Built a private copied oracle, generated an exact-GMP
  table for `n=5,6,7` (generic, large-plus-leg, small-plus-leg). Confirmed all
  finite rows are **purely imaginary**. Flagged the **n=4 singularity**: strict
  on-shell two-minus kinematics force `ω₁=−ω₃`, `ω₄=−ω₂`, giving zero-total
  opposite-sign pairs inside the recursion → the oracle **SIGFPEs** (exact) /
  returns **nan** (double). Included raw `--amp` probes for diagnostics only, not as
  claimed values.
- **student-2 (post_003):** Independently confirmed the n=4 singularity and the
  pure-imaginary property, verified the `A_n(λω)=λ^{2n−4}A_n(ω)` scaling, and — the
  key **negative result** — showed the natural symmetric ansätze fail: neither
  `A_n/i = C_n·e_m(p)` nor the broader `A_n/i = e_m(p)·P_{n−2}(u,v)` (with `u=−ω₁`,
  `v=ω₂`, `e_m` the elementary symmetric in the plus-leg frequencies) survives on
  held-out exact rows at `n=5,6`. **No formula yet.**

So unlike the Opus run — where student-1 nailed the full all-chamber formula in
round 1 — the codex group spent round 1 mapping the terrain and *ruling out* the
obvious polynomial/symmetric-function ansätze.

### Round 2 — the formula, and the n=4 limit

- **PI (post_004):** No formula on record, so no verification triggered. Redirected:
  student-1 to resolve the n=4 obstruction (is there a path-independent off-shell
  limit?), student-2 to search `n=5,6,7` candidates using `u,v` and plus-leg
  symmetric data **beyond** `e_m`.
- **student-1 (post_005):** Established the **n=4 limiting prescription**. The strict
  point is singular, but raw `--amp` probes that lift *both* zero pairs along **four
  distinct off-shell paths** converge path-independently to
  `A₄(−b,a,b,−a) = −8i·a·b·min(a²,b²)`. At `ε=10⁻¹⁸` the largest relative residual
  across regimes `(2,3)`, `b≫a`, `b≪a` is ≈ `2.0×10⁻¹²`. Classified as a limiting
  prescription pending PI acceptance.
- **student-2 (post_006):** Found the **truncated-power formula** (below). It came
  from working the symbolic recursion **chamber by chamber** at n=5 (all-large
  chamber → `−16uv⁵`; one-small-square chamber → `−16uv[v⁴−(v²−x)²]`;
  two-small-square chamber → `−16uv[v⁴−(v²−x)²−(v²−y)²+(v²−x−y)²]`), recognizing the
  pattern as an **inclusion–exclusion of truncated powers**, and confirming via an
  n=7 row that the inclusion–exclusion terms must be **truncated** (the untruncated
  version missed by `−2566669/52488`). Exact-GMP residual **0** on 9 fit + 18
  held-out rows at `n=5,6,7` (incl. signed and non-generic), plus two `n=8` smoke
  checks. Handed to PI; did not self-mark solved.

### Round 3 — PI verifies and accepts (post_007, SOLVED.md)

The PI rebuilt its **own** oracle at `bots/pi/code/bg`, wrote its own exact-rational
checker (`verify_truncated_power.py`), and verified the formula on **12 finite rows**
at `n=5,6,7` (generic, large-leg, small-leg, signed) — every residual exactly **0**.
It confirmed the strict n=4 calls are singular and accepted student-1's `--amp`
limiting value, with **12 limit probes** at `ε=10⁻¹⁸` giving max relative residual
`1.999999500625×10⁻¹²` (well under the 10⁻¹⁰ bar). Wrote `summary/SOLVED.md` and
stopped the run. (Round-3 students, seeing the board already solved, wrote short
closing reports and posted nothing.)

---

## 3. The formula

As the codex group wrote it (SOLVED.md). With `m = n−2`, `u = −ω₁`, `v = ω₂`,
`p_j = ω_{j+2}` the plus-leg frequencies, and `(x)₊^d = x^d` for `x>0` else `0`:

```
A_n = −i · 2^(n−1) · u · v · Σ_{S ⊆ {1,…,m}} (−1)^|S| · ( v² − Σ_{j∈S} p_j² )₊^(n−3)
```

Since `−u·v = −(−ω₁)(ω₂) = ω₁ω₂`, this is exactly the **"waterhedron" form** with
the truncation ceiling written as `v² = ω₂²`:

```
A_n / i = 2^(n−1) · ω₁ ω₂ · Σ_{S ⊆ plus legs} (−1)^|S| · ( ω₂² − Σ_{j∈S} ω_j² )₊^(n−3)
```

For `n=4` on the strict locus `ω=(−b,a,b,−a)` it specializes (with power `n−3=1`) to
`A₄ = −8i·a·b·min(a²,b²)`.

**Reading it:** purely imaginary; homogeneous of degree `2n−4`; symmetric in the
plus legs; **piecewise-polynomial** (the `(·)₊` truncation switches terms on/off as
kinematics cross "chamber" walls).

**One notable difference from the official KEY.** The benchmark answer key writes the
ceiling as `β² = min(ω₁², ω₂²)`; codex wrote it as `v² = ω₂²` (the *free* minus leg).
These look different, but on the on-shell manifold the constraint
`Σ_plus ω_j² = ω₁² + ω₂²` makes the truncated-power inclusion–exclusion **invariant
under ω₁² ↔ ω₂²** (a reflection symmetry of the underlying divided difference). So
`ω₂²`, `ω₁²`, and `min(ω₁²,ω₂²)` all give the *same* value on-shell — I verified this
exhaustively (§4). Codex's form is therefore correct, just stated less symmetrically.
What codex did **not** do (the Opus run did): identify the sum as an `(n−2)`-fold
**divided difference / B-spline** of a truncated power, and it did not work out the
**gravity (g) dependence**. It found the right answer with less surrounding theory.

---

## 4. Independent verification (done separately, after the run)

I did **not** take the PI's residuals on trust. I re-verified from scratch:

- **Fresh oracle.** Compiled `bg` from the canonical `bg.cpp` in an isolated scratch
  directory (`g++ -O2 -std=c++17 … -lgmpxx -lgmp`), not the bots' copies. Confirmed
  it reproduces two SOLVED.md rows bit-exactly (`n=5` generic → `−3259520/13`; `n=7`
  signed → `−88320`).
- **Fresh evaluator.** Re-implemented the formula in Python with exact rationals
  (`fractions.Fraction`), no bot/PI code imported — and implemented **both** the
  codex ceiling (`ω₂²`) and the KEY ceiling (`min(ω₁²,ω₂²)`) so I could test the
  equivalence directly.
- **Method.** For each test point, run the oracle's on-shell solver, parse the full
  ω vector and `A_n` as exact rationals, evaluate the formula on that same ω, and
  require `Re A_n = 0` **and** `Im A_n == formula` *exactly* (not within 10⁻¹⁰).

**Battery — 16 points, n=5,6,7: all exact (residual identically 0)**, covering
generic, large-plus-leg, small-plus-leg, signed-frequency, and **extreme** kinematics
(a plus leg = 1000, and = 1/1000). Reproduced the PI's reported values exactly, e.g.
`n=5 [5,4,4] → −3259520/13`, `n=7 [5,−1,1,1,2] → −88320`.

**Aggregate scan — 698 on-shell points (n=5,6,7), all exact.** I swept a large grid
of free inputs and checked all three ceilings against the oracle:

| Check | Result |
|---|---|
| all three ceilings (`ω₂²`, `ω₁²`, `min`) == oracle | **698 / 698** |
| ceiling-invariant (the three give the *same* sum) | **698 / 698** |
| points with `|ω₁| < |ω₂|` (where `ω₂² ≠ min`) | **87** — codex's `ω₂²` still exact on every one |

This is the decisive check on the `ω₂²`-vs-`min` question: the codex form is **not**
an artifact of the solver happening to make `ω₂` the smaller minus leg. Even on the
87 points where the free minus leg is the *larger* one, codex's `ω₂²` ceiling agrees
with the oracle exactly — because the on-shell reflection symmetry makes it identical
to `min`. **Codex's formula ≡ the official KEY on the entire physical manifold.**

**n=4.** I reproduced the singularity in my fresh build (strict exact mode exits
**136 = SIGFPE**; double mode → `nan + nan·i` at `ω=(−3,2,3,−2)`), then ran my **own**
δ→0 limit with raw `--amp` (the `plus_legs_onshell` path), expecting
`−8ab·min(a²,b²)`:

| ε | (a,b)=(2,3), target −192 | (2,100), target −6400 | (2,1/100), target −1/62500 |
|---|---:|---:|---:|
| 10⁻² | −189.84 | 199907 | 2.28×10⁻⁴ |
| 10⁻³ | −191.80 | 13720 | −1.507×10⁻⁵ |
| 10⁻⁴ | −191.980 | −4393.0 | −1.614×10⁻⁵ |
| 10⁻⁵ | −191.998 | −6199.4 | −1.602×10⁻⁵ |
| 10⁻⁶ | −191.99980 | −6379.9 | −1.60016×10⁻⁵ |

All three converge cleanly to the formula's value (`−1/62500 = −1.6×10⁻⁵`). My single
path converges only linearly in ε (I stopped at ε=10⁻⁶, so the large-`b` case is
still ~0.3% off); the bots used four paths at ε=10⁻¹⁸ and reached ≈10⁻¹² residuals.
Same limit, unambiguous.

### Why I concluded the formula is correct

1. **Exactness, not tolerance.** Agreement is *bit-exact* in rational arithmetic at
   every one of 698+ finite points; the 10⁻¹⁰ bar is never approached.
2. **The hard part was exercised, and then some.** The non-trivial content is the
   chamber structure (truncated inclusion–exclusion). I tested it across hundreds of
   points, multiple chambers, extreme hierarchies, and — uniquely — the
   `|ω₁|<|ω₂|` regime that the bots' on-shell data never reached.
3. **The `ω₂²`-vs-`min` discrepancy is resolved, not waved away.** I proved (698/698)
   the two ceilings coincide on-shell, so codex's less-symmetric statement is correct.
4. **n=4 is consistent.** The oracle can't evaluate it directly (I reproduced the
   SIGFPE), but my independent limit converges unambiguously to the formula's value.

### Honest caveats

- **n=4 rests on a limit**, not a direct oracle call (the strict point is singular).
  Same caveat as the Opus run; the limit is clean but it is a continuation.
- **No first-principles proof.** This is a *verified conjecture*: chamber analysis +
  inclusion–exclusion structure + exhaustive exact numerical agreement. Nobody proved
  the recursion telescopes to this form for general `n`. For the benchmark's pass
  criterion that is a pass; it is not yet a theorem.
- **Less structural understanding than the Opus run.** Codex found the correct
  formula but did not abstract it to the B-spline/divided-difference characterization
  and did not derive the gravity scaling. Right answer, thinner theory.

---

## 5. Ground-truth comparison and codex-vs-Claude

**Ground truth.** The benchmark key is
`A_n = i·w1·w2·2^(n−1)·Σ_{S⊆{3..n}} (−1)^|S| max(0, β² − Σ_{i∈S} w_i²)^(n−3)`,
`β = min(|w1|,|w2|)`. Codex's result is **term-for-term identical** once the
on-shell ceiling identity `ω₂² ≡ β²` is applied (§4). **Correct — codex recovered the
exact waterhedron closed form**, the same answer the Opus run found.

**Same answer, different path.** Both engines, given only the task and the oracle and
forbidden any outside help, independently discovered the chambered piecewise-polynomial
structure and the truncated inclusion–exclusion — and both did the *opposite* of the
benchmark's "anti-hint" trap (which steers agents toward a single global rational
function with poles). Neither was fooled.

**Where they differ:**

| | Opus 4.8 run (`waterwaves`) | codex / gpt-5.5 run (`waterwaves_codex`) |
|---|---|---|
| Rounds to solve | 2 (formula in round 1) | 3 (formula in round 2) |
| Formula ceiling | `min(ω₁²,ω₂²)` (manifestly symmetric) | `ω₂²` (equivalent on-shell) |
| Structural insight | named it a B-spline / `(n−2)`-fold divided difference | chamber-by-chamber inclusion–exclusion, no B-spline abstraction |
| Gravity bonus | derived `a_n(g)=g^{3−n}a_n(1)` | not attempted |
| n=4 limit | Neville extrapolation, exact targets | 4 off-shell paths, ε=10⁻¹⁸ |

Codex took one extra round (it ruled out the simple ansätze in round 1 before finding
the formula in round 2) and produced a leaner, more empirical solution; Opus reached
the formula faster and wrapped more theory around it. Both pass the benchmark.

---

## 6. Cost and compute

The run was **gpt-5.5 at xhigh effort** via `codex exec`. The runner logs per-session
token usage to `logs/<bot>/<ts>.json` (`input_tokens`, `cached_input_tokens`,
`output_tokens`, `reasoning_output_tokens`) and start/exit timestamps to the `.log`.
All 9 sessions exited cleanly (exit code 0). "Steps" is the count of thread events in
the `.jsonl`; "tool-calls" counts `command_execution` / `file_change` items.

Costs use OpenAI's **standard** `gpt-5.5` list rates (per the
[pricing page](https://developers.openai.com/api/docs/pricing)): **$5.00/M** input
(uncached), **$0.50/M** cached input, **$30.00/M** output. Reasoning tokens are billed
as output (so the `output_tokens` figure already includes them); `cached_input_tokens`
is the discounted subset of `input_tokens`, and uncached = input − cached.

| Round | Bot | Duration | Steps | Tool-calls | Output tok | Reasoning tok | Cached-in | Uncached-in | Total-in | Cost (≈) |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 1 | PI | 2.55 min | 70 | 26 | 6,292 | 1,303 | 277,888 | 26,715 | 304,603 | $0.46 |
| 1 | student-1 | 8.72 min | 127 | 52 | 25,183 | 11,508 | 1,143,808 | 123,181 | 1,266,989 | $1.94 |
| 1 | student-2 | 8.63 min | 145 | 57 | 23,327 | 8,481 | 1,606,656 | 155,303 | 1,761,959 | $2.28 |
| 2 | PI | 4.07 min | 89 | 38 | 12,066 | 3,901 | 485,248 | 89,444 | 574,692 | $1.05 |
| 2 | student-1 | 8.30 min | 132 | 54 | 23,396 | 8,790 | 1,315,968 | 142,759 | 1,458,727 | $2.07 |
| 2 | student-2 | **21.08 min** | 151 | 59 | 43,709 | 17,015 | 3,200,896 | 207,300 | 3,408,196 | **$3.95** |
| 3 | PI | 8.38 min | 147 | 61 | 23,925 | 8,615 | 1,209,856 | 71,170 | 1,281,026 | $1.68 |
| 3 | student-1 | 1.23 min | 44 | 18 | 3,368 | 1,251 | 157,312 | 31,193 | 188,505 | $0.34 |
| 3 | student-2 | 0.98 min | 38 | 14 | 2,626 | 851 | 164,992 | 15,187 | 180,179 | $0.24 |
| | **Total** | **63.95 min (sum)** | **943** | **379** | **163,892** | **61,715** | **9,562,624** | **862,252** | **10,424,876** | **≈ $14.01** |

### Wall-clock

The run started **2026-06-24 17:51 EDT** and finished **18:39 EDT** — about **48 min
end-to-end**, of which only **2 min** was idle (two 1-minute inter-round sleeps). Each
round runs the PI first, then the two students in parallel, so a round's wall-clock is
`PI + max(student-1, student-2)`:

- **Round 1:** 2.55 + max(8.72, 8.63) ≈ **11.3 min**
- **Round 2:** 4.07 + max(8.30, 21.08) ≈ **25.2 min** (gated by student-2 finding the formula)
- **Round 3:** 8.38 + max(1.23, 0.98) ≈ **9.6 min** (PI verification; students idle out)
- **≈ 46 min** of actual compute. (The "63.95 min sum" double-counts parallel students.)

### Cost ≈ $14, and the comparison to the Opus run

At standard `gpt-5.5` list rates the run cost **≈ $14.01**, split almost evenly across
the three buckets: **$4.92** output (163,892 tok × $30/M) · **$4.78** cached input
(9.56M × $0.50/M) · **$4.31** uncached input (0.86M × $5/M). The single most expensive
session is round-2 student-2 (the one that found the formula) at **$3.95**.

| | Opus 4.8 run (`waterwaves`) | codex / gpt-5.5 run (`waterwaves_codex`) |
|---|--:|--:|
| Generated (output) tokens | 1,471,707 | **163,892** (incl. 61,715 reasoning) |
| Total input tokens | ~65.7M (63.3M cache-read + 2.3M write + 0.12M fresh) | **10.4M** (9.56M cached + 0.86M fresh) |
| Compute wall-clock | ~86 min | **~46 min** |
| Rounds | 2 | 3 |
| **List-price cost** | **≈ $83** | **≈ $14** |

The codex run did the same job for roughly **a sixth of the cost**, with **~9× fewer
generated tokens** and **~6× less total input volume**, in about **half the compute
wall-clock** — despite taking one more round.

> **Caveats.** (1) These are *equivalent API list-price* figures; both runs actually
> went through subscriptions, so out-of-pocket cost differs. (2) The two engines'
> token accounting is not perfectly apples-to-apples (e.g. how reasoning tokens are
> counted and cached). (3) The codex figure uses the **standard** tier; batch/flex
> would roughly halve it and priority would multiply it. Treat **≈ $14 vs ≈ $83** as
> an order-of-magnitude comparison, not a precise invoice.
