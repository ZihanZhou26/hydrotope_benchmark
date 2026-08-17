# Full-magnitude-sort refutation and the missing \(Q_T\)-wall orbit

## Result

The magnitude-tie fan is not the complete polynomial fan of
\[
R_{\mathrm{spline}}=A_6/i-P_{\mathrm{pole}}.
\]
Even after fixing the signed energy sheet, the exact polynomial continuation
changes when one triple quantity
\[
Q_{m;pq}=\omega_p^2+\omega_q^2-\omega_m^2
\]
changes sign while all nine cross-sector pair signs
\[
q_{mp}=\omega_p^2-\omega_m^2
\]
and the full labeled magnitude order remain fixed.  Therefore a coupled
Möbius construction over only the \(\beta\)-minimum/magnitude-tie fan cannot
assemble the complete \(R_{\mathrm{spline}}\).  At minimum, the regular
nine-element \(S_3(M)\times S_3(P)\) orbit \(Q_{m;pq}=0\) must be included as
well.

This is a branch-wall statement, not a pole statement.  The tested values are
generic and off every wall; no BG evaluation was made on \(q_{mp}=0\) or
\(Q_{m;pq}=0\).

## 1. Direct test of an unsigned full-sort polynomial

In the homogeneous on-shell quotient basis
\[
\mathcal B_8=\left\{
\omega_1^{a_1}\cdots\omega_5^{a_5}:
\sum_i a_i=8,\ a_5\leq1
\right\},\qquad |\mathcal B_8|=285,
\]
I attempted one exact polynomial reconstruction for each of the eight
symmetry-reduced magnitude words
\[
\{+-+--+,+--++-,+--+-+,+---++,
-+++--,-++-+-,-++--+,-+-++-\}.
\]
The sampling fixed the canonical labeled order of magnitudes for the word but
deliberately did not fix energy signs or \(Q_T\) signs.

Every \(285\times285\) system had exact rank \(285\) and zero training
residual.  On \(30\) fresh exact GMP holdouts per word, however, only
\[
\boxed{17/240}
\]
residuals vanished.  The per-word zero counts were
\[
(0,3,2,4,4,3,1,0).
\]
Thus an unsigned magnitude word does not support a single homogeneous
degree-eight polynomial.

These mixed fits are diagnostic only.  Their coefficient arrays are not
candidate chamber formulas and must not be used for assembly.

## 2. Controlled continuation test inside fixed pair cells

For a sharper isolation, I used the eight already validated round-3 branch
polynomials.  For each source branch I generated fresh exact points with the
same sorted sector word and the same complete labeled set of nine \(q_{mp}\)
signs.  The source polynomial was then evaluated without refitting.

The stored test battery contains:

* \(96/96\) same-\(Q_T\)-signature controls with zero residual;
* \(0/160\) probes with exactly one \(Q_T\) sign changed;
* after additionally requiring the same six energy signs,
  \(21/21\) controls with zero residual and \(0/15\) one-\(Q_T\)-flip probes
  with zero residual.

The fixed-energy one-wall probes cover
\[
Q_{1;45},\quad Q_{1;46},\quad Q_{1;56},\quad Q_{2;45},
\]
which are all representatives of the same
\(S_3(M)\times S_3(P)\) orbit.

## 3. Exact witness with identical signed labeled sorting cell

Take
\[
\omega=\left(\frac{21}{2},-8,1,-7,-6,\frac{19}{2}\right).
\]
It obeys both conservation equations, has energy-sign pattern
\[
(+,-,+,-,-,+),
\]
and descending labeled magnitude order
\[
(1,6,2,4,5,3).
\]
Its nine cross-pair signs are
\[
(q_{14},q_{15},q_{16},q_{24},q_{25},q_{26},q_{34},q_{35},q_{36})
=(-,-,-,-,-,+,+,+,+).
\]
Relative to the validated `round3_context_c_left` branch, all these data and
the energy signs agree.  Exactly one triple sign differs:
\[
Q_{1;45}=-\frac{101}{4}<0,
\]
whereas the source branch has \(Q_{1;45}>0\); every other \(Q_T\) sign agrees.

A fresh exact BG evaluation gives
\[
R_{\mathrm{spline}}=-49008548.
\]
Analytic continuation of the validated source-cell polynomial gives
\[
R_{\mathrm{source\ poly}}=\frac{19021715}{8},
\]
so
\[
\boxed{
R_{\mathrm{source\ poly}}-R_{\mathrm{spline}}
=\frac{411090099}{8}\ne0.}
\]
This witness fixes the complete labeled magnitude order, not merely its
unlabeled sector word, so neither an energy-sheet change nor a same-sector
label-order change can explain the mismatch.

## 4. Two pre-existing branch comparisons

The independently reconstructed pairs

* `round3_context_a_left` versus `round3_context_c_right`, and
* `round3_context_a_right` versus `round3_context_c_left`

have identical labeled magnitude orders and identical nine pair-sign
patterns within each pair.  Their exact degree-eight polynomial differences
are nevertheless nonzero, with \(188\) quotient-basis terms and leading
coefficient \(32\) on \(\omega_1^8\).  These comparisons involve energy-sheet
changes, so they are supporting evidence only; the fixed-energy witness above
is the load-bearing isolation of the \(Q_T\) wall.

## 5. Consequence for the compact assembly

The round-3 four-leg \(\beta=\min\) pair-wall brick remains exact.  What fails
is the hypothesis that its magnitude-tie fan is the whole fan.  A complete
assembly now needs at least two coupled wall orbits:
\[
\{q_{mp}=0\}_{3\times3}
\qquad\text{and}\qquad
\{Q_{m;pq}=0\}_{3\times3}.
\]
The unresolved minimal structure is therefore:

1. extract the denominator-free polynomial jump of \(R_{\mathrm{spline}}\)
   across one isolated \(Q_{m;pq}=0\) component on a fixed signed pair cell;
2. factor that \(Q\)-brick into compact blocks;
3. integrate the joint \(q/Q\) fan, including its intersections with the
   four-leg \(\beta\)-minimum fan;
4. only then determine a common symmetric \(R_0\).

No complete \(A_6\) formula is claimed this round.

## Reproducibility

* Mixed unsigned-sort reconstruction:
  `bots/student-2/code/round4_full_sort.py`
* Full exact mixed-fit data:
  `bots/student-2/data/round4_full_sort.json`
* Fixed-branch continuation diagnostic:
  `bots/student-2/code/round4_refinement_diagnostic.py`
* Exact controls and one-\(Q_T\)-flip probes:
  `bots/student-2/data/round4_refinement_diagnostic.json`
* Corrected/deprecated round-3 trace column:
  `bots/student-2/data/round3_wall_trace_scan_corrected.json`

The oracle was freshly copied from the shared immutable `bg.cpp`, rebuilt with
GMP, and queried in exact mode throughout.
