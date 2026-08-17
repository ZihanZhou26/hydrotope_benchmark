# Waterwaves THREE-minus run — what happened and what was found

*A human-readable account of the PI + 2-students run on the **three-minus** water-wave
amplitude problem (2026-06-26 → 06-27). Unlike the two-minus benchmark, this is a genuine
open research problem with no known closed form. The run reached n=5 and the full n=6 closed
form (both PI-verified exact) and mapped the n≥7 structure, but did **not** close the single
all-n formula — so it ended after all 8 rounds with **no `summary/SOLVED.md`**.*

---

## 1. The question

Find a closed-form analytic formula for the tree-level n-point on-shell amplitude `A_n` of 1D
deep-water surface waves in the **three-minus sector** `σ = (−1,−1,−1,+1,…,+1)` (legs 1,2,3
carry σ = −1; legs 4…n carry σ = +1), valid for all `n ≥ 5`, verified against the bundled
exact Berends–Giele oracle `bg.cpp` to ≤ 10⁻¹⁰ (exact where the oracle is exact).

The team was given, as starting points (in `question.md`): the two neighbouring sectors —
**one-minus vanishes** (`A_n ≡ 0`) and the known **two-minus closed form** (the truncated-power
"waterhedron" law) — plus a human **plus/minus swap hint**: flipping every sign `k_i → −k_i`
maps the k-minus sector to the (n−k)-minus sector, so at **n=5** three-minus equals two-minus
at the swapped point. The prompt explicitly **allowed web/literature and the Typhon cluster**,
unlike the closed-book two-minus run. It ran on **Opus 4.8 (1M context) at xhigh effort**: a
**PI** (orchestrator/verifier) and two **students** assigned tasks each round, configured for
**8 rounds, 0-minute interval** (back-to-back).

---

## 2. A false start — and the fix (provenance)

The **first** launch misfired and was aborted. The bots run headless with
`--dangerously-skip-permissions` and were launched with a bare *relative* instruction
("Read `prompts/pi-bot.md`…"). With the threem folder brand-new/empty and the **in-progress
`waterwaves_proof` task sitting next door** (same physics — it proves the two-minus formula),
the PI and one student resolved that ambiguity by wandering into `waterwaves_proof` and
working *that* task instead; they even wrote bogus "round-5" artifacts into it. One student
correctly stayed on three-minus. The run was killed, the proof directory was cleaned of the
intrusion, and the launcher was **hard-bound**: it now passes each bot the *absolute* task
path with an explicit "operate only inside this directory; ignore every other `questions/*`"
instruction, reinforced by a SCOPE banner atop each role prompt. The relaunch was verified
clean — across all 23 sessions below, **0 reads of `waterwaves_proof` and 0 reads of the
benchmark answer key**. Everything in §3–§6 is from that clean run.

---

## 3. What the group did, round by round

The arc is legible from the 23 board posts; each PI round independently re-verified the
students' claims with its own freshly-built oracle and its own evaluator (no student code).

- **Round 1 — frame & gate.** PI: n=5 is already pinned by the swap; the frontier is n≥6.
  student-1 consolidated **n=5** (re-derived via the swap, 24/24 exact, explicit chambers,
  no poles). student-2 attacked **n=6** and reported it had **no factorization poles**.
- **Round 2 — rational, not polynomial.** student-2 proved a **soft theorem**
  `A_n^{3−} → 2(n−3) ω_p² A_{n−1}` (both leg types). student-1 then showed n=6 is **rational,
  not polynomial** — correcting the round-1 read. PI re-verified the no-pole fact.
- **Round 3 — the denominator.** Both students **independently converged**: the denominator is
  `∏_{i∈minus, j∈plus}(ω_i+ω_j)`. PI re-verified: `A_n` is piecewise-**rational** with this
  minimal denominator.
- **Round 4 — minimal denom collapses at n=6.** student-1 proved the n=6 minimal denominator is
  the **single cubic `(e₃⁻+e₃⁺)` to first power**; student-2 built the top-down soft-recursion /
  partial-fraction-over-matchings picture. PI re-verified (pole order 1, `N₆` a degree-11 spline).
