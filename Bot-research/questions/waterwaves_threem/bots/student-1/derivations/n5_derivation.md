# The $n=5$ three-minus closed form, its derivation, and its chamber decomposition

**Author:** student-1  **Task:** `r1-student-1`  **Date (UTC):** 2026-06-26T18:43:14

**Sector:** $\sigma=(-1,-1,-1,+1,+1)$ — legs $1,2,3$ are the minus legs, legs $4,5$ the plus legs.
Dispersion $\omega_i^2=g|k_i|$, momenta $k_i=\sigma_i\omega_i^2/g$. On-shell both conservation
laws hold:
$$\textstyle\sum_i\omega_i=0,\qquad \sum_i\sigma_i\omega_i^2=0\ \Longleftrightarrow\ \omega_1^2+\omega_2^2+\omega_3^2=\omega_4^2+\omega_5^2 .$$

---

## 1. The result

$$\boxed{\;A_5 \;=\; i\,2^{4}\,g^{-2}\,\omega_4\,\omega_5
\sum_{S\subseteq\{1,2,3\}}(-1)^{|S|}\Big(\beta^2-\sum_{j\in S}\omega_j^2\Big)_+^{2},
\qquad \beta=\min\!\big(|\omega_4|,|\omega_5|\big),\ (x)_+=\max(x,0).\;}$$

It is purely imaginary, **continuous, piecewise-homogeneous of degree $6$** in the frequencies
(times $g^{-2}$), and **has no poles** in this sector — exactly the two-minus "truncated power"
behaviour. Verified to **exact rational agreement at 24/24** non-degenerate kinematic points
(`code/verify_n5.py`), independent of the PI's check, against my own copy of `bg.cpp`.

---

## 2. Derivation via the plus/minus swap (clean relabeling)

**Inputs.** Two facts from `question.md`:

* **(item 2) Two-minus closed form.** For $\sigma=(-1,-1,+1,\dots,+1)$ with minus legs $\{a,b\}$
  and plus legs the rest,
  $$A_n=i\,2^{\,n-1}g^{\,3-n}\,\omega_a\,\omega_b\!\!\sum_{S\subseteq\text{plus}}(-1)^{|S|}\Big(B^2-\sum_{j\in S}\omega_j^2\Big)_+^{\,n-3},\quad B=\min(|\omega_a|,|\omega_b|).$$
  The amplitude is totally symmetric under permuting like-sign legs, so this holds for *any*
  choice of the two minus legs $\{a,b\}$ (not only $\{1,2\}$).

* **(item 3) Plus/minus swap.** Flipping every momentum $k_i\to-k_i$ (equivalently
  $\sigma_i\to-\sigma_i$) at **fixed frequencies** preserves both conservation laws and the
  dispersion ($|k_i|$ unchanged), so $A_n$ is invariant. This maps the $k$-minus sector to the
  $(n-k)$-minus sector.

**Step 1 — apply the swap.** Start in three-minus at $n=5$: $\sigma=(-,-,-,+,+)$ on legs
$(1,2,3,4,5)$. The all-sign flip gives $\sigma'=(+,+,+,-,-)$: a **two-minus** configuration
whose **minus legs are $4,5$** and whose plus legs are $1,2,3$ — at the *same* frequencies
$\omega_1,\dots,\omega_5$. By item 3,
$$A_5^{(3\text{-minus})}(\omega_1,\dots,\omega_5)=A_5^{(2\text{-minus, minus legs }4,5)}(\omega_1,\dots,\omega_5).$$

**Step 2 — apply the two-minus law to the relabeled configuration.** In item 2 take
$\{a,b\}=\{4,5\}$ (the minus legs of the swapped config) and $\text{plus}=\{1,2,3\}$, with $n=5$:
$$A_5 = i\,2^{4}\,g^{-2}\,\omega_4\,\omega_5\sum_{S\subseteq\{1,2,3\}}(-1)^{|S|}\Big(\beta^2-\sum_{j\in S}\omega_j^2\Big)_+^{2},\qquad \beta=\min(|\omega_4|,|\omega_5|).$$
This is the boxed formula. The leg map under the swap is

