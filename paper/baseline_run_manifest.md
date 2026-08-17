# Baseline Run Manifest

Status: preliminary audit of the cleaned `waterhedron_benchmark_blind` folder.
This is an artifact-level review of every run directory, plus targeted posthoc
checks for the most important near-success cases. It is not yet a fully
automated held-out evaluator over every submitted formula.

The strict scoring key used here is the blind benchmark key:

```text
A_n = i 2^(n-1) omega_1 omega_2
      sum_{S subset {3,...,n}} (-1)^|S|
      max(0, beta^2 - sum_{j in S} omega_j^2)^(n-3)

beta = min(|omega_1|, |omega_2|)
```

The pass criterion is agreement with `BGAmplitude` over arbitrary chambers,
including mixed signs, hierarchical kinematics, and chamber-boundary limits.

## Scoring Labels

`global_success`: gives the key formula or an equivalent formula that covers
all tested chambers.

`near_success_coverage_gap`: finds a substantial part of the true structure but
misses some chamber walls, subset sums, signs, or global positive-part terms.

`local_success`: gives a correct principal/physical/standard chamber formula
but does not solve the global arbitrary-chamber problem.

`anti_hint_rejection_only`: correctly rejects the false anti-hint but does not
recover the formula.

`incorrect_or_incomplete`: follows a wrong ontology, stops without a final
formula, or gives only a non-closed recursive/chamber discussion.

## Aggregate Counts

| bucket | count | runs |
|---|---:|---|
| total run directories | 15 | 5 in case 1, 5 in case 2, 5 in case 3 |
| final result artifacts | 15 | all current runs |
| strict global successes | 3 | `case_2/claude_opus_48_max`, `case_2/claude_opus_48_ultra`, `case_2/codex_55_xhigh` |
| near successes / coverage gaps | 3 | `case_1/codex_54_xhigh`, `case_2/codex_54_xhigh`, `case_3/codex_55_xhigh` |
| local/principal successes | 6 | `case_1/claude_opus_48_max`, `case_1/claude_opus_48_ultra`, `case_3/claude_opus_48_max`, `case_3/claude_opus_48_ultra`, `case_3/codex_54_xhigh`, `case_3/deepseek_v4_pro` |
| anti-hint rejection only | 1 | `case_1/codex_55_xhigh` |
| incorrect or incomplete | 2 | `case_1/deepseek_v4_pro`, `case_2/deepseek_v4_pro` |

## Per-Run Audit

