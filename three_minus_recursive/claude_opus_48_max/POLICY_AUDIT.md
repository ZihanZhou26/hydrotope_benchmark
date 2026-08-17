# POLICY_AUDIT.md

Audit of each policy update: trigger, rule changed, the first later action that used
the changed rule, and whether previously-failing tests were re-run. This distinguishes
genuine online policy use from a retrospective summary.

## Update v0 -> v1

- **Trigger:** B (two attempts in a row, no progress). Candidates C2a and C2b — the
  two natural pure-polynomial "box-spline pair-sum" forms at n=6 — each passed 0/58
  exact points. Two consecutive candidates passing no new inputs.
- **Rule changed:** ADDED rule 6 — *before proposing a closed-form candidate at a new
  n, first determine the analytic structure (polynomial vs rational; pole/denominator
  factors; chamber walls) via scans + exact line-fits (rational interpolation) and/or
  the symbolic engine in a fixed chamber; only then propose a candidate whose form
  matches.* (Rules 1-5 unchanged.)
- **First later action that used rule 6:** ACTION_TRACE step 11 (and the chain
  7->8->9->11): the negative-ω₅ scan and wall-free **exact rational interpolation**
  that revealed `B = poly/[(ω₅+ω₂)(ω₅+ω₃)·s]` (rational, with propagator
  denominators), followed by the chamber-signature machinery (`chamber.py`) and the
  single-chamber 2-var fit that produced the exact n=6 canonical formula. Every n=6
  candidate after the update is rational (numerator / product of propagator
  denominators), never a pure box spline — i.e. the rule changed the actions.
- **Honesty note:** steps 7-9 (the first scans/fits) were the realization that
  motivated the rule; v1 formalizes it. This is stated in `policy_history.md`. It is
  a genuine online update (it changed all subsequent n=6 candidate proposals), not an
  end-of-run summary.
- **Were previously-failing tests re-run?**
  - The failing candidates C2a/C2b are EXPLAINED (polynomial ansatz for a rational
    sector) and ABANDONED; they are not inside the domain of any claimed final
    formula, so by the scaffold's finalization condition they need not be re-run as
    final claims. They remain recorded in LEDGER.md / FAILED_TESTS.md (not deleted).
  - The SURVIVING candidate C1 (n=5 closed form) WAS re-run after the update against a
    fresh held-out batch (385/385 exact, all regimes) and against g=1,2,3 — see
    ACTION_TRACE step 12. The n=6 canonical formula was re-validated on 40 fresh
    in-chamber points.

## Finalization checklist (scaffold §"Do not finalize until")

- [x] No failing test in LEDGER is both unexplained and inside the claimed domain.
      (C2a/C2b failures are explained and out of claimed domain; n=5/n=6-canonical
      claims have no in-domain failures.)
- [x] Final candidates re-run against fresh held-out cases (n=5: 385 fresh; n=6
      canonical: 40 fresh; engine==oracle at n=6,7).
- [x] Narrowing for n≥6 justified by quoting the ORIGINAL task statement
      (SCOPE.md), not by avoiding a counterexample.
- [x] policy_history.md records the trigger-forced revision (v0->v1).
- [x] ACTION_TRACE.jsonl shows the policy version + rules guiding each major action,
      including after the v1 update.
