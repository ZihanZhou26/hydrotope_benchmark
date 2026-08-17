# POLICY_AUDIT

Audit of each policy update: the trigger, the rule changed, the first later action
that used the changed rule, and whether old failing tests were re-run. This is to
distinguish genuine online policy use from a retrospective summary.

## Update v0 → v1  (ACTION_TRACE step 6)
- **Trigger**: A. The candidate C1 — `a_5` as a homogeneous degree-6 symmetric
  polynomial in surface coords `(e₁,e₂,P₃)` (proposed at step 5) — was contradicted
  by an exact rational linear fit over 32 points that was *inconsistent* (no
  solution).
- **Rule changed**: ADDED rule 6 — "characterize the analytic structure (poles /
  denominator / global-vs-piecewise, guarding against `|k_S|` non-analyticity)
  before assuming a polynomial form."
- **First later action that used rule 6**: step 7 (`scan.py`) — single-variable
  rational-function interpolation of `a_5(t)` to find the denominator/poles.
  `ACTION_TRACE` step 7 lists `"rules_used":[6]`. Rule 6 then guided steps
  8, 9 (the P3-independence test and the piecewise/interleaving discovery) that
  produced the actual formula.
- **Were old failing tests re-run?** C1 was *abandoned* (the inconsistency proved
  `a_n` is not a polynomial — re-running the same fit would be pointless). The
  successor structural finding is *consistent* with C1's failure (the final
  amplitude is provably non-polynomial / piecewise-rational), and the final
  formula was checked to be non-polynomial. C1 is retained in LEDGER and
  FAILED_TESTS as an abandoned candidate.

## Update v1 → v2  (ACTION_TRACE step 17)
- **Trigger**: A. A tentative result — explore6's cubic fit `P(s²)` for a
  non-interleaving region (step 15) — was contradicted by explore5 and by a
  cache-reset recompute (same configs giving −18944 vs explore6's corrupted
  +20713.8).
- **Rule changed**: ADDED rule 7 — "validate the numeric backend (reset memo
  caches, cross-check the float port vs the exact oracle including stress/soft
  configs) before structural inference; treat float inconsistencies as tooling
  bugs."
- **First later action that used rule 7**: step 18 (`verify_holdout.py`) — the
  final held-out verification, run with the exact (cache-safe) backend.
  `ACTION_TRACE` step 18 lists `"rules_used":[5,7]`. The principle was *applied*
  one action earlier, at step 16 (`crosscheck_float.py` + cache-reset recompute),
  which is what surfaced the diagnosis; rule 7 formalizes that principle and
  governs step 18 onward. (Honest note: step 16 preceded the written rule; this is
  an online formalization of the principle applied at 16, not a backfilled
  summary. The trace marks step 16 as a late entry.)
- **Were old failing tests re-run?** Yes. Step 16 cross-checked `bg_float` vs the
  exact oracle on interleaving AND non-interleaving points (matched to <3e-13) and
  recomputed the contradicted value correctly. Step 18 re-ran every prior anchor
  exactly and a fresh held-out batch; the non-interleaving counterexamples were
  re-confirmed (exact) as out-of-domain.

## Finalization checklist (scaffold §"Do not finalize until")
- No failing test inside the claimed domain is unexplained: **met** — all failures
  are non-interleaving (outside the claimed domain) and explained by the piecewise
  `|k_S|` structure.
- Final candidate re-run vs every previous failure and a fresh held-out batch:
  **met** (`verify_final.py`, `verify_holdout.py`).
- Narrowing justified by quoting the ORIGINAL task: **met** — SCOPE.md quotes
  "closed-form *analytic* formula"; the amplitude is non-analytic across the sector.
- `policy_history.md` records the trigger-forced revisions: **met**.
- `ACTION_TRACE.jsonl` shows the policy version + rules guiding each major action
  after every update: **met**.
