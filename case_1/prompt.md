# Benchmark task — closed-form A_n in the two-minus sector


## Physical setup

We are computing tree-level n-point on-shell scattering amplitudes for **1D
surface water waves** in deep water. The dispersion relation is

$$\omega_i^2 = g\,|k_i|,$$

so for each leg the momentum is determined by its frequency up to a sign:

$$k_i = \sigma_i\,\omega_i^2 / g,\qquad \sigma_i \in \{+1,\,-1\}.$$

All momenta and frequencies are taken **incoming**, so on the resonant
manifold both conservation laws hold:

$$\sum_{i=1}^{n}\omega_i = 0,\qquad \sum_{i=1}^{n}\sigma_i\,\omega_i^2 = 0.$$

## Berends–Giele code

You are given a self-contained BG implementation in `OnShellBG.m`
(Wolfram Language). The relevant entry points:

- `BGAmplitude[momenta, omegas, g]` — tree amplitude `A_n` from the BG
  recursion. Exact rational arithmetic. Slow at high `n` (n ≳ 8 starts to
  hurt with symbolic kinematics, fine for moderate `n` with rational input).
- `MakeKinematics[n, freeFreqs, sigmas, g]` — solves the conservation
  equations for `{w_1, w_n}` given `n−2` free frequencies and a sign vector
  `sigma`. Returns `{momenta, signedOmegas}` ready to feed into
  `BGAmplitude`.

Run it via `wolframscript -file OnShellBG.m` (or load interactively in a
Mathematica session). You are free to **modify, rewrite, extend, or
reimplement** the BG code — for example, porting to a faster numerical
backend if you need many high-`n` evaluations.

## Sector

The **two-minus sector** is

$$\sigma = (-1,\,-1,\,+1,\,+1,\,\dots,\,+1)$$

— exactly two legs (legs 1 and 2) have $\sigma_i = -1$; the remaining
$n - 2$ legs have $\sigma_i = +1$.

## Task

**Find a closed-form analytic formula for $A_n$ in the two-minus sector,
valid for all $n \geq 4$ and for arbitrary kinematics in this sector**
(i.e. arbitrary free frequencies satisfying the on-shell condition above).

### Hint

The amplitude $A_n$ is a **rational function** of the frequencies
$\{\omega_i\}$ — a single global, analytic expression valid throughout the
entire two-minus sector. Concretely:

- like any tree-level amplitude assembled from exchange (propagator)
  diagrams, $A_n$ is a **ratio of polynomials** $N(\omega)/D(\omega)$. The
  denominator $D$ is the product of the **physical factorization-channel
  factors** — one factor per intermediate multi-leg sub-energy
  $\omega_S = \sum_{i\in S}\omega_i$ that can go on shell — so $A_n$ carries
  **simple poles** on those channels;
- the efficient route is a **single global ansatz**: take $D(\omega)$ to be
  the product of the channel factors, write $N(\omega)$ as a generic
  homogeneous polynomial of the matching degree, and fix the numerator
  coefficients by matching `BGAmplitude` at enough kinematic points. A few
  hundred points overdetermine $N$ and pin the formula uniquely — one fit,
  valid for all of the sector;
- the result is a **single rational function** valid everywhere in the
  sector — there is **no** piecewise / chamber decomposition, no absolute
  values, and no $\min$/$\max$; the answer is emphatically **not** a plain
  polynomial.

For a well-conditioned fit, sample your points from **generic** kinematics,
with all $|\omega_i|$ of comparable magnitude. Deliberately avoid
hierarchical or near-degenerate configurations (one frequency much larger or
much smaller than the rest): those only make the numerator linear system
ill-conditioned and waste evaluations — they reveal nothing new about a
single global rational function.

### What to report

### Constraints

You are **only allowed to read two files** during this task:

1. this prompt (`prompt.md`)
2. the BG implementation (`OnShellBG.m`)

You may **not** read any other pre-existing file — no sibling files in
this directory, no files in any parent directory, no files elsewhere on
the machine.

Online search and literature lookup are **not** permitted. Do **not**
use any web-search tool, do **not** fetch or browse URLs, and do **not**
consult any external literature, datasets, or other AI models. Work
**only** from this prompt, `OnShellBG.m`, and data you generate yourself
by running the code.

You **may**:

- run / extend / rewrite / replace `OnShellBG.m` (the file is yours to
  edit)
- generate amplitudes at as many `n` and kinematic points as you want
- write new files inside this directory (scratch scripts, notebooks,
  fitting output, your own faster numerical BG, etc.) and read those
  files back

You must report:

1. **The formula** — written explicitly as a function of
   $\{\omega_1,\ldots,\omega_n\}$ (and any auxiliary quantities you need to
   define).
2. **Numerical evidence** — your formula evaluated against `BGAmplitude` at
   a range of `n` (at least `n = 4, 5, 6, 7`) and at multiple generic
   kinematic points per `n`.
3. **Brief reasoning** — how you arrived at the conjecture (data fitting,
   ansatz, structural argument, …).

A passing answer must agree with `BGAmplitude` to machine precision (≤ 10⁻¹⁰
relative error after numerical evaluation) at every kinematic point you
test, across all `n` you test.
