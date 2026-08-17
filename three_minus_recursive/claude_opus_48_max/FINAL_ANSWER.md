# FINAL_ANSWER.md — closed-form A_n in the THREE-minus sector

Sector: `sigma = (-1,-1,-1,+1,...,+1)` (legs 1,2,3 minus; legs 4..n plus).
All amplitudes are **pure imaginary**: write `A_n = i * B_n` with `B_n` real.
The oracle `bg.cpp` is the only judge; every claim below is checked against it
in exact GMP-rational arithmetic (or `--double` for bulk scans).

---

## 0. Universal structural facts (verified n=4,5,6,7)

For all n in this sector:
- `A_n = i * B_n`, `A_n` is pure imaginary (real part 0 at every tested point).
- **Homogeneity:** `B_n(lambda * omega) = lambda^{2(n-2)} B_n(omega)`.
  (Checked: B(2w)/B(w) = 2^{2(n-2)} = 64, 256, 1024 at n=5,6,7.)
- **Symmetry:** `B_n` is totally symmetric under permutations of the minus legs
  {1,2,3} and, separately, of the plus legs {4,...,n}. (Checked n=5,6,7.)
- **g-dependence:** an overall factor `g^{3-n}` (verified for n=5 at g=1,2,3).

These pin the *shape* of any candidate: an overall `i * 2^{n-1} g^{3-n}`, times a
degree-`2(n-2)` object symmetric in each sign-class.

---

## 1. n = 4 (degenerate boundary): A_4 = 0

`A_4 = 0` identically. (Verified at free=(2,3),(5/2,4),(1,5): B=0.)
Reason: the n=4 three-minus pattern `(-,-,-,+)` is the **one-plus** sector (a single
`+` leg); it vanishes by the +/- (creation/annihilation) conjugation symmetry that
makes the one-minus sector vanish.

---

## 2. n = 5 (CLOSED FORM — solved)

```
                                          ___
              n-1   3-n                    \             |S|  (             ___              )^(n-3)
  A_5 = i * 2     g     * omega_4 omega_5 * /__   (-1)      ( min(w4^2,w5^2) - >_{j in S} w_j^2 )
                                          S subset {1,2,3}                                  +
```

i.e. with n=5  (`2^{n-1}=16`, `g^{3-n}=g^{-2}`, exponent `n-3=2`):

  B_5 = 16 g^{-2} * w4 * w5 * SUM_{S ⊆ {1,2,3}} (-1)^{|S|} ( min(w4^2,w5^2) - SUM_{j∈S} w_j^2 )_+^2

where `(x)_+ = max(x,0)` and the sum is over all 8 subsets S of the three minus
legs {1,2,3} (including S = empty).

**What it is / how it was found.** This is the documented two-minus law with the
roles of `+` and `-` swapped. In the two-minus sector the *two minus legs* are the
"special pair" (prefactor `w1 w2`, cutoff `beta = min(|w1|,|w2|)`) and one box-spline-
sums over the plus legs. The unifying principle, confirmed here, is:

> partition the n legs as **2 special legs + (n-2) summed legs**; the summed set is
> box-spline-summed (truncated-power order n-2, exponent n-3); this is a *single
> polynomial* (no poles) exactly when one sign-class has exactly 2 legs.

For three-minus this clean case is **n = 5 only**, where the plus class has exactly
2 legs {4,5}; they become the special pair and the box-spline sum runs over the 3
minus legs. (Idea contributed/confirmed in-run: "n=5 = two-minus with +/- swapped".)

**Validation (all EXACT, away from walls):**
- 89/89 integer-grid points (w2<=w3 in 1..6, w4 in 1..6).
- 385/385 fresh held-out random points (seed 4242) across regimes: generic,
  one plus freq huge, one plus freq tiny, one minus freq huge.
- 479 earlier random/extreme points.
- g-dependence: exact at g=1,2,3.
- Only true chamber-wall points (|w_plus| = |w_minus|, oracle 0/0) are excluded.

