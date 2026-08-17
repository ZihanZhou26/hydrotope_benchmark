# SOLVED — Compact closed-form $A_6$ in the three-minus sector

- **Status:** SOLVED. Verifier-confirmed (round 8, `VERDICT: VERIFIED`) **and**
  independently re-implemented and re-verified by the PI (round 9).
- **Producer:** student-1, claim `s1_010` (round 8). Independent verification:
  Claude verifier round 8 (>6000 exact BG comparisons) and PI round 9 (5733
  additional exact BG comparisons, own hand-transcribed evaluator).
- **PI timestamp (UTC):** 2026-07-27T01:32:23

---

## 1. The formula

Sector $\sigma=(-1,-1,-1,+1,+1,+1)$: minus legs $M=\{1,2,3\}$, plus legs
$P=\{4,5,6\}$. All frequencies real, incoming, on the resonant manifold
$\sum_i\omega_i=0$, $\ \sum_i\sigma_i\omega_i^2=0$ (equivalently
$\sum_{p\in P}\omega_p^2=\sum_{m\in M}\omega_m^2$). Write $(x)_+=\max(x,0)$.

$$
\boxed{\,A_6=i\,g^{-3}\big(P_{\rm pole}+R_Q+R_0+R_q\big)\,}
$$

The four pieces are built from **three seed polynomials** and **one truncated
block**, summed over the $S_3(M)\times S_3(P)$ orbit. There is no chamber table.

### 1a. Regular part $R_0+R_q$

For $m\in M$ let $\{r,s\}=M\setminus\{m\}$; for $p\in P$ let
$\{t,z\}=P\setminus\{p\}$; let $\phi:\{r,s\}\to\{t,z\}$ run over the **two**
bijections. Define the pair-wall hinge
$$
h_{mp}=(\omega_p^2-\omega_m^2)_+ .
$$
Then
$$
R_q=4\sum_{m\in M}\sum_{p\in P} h_{mp}\,
      H_1\!\big(\omega_m,\omega_p,\ \omega_r+\omega_s,\ \omega_r\omega_s\big)
   \;+\;2\sum_{m\in M}\sum_{p\in P}\sum_{\phi}
      h_{r,\phi(r)}\,h_{s,\phi(s)}\,
      H_2\!\big(\omega_m,\omega_p,\ \omega_r+\omega_s,\ \omega_r\omega_s,\
      \omega_r\omega_{\phi(r)}+\omega_s\omega_{\phi(s)}\big),
$$
$$
R_0=H_0(u,v,e_-,e_+),\qquad
u=\!\sum_{m\in M}\!\omega_m,\quad
v=\!\!\sum_{m<m'\in M}\!\!\omega_m\omega_{m'},\quad
e_-=\omega_1\omega_2\omega_3,\quad e_+=\omega_4\omega_5\omega_6 .
$$

**Seed $H_1(a,b,s,v)$** (46 monomials):
$$
\begin{aligned}
H_1=2\big[&12s^6-21s^5a-22s^5b-115s^4v-48s^4ab-58s^4b^2\\
&+36s^3va+44s^3vb+13s^3a^3+12s^3a^2b-5s^3ab^2-4s^3b^3\\
&+268s^2v^2+25s^2va^2+308s^2vab+323s^2vb^2\\
&-16s^2a^4-66s^2a^3b-62s^2a^2b^2+30s^2ab^3+42s^2b^4\\
&+240sv^2a+240sv^2b-92sva^3+14sva^2b+328svab^2+222svb^3\\
&-64sa^4b-212sa^3b^2-206sa^2b^3-32sab^4+26sb^5\\
&-8v^3+42v^2a^2+72v^2ab+30v^2b^2\\
&-36va^4-112va^3b-78va^2b^2+36vab^3+38vb^4\\
&+4a^6-44a^4b^2-112a^3b^3-112a^2b^4-40ab^5\big].
\end{aligned}
$$

