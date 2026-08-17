# Closed form for the two-minus sector

Let

\[
\sigma=(-1,-1,+1,\ldots,+1),\qquad q_i=\omega_i^2,
\]

with the on-shell constraints

\[
\sum_{i=1}^n \omega_i=0,
\qquad
-q_1-q_2+\sum_{a=3}^n q_a=0.
\]

For a subset \(S\subseteq P:=\{3,\ldots,n\}\), define

\[
q_S:=\sum_{a\in S}q_a,
\qquad
(x)_+^m:=\begin{cases}
x^m,&x>0,\\
0,&x\le 0.
\end{cases}
\]

The formula I find is

\[
\boxed{
A_n
=
\frac{i\,2^{n-1}}{g^{\,n-3}}\,\omega_1\omega_2
\sum_{S\subseteq \{3,\ldots,n\}}(-1)^{|S|}
\left(q_1-q_S\right)_+^{\,n-3}
}
\qquad(n\ge4).
\]

Equivalently, because \(\sum_{a=3}^n q_a=q_1+q_2\), the same expression can be written with \(q_2\) replacing \(q_1\); this makes the symmetry between the two minus legs manifest.

## Chamber decomposition

The chambers are the connected components cut out by the hyperplanes

\[
q_S=q_1,\qquad S\subseteq\{3,\ldots,n\}.
\]

On a fixed open chamber \(C\), the set

\[
\mathcal I_C=\{S\subseteq\{3,\ldots,n\}:q_S<q_1\}
\]

is constant, and the closed form is the homogeneous polynomial

\[
A_n\big|_C
=
\frac{i\,2^{n-1}}{g^{\,n-3}}\,\omega_1\omega_2
\sum_{S\in\mathcal I_C}(-1)^{|S|}
\left(q_1-q_S\right)^{n-3}.
\]

This has total frequency degree \(2n-4\). On chamber walls the formula is understood by continuity; since \(n\ge4\), the wall terms vanish.

For example, at four points

\[
A_4=8i\omega_1\omega_2\left[q_1-(q_1-q_3)_+-(q_1-q_4)_+\right]
\]

for \(g=1\). In the `MakeKinematics[4,{a,b},...]` branch this reduces to

\[
A_4=-8i\,a b\min(a^2,b^2),
\]

which is the symbolic `BGAmplitude` limit; direct exact substitution into the supplied code can hit removable `0*ComplexInfinity` terms at four points.

### Important note on the \(n=4\) test (verified independently)

At \(n=4\) the on-shell solver `MakeKinematics[4,{a,b},{-1,-1,1,1},1]` always
returns \(\omega=(-b,\,a,\,b,\,-a)\). Consequently legs 2 and 4 carry exactly
opposite momenta, \(k_2+k_4 = \sigma_2 a^2 + \sigma_4 a^2 = -a^2 + a^2 = 0\),
for **every** kinematic point in this sector. The BG recursion forms a current
on the subset \(\{2,4\}\) whose propagator is
\(-i/(\omega_S^2/|k_S| - g)\) with \(|k_S| = |k_2+k_4| = 0\), so a
`1/0` (`ComplexInfinity`) is multiplied by a vanishing numerator and
`BGAmplitude` returns `Indeterminate` for any *direct* \(n=4\) evaluation
(confirmed numerically: perturbing off the degeneracy and taking the limit
still routes through the pole). The physically correct value is obtained by
evaluating BG with **symbolic** free frequencies and simplifying per chamber,
which yields the removable-singularity limit
\(-8i\,a^3 b\) for \(b>a\) and \(-8i\,a\,b^3\) for \(a>b\) — exactly the closed
form above. This is a property of the supplied code at \(n=4\), not of the
formula, and it is the reason the \(n=4\) rows in the table below are reported
via the symbolic-chamber limit.

## Numerical evidence against `BGAmplitude`

All entries below use \(g=1\), \(\sigma=(-1,-1,+,\ldots,+)\), and exact rational arithmetic.  The “active” column is the number of subsets \(S\subseteq\{3,\ldots,n\}\) with \(q_S<q_1\), showing that the tests hit different chambers.  Relative error was exactly zero in the Wolfram exact comparisons; numerically this is \(\le10^{-10}\).

