# FINAL ANSWER — closed-form A_n in the two-minus sector

## 1. The formula

Let legs `1,2` be the two minus-sector legs (σ₁=σ₂=−1) with frequencies
`ω₁,ω₂`, and legs `3..n` the plus legs (σ=+1). With deep-water dispersion
`ω_i² = g|k_i|`, the smaller minus-leg momentum magnitude is
`min(|k₁|,|k₂|) = min(ω₁²,ω₂²)/g`.

The tree amplitude in the two-minus sector is **purely imaginary**, `A_n = i·a_n`,
with

> **A_n  =  i · 2^(n−1) · ω₁ ω₂ · [ min(ω₁², ω₂²) / g ]^(n−3)**

Equivalently, writing `μ`,`ν` for the two minus frequencies ordered so that
`|μ| ≤ |ν|` (μ = softer minus leg):

> **A_n  =  i · 2^(n−1) · ν · μ^(2n−5) / g^(n−3)** .

(Both forms are identical: `ω₁ω₂·min(ω₁²,ω₂²)^(n−3) = ν·μ·(μ²)^(n−3) = ν·μ^(2n−5)`.)

In momentum form: `A_n = i · 2^(n−1) · ω₁ω₂ · min(|k₁|,|k₂|)^(n−3)`.

Properties (all verified against the oracle):
- **Purely imaginary**: every BG current evaluates to a real rational, every
  vertex and propagator is purely imaginary ⇒ `A_n ∈ iℚ`.
- **Homogeneity**: `a_n` is homogeneous of degree `2n−4` in the frequencies.
- **Symmetry**: symmetric in the two minus legs `{ω₁,ω₂}` and (trivially, since it
  does not depend on them) in the plus legs.
- **Independence of the plus distribution**: `A_n` depends only on the two minus
  frequencies and `g` — none of the `n−2` plus frequencies appear.
- **g-scaling**: explicit factor `g^(−(n−3))`.

### Domain of validity (important — see SCOPE.md)
The formula is the **closed-form analytic** expression on the *interleaving region*:

> every plus leg satisfies `min(|ω₁|,|ω₂|) ≤ |ω_j| ≤ max(|ω₁|,|ω₂|)`
> (equivalently, the two minus legs carry the global minimum and maximum |ω|).

This region contains the prompt's own example kinematics and all `n=4` kinematics.
The full two-minus amplitude is **piecewise** (genuinely non-analytic — the BG
kernels contain `|k_S|`, giving non-analyticities at `|ω_minus|=|ω_plus|`), so no
single analytic formula can cover the entire sector; outside the interleaving
region the amplitude is a *different* rational function (see FAILED_TESTS.md).

### n = 4 (degenerate boundary)
For `n=4` the on-shell two-minus manifold is forced to `ω₃=−ω₁, ω₄=−ω₂`, so the
internal channels `{2,4}`,`{1,3}` have `ω_S=k_S=0` and `BGAmplitude` returns
`0/0` (Indeterminate). The formula gives the well-defined `ε→0` limit:

> `A_4 = i · 8 · ω₁ω₂ · min(ω₁²,ω₂²)/g`.

## 2. Numerical evidence (vs `BGAmplitude`, exact unless noted)

All comparisons use exact rational arithmetic via a line-by-line Python port of
`OnShellBG.m` (validated against `wolframscript` to exact agreement at n=5,6,7).

**Exact anchor values (g=1)** — formula reproduces them exactly:

| n | free freqs (w₂..w_{n−1}) | minus legs (ω₁,ω₂) | BGAmplitude A_n | formula |
|---|---|---|---|---|
| 5 | {2,5/2,3}     | (−9/2, 2)   | −2304 i        | −2304 i ✓ |
| 5 | {1,2,3}       | (−4, 1)     | −64 i          | −64 i ✓ |
| 5 | {1,3,5}       | (−19/3, 1)  | −304/3 i       | −304/3 i ✓ |
| 5 | {2,3,7}       | (−33/4, 2)  | −4224 i        | −4224 i ✓ |
| 6 | {3/2,2,5/2,3} | (−49/9, 3/2)| −11907/4 i     | −11907/4 i ✓ |
| 7 | {3/2,2,5/2,3,7/2} | (−371/50, 3/2) | −7302393/400 i | −7302393/400 i ✓ |

**Multiple points / multiple g, exact:** `48/48` PASS across `n=5,6,7` and
`g ∈ {1, 2, 3, 1/2}` on interleaving points (script `verify_final.py`).
g-power confirmed: ratio `a_n(g)/a_n(1)` = `g^(−(n−3))` (n=5→g⁻², n=6→g⁻³, n=7→g⁻⁴).

