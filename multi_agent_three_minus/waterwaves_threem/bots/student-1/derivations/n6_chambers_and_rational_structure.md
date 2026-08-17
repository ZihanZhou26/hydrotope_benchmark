# $n=6$ three-minus: chamber arrangement and the RATIONAL (not polynomial) structure of $A_6$

**Author:** student-1  **Task:** `r2-student-1`  **Sector:** $\sigma=(-1,-1,-1,+1,+1,+1)$
(minus legs $1,2,3$; plus legs $4,5,6$).  Notation: $a_i=\omega_i^2$ ($i\in M=\{1,2,3\}$),
$b_j=\omega_j^2$ ($j\in P=\{4,5,6\}$).  On-shell: $\sum_i\omega_i=0$ and
$\sum_M a_i=\sum_P b_j=:Q$.  All checks against my own copy of `bg.cpp`
(`bots/student-1/code/bg.cpp`, rebuilt; shared oracle untouched).

---

## 1. Headline (corrects the round-1 gate)

> **$A_6$ in the three-minus sector is piecewise-RATIONAL, NOT piecewise-polynomial.**
> The round-1 "gate" recorded it as a degree-8 polynomial spline. That is wrong:
> $A_6$ is a *ratio* of polynomials. Its denominators are momentum-magnitude factors
> $|k_S|$ from the Berends–Giele kernels that **fail to cancel at $n=6$** (they *do*
> cancel at $n=5$, which is why two-minus / $n=5$ three-minus are polynomial). The
> surviving denominators are sums of squares (e.g. $\omega_4^2+\omega_5^2$), so they
> never vanish on the physical manifold: **$A_6$ is finite everywhere (no physical
> poles — that part of the gate is correct), but it is genuinely rational.**

This means **the whole "polynomial spline / box-spline" ansatz family the group has been
pursuing cannot work.** The closed form must be a *rational* function (ratio of
polynomials with sum-of-squares denominators), not a spline of truncated powers.

### Proof that $A_6$ is not polynomial (rigorous)
If $A_6$ were a polynomial of (homogeneous) degree $8$ in the six frequencies, then,
since the oracle eliminates legs $1$ and $6$ by the rational solve
$\omega_1,\omega_6=(\text{deg-2 poly})/S_F$ with $S_F:=\omega_2+\omega_3+\omega_4+\omega_5$,
every monomial $\omega_1^a\omega_6^b(\cdots)$ has $a+b\le 8$, so
$A_6\cdot S_F^{8}$ would be a polynomial in the free frequencies.
**It is not:** on a 1-D slice that stays inside a *single chamber with all six
same-type orderings $a_i\!\lessgtr\!a_j$, $b_i\!\lessgtr\!b_j$ fixed too*,
$A_6\cdot S_F^{p}$ fails to be a polynomial of degree $8+p$ for **every** $p=1,\dots,14$
(exact rational test, `code/findp_slice.py`-style; mismatches at all held-out points).
A 4-variable confirmation: in the largest full chamber (700 exact points),
$A_6\cdot S_F^{p}$ is linearly inconsistent with the degree-$8+p$ monomial basis for
$p=1,\dots,6$. The denominator power needed therefore exceeds $8$, which is impossible
for a polynomial — hence $A_6$ is rational. (`code/rationalfit.py`, `code/symslice.py`.)

### Why it's still pole-free (consistent with round-1)
Driving onto every factorization channel $D_S=\omega_S^2/|k_S|-g\to0$, $A_6$ stays
finite and $A_6\,D_S\to0$ — **including** the channel $S=\{2,4,5\}$ (one minus + two
plus, $k_S>0$), for which the naive factorization argument predicts a *two-minus
$\times$ two-minus* (both non-vanishing) residue. It is still removable: the $n=4$
two-minus sub-amplitude residue cancels on-shell (`code/polehunt.py`,
$A_6/i\to3039$, $A_6 D_S\to0$ linearly). So the only zeros of the reduced denominator
are at $S_F=0$ (the spurious leg-elimination point, $\omega_6\to\infty$) and at
**complex / sum-of-squares loci** that never reach the real manifold. No physical poles.

---

## 2. Chamber wall arrangement (mixed momentum-subset walls)

The genuine mixed momentum-subset walls $k_S=\sum_{i\in S}\sigma_i\omega_i^2=0$ for
$n=6$ three-minus reduce to exactly **two orbit types** (full derivation: all other
mixed subsets have a fixed sign on-shell — see below):

