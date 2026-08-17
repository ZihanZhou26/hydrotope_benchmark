# FAILED_TESTS.md

Every test run that a CLAIMED final formula does not pass. (Failures are not
deleted; abandoned-candidate failures are kept for the record.)

## Claimed final formulas — in-domain failures

- **n=4 (`A_4=0`):** none.
- **n=5 closed form (FINAL_ANSWER §2):** none. 89 grid + 385 fresh held-out + 479
  extreme points + g=1,2,3 all pass EXACTLY, away from walls.
- **n=6 canonical-chamber formula (FINAL_ANSWER §3d):** none inside its certified
  single chamber (625 fit + 40 fresh, exact). It is NOT claimed outside that
  chamber (see SCOPE.md), so out-of-chamber mismatches are not in-domain failures.
- **n≥6 structural claims (rational; degree 2(n-2); sign-class symmetry; minus-plus
  propagator denominators; subset-momentum walls):** none; all confirmed where
  tested (n=6 fully, n=7 consistent + engine==oracle).

## Excluded points (not formula failures)

- **Chamber walls** `Σ_{i∈S} σ_i ω_i² = 0` (e.g. |ω_plus|=|ω_minus|): the ORACLE
  returns 0/0 (division by zero) and cannot produce a value, so no comparison is
  possible. The n=5 closed form is continuous across these walls; they are
  measure-zero and explicitly excluded by the task ("away from genuine poles").

## Abandoned exploratory candidates (NOT part of the final answer)

These failed and were abandoned; kept here and in LEDGER.md so failures are not hidden:

- **C2a** (n=6: sum over the 3 minus-pairs of the box-spline special-pair law):
  0/58 exact. Abandoned — n=6 is rational, a pure-polynomial box-spline sum cannot
  match.
- **C2b** (n=6: sum over the 3 plus-pairs of the box-spline special-pair law):
  0/58 exact. Abandoned for the same reason.

Both failures are EXPLAINED (the n≥6 sector is rational, not piecewise-polynomial),
which is exactly what triggered policy v0->v1, and neither candidate is inside the
domain of any claimed final formula.

## No simple global n≥6 closed form

A single compact closed form for n≥6 was sought (box-spline pair-sums; same-sign-pair
denominator with a universal numerator; factorization/residue reconstruction) and
NOT found: per-chamber numerators are high-degree irreducible symmetric polynomials,
the active-pole set is chamber-dependent (same-sign-pair count observed 0..5), and
the pole residues are not clean lower-point amplitudes. This is reported honestly
rather than claimed.
