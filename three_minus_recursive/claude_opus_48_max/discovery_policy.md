# discovery_policy.md — policy version v1

Policy version: **v1**

The numbered rules currently in force for searching for the closed form:

1. build a reliable oracle harness;
2. collect exact small-case data;
3. infer simple invariants (scaling, symmetry, sign, variable dependence);
4. propose the simplest candidate that explains a nontrivial subset of the data;
5. try to break the candidate before trusting it.
6. **(v1)** Before proposing a closed-form candidate at a new n, FIRST determine the
   analytic structure: is B polynomial or rational? Map the chamber walls
   (subset momenta sum_{i in S} sigma_i w_i^2 = 0) and the pole/denominator factors
   (propagator denominators w_S^2 - |k_S|) via numerical scans + exact line-fits
   (rational interpolation) and/or the symbolic engine in a fixed chamber. Only then
   propose a candidate whose form (polynomial vs rational, which factors) matches.

(v0 was the mandated initial policy. v1 added rule 6 after Trigger B — see
`policy_history.md`.)