A_5 is **continuous, piecewise-polynomial, pole-free** (a box spline), exactly like
the two-minus sector.

---

## 3. n >= 6 (genuinely piecewise-RATIONAL; full simple closed form open)

At n=6 neither sign-class is a pair (3 minus, >=3 plus), so the box-spline collapse
fails and **factorization poles survive**: `B_n` becomes a *rational* function,
piecewise across kinematic chambers. This is the "genuinely new structure at n=6"
anticipated by the prompt. Established and validated facts:

### 3a. It is rational, not polynomial
In a wall-free interval a **pure-polynomial fit fails**, while a rational fit
succeeds with a nontrivial denominator (degN=4, degD=3 on a test line). So `B_6`
is not a box spline.

### 3b. Pole / denominator structure
Within a chamber, `B_n = P / D` with `P` a symmetric polynomial and
```
  D = PRODUCT over minus-plus pairs {i,j} of  (omega_i + omega_j),
```
i.e. the factors are the 2-point **propagator denominators** of the minus-plus
channels. The active pairs are exactly the **same-sign** minus-plus pairs (omega_i, omega_j
with the same sign), i.e. the pairs with `|omega_i + omega_j| = |omega_i| + |omega_j|`.
Verified across **four distinct chambers** (all with frequency-sign pattern
(-,+,+,+,+,-)); e.g. the canonical chamber exact denominator is
```
  D = (w1+w6)(w2+w4)(w2+w5)(w3+w4)(w3+w5)      [up to sign]
```
(the {1,6} factor enters as s = w2+w3+w4+w5 = -(w1+w6) in the free-variable solve).
In each chamber tested, varying any free leg, the denominator's varied-leg factors are
exactly `(w_varied + w_partner)` over its same-sign partners — e.g. base (2,3,4,7)
gives D|_{vary w4} = (w4+2)(w4+3)(w4+12); base (1,2,5,4) gives (w5+1)(w5+2)(w5+8);
base (2,4,6,3) gives (w4+2)(w4+4)(w4+9). The number of same-sign pairs varies by
chamber (observed 0..5 across sign patterns), so `deg D` is chamber-dependent — which
is why there is no single fixed-degree global denominator.

### 3c. Wall structure (chamber boundaries)
Chambers are bounded by **subset-momentum walls** `SUM_{i in S} sigma_i omega_i^2 = 0`
(equivalently `|k_minus| = |k_plus|` for a subset). The oracle returns 0/0 exactly
on these walls; `B_n` itself is finite and continuous across them, with the rational
expression switching form. Example wall set on a line: w5 = ±w2, ±w3, w5^2 = w2^2+w3^2.

### 3d. Explicit validated n=6 chamber formula (concrete instance)
In the canonical chamber, fixing the two free minus legs w2=2, w3=3 (with w4,w5 the
two free plus legs, w1,w6 solved on-shell), the EXACT amplitude is
```
                  -3456 * N(w4,w5)
  B_6 = ----------------------------------------------,   s = w2+w3+w4+w5 = 5+w4+w5
        s*(w4+2)(w4+3)(w5+2)(w5+3)

  N(w4,w5) = 55 w4^4 w5^2 + 275 w4^4 w5 + 260 w4^4
           + 55 w4^3 w5^3 + 799 w4^3 w5^2 + 2810 w4^3 w5 + 2288 w4^3
           + 55 w4^2 w5^4 + 799 w4^2 w5^3 + 4515 w4^2 w5^2 + 10307 w4^2 w5 + 6500 w4^2
           + 275 w4 w5^4 + 2810 w4 w5^3 + 10307 w4 w5^2 + 15240 w4 w5 + 5928 w4
           + 260 w5^4 + 2288 w5^3 + 6500 w5^2 + 5928 w5
```
`N` is symmetric in w4<->w5 (as required) and irreducible over Q.
**Validation:** EXACT on 625 single-chamber grid points used to fit, plus 40/40
fresh exact in-chamber points. (The chamber was certified single by a
subset-momentum signature check, `scripts/chamber.py`.)

