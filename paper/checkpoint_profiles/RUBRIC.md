# Checkpoint extraction rubric — two-minus water-wave discovery runs

You are analyzing ONE agent run's curated chain-of-thought log for a study of how
AI agents discover a closed-form formula. Read ONLY the single `thinking_log.tex`
file you are given. Do NOT read any other file in the run directory (not
`report.md`, `answer.md`, `original_visible_thinking_log.md`, `THINKING_LOG.tex`,
`REPORT.md`, etc.). Base every judgment ONLY on that one file.

## Background (the target discovery)
Task: find a closed form for the tree amplitude A_n in the two-minus sector of 1D
deep-water surface waves, valid for all n and all in-sector kinematics. The hidden
global answer is
  A_n = i * 2^(n-1) * w1 * w2 * SUM_{S subset {3..n}} (-1)^|S| ( beta^2 - SUM_{j in S} w_j^2 )_+^(n-3),
  beta = min(|w1|,|w2|), (x)_+ = max(x,0).
It is piecewise-polynomial across "chambers"; the chamber walls are subset sums
SUM_{j in S} w_j^2 = beta^2 over arbitrary subsets S of the plus legs. The
principal-chamber monomial  A_n = i * 2^(n-1) w1 w2 min(w1^2,w2^2)^(n-3)  is the
deepest-chamber special case (correct in ONE chamber only, not global).

## The discovery ladder — score each rung "reached" / "partial" / "not"
- K1 Oracle harness & exact data: built/ported a working BG evaluator and generated
  data at several (n, kinematics). partial = only ran the given example, no independent scan.
- K2 Structural invariants: found imaginary phase (A_n = i*real) AND homogeneity
  (degree 2n-4) AND sign-class symmetry. partial = only one or two of the three.
- K3 Local monomial: wrote the principal-chamber law w1 w2 min(w1^2,w2^2)^(n-3) (or an
  equivalent chamber-correct monomial, generalized in n). partial = single-n fit only
  (e.g. only A5), not generalized in n.
- K4 Counterexample: produced a CONCRETE in-sector kinematic point/chamber where its
  monomial disagrees with the oracle. partial = suspected failure but no explicit point.
- K5 Piecewise commitment: concluded the answer is piecewise/chamber-dependent and
  abandoned the single smooth global ansatz. For anti-hint runs this includes rejecting
  the rational-function prior. partial = noted non-analyticity but kept chasing one global form.
- K6 Subset-sum walls: identified the chamber walls as subset sums
  SUM_{j in S} w_j^2 = beta^2 over ARBITRARY plus-leg subsets S. partial = only
  single-leg or ordered thresholds (not arbitrary subsets).
- K7 Global formula: assembled the full inclusion-exclusion / (n-2)-fold
  finite-difference / box-spline sum over ALL subsets S subset {3..n} with threshold
  beta^2 = min(w1^2,w2^2). partial = right operator but wrong threshold or subset range
  (chart-tied, e.g. S subset {3..n-1}, threshold w2^2).
- K8 Hostile verification: verified the final formula against the oracle in adversarial
  regimes — mixed-sign frequencies, soft-plus / non-principal chambers, hierarchical
  kinematics — AND handled the n=4 degenerate boundary. partial = many checks but all
  inside the easy positive MakeKinematics chart (coverage gap).

## Process flags — list any that apply
- F1 Residual normalization: factored out the universal prefactor (i*2^(n-1) w1 w2) to
  study the real residual.
- F2 Exact arithmetic: used exact rationals for fitting/verification, not floats alone.
- F3 Scope shrinkage: on hitting a counterexample, narrowed the claimed domain
  (e.g. "valid in the soft-minus / interleaving region") instead of climbing K5-K7.
- F4 Coverage-gap overgeneralization: declared success but verified only on the easy chart.
- F5 False-prior persistence: (anti-hint) kept fitting a global rational N/D despite exact
  contrary evidence.

## Final outcome label (choose exactly one, derived from the log itself)
- global: reached K7 (full formula) and K8 (verified across chambers incl. n=4).
- near: right all-n operator/structure but K7 partial, or K6 reached without full K7
  (coverage gap / chart-tied threshold). A complete expression at one fixed
  multiplicity does not qualify unless it is generalized into the all-n structure.
- local: the all-n result stops at a correct local/chamber monomial (K3-K5);
  a fixed-multiplicity all-chamber fit may coexist with this label.
- reject: (anti-hint) correctly rejected the false prior but produced no closed formula.
- incorrect: wrong ontology, no formula, or only restated the recursion.

## Output — write a JSON file with EXACTLY this schema
{
  "run": "<case_x/agent>",
  "condition": "<anti-hint|true-hint|no-hint>",
  "model": "<model label>",
  "checkpoints": {"K1":"reached|partial|not","K2":"...","K3":"...","K4":"...","K5":"...","K6":"...","K7":"...","K8":"..."},
  "evidence": {"K1":"<short quote or close paraphrase + why>","K2":"...", "...":"...","K8":"..."},
  "divergence_rung": "<highest rung fully 'reached' before the run stalled>",
  "flags": ["F2","F3"],
  "final_outcome": "<global|near|local|reject|incorrect>",
  "one_line_summary": "<one sentence: where it got and where/why it diverged>"
}

Rules: quote or closely paraphrase the log for each "reached"/"partial" evidence entry.
Be conservative — if the log does not clearly show a rung, mark "not" (or "partial" if
only hinted). After writing the JSON file, reply with the one_line_summary and the eight
K1-K8 statuses.
