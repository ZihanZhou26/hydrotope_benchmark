# Compact closed-form $A_6$ in the THREE-minus sector

## Physical setup

We are computing tree-level on-shell scattering amplitudes for one-dimensional
surface water waves in deep water. The dispersion relation is

$$
\omega_i^2=g|k_i|,
$$

so each external momentum is

$$
k_i=\sigma_i\frac{\omega_i^2}{g},\qquad \sigma_i\in\{+1,-1\}.
$$

All momenta and frequencies are incoming. On the resonant manifold,

$$
\sum_{i=1}^{6}\omega_i=0,
\qquad
\sum_{i=1}^{6}\sigma_i\omega_i^2=0.
$$

## BG reference code

The supplied `bg.cpp` evaluates the amplitude using exact GMP rational
arithmetic. Build it with

```bash
g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp
```

For on-shell six-point samples, use

```bash
./bg -n 6 -w <omega_2,omega_3,omega_4,omega_5> \
  -s -1,-1,-1,1,1,1 [-g 1]
```

The program solves the two conservation equations for $\omega_1$ and
$\omega_6$. It can also evaluate arbitrary kinematics using

```bash
./bg --amp -K <six momenta> -W <six frequencies> [-g 1]
```

Add `--double` for fast exploratory scans, but recheck every final claim in
exact mode. The shared `bg.cpp` is immutable: copy it into the relevant bot's
directory before building or modifying it.

## Sector

Study only the six-point three-minus sector

$$
\sigma=(-1,-1,-1,+1,+1,+1).
$$

Thus legs $1,2,3$ are minus legs and legs $4,5,6$ are plus legs.

## Known neighboring results

These facts may be used as starting points and calibration checks.

1. **One-minus vanishing.** For
   $\sigma=(-1,+1,\ldots,+1)$, the on-shell tree amplitude vanishes.

2. **Two-minus formula.** For two minus legs $1,2$,

   $$
   A_n=i\,2^{n-1}g^{3-n}\omega_1\omega_2
   \sum_{S\subseteq\{3,\ldots,n\}}(-1)^{|S|}
   \left(\beta^2-\sum_{j\in S}\omega_j^2\right)_+^{n-3},
   \qquad
   \beta=\min(|\omega_1|,|\omega_2|),
   $$

   where $(x)_+=\max(x,0)$.

3. **Global sign flip.** The amplitude is invariant under
   $k_i\mapsto-k_i$ for every leg at fixed frequencies. At five points this
   maps the three-minus sector to the known two-minus sector, so $A_5$ is
   available as a lower-point calibration. This does not determine $A_6$.

The following are physical expectations to test, not assumptions:

- chamber walls can occur when a momentum subset sum vanishes,
  $k_S=\sum_{i\in S}k_i=0$;
- possible factorization poles occur when an internal line goes on shell,
  $\omega_S^2/|k_S|-g=0$.

## Task

Find a closed-form analytic formula for the complete six-point amplitude

$$
A_6(\omega_1,\ldots,\omega_6)
$$

in the three-minus sector, valid for arbitrary nondegenerate on-shell
kinematics. The answer must give every chamber prescription and every genuine
pole/factorization prescription needed to evaluate it throughout the full
six-point domain.

The goal is specifically $A_6$, not an all-$n$ formula. A result only for one
chamber, a numerical fit without an explicit analytic expression, or a rewrite
of the BG recursion is not a solution.

### Compactness requirement

A representation based on stored chamber polynomials, a large coefficient
table, or a flag-by-flag lookup is **not accepted as a closed formula for this
task**. Likewise, a divided-difference or residue notation that merely hides
such a table or lookup does not solve the compactness problem.

Continue the research until the numerator is reduced to a genuinely
human-readable analytic construction: for example a short set of symmetric
building blocks, finite orbit sums, positive-part/truncated-power terms,
determinants, residues whose integrand is explicitly compact, or another
comparably concise structure. The main mathematical content must be visible in
the written formula rather than hidden in a large coefficient file.

## Allowed resources

- Build, query, copy, extend, or faithfully reimplement `bg.cpp` inside a bot's
  own directory.
- Use Python, Julia, C++, symbolic algebra, exact interpolation, numerical
  fitting, and mathematical derivations.
- Use online search and scientific literature, citing any relied-upon source.
- Use Typhon for computations that genuinely require it, following
  `IAS_COMPUTE_GUIDE.md` and the detached-job protocol in the role prompts.
- Do not consult other AI systems or any prior local run. All agents must remain
  inside this question tree for local file access.

## Required result

The final result must contain:

1. An explicit analytic formula for $A_6$ in terms of
   $\{\omega_1,\ldots,\omega_6\}$ and $g$, with every auxiliary quantity
   defined.
2. The exact chamber selection rule and genuine pole prescription, including
   boundary/limiting behavior where relevant.
3. A concise derivation or structural argument explaining the formula.
4. A self-contained evaluator and verification script that compares the formula
   with a freshly built copy of `bg.cpp` and reports residuals.
5. A compactness account: identify the finite analytic building blocks, count
   their terms or orbit representatives, and explain how they generate every
   chamber numerator. The evaluator for the final formula must construct the
   numerator from these building blocks and must not load a large
   chamber-specific coefficient table or an equivalent fitted lookup.

## Definition of done

The PI must independently implement and verify the proposed formula rather than
trust a student's evaluator. Acceptance requires:

- exact agreement wherever exact evaluation is practical and relative error at
  most $10^{-10}$ otherwise;
- at least 20 distinct generic six-point samples spanning different chambers;
- permutations within the three minus legs and within the three plus legs;
- hierarchical regimes with one frequency much larger or smaller than the
  others;
- two-sided approaches to representative chamber walls and every distinct
  candidate pole orbit;
- a five-point calibration check confirming the BG harness against the known
  sign-flipped two-minus formula.

In addition, the PI must inspect the final formula itself and confirm all of the
following before declaring success:

- the formula can be displayed completely in `summary/SOLVED.md` using a small
  number of defined analytic building blocks and finite symmetry/orbit rules;
- its essential content is not a list of hundreds of chamber-specific
  coefficients;
- its evaluator reconstructs $A_6$ without reading a chamber-specific
  coefficient table or a repackaged equivalent;
- exact equality to fresh BG data is demonstrated across the physically
  realized chamber patterns and the required wall/limit tests.

On acceptance, the PI writes `summary/SOLVED.md` containing the formula,
chamber/pole domain, exact tested points and residuals, independent verification
method, and the student/session that produced the result. If the round budget
ends first, `summary/FINAL_SUMMARY.md` must state the best verified progress and
the precise remaining obstruction; it must not label a partial result solved.
