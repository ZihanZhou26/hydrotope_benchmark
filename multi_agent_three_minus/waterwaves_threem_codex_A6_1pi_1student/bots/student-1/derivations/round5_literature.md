# Round 5 literature search: six-wave formulas

Search date: 2026-07-26.

## Result

I found no published closed form for the exact tree-level six-point
three-minus amplitude in the deep-water surface-elevation theory evaluated by
`bg.cpp`.

The closest direct source is Arkani-Hamed, Calisto, Ussembayev, Zhao, and Zhou,
["Surface Water Wave Scattering and the
Hydrotope"](https://arxiv.org/abs/2606.28280), arXiv:2606.28280v1 (2026).
It gives the complete two-minus formula, but states explicitly that detailed
analysis of the three-minus sector begins at six points and "will be
investigated in future work"; its cited follow-up is only "to appear."
Consequently it supplies the BG/Lagrangian framework and the neighboring
hydrotope result, not the requested $A_6^{(---+++)}$ formula.

Dyachenko, Kachulin, and Zakharov,
["Six-waves scattering matrix for water wave
equation"](https://www.fields.utoronto.ca/programs/scientific/12-13/mathofoceans/wavedynamics/Zakharov2.pdf)
(2012 preprint), derive a compact nine-diagram/channel expression for a
six-wave kernel.  It is not the present amplitude: their calculation uses the
quartic compact one-dimensional Zakharov equation, with all Fourier modes
projected to one propagation direction.  Their conclusion explicitly notes
that the exact water-wave equation has its own six-wave term which can change
the total coefficient.  Thus this expression is useful motivation for a
channel sum, but it cannot be substituted for the exact mixed-momentum BG
amplitude.

The older exact five-wave result of Dyachenko, L'vov, and Zakharov,
["Five-wave interaction on the surface of deep
fluid"](https://doi.org/10.1016/0167-2789(95)00168-4), Physica D 87 (1995)
233--261, concerns the lower-point effective Hamiltonian and does not contain
the genuinely new six-point three-minus answer.

## Consequence for this round

The literature does not shortcut the problem.  It does, however, support
testing a finite orbit sum over two- and three-particle channels.  Any such
test must be made against the exact BG evaluator and cannot import the 2012
quartic-model numerators.