**Seed $H_2(a,b,s,v,c)$** (23 monomials):
$$
\begin{aligned}
H_2=-4\big[&4cs^2+4csa+4csb+22ca^2+4cab-22cb^2\\
&+4s^4+4s^3a+4s^3b-8s^2v+12s^2a^2-16s^2b^2\\
&-8sva-8svb+sa^3-9sab^2-4sb^3\\
&-23va^2+19vb^2+12a^4+22a^3b-12a^2b^2-22ab^3\big].
\end{aligned}
$$

**Seed $H_0(u,v,e_-,e_+)$** (13 monomials):
$$
\begin{aligned}
H_0=16\big[&69e_-^2v-126e_-e_+u^2-18e_-e_+v-40e_-uv^2\\
&+42e_+^2u^2-57e_+^2v-52e_+u^5+204e_+u^3v-54e_+uv^2\\
&+4u^8-32u^6v+68u^4v^2-16u^2v^3\big].
\end{aligned}
$$

### 1b. Triple-wall orbit $R_Q$

For $m\in M$ and an unordered plus pair $\{p,q\}\subset P$ with omitted plus leg
$t=P\setminus\{p,q\}$,
$$
Q_{m;pq}=\omega_p^2+\omega_q^2-\omega_m^2,
\qquad
R_Q=-32\sum_{m\in M}\ \sum_{\{p,q\}\subset P}(Q_{m;pq})_+^{3}\,\omega_m\,\omega_t .
$$

### 1c. Pole part $P_{\rm pole}$

Single truncated block (threshold = **sum of squares**)
$$
\mathcal H(B;c,d)=B-(B-\omega_c^2)_+-(B-\omega_d^2)_+ +(B-\omega_c^2-\omega_d^2)_+ .
$$
With $\{r,s\}=M\setminus\{m\}$, $t=P\setminus\{p,q\}$, and
$d_{m;pq}=2(\omega_m+\omega_p)(\omega_m+\omega_q)$,
$$
P_{\rm pole}=-64\!\!\sum_{\substack{m\in M,\ \{p,q\}\subset P\\ Q_{m;pq}>0}}\!\!
\frac{\omega_m\,\omega_t\,Q_{m;pq}^2}{d_{m;pq}}\;
\mathcal H\!\big(\min(\omega_m^2,Q_{m;pq});p,q\big)\,
\mathcal H\!\big(\min(\omega_t^2,Q_{m;pq});r,s\big).
$$

---

## 2. Chamber-selection and pole prescription

- **Chambers.** All chamber dependence is carried by the ordinary positive parts
  $h_{mp}=(\omega_p^2-\omega_m^2)_+$, $(Q_{m;pq})_+$, and the $\min/(\,\cdot\,)_+$
  inside $\mathcal H$. No flag, no sort, no lookup. The relevant arrangement is
  the **18 hyperplanes** $\{q_{mp}=\omega_p^2-\omega_m^2=0\}$ (9, jump order 1)
  $\cup\ \{Q_{m;pq}=0\}$ (9, jump order 3); both are genuine subset-momentum walls
  $k_S=0$. The formula is continuous across every wall (derivatives may jump);
  the order-1 $q$-jump is supplied by $R_q$, the order-3 $Q$-jump by $R_Q$.
- **At a $q$-wall** $q_{mp}=0$: set $h_{mp}=0$. Value-continuous.
- **At a $Q$-wall** $Q_{m;pq}=0$: both $R_Q$ and the matching $P_{\rm pole}$
  channel have continuous zero limits.
- **Pole prescription.** The **only denominators** are $d_{m;pq}$ in the active
  ($Q_{m;pq}>0$) $P_{\rm pole}$ channels. The locus $d_{m;pq}=0$ (i.e.
  $\omega_m=-\omega_p$ or $\omega_m=-\omega_q$) lies on the $\omega_p=-\omega_m$
  **sheet of the $q_{mp}=0$ wall**; there the numerator vanishes so the apparent
  $1/d$ pole is **removable** and $A_6$ is finite. Evaluate off $d_{m;pq}=0$; at
  an isolated $d_{m;pq}=0$ take the two-sided limit. **The three-minus $A_6$ has
  no genuine factorization pole in the probed interior**: internal lines can go
  on shell ($D_S=\omega_S^2/|k_S|-g\to0$) but the residue vanishes and $A_6$
  stays finite (verifier V6: 1552 crossings; PI: 106 crossings, all exact).