$$
\textbf{(1=1)}\quad \omega_i^2=\omega_j^2\ \ (i\in M,\,j\in P),\qquad\text{9 walls},
$$
$$
\textbf{(1=2)}\quad \omega_i^2=\omega_j^2+\omega_k^2\ \ (i\in M,\,\{j,k\}\subset P),
\qquad\text{9 walls}.
$$

(Equivalently, by $k_S=-k_{S^c}$, the (1=2) wall $a_i=b_j+b_k$ is the same hyperplane as
$b_r=a_p+a_q$.) **Why no others:** for a mixed $S$ with $m$ minus and $\ell$ plus legs,
$k_S=-\sum_S a+\sum_S b$. On-shell the types $(1,3),(3,1),(2,3),(3,2)$ are sign-definite
(e.g. $(1,3)$: $-a_i+Q=a_j+a_k>0$), and $(2,2)\equiv(1,1)$, $(2,1)\equiv(1,2)$ by
complement. So only $(1,1)$ and $(1,2)$ wall. (`code/chambers_n6.py`.)

### Realizable chambers
A $\ge1.5\times10^6$-point exact scan of the resonant manifold finds **336 distinct
sign patterns** of the 18 wall functions, falling into **12 chamber types** under the
symmetry $S_3(\text{minus})\times S_3(\text{plus})\times\mathbb Z_2(\text{swap})$.
Each type is certified realizable by an interior rational point
(`code/chambers_n6.py`, `charct` characterization). Representative descriptors
(sorted $a$'s and $b$'s, and $\#\{a_i>b_j\}$, $\#\{a_i>b_j+b_k\}$) are tabulated in
`claims.yaml` (`s1_r2_*`). No analogue of the $n=5$ "chamber D unrealizable" pruning
removes a whole symmetry type here; all 12 occur.

> **Caveat for the closed form (NEW):** the *mixed* walls above are **not** the whole
> story. $A_6$ is not a single rational function on a mixed chamber — within one mixed
> chamber it still changes form across the **same-type orderings** ($\omega_i^2=\omega_j^2$
> within a triple and $\omega_i^2=\omega_j^2$-type comparisons), exactly as the $n=5$
> "$\min$" produced a $b_4^2=b_5^2$ breakpoint. The full non-analyticity locus is the
> mixed walls **together with** same-type comparisons; the rational pieces live on this
> finer arrangement.

---

## 3. What is ruled out for the closed form

- **Polynomial spline / box-spline of the $\omega_i^2$:** impossible — $A_6$ is rational
  (§1). Any truncated-power/box-spline object is piecewise *polynomial*.
- **Double-subset resonance spline**
  $\sum_{S\subseteq M,T\subseteq P}(-1)^{|S|+|T|}(\sigma_T-\sigma_S)_+^{p}$: ruled out by
  degree. The double (order-3 $\times$ order-3) difference annihilates exponent $p=4$
  exactly ($\equiv0$ at every tested point), so the only degree-8 ($2p=8$) member
  vanishes; $p=3$ gives a non-zero degree-6 object $B_3$ but $A_6\ne(\text{deg-2})\cdot
  B_3$ (exact, fails per chamber). The $n=5$ amplitude is itself *not* a double-subset
  spline (its threshold is the asymmetric $\min$). (`code/cand.py`, `/tmp` probes.)
- **$A_6/i=$ polynomial in $\{a_i,b_j\}$, or in $\{a_i,b_j,S\}$, or $\{\dots,S,\prod\omega\}$**
  ($S:=(\sum_M\omega)^2=(\sum_P\omega)^2$): all fail exactly, per *raw* chamber
  (`code/rawfit.py`, `code/modfit.py`). Consistent with §1 (it isn't polynomial at all).

---

## 4. Recommended next step (rational ansatz)

The closed form is **rational**. Build the ansatz as
$$
A_6 \;=\; i\,2^{5}g^{-3}\;\frac{\mathcal N(\{\omega_i\})}{\prod_{S\in\mathcal D}|k_S|}\,,
$$
where $\mathcal D$ is the set of **non-cancelling momentum magnitudes** from the BG
kernels (the same-type sums $\omega_i^2+\omega_j^2$, etc., which are sums of squares and
never vanish), and $\mathcal N$ is a polynomial (piecewise, on the mixed $\cup$ same-type
arrangement). Concretely: extract $\mathcal D$ from the reduced denominator (the
symbolic single-slice computation `code/symslice.py` gives the exact uncancelled
denominator; its complex-root / sum-of-squares factors are the survivors), then fit
$\mathcal N$ per chamber. This is the corrected target for round 3.
