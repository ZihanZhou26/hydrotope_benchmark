# n=7 three-minus, round 7: wall map, jump exponents, cross-term structure, and the parity correction

**student-1, round 7 (2026-06-27).** All exact-rational against my own copy of
`bg.cpp` (`bots/student-1/code/bg.cpp`; shared oracle untouched), cross-checked by
the native-Python BG port `pybg.py` (== `./bg` at n=5,6,7).

Sector at n=7: minus legs {1,2,3}, plus legs {4,5,6,7}. On-shell solve: free =
(ω₂,…,ω₆) (legs 2..6; legs 2,3 minus, 4,5,6 plus), legs 1,7 solved.
Denominator (fixed, s2_018/PI-corroborated): D₇ = ∏_{i∈M,j∈P}(ωᵢ+ωⱼ), 12 mixed
pairs, degree 12, pole order 1. So
$$A_7 = i\,2^{6} g^{-4}\,\frac{N_7}{D_7},\qquad N_7 = \frac{A_7 D_7}{i\,2^6 g^{-4}},\quad \deg N_7 = 2n-4+3(n-3)=22.$$

## 0. PARITY CORRECTION — N₇ is EVEN, not odd

The round-4..6 claims and the round-7 task brief state "N_n is ω→−ω ODD". That is
correct **only at n=6**, where the minimal denominator e₃⁻+e₃⁺ (degree 3) is odd, so
N₆ = A₆·(e₃⁻+e₃⁺) = even·odd = odd. **At n=7 the minimal denominator is the full
12-factor product D₇, which is EVEN** (12 factors, (−1)¹²=+1 under ω→−ω). Hence
$$N_7(-\omega) = A_7(-\omega)\,D_7(-\omega) = A_7(\omega)\,D_7(\omega) = +N_7(\omega)\quad\text{(EVEN).}$$
Verified directly against `./bg`: A₇(−ω)=A₇(ω) and N₇(−ω)=N₇(ω) (exact, two points).
Consequence: every coefficient polynomial in the truncated-power decomposition, and the
smooth base, has EVEN total degree (n=6 had odd ones). In particular the
"box-spline-of-ω²" / polynomial-in-squares idea that parity ruled out at n=6 (s2_015)
is **not** killed by parity at n=7.

## 1. Wall map — 42 mixed walls, three S₃×S₄ orbits

Mixed subset-sum walls k_S = Σ_{i∈S} σᵢ ωᵢ² = 0 reduce (mod the complement identity
k_S = −k_{Sᶜ} on the manifold) to THREE orbit types under S₃(minus)×S₄(plus):

| orbit | wall eqn (a=ω²minus, b=ω²plus) | # walls | (2=...) complement form |
|---|---|---|---|
| (1=1) | aᵢ = bⱼ | 12 | (2=3): aₚ+a_q = b_l+b_m+b_n |
| (1=2) | aᵢ = bⱼ+b_k | 18 | (2=2): aₚ+a_q = b_l+b_m |
| (1=3) | aᵢ = bⱼ+b_k+b_l | 12 | (2=1): aₚ+a_q = b_m |

Total 42 distinct loci. Using the single-minus representation aᵢ = (sum of plus
squares) gives one canonical function per wall, so the (2=q) walls are already covered
(e.g. aₚ+a_q=bⱼ ≡ a_r = b_{the other three plus}, a (1=3)). Same-type orderings
(ωᵢ²=ωⱼ² within a block) are analytic, as at n=6.

## 2. Single-wall LOCAL jump exponents (EXACT)

On clean single-wall crossings (sd=1 against the 42-wall signature), reconstructing
N₇(t) as a polynomial on each side of the wall and reading the order of vanishing of
the jump N_R−N_L:

| wall | n=6 (control) | n=7 |
|---|---|---|
| (1=1) aᵢ=bⱼ | 1 | **1** |
| (1=2) aᵢ=bⱼ+b_k | 3 (=n−3) | **2** |
| (1=3) aᵢ=bⱼ+b_k+b_l | — (degenerate at n=6) | **4** (=n−3) |

The n=6 control reproduces the established (1=1)→1, (1=2)→3. The measured numbers are the
**LOCAL jump order** (smoothness) on a generic single-wall crossing; because the jump is
the sum of every truncated-power term that turns on across the wall, the measured order is
the **minimum** over the single-wall term and any active CROSS-term — so cross-terms can
*lower* it below the pure single-wall exponent (this is the key to reading the table).

## 3. Cross-term structure — the (1=2) "exponent 2" is the (1=1)×(1=1) matching cross-term

At n=6 the only cross-terms are the matching PAIRS $(b_j-a_i)_+(b_l-a_k)_+$ (disjoint
mixed edges, exponent (1,1)); two disjoint (1=1) edges on the manifold force a THIRD (1=1)
edge (a perfect matching), so the pair lives on a (1=1)∩(1=1) corner (s1_017).

**At n≥7 the forcing geometry changes (s1_019):** two disjoint (1=1) edges no longer force
a third (1=1) edge but a SUBSET-SUM relation. Concretely, the (1=2) wall $\{a_2=b_4+b_5\}$
is exactly the locus FORCED by either disjoint (1=1) edge pair
$$P_1=\{a_1=b_6\}\cap\{a_3=b_7\}\quad\text{or}\quad P_2=\{a_1=b_7\}\cap\{a_3=b_6\},$$
because on the manifold $a_1+a_3=b_6+b_7 \iff a_2=b_4+b_5$ (conservation, the four legs
1,3,6,7 being the complement of 2,4,5). So the n=6 matching cross-term
$(b_6-a_1)_+(b_7-a_3)_+\,(\dots)$ — still present at n=7 with each factor exponent 1 — sits
ON the (1=2) wall $\{a_2=b_4+b_5\}$, and crossing that (1=2) wall while the cross-term is
active produces a jump of order $1+1=2$.

