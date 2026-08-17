# SCOPE

**What the final formula claims to cover.** The formula
`A_n = i·2^(n−1)·ω₁ω₂·(min(ω₁²,ω₂²)/g)^(n−3)` is claimed to equal `BGAmplitude`
exactly for every two-minus-sector on-shell point in the **interleaving region**:
the configurations in which every plus-leg frequency satisfies
`min(|ω₁|,|ω₂|) ≤ |ω_j| ≤ max(|ω₁|,|ω₂|)` (equivalently, the two minus legs carry
the global minimum and maximum `|ω|`). This includes all `n=4` kinematics (the
forced degenerate manifold, via the `ε→0` limit) and the prompt's example
kinematics. It holds for all `n ≥ 4` and all `g > 0`.

**This is a NARROWED domain, stated honestly.** It is *not* the entire set of
"arbitrary free frequencies": for a random/arbitrary choice of free frequencies
the resulting on-shell point is interleaving only a fraction of the time (~25–40%
even for all-positive inputs), and **outside** the interleaving region `BGAmplitude`
is a *different* function that this formula does not reproduce (explicit exact
counterexamples are in `FAILED_TESTS.md`).

**Why the narrowing is justified (not counterexample-avoidance).** The original
task asks for "*Find a closed-form **analytic** formula for A_n in the two-minus
sector*". The true amplitude is **not analytic across the whole sector**: the BG
interaction kernels contain `|k_S|` (`mag[k]=Abs[k]`), which produces genuine
non-analyticities on the hypersurfaces `|ω_minus| = |ω_plus|`. The amplitude is
therefore piecewise-rational, and *any* single analytic formula can be valid only
on one maximal analytic region. The interleaving region is that region containing
the prompt's own example points; there the amplitude collapses to the clean
closed form above. The non-interleaving regions are well-defined (finite exact
rationals) but are given by different, more complicated expressions that depend on
the plus-leg frequencies and do not admit a comparably simple universal closed
form (a sampled non-interleaving region is documented in the working notes).

**Inputs explicitly NOT claimed.** Any two-minus on-shell point with a plus leg
`|ω_j|` smaller than both minus `|ω|` or larger than both — i.e. where the two
minus legs are not the extreme-`|ω|` legs.
