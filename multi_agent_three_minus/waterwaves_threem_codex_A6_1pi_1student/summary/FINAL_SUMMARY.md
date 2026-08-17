# FINAL SUMMARY — compact closed-form $A_6$, three-minus sector

**Round 10 (final PI summary). Author: PI. Date: 2026-07-26T22:11:23 UTC.**

## Verdict

**NOT SOLVED (substantial, independently verified partial result).** The task
asks for a genuinely human-readable full-domain closed form for the tree-level
six-point amplitude $A_6(\omega_1,\dots,\omega_6)$ in the three-minus sector
$\sigma=(-1,-1,-1,+1,+1,+1)$. We have a **compact, exact, independently
verified closed form for two opposite chambers**, but **not for the full
domain**: the other physically realized chambers carry strictly higher-degree
numerators/denominators that were never reconstructed, so the conjectured
single master object remains untested. Per the definition of done, this is
recorded as `FINAL_SUMMARY.md`, **not** `SOLVED.md`.

This final round re-verified **every load-bearing claim** below on a **truly
fresh binary `bg_r10`** — built this round from a byte-identical copy of the
immutable root `bg.cpp` (md5 `41715c4af3ee5a61b1c4bfce40426ac8`, sha256
`bd1afe67…c9040c1`) — and with **points I collected myself** [pi_v_030].

---

## 1. Problem recap

Deep-water 1D surface gravity waves, dispersion $\omega_i^2=g|k_i|$, so
$k_i=\sigma_i\,\omega_i^2/g$. All momenta/frequencies incoming; on the resonant
manifold $\sum_i\omega_i=0$ and $\sum_i\sigma_i\omega_i^2=0$. Sector: minus legs
$1,2,3$, plus legs $4,5,6$. Reference: exact GMP evaluator `bg.cpp` (immutable
root, md5 `41715c4af3ee5a61b1c4bfce40426ac8`). Compactness bar: the numerator
must be a short set of defined analytic building blocks — **no stored chamber
polynomial table, coefficient dump, or flag-by-flag lookup**.

---

## 2. What IS solved and banked (independently verified)

### 2.1 The skeleton (all PI-verified, exact)

- **Reality & symmetry** [pi_v_005]: $A_6/i$ is real, degree-8 homogeneous, and
  invariant under all $36$ $S_3\times S_3$ leg permutations **and** the
  minus$\leftrightarrow$plus swap.
- **Prefactor** [pi_v_012, corr. pi_v_014]: $A_6 = i\,\big(\prod_{k=1}^6\omega_k\big)\,H$
  with $H=A_6/(i\prod\omega)$ rational, degree-2 homogeneous, $S_3\times S_3$+swap
  symmetric, and **sign-dependent** (NOT a function of the squares).
- **Interior momentum walls** [pi_v_004]: exactly 18, in two $S_3\times S_3$
  orbits, $\{a_i-b_j=0\}$ (9) and $\{a_i+b_j-T=0\}$ (9), with
  $a_i=\omega_i^2,\ b_j=\omega_{3+j}^2,\ T=\sum a_i=\sum b_j$.
- **Finite, no genuine poles** [pi_v_006]: two-sided approaches to every
  factorization surface $h_S=\omega_S^2-|k_S|=0$ and to every momentum wall give
  **finite** $A_6$; each $h_S$ is **removable**.
- **Genuinely rational** [pi_v_008/009/018]: $A_6$ is NOT piecewise-polynomial,
  even holding all 53 signs (18 walls + 35 factorization surfaces) constant on a
  single true piece. (So any pure box-spline/truncated-power numerator is dead.)

### 2.2 The compact TWO-CHAMBER formula (BANKED)