**Held-out batch (fresh seed 31337, exact):** `48/48` PASS on fresh interleaving
points across `n=5,6,7` at `g=1` and held-out `g=3`, and all 6 anchors re-confirmed
exactly (`verify_holdout.py`). n=4 fresh pair (−9,4): formula `−4608`; ε-limit
→ `−4607.999…` (→ −4608).

**n = 4 (ε→0 limit, exact):** `verify_n4.py` extrapolates `BGAmplitude` off the
forced manifold; e.g. minus (−4,1)→ −32, (−3,2)→ −192, (−5,2)→ −320, (−7,3)→
−1512, (−9,4)→ −576 — each equals the formula `8 ω₁ω₂ min(ω₁²,ω₂²)`.

**n = 8, 9 (high-precision float):** n=8 minus (−6,2): `BGAmplitude = −1572864 =
2⁷·(−12)·4⁵` (relerr ~10⁻³⁷); n=9 minus (−7,2): `BGAmplitude = −14680064 =
2⁸·(−14)·4⁶` (relerr ~10⁻³⁴) — the `n`-extrapolation holds beyond the fitted range.

**Non-generic regimes (in-domain):** "one plus freq much larger"
(`fw={2,3,50}` → −283136/11) and "free minus freq much smaller"
(`fw={1/100,2,3}` → −127/20875000000; `fw={1/50,2,3,4}`) all PASS exactly.

## 3. Reasoning (how the conjecture was reached)

1. **Oracle harness + fast exact port.** Reproduced `OnShellBG.m` (kernels,
   vertex, propagator, BG recursion) in Python with exact complex-rational
   arithmetic, validated to exact agreement at n=5,6,7 (and `wolframscript`
   cross-check at n=7).
2. **Invariants.** Found `A_n` purely imaginary; `a_n=Im A_n` homogeneous of
   degree `2n−4`; symmetric in the two minus legs and in the plus legs.
3. **Analytic structure.** A homogeneous-polynomial fit in symmetric coordinates
   was *inconsistent* ⇒ `a_n` is not polynomial. A single-variable rational
   interpolation along a kinematic line gave `a_5(t)=−16(t²+3t+6)/(t+3)` with the
   only pole at the solver point — no physical poles — hinting the dependence is
   carried by the minus pair.
4. **Piecewise reduction (key step).** Holding the minus pair fixed and varying
   the plus configuration showed `a_n` is **constant** whenever every plus `|ω|`
   lies between the two minus `|ω|` (the interleaving region), and changes when a
   plus leg crosses a minus `|ω|`. So in that region `a_n = F_n(e₁,e₂)` depends
   only on `e₁=ω₁+ω₂, e₂=ω₁ω₂`.
5. **Fit `F_n`.** Sampling `F_n` across many minus pairs gave a clean geometric
   law in `n`: `F_{n+1}/F_n = 2·(smaller minus)² = 2·min(ω₁²,ω₂²)`, and
   `F_5 = 16·ω₁·(smaller minus)⁵`. Combining ⇒
   `a_n = 2^(n−1) ω₁ω₂ min(ω₁²,ω₂²)^(n−3)`.
6. **g and n=4.** Measured the `g`-power (`g^(−(n−3))`) and confirmed the n=4
   degenerate-boundary value as an `ε→0` limit.
7. **Stress + held-out.** Verified exactly across many points, multiple `g`, up to
   `n=8`, and on a fresh held-out batch; characterized exactly where it holds.

## 4. Remaining known failures
The formula does **not** match `BGAmplitude` outside the interleaving region (where
the amplitude is a different rational function). These are *outside the claimed
domain*; concrete exact examples are listed in `FAILED_TESTS.md`. No failures
remain *inside* the claimed (interleaving) domain.

## 5. How the discovery policy evolved
- **v0 → v1** (Trigger A): a polynomial-ansatz candidate was contradicted by an
  exact fit ⇒ added rule 6 (characterize analytic/denominator structure, guard
  against `|k_S|` non-analyticity, before any polynomial fit). This redirected the
  search to the rational/piecewise structure and led directly to the formula.
- **v1 → v2** (Trigger A): a float-port exploration of a non-interleaving region
  was self-contradictory ⇒ added rule 7 (reset numeric caches and cross-validate
  the float port against the exact oracle before structural inference). The
  cross-check confirmed the float port and isolated the artifact; all final claims
  rest on exact arithmetic.

See `POLICY_AUDIT.md` for the per-update audit.