### 3e. General-n evaluation
A faithful Python re-implementation of the Berends-Giele oracle (`scripts/sym_engine.py`)
reproduces `bg.cpp` **exactly** at n=5,6,7 (e.g. n=6: -29948208/17; n=7:
-2242013037888/32725). It evaluates `A_n` for arbitrary n and kinematics, and (run
symbolically in a fixed chamber) returns the exact per-chamber rational function.

### 3f. What is NOT claimed for n>=6
A single simple closed form (one compact symmetric expression like the n<=5 box
spline) was **not** found, and the most natural candidate was **rigorously excluded**:
a modular consistency test (mod the prime 2^31-1, across many chambers, weighted
degrees 13..20) shows that `B * PRODUCT_{all 9 minus-plus pairs}(omega_i+omega_j)` is
NOT a global symmetric polynomial (full-rank but inconsistent at every degree). Hence
there is no clean global form `B = polynomial / PRODUCT(omega_i+omega_j)`. The
per-chamber numerators are high-degree, irreducible symmetric polynomials with no
clean factorization, and the active-pole set changes across chambers. This matches the open-problem status (the methodological-parent
"single-minus" amplitude papers likewise leave the general-kinematics simplification
to future work). The complete, validated description for n>=6 is: pure-imaginary,
homogeneous degree 2(n-2), symmetric in each sign-class, piecewise-rational with
minus-plus propagator poles `(omega_i+omega_j)` and subset-momentum chamber walls,
plus the exact evaluator and the explicit canonical-chamber n=6 formula above.

---

## 4. Numerical evidence (summary table)

| n | claim | test set | result |
|---|-------|----------|--------|
| 4 | A_4 = 0 | 3 points | exact 0 |
| 5 | box-spline closed form (sec. 2) | 89 grid + 385 fresh + 479 extreme; g=1,2,3 | ALL exact |
| 6 | rational (not polynomial) | wall-free line fit | poly fails, rational degD=3 |
| 6 | denominator = same-sign minus-plus (w_i+w_j) | 4 distinct chambers | exact |
| 6 | canonical chamber formula (sec. 3d) | 625 fit + 40 fresh | ALL exact |
| 6,7 | engine == oracle | exact points | exact match |
| 5,6,7 | homogeneity 2(n-2), sign-class symmetry | multiple | confirmed |

"Exact" = identical rational to `bg.cpp` GMP output (relative error 0, well under the
1e-10 bar). All tests are away from genuine walls/poles, as required.

---

## 5. How the discovery policy evolved

- **v0 -> v1:** after two pure-polynomial "box-spline pair-sum" candidates scored
  0/58 at n=6 (Trigger B), added the rule: *determine the analytic structure
  (polynomial vs rational; pole/denominator factors; chamber walls) BEFORE proposing
  a closed-form candidate.* This redirected effort from blind ansatz-fitting to
  scans + exact rational interpolation + symbolic chamber computation, which is what
  revealed the rational/pole/chamber structure. See `policy_history.md`,
  `POLICY_AUDIT.md`.

## 6. Reproducing everything
`scripts/harness.py` (oracle wrapper + kinematics), `formulas.py` (the closed forms),
`verify.py` (exact/double validation batches), `rational_interp.py` (1-var rational
fits), `chamber.py` (chamber signatures / single-chamber boxes), `sym_engine.py`
(faithful symbolic BG engine), `fit2d_v3.py`/`fit4d.py` (chamber numerator fits),
`gendata.py`/`explore.py` (data + invariants). Build the oracle:
`g++ -O2 -std=c++17 -o bg ../bg.cpp -lgmpxx -lgmp`.
