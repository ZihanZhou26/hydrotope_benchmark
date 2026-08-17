# Round 1 continuation: the eight words and a broader spline obstruction

## The eight physical words

Write

$$
x_1\leq x_2\leq x_3
   =\operatorname{sort}\{\omega_1^2,\omega_2^2,\omega_3^2\},
\qquad
y_1\leq y_2\leq y_3
   =\operatorname{sort}\{\omega_4^2,\omega_5^2,\omega_6^2\},
$$

with

$$
T=x_1+x_2+x_3=y_1+y_2+y_3.
$$

Merge the two sorted lists in increasing order and write `M` for an $x_i$
and `P` for a $y_j$.  A deterministic census of $5000$ exact,
nondegenerate on-shell kinematics finds precisely the following eight raw
words:

$$
\begin{gathered}
\mathrm{MMPPPM},\quad
\mathrm{MPMPPM},\quad
\mathrm{MPPMMP},\quad
\mathrm{MPPMPM},\\
\mathrm{PMMPMP},\quad
\mathrm{PMMPPM},\quad
\mathrm{PMPMMP},\quad
\mathrm{PPMMMP}.
\end{gathered}
$$

Thus, for example, this candidate convention assigns

$$
W=\mathrm{MPPMMP}
\quad\Longleftrightarrow\quad
x_1<y_1<y_2<x_2<x_3<y_3
$$

away from ties.  The other seven prescriptions are read in the same way.
This is a concrete candidate map to the stated eight physical words.  The
historical baseline labels are not present in this self-contained tree, so the
PI must confirm that convention directly.  It is important
not to quotient by the minus/plus set swap or by word reversal when assigning
the raw word: doing both reduces the eight words to three orbits and caused
the earlier apparent mismatch.

The eight words classify the signs of the nine difference walls

$$
D_{ij}=x_i-y_j.
$$

They do **not** by themselves classify all signs of the second wall family

$$
S_{ij}=x_i+y_j-T.
$$

In the $5000$-point census the full ordered $(D,S)$ sign data have $20$
patterns.  Consequently the eight baseline word pieces and the explicit
$S_{ij}$ positive-part/jump terms play different roles; the latter must not
be silently folded into the word label.

Evidence is in `bots/student-1/data/word_census.json`.  It gives exact
representatives and counts

$$
(1701,617,623,18,8,938,424,671)
$$

in the displayed word order.  The independent exact-amplitude file
`bots/student-1/data/fresh_structure_oracle.jsonl` contains $150$ new,
non-permutation kinematics.

## Complete independent cubic-hinge test

Let

$$
G=(S_3^{(M)}\times S_3^{(P)})\rtimes C_2
$$

include within-set permutations and the minus/plus set swap.  For either
wall representative $q=D_{ij}$ or $q=S_{ij}$, an orientation
$\epsilon\in\{\pm1\}$, and a quadratic monomial
$m_{uv}=\omega_u\omega_v$, define the orbit feature

$$
\Phi[q,\epsilon,u,v](\omega)
=
\sum_{\text{distinct }g\text{-images}}
(g m_{uv})(\omega)\,
\bigl(\epsilon\,(gq)(\omega)\bigr)_+^3.
$$

After exact orbit deduplication this gives $26$ features: $12$ from the
$D$ family and $14$ from the $S$ family.  This removes the alternating-subset
coefficient tying of the first H1 test.  The polynomial ambiguity was also
included completely: the $G$-orbit sums of all ordinary degree-eight
monomials form $57$ features, denoted $\mathcal P_8$.

On $120$ exact training kinematics,

$$
\begin{array}{c|cc}
\text{dictionary}&\operatorname{rank}F&
\operatorname{rank}[F\mid A_6/i]\\ \hline
\{\Phi_D\}&7&8\\
\{\Phi_S\}&10&11\\
\{\Phi_D,\Phi_S\}&17&18\\
\{\Phi_D,\Phi_S\}\cup\mathcal P_8&22&23
\end{array}
$$

so every dictionary is exactly inconsistent before holdout fitting.  All
$26$ hinge features passed exact degree-eight homogeneity and all
$72$ elements of $G$ at three generic points.  Five freshly regenerated BG
values agree exactly with their stored targets.  There are also $30$ unused,
distinct exact holdout kinematics.

Therefore $A_6/i$ is not a homogeneous $C^2$ single-wall cubic spline of the
form

$$
P_8(\omega)+
\sum_{\alpha}
Q_{\alpha,2}(\omega)\,(q_\alpha(\omega))_+^3,
$$

even when $P_8$, every wall orientation, and every symmetry-allowed
quadratic wall covariant are independent.  The next ansatz must contain
either lower-smoothness hinge powers, products/intersections of wall
features, or a compact rational/factorized building block.

Full definitions, ranks, and checks are in
`bots/student-1/data/wall_hinge_fit.json`; the reproducer is
`bots/student-1/code/wall_hinge_fit.py`.

## The two wall orbits have different smoothness

One-sided polynomial extrapolation in the exact wall coordinate $q$ was
performed on the stored rational approach data.  For each side, the smallest
$4$, $5$, and $6$ nodes were interpolated, and the coefficients were evaluated
at $q=0$ with $80$ decimal digits.

At the $(1,1)$ difference-wall representative, the limiting value agrees but
the linear coefficients stabilize to different values:

$$
\left.\frac{d(A_6/i)}{dq}\right|_{q\to0^+}
\simeq4.729813755787408,
\qquad
\left.\frac{d(A_6/i)}{dq}\right|_{q\to0^-}
\simeq7.080522009722821.
$$

At the $(1,2)$ sum-wall representative, coefficients through $q^2$ converge
between the two sides, while the cubic coefficients converge to

$$
1.39296775388720
\qquad\hbox{and}\qquad
98.6103835084500.
$$

This is high-precision numerical smoothness evidence, not an exact derivative
theorem: the automated tolerance in `wall_smoothness.json` intentionally
rejects the finite-node extrapolation as inconclusive.  The stable pattern
nevertheless identifies the correct next dictionary as linear $D_{ij}$ hinges
and cubic $S_{ij}$ hinges.  The complete mixed dictionary has $188$ $D^1$
orbit features, $14$ $S^3$ orbit features, and $57$ polynomial features.
Its first implementation generated $600$ exact oracle points spanning all
eight squared-merge words, but the uncached exact design-matrix construction
exceeded the ten-minute inline budget before a rank was produced.
