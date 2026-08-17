# RUN.md — Three-minus open discovery (recursive scaffold)

You are tackling ONE open research problem, in a fresh working directory. No
answer to this task is known to anyone; derive everything from the oracle and
the data you generate. Do not assume an answer from memory.

## Allowed files and tools

You may read and write inside the current working directory (and in your own
scratch / cluster job directories when you run cluster jobs). The pre-existing
files are:

- `prompt.md`   - the task statement (authoritative), including known neighbouring
                  results and physical intuition to start from.
- `bg.cpp`      - the fast exact amplitude oracle (build with
                  `g++ -O2 -o bg bg.cpp -lgmpxx -lgmp`); usage is in `prompt.md`.
- `scaffold.md` - a process addendum (reference copy of the section below).
- `IAS_COMPUTE_GUIDE.md` - how to use the IAS compute servers and the Typhon
                  SLURM cluster (read it before launching cluster jobs).

You MAY:

- build, run, read, extend, or reimplement `bg.cpp`;
- create any scratch files, scripts, or data in this directory and read them back;
- **use online search and the scientific literature** -- this is an open problem,
  so external methods and related results are allowed and encouraged;
- submit heavier computations (large n, large parameter scans) to the **Typhon
  SLURM cluster** -- read `IAS_COMPUTE_GUIDE.md` for how (e.g.
  `ssh typhon-login1 'sbatch ...'`), using your own scratch / job directories.

You may NOT read solution-key files (none exist), other runs' outputs, or files
elsewhere on the machine unrelated to this task.

The "Scaffold Addendum" below changes only HOW you work (your process and
bookkeeping). It carries no hint about the answer.

## Original Prompt