**This explains the measured (1=2)→2 as a CROSS-TERM artifact, not the pure single
exponent.** Evidence:
- the n=6 control gives (1=2)→3 cleanly, because at n=6 there is no (1=1)×(1=1) cross-term
  on a (1=2) wall (the matching forces a (1=1), not a (1=2));
- at n=7, EVERY measured (1=2)→2 crossing (5 distinct chambers) has the leftover-plus
  (1=1) walls active;
- $2=1+1$ matches two (1=1) factors of exponent 1;
- (1=3)→4 (no (1=1)² cross-term forces a (1=3) wall here) is consistent with the pure
  subset-sum exponent being $n-3=4$.

**Conjecture (pure exponents):** the *pure* single-wall exponents are
$$(1{=}1)\to 1,\qquad \text{every subset-sum wall}\ (1{=}q,\ q\ge 2)\to n-3,$$
and the OBSERVED local orders are lowered by the (1=1)×(1=1) matching cross-terms whose
forced locus is a subset-sum wall. So the n=7 numerator has the schematic shape
$$N_7 = B + \sum_{(1=1)}(b_j-a_i)_+\,P + \!\!\sum_{\text{disjoint }(1=1)\text{ pairs}}\!\!(b_j-a_i)_+(b_l-a_k)_+\,R
 + \sum_{(1=2)}(\dots)_+^{4}Q + \sum_{(1=3)}(\dots)_+^{4}S + (\text{higher cross-terms}),$$
the matching-pair sum now ranging over disjoint (1=1) edge pairs (injections, not just the
n=6 bijections), and possibly higher products as the injection structure allows. Whether
the (1=1) box spline closes at pairwise cross-terms (as at n=6) or needs triples at n=7
(three disjoint (1=1) edges exist: 3 minus × choose-3-of-4 plus) is the next structural
question.

### 3a. Direct forcing-edge isolation (status)

The clean isolation — measure the (1=2) jump where BOTH forcing pairs are inactive,
expecting the order to rise above 2 — is constrained: on the wall $a_2=b_4+b_5$ the
complement forces $a_1+a_3=b_6+b_7$, so the minus pair {1,3} and plus pair {6,7} have
equal sum-of-squares, and "both forcing pairs inactive" lives in a narrow region that is
hard to reach as a *thick* chamber via the rational on-shell solve (`n7_forcing.py`). The
multi-chamber data we do have is uniform: every clean (1=2)→2 crossing measured (5
chambers) has the relevant leftover (1=1) walls active, never the pure exponent. So the
isolation remains the one open check; the conclusion rests on the forcing geometry +
n=6 analogy + the 1+1=2 arithmetic + (1=3)→4=n−3.

## 4. The full N₇ assembly — scope and status

$\deg N_7 = 22$ (even). A direct exact box-spline assembly (as at n=6) needs: a smooth
base $B$ (≈300+ independent $S_3\times S_4$-symmetric even weighted-degree-22 templates in
the invariants $e_1,e_2,e_3^-,e_3^+,e_4^+$), a single-(1=1) coefficient $P$ of degree 20,
the (1=2)/(1=3) coefficients of degree 14, and the matching/cross-term coefficients —
several hundred to ~1000 exact coefficients, each fit needing >1000 exact n=7 amplitudes
(~1 s each). This is at the edge of one session and is the natural joint frontier with
student-2's top-down all-$n$ ansatz, which the PI's task split anticipates ("hand the
wall/exponent/cross-term TABLE to student-2"). The table below is that hand-off.

## 5. Hand-off TABLE (for student-2's all-n lift)

- **Denominator:** $D_7=\prod_{i\in M,j\in P}(\omega_i+\omega_j)$, degree 12, pole order 1
  (no n=6-style collapse; s2_018). $\deg N_7 = 5n-13 = 22$.
- **Symmetry:** $S_3(\text{minus})\times S_4(\text{plus})$ (NO $Z_2$ swap at $n\ge7$).
- **Parity:** $N_7$ is **EVEN** under $\omega\to-\omega$ (NOT odd — odd was an n=6 artifact).
- **Walls:** 42 = (1=1)[12] ∪ (1=2)[18] ∪ (1=3)[12].
- **Local jump orders (generic chamber):** (1=1)→1, (1=2)→2, (1=3)→4.
- **Pure single exponents (conjectured):** (1=1)→1, all subset-sum (1=q,q≥2)→$n-3=4$.
- **Cross-terms:** (1=1)×(1=1) matching products (each factor exp 1); at $n\ge7$ a disjoint
  pair of (1=1) edges forces a subset-sum wall (s1_019), so the matching cross-term shows up
  as a *lowered* jump order on (1=2)/(1=3) walls. Matchings are injections $M\hookrightarrow P$
  (not bijections); closing order (pairs vs triples) open.
- **Soft / residue constraints:** s2_012 (soft recursion, both legs), s2_020 (single-pair
  residues, accessible at n=7).

## 6. Reproduce
```
cd bots/student-1/code
g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp
python3 n7lib.py            # infra + parity check (N_7 EVEN)
python3 n7_walls.py         # wall map (42 = 12+18+12) + exponents
python3 n7_exponents.py     # n=6 control + n=7 exponents (EXACT)
python3 n7_exp_clean.py     # (1=3)->4, multi-chamber (1=2)->2
python3 n7_xterm_test.py    # (1=2)->2 across chambers, active (1=1) partners
```


