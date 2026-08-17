# Closed form for $A_n$ in the two‑minus sector

**Sector:** $\sigma=(-1,-1,+1,\dots,+1)$ — legs $1,2$ carry $\sigma=-1$, legs $3,\dots,n$ carry $\sigma=+1$.
**Setup:** deep‑water dispersion $\omega_i^2=g\,|k_i|$, $k_i=\sigma_i\omega_i^2/g$; all momenta incoming, on the resonant manifold $\sum_i\omega_i=0$, $\sum_i\sigma_i\omega_i^2=0$.

---

## 1. The formula

Let

$$q_S \;=\; \sum_{j\in S}\omega_j^2 ,\qquad (x)_+=\max(x,0),$$

and let $S$ range over subsets of the **plus legs** $\{3,\dots,n\}$. Then for **all $n\ge 4$** and **arbitrary kinematics in the sector**,

$$\boxed{\;A_n \;=\; -\,i\,\frac{2^{\,n-1}}{g^{\,n-3}}\;\omega_1\,\omega_2
\sum_{S\subseteq\{3,\dots,n\}} (-1)^{|S|+1}\,\Big[\big(\omega_2^{2}-q_S\big)_+\Big]^{\,n-3}\;}$$

The truncated power $\big[(\omega_2^2-q_S)_+\big]^{n-3}$ means: a subset $S$ contributes $(\omega_2^2-q_S)^{n-3}$ only when $\omega_2^2>q_S$, and $0$ otherwise. (At $g=1$, the convention used throughout the benchmark, the prefactor $g^{-(n-3)}=1$.)

The amplitude is **purely imaginary**: $A_n=-i\,P_n$ with $P_n$ a real polynomial in the frequencies.

**Equivalent $g$‑free statement.** Since $|k_j|=\omega_j^2/g$, the factors of $g$ cancel inside the bracket:
$$A_n=-\,i\,2^{\,n-1}\,\omega_1\omega_2\sum_{S}(-1)^{|S|+1}\Big[\big(|k_2|-\textstyle\sum_{j\in S}|k_j|\big)_+\Big]^{n-3}.$$

**Symmetry / well‑definedness.** $A_n$ is Bose‑symmetric: invariant under exchanging the two minus legs $1\leftrightarrow2$ and under permuting the plus legs $3,\dots,n$. Although the threshold above is written with $\omega_2^2$, one may use $\omega_1^2$ instead and get the identical value. This is forced by the identity
$$\sum_{S\subseteq\{3,\dots,n\}}(-1)^{|S|}\,(x-q_S)^{\,n-3}=0\qquad(\text{identically in }x),$$
which holds because there are $n-2$ plus legs but the power is only $n-3$ (an $(n-2)$‑fold finite difference annihilates a degree‑$(n-3)$ polynomial). Together with $\omega_1^2+\omega_2^2=q_{\{3..n\}}$ on shell, this makes the truncated sums built from $\omega_1^2$ and from $\omega_2^2$ agree.

---

## 2. Chamber decomposition

$A_n$ is a **continuous, piecewise homogeneous polynomial** of degree $2(n-2)$ in the $\omega_i$.

* **Walls.** The kinematic space is cut by the subset‑sum hypersurfaces
  $$\omega_2^{2}=q_S=\sum_{j\in S}\omega_j^{2},\qquad S\subseteq\{3,\dots,n\}.$$
  These are exactly the loci where an internal Berends–Giele momentum $k_{T}=\sum_{i\in T}\sigma_i\omega_i^2$ changes sign — the only place the absolute values in the BG kernels act.

