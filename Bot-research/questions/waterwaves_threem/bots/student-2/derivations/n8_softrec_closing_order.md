# Round 8 (student-2, top-down): soft recursion re-confirmed + the cross-term CLOSING ORDER pinned by sign-independent forcing geometry

**Sector** $\sigma=(-1,-1,-1,+1,\dots,+1)$, minus legs $M=\{1,2,3\}$, plus legs
$P=\{4,\dots,n\}$. PI-verified baseline:
$$A_n^{3-}=i\,2^{n-1}g^{3-n}\,\frac{N_n(\omega)}{D_n(\omega)},\qquad
D_n=\prod_{i\in M}\prod_{j\in P}(\omega_i+\omega_j),$$
$N_n$ a continuous truncated-power **spline**, $\deg N_n=5n-13$, $S_3(M)\times S_{n-3}(P)$-symmetric,
parity $(-1)^{\deg D_n}=(-1)^{3(n-3)}$ (so $N_n$ even iff $n$ odd). $n=5,6$ SOLVED & PI-verified.
The OPEN problem is the explicit $N_n$ for $n\ge7$; the live sub-question is the **cross-term
closing order** (PI round-8 task; s1_022 was TENTATIVE). All amplitudes checked against my own
copy of `bg.cpp` (exact GMP), now with a guarded `--batch` mode (`r8bg.py`). One command:
`python3 bots/student-2/code/verify_r8.py`.

Notation: $a_i:=\omega_i^2$ ($i\in M$), $b_j:=\omega_j^2$ ($j\in P$). The mixed subset-sum
walls are the **square** relations $k_S=\sum_{i\in S}\sigma_i\omega_i^2=0$; the orbits under
$S_3(M)\times S_{n-3}(P)$ are $(1{=}q)$: $a_i=\sum_{j\in T}b_j$ with $|T|=q$.

---

## 1. Soft recursion re-confirmed at $n=7$, BOTH legs (own oracle)

Using $A_n^{3-}\to 2(n-3)\,\omega_p^2\,A_{n-1}$ with $2(n-3)=8$ at $n=7$, take $\omega_p\to0$
through tiny values (single soft chamber) and compute the exact ratio $A_7/(i\,\varepsilon^2)$:

| soft leg | ratios $A_7/(i\varepsilon^2)$ ($\varepsilon=\tfrac{4,2,1}{2000}$) | $\to$ target |
|---|---|---|
| plus  ($\omega_4$) | $-21258202,\,-21261015,\,-21262422$ | $8\,A_6^{3-}=-21263828$ |
| minus ($\omega_2$) | $-9284208,\,-9282580,\,-9281767$ | $8\,A_6^{2-}=-9280955$ |

Both monotonically converge to $8\times$ the surviving $A_6$ (three-minus for a soft plus leg,
two-minus for a soft minus leg). This re-confirms s2_021 with my own evaluator. (The amplitude
$N_n=A_nD_n$ therefore vanishes to order $\varepsilon^2$ on each $\{\omega_p=0\}$; the
$\varepsilon^2$-coefficient is fixed by $N_{n-1}$ / the two-minus law — a recursion on the
hyperplane restriction, boundary the two-minus law.)

---

## 2. The cross-term closing order, from SIGN-INDEPENDENT forcing geometry (main result)

A cross-term in $N_n$ is a product of truncated powers on walls $W_1,W_2,\dots$ and is nonzero
only on a **transversal codimension-$k$ stratum** of the wall arrangement. The strata are governed
by the two manifold identities — resonance $\sum_{i\in M}a_i=\sum_{j\in P}b_j$ and momentum
$\sum_{\rm all}\omega=0$ — applied to the **square** relations $a_i=b_j$ (the $(1{=}1)$ walls
are conditions on the SQUARES; they do NOT fix the signs of $\omega_i,\omega_j$). This is the key
point I initially got wrong by fixing matching signs, and it changes the conclusion.

