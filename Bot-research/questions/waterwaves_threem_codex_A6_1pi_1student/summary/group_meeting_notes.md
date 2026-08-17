# Group meeting notes — compact closed-form $A_6$ (three-minus sector)

_Maintained by the PI as a bounded current-state digest (not an append log)._

## FINAL STATE (round 10 — 2026-07-26T22:11:23) — NOT SOLVED (verified partial)

**Verdict:** the two opposite chambers are solved compactly and independently verified; the full-domain
human-readable closed form was **not** reached. `summary/FINAL_SUMMARY.md` is written; `SOLVED.md` is
**not**. Precise blocker: the other realized chambers are strictly higher-degree ($\deg Q_{\rm hom}\ge13$
vs $10$) and none was reconstructed/factored, so the conjectured **rational signed-channel master**
object is untested (a pure box-spline master is excluded [pi_v_027]). Details below.

**Round-10 final re-verification [pi_v_030].** Every load-bearing claim was independently reproduced this
round on a **truly fresh binary `bg_r10`** (byte-identical source to the immutable root `bg.cpp`, md5
`41715c4a…`, sha256 `bd1afe67…`; canonical check reproduces $A_6=i(-29948208/17)$) with the PI's own code
and own data: (0) **five-point calibration 6/6 exact** (three-minus $A_5$ = sign-flipped two-minus, plus
two-minus $n=5$); (1) **symbolic** (BG-independent): `cancel(fourblock − core)=0` for A,B, plus
$B_M+B_P=\omega_S^2$, $4B_MB_P=\omega_S^4-k_S^2$, and reduced $H_A$ has $\gcd=1$, $\deg N=12$,
$\deg Q=10$ factoring **exactly** as $uv(r{+}u)(r{+}v)(s{+}u)(s{+}v)B_MB_P$; (2) **numeric** four-block
$H_A,H_B$ reproduce `bg_r10` **exactly** (`Fraction`) 40/40 in-piece per chamber; (3) **boundary**:
both fail at `12ea165a03`, 0/30 in-piece; (4) **obstruction**: an equal-bound rank scan on **1250
in-piece points I collected myself** with `bg_r10` is full column rank (nullity $(0,0)$ over two primes)
at **both $d=12$ and $d=13$** $\Rightarrow \deg Q_{\rm hom}\ge12$ in `12ea165a03`. Code
`bots/pi/code/round10_final_verify.py`; claims `pi_v_030`, `pi_note_004`.

## Current state (through round 8 — 2026-07-26)

### The skeleton (all PI-verified, exact)
1. **Symmetry & reality** [pi_v_005]: $A_6/i$ real, degree-8 homogeneous, invariant under all
   $S_3\times S_3$ leg permutations **and** the minus$\leftrightarrow$plus swap.
2. **Walls** [pi_v_004]: 18 interior momentum walls — $a_i-b_j=0$ (9) and $a_i+b_j-T=0$ (9).
3. **Rational, no poles** [pi_v_006/008/018]: $A_6$ **finite everywhere** (every $h_S$ **removable**)
   yet a genuine **rational** function, even inside one true piece (all 53 signs fixed).
4. **Prefactor** [pi_v_012/014]: $A_6=i(\prod_k\omega_k)H$ with $H$ rational, degree-2 homogeneous,
   $S_3\times S_3$+swap symmetric, and **sign-dependent** (not even).

### ROUND-6 BREAKTHROUGH — the in-piece formula is found and factored [pi_v_021]
The key was a **cone** observation: $H$ and all 53 surfaces are homogeneous, so a single true piece
is scale-invariant. **Dehomogenize by $\omega_2$** ($x=\omega_3/\omega_2$, etc.): $h=H/\omega_2^2$
becomes a rational function of **3 variables**, collapsing the fit that stalled in round 5. A modular
null-space search + 5-prime CRT reconstruction, **exact-`Fraction`-validated 1000/1000 in two
independent true pieces** vs fresh `bg_r6`, gives $H=P/Q$ with a **degree-10 denominator that
FACTORS**:

