# Closed-form A_n in the two-minus sector (1D deep-water surface waves)

## Physical setup

We compute tree-level n-point on-shell scattering amplitudes for **1D surface
water waves** in deep water. The dispersion relation is

$$\omega_i^2 = g\,|k_i|, \qquad k_i = \sigma_i\,\omega_i^2/g,\quad \sigma_i\in\{+1,-1\}.$$

All momenta/frequencies are incoming, so on the resonant manifold

$$\sum_{i=1}^{n}\omega_i = 0, \qquad \sum_{i=1}^{n}\sigma_i\,\omega_i^2 = 0.$$

## The oracle (`bg.cpp`)

A self-contained Berends–Giele evaluator is provided in `bg.cpp` (exact GMP
rational by default; `--double` for fast `long double`). It is a pure amplitude
evaluator — it contains no closed form / no answer.

**Build (this machine):**
```
# macOS (Homebrew GMP):
g++ -O2 -std=c++17 -I"$(brew --prefix gmp)/include" -L"$(brew --prefix gmp)/lib" -o bg bg.cpp -lgmpxx -lgmp
# Linux (after: sudo apt-get install -y libgmp-dev g++):
g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp
```

**Use:**
- On-shell amplitude: `./bg -n N -w <n-2 free freqs> -s <n signs> [-g 1]`
  (e.g. `./bg -n 5 -w 2,5/2,3 -s -1,-1,1,1,1`).
- Raw amplitude: `./bg --amp -K <n momenta> -W <n omegas> [-g 1]`.
- Fast double mode: add `--double`.

## Sector

The **two-minus sector** is `σ = (-1,-1,+1,…,+1)` — legs 1 and 2 have
`σ_i = -1`, the remaining `n-2` legs have `σ_i = +1`.

## Task

Find a **closed-form analytic formula for `A_n` in the two-minus sector**, valid
for all `n ≥ 4` and arbitrary in-sector kinematics. You must report:

1. **The formula** — explicit as a function of `{ω_1,…,ω_n}` (define any
   auxiliary quantities).
2. **Numerical evidence** — your formula vs `BGAmplitude` at `n = 4,5,6,7` and
   multiple kinematic points per `n`, including non-generic regimes (one
   frequency ≫ or ≪ the others).
3. **Brief reasoning** — how you arrived at the conjecture.

**Pass bar:** agreement with `BGAmplitude` to ≤ 10⁻¹⁰ relative error at every
tested point, across all tested `n`.

## Hard constraints — read carefully

- **No external information of any kind, for everyone (PI and students).** Do
  NOT use web search, do NOT fetch or browse URLs, do NOT consult arXiv/ADS/any
  literature, datasets, or other AI models. Work only from this `question.md`,
  `bg.cpp`, and data you generate by running the code.
- **Read only this question's own working tree.** You may read: this
  `question.md`, `bg.cpp`, `board.json`, any bot's `sessions/` and
  `claims.yaml`/`figures.yaml`/`decisions.yaml`, `notebooks/`, and files the team
  generates inside `questions/waterwaves/`. Do NOT read other question
  directories, parent-directory files, or anything elsewhere on the machine.
- **Keep the shared oracle pristine.** Never modify `bg.cpp` in this directory in
  place. If you want to extend/rewrite/port it, copy it into your own bot
  directory first (e.g. `bots/<you>/code/bg.cpp`) and work on the copy.
- You **may** generate amplitudes at any `n`/kinematics, write scratch
  scripts/notebooks/data inside your own bot directory, and read those back.

## Definition of done

A formula is accepted only when the **PI independently verifies** it against the
oracle (rebuilt/run by the PI itself) at `n = 4,5,6,7` and multiple kinematic
points including non-generic limits, all to ≤ 10⁻¹⁰. On acceptance the PI writes
`summary/SOLVED.md` and the run stops.
