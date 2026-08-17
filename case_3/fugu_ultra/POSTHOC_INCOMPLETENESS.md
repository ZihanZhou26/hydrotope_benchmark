# Precise Scope of the Fugu Ultra Result

Date: 2026-07-18  
Source: Post-hoc review of [thinking_log.tex](thinking_log.tex),
[report.md](report.md), the [benchmark prompt](../prompt.md), and exact
on-shell checks.

> **Blindness warning.** This is a post-hoc evaluation note containing the
> global answer. Remove or hide it before rerunning an agent in this benchmark
> directory.

## Summary

The Fugu Ultra result contains the correct prefactor, degree, truncated-power
structure, and inclusion--exclusion geometry. Its central mathematical
discovery is correct.

The result is incomplete only as a formula for **all arbitrary signed
kinematics** requested by the prompt. There are two precise gaps:

1. The boxed fixed-label formula omits the last plus leg, \(\omega_n^2\).
   This omission is valid in the canonical chamber tested by Fugu, but it is
   not valid in every sign chamber.
2. The later sign-based rule for choosing \(p\) and \(R\) repairs many other
   chambers, but some valid kinematics have no leg satisfying that selection
   rule.

Replacing \(\beta^2\) by either \(\omega_1^2\) or \(\omega_2^2\) is exact when
the spline includes **all** plus legs. The threshold choice is not a source of
error.

## Required notation

The two-minus sector has

$$
\sigma=(-1,-1,+1,\ldots,+1),
$$

with signed incoming frequencies satisfying

$$
\sum_{i=1}^n\omega_i=0,
\qquad
-\omega_1^2-\omega_2^2+\sum_{j=3}^n\omega_j^2=0.
$$

For \(m=n-3\), define the truncated-power function

$$
T_m(t;\{a_j\}_{j\in R})
=
\sum_{S\subseteq R}(-1)^{|S|}
\left[t-\sum_{j\in S}a_j\right]_+^m,
\qquad
[x]_+=\max(x,0).
$$

The global formula is

$$
A_n
=
i\,\frac{2^{n-1}}{g^{n-3}}\,\omega_1\omega_2\,
T_{n-3}\!\left(
\beta^2;\{\omega_j^2\}_{j=3}^{n}
\right),
\qquad
\beta=\min(|\omega_1|,|\omega_2|).
$$

The set of spline arguments contains all \(n-2\) plus legs,
\(j=3,\ldots,n\).

## What Fugu got exactly right

Fugu identified

- the universal prefactor
  \(i\,2^{n-1}\omega_1\omega_2/g^{n-3}\);
- the degree \(m=n-3\);
- the positive-part powers;
- the alternating subset sum;
- the chamber walls \(t=\sum_{j\in S}\omega_j^2\);
- the interpretation as one spline rather than unrelated chamber
  polynomials.

These are the essential hydrotope structure. The remaining issue concerns how
to express all chambers with one global choice of spline arguments.

## The threshold \(\beta^2\) is interchangeable

Set

$$
a_j=\omega_j^2,
\qquad
A=\sum_{j=3}^n a_j.
$$

There are \(n-2=m+1\) variables \(a_j\). The \((m+1)\)-fold finite difference
of a degree-\(m\) polynomial vanishes:

$$
\sum_{S\subseteq\{3,\ldots,n\}}
(-1)^{|S|}
\left(t-\sum_{j\in S}a_j\right)^m
=0.
$$

Using

$$
x^m=[x]_+^m+(-1)^m[-x]_+^m
$$

in this identity, and then replacing every subset by its complement, gives
the reflection identity

$$
T_m(t;\{a_j\}_{j=3}^{n})
=
T_m(A-t;\{a_j\}_{j=3}^{n}).
$$

Momentum conservation gives

$$
A=\omega_1^2+\omega_2^2.
$$

Therefore,

$$
\begin{aligned}
T_m(\omega_1^2;\{\omega_j^2\}_{j=3}^{n})
&=
T_m(\omega_2^2;\{\omega_j^2\}_{j=3}^{n})\\
&=
T_m(\beta^2;\{\omega_j^2\}_{j=3}^{n}).
\end{aligned}
$$

Thus the exact global answer may use \(\omega_1^2\), \(\omega_2^2\), or
\(\beta^2\) as its threshold. Exact rational tests over signed on-shell
points at \(n=4,\ldots,7\) also gave equality for all three choices.

## Incompleteness 1: the boxed formula omits one plus leg

The boxed formula in [thinking_log.tex](thinking_log.tex) is