---

## 3. Structural argument (concise)

1. **Decomposition.** $A_6/i=P_{\rm pole}+R_{\rm spline}$, where
   $R_{\rm spline}=A_6/i-P_{\rm pole}$ is denominator-free, degree-8,
   dual-$S_3$-symmetric, and a continuous polynomial spline over the 18-wall fan.
   $P_{\rm pole}$ is fixed by factorization: on $Q_{m;pq}>0$ both cut sides are
   known two-minus $A_4$'s, giving the single $\mathcal H\mathcal H$ block over
   9 channels (verifier-confirmed, all chambers).
2. **Order-3 orbit.** Across $Q_{m;pq}=0$ the spline jumps at order exactly 3
   with degree-2 cofactor $-32\,\omega_m\omega_t$, so
   $R_Q=-32\sum(Q_{m;pq})_+^3\omega_m\omega_t$; then $S:=R_{\rm spline}-R_Q$ is a
   spline over the 9 pair walls only (verifier: $S$ smooth across 24/24 fresh
   isolated $Q$-walls).
3. **Order-1 orbit + global remainder.** $S=R_0+R_q$ was pinned by an exact
   linear existence solve: with the manifestly-continuous hinge basis
   $\Phi_f=\mathrm{Orb}_{S_3\times S_3}[\prod(q_{mp})_+^{r_{mp}}\prod\omega_i^{\alpha_i}]$
   (hinge depth $\le4$, degree 8) plus the 17-dim global $R_0$ basis
   $\{u^iv^je_-^ke_+^\ell\}$, the $900\times605$ system is **consistent**
   ($\mathrm{rank}\,A=\mathrm{rank}[A|S]=182$ at three primes). The recovered
   85-term solution uses **only** depth-1 (single hinge) and depth-2 (matching)
   terms; averaging over edge stabilizers collapses the two full 36-element
   Reynolds sums to the displayed 9 single-hinge + 18 matching terms with seeds
   $H_1,H_2$, and $R_0=H_0$. This is exactly the coupled single/double-hinge
   cocycle that student-2's off-wall obstruction analysis predicted, and it is
   off-wall–correct (it passes the two-sided cure test that killed the earlier
   $C^0$-only symmetric brick).

---

## 4. Compactness account (finite building blocks)

**Building blocks (all displayed above):**

| block | role | count |
|---|---|---|
| $H_1(a,b,s,v)$ | single-hinge seed | 46 monomials |
| $H_2(a,b,s,v,c)$ | matching-hinge seed | 23 monomials |
| $H_0(u,v,e_-,e_+)$ | global symmetric remainder | 13 monomials |
| $\mathcal H(B;c,d)$ | truncated block in $P_{\rm pole}$ | 4 truncated-power terms |
| $(x)_+$ | positive part | — |

**Orbit rules (finite $S_3\times S_3$ sums):** $R_q$ = 9 single-hinge + 18
matching terms; $R_Q$ = 9 triple-wall terms; $P_{\rm pole}$ = 9 pole channels
(only $Q>0$ active); $R_0$ = 1 global term.

**Total: 82 integer-coefficient monomials in 3 seeds**, assembled by ordinary
positive parts over a single symmetry orbit. **Zero chamber-specific
coefficients**; the *same* three seeds generate every chamber numerator. This is
a finite positive-part/truncated-power orbit sum — exactly the task's own
permitted form — not a stored chamber-polynomial table, not a coefficient
lookup, not a hidden divided-difference table. **PI compactness judgment: MET**
(fully human-readable; the mathematical content is visible in the written
formula). The evaluator `bots/pi/code/pi_r9_eval.py` loads no data file, JSON, or
coefficient table.

