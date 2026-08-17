# Two-minus closed form for the on-shell water-wave tree amplitude

## Formula

Work on the two-minus on-shell manifold

\[
\sigma=(-1,-1,+1,\dots,+1), \qquad
\sum_{i=1}^n \omega_i = 0, \qquad
-\omega_1^2-\omega_2^2+\sum_{i=3}^n \omega_i^2 = 0.
\]

Using the same coordinates as `MakeKinematics`, take

\[
m := n-3, \qquad X := \omega_2^2, \qquad a_r := \omega_r^2 \ \ (r=3,\dots,n-1),
\]

with \(\omega_1,\omega_n\) fixed by the two conservation laws. Define the
order-\(m\) subset-sum truncated-power spline

\[
\mathcal B_m(X; a_3,\dots,a_{n-1})
:=
\sum_{J \subseteq \{3,\dots,n-1\}}
(-1)^{|J|}
\Bigl(X-\sum_{j\in J} a_j\Bigr)_+^m,
\]

where

\[
u_+^m :=
\begin{cases}
u^m, & u>0, \\
0, & u<0,
\end{cases}
\]

and on a chamber wall one takes the continuous extension.

The conjectured all-\(n\) closed form is

\[
\boxed{
A_n^{(--+\cdots+)}
=
i\,2^{\,n-1}\,\omega_1 \omega_2\,
\mathcal B_{n-3}(\omega_2^2;\omega_3^2,\dots,\omega_{n-1}^2)
}
\]

valid for every \(n\ge 4\).

## Chamber decomposition

The chamber walls are exactly the subset-sum hyper-surfaces

\[
\omega_2^2 = \sum_{j\in J}\omega_j^2,
\qquad J\subseteq\{3,\dots,n-1\}.
\]

So on any open chamber, the active subset set

\[
\mathcal A
:=
\left\{
J \subseteq \{3,\dots,n-1\} :
\sum_{j\in J}\omega_j^2 < \omega_2^2
\right\}
\]

is fixed, and the amplitude becomes the ordinary homogeneous polynomial

\[
A_n
=
i\,2^{\,n-1}\,\omega_1\omega_2
\sum_{J\in\mathcal A}
(-1)^{|J|}
\Bigl(\omega_2^2-\sum_{j\in J}\omega_j^2\Bigr)^{n-3}.
\]

That is the full chamberwise polynomial answer.

## Low-point examples

### \(n=4\)

\[
A_4
=
8i\,\omega_1\omega_2
\Bigl[\omega_2^2-(\omega_2^2-\omega_3^2)_+\Bigr].
\]

Equivalently:

- if \(\omega_2^2<\omega_3^2\), then \(A_4 = 8i\,\omega_1\omega_2^3\);
- if \(\omega_2^2>\omega_3^2\), then \(A_4 = 8i\,\omega_1\omega_2\omega_3^2\).

### \(n=5\)

Let \(x=\omega_2^2\), \(a=\omega_3^2\), \(b=\omega_4^2\). Then

\[
A_5
=
16i\,\omega_1\omega_2\,
\Bigl[x^2-(x-a)_+^2-(x-b)_+^2+(x-a-b)_+^2\Bigr].
\]

Generic chambers:

- \(x<a\) and \(x<b\): \(A_5 = 16i\,\omega_1\omega_2^5\).
- \(a<x<b\): \(A_5 = 16i\,\omega_1\omega_2\,a(2x-a)\).
- \(b<x<a\): same with \(a \leftrightarrow b\).
- \(a,b<x<a+b\): \(A_5 = 16i\,\omega_1\omega_2\,[2x(a+b)-x^2-a^2-b^2]\).
- \(a+b<x\): \(A_5 = 32i\,\omega_1\omega_2\,ab\).

## How I arrived at it

I reimplemented the BG recursion exactly in rational arithmetic in
`analyze_bg.py`, sampled many two-minus kinematic points, and sorted them by
the sign pattern of the internal subset momenta that feed the `Abs[...]`
factors.

At 5 points, the chamber polynomials matched

\[
x^2-(x-a)_+^2-(x-b)_+^2+(x-a-b)_+^2,
\]

which is the order-2 subset-sum truncated-power spline. Extending that ansatz
to higher \(n\), the unique prefactor consistent with the exact BG data is
\(i\,2^{n-1}\omega_1\omega_2\), and the spline order is \(n-3\).

## Numerical evidence

Exact checks for \(n=5,6,7\), and the \(n=4\) limiting checks, are in
`verification.txt`, produced by `verify_formula.py`.

Summary:

- For all listed \(n=5,6,7\) test points, the formula matches the exact BG
  recursion **exactly** as a rational number, so the relative error is
  `0.000e+00`.
- The tested points span multiple chambers, recorded in `verification.txt` via
  the active subset set `active = [...]`.
- At \(n=4\), the on-shell BG representation pinches a `0/0` internal channel,
  so I checked the formula by taking near-on-shell limits from both 4-point
  chambers. The recorded relative errors are `5.000e-11` and `2.667e-11`.

Files:

- `analyze_bg.py`: exact rational BG reimplementation used for fitting.
- `verify_formula.py`: formula evaluator and verification driver.
- `verification.txt`: captured verification output.