Chart eliminating legs $1,6$: $(u,v,r,s)=(\omega_2,\omega_3,\omega_4,\omega_5)$
(legs $2,3$ minus; $4,5$ plus). Define
$$
\Omega=u+v+r+s,\qquad e_2=e_2(u,v,r,s),\qquad
B_M=u^2+v^2+e_2,\qquad B_P=r^2+s^2+e_2,
$$
$$
L=(u+r)(u+s)(v+r)(v+s),\qquad C(u;r,s)=r^3(u+s)+s^3(u+r).
$$
Then in the **all-$+$ comparison-matrix** chamber (piece **A**, base
$\omega=(-7,9,-8,-3,-4,13)$),
$$
\boxed{\,H_A=\frac{64\,rs\,(r^2+s^2)}{B_P}
-\frac{32\,r^2s^2\,(r^2+s^2)\,\Omega}{u\,(u+r)(u+s)\,B_M}
-\frac{32\,rs\,\Omega\,C(u;r,s)}{u\,L}
-\frac{64\,rs\,(r^2+s^2)(u+r+s)}{v\,(u+r)(u+s)}\,}
$$
and the **all-$-$** chamber (piece **B**) is the minus$\leftrightarrow$plus swap
$H_B(u,v,r,s)=H_A(r,s,u,v)$. The amplitude is recovered by
$A_6 = i\big(\prod_\ell\omega_\ell\big)H$.

Equivalently, in a single-$P/Q$ form with a genuine 31-term
weighted-degree-9 core $F$,
$$
H_A=\frac{-32\,rs\,\Omega\,F(m_1,p_1,m_2,p_2)}{u\,v\,L\,B_M\,B_P},\qquad
H_B=\frac{-32\,u\,v\,\Omega\,F(p_1,m_1,p_2,m_2)}{r\,s\,L\,B_M\,B_P},
$$
with $m_1=u+v,\ m_2=uv,\ p_1=r+s,\ p_2=rs$; the two forms are the same rational
function [pi_v_026, re-verified pi_v_030]. Reduced $H_A$ is genuinely rational
with $\gcd(P,Q)=1$, homogeneous $\deg N=12$, and $\deg Q_{\rm hom}=10$ factoring
**exactly** as $u\,v\,(r{+}u)(r{+}v)(s{+}u)(s{+}v)\,B_MB_P$ [pi_v_021/027,
re-verified symbolically pi_v_030].

**Physical content of the blocks.** For $S=\{2,3,4,5\}=\{1,6\}^c$,
$B_M+B_P=\omega_S^2$ and $4B_MB_P=\omega_S^4-k_S^2=h_S(\omega_S^2+|k_S|)$
[pi_v_021, re-verified symbolically pi_v_030]: $B_M,B_P$ are the two sign-branches
of the complementary internal-line propagator $h_{\{1,6\}^c}$. The removable
$h_S$ sits **inside** $Q$ and the numerator supplies the compensating zero —
pi_v_006 removability made explicit. The denominator building blocks are
**SIGNED** (single legs $\omega_i$, mixed pair sums $\omega_i+\omega_j$, and
$B_M,B_P$); the mixed-pair factors and $B_M,B_P$ are chart-universal, only the
single-leg product is chamber-selected.

**Compactness of this partial result.** Piece A is **FOUR rational channel
blocks**, each with a single simple denominator ($B_P$; $u(u+r)(u+s)B_M$; $uL$;
$v(u+r)(u+s)$); piece B is one swap of A. No coefficient table is used.

**Verification (round 10, fresh build + fresh data).** `bg_r10` built from the
immutable root `bg.cpp` (source md5 identical; canonical check `bg_r10 -n6 -w
2,3,5,7` reproduces $A_6=i(-29948208/17)$). The four-block form matches the PI's
own independent 31-term core symbolically (`sympy.cancel(fourblock - core)=0`
for A and B) and reproduces `bg_r10` **exactly** (`fractions.Fraction`) on 40/40
in-piece points per piece [pi_v_030]. This reconfirms the round-6/7/8/9 banks
(pi_v_021/023/026/028) against yet another fresh immutable-source binary.

