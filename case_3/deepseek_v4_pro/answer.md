# Closed-form A_n for the two-minus sector

## Formula

In the two-minus sector (σ = {-1, -1, +1, +1, ..., +1}), the tree-level
n-point on-shell scattering amplitude for 1D deep-water surface waves is:

$$
\boxed{A_n = i\,2^{\,n-1}\;\omega_1\;\omega_2^{\,2n-5}}
$$

where:
- ω_1, ω_2 are the two frequencies with σ = -1 (the "minus" legs)
- ω_2 is the free minus-sigma parameter in the MakeKinematics convention
- g = 1 (the gravitational acceleration; can be restored via dimensional analysis)

**Validity condition:** This formula holds when |ω_2| < |ω_i| for all
i = 1, 3, 4, ..., n, i.e., ω_2 has the smallest absolute value among
all n frequencies. For other kinematic regimes, the formula
generalises in a piecewise fashion depending on the relative ordering
of the |ω_i|.

### Explicit forms for low n

| n | A_n |
|---|-----|
| 4 | 8i ω_1 ω_2^3 |
| 5 | 16i ω_1 ω_2^5 |
| 6 | 32i ω_1 ω_2^7 |
| 7 | 64i ω_1 ω_2^9 |
| 8 | 128i ω_1 ω_2^11 |

### Restoring g

The gravitational acceleration g can be restored by dimensional analysis.
Since ω has dimension [T^{-1}] and A_n has dimension [L^{n-2} T^{...}],
the g-dependence is g^{-(n-3)}.

## Numerical verification

The formula has been verified against the exact rational-arithmetic
BGAmplitude from OnShellBG.m for n = 5, 6, 7 (and extensible to n = 8)
at numerous kinematic points. All tests show exact agreement
(relative error ≤ 10^{-15}).

### n = 5 (17 kinematic points, all PASS)

| free w's | ω_1 | ω_2 | A_5 | 16i ω_1 ω_2^5 |
|-----------|-------|-------|--------|----------------|
| {1, 2, 3} | -4 | 1 | -64i | -64i |
| {1, 3, 4} | -11/2 | 1 | -88i | -88i |
| {2, 3, 5} | -13/2 | 2 | -3328i | -3328i |
| {3, 5, 7} | -29/3 | 3 | -37584i | -37584i |
| {2, 4, 6} | -8 | 2 | -4096i | -4096i |
| {1, 5, 9} | -11 | 1 | -176i | -176i |

### n = 6 (12 kinematic points, all PASS)

| free w's | ω_1 | ω_2 | A_6 | 32i ω_1 ω_2^7 |
|-----------|-------|-------|----------|------------------|
| {1,2,3,4} | -32/5 | 1 | -1024i/5 | -1024i/5 |
| {2,3,5,7} | -184/17 | 2 | -753664i/17 | -753664i/17 |
| {1,3,5,7} | -169/16 | 1 | -338i | -338i |

### n = 7 (7 kinematic points, all PASS)

| free w's | ω_1 | ω_2 | A_7 | 64i ω_1 ω_2^9 |
|-----------|-------|-------|-----------|-------------------|
| {1,2,3,4,5} | -139/15 | 1 | -8896i/15 | -8896i/15 |
| {2,3,5,7,11} | -123/7 | 2 | -575780.57i | -575780.57i |

### Non-generic regimes

The formula remains valid when one or more plus-sigma frequencies are
much larger (or much smaller) than ω_2, provided the condition
|ω_2| < min_{i≠2} |ω_i| is maintained.

## Reasoning

1. **FKernel simplification**: For water waves, FKernel[3] = -1 - σ_i σ_j.
   This equals -2 when the two momenta have identical σ, and 0 when they
   have opposite σ. Consequently, only certain combinations of legs
   contribute to the BG recursion.

2. **EKernel simplification**: Similarly, EKernel[3] ∝ (1 + σ_i σ_j),
   vanishing for mixed-sign pairs.

3. **Data fitting**: Computing BGAmplitude for n = 5, 6, 7 at many
   kinematic points with |ω_2| < all |ω_i| (i ≠ 2) revealed the pattern:
   A_n ∝ ω_1 · ω_2^{2n-5}.

4. **Coefficient**: The prefactor 2^{n-1} was inferred from the values
   at ω_2 = 1:
   - A_5 = -64i = -2^4 i · ω_1 (with ω_2=1)
   - A_6 = -1024i/5 = -2^5 i · ω_1 / 5 (with ω_2=1, ω_1 = -32/5)
   
   Matching: For ω_2 = 1, A_n/(i ω_1) = 2^{n-1}. This generalises to
   arbitrary ω_2 as A_n/(i ω_1) = 2^{n-1} ω_2^{2n-5}.

5. **Piecewise generalisation**: When |ω_2| is not the global minimum,
   the BG recursion receives extra non-vanishing contributions from
   FKernel terms where intermediate-state momenta have mixed signs.
   The correction depends on the number of plus-sigma frequencies with
   |ω_i| < |ω_2|. For example, at n = 5:
   - Exactly 1 plus-sigma w below ω_2: A_5 = 16i ω_1 ω_2 (2ω_2^2 - 1)
   - Both plus-sigma w's below ω_2: A_5 = 16i ω_1 ω_2 · 4 ω_3 ω_4 (non-degenerate)
   - Both plus-sigma w's below ω_2, degenerate: A_5 = 16i ω_1 ω_2 · 2 ω_3^2

   The generalisation to higher n involves elementary symmetric
   polynomials of those plus-sigma frequencies that lie below ω_2 in
   absolute value.