| two-minus law symbol | maps to (here) |
|---|---|
| minus leg $a$, freq $\omega_a$ | leg $4$, $\omega_4$ |
| minus leg $b$, freq $\omega_b$ | leg $5$, $\omega_5$ |
| $B=\min(|\omega_a|,|\omega_b|)$ | $\beta=\min(|\omega_4|,|\omega_5|)$ |
| plus legs $\{3,\dots,n\}$ | $\{1,2,3\}$ |
| exponent $n-3=2$ | $2$ |
| prefactor $2^{\,n-1}g^{\,3-n}$ | $2^4 g^{-2}$ |

**Step 3 — direct oracle confirmation of the swap.** `code/verify_n5.py` also checks the swap at
the level of the oracle itself, in raw `--amp` mode: build the three-minus momenta
$K=(-\omega_1^2,-\omega_2^2,-\omega_3^2,+\omega_4^2,+\omega_5^2)$, evaluate $A_5$, then flip
$K\to-K$ and evaluate again. The two values are **identical** at every tested point — the swap
invariance is a property of `bg.cpp`, not an assumption.

---

## 3. Chamber decomposition (explicit, in the original frequencies)

Write $a=\omega_1^2,\ b=\omega_2^2,\ c=\omega_3^2$ (minus-leg squares) and
$m=\beta^2=\min(\omega_4^2,\omega_5^2)$. A subset $S\subseteq\{1,2,3\}$ is **active** iff
$\sum_{j\in S}\omega_j^2<m$; only active subsets contribute (the $(\cdot)_+$ truncates the rest).
Since subset sums are monotone, the active subsets form a **down-set**.

### 3.1 Chamber walls
The $(\cdot)_+$ terms switch on/off across the seven hypersurfaces
$$\sum_{j\in S}\omega_j^2=\beta^2=\min(\omega_4^2,\omega_5^2),\qquad \varnothing\neq S\subseteq\{1,2,3\},$$
i.e. $\ \omega_1^2=m,\ \omega_2^2=m,\ \omega_3^2=m,\ \omega_1^2+\omega_2^2=m,\ \omega_1^2+\omega_3^2=m,\ \omega_2^2+\omega_3^2=m,\ \omega_1^2+\omega_2^2+\omega_3^2=m,$
plus the **$\beta$-switch** $\omega_4^2=\omega_5^2$ (where $\beta$ changes which plus leg it tracks).

### 3.2 Which chambers are realizable (on-shell selection rule)
The momentum constraint $\omega_4^2+\omega_5^2=\omega_1^2+\omega_2^2+\omega_3^2=:T$ forces
$m=\min(\omega_4^2,\omega_5^2)\le T/2$. This kills three a-priori chambers:

* **Triple never active.** $m\le T/2<T=\omega_1^2+\omega_2^2+\omega_3^2$, so
  $\big(\beta^2-T\big)_+=0$ always. The $S=\{1,2,3\}$ term is identically zero on-shell.
* **At most one pair active.** If $\{i,j\}$ and $\{i,k\}$ were both active then
  $2\omega_i^2+\omega_j^2+\omega_k^2<2m\le T$, forcing $\omega_i^2<0$ — impossible. And if a pair
  $\{i,j\}$ is active, the third singleton $\{k\}$ is automatically **inactive**
  ($\omega_k^2=T-\omega_i^2-\omega_j^2>T-m\ge T/2\ge m$).
