# Group meeting notes — waterwaves_threem

## Round 8 — 2026-06-27T06:51:27Z (PI)

### Round-7 student results INDEPENDENTLY RE-VERIFIED (own oracle + own evaluator, no student code)
Round 7 produced no new closed form but three load-bearing facts about the $n\ge7$ regime.
I rebuilt my oracle fresh (byte-identical to shared `bg.cpp`), wrote my own batched exact
evaluator (`bots/pi/code/pi_batch.cpp`, cross-checked vs `./bg`), and re-derived each claim with
my own slice/interpolation/exponent code (`pi_r8_verify.py`, `pi_r8_fix.py`, `pi_r8_fix2.py`):

1. **PARITY CORRECTION (s1_020) — CONFIRMED.** $A_n$ is ALWAYS even under $\omega\to-\omega$ (even
   homogeneity, degree $2n-4$); hence $N_n=A_n D_n^{\min}$ has parity $(-1)^{\deg D_n^{\min}}$. At
   $n=6$ the minimal denominator $e_3^-+e_3^+$ has degree 3 (ODD) $\Rightarrow N_6$ ODD; at $n=7$ it
   is the full 12-factor product (degree $3(n-3)=12$, EVEN) $\Rightarrow N_7$ EVEN. **So "$N_n$ odd"
   was an $n=6$-only artifact; in general $N_n$ is even iff $n$ is odd.** (Direct exact check:
   $A_6(-\omega)=A_6(\omega)$, $A_7(-\omega)=A_7(\omega)$; $N_6(-\omega)=-N_6(\omega)$,
   $N_7(-\omega)=+N_7(\omega)$.)

2. **SOFT RECURSION (s2_021) — CONFIRMED EXACT at $n=7$, BOTH legs.** $A_n^{3-}\to 2(n-3)\,\omega_p^2
   A_{n-1}$ as $\omega_p\to0$. Via an F-const slice taking $\varepsilon\to0$ IN THE SOFT CHAMBER (the
   subtlety: a wide $\varepsilon$ window sits in a different chamber than $\varepsilon\to0^+$ — sample
   tiny $\varepsilon$): a soft PLUS leg gives $\lim A_7/(i\varepsilon^2)=8\,A_6^{3-}=-3517680816/161$,
   a soft MINUS leg gives $8\,A_6^{2-}=-13249051200$ (each compared to my OWN independent direct
   $8A_6$); $N_7$ vanishes to exactly $O(\varepsilon^2)$.

3. **n=7 SINGLE-WALL JUMP EXPONENTS (s1_021) — CONFIRMED.** On clean single-wall windows (with a
   pre-scan to keep only the target wall in-window; this is essential — at $n=7$ a second wall sits
   only $\sim0.045$ away from the $(1{=}2)$ crossing and contaminated my first attempt) and the n=6
   controls passing ($(1{=}1)\to1$, $(1{=}2)\to3$): at $n=7$ **$(1{=}1)\to1$, $(1{=}2)\to2$**
   (I directly re-measured both; $(1{=}3)\to4$ from student-1, method now validated at 4 wall types).
   The split/lowered exponents are real; their cross-term interpretation (s1_022) stays TENTATIVE.

### What is SOLVED vs OPEN (unchanged headline; n=7 structure now PI-pinned)
- **Solved & PI-verified:** $n=5$ and the **FULL $n=6$ closed form**; no factorization poles; the
  all-$n$ minimal denominator $\prod(\omega_i+\omega_j)$ (pole order 1, collapse to $(e_3^-+e_3^+)^1$
  only at $n=6$); degree law $\deg N_n=5n-13$; symmetry ($S_3\wr Z_2$ at $n=6$, $S_3\times S_{n-3}$
  for $n\ge7$); $n$-DEPENDENT parity; n=7 wall map ($42=12+18+12$) + exponents; the explicit $(1{=}2)$
  coefficient $Q$; soft recursion (both legs) + single-pair residues + matching/Cauchy.
- **OPEN (the whole remaining task):** the EXPLICIT numerator $N_n$ for $n\ge7$ — hence the single
  all-$n$ closed form. **Not SOLVED — no `SOLVED.md`** (the task asks for all $n\ge5$).

### Tasks this round (the assembly endgame: explicit $N_7$ / all-$n$ $N_n$)
- **student-1 (bottom-up, ASSEMBLE $N_7$):** with the wall map, exponents and EVEN parity now fixed,
  (i) extract the CLEAN chamber-independent subset-sum coefficients (the $(1{=}2)$/$(1{=}3)$
  truncated-power coefficients — the $n=7$ analog of the $n=6$ $Q$); (ii) PIN the cross-term closing
  order (disjoint $(1{=}1)$ pairs? $(1{=}1)\times$subset-sum? triples? — close the tentative s1_022);
  (iii) FIT all coefficients EXACTLY (scaled-up `r6_fit`/`r6_extract`, $S_3\times S_4$ orbit-sum,
  parity-EVEN templates — hundreds-1000 exact coeffs; Typhon SLURM if needed); (iv) assemble $N_7$
  over $D_7=\prod(\omega_i+\omega_j)$ and VERIFY EXACTLY across $\ge4$ chambers + two-sided wall
  limits. Spot-check $n=8$.
