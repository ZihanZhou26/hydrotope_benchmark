# Closed-form result for the two-minus sector

## Formula

Take the two `sigma=-1` frequencies and call them `s` and `h`, with

```text
s^2 <= h^2 .
```

Thus `s` is the smaller-magnitude negative-momentum frequency and `h` is
the other one.  Let

```text
U = s^2,
m = n - 3,
{x_1 <= x_2 <= ... <= x_{n-2}} = sort({omega_j^2 : sigma_j = +1}).
```

Define

```text
r = min(m, number of x_j with x_j < U)
```

and the finite-difference polynomial

```text
G_m(U; x) =
  sum_{S subset {1,...,r}} (-1)^|S| (U - sum_{j in S} x_j)^m .
```

Then the on-shell tree amplitude in the two-minus sector is

```text
A_n = i 2^(n-1) g^(3-n) h s G_{n-3}(s^2; {omega_j^2}_{sigma_j=+1}) .
```

Useful special cases:

```text
r = 0:       G_m = U^m
r = m:       G_m = m! x_1 x_2 ... x_m
```

For `n=5` (`m=2`), this gives

```text
G_2 = U^2                                      if U < x_1
G_2 = U^2 - (U - x_1)^2                       if x_1 < U < x_2
G_2 = U^2 - (U - x_1)^2 - (U - x_2)^2
        + (U - x_1 - x_2)^2 = 2 x_1 x_2       if x_2 < U .
```

Degenerate equalities are chamber-boundary limits.  The exact `n=4`
two-minus manifold is entirely degenerate in the supplied BG recursion: a
zero-energy/zero-momentum two-point subcurrent appears, so raw
`BGAmplitude` returns `Indeterminate`.  The finite continuation of the
formula has `m=1`, hence `G_1=U`; for example
`omega={-3,2,3,-2}` gives `A_4 = -192 i / g`.

## Evidence

I evaluated the formula against the supplied `BGAmplitude` with exact
rational arithmetic at `g=1`.  The nonzero checks below all returned
`Simplify[BGAmplitude - formula] == 0`, so the numerical relative error is
zero before floating-point evaluation.

| n | free frequencies passed to `MakeKinematics` | BG amplitude | formula difference |
|---|---:|---:|---:|
| 5 | `{2,3,5}` | `-3328 I` | `0` |
| 5 | `{-3,1,12}` | `(458784 I)/125` | `0` |
| 5 | `{2,-3,10}` | `(-888832 I)/243` | `0` |
| 5 | `{4,1,8}` | `(-216256 I)/13` | `0` |
| 5 | `{8,1,4}` | `(-249856 I)/13` | `0` |
| 5 | `{1/3,2,9}` | `(-2560 I)/4131` | `0` |
| 5 | `{2,7,11}` | `(-36224 I)/5` | `0` |
| 6 | `{2,3,5,7}` | `(-753664 I)/17` | `0` |
| 6 | `{1,4,9,16}` | `(-10016 I)/15` | `0` |
| 6 | `{-3,1,5,20}` | `(2502101403648 I)/6436343` | `0` |
| 6 | `{-3,1,12,20}` | `(2492896 I)/5` | `0` |
| 6 | `{4,1,8,10}` | `(-31285632 I)/23` | `0` |
| 6 | `{8,1,4,10}` | `(-396914688 I)/23` | `0` |
| 6 | `{20,1,4,8}` | `-45875200 I` | `0` |
| 6 | `{2,-3,10,11}` | `(-320512 I)/5` | `0` |
| 6 | `{-10,1,2,30}` | `8017920 I` | `0` |
| 6 | `{-5,1,2,20}` | `(44154880 I)/243` | `0` |
| 7 | `{2,3,5,7,11}` | `(-4030464 I)/7` | `0` |
| 7 | `{1,4,9,16,25}` | `(-128064 I)/55` | `0` |
| 7 | `{-3,1,5,20,21}` | `15026640 I` | `0` |

These points cover:

- `r=0`, where all positive-sector squared frequencies are above `s^2`;
- intermediate chambers such as `r=1` and `r=2`;
- saturated chambers with `r=m`;
- mixed signs among the free frequencies;
- a small-frequency regime, e.g. `n=5`, `{1/3,2,9}`.

## How the formula was found

I normalized the exact BG data by

```text
A_n / (i 2^(n-1) h s)
```

after choosing the smaller-magnitude `sigma=-1` frequency `s`.  The
normalized values depended only on `U=s^2` and the ordered positive-sector
squares below `U`.

At five points (`m=2`) the chambers gave

```text
U^2
U^2 - (U - x_1)^2
U^2 - (U - x_1)^2 - (U - x_2)^2 + (U - x_1 - x_2)^2 .
```

At six points (`m=3`) the next chamber was

```text
U^3 - (U - x_1)^3 - (U - x_2)^3
  + (U - x_1 - x_2)^3 ,
```

and the saturated chamber reduced to `6 x_1 x_2 x_3`.  This identified the
general `m`th finite difference written above.  I then tested the resulting
closed form against fresh BG evaluations at `n=5,6,7`.