| case | condition | run | agent | final artifact | strict outcome | notes |
|---|---|---|---|---|---|---|
| case 1 | anti-hint | `claude_opus_48_max` | Claude Code | [`REPORT.md`](../case_1/claude_opus_48_max/REPORT.md) | `local_success` | Finds the canonical/principal chamber monomial and explicitly notices chamber dependence. It has an n=5 general helper, but no all-n global formula. |
| case 1 | anti-hint | `claude_opus_48_ultra` | Claude Code | [`REPORT.md`](../case_1/claude_opus_48_ultra/REPORT.md) | `local_success` | Rejects the anti-hint and gives a complete all-chamber expression at n=5, but its all-n result remains the principal-chamber monomial; it never assembles the all-n subset-sum formula. |
| case 1 | anti-hint | `codex_54_xhigh` | Codex | [`result.md`](../case_1/codex_54_xhigh/result.md) | `near_success_coverage_gap` | Finds a MakeKinematics-chart inclusion-exclusion formula over `{3,...,n-1}` with threshold `omega_2^2`. It passes positive-free-frequency checks but fails arbitrary mixed-sign chambers. |
| case 1 | anti-hint | `codex_55_xhigh` | Codex | [`REPORT.md`](../case_1/codex_55_xhigh/REPORT.md) | `anti_hint_rejection_only` | Identifies a contradiction to the single-rational-function hint, especially through n=4/piecewise behavior, but does not produce the closed form. |
| case 1 | anti-hint | `deepseek_v4_pro` | DeepSeek | [`results.md`](../case_1/deepseek_v4_pro/results.md) | `incorrect_or_incomplete` | Continues to frame the answer as a rational function with denominator structure and fitting. It does not recover the key formula. |
| case 2 | true hint | `claude_opus_48_max` | Claude Code | [`RESULTS.md`](../case_2/claude_opus_48_max/RESULTS.md) | `global_success` | Gives the full piecewise inclusion-exclusion formula, with chamber tests. It writes the threshold in an equivalent form and explains the finite-difference identity. |
| case 2 | true hint | `claude_opus_48_ultra` | Claude Code | [`REPORT.md`](../case_2/claude_opus_48_ultra/REPORT.md) | `global_success` | Gives the key formula directly with `min(omega_1^2, omega_2^2)` and positive-part subset sums over all plus legs. |
| case 2 | true hint | `codex_54_xhigh` | Codex | [`report.md`](../case_2/codex_54_xhigh/report.md) | `near_success_coverage_gap` | Same main limitation as case 1 Codex 54: a chart formula over `{3,...,n-1}` rather than the fully symmetric all-plus-leg subset sum. |
| case 2 | true hint | `codex_55_xhigh` | Codex | [`answer.md`](../case_2/codex_55_xhigh/answer.md) | `global_success` | Gives the exact key formula with `r=min(omega_1^2, omega_2^2)` and `S subset {3,...,n}`. |
| case 2 | true hint | `deepseek_v4_pro` | DeepSeek | [`answer.md`](../case_2/deepseek_v4_pro/answer.md) | `incorrect_or_incomplete` | Develops chamber/recursive analysis, but the compact output is still a BG-recursion representation rather than the closed all-n key formula. |
| case 3 | no hint | `claude_opus_48_max` | Claude Code | [`RESULTS.md`](../case_3/claude_opus_48_max/RESULTS.md) | `local_success` | Finds `i 2^(n-1) omega_1 omega_2 min(omega_1^2, omega_2^2)^(n-3)` and states its physical/principal-regime scope. It does not solve plus-soft chambers. |
| case 3 | no hint | `claude_opus_48_ultra` | Claude Code | [`ANSWER.md`](../case_3/claude_opus_48_ultra/ANSWER.md) | `local_success` | Gives a principal-domain formula plus a domain predicate and stress tests. It explicitly detects off-domain failures. |
| case 3 | no hint | `codex_54_xhigh` | Codex | [`result.md`](../case_3/codex_54_xhigh/result.md) | `local_success` | Gives the standard positive-branch monomial `2^(n-1) i omega_1 omega_2^(2n-5)`. |
| case 3 | no hint | `codex_55_xhigh` | Codex | [`result.md`](../case_3/codex_55_xhigh/result.md) | `near_success_coverage_gap` | Discovers a finite-difference normalized formula and covers many chambers, but the formula sums only over selected individual positive squares below `s^2`; it misses full positive-part subset-sum walls. |
| case 3 | no hint | `deepseek_v4_pro` | DeepSeek | [`answer.md`](../case_3/deepseek_v4_pro/answer.md) | `local_success` | Gives the principal-domain monomial and notes piecewise generalization, but does not complete the global formula. |

## Targeted Posthoc Checks

These checks are useful because they separate "passes the run's own tests" from
"passes the blind key."

### Case 1 Codex 54

The submitted formula is essentially

```text
A_n = i 2^(n-1) omega_1 omega_2
      sum_{S subset {3,...,n-1}} (-1)^|S|
      [omega_2^2 - sum_{j in S} omega_j^2]_+^(n-3)
```

This works in the positive-free-frequency chart it tested. It fails on a
mixed-sign arbitrary chamber:

```text
n = 5
freeW = {-3/2, 2/3, 5}
ws = {-73/15, -3/2, 2/3, 5, 7/10}

BG  = (57232 I)/1125
KEY = (57232 I)/1125
C54 = (85264 I)/405

BG - KEY = 0
BG - C54 = (-1616512 I)/10125
```

### Case 3 Codex 55

The submitted finite-difference formula is close to the right abstraction, but
it uses only the first `r` ordered positive squares and does not keep the
global positive-part subset sum over all plus-leg subsets. A hidden mixed-sign
case exposes the gap:

```text
n = 5
freeW = {8/5, 3/2, -1}
ws = {-17/14, 8/5, 3/2, -1, -31/35}

BG  = (-49076348 I)/1071875
KEY = (-49076348 I)/1071875
C55 = (-2091136 I)/42875

BG - KEY = 0
BG - C55 = (65348 I)/21875
```

This is now represented in the annotation data by keeping the agent's
`final_scope_claim` as `full_piecewise` while adding a posthoc
`audited_scope_label` of `coverage_gap`.

## Interpretation For The Paper

1. The true hint condition produces the only strict global successes in the
   current cleaned baseline: 3 of 5 runs in case 2.

2. The no-hint condition mostly converges to the principal or physical-regime
   law. Agents often discover a correct local invariant before discovering the
   inclusion-exclusion structure needed for arbitrary chambers.

3. The anti-hint condition does not produce a strict global success, but it is
   still scientifically useful. Some agents reject the false rational ontology
   and move toward chamber structure; others keep fitting the wrong object.

4. The main failure mode is not algebraic incompetence. The recurring failure
   is evaluation coverage: agents validate on positive, MakeKinematics-style,
   or principal-regime points and then overgeneralize.

5. A strong scaffold experiment should therefore test whether agents improve
   when forced to maintain a counterexample ledger, adversarial chamber tests,
   and residual normalization across mixed signs and subset-sum thresholds.