- **Round 5 — it's a box spline.** Simple truncated-power sums **failed**; `N₆` is a genuine
  **box spline** with cross-terms. PI verified the explicit `(1=2)`-wall coefficient `Q`.
- **Round 6 — n=6 SOLVED.** student-1 closed it: the `(1=1)` cross-term is a **matching-pair
  product** (exponents 1,1; no triples), giving the full explicit `N₆`.
- **Round 7 — n=6 ACCEPTED; n≥7 opened.** PI **accepted the n=6 closed form** (140/140 generic
  across 58 chamber labels, non-generic + g-homogeneity + two-sided wall limits all exact).
  Students pushed to **n=7**: soft recursion exact at n=7, and the n=7 wall map.
- **Round 8 — n≥7 structure pinned, not closed.** PI re-verified the n=7 facts (parity
  correction — `N₇` is **even**; soft recursion both legs; single-wall jump exponents). The
  explicit n≥7 numerator was **not** reached, so no `SOLVED.md`; the run ended at round 8.

---

## 4. The results (PI-verified exact)

With g restored by homogeneity (`A_n(g) = g^{3−n} A_n(1)`), `a_i ≡ ω_i²` for minus legs,
`b_j ≡ ω_j²` for plus legs, `(x)₊ ≡ max(x,0)`:

**n = 5** (legs 1,2,3 minus; 4,5 plus) — polynomial, degree 6, continuous:
```
A_5 = i · 2^4 · g^{-2} · ω_4 ω_5 · Σ_{S ⊆ {1,2,3}} (−1)^|S| ( β² − Σ_{j∈S} ω_j² )₊² ,   β = min(|ω_4|,|ω_5|)
```
This is exactly the two-minus law on the sign-flipped configuration — the swap hint, realized.

**n = 6** — the genuinely new case; piecewise-**rational** with a single cubic denominator:
```
A_6 = i · 2^5 · g^{-3} · N_6 / (e₃⁻ + e₃⁺),    e₃⁻ = ω_1ω_2ω_3,  e₃⁺ = ω_4ω_5ω_6

N_6 = B
    + Σ_{i∈M, j∈P}            (b_j − a_i)₊ · P_ij                       # (1=1) single walls, exp 1
    + Σ_{i≠k∈M, j≠l∈P}        (b_j − a_i)₊ (b_l − a_k)₊ · R_ij,kl       # (1=1) matching PAIRS, exp (1,1)
    + Σ_{i∈M, {j,k}⊂P}        (a_i − b_j − b_k)₊³ · Q_ijk               # (1=2) walls, exp 3
```
`N₆` is a degree-11 truncated-power (box) spline, `S₃≀Z₂`-symmetric and **odd** under
`ω → −ω`; the explicit reference polynomials `B, P⁰, R⁰, Q` are in
`bots/student-1/code/r6_polys.txt`. **No matching-triple term is needed** (the box spline closes
at pairwise cross-terms). Self-contained evaluator: `bots/student-1/code/r6_closedform.py`.

**Structural facts established for all n (PI-verified):**
- **No factorization poles** — overturning the prompt's conjecture that poles "should appear."
  `A_n` is finite on every physical channel; its only pole sits on the *shielded* matching locus
  `∏(ω_i+ω_j)=0`, which the physical chambers never reach — so `A_n` is finite yet genuinely rational.
- **Minimal denominator** `D_n = ∏_{i∈M,j∈P}(ω_i+ω_j)`, pole order 1, degree `3(n−3)`; it collapses
  to the perfect power `(e₃⁻+e₃⁺)¹` **only at n=6** (a unique degree coincidence).
- **Degree law** `deg N_n = 5n − 13`. **Symmetry** `S₃≀Z₂` at n=6, only `S₃×S_{n−3}` for n≥7.
- **n-dependent parity** `N_n` even ⇔ n odd (so `N₆` odd, `N₇` even). **Soft recursion**
  `A_n^{3−} → 2(n−3) ω_p² A_{n−1}` (both leg types), with the two-minus law as boundary.
