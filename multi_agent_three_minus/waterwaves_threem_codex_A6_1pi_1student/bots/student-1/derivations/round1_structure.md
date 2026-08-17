# Round 1 structure and negative box-spline test

## Exact setup

Let

$$
M=\{1,2,3\},\qquad P=\{4,5,6\},\qquad
a_i=\omega_i^2,\qquad b_j=\omega_{3+j}^2,
$$

and

$$
T=\sum_{i=1}^3 a_i=\sum_{j=1}^3 b_j.
$$

The copied GMP oracle is `bots/student-1/code/bg.cpp`, and its exact
calibration is in `bots/student-1/data/calibration.txt`.

## Momentum walls

A mixed momentum subset has

$$
gk_S=-\sum_{i\in I}a_i+\sum_{j\in J}b_j.
$$

After using total momentum conservation and identifying a subset with its
complement, every nondegenerate wall is in one of two labeled families:

$$
W^{(11)}_{ij}=a_i-b_j=0,
\qquad
W^{(12)}_{ij}=a_i+b_j-T=0,
\qquad 1\leq i,j\leq3.
$$

There are nine walls of each type.  The six additional equalities in
`wall_catalog.json` are external-degeneracy boundaries equivalent to one or
more external frequencies vanishing.  Exact two-sided approaches to one
isolated representative of each nondegenerate orbit are stored in
`wall_approaches.json`; the target wall argument decreases by a factor of
approximately $10$ per decade on both sides.

The exact oracle has $225$ points and $57$ labeled sign vectors.  Quotienting
the sign vectors by $S_3\times S_3$ gives three observed classes, not eight.
The eight-piece baseline therefore uses a finer or different "word" invariant;
this round did not recover that mapping.

## Candidate factorization poles

For an internal subset $S$, define

$$
q_S=\sum_{i\in S}\sigma_i\omega_i^2,\qquad
h_S=\left(\sum_{i\in S}\omega_i\right)^2-|q_S|.
$$

Modulo complements, within-set permutations, and the set swap, the subset
compositions are $(2,0)$, $(1,1)$, $(3,0)$, and $(2,1)$.  Pair candidates are
degenerate: for a same-side pair,

$$
h_{\{a,b\}}=2\omega_a\omega_b,
$$

and the mixed-pair branches force an external zero or $q_S=0$.

For the mixed triple representative $S=\{1,2,4\}$, one exact pole point is

$$
(\omega_1,\ldots,\omega_6)
=\left(-\frac13,-\frac12,-\frac72,\frac12,\frac13,\frac72\right).
$$

Exact side sequences have $|h_S|\sim3.3333\times10^{-d}$ for
$d=5,6,7$, while $|A_6/i|\to2.74494\ldots$ and
$|(A_6/i)h_S|\to0$.  At the isolated all-side triple representative,
$|h_S|\sim1.18669\times10^{1-d}$, while
$|A_6/i|\to72.0772\ldots$ and $|(A_6/i)h_S|\to0$.
Thus both tested triple surfaces are removable at these representatives.

## H1 feature family and exact failure

For a target set $R$, define

$$
B_R(x)=\sum_{J\subseteq R}(-1)^{|J|}
\left(x-\sum_{j\in J}\omega_j^2\right)_+^3.
$$

For each threshold-subset size $r=1,2$, split the six indices into
$A=I$, $C=M\setminus I$, and $R=P$.  The implementation enumerates every
nonempty orbit of quadratic monomials $\omega_u\omega_v$ under the stabilizer
of $I$ and $S_3(P)$, sums over every $I\subset M$ of size $r$, and adds the
minus/plus-swapped image.  There are eight features for $r=1$ and eight more
for $r=2$.  Every individual feature passed exact invariance tests under all
$36$ within-set permutations and the set swap at three generic points.

The exact fit is inconsistent:

- singleton thresholds: $\operatorname{rank}F=4$ but
  $\operatorname{rank}[F|A_6/i]=5$;
- singleton plus doubleton thresholds: $\operatorname{rank}F=6$ but
  $\operatorname{rank}[F|A_6/i]=7$.

The first stored contradictions are `base-6` and `aff-1--1-1/4`,
respectively.  Hence H1, in this symmetry-complete quadratic-prefactor form,
cannot represent $A_6$ even on the sampled chambers.