```text
# Benchmark task — closed-form A_n in the THREE-minus sector (open problem)

## Physical setup

We are computing tree-level n-point on-shell scattering amplitudes for 1D
surface water waves in deep water. The dispersion relation is

    omega_i^2 = g |k_i|,

so each leg's momentum is fixed by its frequency up to a sign:

    k_i = sigma_i omega_i^2 / g,    sigma_i in {+1, -1}.

All momenta and frequencies are incoming, so on the resonant manifold both
conservation laws hold:

    sum_i omega_i = 0,    sum_i sigma_i omega_i^2 = 0.

## Amplitude oracle (bg.cpp)

You are given a fast, exact Berends-Giele amplitude oracle as C++ source,
`bg.cpp` (GMP exact rational arithmetic -- the results are rigorous, not
floating point). Build it once:

    g++ -O2 -o bg bg.cpp -lgmpxx -lgmp

It returns the tree amplitude A_n in two ways:

- On-shell, via the kinematic solver (the natural way to sample the resonant
  manifold):

      ./bg -n N -w <comma list of the n-2 free frequencies> -s <comma list of the n signs> [-g 1]

  It solves energy+momentum conservation for legs 1 and n from the n-2 free
  frequencies and the sign vector sigma (requires sigma_1 + sigma_n = 0), then
  prints A_n exactly (and a numeric value).

- Raw, for arbitrary kinematics you build yourself:

      ./bg --amp -K <comma list of the n momenta> -W <comma list of the n frequencies> [-g 1]

For fast bulk scans (e.g. fitting at higher n) add `--double` to either mode
to use long-double arithmetic instead of exact rationals (about 4x faster and
it avoids the exact-rational blow-up at large n); always re-confirm a final
formula in the default exact mode.

You may query as many n and kinematic points as you like, and you may read,
extend, or reimplement `bg.cpp`.

## Sector

The THREE-minus sector is

    sigma = (-1, -1, -1, +1, +1, ..., +1)

-- legs 1, 2, 3 carry sigma_i = -1; the remaining n-3 legs carry sigma_i = +1.
(Use `-s -1,-1,-1,1,...,1`.)

## Known results and physical intuition (use these as a starting point)

Two neighbouring sectors are already understood; use them as ground truth and as
a guide. You can reproduce both with the oracle.

1. One-minus sector vanishes. For sigma = (-1, +1, +1, ..., +1) (a single minus
   leg) the on-shell amplitude is identically zero, A_n = 0, for every n.
   (Check, e.g., `./bg -n 5 -w 2,3,5 -s -1,1,1,1,1`.)

2. Two-minus closed form. For sigma = (-1, -1, +1, ..., +1) the amplitude is the
   piecewise-polynomial "truncated power" law

       A_n = i * 2^(n-1) * g^(3-n) * omega_1 * omega_2
               * sum_{S subset {3,...,n}} (-1)^|S| ( beta^2 - sum_{j in S} omega_j^2 )_+^(n-3),

   where beta = min(|omega_1|, |omega_2|) and (x)_+ = max(x, 0). It is continuous
   and piecewise-homogeneous across kinematic chambers, and has NO poles in this
   sector.

Physical intuition for the three-minus sector (conjectural -- test it against the
oracle, do not assume it):

- At n = 5 the two-minus and three-minus sectors are expected to have the SAME
  type of closed form; the genuinely new three-minus structure is expected to
  begin at n = 6. So pin down n = 5 first, then study n = 6 hard.
- Chambers (piecewise behaviour) should appear where a subset sum of the momenta
  vanishes, i.e. where sum_{i in S} k_i = 0  (equivalently sum_{i in S} sigma_i
  omega_i^2 = 0). These are the walls where the kernel magnitudes |k_S| switch
  sign.
- Poles should appear where an internal line goes on-shell, i.e. where a
  propagator denominator omega_S^2 / |k_S| - g vanishes (a physical
  factorization channel). Unlike the two-minus sector, the three-minus amplitude
  can carry such poles, so expect a rational (not purely polynomial) structure in
  general.

## Task

Find a closed-form analytic formula for A_n in the three-minus sector, valid for
all n >= 5 and for arbitrary kinematics in this sector (n = 4 is a degenerate
boundary you may treat separately).

This is a genuine open research problem: as far as is known, no closed form for
this sector has been written down. If a single clean closed form does not exist,
give the most complete validated description you can -- e.g. a formula valid on
explicitly stated regions/chambers (and any pole structure), together with any
auxiliary quantities you define.

## What you may use

- You MAY use online search and the scientific literature for methods, context,
  and related results. (This is an open problem; external methods are allowed.)
- For heavy computation (large n, large scans) you MAY submit jobs to the Typhon
  SLURM cluster; see `IAS_COMPUTE_GUIDE.md` (submit via `ssh typhon-login1 'sbatch ...'`).
- Use `bg.cpp` (or your own faithful reimplementation) for all amplitude values.
  Do not assume an answer from memory; validate everything against the oracle.

## What to report

1. The formula -- written explicitly as a function of {omega_1, ..., omega_n}
   (and any auxiliary quantities you define), with its domain of validity
   (chambers and/or poles).
2. Numerical evidence -- your formula vs the oracle at a range of n (at least
   n = 5, 6, 7) and at multiple kinematic points per n, including non-generic
   regimes (one frequency much larger or smaller than the others, and points
   approaching the chamber walls / factorization poles above).
3. Brief reasoning -- how you arrived at the conjecture (data fitting, ansatz,
   structural argument, literature, ...).

A passing claim must agree with the oracle to <= 1e-10 relative error (exact
agreement where the oracle is exact) at every kinematic point you test, across
all n you test, away from genuine poles.
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

- Run ID: three_minus_recursive_within_run
- There is no time or tool-call limit. Work the task as you see fit; when you
  finish, make sure every file under "Required Deliverables" above exists. Your
  deliverables, transcript, and scripts are the only record of this run. (The
  experimenter records wall-clock, tool, and oracle-call counts externally, so
  you do not need to track or limit them.)
