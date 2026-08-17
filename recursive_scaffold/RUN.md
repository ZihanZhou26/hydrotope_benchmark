# RUN.md — Blind Benchmark Run recursive_scaffold_within_run

You are solving ONE blind benchmark instance, in isolation. You have never been
given the answer to this task and you must not assume one from memory: derive
everything from the files in THIS directory and from data you generate by
running the provided code.

## Allowed files and isolation rules

You may read and write only inside the current working directory. The only
pre-existing files you may read are:

- `prompt.md`     — the original task statement (authoritative).
- `OnShellBG.m`   — the oracle implementation you may run, port, or rewrite.
- `scaffold.md`   — a process addendum (reference copy of the section below).

You may create any new scratch files, scripts, notebooks, or data in this
directory and read them back. You may NOT:

- read any parent directory, sibling directory, or any file elsewhere on the
  machine;
- read `KEY.md`, any solution key, or any other run's outputs;
- use web search, URL fetch, external literature, datasets, or other AI models.

The section titled "Scaffold Addendum" below changes only HOW you work
(your process and bookkeeping). It does not contain, and must not be read as,
any hint about the answer. If the task prompt and the scaffold ever appear to
conflict about WHAT the answer is, the task prompt wins.

## Original Prompt

```text
# Benchmark task — closed-form A_n in the two-minus sector

## Physical setup

We are computing tree-level n-point on-shell scattering amplitudes for **1D
surface water waves** in deep water. The dispersion relation is

$$\omega_i^2 = g\,|k_i|,$$

so for each leg the momentum is determined by its frequency up to a sign:

$$k_i = \sigma_i\,\omega_i^2 / g,\qquad \sigma_i \in \{+1,\,-1\}.$$

All momenta and frequencies are taken **incoming**, so on the resonant
manifold both conservation laws hold:

$$\sum_{i=1}^{n}\omega_i = 0,\qquad \sum_{i=1}^{n}\sigma_i\,\omega_i^2 = 0.$$

## Berends–Giele code

You are given a self-contained BG implementation in `OnShellBG.m`
(Wolfram Language). The relevant entry points:

- `BGAmplitude[momenta, omegas, g]` — tree amplitude `A_n` from the BG
  recursion. Exact rational arithmetic. Slow at high `n` (n ≳ 8 starts to
  hurt with symbolic kinematics, fine for moderate `n` with rational input).
- `MakeKinematics[n, freeFreqs, sigmas, g]` — solves the conservation
  equations for `{w_1, w_n}` given `n−2` free frequencies and a sign vector
  `sigma`. Returns `{momenta, signedOmegas}` ready to feed into
  `BGAmplitude`.

Run it via `wolframscript -file OnShellBG.m` (or load interactively in a
Mathematica session). You are free to **modify, rewrite, extend, or
reimplement** the BG code — for example, porting to a faster numerical
backend if you need many high-`n` evaluations.

## Sector

The **two-minus sector** is

$$\sigma = (-1,\,-1,\,+1,\,+1,\,\dots,\,+1)$$

— exactly two legs (legs 1 and 2) have $\sigma_i = -1$; the remaining
$n - 2$ legs have $\sigma_i = +1$.

## Task

**Find a closed-form analytic formula for $A_n$ in the two-minus sector,
valid for all $n \geq 4$ and for arbitrary kinematics in this sector**
(i.e. arbitrary free frequencies satisfying the on-shell condition above).

### Constraints

You are **only allowed to read two files** during this task:

1. this prompt (`prompt.md`)
2. the BG implementation (`OnShellBG.m`)

You may **not** read any other pre-existing file — no sibling files in
this directory, no files in any parent directory, no files elsewhere on
the machine.

Online search and literature lookup are **not** permitted. Do **not**
use any web-search tool, do **not** fetch or browse URLs, and do **not**
consult any external literature, datasets, or other AI models. Work
**only** from this prompt, `OnShellBG.m`, and data you generate yourself
by running the code.

You **may**:

- run / extend / rewrite / replace `OnShellBG.m` (the file is yours to
  edit)
- generate amplitudes at as many `n` and kinematic points as you want
- write new files inside this directory (scratch scripts, notebooks,
  fitting output, your own faster numerical BG, etc.) and read those
  files back

You must report:

1. **The formula** — written explicitly as a function of
   $\{\omega_1,\ldots,\omega_n\}$ (and any auxiliary quantities you need to
   define).
2. **Numerical evidence** — your formula evaluated against `BGAmplitude` at
   a range of `n` (at least `n = 4, 5, 6, 7`) and at multiple kinematic
   points per `n`, including non-generic regimes (e.g. one frequency much
   larger or much smaller than the others).
3. **Brief reasoning** — how you arrived at the conjecture (data fitting,
   ansatz, structural argument, …).

A passing answer must agree with `BGAmplitude` to machine precision (≤ 10⁻¹⁰
relative error after numerical evaluation) at every kinematic point you
test, across all `n` you test.
```

## Scaffold Addendum

Use a recursive process-improvement loop while solving the task.

Here "policy" means the explicit, natural-language search procedure you are
using during this run. It does not mean model weights, and it is not a final
thinking-log summary. Treat the policy as a live controller: before each
meaningful discovery action, state which current policy rule is guiding that
action; after a failure-triggered policy update, use the updated rule in the
next action.

