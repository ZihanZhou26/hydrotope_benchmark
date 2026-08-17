# Independent Verification — Round 8 — compact three-minus $A_6$

- **Verifier:** Claude verifier (independent)
- **Timestamp (UTC):** 2026-07-26T23:55:49
- **Round audited:** 8. Strongest new load-bearing item:
  - **student-1 [s1_010, post_032]:** the FIRST complete, table-free candidate for
    the full six-point amplitude,
    $$A_6=i\,g^{-3}\left(P_{\rm pole}+R_Q+R_0+R_q\right),$$
    with $R_0=H_0(u,v,e_-,e_+)$ and
    $R_q=4\sum_{m,p}h_{mp}H_1+2\sum_{m,p,\phi}h_{r,\phi(r)}h_{s,\phi(s)}H_2$,
    the three seed polynomials $H_0,H_1,H_2$ (13/46/23 monomials) written out
    explicitly. This is the object student-2's round-7/8 obstruction analysis
    predicted (coupled single/double-hinge cocycle) and it is the first candidate
    since round 1 that offers a *complete* $A_6$.
  - student-2 [s2_014/s2_015, post_031] shipped exact off-wall cofactor ground
    truth but **no $R_q$ candidate** (partial); nothing to promote there.

- **Oracle:** fresh from-scratch rebuild of the shared `bg.cpp` in my own directory
  (`bots/verifier/code/bg_r8`), built this round with
  `g++ -O2 -std=c++17 -o bg_r8 bg_r8.cpp -lgmpxx -lgmp`. Source **md5
  `41715c4af3ee5a61b1c4bfce40426ac8`** (= immutable shared reference, byte-identical
  to the canonical `./bg.cpp` and all four bot copies), **sha256
  `bd1afe67…9040c1`**. Every amplitude comes only from this binary in exact rational
  mode (`-n 6` and `--amp`) via my own wrapper.
- **Independence:** the evaluator `bots/verifier/code/vr8_core.py` is HAND-TRANSCRIBED
  from the WRITTEN derivation `s1_010_…md` (LaTeX for $P_{\rm pole}$, $R_Q$,
  $H_0,H_1,H_2$, the $\mathcal H$-block, and the $R_q$ orbit assembly). **The student
  evaluator `round8_compact_candidate.py` was NOT imported.** Both anchors and every
  component split reproduce from my transcription, so any typo between the displayed
  formula and the student's code would have surfaced (none did).

## Headline result of this audit

**The candidate SURVIVES independent attack — VERIFIED.** Across **> 6000 exact
rational BG comparisons** spanning the entire definition-of-done battery I found
**zero mismatches**. The formula reproduces a freshly-built exact BG oracle bit-for-bit
in every chamber, under all same-sign permutations, in hierarchical regimes, on both
sides of every $q$- and $Q$-wall, at the $d_{m;pq}=0$ pole loci, and arbitrarily close
to genuine internal-line-on-shell crossings. It is table-free. This is the first
complete candidate to pass; **G1 (the missing compact $R_q$/$R_0$) is CLOSED** subject
only to the PI's final compactness judgment (Finding 1, minor).

Critically, this is strictly stronger than the continuity property that killed the
round-7 $B^{\rm sym}$ candidate: there the cure test $S-R_q^{\rm sym}$ was $C^0$ but
off-wall-WRONG (smooth 0/18). Here the formula is off-wall-**correct** — it equals BG
exactly on both sides of every wall, so continuity is automatic and the off-wall
degree-6 cofactor is reproduced.

## Independent checks and outcomes

"PASS" = my independent computation reproduced BG with **zero** residual (exact rationals).

### V0. Anchors on the fresh oracle — PASS
$\{-8,2,3,4,5,-6\}$: $A_6/i=-9190656/7$; my split $P_{\rm pole}=42588288/7$,
$R_Q=-136630560$, $S=R_0+R_q=129233568$ — all exact.
$\{-\tfrac{154}{17},3,5,2,7,-\tfrac{135}{17}\}$: $A_6/i=-641893056/85$ — exact.

### V1. Multi-chamber random sweep — PASS (359/359)
359 fresh on-shell rational points; my formula equals BG **exactly on all 359**.
Coverage census: **93 distinct chamber signatures**, **55 distinct $q$-wall sign
patterns**, **31 distinct $Q$-wall sign patterns**. (`vr8_sweep.py`.)

### V2. Permutations within minus $\{1,2,3\}$ and plus $\{4,5,6\}$ — PASS (288/288)
For 8 base points I applied all $6\times6$ same-sign permutations via explicit
`--amp` kinematics. BG is invariant (0 changes), my formula is invariant (0 changes),
and formula $=$ BG on all 288. (`vr8_perm_hier.py`.)

### V3. Hierarchical regimes — PASS (35/35)
One frequency pushed to $\{1/200,\dots,1000\}\times$ the others. Exact on all 35.

### V4. Two-sided wall crossings — PASS (2202 points / 204 crossings)
On genuine on-shell 1-parameter families (bg `-n` keeps every point on-shell), I
straddled every detected sign flip of the 9 pair-wall locators $q_{mp}$ and 9
triple-wall locators $Q_{m;pq}$: **204 crossings**, both wall types, **0 mismatch**
at all 2202 sampled points. This is the decisive cure test the earlier candidates
failed; the new $R_q$ passes it. (`vr8_walls.py`.)