**(F1) A disjoint $(1{=}1)$ pair forces a complementary subset-sum wall.**
Impose $a_1=b_4$ and $a_2=b_5$ ($i\ne k$, $j\ne l$). Resonance gives
$$a_3=\Big(\sum_{j\in P}b_j\Big)-b_4-b_5=\sum_{j\in P\setminus\{4,5\}}b_j,$$
a $(1{=}(n{-}5))$ wall on the third minus leg. This is EXACT and sign-independent. Specializations:
- $n=6$: $a_3=b_6$ — a $(1{=}1)$ wall (the third matching edge). The disjoint pair completes a
  **perfect matching** (bijection) — exactly student-1's verified $n=6$ matching-pair cross-term.
- $n=7$: $a_3=b_6+b_7$ — a $(1{=}2)$ wall. The disjoint $(1{=}1)$ pair corner sits ON a $(1{=}2)$
  wall. Hence a $(1{=}1)\times(1{=}1)$ cross-term contributes jump order $1+1=2$ to the $(1{=}2)$
  wall — **this is exactly the measured $(1{=}2)\to2$** (PI/s1_021), confirming the TENTATIVE
  reading s1_022 with a rigorous mechanism. (The pure single-$(1{=}2)$ truncated power, if present,
  carries the two-minus exponent $n-3=4$; the OBSERVED jump order is the minimum, $=2$.)
- $n=8$: $a_3=b_6+b_7+b_8$ — a $(1{=}3)$ wall.

**Realizable, non-degenerate at $n=7$** (`verify_r8.py` part 2): fixing $\omega_2=\omega_5$ (so
$a_2=b_5$) and scanning, the on-shell solver hits $a_1=b_4$ at $\omega_3\approx-4.253$
(with $\omega_4=5,\omega_6=2$), a non-degenerate point whose corner lies on $a_3=b_6+b_7$.

**(F2) Same-leg $(1{=}1)$ pairs do NOT couple.** $a_i=b_j$ and $a_i=b_k$ give $b_j=b_k$
(an analytic same-type PLUS locus); $a_i=b_j$ and $a_k=b_j$ give $a_i=a_k$ (same-type MINUS).
Same-type orderings are analytic (not walls), so these are not transversal mixed strata.
Only **disjoint** $(1{=}1)$ pairs couple.

**(F3) Three disjoint $(1{=}1)$ edges force vanishing legs — NO triple-$(1{=}1)$ cross-term for $n\ge7$.**
Impose $a_1=b_4,a_2=b_5,a_3=b_6$. Resonance gives
$$\sum_{j\in P\setminus\{4,5,6\}}b_j=0,$$
i.e. the remaining $n-6$ plus squares sum to zero — for real frequencies they all vanish.
- $n=6$: no remaining plus leg, so this is the (realizable) perfect matching — the $n=6$ special case.
- $n\ge7$: at least one plus leg is forced to $0$ (DEGENERATE). So there is no transversal
  triple-$(1{=}1)$ stratum, hence **no triple-$(1{=}1)$ cross-term**. The $(1{=}1)$ sector closes
  at PAIRWISE products for all $n$ (the $n=6$ "triple adds nothing", s1_017, persists structurally).

**General-$n$ statement.** $k$ pairwise-disjoint $(1{=}1)$ edges force
$\sum_{j\in P\setminus(\text{used})}b_j=\sum_{\text{remaining }k\text{ minus}}a_i$ over the
$n-3-k$ unused plus legs; the family is non-degenerate iff there are enough unused plus legs to
absorb it, which fails for $k=3$ once $n\ge7$. So **the $(1{=}1)$ cross-terms are exactly the
disjoint matching PAIRS**, whose forced locus migrates from a $(1{=}1)$ wall ($n=6$) to a
$(1{=}(n-5))$ wall ($n\ge7$).

---

## 3. Independent exact confirmation of single-wall exponents (own oracle)