* **All three singletons never active simultaneously (chamber "D" is empty).** This requires
  $m>\max(\omega_1^2,\omega_2^2,\omega_3^2)$, i.e. $\min(\omega_4^2,\omega_5^2)>\max(\omega_i^2)$.
  Using $\omega_4\omega_5=\tfrac12\big((\sum\omega_i)^2-T\big)=\omega_1\omega_2+\omega_1\omega_3+\omega_2\omega_3=:e_2$
  and $\min(\omega_4^2,\omega_5^2)=\tfrac12\!\big(T-\sqrt{T^2-4e_2^2}\big)$, the condition reduces to
  $e_2^2>M(T-M)$ with $M=\max(\omega_i^2)$. On the manifold (reality of $\omega_4,\omega_5$,
  $\;\Leftrightarrow e_2\le T/2$) this **never holds**: maximizing
  $\min(\omega_4^2,\omega_5^2)-\max(\omega_i^2)$ over the whole manifold gives supremum $0$,
  attained only in the degenerate all-vanishing limit (dense scan $+$ multistart optimization,
  $>3\times10^6$ samples; max gap $\approx-4\times10^{-5}<0$). So **at least one minus singleton is
  always inactive.**

**Realizable chamber types** (up to permuting the symmetric minus legs $1,2,3$): $A,B,C,E$ only.

### 3.3 The closed form on each realizable chamber
Let $P:=i\,2^4 g^{-2}\,\omega_4\omega_5$ and $F:=A_5/P$.

| type | active down-set | condition on the $\omega_i^2$ | $F=A_5/P$ |
|---|---|---|---|
| **A** | $\{\varnothing\}$ | $\min(\omega_i^2)\ge m$ | $F=m^2=\beta^4$ |
| **B** | $\{\varnothing,\{i\}\}$ | one $\omega_i^2<m$, others $\ge m$ | $F=\omega_i^2\,(2m-\omega_i^2)$ |
| **C** | $\{\varnothing,\{i\},\{j\}\}$ | $\omega_i^2,\omega_j^2<m\le\omega_k^2$, $\ \omega_i^2+\omega_j^2\ge m$ | $F=2m(\omega_i^2+\omega_j^2)-m^2-\omega_i^4-\omega_j^4$ |
| **E** | $\{\varnothing,\{i\},\{j\},\{i,j\}\}$ | $\omega_i^2+\omega_j^2<m$ (then $\omega_k^2\ge m$) | $F=2\,\omega_i^2\,\omega_j^2$ |

The **E** form is the clean surprise: the $m$-dependence cancels completely and
$A_5=i\,2^5 g^{-2}\,\omega_4\omega_5\,\omega_i^2\,\omega_j^2$ for the active pair $\{i,j\}$.
Each row was verified to equal both the full $(\cdot)_+$ formula and the oracle, exactly, at
off-wall rational representatives (`code/verify_n5.py`; chamber column).

### 3.4 Continuity / smoothness across chamber walls
Each contribution $\big(\beta^2-\sum_S\omega_j^2\big)_+^{2}$ is a **squared** truncated power; since
$\tfrac{d}{dx}(x)_+^2=2(x)_+$ is continuous (and $=0$ at $x=0$), every term is $C^1$. Hence $A_5$ is
**$C^1$ across every chamber wall** — value and first derivative match, only the second derivative
jumps. Demonstrated in `code/walls_n5.py` (sweep $E\!\to\!C\!\to\!A$, no jumps; oracle$=$formula in
each chamber) and by the matching one-sided slopes at the $|k_S|$ walls below.

---

## 4. The $|k_S|=0$ walls (oracle SIGFPE) are finite, $C^1$ points — no poles

`bg.cpp` evaluates a propagator $\propto 1/\big(\omega_S^2/|k_S|-g\big)$ that divides by
$|k_S|$, $k_S=\sum_{i\in S}\sigma_i\omega_i^2$, for every subset $S$ of legs $\{2,3,4,5\}$ (leg $1$
is the reference leg and never carries a current). Where $k_S=0$ the oracle throws SIGFPE (exact)
or returns inf/nan (`--double`). These are **coordinate singularities of the BG representation, not
of $A_5$.** The non-degenerate ones reduce, using momentum conservation, to chamber walls:

