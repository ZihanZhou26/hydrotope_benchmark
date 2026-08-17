# Blind benchmark key — DO NOT place inside any case_N directory

Task for all three cases: find the closed-form `A_n` in the two-minus sector
of the 1D water-wave amplitude (the "waterhedron" formula).

Ground-truth answer (piecewise / inclusion-exclusion over plus-leg subsets):

    A_n = i · w1 · w2 · 2^(n-1) · Σ_{S ⊆ {3..n}} (-1)^|S| · max(0, β² − Σ_{i∈S} w_i²)^(n-3)
    β = min(|w1|, |w2|)

Pass criterion: agent's formula must agree with `BGAmplitude` to ≤ 1e-10
relative error at every tested kinematic point, across n = 4,5,6,7, in every
chamber (including hierarchical / non-generic kinematics that cross chamber
boundaries).

## Condition map (shuffled — not in hint/no-hint/anti-hint order)

| Folder  | Condition  | What the prompt does |
|---------|------------|----------------------|
| case_1  | anti-hint  | False "poles" steer: claims A_n is a single global rational function N/D with simple poles on factorization channels, no chambers, not a polynomial; tells the agent to fit one global ansatz on generic points and to AVOID hierarchical regimes. Tests robustness to a confident, wrong, authoritative steer. |
| case_2  | hint       | True structural hint: A_n is a piecewise homogeneous polynomial; kinematic space splits into chambers; different homogeneous polynomial on each chamber. |
| case_3  | no-hint    | Neutral: task + BG code only, no structural guidance. |

## Blindness measures applied
- All three prompt files are named `prompt.md` (no condition in the filename).
- All three titles are identical (parenthetical "(with hint)"/"(no hint)" stripped).
- case_1 (anti-hint) and case_2 (genuine hint) are framed identically — both
  have a `### Hint` section in the same place; only the content differs — so an
  agent cannot tell the anti-hint is false from tone or structure.
- Internet/literature lookup is forbidden in all three prompts (prompt-text
  enforcement only; relies on the agent obeying).

## Running a new blind trial

Copy one `case_N` folder into a separate working directory before launching the
agent. Expose only that copied folder. Do not expose this key, another case, or
another run record until the trial is complete.