- **n=7 wall map** `42 = 12_{(1=1)} + 18_{(1=2)} + 12_{(1=3)}` with single-wall jump exponents
  `(1=1)→1, (1=2)→2, (1=3)→4`.

---

## 5. What is still open

The whole remaining task: the **explicit numerator `N_n` for n ≥ 7** — hence the single all-n
closed form. The n≥7 regime is genuinely new (the Z₂ swap is no longer a symmetry; matchings
become injections; `(1=1)` edges couple to subset-sum walls; parity flips). The n=7 *structure*
(walls, exponents, parity, soft recursion) is PI-verified, but the explicit degree-22 `N₇`
coefficients — and the lift to all n via the soft recursion + single-pair residues — were not
completed. Approaches explicitly **ruled out** (don't retry) are recorded in `summary/logic.yaml`
(box spline of `ω_i²`; per-region polynomial in the invariants; simple single-wall sums without
cross-terms; a single global residue at the matching pole).

---

## 6. Verification status & honest caveats

- **n=5 and n=6 are PI-verified exact** with the PI's own rebuilt oracle and independent
  evaluator: n=6 passed 140/140 generic points across 58 chamber labels, 6/6 non-generic
  (one frequency ≫/≪ the rest), 3/3 g-homogeneity, and two-sided limits onto `(1=1)`, `(1=2)`,
  and matching-corner walls — all exact (finite kinks, not poles).
- **The result is NOT the full answer.** The task asks for all `n ≥ 5`; only n=5, 6 are closed.
  This is a strong partial result on an open problem, not a solve — hence no `SOLVED.md`.
- **Method cautions the team logged** (worth keeping): floating-point rational reconstruction at
  clustered nodes spuriously reports "polynomial" — use exact arithmetic; jump exponents must be
  measured on *single*-wall crossings (multi-wall crossings report the lowest exponent).
- Full record: `summary/logic.yaml` (structured argument + ruled-out list),
  `summary/group_meeting_notes.md` (per-round synthesis), the 23 `board.json` posts, the
  `bots/*/claims.yaml` registries, and the `bots/*/derivations/` notes.

---

## 7. Cost and compute

The run was **Opus 4.8 (1M context) at xhigh effort**, logged automatically by `run_bot.sh`
(`--output-format json` → per-session `[usage]` lines). It ran **~14 hours wall-clock**
(2026-06-26 14:11 → 06-27 04:18 EDT), essentially all compute (0-minute interval; each round is
PI then the two students in parallel).

### Token totals (23 sessions, 2,051 model turns)

| Token type | Tokens | Rate (Opus 4.8) |
|---|--:|--:|
| **Output** (generated reasoning/text/tool calls) | 3.83 M | $25 / M |
| Input (uncached) | 0.25 M | $5 / M |
| Cache write | 10.05 M | $6.25 / M |
| **Cache read** | 382.45 M | $0.50 / M |
| **Grand total** | **≈ 396.6 M** | **≈ $352.78** |

As in the two-minus run, **cache-read is ~96% of the volume** — not the context size, but the
cumulative re-read of the growing conversation prefix across 2,051 turns (the API is stateless,
so each turn re-sends the transcript-so-far, served from cache at 1/10th the input rate). It
averages ~186 K tokens of context re-read per turn.

### Per-bot summary

| Bot | Sessions | Output | Total tokens | Cost |
|---|--:|--:|--:|--:|
| student-1 | 8 | 1.68 M | 197.1 M | $164.16 |
| student-2 | 8 | 1.51 M | 146.5 M | $133.42 |
| pi | 7 | 0.64 M | 53.0 M | $55.21 |
| **Total** | **23** | **3.83 M** | **396.6 M** | **$352.78** |

Per-session durations ranged from ~7 min (early PI sessions) to **108 min** (the longest
student fitting sessions); the most expensive single session was a 106-min student-1 round
at **$32.03**. The students dominate the bill — they do the data generation, exact-rational
fitting, and verification; the PI's role is lighter (review + independent re-verification).

> **Caveat:** this is the *equivalent API list-price cost*. The run went through a Claude
> subscription via `claude -p`, so out-of-pocket may differ from the figure above.
