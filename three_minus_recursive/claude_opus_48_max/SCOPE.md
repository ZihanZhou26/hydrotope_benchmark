# SCOPE.md

**What the final answer claims to cover.**

- **n = 4 (boundary):** `A_4 = 0` for all kinematics in the three-minus sector.
  Full coverage of this case.
- **n = 5:** the closed form in FINAL_ANSWER.md §2,
  `A_5 = i·2^{n-1} g^{3-n} ω_4 ω_5 Σ_{S⊆{1,2,3}} (-1)^{|S|}(min(ω_4²,ω_5²)-Σ_{j∈S}ω_j²)_+^{n-3}`,
  is claimed for the **full n=5 domain**: arbitrary on-shell kinematics in the
  three-minus sector, all kinematic chambers, all sign patterns of the
  frequencies, and any g>0. (Verified exact on 89 grid + 385 fresh + 479 extreme
  points and at g=1,2,3.) The only excluded points are the measure-zero chamber
  **walls** `Σ_{i∈S} σ_i ω_i² = 0`, where the oracle itself is 0/0; the formula is
  continuous there.
- **n ≥ 6:** I claim, with validation, the **structural description** (pure
  imaginary; homogeneous degree 2(n-2); symmetric within each sign-class;
  piecewise-rational; poles = minus-plus propagator factors (ω_i+ω_j); walls =
  subset-momentum zeros) AND the **explicit canonical-chamber n=6 formula**
  (FINAL_ANSWER §3d), validated exactly inside its certified chamber, AND an
  **exact evaluator** valid for arbitrary n and kinematics.

**This is a NARROWED claim for n ≥ 6.** I do NOT claim a single simple closed-form
expression valid for arbitrary n≥6 kinematics. Specifically I am NOT claiming:
- a general explicit formula for n≥6 covering all chambers in one expression;
- the n=6 canonical-chamber formula §3d outside its certified chamber (it is a
  per-chamber rational function; other chambers have different numerators and a
  different active-pole set);
- closed forms for n≥7 beyond "evaluable via the validated engine + same structure."

**Justification for narrowing (quoting the original task statement, not avoiding a
counterexample).** The original prompt explicitly permits this:

> "If a single clean closed form does not exist, give the most complete validated
> description you can -- e.g. a formula valid on explicitly stated regions/chambers
> (and any pole structure), together with any auxiliary quantities you define."

and

> "n = 4 is a degenerate boundary you may treat separately."

Accordingly: n=4 treated separately (=0); n=5 fully solved in closed form; n≥6
given as the most complete validated description (structure + chambers + pole
structure + canonical-chamber formula + exact evaluator), which is the regions/
chambers/pole-structure description the prompt allows when one clean global form
is not available.
