# Literature check: two-minus origin and three-minus status

## Primary modern source

N. Arkani-Hamed, F. Calisto, N. Ussembayev, W. W. Zhao, and Z. Zhou,
“Surface Water Wave Scattering and the Hydrotope,” arXiv:2606.28280 (2026):
https://arxiv.org/abs/2606.28280

This paper is the direct source of the two-minus formula used in the question.
It identifies the truncated-power sum with the volume of a box sliced by one
hyperplane.  Its equations (14)--(17) give the hydrotope and its
inclusion--exclusion evaluation.  The paper explicitly says that detailed
three-minus analysis first matters at six points and is left to future work.
Consequently it does not supply the requested \(A_6^{---+++}\) formula.

The structural warning relevant to this round is also explicit: the paper's
no-pole/uniqueness argument is made for the **two-minus** sector using the
vanishing one-minus amplitudes and soft limits.  It cannot simply be assumed
for the first three-minus amplitude.

## Earlier recursion and interaction literature

N. S. Ussembayev, “Non-interacting gravity waves on the surface of a deep
fluid,” arXiv:1903.10854 (2019):
https://arxiv.org/abs/1903.10854

This paper derives an arbitrary-order recursion for the Hamiltonian expansion
kernels and explains several vanishing sectors.  It discusses six-wave
interaction kernels and resonant sign configurations, but does not present a
compact complete three-minus six-point scattering amplitude of the form needed
here.

## Consequence for the ansatz search

The literature supports truncated box splines in the two-minus sector, but it
does not support replacing the three-minus amplitude by a sum of three
independent two-minus hydrotopes.  Combined with the exact rejection in
`s1_001_h1_rejection.md`, the next compact search should first isolate the
non-polynomial/contact or factorization part (if it survives on shell), then fit
only the regular chamber remainder to multivariate spline/positive-geometry
blocks.