- **Piece A**: $Q_A\propto x\,(x+y)(x+z)(y+1)(z+1)\,Q_aQ_b$
- **Piece B**: $Q_B\propto y\,z\,(x+y)(x+z)(y+1)(z+1)\,Q_aQ_b$

with the **same** quadratics $Q_a=x^2+xy+xz+x+yz+y+z+1$, $Q_b=xy+xz+x+y^2+yz+y+z^2+z$.

**Building blocks (homogenized; free legs $2,3$ minus, $4,5$ plus):**
| block | homogeneous | type |
|---|---|---|
| $x$ / $y,z$ | $\omega_3$ / $\omega_4,\omega_5$ | single legs (chamber-selected) |
| $x+y,x+z,y+1,z+1$ | $\omega_3+\omega_4,\ \omega_3+\omega_5,\ \omega_2+\omega_4,\ \omega_2+\omega_5$ | mixed pair sums (universal) |
| $Q_a$ | $e_2(\omega_{2..5})+\omega_2^2+\omega_3^2$ | irreducible quadratic (universal) |
| $Q_b$ | $e_2(\omega_{2..5})+\omega_4^2+\omega_5^2$ | irreducible quadratic (universal) |

The **four mixed-pair factors and $Q_a,Q_b$ are identical in both pieces**; only the **single-leg
product is chamber-dependent** (A: $\{\omega_3\}$, B: $\{\omega_4,\omega_5\}$).

**Physical identity of the quadratics** (verified symbolically): for $S=\{2,3,4,5\}=\{1,6\}^c$,
$$Q_a+Q_b=\omega_S^2,\qquad 4Q_aQ_b=\omega_S^4-k_S^2=h_S(\omega_S^2+|k_S|).$$
So $Q_a,Q_b$ are the two sign-branches of the **complementary internal-line propagator $h_{\{1,6\}^c}$**;
the removable surface $h_S$ lives **inside $Q$**, and the numerator $P$ supplies the compensating zero —
pi_v_006 removability made explicit.

### This RESOLVES the round-5 puzzle
The genuine denominator factors are **SIGNED** (single legs, mixed pair sums, $Q_a,Q_b$). Every excluded
family — $\prod(a_i+b_j)$ [s1_015], $a_i+a_j$, $T$, $p$, $\omega_i\omega_j$ [pi_v_017/019] — was built
from **EVEN** blocks (functions of the squares). Wrong parity ⇒ **no product of them can ever clear $H$**.
The single-$Q$ picture was not dead; it was searched in the wrong ring. **s1_017** (simple even-$|K|$
channel sums fail) is independently **confirmed sound** [pi_v_022] and explained by the same root cause.

### ROUND-7 — the two-chamber formula is CONFIRMED but is NOT the full answer
- **[pi_v_023] CONFIRMED (independent).** With PI-transcribed blocks and a fresh `bg_r7`,
  $H_A=-32\,rs\,\Omega\,F(m_1,p_1,m_2,p_2)/(uv\,L\,B_MB_P)$ and its minus$\leftrightarrow$plus swap $H_B$
  reproduce BG **exactly** ($40/40$ in-piece points each, `Fraction`). $F$ is a genuine 31-term
  weighted-degree-9 core; $L$, $B_M(=Q_a)$, $B_P(=Q_b)$ are universal. **This compact partial result is
  banked.**
- **[pi_v_024] It does NOT extend.** Both $H_A,H_B$ **fail** at all three other realized bases from job
  `r6_piece_20260726T173931Z` (12ea165a03, 7608cb858a, a2fa6ab8af) — independently confirming the job's
  `no_fixed_den_fit`. Crucially **12ea165a03 has the SAME comparison matrix as A** ([[1,1],[1,1]]) yet
  fails; it differs from A in the sign of $h_{2345}=h_{\{1,6\}^c}$ (A: $-84$, so $B_MB_P<0$; here $+80$,
  $B_MB_P>0$). So formula-chambers are indexed by **more than** the free-leg comparison matrix.