**Provenance.** Reconstruction/factorization: PI round 6 (pi_v_021).
Two-chamber single-core form: student round 6 (s1_018/019), PI-confirmed round 7
(pi_v_023). Four-block compression: student round 7 (s1_020), PI-confirmed round 8
(pi_v_026). Rationality no-go for a pure master: student round 7 (s1_021),
PI-confirmed round 8 (pi_v_027). Fresh-build re-banks: rounds 9–10
(pi_v_028, pi_v_030).

---

## 3. The precise remaining obstruction (why this is not the full answer)

The two-chamber formula holds **only** in the two opposite chambers and does
**not** extend:

- **Boundary** [pi_v_024, re-confirmed pi_v_029/030]: both $H_A$ and $H_B$ fail
  at all three other realized bases (`12ea165a03`, `7608cb858a`, `a2fa6ab8af`).
  At `12ea165a03` (base $\omega=(-20/7,9,8,2,-5,-78/7)$,
  $A_6/i=1347295721472/184877$), the round-10 check gives $H_A$ pred
  $=1191603200/77$, $H_B$ pred $=27082874880/7$, neither equal to BG, and
  **0/30** in-piece perturbations match either formula. Notably `12ea165a03` has
  the **same** free-leg comparison matrix as A but the **opposite** sign of
  $h_{\{1,6\}^c}$ (so $B_MB_P$ flips sign): formula-chambers are indexed by
  **more than** the comparison matrix.

- **Higher degree** [pi_v_025, extended pi_v_029/030]: in `12ea165a03` the
  dehomogenized cone target $h$ has **no** rational representation of low
  degree. An equal-bound modular rank scan $[M_{\le d}\mid -h\,M_{\le d}]$ on
  **1250 exact in-piece points I collected myself this round with `bg_r10`**
  (seed 101010, persisted at `bots/pi/code/round10_pts_12ea165a03.json`) is
  **full column rank** (nullity $(0,0)$ over primes $2147483647$ and
  $2147483629$) at **both $d=12$ and $d=13$**. So $d_{\rm eq}\ge14$, hence
  $\deg Q_{\rm hom}\ge12$ in this chamber — **strictly above** the solved
  chambers' $\deg Q_{\rm hom}=10$. The student pushed this one rung further
  (s1_022: $d=14$ also empty $\Rightarrow d_{\rm eq}\ge15$, $\deg Q_{\rm hom}\ge13$,
  $\deg P_{\rm hom}\ge15$); I independently confirm the load-bearing structural
  fact ($\ge12$, with entirely fresh data) and accept the $\ge13$ refinement as
  reported.

**Consequence.** The full-domain answer is **not** "one 31-term core $F$ plus a
single-leg reselection rule." The other realized chambers are genuinely
more complex. The leading hypothesis for the full-domain object is a **single
compact RATIONAL signed-channel master** — the true analog of the two-minus
box-spline sum $\sum_S(-1)^{|S|}(\beta^2-\sum_S\omega^2)_+^{n-3}$ — whose
truncations reduce to the four-block $H_A$ in the all-$+$ chamber and generate
the higher-degree pieces elsewhere. A **pure** positive-part / box-spline master
(polynomial per sign chamber) is **excluded** [pi_v_027], because reduced $H_A$
is genuinely rational ($\gcd(P_A,Q_A)=1$, $Q_A$ nonconstant), so equality on the
open A-chamber would force $Q_A\mid P_A$. The master must use rational signed
channels.

**What blocks closing it.** A second, higher-degree chamber ($\deg Q_{\rm hom}\ge13$)
was never reconstructed or factored — the technician sub-agent exhausted its
isolated context on the deg-13/14 batch and produced no artifact (round 7),
and the round-8 push established only the negative degree bound, not a factored
$Q$. Without at least one factored higher-degree chamber, the new signed
denominator factors (beyond $u,v,(r{+}u)(r{+}v)(s{+}u)(s{+}v),B_M,B_P$) are
unknown and the signed-channel master hypothesis is untested. Reaching
$d_{\rm eq}\ge15$ means the first candidate reconstruction is a 4-variable
degree-15 fit — a larger scan than what was run, the concrete next step. This is
a **tractability** obstruction, not a wrong method.