| n | free frequencies passed to `MakeKinematics` | resulting \(\omega\) | active subsets | `BGAmplitude` | formula | rel. err. |
|---:|---|---|---:|---:|---:|---:|
| 4 | `{2,3}` | `{-3,2,3,-2}` | boundary | \(-192 i\) | \(-192 i\) | 0 |
| 4 | `{3,2}` | `{-2,3,2,-3}` | boundary | \(-192 i\) | \(-192 i\) | 0 |
| 4 | `{-2,5}` | `{-5,-2,5,2}` | boundary | \(320 i\) | \(320 i\) | 0 |
| 5 | `{2,3,4}` | `{-17/3,2,3,4,-10/3}` | 7 / 8 | \(-8704 i/3\) | \(-8704 i/3\) | 0 |
| 5 | `{4,3,2}` | `{-13/3,4,3,2,-14/3}` | 4 / 8 | \(-19968 i\) | \(-19968 i\) | 0 |
| 5 | `{-2,3,4}` | `{-23/5,-2,3,4,-2/5}` | 6 / 8 | \(577024 i/3125\) | \(577024 i/3125\) | 0 |
| 6 | `{2,1,1,1}` | `{-12/5,2,1,1,1,-13/5}` | 8 / 16 | \(-4608 i/5\) | \(-4608 i/5\) | 0 |
| 6 | `{2,1,1,3}` | `{-4,2,1,1,3,-3}` | 12 / 16 | \(-4608 i\) | \(-4608 i\) | 0 |
| 6 | `{4,1,3,3}` | `{-62/11,4,1,3,3,-59/11}` | 10 / 16 | \(-3706112 i/11\) | \(-3706112 i/11\) | 0 |
| 7 | `{3,1,1,1,1}` | `{-22/7,3,1,1,1,1,-27/7}` | 16 / 32 | \(-101376 i/7\) | \(-101376 i/7\) | 0 |
| 7 | `{2,1,1,1,3}` | `{-9/2,2,1,1,1,3,-7/2}` | 24 / 32 | \(-34560 i\) | \(-34560 i\) | 0 |
| 7 | `{2,1,3,3,3}` | `{-7,2,1,3,3,3,-5}` | 30 / 32 | \(-156800 i\) | \(-156800 i\) | 0 |

I also checked the expected gravity scaling separately: at five points with free frequencies `{2,3,4}`, the BG values for \(g=1,2,3\) agree with the formula's \(g^{-(n-3)}\) scaling.

### Reproducing the evidence

The script `verify.wls` in this folder regenerates all of the above
independently. Run it from this directory with

```
wolframscript -file verify.wls
```

It loads only the definition section of `../OnShellBG.m` (everything before the
`gVal = 1;` test driver, so the slow built-in tests are skipped), reimplements
the closed form from scratch, and prints `relerr` for every point at
\(n=5,6,7\) (multiple chambers, \(g=1,2,3\)). It also prints the \(n=4\)
symbolic-chamber limit. The reported `max relative error (n=5,6,7)` is `0`
(exact rational agreement, hence well within the required \(\le10^{-10}\)).

## How I arrived at it

1. The kernels only introduce absolute values of internal momenta.  In this sector those internal momenta are sums of signed \(q_i=\omega_i^2\), so the natural chamber walls are subset-sum walls \(q_S=q_1\) (equivalently \(q_{P\setminus S}=q_2\)).
2. The amplitude is homogeneous of degree \(2n-4\).  Thus, after factoring out \(\omega_1\omega_2/g^{n-3}\), the remaining object should have degree \(n-3\) in the \(q_i\).
3. Fitting the BG data in several chambers at \(n=4,5,6\) singled out the finite-difference/truncated-power expression
   \[
   \sum_S(-1)^{|S|}(q_1-q_S)_+^{n-3},
   \]
   with overall coefficient \(i2^{n-1}\).
4. I then verified the resulting all-\(n\) conjecture directly against the supplied `BGAmplitude` through \(n=7\), in multiple chambers as shown above.