* **Chambers.** A chamber is a region where the **active set**
  $$\mathcal A(\omega)=\{\,S\subseteq\{3,\dots,n\}:\ \omega_2^{2}>q_S\,\}$$
  is constant. Because $q_{S'}\le q_S$ when $S'\subseteq S$, every active set is a **lower set** (order ideal) of the Boolean lattice; and the full set $\{3,\dots,n\}$ is never active (it would require $\omega_1^2<0$).

* **Polynomial on a chamber.** On the chamber with active set $\mathcal A$,
  $$A_n=-\,i\,\frac{2^{\,n-1}}{g^{\,n-3}}\,\omega_1\omega_2\!\!\sum_{S\in\mathcal A}(-1)^{|S|+1}\big(\omega_2^{2}-q_S\big)^{n-3},$$
  a single homogeneous polynomial of degree $2(n-2)$. Adjacent chambers (across a wall $\omega_2^2=q_S$) differ by the term $(-1)^{|S|+1}(\omega_2^2-q_S)^{n-3}$, which vanishes to order $n-3$ on the wall — hence the function and its first $n-4$ derivatives are continuous (a spline).

### Worked examples (chamber polynomials)

* **$\omega_2$ is the smallest‑magnitude leg** ($\mathcal A=\{\varnothing\}$): only $S=\varnothing$ is active, giving a pure monomial
  $$A_n=\;i\,\frac{2^{\,n-1}}{g^{\,n-3}}\;\omega_1\,\omega_2^{\,2n-5}\qquad\Big(\tfrac{A_n}{-i}=-2^{\,n-1}\omega_1\omega_2^{\,2n-5}\ \text{at }g=1\Big).$$

* **$n=5$, $\omega_3^2<\omega_2^2<\omega_4^2,\omega_5^2$** ($\mathcal A=\{\varnothing,\{3\}\}$):
  $$\tfrac{A_5}{-i}=16\,\omega_1\omega_2\big[-(\omega_2^2)^2+(\omega_2^2-\omega_3^2)^2\big]=-16\,\omega_1\omega_2\,\omega_3^2\,(2\omega_2^2-\omega_3^2).$$

* **$n=5$, $\omega_3^2+\omega_4^2<\omega_2^2<\omega_5^2$** ($\mathcal A=\{\varnothing,\{3\},\{4\},\{3,4\}\}$):
  $$\tfrac{A_5}{-i}=16\,\omega_1\omega_2\big[-(\omega_2^2)^2+(\omega_2^2-\omega_3^2)^2+(\omega_2^2-\omega_4^2)^2-(\omega_2^2-\omega_3^2-\omega_4^2)^2\big]=-32\,\omega_1\omega_2\,\omega_3^2\,\omega_4^2.$$

---

## 3. The special case $n=4$

For $n=4$ the two conservation laws force the on‑shell configuration onto a wall: every two‑minus point has $\omega_1^2=\omega_3^2$ and $\omega_2^2=\omega_4^2$ (up to relabeling), so one internal momentum vanishes and `BGAmplitude` returns the indeterminate form $0\cdot\infty$. The formula, being a continuous spline, has a well‑defined value there, and it equals the limit of `BGAmplitude` as the singular locus is approached. With $\omega_2$ the smaller minus leg,
$$A_4=\;i\,2^{3}\,\omega_1\omega_2^{3}=8\,i\,\omega_1\omega_2^{3}\qquad\big(\tfrac{A_4}{-i}=-8\,\omega_1\omega_2^{3}\big).$$
This was checked against the exact symbolic limit $\lim_{d\to0}\texttt{BGAmplitude}$ and against an explicit numerical limit (see §4).

---

## 4. Numerical evidence

All checks use `OnShellBG.m` (`BGAmplitude`) with $g=1$, **exact rational arithmetic**. For $n=5,6,7$ the formula reproduces `BGAmplitude` with **identically zero residual** (far beyond the $10^{-10}$ relative‑error requirement). For $n=4$ the BG value is the limit toward the (degenerate) on‑shell point.

**Summary of checks (formula vs `BGAmplitude`, exact arithmetic, $g=1$):**

| $n$ | points tested | distinct chambers | mismatches | how (saved scripts) |
|----|----|----|----|----|
| 4 | 5 | (degenerate locus) | **0** | exact symbolic $\lim_{d\to0}$ of BG = formula (`final_verify.wl`) |
| 5 | 100+ | 8+ | **0** | chamber sweep + 76‑pt stress + 21 pts incl. $\omega_1$‑smallest (`final_verify.wl`,`verify1.wl`) |
| 6 | 80+ | 18+ | **0** | chamber sweep (sizes 1–8) + 38‑pt stress + `verify2.wl` (35 pts/11 chambers) |
| 7 | 45+ | 14+ | **0** | chamber sweep (sizes up to 16) + 7‑pt stress + `verify2.wl` (26 pts/12 chambers) |

Every tested point matched with **exactly zero residual** (rational arithmetic), i.e. relative error $0\le10^{-10}$, in every chamber. (`final_verify.wl` calls the slow `BGAmplitude` on one representative per distinct chamber, so it covers chambers efficiently; `verify1.wl`/`verify2.wl` add hundreds of random points and explicit $\omega_1$‑smallest configurations.)

**Sample of distinct chambers (residual $A_{\text{formula}}-A_{\text{BG}}=0$ in all):**

*n=4 (exact symbolic limit of BG → formula):*
```
(a,b)=(1,3)  w=(-3,1,3,-1)   A_formula=-24 i    lim BG=-24 i     match
(a,b)=(2,5)  w=(-5,2,5,-2)   A_formula=-320 i   lim BG=-320 i    match
(a,b)=(3,7)  w=(-7,3,7,-3)   A_formula=-1512 i  lim BG=-1512 i   match
(a,b)=(5,2)  w=(-2,5,2,-5)   A_formula=-320 i   lim BG=-320 i    match   (a>b)
```
*n=5 (4 chambers, plus-legs {5,7}, sweeping ω₂; active-set size grows 1→4):*
```
w=(-9.31, 1, 5, 7, -3.69)    |A|active=1   A_BG=-1936 i/13      resid 0
w=(-10.06, 6, 5, 7, -7.94)   |A|active=2   A_BG=-3402800 i/3    resid 0
w=(-10.25, 8, 5, 7, -9.75)   |A|active=3   A_BG=-3083200 i      resid 0
w=(-10.33, 9, 5, 7, -10.67)  |A|active=4   A_BG=-3645600 i      resid 0
```
*n=6 (8 chambers on one sweep, active-set sizes 1…8): all resid 0.*
*n=7 (12 chambers on one sweep, active-set sizes {1,2,3,4,5,6,8,10,12,13,15,16} — chamber polynomials with up to 16 truncated-power terms): all resid 0.*

One representative `BGAmplitude` value per chamber was checked against the formula; e.g. for n=7 the verified set spans tiny chambers (1 active term, $A_n=-2^{n-1}\omega_1\omega_2^{2n-5}$) up to 16-term chamber polynomials, all reproduced with zero residual. Full transcript: `final_verify.out`.


**Reproduce:** `wolframscript -file final_verify.wl` (full table + random stress test); `python3 two_minus_amplitude.py` (formula self‑test against stored BG values).

---

## 5. How the conjecture was reached

1. **Probing BG.** Generated amplitudes over a range of $n$ and kinematics. Found $A_n$ purely imaginary, homogeneous of degree $2(n-2)$, and Bose‑symmetric under $S_2\times S_{n-2}$ (verified by permuting legs, which preserves both conservation laws).

2. **A symmetric polynomial fit fails.** Fitting $A_n/(-i)$ to a homogeneous polynomial in the elementary symmetric functions of the plus legs failed badly (residuals $\sim10^{11}$). This showed the function is **not** a single polynomial: it is *piecewise*. The only absolute values in the BG code act on internal subset‑momenta $k_T=\sum_{i\in T}\sigma_i\omega_i^2$, so the chamber walls are the sign changes of the $k_T$ — i.e. the subset‑sum surfaces $\omega_2^2=q_S$.

3. **Exact 1‑D reconstruction.** Computing $A_n$ along lines (vary one frequency, fix the rest) and reconstructing the exact rational function showed that within each chamber $A_n$ is a clean polynomial. In the chamber where $\omega_2$ is smallest it is the monomial $-2^{n-1}\omega_1\omega_2^{2n-5}$ (verified for $n=5,6,7$).

4. **Wall‑crossing → spline.** Differencing the polynomials of chambers adjacent across the wall $\omega_2^2=q_S$ gave exactly $(-1)^{|S|+1}(\omega_2^2-q_S)^{\,n-3}$ (times the universal $2^{n-1}\omega_1\omega_2$). Summing these truncated powers over all subsets yields the boxed formula. The signs and the power $n-3$ make it the unique continuous spline matching the smallest‑leg monomial.

5. **Validation.** The exponent $n-3$ and coefficient $2^{n-1}$ were confirmed against BG for $n=5,6,7$ at hundreds of points across all reachable chambers (exact zero residual); the $\omega_1^2/\omega_2^2$ interchangeability was confirmed and explained by the finite‑difference identity; $n=4$ was confirmed by the exact symbolic limit; and the $g$‑scaling $A_n\propto g^{-(n-3)}$ was confirmed.

---

## 6. Files

| file | contents |
|------|----------|
| `RESULTS.md` | this report |
| `two_minus_amplitude.py` | self‑contained Python implementation of the closed form + self‑test |
| `formula.wl` | Wolfram implementation of the closed form (one function) |
| `final_verify.wl` | full verification: chamber table (n=5,6,7), random stress test, exact n=4 limit |
| `final_verify.out` | saved output of the above |
| `bg_defs.wl`, `lib.wl` | BG definitions (copied from `OnShellBG.m`) + helpers used by the scripts |
| `probe*.wl`, `verify*.wl`, `fit*.wl`, `n4limit.wl` | the exploratory scripts that led to the result |
