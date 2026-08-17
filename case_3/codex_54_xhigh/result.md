# Two-minus closed form

For the standard `MakeKinematics` branch used in the supplied examples,

- `sigma = (-1, -1, +1, ..., +1)`
- `freeW = {omega_2, ..., omega_{n-1}}`
- `omega_2, ..., omega_{n-1} > 0`, so the solver returns `omega_1 < 0` and `omega_n < 0`

the `n`-point on-shell BG amplitude is

```math
A_n = 2^{n-1}\, i\, \omega_1\, \omega_2^{\,2n-5}, \qquad n \ge 4.
```

Here `omega_1` and `omega_n` are the values solved by `MakeKinematics`. In this normalization the answer is independent of `g` after substituting the on-shell momenta `k_i = sigma_i omega_i^2 / g`.

## How I got it

I copied the BG recursion into [analysis.py](/home/zihanz/waterhedron_benchmark_blind/case_3/codex_54_xhigh/analysis.py) and used it to generate exact rational amplitudes in the two-minus sector. Three patterns emerged immediately:

1. Under `omega_i -> lambda omega_i`, the amplitude scales as `lambda^(2n-4)`.
2. For fixed `n`, the ratio `A_n / (i omega_1 omega_2^(2n-5))` was constant across many kinematic points.
3. Those constants were `16, 32, 64, ...`, i.e. `2^(n-1)`.

I then checked the conjecture directly against the original Wolfram recursion in [verify_formula.wls](/home/zihanz/waterhedron_benchmark_blind/case_3/codex_54_xhigh/verify_formula.wls).

## Numerical evidence

Exact Wolfram checks are in [verify_formula.out](/home/zihanz/waterhedron_benchmark_blind/case_3/codex_54_xhigh/verify_formula.out). Representative points:

| n | freeW | solved omegas `ws` | BGAmplitude | formula |
|---|---|---|---|---|
| 5 | `{1,2,3}` | `{-4,1,2,3,-2}` | `-64 I` | `-64 I` |
| 5 | `{2,5/2,3}` | `{-9/2,2,5/2,3,-3}` | `-2304 I` | `-2304 I` |
| 6 | `{3/2,2,5/2,3}` | `{-49/9,3/2,2,5/2,3,-32/9}` | `-(11907/4) I` | `-(11907/4) I` |
| 6 | `{2,3,4,9}` | `{-71/6,2,3,4,9,-37/6}` | `-(145408/3) I` | `-(145408/3) I` |
| 7 | `{1,2,3,4,5}` | `{-139/15,1,2,3,4,5,-86/15}` | `-(8896/15) I` | `-(8896/15) I` |
| 7 | `{1,4,5,6,20}` | `{-443/18,1,4,5,6,20,-205/18}` | `-(14176/9) I` | `-(14176/9) I` |

Non-generic small-frequency checks are in [extreme_checks.out](/home/zihanz/waterhedron_benchmark_blind/case_3/codex_54_xhigh/extreme_checks.out). Examples:

| n | freeW | BGAmplitude | formula |
|---|---|---|---|
| 5 | `{1/10,3,11}` | `-(274/146875) I` | `-(274/146875) I` |
| 6 | `{1/10,2,5,11}` | `-(597/14140625) I` | `-(597/14140625) I` |
| 7 | `{1/10,2,3,5,13}` | `-(529/515625000) I` | `-(529/515625000) I` |

All of those checks agree exactly, so the relative error is `0`.

## The `n = 4` endpoint

The raw `BGAmplitude` code returns `Indeterminate` at `n = 4` in this branch because the `{2,4}` subcurrent hits an exact removable `0/0` channel. I resolved that by a tiny off-shell deformation of the external momenta in [n4_limit_check.py](/home/zihanz/waterhedron_benchmark_blind/case_3/codex_54_xhigh/n4_limit_check.py); the output is in [n4_limit_check.out](/home/zihanz/waterhedron_benchmark_blind/case_3/codex_54_xhigh/n4_limit_check.out).

For example:

- `freeW = {2,3}` gives `ws = {-3,2,3,-2}` and the formula predicts `A_4 = -192 I`.
- With momentum deformation size `delta = 10^-7`, the regularized BG value is `-191.9999979000000408 I`, a relative error `1.09e-8`.
- `freeW = {3/2,5}` gives `ws = {-5,3/2,5,-3/2}` and the formula predicts `A_4 = -135 I`.
- With the same deformation, the regularized BG value is `-134.9999883000005010 I`, a relative error `8.67e-8`.

So the resolved `n = 4` limit is also consistent with

```math
A_4 = 8\, i\, \omega_1\, \omega_2^3.
```
