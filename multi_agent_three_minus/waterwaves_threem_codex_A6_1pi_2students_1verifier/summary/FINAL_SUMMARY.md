# FINAL SUMMARY — Compact closed-form $A_6$ in the three-minus sector

- **Status: SOLVED.** The full definition of done is met and **no blocking
  verifier gap remains**.
- **Final PI summary round:** 10 — 2026-07-27T01:40:47 UTC.
- **Companion documents:** the complete accepted result (formula, chamber/pole
  prescription, derivation, compactness account, tested points/residuals,
  provenance) is in `summary/SOLVED.md`. Current-state digest in
  `summary/logic.yaml`; running narrative in `summary/group_meeting_notes.md`.

---

## 1. What was asked

A genuinely compact, human-readable analytic closed form for the tree-level
six-point water-wave amplitude
$$
A_6(\omega_1,\dots,\omega_6),\qquad \sigma=(-1,-1,-1,+1,+1,+1),
$$
valid for arbitrary nondegenerate on-shell kinematics, with every chamber
prescription and every genuine pole/factorization prescription, a table-free
evaluator, and a PI-independent verification against a fresh `bg.cpp`. A
single-chamber result, a numerical fit, a rewrite of the BG recursion, or a
stored chamber-polynomial / coefficient-table representation is explicitly **not**
accepted.

## 2. The verified result (one line)

$$
\boxed{\,A_6=i\,g^{-3}\big(P_{\rm pole}+R_Q+R_0+R_q\big)\,}
$$
with minus legs $M=\{1,2,3\}$, plus legs $P=\{4,5,6\}$, and (writing
$(x)_+=\max(x,0)$, $h_{mp}=(\omega_p^2-\omega_m^2)_+$,
$Q_{m;pq}=\omega_p^2+\omega_q^2-\omega_m^2$, $t=P\setminus\{p,q\}$,
$d_{m;pq}=2(\omega_m+\omega_p)(\omega_m+\omega_q)$):

- **$R_q=4\sum_{m,p}h_{mp}\,H_1+2\sum_{m,p,\phi}h_{r,\phi(r)}h_{s,\phi(s)}\,H_2$** —
  the continuous **order-1 $q$-orbit** (9 single-hinge + 18 matching terms);
- **$R_0=H_0(u,v,e_-,e_+)$** — the smooth global remainder (1 term);
- **$R_Q=-32\sum_{m;\{p,q\}}(Q_{m;pq})_+^3\,\omega_m\omega_t$** — the **order-3
  $Q$-orbit** (9 terms);
- **$P_{\rm pole}=-64\sum_{Q_{m;pq}>0}\dfrac{\omega_m\omega_t Q_{m;pq}^2}{d_{m;pq}}\,
  \mathcal H(\min(\omega_m^2,Q);p,q)\,\mathcal H(\min(\omega_t^2,Q);r,s)$** —
  factorization part (9 channels), with the single truncated block
  $\mathcal H(B;c,d)=B-(B-\omega_c^2)_+-(B-\omega_d^2)_++(B-\omega_c^2-\omega_d^2)_+$.

The **entire numerator is 82 integer-coefficient monomials in THREE displayed
seeds** — $H_1$ (46), $H_2$ (23), $H_0$ (13) — assembled by finite
$S_3(M)\times S_3(P)$ orbit sums over ordinary positive parts, plus the single
$\mathcal H$-block. **Zero chamber-specific coefficients**; the same three seeds
generate every chamber numerator. The seeds are displayed in full in
`summary/SOLVED.md`.

**Chamber / pole prescription.** All chamber dependence is carried by the
positive parts $h_{mp}$, $(Q_{m;pq})_+$, and the $\min/(\cdot)_+$ inside
$\mathcal H$ — no flag, sort, or lookup. The relevant arrangement is the 18
subset-momentum hyperplanes $\{q_{mp}=0\}$ (order-1 jump, supplied by $R_q$) and
$\{Q_{m;pq}=0\}$ (order-3 jump, supplied by $R_Q$); $A_6$ is continuous across
every wall. The only denominators are $d_{m;pq}$ in the active ($Q>0$)
$P_{\rm pole}$ channels; $d_{m;pq}=0$ lies on the $\omega_p=-\omega_m$ sheet of
$q_{mp}=0$ where the numerator vanishes, so the apparent $1/d$ pole is
**removable** and $A_6$ is finite. Empirically the three-minus $A_6$ has **no
genuine factorization pole** in the probed interior: internal lines can go on
shell ($D_S=\omega_S^2/|k_S|-g\to0$) but the residue vanishes.

## 3. What is verifier-confirmed vs. what is an unverified claim

**Verifier-confirmed (round-8 Claude verifier, `VERDICT: VERIFIED`, independent
from-scratch oracle + hand-transcribed evaluator, >6000 exact rational BG
comparisons, zero mismatch):**

- the complete decomposition $A_6=i\,g^{-3}(P_{\rm pole}+R_Q+R_0+R_q)$ and every
  displayed piece, including the previously missing compact $R_0+R_q$;
- exact BG agreement across 93 chamber signatures / 55 $q$- and 31 $Q$-patterns
  (359 generic points); 288 minus/plus permutations (manifest invariance); 35
  hierarchical regimes; two-sided crossings of 204 $q$- and $Q$-walls (2202
  points) — the decisive off-wall cure test that killed the round-7 $C^0$-only
  brick; the $d_{m;pq}=0$ pole loci (removable) and 1552 internal-line $D_S=0$
  crossings (finite/removable); $g$-scaling; and the 5-point calibration against
  the sign-flipped two-minus master;