---

## 5. Independent PI verification (round 9)

- **Oracle:** clean-room rebuild `bots/pi/code/bg_r9` of the immutable shared
  `bg.cpp` (source md5 `41715c4a…`, sha256 `bd1afe67…9040c1`), exact rational
  mode only.
- **Evaluator:** `bots/pi/code/pi_r9_eval.py`, hand-transcribed by the PI from
  the written derivation `s1_010`; **no student/verifier code imported**.
- **Battery** (`pi_r9_battery.py`, `pi_r9_poles.py`, `pi_r9_dpole.py`) — total
  **5733 exact rational comparisons, zero residual**:

| test | result |
|---|---|
| Anchors $\{-8,2,3,4,5,-6\}$, $\{-\tfrac{154}{17},3,5,2,7,-\tfrac{135}{17}\}$ | $A_6/i=-\tfrac{9190656}{7},\,-\tfrac{641893056}{85}$ — exact; split $P_{\rm pole}=\tfrac{42588288}{7}$, $R_Q=-136630560$, $S=129233568$ |
| Generic multi-chamber sweep | 260 points / **81 distinct $(q,Q)$-chambers** (54 $q$-, 32 $Q$-patterns) — 260/260 |
| Minus/plus permutations | 216 evaluations (6 bases $\times$ 36) — BG invariant, 216/216 |
| Hierarchical ($1/200\ldots1000\times$) | 28/28 |
| Two-sided $q$-walls / $Q$-walls | 19 + 35 straddled crossings, exact both sides |
| Internal-line $D_S=0$ crossings | 106 straddled, $A_6$ finite, exact |
| Pole orbit $d_{m;pq}=0$ (removable) | 4733 near-pole + a clean two-sided sign-flip straddle (|d|$\sim2\times10^{-5}$), active channel, BG finite, exact both sides |
| $g$-scaling $A_6=g^{-3}\cdot$stripped | $g\in\{1,2,\tfrac32,5,\tfrac13\}$ — 5/5 |
| 5-pt calibration vs two-minus master (sign-flip) | anchor $A_5=-19968\,i$ + 28 random — exact |

- **Prior verifier confirmation (round 8):** independent from-scratch oracle +
  hand-transcribed evaluator, >6000 exact comparisons, zero mismatch; `G1`
  (missing compact $R_q/R_0$) declared CLOSED; `VERDICT: VERIFIED`.
- **Final-round PI ratification (round 10, `pi_vchk_007`):** a bounded fresh
  independent spot-check on a newly rebuilt md5-matched oracle `bg_final`
  (`pi_final_spotcheck.py`) reproduced the formula exactly on the anchor plus 81
  fresh generic on-shell points spanning **40 distinct $(q,Q)$-chambers** —
  **82/82 exact, zero residual** — reconfirming the load-bearing claim before
  sign-off. (Not a rerun of the full battery; that is `pi_vchk_006`.)

**Definition of done — all acceptance criteria met:** exact agreement
throughout; ≥20 generic samples across chambers (260/81); minus/plus
permutations; hierarchical regimes; two-sided wall and pole-orbit approaches;
5-pt calibration; PI independent re-implementation; displayable in a small number
of building blocks; not a coefficient list; table-free evaluator.

---

## 6. Caveat (non-blocking)

Chamber-coverage completeness is **empirical, not a symbolic proof**: the sweep
reaches physically-realizable chambers (BG cannot leave the on-shell manifold
either) — 81 $(q,Q)$-chambers hit and 160 wall crossings straddled — but a
symbolic proof that the wall set is *exactly* these 18 hyperplanes (no hidden
$k_S=0$ jump) is still owed. This has been a standing minor since the arrangement
was fixed; the residual risk is low (piecewise-polynomial form matching BG at
many generic points per chamber and on both sides of every crossed wall) and it
is **not** a correctness gap in the formula. It does not block acceptance under
the stated definition of done.
