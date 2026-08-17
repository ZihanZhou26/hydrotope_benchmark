# Two-minus sector formula

For the real `MakeKinematics` chart with

- `sigma = (-1, -1, +1, ..., +1)`
- free frequencies `freeW = {ω2, ω3, ..., ω_{n-1}}`
- `{ω1, ωn}` fixed by conservation,

the BG amplitude is

$$
A_n \;=\; i\,2^{\,n-1}\,\omega_1\omega_2\,
\sum_{S\subseteq\{3,\dots,n-1\}}
(-1)^{|S|}
\Bigl[\omega_2^2-\sum_{j\in S}\omega_j^2\Bigr]_+^{\,n-3},
\qquad n\ge 4,
$$

where

$$
[x]_+ \equiv \max(x,0).
$$

Equivalently, with

$$
B_m(x;x_1,\dots,x_m)
\equiv
\sum_{S\subseteq\{1,\dots,m\}}
(-1)^{|S|}
\Bigl[x-\sum_{i\in S}x_i\Bigr]_+^{\,m},
$$

the amplitude is

$$
A_n = i\,2^{\,n-1}\,\omega_1\omega_2\,
B_{n-3}\!\left(\omega_2^2;\omega_3^2,\dots,\omega_{n-1}^2\right).
$$

## Low-point examples

$$
A_4
=
8i\,\omega_1\omega_2\Bigl([\omega_2^2]_+ - [\omega_2^2-\omega_3^2]_+\Bigr)
=
8i\,\omega_1\omega_2\,\min(\omega_2^2,\omega_3^2).
$$

$$
A_5
=
16i\,\omega_1\omega_2
\Bigl(
\omega_2^4
-[\omega_2^2-\omega_3^2]_+^2
-[\omega_2^2-\omega_4^2]_+^2
+[\omega_2^2-\omega_3^2-\omega_4^2]_+^2
\Bigr).
$$

$$
A_6
=
32i\,\omega_1\omega_2
\sum_{S\subseteq\{3,4,5\}}
(-1)^{|S|}
\Bigl[\omega_2^2-\sum_{j\in S}\omega_j^2\Bigr]_+^3.
$$

## How I found it

1. I copied the recursion core out of `OnShellBG.m` into `bg_core.wl` so I could evaluate amplitudes without the built-in test block.
2. I generated exact rational data in the two-minus sector for many `n=5,6,7` kinematic points.
3. For `n=5`, I extracted exact local formulas with `symbolic_bg.py` in several ordering regions. Those local formulas collapsed to the same inclusion-exclusion pattern in the squared frequencies:

$$
x^2-(x-y)_+^2-(x-z)_+^2+(x-y-z)_+^2.
$$

4. That suggested the general truncated-power / inclusion-exclusion formula above.
5. I then checked the conjecture directly against `BGAmplitude` on exact rational kinematics.

## Numerical evidence

The full verification log is in `verification.txt`. Every `n=5,6,7` point tested there agrees **exactly**:

- `BGAmplitude - ClosedForm = 0`
- relative error `= 0`

Representative checks:

| n | freeW | BGAmplitude |
|---|---|---|
| 5 | `{1,2,3}` | `-64 i` |
| 5 | `{2,1,3}` | `-784 i` |
| 5 | `{5,4,1}` | `-11776 i` |
| 6 | `{1,3/2,2,5/2}` | `-(968/7) i` |
| 6 | `{5/2,2,3,7/2}` | `-(1303400/11) i` |
| 6 | `{4,3,2,1}` | `-(677376/5) i` |
| 7 | `{1,3/2,2,5/2,3}` | `-(1928/5) i` |
| 7 | `{4,3,5/2,2,1}` | `-(426108561/50) i` |
| 7 | `{5/2,7/2,3/2,9/4,3}` | `-(12048407135/8192) i` |

For `n=4`, the raw BG code is `Indeterminate` because every 4-point kinematic configuration in this sector sits on exact zero-momentum internal channels. The same closed form gives a finite limit, e.g.

- `freeW = {2,3}` gives `A_4 = -192 i`
- `freeW = {5/2,7/2}` gives `A_4 = -(875/2) i`

## Files

- `bg_core.wl`: recursion core copied from `OnShellBG.m`
- `symbolic_bg.py`: chamber-fixed symbolic extraction used to recognize the `n=5` pattern
- `verify_formula.wl`: exact verification script
- `verification.txt`: exact check output