Polynomial-division jump extractor (`r8_jumps.py`): on an F-const slice, reconstruct
$N_7=A_7D_n$ as a polynomial on each side of a SINGLE-wall crossing (pre-scan to isolate one
wall), form $J=N_+-N_-$, and take the exponent $=$ max power of the (polynomial) wall function
dividing $J$ (exact, robust to irrational wall locations). Confirmed:
- $(1{=}3)\to4=n-3$ (slices C, D, F) — the **pure two-minus-like exponent**.
- $(1{=}1)\to1$ (slice F) — the anomalous exponent.

$(1{=}2)\to2$ is PI-verified (twice) and now explained by (F1). Together: the single-wall **pure**
exponents are $(1{=}1)\to1$ and $(1{=}q\ge2)\to n-3$; the OBSERVED $(1{=}2)\to2$ at $n=7$ is the
disjoint-$(1{=}1)$-pair cross-term, not a pure exponent.

---

## 4. The subset-sum coefficient is NOT a simple two-minus amplitude

The conjecture "the subset-sum truncated-power coefficient is a two-minus block of a sub-config"
fails as literally stated: the PI-verified $n=6$ $(1{=}2)$ coefficient
$Q=A_2B_1(y^2-A_1^2-A_1B_1+A_2-B_2)+B_2y(A_2-B_1y-B_2)$ (minus pair $A_1,A_2$, plus pair $B_1,B_2$,
excluded plus $y$) is **degree 5, ODD, and irreducible over $\mathbb Q$** — whereas a two-minus
amplitude $A^{2-}/i$ is even of degree $2m-4$. So the subset-sum coefficients are genuinely new
polynomials (the open piece of the fit), not pull-backs of the two-minus law.

---

## 5. The all-$n$ description (refined; pinned vs open)

$$\boxed{\,A_n^{3-}=i\,2^{n-1}g^{3-n}\,\frac{N_n}{\prod_{i\in M,j\in P}(\omega_i+\omega_j)}\,}$$
with $N_n$ the $S_3\times S_{n-3}$-symmetric truncated-power spline on $\{a_i=\sum_T b_j\}$:
$$N_n=B_n+\sum_{i,j}(b_j-a_i)_+\,P_{ij}+\sum_{\substack{\text{disjoint }(1{=}1)\\\text{pairs}}}(b_j-a_i)_+(b_l-a_k)_+\,R+\sum_{i,\,|T|\ge2}(a_i-\textstyle\sum_{T}b_j)_+^{\,n-3}\,Q_{i,T}+\dots$$

**Pinned (all $n$):** minimal denominator $D_n$ (pole order 1; collapse only at $n=6$);
$\deg N_n=5n-13$; $S_3\times S_{n-3}$ symmetry; $n$-dependent parity; the soft recursion on every
$\{\omega_p=0\}$ (both legs, boundary the two-minus law); the recursive matching residue (s2_022);
the **pure** wall exponents $(1{=}1)\to1$, $(1{=}q\ge2)\to n-3$; and the **$(1{=}1)$ cross-term
closing order = disjoint matching PAIRS only (no triples), with the pair corner on the
$(1{=}(n-5))$ wall** (§2).

**Open:** the explicit base $B_n$ and the coefficient polynomials $P_{ij},R,Q_{i,T}$ for $n\ge7$
(student-1's exact fit), and whether genuine $(1{=}1)\times(\text{subset-sum})$ or
$(\text{subset-sum})^2$ couplings beyond the matching pair are present (a rank question for the
fit; the matching pair is the only one forced by the geometry).

### Literature (cited)
Berends–Giele / perturbiner: Mizera & Skrzypek, arXiv:1809.02096 (JHEP 2019).
Truncated-power / box-spline & partial fractions: de Boor–Höllig–Riemenschneider, *Box Splines*
(1993); De Concini–Procesi–Vergne (2010). Single-minus gauge/gravity cousins: arXiv:2602.12176,
2603.04330 (2026). No published closed form for this sector.
