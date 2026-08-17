# Summary — two-minus sector investigation

I did **not** obtain a trustworthy closed-form formula satisfying the prompt's stated requirements. The main useful outcome is a set of checks showing that the simple polynomial formula found early in the run is **not** a valid global answer.

## What was tested

The early candidate was, on a chamber with one positive and one negative two-minus frequency,

\[
A_n = i\,2^{n-1} g^{3-n}\,q\,p^{2n-5},
\]

where \(p\) is the positive-frequency member of \(\{\omega_1,\omega_2\}\) and \(q\) is the other one. In the labeling \(\omega_2=p>0\), this is

\[
A_n = i\,2^{n-1}g^{3-n}\omega_1\omega_2^{2n-5}.
\]

This matched several `MakeKinematics` samples for `n=5,6,7`, e.g.

- `n=5`, `ws={-9/2,2,5/2,3,-3}`: `BGAmplitude/I = -2304`, candidate/I = `-2304`.
- `n=6`, `ws={-184/17,2,3,5,7,-105/17}`: `BGAmplitude/I = -753664/17`, candidate/I = `-753664/17`.
- `n=7`, `ws={-123/7,2,3,5,7,11,-73/7}`: `BGAmplitude/I = -4030464/7`, candidate/I = `-4030464/7`.

## Why that candidate is not the requested answer

The prompt explicitly asks for a single global rational function, not a chamber-selected/polynomial expression. I found direct counterexamples showing that the polynomial candidate is not globally valid.

For `n=5`, fix the two minus legs at

\[
(\omega_1,\omega_2)=(-9/2,2).
\]

Then energy and momentum conservation require the three plus legs to have

\[
e_1=\omega_3+\omega_4+\omega_5=5/2,\qquad
 e_2=\omega_3\omega_4+\omega_3\omega_5+\omega_4\omega_5=-9,
\]

but leave \(e_3=\omega_3\omega_4\omega_5\) free. Numerically evaluating `BGAmplitude` at several real generic choices gives:

| e3 | BGAmplitude/I | polynomial candidate/I |
|---:|---:|---:|
| -15 | -1744.22843283248 | -2304 |
| -16 | -1901.43680531106 | -2304 |
| -17 | -2046.77357602551 | -2304 |
| -19 | -2265.24453611222 | -2304 |
| -21 | -2304.00000000000 | -2304 |

So the amplitude genuinely depends on the plus-leg configuration; it is not determined only by the two minus-leg frequencies.

## Structural notes found

- A useful rational parametrization is to take independent variables
  \((\omega_1,\\omega_3,\ldots,\omega_{n-1})\) and solve linearly for
  \((\omega_2,\omega_n)\), since \(\sigma_2+
  \sigma_n=0\).
- In this parametrization for `n=5`, with independent variables
  \((w_1,w_3,w_4)\), one has
  \[
  S=-(w_1+w_3+w_4),\qquad
  M=-(-w_1^2+w_3^2+w_4^2),
  \]
  \[
  \omega_5=\frac{S+M/S}{2},\qquad
  \omega_2=\frac{S-M/S}{2}.
  \]
- The BG code contains `Abs[k]`, so real samples can show chamber-dependent rational expressions. A slice crossing chambers does not reconstruct as a single low-degree rational function unless the correct analytic continuation/channel factors are used.
- A likely physical channel factor for a subset \(S\) is
  \[
  F_S=(\sum_{i\in S}\omega_i)^2-\sum_{i\in S}\sigma_i\omega_i^2,
  \]
  up to sign/chamber conventions from the `Abs` in the propagator.

## Status

A complete closed-form global rational expression was **not** reached before interruption. The previous `fugu_ultra/report.md` candidate should be treated as **not passing** the prompt's global-validity requirement; the counterexamples above are the most important result to preserve.
