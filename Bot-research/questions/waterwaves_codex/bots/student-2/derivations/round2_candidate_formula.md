# Round 2 candidate formula

Timestamp: `2026-06-24T22:25:01Z`

All checks below use the private copied exact-GMP oracle
`bots/student-2/code/bg`, not the shared `bg.cpp`.

## Candidate

Let
$$
u=-\omega_1,\qquad v=\omega_2,\qquad p_j=\omega_{j+2},
\qquad j=1,\ldots,m,\quad m=n-2.
$$

Define the truncated power
$$
(x)_+^d=\begin{cases}
x^d,&x>0,\\
0,&x\leq 0.
\end{cases}
$$

The finite-data candidate for $n\geq 5$ is
$$
A_n=-i\,2^{n-1}uv
\sum_{S\subseteq\{1,\ldots,m\}}(-1)^{|S|}
\left(v^2-\sum_{j\in S}p_j^2\right)_+^{n-3}.
$$

Equivalently, since $A_n$ is pure imaginary in all finite rows tested,
$$
\frac{A_n}{i}=
-2^{n-1}uv
\sum_{S\subseteq\{1,\ldots,m\}}(-1)^{|S|}
\left(v^2-\sum_{j\in S}p_j^2\right)_+^{n-3}.
$$

This is symmetric in the $\sigma=+1$ legs, homogeneous of degree $2n-4$, and
depends on the subchannel thresholds $v^2-\sum_{j\in S}p_j^2$ rather than only
on elementary symmetric polynomials $e_3(p),\ldots,e_m(p)$.

I do **not** claim this as the final all-$n$ answer from `student-2` alone
because strict $n=4$ still requires PI acceptance of a limiting prescription.

## How I found it

The round-1 polynomial fits in $u,v,e_3,\ldots,e_m$ failed, which suggested that
the absolute values in the BG propagators leave piecewise subchannel data in the
answer.

For $n=5$ I evaluated the symbolic BG recursion in fixed sign chambers. With
free variables $v,a,b$ and solved positive leg
$$
c=-\frac{(v+a)(v+b)}{v+a+b},\qquad
u=\frac{a^2+ab+av+b^2+bv}{a+b+v},
$$
the all-large chamber $a^2,b^2,c^2>v^2$ gives
$$
\frac{A_5}{i}=-16uv^5.
$$
The chamber with one small square $x=a^2<v^2$ gives
$$
\frac{A_5}{i}=-16uv\,x(2v^2-x)
=-16uv\left[v^4-(v^2-x)^2\right],
$$
and the chamber with two small squares $x,y<v^2$ and $x+y<v^2$ gives
$$
\frac{A_5}{i}=-32uv\,xy
=-16uv\left[v^4-(v^2-x)^2-(v^2-y)^2+(v^2-x-y)^2\right].
$$
An $n=7$ row with small-square sum above $v^2$ showed that the last term must be
truncated: the untruncated inclusion-exclusion missed by
$$
-\frac{2566669}{52488},
$$
while the truncated formula above matched exactly.

The same finite-difference pattern with power $n-3$ then matched all checked
$n=5,6,7$ rows.

## Compatibility with the $n=4$ limiting prescription

After this formula was found, `student-1` posted the limiting prescription
$$
A_4(-b,a,b,-a)=-8i\,ab\,\min(a^2,b^2).
$$
The same truncated-power expression is compatible with that limit if it is
extended to $n=4$.  In strict $n=4$ kinematics,
$$
u=b,\qquad v=a,\qquad p_1=b,\qquad p_2=-a,
$$
and the power is $n-3=1$.  Therefore
$$
\frac{A_4}{i}=-8ab\sum_{S\subseteq\{1,2\}}(-1)^{|S|}
\left(a^2-\sum_{j\in S}p_j^2\right)_+
=-8ab\,\min(a^2,b^2).
$$
This is a consistency check only; I did not independently resolve the strict
$n=4$ oracle singularity in this session.

## Exact evidence

Reproduction:

```sh
python3 bots/student-2/code/round2_candidate_formula.py
```

Output summary:

```json
{
  "finite_rows": 29,
  "assigned_finite_rows_n5_n6_n7": 27,
  "assigned_failures": 0,
  "by_set": {
    "fit": {"finite": 9, "max_relative_error": 0.0},
    "heldout": {"finite": 18, "max_relative_error": 0.0},
    "smoke_n8": {"finite": 2, "max_relative_error": 0.0}
  }
}
```

Representative exact held-out rows:

| label | $n$ | free $\omega_2,\ldots,\omega_{n-1}$ | oracle $A_n/i$ | residual |
| --- | ---: | --- | ---: | ---: |
| `n5_truncated_sum_gt_v2_new` | 5 | `5,4,4` | $-3259520/13$ | $0$ |
| `n5_signed_new` | 5 | `5,3,-3` | $-944784/625$ | $0$ |
| `n6_signed_new` | 6 | `5,-1,1,1` | $-1943515/4374$ | $0$ |
| `n6_extreme_small_v_new` | 6 | `1/10,20,3,5` | $-3059/43906250$ | $0$ |
| `n7_truncated_new` | 7 | `5,2/3,7/2,7/2,2/3` | $-79831105907/52488$ | $0$ |
| `n7_signed_new` | 7 | `5,-1,1,1,2` | $-88320$ | $0$ |
| `n7_extreme_small_v_new` | 7 | `1/10,20,3,5,7` | $-343/219375000$ | $0$ |

Full exact rows and residuals are in
`bots/student-2/data/round2_candidate_checks.json`.

## Status

This is now a strong finite-data candidate for all finite $n\geq 5$ two-minus
rows tested. It also passed two optional exact $n=8$ smoke checks and is
algebraically compatible with the $n=4$ limiting formula reported by
`student-1`. The remaining group gap is PI acceptance of the limiting $n=4$
prescription and independent PI verification of the combined formula.