- **student-2 (top-down, all-$n$):** SOLVE (not just check) the soft recursion — now PI-verified both
  legs — which fixes $N_n$ on every $\{\omega_p=0\}$ in terms of $N_{n-1}$ (boundary the two-minus
  law), combined with the recursive single-pair residue structure (s2_022), the matching/Cauchy
  picture, the $n$-dependent parity / $S_3\times S_{n-3}$ symmetry / degree law, and the PI-verified
  $n=6$ box spline + $Q$. Produce an explicit all-$n$ $N_n$ candidate, recover $n=5,6$, and TEST
  EXACTLY at $n=7$ (against student-1's emerging $N_7$) + $n=8$ spot-check. A precisely-characterized
  near-miss is valuable.

### Next steps
The two tasks dovetail: student-1 yields explicit $N_7$ data; student-2 yields an all-$n$ ansatz;
cross-validate. As soon as either gives an $N_{n\ge7}$ (hence $A_n$) candidate that passes my
independent exact re-verification ($\ge4$ chambers + two-sided wall limits at $n=6,7$, $n=8$
spot-check), the all-$n$ form is essentially complete and I write `SOLVED.md`. If $N_{n\ge7}$ refuses
to close, the deliverable is the verified description (explicit $n=5,6$ + the all-$n$
denominator/degree/symmetry/parity/wall-exponent law + whatever part of $N_{n\ge7}$ is pinned).

## Round 7 — 2026-06-27T04:33:11Z (PI)

### MILESTONE: the FULL n=6 closed form is PI-VERIFIED EXACT (independent evaluator)
Student-1 (post_016, s1_018) assembled the complete $n=6$ three-minus numerator and verified it.
I rebuilt my oracle fresh (byte-identical to shared `bg.cpp`) and re-verified the headline claim
**with my own evaluator** — my own group/orbit-sum/assembly logic in
`bots/pi/code/pi_r7_independent.py` + `pi_r7_walls.py`, taking ONLY the published reference
polynomials (`r6_polys.txt` + $Q$) as the candidate under test, importing no student code:

$$\boxed{\,A_6=i\,2^5g^{-3}\,\frac{N_6}{e_3^-+e_3^+}\,,\quad
N_6=B+\!\!\sum_{i\in M,j\in P}\!\!(b_j-a_i)_+P_{ij}
+\!\!\sum_{i\ne k,\,j\ne l}\!\!(b_j-a_i)_+(b_l-a_k)_+R_{ij,kl}
+\!\!\sum_{i,\{j,k\}}\!\!(a_i-b_j-b_k)_+^3Q_{ijk}\,}$$

$a_i=\omega_i^2$ (minus), $b_j=\omega_j^2$ (plus), $(x)_+=\max(x,0)$; $\deg N_6=11$, $S_3\wr Z_2$-symmetric,
$\omega\to-\omega$-ODD, CONTINUOUS box spline. Explicit $B,P^0,R^0,Q$ in `r6_polys.txt`.

**PI independent verification (all EXACT):**
- **140/140** generic on-shell points spanning **58 distinct chamber labels** — formula $=$ my `./bg`.
- **6/6** non-generic regimes (one frequency $\gg$ or $\ll$ the rest, e.g. $w=1000,2,3,5$ and $1/1000,2,3,5$).
- **3/3** $g$-homogeneity checks ($g=2,\tfrac13,\tfrac72$): the $g^{-3}$ scaling holds exactly.
- **Two-sided WALL LIMITS** onto a $(1{=}1)$ wall, a $(1{=}2)$ wall, AND a matching corner — formula
  $=$ `./bg` exactly on BOTH sides down to $\varepsilon=10^{-4}$ (finite, continuous: kinks, not poles;
  the oracle SIGFPEs *on* the wall, the closed form is exact there as a limit).
- Structural self-consistency: $N_6$ ODD (10/10), $A_6$ homogeneous degree 8 (10/10).

The $(1{=}1)$ cross-term is a matching-PAIR product (exp $(1,1)$, **no triple** needed); the $(1{=}2)$
sector is the clean cubic-kink coefficient $Q$ (s1_015). **So $n=6$ is CLOSED.**

### PI-corroborated: the all-n minimal denominator (s2_018)
Student-2 (post_017) pinned the all-$n$ minimal denominator: $D_n^{\min}=\prod_{i\in M,j\in P}(\omega_i+\omega_j)$,
degree $3(n-3)$, **pole order 1**, with the $n=6$ cube-collapse to $(e_3^-+e_3^+)^1$ the **unique**
exception. PI symbolic check: $r_n:=Q_n\bmod p_-$ has degree 0 only at $n=6$ ($r_6=e_3^-+e_3^+$ exactly,
$=1162/3$ at a test point) and degree 1 at $n=7$ ($\Rightarrow$ no collapse; full 12-pair product is
minimal, $\deg N_7=22$). Mechanism + degree law $\deg N_n=5n-13$ confirmed.

### What is SOLVED vs OPEN
- **Solved & PI-verified:** the $n=5$ closed form; the **FULL $n=6$ closed form** (explicit box-spline
  numerator + minimal denominator); no factorization poles; the all-$n$ minimal denominator
  $\prod(\omega_i+\omega_j)$ (pole order 1); degree law $5n-13$; symmetry, parity, jump exponents; the
  explicit $(1{=}2)$ coefficient $Q$; the soft recursion + single-pair residues + matching/Cauchy handles.
- **OPEN (the whole remaining task):** the EXPLICIT numerator $N_n$ for $n\ge7$ — hence the single
  all-$n$ closed form. The $n\ge7$ regime is genuinely new: the $Z_2$ swap is NOT a symmetry (only
  $S_3\times S_{n-3}$); matchings become injections; $(1{=}1)$ edges couple to subset-sum walls. **Not
  SOLVED — no `SOLVED.md`** (a clean all-$n$ form is not yet reached; the task asks for all $n\ge5$).

### Tasks this round (both attack the n>=7 numerator)
- **student-1 (bottom-up, assemble $N_7$):** map the full $n=7$ subset-sum wall arrangement under
  $S_3\times S_4$ (no $Z_2$), measure all single-wall exponents (confirm $(1{=}1)\to1$, subset-sum$\to4$),
  determine the cross-term products (pairs/triples/mixed; closing order), fit all coefficients EXACTLY
  (deg 22), assemble $N_7$ over $D_7=\prod(\omega_i+\omega_j)$, verify EXACTLY across chambers + wall
  limits; hand the wall/exponent/cross-term table to student-2 and spot-check $n=8$.
- **student-2 (top-down, all-$n$):** propose an explicit all-$n$ $N_n$ from the soft recursion +
  single-pair residues + matching/Cauchy, recovering $n=5,6$ and the verified $Q$, with the $n\ge7$
  injection structure; check boundaries/recursion exactly; test at $n=7$ (+ $n=8$ spot-check). If a
  single form resists, deliver the most complete validated all-$n$ description.

### Next steps
As soon as either yields an $N_n$ (hence $A_n$) candidate for $n\ge7$ that passes my independent exact
re-verification (own oracle + own evaluator) across $\ge4$ chamber types and two-sided wall limits at
$n=6,7$ (and a spot-check at $n=8$), the all-$n$ form is essentially complete and I write `SOLVED.md`
with the per-$n$ explicit forms + the all-$n$ structure. If $N_n$ for $n\ge7$ refuses to close, the
deliverable becomes the verified description: explicit closed forms at $n=5,6$ + the all-$n$
denominator/degree/symmetry/parity/wall-exponent law + whatever part of $N_{n\ge7}$ is pinned.

## Round 6 — 2026-06-27T03:13:00Z (PI)

### Round-5 results INDEPENDENTLY RE-VERIFIED — the spline is a BOX SPLINE, and the (1=2) coefficient is now explicit
Both students converged this round (post_013 student-2 top-down; post_014 student-1 bottom-up)
on a **correction to the round-5 task premise**: $N_6$ is NOT a simple single-wall
truncated-power sum — it is a **genuine box spline with $(1{=}1)$ cross-terms**. I rebuilt my
oracle, added a guarded fast EXACT batch variant (`bots/pi/code/bgb.cpp --batch`, cross-checked
**22/22 exactly vs ./bg**), and re-verified the load-bearing claims with my own exact code
(`pi_r6_verify.py`, `pi_r6_Qcheck.py`; no student code):

$$\boxed{\,A_6=i\,2^{5}g^{-3}\,\frac{N_6(\omega)}{e_3^-+e_3^+}\,,\quad N_6=B+\sum_{(1=2)}(k_{ijk})_+^{3}Q_{ijk}+\big(\text{$(1{=}1)$ matching cross-term box spline}\big),\ \deg N_6=11\ \text{ODD}.}$$

- **(s1_015) the EXPLICIT $(1{=}2)$ jump coefficient $Q$ — PI-VERIFIED EXACT, multiple gauges.**
  For minus $i$, plus pair $\{j,k\}$, excluded plus $l$, other minus $\{p,q\}$
  ($A_1=\omega_p+\omega_q,A_2=\omega_p\omega_q,B_1=\omega_j+\omega_k,B_2=\omega_j\omega_k,y=\omega_l$):
  $$Q=A_2B_1(y^2-A_1^2-A_1B_1+A_2-B_2)+B_2\,y\,(A_2-B_1y-B_2).$$
  The $(1{=}2)$ jump of $N_6$ is exactly $N_+-N_-=(k_{ijk})^3Q$, $k_{ijk}=\omega_i^2-\omega_j^2-\omega_k^2$.
  PI CHECK: on clean single-$(1{=}2)$ crossings $\Delta(t)/[k_{ijk}(t)^3Q(t)]=32$ (the $i2^5g^{-3}$
  convention) EXACTLY at **several walls with different gauge legs** (minus $i=1$ AND $i=3$,
  different plus pairs). The $(1{=}2)$ sector is chamber-INDEPENDENT (clean). **This is the
  fixed part of the spline — a concrete deliverable.**
- **(s1_014) the simple single-wall sum FAILS — PI-CORROBORATED.** Student-1's complete-basis
  modular fit (137 cols, full rank but INCONSISTENT) with a passing synthetic control proves the
  $(1{=}1)$ jump coefficient is chamber-dependent (cross-terms). My own checks: (i) `pi_r6_verify.py`
  PART C — away from matchings, the mixed second difference across two NON-forced $(1{=}1)$ walls
  ($\{2,4\},\{2,5\}$) scales as $\epsilon^2$, matching a synthetic simple-sum control, so the
  cross-terms are **matching-localized** (consistent with s1_016); (ii) a purely local clean
  refutation is **geometrically obstructed** — the $(1{=}1)$ kink lives on the difference branch
  $\omega_i=\omega_j$ (crossed once per line) while the sum branch is the matching/pole (always a
  multi-wall crossing) — so the decisive test is the global fit (done) plus my round-5
  invariant-polynomial-per-region negative and student-2's chamber-dependent residue (s2_016).
  Verdict: **established (confidence high).**
- **(s2_015) box-spline-of-$\omega^2$ RULED OUT — PI-VERIFIED by consequence.** My PART A re-confirms
  $N_6$ is ODD ($N_6(-w)=-N_6(w)$) and $A_6$ has a genuine SIMPLE pole (pole order 1: $A_6/i$ not
  polynomial on a slice, $A_6/i\cdot(e_3^-+e_3^+)$ IS). An even box spline of $\omega_i^2$ cannot be
  an odd $N_6$, and a piecewise-polynomial cannot have $A_6$'s pole. So the closed form is a
  truncated-power spline in LEG variables — exactly the assembly target.
- **(s1_016 / s2_016) cross-terms / residue are MATCHING-structured** — consistent with everything:
  the difference-branch matchings ($\omega_2^2=\omega_4^2$ & $\omega_3^2=\omega_5^2\Rightarrow
  \omega_1^2=\omega_6^2$) are the $(1{=}1)$ mirror of the sum-branch pole locus $e_3^-+e_3^+=0$.

### What is SOLVED vs OPEN
- **Solved & PI-verified:** $n=5$ closed form; no factorization poles; the rational structure with
  MINIMAL denominator $(e_3^-+e_3^+)$ (pole order 1, $\deg N_6=11$); $A_6$ even / $N_6$ odd /
  $S_3\wr Z_2$; the jump exponents (1 and 3); the **explicit $(1{=}2)$ coefficient $Q$**; the
  box-spline-of-squares ruling-out; the soft recursion and matching-pole structure.
- **OPEN (the whole remaining problem):** the $(1{=}1)$ box-spline CROSS-TERM part of $N_6$
  (matching-indexed truncated-power products), hence $N_n$ for all $n\ge6$; and the $n\ne6$ minimal
  denominator. **Not SOLVED — no `SOLVED.md`.**

### Tasks this round (both on the (1=1) cross-terms, with Q now fixed)
- **student-1 (bottom-up, assemble the $(1{=}1)$ box spline):** with the PI-verified $Q$ fixed, work
  on $M=N_6-\sum_{(1=2)}(k_{ijk})_+^3 Q_{ijk}$. Determine its $(1{=}1)$ cross-term structure as
  MATCHING-INDEXED truncated-power products $\prod_i(k_{i\sigma(i)})_+\times(\text{poly})$ over the 6
  matchings (s1_016), plus a symmetric base $B$. Assemble $N_6$, symmetrize, verify EXACTLY across
  chambers + two-sided wall limits.
- **student-2 (top-down, all-$n$ + denominator):** turn the matching/Cauchy partial-fraction +
  soft-recursion picture into the explicit $(1{=}1)$ cross-term / all-$n$ $N_n$ (recovering $n=5$ and
  the verified $Q$), test EXACTLY at $n=6,7$; AND pin the $n=7$ MINIMAL denominator (higher-degree
  reconstruction or multivariate fit) since the cube-collapse is special to $n=6$.

### Next steps
As soon as either yields an $N_n$ (hence $A_n$) candidate that passes my independent exact
re-verification (own oracle + batch evaluator) across $\ge4$ chamber types and two-sided wall limits
at $n=5,6,7$, I write `SOLVED.md`. If $N_6$ refuses to collapse, the deliverable becomes the verified
description: minimal denominator $(e_3^-+e_3^+)$ + explicit $(1{=}2)$ coefficient $Q$ + the per-chamber
$N_6$ table / matching cross-term structure — already a substantial validated description.

## Round 5 — 2026-06-27T00:39:17Z (PI)

### Round-4 results INDEPENDENTLY RE-VERIFIED — the minimal denominator holds
Both students worked round 4 (student-1 bottom-up, student-2 top-down). The
headline round-4 result is student-1's **simplification of the denominator**
(post_011, claims s1_011/012/013), which I rebuilt the oracle and re-checked
end-to-end with my own exact-rational code (`bots/pi/code/pi_r5_min_denom.py`,
`pi_r5_kinks.py`; no student code):

$$\boxed{\,A_6=i\,2^{5}g^{-3}\,\frac{N(\omega)}{\omega_1\omega_2\omega_3+\omega_4\omega_5\omega_6}\,,\qquad N=\text{degree-11 }S_3\wr Z_2\text{-symmetric, }\omega\to-\omega\text{-odd SPLINE}.}$$

- **(s1_011) $D_9=(e_3^-+e_3^+)^3$ on the manifold** — PI CHECK 1: symbolic ($Q(x)-p_-(x)$
  is $x$-independent on the manifold and equals $e_3^-+e_3^+$, since $e_1^-=-e_1^+$,
  $e_2^-=e_2^+$ make $Q$ and $p_-$ share all but the constant coefficient) **and** numeric
  exact 5/5. So the nine mixed-pair sums collapse to a single cubic cubed.
- **(s1_012) MINIMAL denominator $=(e_3^-+e_3^+)^1$, $\deg N=11$** — PI CHECK 2: on an
  F-const slice $A_6$ is NOT polynomial, $A_6\cdot(e_3^-+e_3^+)$ IS (deg 6 on slice), and
  $A_6\cdot(e_3^-+e_3^+)^3$ over-clears (deg 14) ⇒ **pole order exactly 1**. Homogeneity
  $A_6(2w)/A_6(w)=256$ ⇒ $\deg A_6=8$ ⇒ $\deg N=11$ (not 17). My round-4 "$D_9$ minimal"
  was right only in the FREE 6-variable ring; on the manifold those nine factors are
  dependent. The pole sits on the SINGLE hypersurface $\{e_3^-+e_3^+=0\}$ = the
  perfect-matching locus — this unifies student-2's "entangled / simple matching poles".
- **(s1_013) jump exponents 1 and 3** — PI CHECK 4 (clean single-wall crossings, tracking
  ALL deduped mixed walls incl. solved legs 1,6): across (1=1) $\omega_i=\omega_j$ the jump
  $N_L-N_R$ carries $(2t-1)^1$ ⇒ $A_6$ $C^0$; across (1=2) $\omega_i^2=\omega_j^2+\omega_k^2$
  it carries $(5t-1)^3$ ⇒ $A_6$ $C^2$. I independently hit the multi-wall contamination
  hazard (s1_dec_008/s2_014) and confirmed single-wall discipline is essential.

### NEW PI result (negative, important for the search): N is NOT an invariant polynomial per region
I tested the most tempting next move — fit the global symmetric $N$ as a weighted-degree-11
polynomial in the 4 invariants $(e_1,e_2,e_3^-,e_3^+)$ within a single symmetric region
(`bots/pi/code/pi_r5_invariant_region.py`, modular + held-out). It **FAILS** in every
region — grouped by the 12 canonical chamber-types (I reproduced student-1's count of 12)
**and** by $(\mathrm{sign}\,W_1,\mathrm{sign}\,W_2)$. REASON: a per-chamber piece is
**non-symmetric** in the legs, so as a function of the symmetric invariants it is
**algebraic** (cubic-root), not polynomial — exactly student-1's dec_007 intuition, now
proven. **Consequence for round 5:** do NOT chase a per-region invariant polynomial. Build
$N$ in **leg variables** as a truncated-power spline, or recognize an explicit symmetric
ansatz (box-spline of $x_i=\omega_i^2$ / matching-sum). NB: the split jump exponents (1,3)
do **not** kill the box-spline lead — variable wall-smoothness is generic for $d>1$ box
splines.

### What is SOLVED vs OPEN
- **Solved & PI-verified:** $n=5$ closed form; no factorization poles (n=5,6,7); the
  rational structure with the **minimal** denominator ($(e_3^-+e_3^+)$ at $n=6$;
  $\mathrm{Res}(p_-,Q_n)$ all-$n$); $\deg N=11$, $S_3\wr Z_2$ symmetry, $\omega\to-\omega$
  oddness; the two jump exponents (1 and 3); the soft theorem and the matching-pole
  structure.
- **OPEN (the whole remaining problem):** the explicit closed form for the degree-11
  spline numerator $N_6$ and its all-$n$ generalization. Not SOLVED — no `SOLVED.md`.

### Tasks this round (both on N_n, in LEG variables / explicit ansatz)
- **student-1 (bottom-up, assemble the spline IN LEGS):** get the explicit reference-chamber
  $N_{\rm ref}$ (deg-11 in legs), determine the jump-coefficient polynomials $P_{ij}$ (for
  the (1=1) $(k_{ij})^1$ jumps) and $Q_{ijk}$ (for the (1=2) $(k_{ijk})^3$ jumps) and the
  symmetric base $B$, assemble $N=B+\sum (k_{ij})_+ P_{ij}+\sum (k_{ijk})_+^3 Q_{ijk}$,
  symmetrize, and verify EXACTLY at n=6 across chambers + two-sided wall limits; push to all $n$.
- **student-2 (top-down, all-n / recognition):** turn the soft recursion + matching/partial-
  fraction structure + the $d=3$ box-spline-of-$x_i=\omega_i^2$ picture into a conjectured
  all-$n$ closed form for $N_n$ (recovering $n=5$), and test it EXACTLY at $n=6$ (chambers +
  wall limits) and $n=7$. Coordinate with student-1's jump coefficients.

### Next steps
As soon as either yields an $N_n$ (hence $A_n$) candidate that passes my independent exact
re-verification across chambers and two-sided wall limits at $n=5,6,7$, I write `SOLVED.md`
with the full closed form, domain, and residuals. If $N_6$ refuses to collapse to a single
closed form, the deliverable becomes the verified per-chamber $N_6$ table + the minimal
denominator + the jump structure — already a complete validated description of the rational
structure.

## Round 4 — 2026-06-26T22:50:45Z (PI)

### The round-1/2 GATE IS OVERTURNED — and I have independently re-verified the correction
Round 3 ran without a PI (the PI process failed), so both students worked the open
frontier autonomously and **independently converged** on the same result. This round I
rebuilt the oracle from my own `bg.cpp` and re-verified it end-to-end with my own
exact-rational analysis (no student code). The headline:

$$\boxed{\,A_n^{3-}=i\,2^{\,n-1}g^{\,3-n}\,\frac{N_n(\omega)}{\displaystyle\prod_{i\in\mathrm{minus}}\prod_{j\in\mathrm{plus}}(\omega_i+\omega_j)}\,}$$

- **The sector is piecewise-RATIONAL, NOT piecewise-polynomial.** My round-2 "gate"
  (and student-2's s2_002) concluded *polynomial* — **that was wrong.** "No
  factorization poles" is true but does **not** imply polynomial. My own slice tests
  (`bots/pi/code/pi_r4_denominator.py`): on a clean one-chamber F-constant slice,
  $A_6/i$ is **not** a polynomial up to degree 25, while $(A_6/i)\cdot D_9$ **is** an
  exact polynomial.
- **Denominator** $D_n=\prod_{i\in\mathrm m,j\in\mathrm p}(\omega_i+\omega_j)$ — the
  $3(n-3)$ mixed-pair frequency **SUMS** (not "sums of squares"; I confirmed
  $\prod(\omega_i^2+\omega_j^2)$ does **not** clear). It is **MINIMAL**: I checked
  combinatorially that the $S_3\!\times\!S_3$ orbit of one mixed pair is the full
  9-element set, so the only symmetric divisors are $1$ and $D_9$; since $A_n$ is not
  polynomial, the reduced symmetric denominator is exactly $D_9$.
- **Exact rational reconstruction** of $A_6/i$ on a slice gives a reduced denominator
  that **divides** $D_9$ (its roots are mixed-pair frequency-sum zeros).
- **n=5 control** returns "polynomial" directly (the method is sound); **n=7** spot
  check: $A_7/i$ rational, $(A_7/i)\cdot D_{12}$ polynomial.
- **The numerator $N_n$ is a continuous SPLINE**, so $A_n$ is rational *per chamber*,
  not one global rational function (`pi_r4_spline2.py`): crossing the mixed wall
  $\omega_2=\omega_4$ ($k_{\{2,4\}}=0$, where $D_9\ne0$), $N_6$ is a *different*
  polynomial on each side yet continuous at the wall ⇒ $A_6$ continuous = a **kink, not
  a pole**. (The plus–plus ordering $\omega_4=\omega_5$ is by contrast analytic — same
  polynomial both sides — so the kinks live on the MIXED $\{k_S=0\}$ walls.)

This **reconciles the round-2 split** (student-1's "rational", student-2's earlier
"box spline"): the box-spline/truncated-power object the team was hunting lives in the
polynomial **numerator $N_n$**, not in $A_n$ itself. Both pictures were right about
different objects. Strong cross-validation: two students, two pipelines, one
denominator — now PI-reconfirmed with a third, independent pipeline.

### What is now SOLVED vs OPEN
- **Solved & PI-verified:** $n=5$ closed form; no factorization poles (n=5,6,7);
  the rational structure with explicit, minimal denominator $D_n$; degree
  $5n-13$, $S_3\wr Z_2$ symmetry, $\omega\to-\omega$ parity of $N_n$.
- **OPEN (the whole remaining problem):** the explicit closed form for the spline
  numerator $N_n$ (deg 17 at $n=6$), and its all-$n$ generalization. Not SOLVED — no
  `SOLVED.md` yet.

### Tasks this round (both attack $N_n$, the only open piece)
- **student-1 (bottom-up, rigorous):** extract the EXACT per-chamber polynomial
  $N_6=(A_6/i)\,D_9$ on every realizable chamber, then read off the spline from the
  **cross-wall jumps** — the difference of adjacent-chamber polynomials across each
  $k_S=0$ wall should be a truncated power $\propto(k_S)^p$. Assemble $N_6=$ base
  $+\sum$ jumps and verify globally; push toward all $n$.
- **student-2 (top-down, all-n):** turn the soft theorem
  $A_n\to2(n-3)\omega_p^2A_{n-1}$ into an explicit **recursion on $N_n$** with boundary
  $N_5=A_5\cdot\prod_{6\,\rm mixed}(\omega_i+\omega_j)$; use symmetry+parity and test a
  **matching-sum / Cauchy-type** representation (suggested by the
  $\prod(\omega_i+\omega_j)$ denominator) and the $d=3$ box-spline/truncated-power form
  for $N_n$ — exactly at $n=6,7$ across chambers and wall limits.

### Next steps
As soon as either yields an $N_n$ (hence $A_n$) candidate that passes my independent
exact re-verification across chambers and two-sided wall limits at $n=5,6,7$, I write
`SOLVED.md` with the full closed form, domain, and residuals. If $N_n$ refuses to
collapse to a single closed form, the deliverable becomes the verified per-chamber
$N_6$ table + the explicit denominator + wall arrangement — already a complete
validated description of the rational structure.

## Round 2 — 2026-06-26T19:26:23Z (PI)

### Round 1 reviewed and INDEPENDENTLY RE-VERIFIED
Both students delivered. I rebuilt the oracle from my own `bg.cpp` copy
(`bots/pi/code/`) and reconfirmed every load-bearing claim with my own evaluator:

- **n=5 closed form** — exact, 24/24 (my `verify_n5.py`). Solved.
- **Two-minus B-spline law** — I re-derived it from the truncated-power formula and
  matched the oracle exactly ($n=6$ two-minus $=-247808/7\,i$). This is the
  foundation both higher sectors build on, so I pinned it down myself.
- **n=6 gate claims (student-2)** — all three confirmed exact with my own script
  `verify_n6_gate.py`:
  1. **NO factorization poles.** Driving the channel $S=\{2,3,4\}$ ($D_S\to0$ at
     $\omega_4=-19/5$) from both sides, $A_6/i\to-187375$ (finite) and
     $(A_6/i)\,D_S\to0$ linearly. The propagator poles are spurious/removable.
  2. **Homogeneous degree $2n-4=8$** ($t=2,3,5/2$ give $t^8$ exactly).
  3. **$S_3\wr Z_2$ symmetry** — all minus-perms, plus-perms, and the triple-swap
     leave $A_6=-29948208/17\,i$ exactly.
- **n=7** finite ($-93475650304/1463\,i$), one-minus $\equiv0$. The structure
  (polynomial, symmetric) extends past $n=6$.

**Bottom line on the gate:** three-minus is **piecewise-POLYNOMIAL**, not rational
— same character as two-minus, contrary to question.md's pole conjecture. This
reorients everything: we are looking for a *spline*, not a channel-decomposed
rational.

### What $A_6$ must be, and what it is NOT (PI structural probes)
The core $C := A_6/(i\,2^5 g^{-3})$ is a **degree-8, $S_3\wr Z_2$-symmetric, cubic
piecewise polynomial** on the arrangement $\{k_S=0\}$ of mixed momentum-subset
walls. Degree counting is the sharpest tool:
- $C$ = (degree-2 prefactor) $\times$ (degree-6 cubic block). So **any object
  bilinear in the two triples' quadratic B-spline blocks is degree 10 — impossible.**
  This kills the whole "inner product / convolution of the two densities" family.

I ran two explicit probes (`bots/pi/code/probe_n6_struct.py`, `probe_n6_cubic.py`)
and **RULED OUT** (students: do not repeat these):
- the inner product $\int_0^Q P_-(t)P_+(t)\,dt$ — non-constant ratio to $A_6$;
- the single-min-threshold cubic block $e_2(\text{plus})\,P_-^{(3)}(\min\text{plus}^2)$,
  its swap, and their sum — non-constant ratio.

**Key structural fact to exploit:** both triples' B-spline densities live on the
**same support** $[0,Q]$, $Q=\sum_{\rm minus}\omega^2=\sum_{\rm plus}\omega^2$ (this
is exactly the resonance $\sum_i\sigma_i\omega_i^2=0$). The closed form is most
likely a genuine **multivariate / box spline** of the six knots $\omega_i^2$, or a
**double-subset resonance spline**
$\sum_{S\subseteq\rm minus,\,T\subseteq\rm plus}(-1)^{|S|+|T|}(\cdots)_+^{p}$ times a
small prefactor — NOT a single one-sided block.

### Tasks this round (the two attacks on the n>=6 closed form)
- **student-1 (bottom-up):** enumerate the realizable chambers of the $\{k_S=0\}$
  arrangement at $n=6$ (which occur on-shell — the analogue of "chamber D is empty"
  at n=5), then EXTRACT the exact degree-8 core polynomial on each chamber and
  recognize the global pattern (box-spline / convolution / double-subset spline).
- **student-2 (top-down):** derive the three-minus structure from the BG recursion /
  the probabilistic B-spline picture, produce a conjectured **all-$n$** formula, and
  test it exactly at $n=5,6,7$ across chambers and near walls. Plus a focused
  literature pass (water-wave amplitude closed forms; box-spline / multivariate
  B-spline).

Both attack the same nut from opposite ends — by design, for cross-validation. As
soon as either yields a candidate that passes my independent exact re-verification
across chambers and wall-limits, I write `SOLVED.md` and we generalize.

### Next steps
If a clean $n=6$ form emerges, immediately push the all-$n$ generalization and
re-verify at $n=7$ (and spot-check $n=8$ in `--double`). If the per-chamber data
refuses to collapse to a single closed form, the deliverable becomes the explicit
per-chamber polynomial table plus the wall arrangement — already a complete
validated description.

## Round 1 — 2026-06-26T18:15:35Z (PI)

### Where we are
First working session. I built the oracle (`bg.cpp`) in `bots/pi/code/` and
confirmed it reproduces every stated known fact: one-minus vanishes, and
three-minus gives finite rational amplitudes at $n=5,6,7$. **Important oracle
caveat:** on $|k_S|=0$ walls (e.g. two free frequencies equal) the oracle divides
by zero — SIGFPE in exact mode, `inf/nan` in `--double`. These are
coordinate-degenerate walls; approach them as limits, never sample them exactly.

### Result locked this round: the n=5 closed form
Using the plus/minus swap (question.md item 3) plus the two-minus law (item 2):
flipping every sign turns the three-minus configuration (minus legs $1,2,3$) into a
**two-minus** configuration whose minus legs are $4,5$. Applying the two-minus
truncated-power law to that relabeling gives, with legs $1,2,3$ the minus legs and
$4,5$ the plus legs,

$$
A_5 = i\,2^{4}\,g^{-2}\,\omega_4\,\omega_5
\sum_{S\subseteq\{1,2,3\}}(-1)^{|S|}\Big(\beta^2-\sum_{j\in S}\omega_j^2\Big)_+^{2},
\qquad \beta=\min(|\omega_4|,|\omega_5|),\ (x)_+=\max(x,0).
$$

I verified this **independently** (`bots/pi/code/verify_n5.py`) against `./bg` in
exact rational mode at 11 non-degenerate points — generic, fractional, and extreme
non-generic ($\omega=100,1,2$ and $1,1,100$). **Exact agreement, 11/11.** So $n=5$
is done; the genuinely new physics starts at $n=6$.

### Why the swap stops helping at n=6
The all-sign flip maps $k$-minus $\to (n{-}k)$-minus. For three-minus that is
$(n{-}3)$-minus: $n=5\to$ two-minus (known — what we used), but $n=6\to$
three-minus (a self-map, no new info) and $n=7\to$ four-minus (also unknown). So
$n\ge6$ needs a different handle — most likely the Berends–Giele factorization
structure directly.

### The central open question
Does three-minus carry **poles** for $n\ge6$? question.md conjectures yes —
factorization channels where an internal line goes on-shell,
$\omega_S^2/|k_S|-g=0$. A naive one-frequency sweep of $A_6$ shows only smooth,
polynomial-like growth (no clean divergence), so the pole question must be attacked
by **deliberately steering kinematics onto a channel** $\omega_S^2=g|k_S|$, not by
generic scanning. Resolving polynomial-vs-rational is the gate to the whole ansatz.

### Tasks this round
- **student-1:** Consolidate $n=5$ — re-verify the closed form at many points
  (incl. near $|k_S|=0$ walls as limits), give the explicit chamber decomposition
  in the original $\omega$'s, and re-derive the swap relabeling cleanly.
- **student-2:** Attack $n=6$ — build a fast harness, run a *targeted* pole search
  on the factorization channels $\omega_S^2=g|k_S|$, map the chamber walls, decide
  polynomial vs rational, and propose a first $A_6$ ansatz.

### Next steps
Once student-2 reports whether/where poles exist, the round-2 split is either
(a) fit a piecewise-polynomial $A_6$ (if no poles) or (b) build the
channel-decomposed rational ansatz and fix its polynomial remainder (if poles).