### V5. Factorization-pole loci $d_{m;pq}=2(\omega_m+\omega_p)(\omega_m+\omega_q)=0$ — PASS (40/40)
Approached the candidate's only denominators from both sides down to $\varepsilon=1/5000$.
BG stays **finite** at these loci (removable), and my formula matches exactly on both
sides — the $1/d$ apparent poles are spurious and correctly cancelled. (`vr8_poles.py`.)

### V6. Genuine internal-line on-shell crossings $D_S=\omega_S^2/|k_S|-g=0$ — PASS (3406 points / 1552 crossings)
Tracked every internal propagator $D_S$ ($2\le|S|\le4$) along many families and
straddled every sign flip with $|k_S|$ bounded away from 0: **1552 crossings across
all subset channels**, **0 mismatch** at 3406 points. Probing one crossing by
bisection to $|D_S|\sim2\times10^{-10}$, $|A_6/i|$ remained **finite** ($\sim1.3\times10^5$).
**Conclusion:** the physically-realized three-minus amplitude exhibits **no genuine
factorization pole** in the probed interior — internal lines can go on shell but the
residue vanishes, so $A_6$ is finite there and the formula tracks it exactly. The
question's "possible factorization poles" are (as it flagged) an expectation, not a
fact; here they are removable. (`vr8_polehunt.py`, `vr8_genuine_pole.py`.)

### V7. $g$-scaling — PASS (4/4)
$A_6/i = g^{-3}\,\text{stripped}(\omega)$ verified at $g\in\{1,2,3/2,5\}$; the on-shell
$\omega$-manifold is $g$-independent and only the prefactor scales.

### V8. Five-point calibration of the harness — PASS
$\{-\tfrac{14}{3},2,3,4,-\tfrac{13}{3}\}$: fresh bg_r8 gives $A_5=-19968\,i$ (exact).
My independent two-minus master formula (fact 2, applied to the sign-flipped minus
legs $4,5$) reproduces BG on the anchor and on **21/21** random 5-pt points — the BG
harness is confirmed against the known neighboring result.

### V9. Compactness / no-table audit — PASS (structural), PI judgment pending (Finding 1)
The evaluator imports only `fractions`, `itertools`, `argparse`; it reads **no data
file, JSON, or coefficient table**. The whole numerator is generated by the SAME three
seed polynomials for every chamber: $H_1$ (46 monomials), $H_2$ (23), $H_0$ (13) —
**82 displayed monomials** — assembled through 9 single-hinge + 18 matching-hinge + 9
$Q$-orbit terms + 9 pole channels + 1 global term, all via ordinary positive parts
$(x)_+$. **Zero chamber-specific coefficients.** My hand count of the seeds
(46/23/13) matches the claim.

## Findings

1. **[minor] Compactness clears the letter of the bar; the "human-readable" adjective
   is a PI acceptance call.** The candidate is genuinely table-free — 82 non-chamber-
   specific integer coefficients generate all chambers, far below the "list of hundreds
   of chamber-specific coefficients" the task forbids, and it is a finite positive-part
   orbit sum (exactly the task's own permitted examples). The one soft point is that a
   single seed $H_1$ carries 46 coefficients; whether the group considers 82 monomials
   "genuinely human-readable" is the PI's final judgment when writing `SOLVED.md`. I
   assess the requirement as **met**, with the seeds displayable in full.

2. **[minor] Chamber coverage is empirical, not a symbolic completeness proof.** My
   sampling can only reach physically-realizable chambers (BG cannot leave the on-shell
   manifold either); I hit 93 chamber signatures / 55 $q$-patterns / 31 $Q$-patterns and
   crossed 204 wall boundaries, but this corroborates rather than proves that *every*
   realizable chamber is covered. Given the formula is piecewise-polynomial and matches
   BG at many generic points per chamber plus on both sides of every crossed wall, the
   residual risk is low. (Same carried caveat as prior rounds; not a defect of this
   candidate.)

Note: I did **not** re-audit student-1's $900\times605$ rank/Wolfram-recovery machinery,
and I do not need to — the verifier attacks the *claim*, and the displayed closed form
reproduces fresh BG exactly on its own. The fit is merely how the formula was found; its
correctness is established by the >6000-point exact agreement, not by trusting the
linear algebra.

## Bottom line for the next PI (round 9 / final summary)

**PROMOTE.** For the first time an independent from-scratch oracle + hand-transcribed
evaluator confirms a *complete* table-free $A_6$ across the full definition-of-done
battery with zero residual: 20+ generic chambers (359 points, 93 signatures),
minus/plus permutations (288), hierarchical regimes (35), two-sided $q$- and $Q$-wall
crossings (204 crossings / 2202 points), the $d=0$ pole loci and genuine
internal-line crossings (finite/removable, tracked exactly), $g$-scaling, and the
5-pt calibration. The decomposition and its previously-pinned pieces ($P_{\rm pole}$,
$R_Q$) are re-confirmed, and the long-missing $R_0+R_q$ is now present, table-free, and
off-wall-correct — the exact failure mode ($B^{\rm sym}$, smooth 0/18) is decisively
passed here (off-wall exact on 204 crossings).

Remaining before `SOLVED.md`: only the PI's own independent re-implementation (as the
definition of done requires) and the final compactness judgment on 82 monomials
(Finding 1). No blocking correctness gap remains.

VERDICT: VERIFIED
