# Closed-form two-minus amplitude

For the two-minus sector

```text
sigma = (-1, -1, +1, ..., +1)
```

write

```text
P = {3, 4, ..., n}
q_j = omega_j^2  for j in P
r = min(omega_1^2, omega_2^2)
Q_S = sum_{j in S} q_j
```

and define the truncated power

```text
(x)_+^m = x^m  if x > 0,
          0    if x < 0.
```

On chamber boundaries use the continuous limiting value. Since `m = n - 3 > 0`,
terms with `x = 0` contribute zero.

The conjectured closed form is

```text
A_n = i 2^(n-1) omega_1 omega_2
      sum_{S subset {3,...,n}} (-1)^|S| (r - Q_S)_+^(n-3).
```

Equivalently, each chamber is determined by the inequalities

```text
omega_1^2 < omega_2^2  or  omega_2^2 < omega_1^2
Q_S < r                or  Q_S > r     for every S subset {3,...,n}.
```

Inside one chamber, remove the inactive subsets `Q_S > r`; the remaining
finite sum is an ordinary homogeneous polynomial of total degree `2n - 4` in
the frequencies.

## Notes on n = 4

At four points, real two-minus resonance is pairwise/trivial, so the raw
`BGAmplitude` recursion hits `0/0` internal zero-momentum currents. The formula
above gives the finite continuous boundary value:

```text
A_4 = i 8 omega_1 omega_2 min(omega_1^2, omega_2^2).
```

I checked this by splitting the two positive external momenta by a symbolic
`delta` while keeping total momentum conserved, evaluating BG, and taking
`delta -> 0+`.

## Numerical evidence

The table gives `A_n / i`. The BG and formula columns agree exactly in rational
arithmetic for these non-boundary cases; relative error is therefore zero.

| n | free frequencies used in `MakeKinematics` | signed on-shell `omega` | BG `A_n/i` | formula `A_n/i` |
|---|---|---|---:|---:|
| 4 | boundary limit | `{-3, 2, 3, -2}` | `-192` | `-192` |
| 4 | boundary limit | `{-5, 1, 5, -1}` | `-40` | `-40` |
| 5 | `{2, 5/2, 3}` | `{-9/2, 2, 5/2, 3, -3}` | `-2304` | `-2304` |
| 5 | `{5, 1, 2}` | `{-11/4, 5, 1, 2, -21/4}` | `-1760` | `-1760` |
| 5 | `{-1, 2, 5}` | `{-16/3, -1, 2, 5, -2/3}` | `14336/243` | `14336/243` |
| 6 | `{3/2, 2, 5/2, 3}` | `{-49/9, 3/2, 2, 5/2, 3, -32/9}` | `-11907/4` | `-11907/4` |
| 6 | `{1, -2, 3, 4}` | `{-16/3, 1, -2, 3, 4, -2/3}` | `-309248/2187` | `-309248/2187` |
| 6 | `{5, 1, 2, 3}` | `{-5, 5, 1, 2, 3, -6}` | `-172800` | `-172800` |
| 7 | `{3/2, 2, 5/2, 3, 7/2}` | `{-371/50, 3/2, 2, 5/2, 3, 7/2, -127/25}` | `-7302393/400` | `-7302393/400` |
| 7 | `{1, -2, 3, 4, 5}` | `{-87/11, 1, -2, 3, 4, 5, -34/11}` | `-5568/11` | `-5568/11` |
| 7 | `{5, 1, 2, 3, 9/2}` | `{-499/62, 5, 1, 2, 3, 9/2, -231/31}` | `-9734734015/248` | `-9734734015/248` |

## Reasoning

I generated exact rational BG data from `OnShellBG.m`, then resolved the
absolute values symbolically in representative chambers. At five points the
sign-resolved BG polynomial reduced to

```text
i 16 omega_1 omega_2
sum_S (-1)^|S| (r - Q_S)_+^2.
```

The same normalized object appeared at six and seven points with powers `3`
and `4`, respectively. The polynomial factor after dividing by
`i 2^(n-1) omega_1 omega_2` is the standard inclusion-exclusion truncated
power. Adding one positive leg applies the finite-difference operation

```text
F(r; q_1,...,q_m)
  = F(r; q_1,...,q_{m-1})
    - F(r - q_m; q_1,...,q_{m-1}),
```

which solves to the subset sum above and gives the observed chamber
decomposition by `Q_S < r`.
