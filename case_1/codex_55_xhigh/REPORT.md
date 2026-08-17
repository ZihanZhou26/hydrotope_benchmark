# Two-minus sector: supplied task is inconsistent

## Result

I do not find a closed-form global rational formula because the supplied
`BGAmplitude` does not define a single global rational function in the
two-minus sector as stated in the prompt.

The obstruction already appears at four points.  In the two-minus sector set

```text
sigma = {-1, -1, 1, 1}
free frequencies = {-x, y}, with x > 0, y > 0.
```

The supplied `MakeKinematics` gives

```text
{omega1, omega2, omega3, omega4} = {-y, -x, y, x}.
```

Evaluating the supplied `BGAmplitude` symbolically gives

```text
A4 = Piecewise[
  {{8 I x^3 y, x < y}, {8 I x y^3, x > y}},
  24 I y^4
]
```

The two open-branch formulas differ by

```text
8 I x y (x^2 - y^2).
```

Therefore no single rational function of `x,y` can agree with this expression
on both open sets `x < y` and `x > y`: if a rational function agrees with
`8 I x^3 y` on the open set `x < y`, it is that rational function identically,
and cannot also equal `8 I x y^3` on the open set `x > y`.

This directly contradicts the prompt requirement that the answer be a single
global rational expression with no piecewise/chamber decomposition, valid for
all `n >= 4`.

## Additional issue at n = 4

Direct exact numeric evaluation of the supplied BG code at the same four-point
kinematics is not well-posed.  It hits a zero-momentum internal channel and
returns `Indeterminate`; the finite expression above only appears after
symbolic evaluation leaves the zero channel unevaluated long enough for
cancellations/branching to occur.

This also makes the prompt's requested numerical comparison at `n = 4`
ill-defined for the supplied implementation.

## Reproduction

Run from this folder:

```bash
wolframscript -file verify_n4_contradiction.m
```

The saved output is in `verify_n4_contradiction.out`.

I also generated `bg_numeric.py` and `bg_exact.py`, independent Python ports of
the permitted BG definitions, for nondegenerate numerical exploration at
`n >= 5`.  They match the targeted Wolfram five-point checks I ran, but they do
not remove the four-point contradiction above.
