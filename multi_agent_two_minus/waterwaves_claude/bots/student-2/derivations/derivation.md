# Analytic derivation of A_n in the two-minus sector (student-2, round 1)

**Task t_r1_s2** — derive the closed form from the Berends–Giele recursion in `bg.cpp`.

## Result (headline)

In the **principal kinematic chamber** (defined precisely below), the two-minus
amplitude collapses to a one-line closed form that depends **only on the two
σ = −1 legs**:

> **A_n = i · a_n,  with  a_n = 2^{n−1} · ω₁ · ω₂^{2n−5}**

where legs 1, 2 are the two minus legs (σ₁ = σ₂ = −1), ω₂ is the *smallest* free
frequency, and ω₁ (together with ωₙ) is fixed by the on-shell constraints
Σω = 0, Σσ ω² = 0. Equivalently a_n = 2^{n−1} (ω₁ω₂)·(ω₂²)^{n−3} =
2^{n−1}(ω₁ω₂)·|k₂|^{n−3}.

Degree in ω: 1 + (2n−5) = **2n−4** (matches the PI's scaling dimension). The
plus legs ω₃…ωₙ enter **only** through the constraint that fixes ω₁.

Checked exactly (relative residual ≡ 0, exact rational) against the oracle at
n = 5, 6, 7 over many points incl. extreme regimes; n = 4 by the δ→0 limit
(formula gives the exact integers −24, −320, …). See `data/verification_results.txt`.

---

## 1. Setup and method

`bg.cpp` evaluates `BGAmplitude` from kernels `EKernel`, `FKernel`, `Vertex`,
`Propagator`, `BGCurrent`. Momenta are `K_i = σ_i ω_i²` (g = 1), so |k_i| = ω_i².
The only source of `i` is the factor (−i/2) in `Vertex` and (−i) in `Propagator`;
the kernels are real.

I ported the recursion faithfully to Python (`code/engine.py`) with three back-ends:
exact `fractions.Fraction` (validated against `./bg` on the full PI reference table,
all exact), and a **symbolic** back-end (`sympy`) in which every `abs(·)` of a
momentum partial-sum is resolved by its sign at a generic reference point inside a
chamber. This yields the *exact rational function of the ω_i in that chamber*,
which I then reduce onto the on-shell surface (`code/symbolic.py`, `code/analyze.py`).

## 2. Why A_n is purely imaginary (Re A_n = 0)

`Vertex` = (−i/2)·(real) and `Propagator` = (−i)/(real) are each purely imaginary.
Examine `BGCurrent(S)`:

* |S| = 1: returns (1, 0) — real, carries `i⁰`.
* |S| ≥ 2: `BGCurrent(S) = [ Σ_partitions Vertex · ∏ BGCurrent(block) ] · Propagator`.
  Each term adds exactly **one Vertex and one Propagator** on top of the
  sub-currents, i.e. one extra factor i² = −1. By induction every `BGCurrent`
  carries an **even** number of i's ⇒ every current is **real**.

The amplitude `BGAmplitude` = Σ (root Vertex) · ∏ BGCurrent(block) has **one** Vertex
and **no** overall propagator, i.e. exactly one extra factor i times real currents:

> A_n = i · (real) ⇒ Re A_n = 0.

Confirmed symbolically: the cancelled symbolic Re part is identically 0 at n = 4, 5.

## 3. Why n = 4 is finite (the {2,4} 0/0 is removable)

On-shell the n = 4 two-minus constraints have a branch ω₁ = −ω₃, ω₄ = −ω₂ on which
the internal current over {2,4} has w_S = ω₂+ω₄ = 0 **and** k_S = K₂+K₄ = ω₄²−ω₂² = 0,
so `Propagator({2,4})` is a literal 0/0 (the SIGFPE/NaN the PI saw).

Computing `BGAmplitude` with **independent** ω_i (the `--amp` continuation, no
constraints imposed) and cancelling gives, symbolically,

```
a_4(ω₁,ω₂,ω₃,ω₄) = −ω₁³ω₂ + ω₁²ω₂ω₃ + ω₁²ω₂ω₄ + ω₁ω₂³ + 3ω₁ω₂ω₃² + 3ω₁ω₂ω₄²
                   + ω₂³ω₃ + ω₂³ω₄ + 6ω₂²ω₃ω₄ − ω₂ω₃³ − ω₂ω₃²ω₄ − ω₂ω₃ω₄² − ω₂ω₄³
                   − 2ω₃³ω₄ − 2ω₃ω₄³
```

— a **polynomial** (no surviving denominator). The would-be 1/D_{24} pole is
multiplied by a numerator that vanishes on the surface, so it cancels in the full
amplitude. Hence A_4 is finite; its on-shell value is just this polynomial on the
surface. Restricting (ω₁ = −ω₃, ω₄ = −ω₂):

> **a_4 = −8 ω₂³ω₃ = 8 ω₁ω₂³**   (since ω₃ = −ω₁ on the branch).

At (−3,1,3,−1): 8(−3)(1)³ = **−24**; at (−5,2,5,−2): 8(−5)(2)³ = **−320** — the PI
reference values.

## 4. n = 5 reduction and the general pattern

Running the symbolic recursion at n = 5 (independent ω, chamber reference
(−7,1,2,4,−5)) and reducing onto the on-shell branch (free freqs ω₂,ω₃,ω₄; ω₁,ω₅
solved) gives

```
a_5 = −16 ω₂⁵ (ω₂ω₃ + ω₂ω₄ + ω₃² + ω₃ω₄ + ω₄²) / (ω₂+ω₃+ω₄).
```

The numerator factor equals −ω₁·(ω₂+ω₃+ω₄) (it **is** the solved value of ω₁), so
the (ω₂+ω₃+ω₄) cancels and

> **a_5 = 16 ω₁ ω₂⁵.**

Together with a_4 = 8 ω₁ω₂³ this fixes the family

> **a_n = 2^{n−1} ω₁ ω₂^{2n−5}.**

Coefficient 2^{n−1} (8,16,32,64 for n=4,5,6,7) and ω₂-power 2n−5 (3,5,7,9). The
structural origin of the ω₂ power: `EKernel(n,·)` carries an explicit factor
|p₂|^{n−3} and E₃ ∝ p₁p₂, i.e. ∝ p₁ p₂^{n−2}; with p₂ → the smallest momentum ω₂²
this seeds the ω₂^{2n−6} together with the ω₁ω₂ from the root vertex.

## 5. The amplitude is piecewise; the principal chamber

Because the kernels/propagator contain `abs(k_S)` of momentum partial-sums, the
amplitude is **piecewise-rational**: across a locus where some subset momentum
k_S = Σ_{i∈S} σ_i ω_i² changes sign, |k_S| has a kink (no pole — the propagator
→ 0 there) and the rational expression changes. Within one chamber it is a single
rational function.

* The full amplitude is symmetric under S₂ (swap the two minus legs) × S_{n−2}
  (permute the plus legs) — verified directly on the oracle at n = 4 (by limit),
  5, 6. The simple form 2^{n−1}ω₁ω₂^{2n−5} is **not** S₂-symmetric, because the
  swap maps out of the principal chamber.
* **Principal chamber** = the one reached by the standard `-w` parametrization with
  the free frequencies ordered so that **ω₂ = min(ω₂,…,ω_{n−1})** (the free minus
  leg is the smallest free frequency). Empirically this is exactly the validity
  region: with ω₂ = min(free) the formula holds for *any* arrangement/values of the
  plus legs (it depends only on the minus pair); if ω₂ is not the smallest free
  frequency the value is a different rational piece. Tested at n = 5,6,7 with
  shuffled and extreme plus legs (see verification).

All PI reference points and all natural "ascending free frequency" inputs (incl.
the one-frequency-≫-rest regime) lie in the principal chamber, so the formula
reproduces every pass-bar value exactly.

## 6. Verification (exact rational unless noted)

| n | point (full ω) | oracle a_n | formula 2^{n−1}ω₁ω₂^{2n−5} | rel. resid |
|---|---|---|---|---|
| 4 | (−3,1,3,−1) (δ-limit) | −24 | 8·(−3)·1³ = −24 | →0 |
| 4 | (−5,2,5,−2) (δ-limit) | −320 | 8·(−5)·2³ = −320 | →0 |
| 5 | (−34/7,1,2,4,−15/7) | −544/7 | 16·(−34/7)·1⁵ | 0 (exact) |
| 5 | (−13/2,2,3,5,−7/2) | −3328 | 16·(−13/2)·2⁵ | 0 (exact) |
| 5 | (1,2,1000)  [extreme] | −16048096/1003 | = | 0 (exact) |
| 5 | (2,5,100000)[extreme] | −5120358417920/100007 | = | 0 (exact) |
| 6 | (1,2,3,4) | −1024/5 | 32·ω₁·1⁷ | 0 (exact) |
| 6 | (1,2,3,1000000)[extreme] | −16000096000384/500003 | = | 0 (exact) |
| 7 | (1,2,3,4,5) | −8896/15 | 64·ω₁·1⁹ | 0 (exact) |
| 7 | (1,2,3,4,1000)[extreme] | −32322048/505 | = | 0 (exact) |

Exact n = 7 runs in ≈2 s/point with the Python port (no need for `--double`; in
fact `--double` loses accuracy in the extreme regime). Re A_n = 0 at every point.

Reproduce: `code/final_verify.py` (table in `data/verification_results.txt`,
machine-readable `data/verification_table.json`, figure `figures/verification.png`).

## 7. Open items for round 2

* A first-principles proof (not just symbolic n=4,5 + verified pattern) that the
  principal-chamber recursion telescopes to 2^{n−1}ω₁ω₂^{2n−5}.
* The explicit rational expression in the **other** chambers, and a single
  abs/sign-covariant formula valid for *all* in-sector kinematics (the S₂×S_{n−2}
  symmetrization of the principal-chamber form). Cross-check with student-1's
  empirical factorization.
