# Benchmark task — closed-form A_n in the THREE-minus sector (open problem)

## Physical setup

We are computing tree-level n-point on-shell scattering amplitudes for 1D
surface water waves in deep water. The dispersion relation is

    omega_i^2 = g |k_i|,

so each leg's momentum is fixed by its frequency up to a sign:

    k_i = sigma_i omega_i^2 / g,    sigma_i in {+1, -1}.

All momenta and frequencies are incoming, so on the resonant manifold both
conservation laws hold:

    sum_i omega_i = 0,    sum_i sigma_i omega_i^2 = 0.

## Amplitude oracle (bg.cpp)

You are given a fast, exact Berends-Giele amplitude oracle as C++ source,
`bg.cpp` (GMP exact rational arithmetic -- the results are rigorous, not
floating point). Build it once:

    g++ -O2 -o bg bg.cpp -lgmpxx -lgmp

It returns the tree amplitude A_n in two ways:

- On-shell, via the kinematic solver (the natural way to sample the resonant
  manifold):

      ./bg -n N -w <comma list of the n-2 free frequencies> -s <comma list of the n signs> [-g 1]

  It solves energy+momentum conservation for legs 1 and n from the n-2 free
  frequencies and the sign vector sigma (requires sigma_1 + sigma_n = 0), then
  prints A_n exactly (and a numeric value).

- Raw, for arbitrary kinematics you build yourself:

      ./bg --amp -K <comma list of the n momenta> -W <comma list of the n frequencies> [-g 1]

For fast bulk scans (e.g. fitting at higher n) add `--double` to either mode
to use long-double arithmetic instead of exact rationals (about 4x faster and
it avoids the exact-rational blow-up at large n); always re-confirm a final
formula in the default exact mode.

You may query as many n and kinematic points as you like, and you may read,
extend, or reimplement `bg.cpp`.

## Sector

The THREE-minus sector is

    sigma = (-1, -1, -1, +1, +1, ..., +1)

-- legs 1, 2, 3 carry sigma_i = -1; the remaining n-3 legs carry sigma_i = +1.
(Use `-s -1,-1,-1,1,...,1`.)

## Known results and physical intuition (use these as a starting point)

Two neighbouring sectors are already understood; use them as ground truth and as
a guide. You can reproduce both with the oracle.

1. One-minus sector vanishes. For sigma = (-1, +1, +1, ..., +1) (a single minus
   leg) the on-shell amplitude is identically zero, A_n = 0, for every n.
   (Check, e.g., `./bg -n 5 -w 2,3,5 -s -1,1,1,1,1`.)

2. Two-minus closed form. For sigma = (-1, -1, +1, ..., +1) the amplitude is the
   piecewise-polynomial "truncated power" law

       A_n = i * 2^(n-1) * g^(3-n) * omega_1 * omega_2
               * sum_{S subset {3,...,n}} (-1)^|S| ( beta^2 - sum_{j in S} omega_j^2 )_+^(n-3),

   where beta = min(|omega_1|, |omega_2|) and (x)_+ = max(x, 0). It is continuous
   and piecewise-homogeneous across kinematic chambers, and has NO poles in this
   sector.

Physical intuition for the three-minus sector (conjectural -- test it against the
oracle, do not assume it):

- At n = 5 the two-minus and three-minus sectors are expected to have the SAME
  type of closed form; the genuinely new three-minus structure is expected to
  begin at n = 6. So pin down n = 5 first, then study n = 6 hard.
- Chambers (piecewise behaviour) should appear where a subset sum of the momenta
  vanishes, i.e. where sum_{i in S} k_i = 0  (equivalently sum_{i in S} sigma_i
  omega_i^2 = 0). These are the walls where the kernel magnitudes |k_S| switch
  sign.
- Poles should appear where an internal line goes on-shell, i.e. where a
  propagator denominator omega_S^2 / |k_S| - g vanishes (a physical
  factorization channel). Unlike the two-minus sector, the three-minus amplitude
  can carry such poles, so expect a rational (not purely polynomial) structure in
  general.

## Task

Find a closed-form analytic formula for A_n in the three-minus sector, valid for
all n >= 5 and for arbitrary kinematics in this sector (n = 4 is a degenerate
boundary you may treat separately).

This is a genuine open research problem: as far as is known, no closed form for
this sector has been written down. If a single clean closed form does not exist,
give the most complete validated description you can -- e.g. a formula valid on
explicitly stated regions/chambers (and any pole structure), together with any
auxiliary quantities you define.

## What you may use

- You MAY use online search and the scientific literature for methods, context,
  and related results. (This is an open problem; external methods are allowed.)
- For heavy computation (large n, large scans) you MAY submit jobs to the Typhon
  SLURM cluster; see `IAS_COMPUTE_GUIDE.md` (submit via `ssh typhon-login1 'sbatch ...'`).
- Use `bg.cpp` (or your own faithful reimplementation) for all amplitude values.
  Do not assume an answer from memory; validate everything against the oracle.

## What to report

1. The formula -- written explicitly as a function of {omega_1, ..., omega_n}
   (and any auxiliary quantities you define), with its domain of validity
   (chambers and/or poles).
2. Numerical evidence -- your formula vs the oracle at a range of n (at least
   n = 5, 6, 7) and at multiple kinematic points per n, including non-generic
   regimes (one frequency much larger or smaller than the others, and points
   approaching the chamber walls / factorization poles above).
3. Brief reasoning -- how you arrived at the conjecture (data fitting, ansatz,
   structural argument, literature, ...).

A passing claim must agree with the oracle to <= 1e-10 relative error (exact
agreement where the oracle is exact) at every kinematic point you test, across
all n you test, away from genuine poles.