$$
A_n^{\mathrm{Fugu,box}}
=
i\,\frac{2^{n-1}}{g^{n-3}}\,\omega_1\omega_2\,
T_{n-3}\!\left(
\omega_2^2;\{\omega_j^2\}_{j=3}^{n-1}
\right).
$$

It uses only \(n-3=m\) plus legs and omits \(\omega_n^2\). The reflection
identity above requires all \(n-2=m+1\) plus legs. Consequently, the omitted
leg cannot be dropped globally.

### Exact five-point counterexample

Take \(g=1\), \(\sigma=(-1,-1,+1,+1,+1)\), and

$$
\omega=
\left(
\frac{13}{15},-1,\frac13,-1,\frac45
\right).
$$

Energy conservation holds:

$$
\frac{13}{15}-1+\frac13-1+\frac45=0.
$$

Momentum conservation also holds:

$$
-\left(\frac{13}{15}\right)^2-1
+\left(\frac13\right)^2+1+\left(\frac45\right)^2
=0.
$$

The full spline gives

$$
T_2\!\left(
\omega_2^2;\omega_3^2,\omega_4^2,\omega_5^2
\right)
=
T_2\!\left(1;\frac19,1,\frac{16}{25}\right)
=
\frac{32}{225}.
$$

The boxed Fugu spline gives

$$
T_2\!\left(
\omega_2^2;\omega_3^2,\omega_4^2
\right)
=
T_2\!\left(1;\frac19,1\right)
=
\frac{17}{81}.
$$

Since the common prefactor is nonzero, these produce different amplitudes:

$$
A_5^{\mathrm{global}}
=-\frac{6656}{3375}i,
\qquad
A_5^{\mathrm{Fugu,box}}
=-\frac{3536}{1215}i.
$$

Fugu's later channel-aware rule repairs this particular example by choosing
\(p=\omega_1\) and \(R=\{3,5\}\). Therefore, this example disproves the
global scope of the **boxed fixed-label formula**, rather than the later
selector wherever that selector is defined.

## Incompleteness 2: the channel selector is not defined everywhere

Fugu later proposes:

> Choose the \(\sigma=-1\) leg \(p\) whose frequency sign is shared by
> exactly \(n-3\) plus legs; call those plus legs \(R\), and call the other
> minus leg \(q\).

This gives

$$
A_n^{\mathrm{Fugu,selector}}
=
i\,\frac{2^{n-1}}{g^{n-3}}\,q\,p\,
T_{n-3}\!\left(p^2;\{\omega_j^2\}_{j\in R}\right).
$$

The formula is exact on the chambers where such a \(p\) exists. Some valid
on-shell points have no such candidate.

### Exact selector-gap example

At \(n=5\), take

$$
\omega=
\left(
\frac{152}{9},\frac13,\frac{10}{3},
-\frac{14}{3},-\frac{143}{9}
\right).
$$

Both conservation laws hold:

$$
\sum_{i=1}^5\omega_i=0,
$$

and

$$
-\left(\frac{152}{9}\right)^2
-\left(\frac13\right)^2
+\left(\frac{10}{3}\right)^2
+\left(\frac{14}{3}\right)^2
+\left(\frac{143}{9}\right)^2
=0.
$$

Here \(n-3=2\). Both minus legs, \(\omega_1\) and \(\omega_2\), are positive.
Among the three plus legs, only \(\omega_3\) is positive. Each minus leg
therefore shares its frequency sign with one plus leg rather than two. The
selector returns no candidate.

The amplitude is nevertheless nonzero. The global formula gives

$$
A_5=\frac{2432}{2187}i.
$$

This example shows that the sign-counting selector does not cover every
valid chamber requested by the prompt.

## Precise scope mismatch

The benchmark prompt asks for a formula valid for arbitrary free frequencies
satisfying the on-shell constraints. Fugu verifies the boxed expression on
positive free-frequency inputs and describes those inputs as the setup
specified by the prompt. Positivity is an additional restriction: the prompt
allows signed incoming frequencies and asks for arbitrary kinematics.

Therefore:

- On the canonical positive-free-frequency chart, the boxed Fugu formula is
  exact.
- In many additional sign chambers, the later \(p,q,R\) selector is exact.
- Across all arbitrary signed kinematics, the response leaves some chambers
  uncovered.
- Including every plus leg in \(T_{n-3}\) gives one global expression and
  removes the need for a sign-based selector.

## Recommended characterization

The result should be described as:

> **Correct discovery of the hydrotope closed-form structure, expressed
> through chart-dependent formulas with an incomplete global coverage rule.**

It is more accurate to call this a near-global or structurally correct result
than a local-chamber result. Its incompleteness concerns global indexing and
coverage, not the prefactor, the spline, the degree, or the hydrotope
discovery.
