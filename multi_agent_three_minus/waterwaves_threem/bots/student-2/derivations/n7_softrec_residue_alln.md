# Round 7 (student-2, top-down, all-$n$): soft recursion at $n=7$, the single-pair residue's recursive matching structure, and the all-$n$ description

**Sector** $\sigma=(-1,-1,-1,+1,\dots,+1)$, minus legs $M=\{1,2,3\}$, plus legs
$P=\{4,\dots,n\}$. PI-verified baseline (post_018):
$$A_n^{3-}=i\,2^{\,n-1}g^{\,3-n}\,\frac{N_n(\omega)}{D_n(\omega)},\qquad
D_n=\prod_{i\in M}\prod_{j\in P}(\omega_i+\omega_j),$$
with $N_n$ a continuous truncated-power **spline** (deg $5n-13$ with the FULL
denominator $D_n$, $S_3(\mathrm m)\times S_{n-3}(\mathrm p)$-symmetric, $\omega\to-\omega$
**odd**; the $Z_2$ swap is NOT a symmetry for $n\ge7$). $n=6$ is closed (student-1
s1_018, PI-verified): $A_6=i2^5g^{-3}N_6/(e_3^-+e_3^+)$. The open piece is the
explicit $N_n$ for $n\ge7$. All amplitudes checked against my own copy of `bg.cpp`
(exact GMP rationals).

---

## 1. Soft recursion is EXACT at $n=7$ (both legs) — `r7_soft.py`

The soft theorem / numerator recursion (s2_006, s2_012) is re-verified EXACTLY in
the genuinely-new $n=7$ regime, using an **F-constant slice** so the limit is exact
rather than a numerical extrapolation. Make the soft leg $\omega_p=\varepsilon$ and a
partner plus leg $=c-\varepsilon$ (so $\sum\omega$ is constant $\Rightarrow$ all legs
polynomial in $\varepsilon$ $\Rightarrow$ $A_7\,D_n=:N_{\rm full}(\varepsilon)$ is a
polynomial); then
$$\lim_{\varepsilon\to0}\frac{A_7}{i\,\varepsilon^2}=\frac{[\varepsilon^2]\,N_{\rm full}}{D_n(0)}.$$
Result $=2(n-3)=8$ times the surviving $A_6$ in BOTH cases:
- **plus leg** $\to0$: $\lim A_7/(i\varepsilon^2)=-239585664/17 = 8\cdot A_6^{3-}/i$
  (surviving $A_6^{3-}/i=-29948208/17$). EXACT.
- **minus leg** $\to0$: $\lim A_7/(i\varepsilon^2)=-13369344/25 = 8\cdot A_6^{2-}/i$
  (surviving $A_6^{2-}/i=-1671168/25$). EXACT.

So $A_n^{3-}\to 2(n-3)\,\omega_p^2 A_{n-1}$ holds at $n=7$ with the surviving amplitude
the **6-point three-minus** (soft plus leg) or the **6-point two-minus** (soft minus
leg). This ties the explicit PI-verified $n=6$ closed form to $n=7$ and provides the
numerator recursion on every coordinate hyperplane $\{\omega_p=0\}$.

---

## 2. The single-pair residue: recursive matching / Cauchy structure (`r7_residue.py`, `r7_resid_poly.py`)

At $n\ge7$ a single mixed pair vanishes ALONE (s2_019), so
$\mathrm{Res}_{ij}:=\lim_{\omega_i+\omega_j\to0}(\omega_i+\omega_j)A_n$ is accessible by
a one-parameter on-shell limit. New characterization of its structure:

**(a) The merged pair drops out of conservation.** On the wall $\{\omega_i+\omega_j=0\}$
($i$ minus, $j$ plus, so $\omega_j=-\omega_i$ and $\omega_j^2=\omega_i^2$), the pair
contributes $0$ to $\sum\omega$ and $0$ to $\sum\sigma\omega^2$. Hence the surviving
$n-2$ legs (here $\{1,3,4,6,7\}$ for the pair $(2,5)$: 2 minus + 3 plus) satisfy the
**$(n-2)$-point two-minus on-shell constraints**, INDEPENDENT of the merged scale
$\omega_i$. So $\mathrm{Res}_{ij}$ is a function of (surviving config) AND the merged
scale $\omega_i$ separately.

**(b) The residue is rational in the merged scale, with poles ONLY at sub-collisions.**
With the surviving config held FIXED and the merged scale $\omega_2$ varied,
$$\mathrm{Res}_{25}(\omega_2)=\frac{N_n|_{\rm wall}(\omega_2)}
{\underbrace{(\omega_1-\omega_2)(\omega_3-\omega_2)}_{\text{pairs }(1,5),(3,5)\to0}\,
\underbrace{(\omega_2+\omega_4)(\omega_2+\omega_6)(\omega_2+\omega_7)}_{\text{pairs }(2,4),(2,6),(2,7)\to0}\cdot(\text{survivor-only pairs})}.$$
Each $\omega_2$-pole is a **sub-collision**: a value of the merged scale at which a
SECOND mixed pair also vanishes (a double-collision of the matching). Verified
(survivors $(\omega_1,\omega_3,\omega_4,\omega_6,\omega_7)=(-249/19,3,5,11,-112/19)$;
modular reconstruction at $p=2^{61}-1$, cross-validated against exact $\mathrm{Res}$
values, e.g. $\mathrm{Res}_{25}(\omega_2{=}2)/i=-13576492892160/2622893$):
$$P(\omega_2):=\mathrm{Res}_{25}(\omega_2)\,(\omega_1-\omega_2)(\omega_3-\omega_2)
(\omega_2+\omega_4)(\omega_2+\omega_6)(\omega_2+\omega_7)$$
is a **polynomial of degree 7** in $\omega_2$ (minimal-degree fit through 8 points,
held-out consistent on the rest). So $\mathrm{Res}_{25}(\omega_2)$ is a rational
function whose ONLY merged-scale poles are the 5 sub-collision loci (degree-7
numerator over degree-5 denominator $\Rightarrow$ $\mathrm{Res}\sim\omega_2^2$ at
large scale, consistent with the soft $\omega^2$ law). [`r7_resid_mod.py`;
exact spot values from `r7_resid_fast.py`/`r7_resid_scale3.py`.]