- table-free structure: the evaluator loads no coefficient table; 82 monomials
  in 3 seeds generate every chamber with 0 chamber-specific coefficients;
- **blocking gap G1 (the missing compact $R_q/R_0$) declared CLOSED.**

**PI-confirmed (independent of the students and the verifier):**

- round 9 (`pi_vchk_006`): a full independent re-implementation — clean-room
  oracle `bg_r9` + a hand-transcribed evaluator `pi_r9_eval.py` importing no
  student/verifier code — reproduced BG bit-for-bit across the entire acceptance
  battery, **5733 exact comparisons, zero residual** (81 $(q,Q)$-chambers,
  216 permutations, 28 hierarchical, two-sided $q/Q/d/D_S$ crossings, removable
  $d=0$ straddle, $g$-scaling, 5-pt calibration);
- round 10 (`pi_vchk_007`, this final round): a bounded fresh spot-check on a
  newly rebuilt md5-matched oracle `bg_final` reproduced the formula exactly on
  the anchor plus 81 fresh generic points over **40 distinct chambers —
  82/82 exact, zero residual**;
- earlier PI double-checks stand: the order-3 brick $-32\omega_m\omega_t$
  (`pi_vchk_004`), the joint $\{q=0\}\cup\{Q=0\}$ wall arrangement
  (`pi_vchk_003`), harness/degree/symmetry foundations (`pi_vchk_001`).

**Compactness judgment (a PI acceptance call, not a computed fact):** the
verifier assessed the compactness bar as met and left the final "human-readable"
adjective to the PI; the PI **rules it MET** — 82 non-chamber-specific integer
coefficients in three displayed seeds plus one $\mathcal H$-block and ordinary
positive parts is a finite positive-part/truncated-power orbit sum, exactly the
task's own permitted form, and far below the forbidden "hundreds of
chamber-specific coefficients."

**Remaining unverified claim (non-blocking):** chamber-coverage completeness is
**empirical, not a symbolic proof**. Sampling reaches only physically-realizable
chambers (BG cannot leave the on-shell manifold either); across the verifier and
PI this covered 90+ chamber signatures and 200+ wall crossings, but a symbolic
argument that the wall set is *exactly* these 18 hyperplanes (no hidden $k_S=0$
jump) is still owed. Residual risk is low (a piecewise-polynomial form matching
BG at many generic points per chamber and on both sides of every crossed wall),
and it is **not a correctness gap** in the formula. It does not block acceptance
under the stated definition of done and is recorded as the standing SOLVED
caveat.

## 4. Definition of done — checklist

| requirement | status |
|---|---|
| Exact agreement wherever practical; $\le10^{-10}$ relative otherwise | MET — exact rationals throughout, zero residual (verifier + PI) |
| $\ge20$ generic samples across chambers | MET — 359 (verifier) + 260 (PI) + 82 (final spot-check) |
| Minus/plus permutations | MET — 288 (verifier) + 216 (PI), manifest invariance |
| Hierarchical regimes | MET — 35 (verifier) + 28 (PI), $1/200\ldots1000\times$ |
| Two-sided chamber-wall & pole-orbit approaches | MET — 204 $q/Q$ crossings (verifier) + 54 (PI); removable $d=0$ straddle |
| Five-point calibration vs sign-flipped two-minus master | MET — $A_5=-19968\,i$, exact, + random points |
| PI independently implements and verifies the formula | MET — `pi_vchk_006` (full battery) + `pi_vchk_007` (fresh ratification) |
| Displayable from a few building blocks; not a coefficient list | MET — 3 seeds / 82 monomials; PI compactness ruling MET |
| Evaluator reconstructs $A_6$ without a chamber-specific table | MET — `pi_r9_eval.py` imports only `fractions`; loads no table |

## 5. Provenance

- **Formula:** student-1, claim `s1_010` (round 8), realizing student-2's
  predicted off-wall coupled single/double-hinge cocycle.
- **Independent verification:** Claude verifier, round 8 (`VERDICT: VERIFIED`,
  G1 CLOSED); PI, round 9 (`pi_vchk_006`) and round 10 (`pi_vchk_007`).
- **Artifacts:** derivation `bots/student-1/derivations/s1_010_round8_compact_hinge_candidate.md`;
  student evaluator `bots/student-1/code/round8_compact_candidate.py`; verifier
  `bots/verifier/code/vr8_core.py` + `bots/verifier/VERIFICATION.md`; PI
  evaluator `bots/pi/code/pi_r9_eval.py`, batteries `pi_r9_battery.py` /
  `pi_r9_poles.py` / `pi_r9_dpole.py`, final spot-check
  `pi_r9_eval.py`+`pi_final_spotcheck.py`; clean-room oracles `bots/pi/code/bg_r9`
  and `bots/pi/code/bg_final` (both md5 `41715c4af3ee5a61b1c4bfce40426ac8`, the
  immutable shared `bg.cpp`).

## 6. Bottom line

The six-point three-minus water-wave amplitude has a genuinely compact,
human-readable closed form: four positive-part / truncated-power orbit sums built
from **three integer-coefficient seed polynomials (82 monomials total)** and one
truncated block, with an explicit chamber and (removable) pole prescription and a
table-free evaluator. It is verifier-confirmed with G1 closed and independently
re-implemented and ratified by the PI. **The problem is SOLVED**; the sole
outstanding item is the non-blocking, low-risk symbolic wall-set completeness
proof.
