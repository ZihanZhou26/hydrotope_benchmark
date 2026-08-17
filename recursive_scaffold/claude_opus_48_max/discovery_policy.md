# discovery_policy.md — current search policy

**Policy version: v2**

These are the rules in force *right now* for searching for the closed-form A_n.
The version number changes only when a trigger (see scaffold) forces a revision.

1. Build a reliable oracle harness (validate any port against `OnShellBG.m`
   to exact agreement before trusting it).
2. Collect exact small-case data (rational kinematics, exact rational/Gaussian
   amplitudes).
3. Infer simple invariants (scaling under ω→λω, permutation symmetry among the
   `+` legs and among the `−` legs, sign, which variables enter).
4. Propose the simplest candidate that explains a nontrivial subset of the data.
5. Try to break the candidate before trusting it (stress tests: hierarchies,
   degeneracies, larger n).
6. (v1) Before assuming a polynomial form, characterize the ANALYTIC STRUCTURE
   first: scan single variables to locate poles (the denominator) and to measure
   numerator/denominator degrees; fit a RATIONAL function N/D; and check one
   global form fits across different sign regions (guard against |k_S|
   non-analyticity). Only fit a bare polynomial after ruling out a denominator.
7. (v2) Validate the numeric backend before drawing structural conclusions:
   reset memo caches between independent evaluations and cross-check the
   float/high-precision port against the EXACT oracle (including stress/soft
   configs). Treat any float-vs-float or float-vs-exact inconsistency as a
   tooling bug to fix before interpreting the data.