---

## 4. Independent verification method (round 10)

All checks used `bg_r10`, freshly built this round from the immutable root
`bg.cpp` (source byte-identical, md5 `41715c4af3ee…`, sha256 `bd1afe67…c9040c1`);
code `bots/pi/code/round10_final_verify.py`, output `…/round10_final_verify.out`.
Every result below is **PASS**.

0. **Five-point calibration** (BG-harness validity): three-minus $A_5$ = the
   sign-flipped two-minus formula, exact at 4 points, plus the two-minus $n=5$
   self-check at 2 points (**6/6 exact**).
1. **Symbolic** (BG-independent): four-block $H_A$, $H_B$ equal the PI's own
   31-term core via `sympy.cancel(...) = 0`; **and** $B_M+B_P=\omega_S^2$,
   $4B_MB_P=\omega_S^4-k_S^2$; **and** reduced $H_A$ has $\gcd(N,Q)=1$,
   $\deg N=12$, $\deg Q=10$ factoring exactly as
   $u\,v\,(r{+}u)(r{+}v)(s{+}u)(s{+}v)\,B_MB_P$ (`sympy.factor`).
2. **Numeric**: four-block $H_A$, $H_B$ reproduce `bg_r10` exactly
   (`fractions.Fraction`), 40/40 in-piece points per chamber (same 53-sign
   vector enforced).
3. **Boundary**: two-chamber formula fails at `12ea165a03` (base + 30 in-piece
   perturbations, 0 matches).
4. **Obstruction**: equal-bound cone rank scan full rank at $d=12,13$ over two
   primes on **1250 in-piece points self-collected with `bg_r10`**.

The REQUIRED five-point calibration was thereby re-established this round
directly against `bg_r10`, and was first banked in round 1 [pi_v_001/002].

---

## 5. Ruled-out approaches (do not revisit)

- Piecewise-polynomial numerator [pi_v_008/009/018].
- Fit in symmetric invariants $(s,p,r,t)$ — only algebraic, not low-degree
  rational [pi_v_011].
- $H$ even / function of the squares — false [pi_v_014].
- $H=P/Q$ with $Q$ a product of **even** degree-$\le2$ blocks — false
  [pi_v_017/019], explained by parity: the true blocks are SIGNED [pi_v_021].
- Simple even-$|K|$ single-$1/h_S$ channel orbit sums — false [s1_017, conf
  pi_v_022].
- The two-chamber form as the FULL answer via single-leg reselection — false
  [pi_v_024/025].
- PURE polynomial$\times$positive-part/truncated-power master (no rational
  denominators) — false [s1_021, conf pi_v_027].
- Literature: no published exact $A_6^{(---+++)}$ (arXiv:2606.28280 defers this
  sector) [s1_016].

---

## 6. Best-verified-progress statement

- **Verified full closed form for 2 of the realized chambers** (the two opposite
  comparison-matrix chambers), compact (four signed rational channel blocks, or
  one 31-term core $F$), reconstructed and factored from first principles, and
  reproduced **exactly** against a fresh immutable-source BG build [pi_v_030].
- **Complete structural characterization**: prefactor $\prod\omega$; genuine
  rationality; removable propagator surfaces sitting inside $Q$; SIGNED
  denominator blocks identified as single legs, mixed pair sums, and the two
  branches of the complementary internal-line propagator.
- **Open**: a genuinely human-readable full-domain formula. Precise obstruction:
  the other realized chambers have $\deg Q_{\rm hom}\ge13$ (vs 10) and none was
  reconstructed/factored, so the conjectured rational signed-channel master
  object — the only structurally viable full-domain candidate — is **untested**.
  The concrete next step is a 4-variable degree-$\ge15$ cone reconstruction of
  one higher-degree chamber (CRT over $\ge5$ primes + rational reconstruction +
  factorization), then testing whether the four-block seed plus sign-activated
  extra rational blocks reproduces both A and that chamber.