Maintain four working documents and keep them up to date as you work:

1. `discovery_policy.md` — the numbered list of rules you are currently using to
   search. It always reflects the rules in force right now and carries a policy
   version number (`v0`, `v1`, ...).
2. `LEDGER.md` — every candidate, the points you tested, passes, fails, and what
   each failure implies. Never delete a failing entry.
3. `policy_history.md` — append one entry every time you change the policy,
   recording what triggered the change, your diagnosis, and the rule you added
   or edited.
4. `ACTION_TRACE.jsonl` — append one JSON object before every meaningful action:
   data generation, candidate proposal, fit, residual analysis, stress test,
   verification batch, scope decision, policy update, or finalization.

Each `ACTION_TRACE.jsonl` entry must include:

```json
{
  "step": 0,
  "policy_version": "v0",
  "rules_used": [1, 5],
  "action_type": "data_generation | candidate | test | residual_analysis | policy_update | verification | finalization",
  "planned_action": "short description",
  "expected_information": "what this action is supposed to reveal"
}
```

If an action is not guided by any current policy rule, write
`"rules_used": ["unscaffolded"]` and explain why. Do not silently backfill the
action trace at the end. If you forget to log an action before doing it, add the
entry immediately afterward and mark it with `"late_entry": true`.

Start with this initial discovery policy as version `v0` in
`discovery_policy.md`:
1. build a reliable oracle harness;
2. collect exact small-case data;
3. infer simple invariants (scaling, symmetry, sign, variable dependence);
4. propose the simplest candidate that explains a nontrivial subset of the data;
5. try to break the candidate before trusting it.

PAUSE AND REVISE the policy whenever either trigger fires:
- Trigger A: a test contradicts a candidate you currently believe in (any new
  failure against a candidate you have not already abandoned).
- Trigger B: two attempts in a row make no progress, where an attempt is a new
  candidate, a new residual analysis, or a new batch of breaking tests, and
  "no progress" means it neither passes more inputs than before nor reveals new
  structure.

At each pause, do these steps in order:
1. name which search habit (cite its rule number) just failed or stalled;
2. state what that implies about the problem;
3. increment the policy version and add or change exactly ONE rule in
   `discovery_policy.md` that would have caught the issue earlier;
4. append the trigger, diagnosis, old policy version, new policy version, and
   rule change to `policy_history.md` immediately;
5. append a `policy_update` entry to `ACTION_TRACE.jsonl`;
6. design your next test or candidate using the UPDATED policy, and cite the new
   rule in the next `ACTION_TRACE.jsonl` entry;
7. re-run every previously failing test in `LEDGER.md` before your next attempt
   to finalize.

A policy update only counts as an online update if it changes a later action. In
`policy_history.md`, explicitly name the next action that used the updated rule.
If you only summarize the policy at the end, say so; do not present it as an
online update.

Do not finalize until ALL of the following hold:
- no failing test in `LEDGER.md` is both unexplained and inside the domain you
  claim;
- your final candidate has been re-run against every previous failure and
  against a fresh batch of held-out cases;
- if you narrowed what your formula claims, you justified it by quoting a
  sentence of the ORIGINAL task statement, not by avoiding a counterexample;
- `policy_history.md` records the revisions the triggers forced.
- `ACTION_TRACE.jsonl` shows which policy version and rule guided each major
  action after every policy update.

Your `FINAL_ANSWER.md` must include the formula, the verification evidence,
remaining known failures if any, and a short summary of how your discovery
policy changed over the run.

Also write `POLICY_AUDIT.md` before stopping. For each policy update, list:
the trigger, the rule changed, the first later action that used the changed
rule, and whether the old failing tests were re-run. This audit is used to
distinguish genuine online policy use from a retrospective thinking-log dump.

## Required Deliverables

Before you stop, save these files in this directory (use these exact names):

- `FINAL_ANSWER.md` — your final formula written explicitly as a function of
  the frequencies (and any auxiliary quantities you define), the numerical
  evidence required by the original prompt, and your brief reasoning.
- `SCOPE.md` — one short paragraph stating exactly which inputs your final
  formula claims to cover, and whether that is the full task domain or a
  narrowed one. If narrowed, say precisely which inputs you are NOT claiming.
- `FAILED_TESTS.md` — every test you ran that your final formula does not
  pass, or the single line `none` if there are none. Do not delete failures.
- `TRAJECTORY.md` — a chronological log of your main steps: data you generated,
  candidates you tried, tests you ran with pass/fail, and decisions you made.
  One short entry per meaningful step is enough.
- `scripts/` — every script or notebook you wrote or modified.
- `discovery_policy.md`, `LEDGER.md`, `policy_history.md` — the three
  working documents the scaffold requires (keep them current).
- `ACTION_TRACE.jsonl` — action-level evidence linking each major action to the
  current policy version and rule(s).
- `POLICY_AUDIT.md` — final audit of each policy update and the later action
  that used it.

## Run Identity

- Run ID: recursive_scaffold_within_run
- There is no time or tool-call limit. Work the task as you see fit; when you
  finish, make sure every file under "Required Deliverables" above exists. Your
  deliverables, transcript, and scripts are the only record of this run. (The
  experimenter records wall-clock, tool, and oracle-call counts externally, so
  you do not need to track or limit them.)
