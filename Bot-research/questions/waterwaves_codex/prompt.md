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

You are given a self-contained BG implementation in `bg.cpp` (C++). It is a
faithful transcription of the Berends–Giele recursion
(`EKernel` / `FKernel` / `Vertex` / `Propagator` / `SetPartitions` /
`BGCurrent` / `BGAmplitude`) together with the on-shell kinematic solver
`MakeKinematics`. The engine is templated on the real scalar type, so the
**exact** (GMP `mpq_class` rational) and **fast** (`long double`) paths run the
same algorithm.

Build it with:

```
g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp
```

Then call the `./bg` command-line oracle:

- **On-shell amplitude** (kinematic solver + BG recursion, exact rational):

  ```
  ./bg -n N -w <n-2 free freqs> -s <n signs> [-g 1]
  ```

  `-n` is the number of legs `N`; `-w` the `n−2` free frequencies
  `w_2,…,w_{n-1}` (comma-separated, fractions like `5/2` allowed); `-s` the full
  `n`-component sign vector `σ`; `-g` gravity (default `1`). The tool solves the
  conservation equations for `{w_1, w_n}` (it requires `σ_1 + σ_n = 0`), forms
  the momenta `k_i = σ_i w_i^2 / g`, runs `BGAmplitude`, and prints `A_N` as an
  exact rational (plus a numeric value). Example (two-minus, `n = 5`):

  ```
  ./bg -n 5 -w 2,5/2,3 -s -1,-1,1,1,1
  ```

- **Raw amplitude** on momenta/frequencies you supply directly:

  ```
  ./bg --amp -K <n momenta> -W <n omegas> [-g 1]
  ```

- **Fast double-precision mode** (same algorithm, `long double`): add
  `--double`, e.g. `./bg --double -n 8 -w 1,2,3,4,5,6 -s -1,-1,1,1,1,1,1,1`.

Exact (GMP rational) arithmetic is the default, so results are rigorous; it
slows at high `n` (the vertex sums over `n!` permutations), where `--double` is
useful for fast scans. You are free to **modify, rewrite, extend, or
reimplement** the BG code — for example, porting to a faster numerical backend
if you need many high-`n` evaluations.

## Sector

The **two-minus sector** is

$$\sigma = (-1,\,-1,\,+1,\,+1,\,\dots,\,+1)$$

— exactly two legs (legs 1 and 2) have $\sigma_i = -1$; the remaining
$n - 2$ legs have $\sigma_i = +1$.

## Task

**Find a closed-form analytic formula for $A_n$ in the two-minus sector,
valid for all $n \geq 4$ and for arbitrary kinematics in this sector**
(i.e. arbitrary free frequencies satisfying the on-shell condition above).

### Constraints

You are **only allowed to read two files** during this task:

1. this prompt (`prompt.md`)
2. the BG implementation (`bg.cpp`)

You may **not** read any other pre-existing file — no sibling files in
this directory, no files in any parent directory, no files elsewhere on
the machine.

Online search and literature lookup are **not** permitted. Do **not**
use any web-search tool, do **not** fetch or browse URLs, and do **not**
consult any external literature, datasets, or other AI models. Work
**only** from this prompt, `bg.cpp`, and data you generate yourself
by running the code.

You **may**:

- run / extend / rewrite / replace `bg.cpp` (the file is yours to
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
   a range of `n` (at least `n = 4, 5, 6, 7`) and at multiple kinematic
   points per `n`, including non-generic regimes (e.g. one frequency much
   larger or much smaller than the others).
3. **Brief reasoning** — how you arrived at the conjecture (data fitting,
   ansatz, structural argument, …).

A passing answer must agree with `BGAmplitude` to machine precision (≤ 10⁻¹⁰
relative error after numerical evaluation) at every kinematic point you
test, across all `n` you test.
