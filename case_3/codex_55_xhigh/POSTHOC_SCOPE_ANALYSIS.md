# Precise Scope of the Codex 5.5 X-High Result

Date: 2026-07-18  
Source: Post-hoc review of [thinking_log.tex](thinking_log.tex),
[result.md](result.md), [verify_formula.m](verify_formula.m), the
[benchmark prompt](../prompt.md), and exact `BGAmplitude` checks.

> **Blindness warning.** This post-hoc note contains the global formula and
> counterexamples. Remove or hide it before rerunning a blind agent in this
> benchmark directory.

## Summary

The Codex 5.5 X-High result identifies much of the correct structure:

- the universal prefactor;
- the soft scale \(U=\beta^2\);
- the degree \(m=n-3\);
- the alternating subset sum;
- the piecewise-polynomial character of the answer.

The final formula is nevertheless incomplete for arbitrary kinematics. It
replaces each truncated power

$$
\left[U-\sum_{j\in S}x_j\right]_+^m
$$

by the ordinary power

$$
\left(U-\sum_{j\in S}x_j\right)^m.
$$

This replacement is valid only while the relevant subset sum remains below
\(U\). The final verification points all remain in regions where this
condition holds. A valid positive-free-frequency point crossing a composite
subset wall gives an exact disagreement with `BGAmplitude`.

The result should therefore be classified as a strong structural or
near-global discovery with an incomplete chamber decomposition, rather than a
complete solution for arbitrary kinematics.

## Required notation

In the two-minus sector,

$$
\sigma=(-1,-1,+1,\ldots,+1),
$$

and the signed incoming frequencies satisfy

$$
\sum_{i=1}^n\omega_i=0,
\qquad
-\omega_1^2-\omega_2^2+\sum_{j=3}^n\omega_j^2=0.
$$

Call the two \(\sigma=-1\) frequencies \(s\) and \(h\), ordered by magnitude:

$$
|s|\le |h|.
$$

Define

$$
U=s^2=\min(\omega_1^2,\omega_2^2),
\qquad
m=n-3,
\qquad
x_j=\omega_j^2\quad (j=3,\ldots,n).
$$

The product \(hs\) equals \(\omega_1\omega_2\), independent of which minus leg
is called \(s\).

## The Codex formula

Codex sorts the plus-leg squares and selects those below \(U\). It defines