$$
\begin{aligned}
S=\{2,4\}:&\ \omega_4^2=\omega_2^2, & S=\{2,5\}:&\ \omega_5^2=\omega_2^2,\\
S=\{3,4\}:&\ \omega_4^2=\omega_3^2, & S=\{3,5\}:&\ \omega_5^2=\omega_3^2,\\
S=\{2,3,4\}:&\ \omega_4^2=\omega_2^2+\omega_3^2\ \Leftrightarrow\ \omega_5^2=\omega_1^2, &
S=\{2,3,5\}:&\ \omega_5^2=\omega_2^2+\omega_3^2\ \Leftrightarrow\ \omega_4^2=\omega_1^2.
\end{aligned}
$$

(The remaining subsets force a vanishing frequency: $S=\{2,4,5\}\!\Rightarrow\omega_1^2+\omega_3^2=0$,
$S=\{3,4,5\}\!\Rightarrow\omega_1^2+\omega_2^2=0$, $S=\{2,3,4,5\}\!\Rightarrow\omega_1=0$.)
For example $\omega_4^2=\omega_2^2+\omega_3^2$ together with $\beta^2=\omega_4^2$ is the pair-$\{2,3\}$
wall, and together with $\beta^2=\omega_5^2$ is the singleton-$\{1\}$ wall (since then
$\omega_5^2=\omega_1^2$). So the oracle's blow-up locus lies **on chamber walls**, where $A_5$ is $C^1$.

**One-sided limit evidence** (`code/walls_n5.py`, exact rational mode). On the internal
3-particle channel $S=\{2,3,4\}$ (Pythagorean $3,4,5$, on-shell $\omega=(-6,3,4,5,-6)$):

| $\varepsilon$ | $A_5/i$ at $\omega_4=5-\varepsilon$ minus $A_{\rm wall}$ | at $\omega_4=5+\varepsilon$ minus $A_{\rm wall}$ |
|---|---|---|
| $10^{-1}$ | $+3.42\times10^{3}$ | $-2.96\times10^{3}$ |
| $10^{-2}$ | $+3.00\times10^{2}$ | $-2.96\times10^{2}$ |
| $10^{-3}$ | $+2.96\times10^{1}$ | $-2.96\times10^{1}$ |
| $10^{-5}$ | $+2.96\times10^{-1}$ | $-2.96\times10^{-1}$ |

with $A_{\rm wall}/i=-138240$ (the boxed formula evaluated *at* the wall — it never divides by
anything). Both one-sided limits $\to A_{\rm wall}$ **linearly** in $\varepsilon$ with **equal slopes
$\approx-2957$** (no $1/\varepsilon$ term): $A_5$ is finite and $C^1$ there. Same behaviour on the
two-particle channel $S=\{3,4\}$ ($\omega_4^2=\omega_3^2$). **Conclusion: $A_5$ has no factorization
pole** — the channel $\omega_S^2=g|k_S|$ that becomes a genuine pole at $n\ge6$ is regular at $n=5$,
consistent with the known two-minus structure and `question.md`'s expectation.

---

## 5. Reproducibility

* `code/bg.cpp` — my own copy of the oracle (the shared `bg.cpp` is never touched);
  built with `g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp`.
* `code/verify_n5.py` — builds `bg`, checks the formula vs `./bg` (exact rational) at 24 points
  (generic / fractional / non-generic, all realizable chambers), reports the exact residual at each;
  also checks the plus/minus swap directly via `--amp`. Result: **24/24 exact, swap holds.**
* `code/walls_n5.py` — chamber-wall continuity sweep and the $|k_S|=0$ one-sided-limit tables.

## 6. Sources
Self-contained: derived from `question.md` items 2 (two-minus law) and 3 (plus/minus swap), and
validated entirely against the `bg.cpp` Berends–Giele oracle (Berends & Giele, *Nucl. Phys.* **B306**
(1988) 759 — the recursion the oracle transcribes). No external numerical results were imported.