- **[pi_v_025] The other chambers are HIGHER-DEGREE.** In 12ea165a03, $H$ has **no** dehomogenized
  rational rep of degree $\le 12$ (modular rank scan, 1050 in-piece pts, nulldim$=0$ for $d=3..12$), so
  $\deg Q_{\rm hom}>10$ — strictly above pieces A ($=10$) and B ($=10$). **The full answer is not "one
  core $F$ + a single-leg reselection."**

### ROUND-8 — two-chamber result compressed to FOUR blocks; pure box-spline master killed
- **[pi_v_026] CONFIRMED (independent).** The banked A-piece core equals an exact **four-block**
  partial fraction, with $C(u;r,s)=r^3(u+s)+s^3(u+r)$:
  $$H_A=\frac{64rs(r^2+s^2)}{B_P}-\frac{32r^2s^2(r^2+s^2)\Omega}{u(u+r)(u+s)B_M}-\frac{32rs\,\Omega\,C}{uL}-\frac{64rs(r^2+s^2)(u+r+s)}{v(u+r)(u+s)},$$
  and $H_B(u,v,r,s)=H_A(r,s,u,v)$. The PI verified it **two ways vs its own core** (not the student's
  $P/Q$): `sympy.cancel(fourblock − core)=0` for A and B, **and** exact-`Fraction` match to a fresh
  `bg_r8` at $40/40$ in-piece points per piece. So A/B are **four rational channel blocks**, each with a
  single simple denominator ($B_P$; $u(u+r)(u+s)B_M$; $uL$; $v(u+r)(u+s)$) — a signed-channel **seed**.
- **[pi_v_027] CONFIRMED — pure positive-part master is impossible.** From the four-block form directly:
  reduced $H_A$ has $\gcd(P,Q)=1$, homogeneous $\deg N=12$, $\deg Q_{\rm hom}=10$ factoring as
  $u\,v\,(r{+}u)(r{+}v)(s{+}u)(s{+}v)\,B_MB_P$ (matches round 6); dehomogenized $\deg P_A=12,\deg Q_A=9$.
  Because $B_M,B_P$ are irreducible nonconstant quadratics in $Q$ but not $N$, $H_A$ is **genuinely
  rational**, so a finite **pure** polynomial$\times$positive-part/truncated-power master (polynomial on
  each sign chamber) would force $Q_A\mid P_A$ — impossible. **The master MUST use rational signed
  channels.**
- **Crux NOT reached.** The higher-degree chamber 12ea165a03 was **not** reconstructed — the technician
  sub-agent exhausted context on a 1400-pt deg-13/14 batch and produced no artifact. Master-object
  hypothesis remains **untested** for lack of a second, higher-degree factored $H$.

### ROUND-9 (FINAL) — re-bank on a fresh build + extend the obstruction
- **[pi_v_028] Re-banked on fresh `bg_r9`** (source md5 `41715c4a...`, byte-identical to root; canonical
  check reproduces $A_6=i(-29948208/17)$). The four-block $H_A$ and swap $H_B$ match the PI's own 31-term
  core symbolically (`sympy.cancel = 0` for A,B) **and** reproduce `bg_r9` **exactly** (`Fraction`) on
  $40/40$ in-piece points per chamber. The compact two-chamber formula stands against a fresh
  immutable-source binary.
- **[pi_v_029] Boundary re-confirmed + obstruction extended.** Both $H_A,H_B$ **fail** at 12ea165a03
  (base + $0/30$ in-piece perturbations). An **independent** equal-bound cone rank scan on 1260 exact
  in-piece points (my own 1050 round-7 points + 210 fresh `bg_r9` points) is **full column rank** over
  two primes at **both $d=12$ and $d=13$**, so $d_{\rm eq}\ge14 \Rightarrow \deg Q_{\rm hom}\ge12$ —
  reconfirms pi_v_025 ($>10$) and pushes one rung further. The student's $d=14$ result
  ($\deg Q_{\rm hom}\ge13$) is accepted as reported.

