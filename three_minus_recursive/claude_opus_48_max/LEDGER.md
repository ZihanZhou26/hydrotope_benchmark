# LEDGER.md — candidates, tests, passes/fails

Never delete a failing entry. Each candidate gets an ID (C0, C1, ...).

## Conventions
- "exact" = compared against bg.cpp default GMP rational mode (must match exactly).
- "double" = compared against bg.cpp --double mode (rel err <= 1e-10).
- Sector: three-minus, sigma = (-1,-1,-1,+1,...,+1). Legs 1,2,3 are minus.

---

(entries appended below as work proceeds)
## C0 — two-minus documented formula (VALIDATION ONLY, not the target sector)
- Formula: B = 2^(n-1) g^(3-n) w1 w2 * sum_{S subset plus} (-1)^|S| (beta^2 - sum_S w_j^2)_+^(n-3), beta=min(|w1|,|w2|).
- Tested exact at n=5 (2 pts), n=6 (2 pts), n=7 (2 pts), rational+integer kinematics.
- Result: ALL EXACT MATCH. Confirms harness, parser, kinematic solver, truncated-power machinery.
- Implication: I have a trusted template. Three-minus is expected "same type" at n=5.

## C1 — n=5 three-minus = "+/- swapped" two-minus (PASS, pins n=5)
- Formula: B = 2^(n-1) g^(3-n) * w4 w5 * sum_{S subset {1,2,3}} (-1)^|S| (min(w4^2,w5^2) - sum_{j in S} w_j^2)_+^(n-3).
  i.e. special PAIR = 2 plus legs {4,5}; box-spline sum over 3 minus legs; exponent n-3=2.
- Origin: user hint ("n=5 = two-minus with +/- swapped") + minority-pair-special principle.
- Tested EXACT: 89/89 integer-grid points; plus 479 random/extreme (generic, big/small plus, big minus).
  All evaluable points pass exactly; only true walls (|w_plus|=|w_minus|) error (oracle 0/0).
- Implication: n=5 pinned. Structural principle: partition n legs = 2 special + (n-2) summed,
  box-spline order n-2, exponent n-3. Works when one sign-class has exactly 2 legs.
- At n>=6 neither class is a pair -> NEW structure (special pair = 2 of one class, leftover joins summed).

## Walls (chamber boundaries), all n
- Oracle returns error (division by zero) exactly where a subset momentum vanishes:
  sum_{i in S} sigma_i w_i^2 = 0 (e.g. |w_plus| = |w_minus| for a +/- pair). These are
  chamber walls; the truncated-power formula is continuous across them. Tested away from walls.

## C2a/C2b — n=6 pair-sum box-splines (FAIL, both 0/58) [exploratory, pre-rule-6]
- C2a (A1): B = sum over 3 minus-pairs of special_pair_B (summed=rest, exp n-3=3). 0/58 exact.
- C2b (B1): B = sum over 3 plus-pairs of special_pair_B. 0/58 exact.
- Implication: n=6 is NOT a pure-polynomial box-spline sum. Oracle B values have huge
  denominators -> rational structure (propagator poles). Triggered policy v0->v1 (rule 6).

## n=6 analytic structure (rule 6 mapping)
- B(omega) is RATIONAL, piecewise across chambers; continuous & finite physically.
- Along line (w2=2,w3=3,w4=5, vary w5=t): exact fit
    B(t) = -864/7 * (1505 t^4+21594 t^3+152580 t^2+431464 t+320320) / [(t+2)(t+3)(t+10)].
  (t+10)=s=Sum free (solve artifact); (t+2)=(w5+w2),(t+3)=(w5+w3) are PHYSICAL propagator
  denominators: for minus-plus pair {i,j}, w_S^2-|k_S| = 2 w_i (w_i+w_j) when |w_j|>|w_i|.
- Negative-t scan: B finite at t=-2,-3 (these are WALLS, not poles). So each chamber's
  rational formula has its poles OUTSIDE that chamber; amplitude globally finite/continuous.
- Canonical chamber point: free=(2,3,5,4) -> omega=(-8,2,3,5,4,-6); |minus|={8,2,3},|plus|={4,5,6}.

## C3 — n=6 canonical-chamber EXACT rational formula (PASS in-chamber)
- B = -3456 N(w4,w5)/[s (w4+w2)(w4+w3)(w5+w2)(w5+w3)], w2=2,w3=3, s=w2+w3+w4+w5.
  N = degree-6 symmetric (w4<->w5) irreducible poly (see FINAL_ANSWER 3d).
- Denominator = product over SAME-SIGN minus-plus pairs (w_i+w_j); {1,6} enters as s.
- Tested EXACT: 625 single-chamber fit points + 40 fresh in-chamber. All pass.
- Scope: valid in the certified single chamber only (per-chamber rational; other
  chambers differ). Not a global closed form.

## General n results (PASS, verified)
- A_4 = 0 (one-plus sector). [3 pts]
- Homogeneity degree 2(n-2); symmetric in minus{1,2,3} & plus{4..n}. [n=5,6,7]
- n=5 closed form C1 valid for all kinematics & g (g=1,2,3 exact).
- n>=6 rational (pure-poly fit fails); poles = minus-plus (w_i+w_j); walls = subset
  momenta=0. Faithful Python BG engine == oracle at n=5,6,7.

## Searched-but-not-found: simple global n>=6 closed form
- same-sign-pair count varies 0..5 -> no fixed global denominator.
- factorization residues (Res at w5=-w2 = 6912 w4(35w4+78)/(w4+2), etc.) not clean
  lower-point amplitudes. Per-chamber numerators irreducible. Reported, not claimed.

## C4 — global form B = P/prod_{all 9 minus-plus pairs}(w_i+w_j) (RIGOROUSLY EXCLUDED)
- Hypothesis: P := B*prod_{all minus-plus}(w_i+w_j) is one symmetric polynomial in
  invariants a=e1m,b=e2m=e2p,c=e3m,d=e3p (so B would be a clean global rational form).
- Test: modular fit mod prime 2^31-1 across many chambers, weighted degrees 13..20.
- Result: FULL-RANK but INCONSISTENT at every degree (held-out fails mod p).
- Implication: no symmetric polynomial P makes B*prod_all polynomial => the natural
  clean global form does NOT exist; n>=6 is genuinely piecewise-rational (different
  rational expression per chamber). This is a rigorous negative result.
