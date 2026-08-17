# Process Scaffold

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