### The remaining obstruction (why not solved)
1. **A higher-degree chamber was never reconstructed.** 12ea165a03 has $\deg Q_{\rm hom}\ge13$ (vs $10$
   for the solved chambers). The first candidate reconstruction is a **4-variable degree-15 cone fit** —
   a larger scan than any run this project; the technician sub-agent exhausted context on the deg-13/14
   batch (round 7) and the round-8 push established only the negative degree bound.
2. **The MASTER object is untested.** The only structurally viable full-domain candidate is a single
   compact **rational signed-channel sum** (a pure box-spline / positive-part master is excluded
   [pi_v_027]) whose truncations give the four-block $H_A$ in the all-$+$ chamber **and** the
   higher-degree pieces. Without a factored higher chamber, its new signed denominator factors are
   unknown, so the hypothesis cannot be tested.
3. **Chamber map (partial).** Confirmed switches: the free-leg comparison matrix **and**
   $\mathrm{sign}\,h_{\{1,6\}^c}$ ($=B_MB_P$); the full indexing is not enumerated.

### Dead ends (do not revisit)
- Piecewise-polynomial numerator [pi_v_008/018]; symmetric-invariant $(s,p,r,t)$ fit [pi_v_011];
  $H$ even [pi_v_014]; $H=P/Q$ over **even** blocks [pi_v_017/019] — explained by parity [pi_v_021];
  simple even-$|K|$ single-$1/h_S$ channel sums [s1_017, conf pi_v_022].
- **The round-6 two-chamber form as the FULL answer via single-leg reselection [pi_v_024/025].**
- **PURE polynomial$\times$positive-part/truncated-power master (no rational denominators) [s1_021, conf
  pi_v_027]** — polynomial per sign chamber, but $H_A$ is genuinely rational; the master must be
  rational signed-channel.
- Literature [s1_016]: no published exact $A_6^{(---+++)}$ (arXiv:2606.28280 defers it).

### Verification banked (rounds 8–9)
- **pi_v_026** (r8): two-chamber core = exact **four-block** partial fraction; PI-confirmed two ways
  (`cancel(fourblock − PI-core)=0` for A,B; exact `Fraction` match vs fresh `bg_r8`, 40/40 per piece).
- **pi_v_027** (r8): reduced $H_A$ genuinely rational ($\gcd=1$, $\deg Q_{\rm hom}=10$, factors as
  $uv(r{+}u)(r{+}v)(s{+}u)(s{+}v)B_MB_P$) ⇒ **pure box-spline master impossible** (s1_021 confirmed).
- **pi_v_028** (r9): the four-block two-chamber formula re-banked on a **fresh `bg_r9`** (symbolic
  `cancel=0` + exact `Fraction` match 40/40 per chamber).
- **pi_v_029** (r9): two-chamber formula **fails** at 12ea165a03 ($0/30$ in-piece); independent
  equal-bound rank scan full rank at $d=12,13$ over two primes ⇒ $\deg Q_{\rm hom}\ge12$ there.
- **pi_note_003** (r9): full acceptance bar NOT met; `FINAL_SUMMARY.md` written, `SOLVED.md` not.

### Assignment (round 10 — FINAL)
- **None.** This is the final PI summary round; no new task assigned. `tasks/student-1.md` is left as the
  round-8 brief (historical). Deliverable this round: independent re-verification on a fresh `bg_r10`
  [pi_v_030] and the finalized `summary/FINAL_SUMMARY.md`. No pending blocking jobs (`jobs/` clear).

### Process note
Across 9 rounds the group established the full structural skeleton of $A_6$ (prefactor, genuine
rationality, removable propagator surfaces, signed denominator blocks) and produced a **compact, exact,
independently verified closed form for the two opposite chambers** — four signed rational channel blocks,
equivalently one 31-term core. The **full-domain** formula was not reached: the other realized chambers
are strictly higher-degree and none was reconstructed/factored, so the rational signed-channel master
(the only viable full-domain candidate) is untested. The gating failure was **tractability** (a 4-variable
degree-$\ge15$ cone reconstruction), compounded by an operational technician context blow-out in rounds
7–8 — not a wrong method. `FINAL_SUMMARY.md` banks the verified partial result and states this obstruction
honestly; per the definition of done, the partial result is **not** labeled solved.
