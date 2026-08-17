# Group meeting notes — compact $A_6$ (three-minus sector)

**Round 10 — PI — final summary — 2026-07-27T01:40:47 UTC — SOLVED (signed off)**

Final PI summary round: no new work assigned. I read both round-8 student
handoffs and the round-8 verifier report (`VERDICT: VERIFIED`, G1 CLOSED), and
confirmed the state is stable and consistent. Under the exceptional policy I ran
**one bounded independent double-check** of the load-bearing claim
(`pi_vchk_007`): a freshly rebuilt md5-matched oracle `bg_final` +
`pi_final_spotcheck.py` reproduced the compact formula **exactly on 82/82 points
across 40 distinct $(q,Q)$-chambers, zero residual** — ratifying the SOLVED
verdict on a fresh binary without rerunning the full battery. `summary/SOLVED.md`
stands; `summary/FINAL_SUMMARY.md` written; `summary/logic.yaml` updated. The
only outstanding item is the standing **non-blocking** minor (symbolic wall-set
completeness — empirical coverage only, low risk, not a correctness gap). No
blocking verifier gap remains. Full acceptance-vs-unverified breakdown in
`summary/FINAL_SUMMARY.md`.

---

**Round 9 — PI — 2026-07-27T01:32:23 UTC — SOLVED**

## Headline
**The problem is solved.** student-1's round-8 complete candidate (`s1_010`) was
verifier-confirmed (round 8, `VERDICT: VERIFIED`, >6000 exact BG comparisons,
blocking gap **G1 CLOSED**), and this round I **independently re-implemented and
re-verified it** as the definition of done requires. My clean-room oracle
`bg_r9` + my own hand-transcribed evaluator `pi_r9_eval.py` (no student/verifier
code imported) reproduce a fresh exact BG oracle bit-for-bit across **5733
comparisons, zero residual**, spanning the entire acceptance battery.
`summary/SOLVED.md` is written.

## The formula
$$
A_6=i\,g^{-3}\big(P_{\text{pole}}+R_Q+R_0+R_q\big),\qquad
M=\{1,2,3\},\ P=\{4,5,6\}.
$$
- **$P_{\text{pole}}$** — one $\mathcal H$-block, 9 channels ($Q_{m;pq}>0$),
  threshold = sum of squares. Only denominators $d_{m;pq}$ (removable poles).
- **$R_Q=-32\sum(Q_{m;pq})_+^3\omega_m\omega_t$** — order-3 $Q$-orbit, 9 terms.
- **$R_0=H_0(u,v,e_-,e_+)$** — global symmetric remainder, 13 monomials.
- **$R_q=4\sum h_{mp}H_1+2\sum h\,h\,H_2$** — continuous order-1 $q$-orbit,
  $h_{mp}=(\omega_p^2-\omega_m^2)_+$; 9 single-hinge + 18 matching terms.

**Building blocks:** THREE seeds $H_1$ (46 monomials), $H_2$ (23), $H_0$ (13) =
**82 integer coefficients**, plus the $\mathcal H$-block and ordinary positive
parts. **Zero chamber-specific coefficients**; the same seeds generate every
chamber. Full display in `summary/SOLVED.md`.

## Why it works (structure)
$P_{\text{pole}}$ is fixed by factorization (both cut sides are two-minus
$A_4$'s). The remainder $R_{\text{spline}}=A_6/i-P_{\text{pole}}$ is a
denominator-free degree-8 dual-$S_3$ continuous spline over the 18-wall fan
$\{q_{mp}=0\}\cup\{Q_{m;pq}=0\}$; $R_Q$ supplies the order-3 $Q$-jump and $R_q$
the order-1 $q$-jump, leaving the smooth $R_0$. The decisive round-8 existence
solve ($900\times605$, rank $182$=$182$ at three primes) pinned $R_q$ to the
**coupled single/double-hinge cocycle** that student-2's off-wall obstruction
analysis had predicted — off-wall-correct, unlike the round-7 $C^0$-only
symmetric brick (H5).

## PI independent verification (round 9, `pi_vchk_006`) — 5733 exact, 0 residual
| test | result |
|---|---|
| anchors + component split | exact ($A_6/i$, $P_{\text{pole}}$, $R_Q$, $S$) |
| generic sweep | 260/260 across **81 $(q,Q)$-chambers** |
| minus/plus permutations | 216/216, BG invariant |
| hierarchical $1/200\ldots1000\times$ | 28/28 |
| two-sided $q$/$Q$ walls | 19 + 35 straddles, exact both sides |
| internal-line $D_S=0$ | 106 crossings, $A_6$ finite, exact |
| removable pole $d_{m;pq}=0$ | 4733 near-pole + clean two-sided straddle ($|d|\sim2\times10^{-5}$, active channel, finite, exact) |
| $g$-scaling | 5/5 |
| 5-pt calibration | anchor + 28/28 vs two-minus master |

## Definition of done — met
Exact agreement throughout; ≥20 generic samples across chambers (260/81);
minus/plus permutations; hierarchical regimes; two-sided wall and pole-orbit
approaches; 5-pt calibration; **PI independent re-implementation**; displayable
in a few building blocks; not a coefficient list; table-free evaluator.

## One non-blocking caveat
Chamber coverage is **empirical, not a symbolic completeness proof** (a symbolic
argument that the wall set is *exactly* the 18 hyperplanes is still owed). Low
residual risk; not a correctness gap; recorded in `SOLVED.md`.

## Credit
Formula: **student-1** (`s1_010`, round 8), realizing **student-2**'s predicted
off-wall cocycle. Verification: Claude verifier (round 8) + PI (round 9).
