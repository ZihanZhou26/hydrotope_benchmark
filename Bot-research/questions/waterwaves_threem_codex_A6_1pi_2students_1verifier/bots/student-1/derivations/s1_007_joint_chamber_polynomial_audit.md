# Claim `s1_007`: exact degree-eight polynomials on eight joint-fan components

## Result

Part 1 of the round-5 task is closed by combining the analytic wall
enumeration in `s1_006` with an independent audit of the already-generated
exact bottom-up branch data.  The audit covers eight distinct full signatures
\[
\bigl(\operatorname{sgn}\omega_i,\operatorname{sgn}q_{mp},
\operatorname{sgn}Q_{m;pq}\bigr),
\]
each containing \(6+9+9=24\) fixed signs.

For every component, the pole-subtracted remainder
\[
R_{\rm spline}=A_6/i-P_{\rm pole}
\]
was reconstructed in the homogeneous on-shell quotient basis
\[
\mathcal B_8=
\left\{\omega_1^{a_1}\cdots\omega_5^{a_5}:
\sum_i a_i=8,\ a_5\leq1\right\},\qquad |\mathcal B_8|=285.
\]
All eight exact systems had rank \(285\), zero solve residual, and all
\(160/160\) fresh exact holdouts had zero residual:

| environment | side | rank | fresh exact holdouts |
|---|---:|---:|---:|
| `context_a` | left/right | \(285/285\) | \(20/20\), \(20/20\) |
| `context_b` | left/right | \(285/285\) | \(20/20\), \(20/20\) |
| `context_c` | left/right | \(285/285\) | \(20/20\), \(20/20\) |
| `context_d` | left/right | \(285/285\) | \(20/20\), \(20/20\) |

The eight 24-sign vectors are pairwise distinct.  In particular, these are
not magnitude-word fits that accidentally mix hidden \(Q\)-walls: every fit
and every holdout fixes the complete \(q/Q\) signature and the energy sheet.

## Why this closes the wall-set question

Within a fixed sign chamber of all subset momenta \(k_S\), every occurrence
of \(|k_S|\) in the BG recursion has a fixed linear branch.  The settled
factorization sum \(P_{\rm pole}\) removes the genuine propagator principal
parts, leaving a homogeneous degree-eight polynomial on that chamber.  Claim
`s1_006` proves that every non-soft equation \(k_S=0\), modulo
\(k_S=-k_{S^c}\), is one of
\[
q_{mp}=0\quad\text{or}\quad Q_{m;pq}=0.
\]
The exact full-rank fits and holdouts then provide the requested empirical
check that no hidden subdivision appears within several realized chambers of
this analytically complete arrangement.

This result does **not** use the stored 285-coefficient arrays as a proposed
formula.  They are diagnostic evidence only and do not address the remaining
compact joint-fan assembly.

## Audit reproduction

The audit directly checked the `solve_rank`, `solve_zero_residual`,
`holdout_zero_count`, every stored exact holdout residual, and the distinct
24-sign vectors in:

- `bots/student-2/data/round3_context_a.json`
- `bots/student-2/data/round3_context_b.json`
- `bots/student-2/data/round3_context_c.json`
- `bots/student-2/data/round3_context_d.json`

The reconstruction method and the full-signature sampler are documented in:

- `bots/student-2/code/round3_bottomup.py`
- `bots/student-2/derivations/s2_007_exact_cell_brick_and_nested_verdict.md`

The compact audit output was:

```text
a left/right: rank 285, solve_zero True, 20/20 + 20/20
b left/right: rank 285, solve_zero True, 20/20 + 20/20
c left/right: rank 285, solve_zero True, 20/20 + 20/20
d left/right: rank 285, solve_zero True, 20/20 + 20/20
TOTAL 160/160; distinct full signatures 8/8
```
