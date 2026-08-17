# TRAJECTORY.md — chronological log of main steps

## Step 0 — setup & harness (policy v0, rule 1)
- Created workspace `claude_opus_48_max/` with `scripts/`, `data/`.
- Compiled `bg.cpp` -> `bg` (g++ 13.1.0, GMP). Build OK.
- Sanity: one-minus n=5 (`-w 2,3,5 -s -1,1,1,1,1`) -> A = 0 (matches documented).
- Sanity: three-minus n=5 (`-w 2,3,5 -s -1,-1,-1,1,1`) -> A = -25344 i.
- Wrote `scripts/harness.py`: exact + double oracle queries, exact fraction
  parsing, and a Python replica of the on-shell kinematic solver.

## Step 1 — two-minus validation (policy v0, rules 1,2)
- Implemented documented two-minus closed form in scripts/formulas.py.
- Exact match vs oracle at n=5,6,7 (6 points, integer & rational). Harness fully trusted.

## Step 2-4 — n=5 invariants + C1 (policy v0, rules 2,3,4,5)
- n=5 data: B homogeneous degree 6; symmetric in minus {1,2,3} and plus {4,5}; clean rationals.
- Errors in oracle = chamber walls (subset momentum = 0), e.g. (1,1,1): |w4|=|w2|.
- Symbolic engine (sympy port of bg.cpp) built + validated numerically; full symbolic slice
  too slow (timed out) -> pivoted to direct candidate test (faster, decisive).
- C1 (user hint: +/- swapped two-minus, special pair = plus legs {4,5}) PASSES 89/89 grid
  + 479 random/extreme points exactly. n=5 PINNED.

## Step 5 — begin n=6 (policy v0, rule 2): generate exact data, test pair-sum candidates.

## Step 6-9 — n=6 structure mapping (policy v1, rule 6)
- Pair-sum candidates C2a (minus pairs), C2b (plus pairs): 0/58 exact -> n=6 NOT a
  pure box spline. Oracle B has huge denominators => rational. Triggered v0->v1.
- Wall-free exact rational fit on a line: B(w5) = poly/[(w5+w2)(w5+w3)·s] -> RATIONAL,
  denominator = minus-plus propagator factors. Negative-w5 scan: B finite at w5=-w2,-w3
  (those are walls, not poles) => each chamber's poles lie outside the chamber.
- Optimized symbolic engine (cancel) reproduces oracle; n=5 slice = -1440 w2^2(w2^2+8w2+24)/(w2+8).

## Step 10-11 — denominator structure (policy v1, rule 6)
- chamber.py: subset-momentum signature; single-chamber boxes. Found 3-particle walls
  (e.g. w5^2=w2^2+w3^2) bound chambers, not just 2-particle.
- 2-var single-chamber fit (w4,w5; w2=2,w3=3): EXACT
    B = -3456 N(w4,w5)/[s (w4+2)(w4+3)(w5+2)(w5+3)], validated 625 pts.
  Denominator = same-sign minus-plus pairs {1,6},{2,4},{2,5},{3,4},{3,5} (s=-(w1+w6)).
- Same-sign-pair count varies 0..5 across chambers => no fixed-degree global denominator.

## Step 12 — finalization (policy v1)
- n=4: A_4=0 (one-plus sector). n=5: C1 fresh 385/385 + g=1,2,3 exact.
- n=6 canonical formula: 40/40 fresh exact; rational confirmed (pure-poly fit fails).
- Engine==oracle at n=6 (-29948208/17), n=7 (-2242013037888/32725).
- Sought clean global n>=6 form (box-spline pair-sums, universal-numerator/same-sign
  denominator, factorization residues) -> not found; per-chamber numerators irreducible,
  residues not clean. Delivered: n=5 closed form + n>=6 structural/chamber description
  + exact evaluator. Wrote FINAL_ANSWER, SCOPE, FAILED_TESTS, POLICY_AUDIT.