$$
r=\min\!\left(m,\#\{j:x_j<U\}\right)
$$

and

$$
G_m^{\mathrm{Codex}}(U)
=
\sum_{S\subseteq\{1,\ldots,r\}}
(-1)^{|S|}
\left(U-\sum_{j\in S}x_j\right)^m.
$$

Its proposed amplitude is

$$
A_n^{\mathrm{Codex}}
=
i\,2^{n-1}g^{3-n}\,h\,s\,G_{n-3}^{\mathrm{Codex}}(s^2).
$$

The prefactor, the scale \(U\), and the degree \(m\) are correct. The defect is
inside \(G_m^{\mathrm{Codex}}\).

## The global formula

The global hydrotope function is

$$
T_m(U;\{x_j\})
=
\sum_{S\subseteq\{3,\ldots,n\}}
(-1)^{|S|}
\left[U-\sum_{j\in S}x_j\right]_+^m,
\qquad
[z]_+=\max(z,0).
$$

The exact amplitude is

$$
A_n
=
i\,2^{n-1}g^{3-n}\,h\,s\,
T_{n-3}\!\left(s^2;\{\omega_j^2\}_{j=3}^n\right).
$$

A plus-leg square \(x_j\ge U\) can be removed from the sum because every
subset containing it has a zero positive part. Thus filtering out individual
knots above \(U\) is valid.

After this filtering, the positive-part operation remains essential. Several
individually small knots can have a combined sum larger than \(U\).

## The missed chamber walls

Codex partitions the kinematics using only the individual comparisons

$$
x_j<U.
$$

The true formula also changes at every composite wall

$$
U=\sum_{j\in S}x_j
$$

for each plus-leg subset \(S\). The integer \(r\), which counts individual
knots below \(U\), does not determine the full chamber.

At five points, suppose

$$
x_1<x_2<U.
$$

Codex treats this as one chamber and writes

$$
G_2^{\mathrm{Codex}}
=
U^2-(U-x_1)^2-(U-x_2)^2+(U-x_1-x_2)^2.
$$

The correct expression is

$$
T_2
=
U^2-(U-x_1)^2-(U-x_2)^2
+[U-x_1-x_2]_+^2.
$$

The region \(x_2<U\) therefore contains two distinct chambers:

$$
\begin{array}{ll}
x_1+x_2<U:
&[U-x_1-x_2]_+^2=(U-x_1-x_2)^2,\\[3pt]
U<x_1+x_2:
&[U-x_1-x_2]_+^2=0.
\end{array}
$$

Codex found the first chamber and applied its polynomial to both.

## Exact positive-frequency counterexample

Take \(n=5\), \(g=1\), and the positive free-frequency input

$$
\{\omega_2,\omega_3,\omega_4\}=\{4,3,3\}.
$$

`MakeKinematics` gives

$$
\omega=
\left(-\frac{51}{10},4,3,3,-\frac{49}{10}\right).
$$

Energy conservation holds:

$$
-\frac{51}{10}+4+3+3-\frac{49}{10}=0.
$$

Momentum conservation also holds:

$$
-\left(\frac{51}{10}\right)^2-4^2
+3^2+3^2+\left(\frac{49}{10}\right)^2
=0.
$$

Here

$$
s=4,
\qquad
h=-\frac{51}{10},
\qquad
U=16,
$$

and the plus-leg squares are

$$
\left\{9,9,\frac{2401}{100}\right\}.
$$

The two individual knots \(9\) lie below \(U=16\), but their sum crosses the
composite wall:

$$
9+9=18>16.
$$

Codex evaluates

$$
\begin{aligned}
G_2^{\mathrm{Codex}}
&=16^2-(16-9)^2-(16-9)^2+(16-9-9)^2\\
&=256-49-49+4\\
&=162.
\end{aligned}
$$

The global formula gives

$$
\begin{aligned}
T_2
&=16^2-(16-9)^2-(16-9)^2+[16-9-9]_+^2\\
&=256-49-49+0\\
&=158.
\end{aligned}
$$

Direct exact evaluation of the supplied oracle gives

$$
\begin{aligned}
\texttt{BGAmplitude}
&=-\frac{257856}{5}\,i,\\
A_5^{\mathrm{Codex}}
&=-\frac{264384}{5}\,i,\\
\texttt{BGAmplitude}-A_5^{\mathrm{Codex}}
&=\frac{6528}{5}\,i.
\end{aligned}
$$

This is a generic valid point produced from positive free frequencies. The
failure is therefore part of the prompt's ordinary kinematic scope.

## Why all reported verification points pass

The final verification harness hard-codes twenty points in
[verify_formula.m](verify_formula.m). It does not perform a randomized or
systematic chamber scan.

For each listed point, define \(B\) to be the plus-leg squares selected by the
Codex implementation and define the margin

$$
\Delta=U-\sum_{x\in B}x.
$$

The exact margins, in the same order as the cases in `verify_formula.m`, are

```text
n=5:
4, 119/25, 20/9, 15, 848/169, 1/9, 4

n=6:
4, 1, 1096/529, 8, 15, 47, 496/9, 4, 59, 1424/81

n=7:
4, 1, 8
```

Every margin is positive. Since every \(x_j\) is nonnegative, each subset
\(S\subseteq B\) satisfies

$$
\sum_{j\in S}x_j
\le
\sum_{x\in B}x
<
U.
$$

Therefore, at every reported test point,

$$
\left[U-\sum_{j\in S}x_j\right]_+^m
=
\left(U-\sum_{j\in S}x_j\right)^m
$$

for every subset used by the formula. The incorrect expression is exactly
equal to the correct one throughout these sampled chambers.

The reported \(n=7\) cases exercise only \(r=0\) or \(r=1\), where no
multi-knot subset can expose the missing positive part. The \(n=4\) statement
is a proposed finite continuation rather than a direct oracle comparison,
because the raw recursion is indeterminate at the displayed four-point
kinematics.

## Secondary issue: the \(r=m\) cap

The implementation sets

$$
r=\min\!\left(m,\#\{j:x_j<U\}\right)
$$

and retains only the first \(r\) sorted knots. The global formula has \(m+1\)
plus legs and lets the positive-part operation determine which subsets are
active. If more than \(m\) individual plus-leg squares lie below \(U\), the
cap can discard a leg that participates in an active subset.

The cap is unnecessary once the global positive-part formula is used. The
clean correction is to sum over all plus-leg subsets and keep the
positive-part bracket on every subset sum.

## Precise characterization

Confirmed:

- Codex discovered the correct universal prefactor.
- It chose the correct soft scale \(U=\beta^2\).
- It found the correct degree \(m=n-3\).
- It discovered the alternating subset-sum skeleton.
- Its formula is exact on the reported verification points.
- Its formula is exact more generally whenever every included subset sum
  remains at or below \(U\) and the \(r=m\) cap removes no active leg.

Incomplete:

- The formula omits the positive-part operation on composite subset sums.
- The chamber label \(r\) records only individual walls and misses composite
  walls.
- The \(r=m\) cap can omit an active plus leg.
- Consequently, the formula is not valid for arbitrary kinematics as required
  by the benchmark prompt.

Recommended description:

> **A strong near-global structural discovery that identifies the
> inclusion--exclusion skeleton but coarsens the true hydrotope chamber
> decomposition and therefore gives an incorrect polynomial in some valid
> chambers.**