**(c) Consequence — rules out a clean matching-injection partial fraction.** If
$A_n=i2^{n-1}g^{3-n}\sum_{\sigma:M\hookrightarrow P}\Phi_\sigma/\prod_i(\omega_i+\omega_{\sigma(i)})$
with POLYNOMIAL $\Phi_\sigma$, then $\mathrm{Res}_{25}$ (collecting injections with
$\sigma(2)=5$) would have denominators built only from SURVIVOR pairs and hence NO
$\omega_2$-poles. The observed sub-collision $\omega_2$-poles therefore force the
$\Phi_\sigma$ to be rational/spline, not polynomial: $A_n$ is **not** a permanent of a
single Cauchy kernel (sharpens s2_013, s2_016). The residue is genuinely a **recursive**
rational object: $\mathrm{Res}_{ij}$ is itself a partial fraction over the sub-matchings
$M\setminus\{i\}\hookrightarrow P\setminus\{j\}$ of the surviving minus legs, whose own
poles are the sub-collision loci.

**(d) Soft–residue compatibility.** As a surviving MINUS leg $\to0$, the residue must
vanish (the soft-minus limit $A_n\to(n-3)g\,\omega_p^2\,C^{2-}_{n-1}$ is pole-free in
the survivor pairs), giving an extra constraint on $N_n|_{\rm wall}$.

---

## 3. Unified wall/exponent law (conjectured; partial $n=7$ data)

The proposed all-$n$ ansatz uses the **unified exponent law**: the $(1{=}1)$ walls
$a_i=b_j$ carry the anomalous exponent $1$ (the difference branch of
$|k_{ij}|=|\omega_i-\omega_j||\omega_i+\omega_j|$, whose sum branch is the shielded
pole $D_n$), and **every other** mixed subset-sum wall carries the two-minus exponent
$n-3$. Established data: $(1{=}1)\to1$ at $n=5,6,7$ and $(1{=}2)/(2{=}1)\to n-3$ at
$n=6$ ($=3$) and $n=7$ ($=4$) — student-1 s1_013/s1_019, PI-corroborated. The NEW
walls available only at $n\ge7$ — $(1{=}3)$ $a_i=b_j+b_k+b_l$ and $(2{=}2)$
$a_i+a_k=b_j+b_l$ — are CONJECTURED to carry $n-3$ by the unified law.
My generic F-constant slices (varying two plus legs oppositely) cross several mixed
walls simultaneously (the known multi-wall-contamination hazard, `r7_walls_fast.py`
found no clean sign-diff$=1$ crossing of the new types), so a clean single-wall
measurement of the $(1{=}3)/(2{=}2)$ exponents is deferred to student-1's targeted
bottom-up probes.

---

## 4. The all-$n$ description (proposed ansatz; what is pinned vs open)

$$\boxed{\,A_n^{3-}=i\,2^{\,n-1}g^{\,3-n}\,\frac{N_n}{\prod_{i\in M,j\in P}(\omega_i+\omega_j)}\,}$$
with $N_n$ the $S_3\times S_{n-3}$-symmetric, $\omega$-odd truncated-power spline on the
mixed subset-sum wall arrangement $\{k_S=\sum_{i\in S}\sigma_i\omega_i^2=0\}$:
$$N_n = B_n \;+\!\!\sum_{\substack{i\in M,\,T\subseteq P\\|T|\ge1}}\!\!(a_i-\textstyle\sum_{j\in T}b_j)_+^{\,e(T)}\,Q_{i,T}
\;+\!\!\sum_{\substack{j\in P,\,U\subseteq M\\|U|\ge2}}\!\!(b_j-\textstyle\sum_{i\in U}a_i)_+^{\,n-3}\,\tilde Q_{j,U}
\;+\;(\text{cross-terms}),$$
$e(\{j\})=1$ (the $(1{=}1)$ walls), $e(T)=n-3$ for $|T|\ge2$; cross-terms are products of
truncated powers indexed by the **injection** geometry (disjoint $(1{=}1)$ edges couple
to subset-sum walls for $n\ge7$, s1_019). It specializes to student-1's PI-verified
$N_6$ (where the cross-terms are matching PAIRS, $Z_2$-symmetric, and $D_6$ collapses to
$(e_3^-+e_3^+)$).

**Pinned (this round + prior):** the denominator (minimal, all $n$), degree $5n-13$,
symmetry, parity, the unified wall/exponent law, the soft recursion on every
$\{\omega_p=0\}$ with boundary the two-minus law, and the recursive matching structure of
the simple poles. **Open:** the explicit cross-term coefficient polynomials $Q,\tilde Q$,
and the base $B_n$, for $n\ge7$ — the residual unknown handed to / shared with student-1's
bottom-up assembly.

### Literature (cited)
Berends–Giele / perturbiner: Mizera & Skrzypek, arXiv:1809.02096 (JHEP 2019).
Truncated-power / box-spline & partial fractions: de Boor–Höllig–Riemenschneider,
*Box Splines* (1993); De Concini–Procesi–Vergne (2010). Single-minus gauge/gravity
cousins: arXiv:2602.12176, 2603.04330 (2026). No published closed form for this sector.
