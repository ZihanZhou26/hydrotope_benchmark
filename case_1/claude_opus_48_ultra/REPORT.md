# Closed-form $A_n$ in the two‑minus sector — results

**Author:** Claude Opus 4.8 (ultracode run). Worked only from `prompt.md` and `OnShellBG.m`; all
numbers below come from code I wrote and ran in this folder (no external lookup).

---

## 0. TL;DR

Working entirely from the Berends–Giele code, I found that the on‑shell tree amplitude in the
two‑minus sector is **purely imaginary**, **homogeneous of degree $2(n-2)$** in the frequencies, and
— the central structural result —

> **$A_n$ is a *bounded, piecewise* function of the frequencies, not a single rational function.**

It depends on the **signs** of the $\omega_i$ and on the **type‑1 channel momenta**
$|k_{\mu j}| = |\omega_j^2-\omega_\mu^2|$ (absolute values), i.e. it has a genuine chamber structure.
This is the analytic counterpart of the comment in `OnShellBG.m`: *"No regularization … no poles in
this sector."* The propagator poles cancel, leaving a bounded amplitude whose only non‑analyticity is
the $|k_S|$ in the BG propagators/kernels.

Two exact closed forms result (both verified to machine precision = **0 error**, exact rational
arithmetic, against `BGAmplitude`):

**(1) Principal‑regime formula — general $n\ge4$, sign‑robust.**
Whenever the smallest $|\omega_i|$ belongs to one of the two $\sigma=-1$ legs (legs 1,2) — the regime
of *every* example in `OnShellBG.m` —
$$\boxed{\,A_n \;=\; i\,\cdot\,2^{\,n-1}\;\omega_1\,\omega_2\,\bigl(\min(\omega_1^2,\omega_2^2)\bigr)^{\,n-3}\,}$$

**(2) Complete $n=5$ formula — valid in *every* chamber (arbitrary kinematics).**
$$A_5 \;=\; i\Bigl[\,P_0(\omega)\;+\!\!\sum_{\mu\in\{1,2\}}\sum_{j\in\{3,4,5\}}\!\! P_{\mu j}(\omega)\,\bigl|\omega_j^2-\omega_\mu^2\bigr|\Bigr]$$
with explicit polynomials $P_0,P_{\mu j}$ given in §5. The $|\omega_j^2-\omega_\mu^2|$ are exactly the
type‑1 sub‑channel momenta; the absolute values are *essential* and carry the chamber dependence.

---

## 1. Setup and a fast, exact evaluator

`OnShellBG.m` defines exact interaction kernels `EKernel`/`FKernel`, the vertex, the propagator
$-i/(\omega_S^2/|k_S|-g)$, and the BG recursion. I re‑typed the definitions into `bg_defs.m`
(definitions only) and ported the whole recursion to exact **Gaussian‑rational** Python in `bg.py`
(class `BG`, `amp_two_minus`). Because every input frequency is rational and $|k_i|=\omega_i^2$, all
arithmetic is exact.

`bg.py` reproduces the Mathematica `BGAmplitude` **exactly** (a representative cross‑check):

| $n$ | free freqs | `BGAmplitude` (Mathematica) | `bg.py` |
|----|------------|------------------------------|---------|
| 5 | $\{2,5/2,3\}$ | $-2304\,i$ | $-2304\,i$ |
| 5 | $\{3/2,11/5,7/3\}$ | $-\tfrac{404919}{905}\,i$ | $-\tfrac{404919}{905}\,i$ |
| 6 | $\{3/2,2,5/2,3\}$ | $-\tfrac{11907}{4}\,i$ | $-\tfrac{11907}{4}\,i$ |
| 6 | $\{2,3,7/2,11/3\}$ | $-\tfrac{6588416}{219}\,i$ | $-\tfrac{6588416}{219}\,i$ |

(One bug I fixed during the port: the Mathematica `FKernel[n≥4]` divides the whole result by
`|p2|`; the port matched only after restoring that `/qp2`.) The kinematic solver `MakeKinematics`
needs $\sigma_1+\sigma_n=0$, which holds in the two‑minus sector ($\sigma_1=-1,\sigma_n=+1$).

**Homogeneity.** Scaling $\omega\to\lambda\omega$ gives $A_n\to\lambda^{2(n-2)}A_n$ (measured: $n=5\!:\!\lambda^6$,
$n=6\!:\!\lambda^8$, $n=7\!:\!\lambda^{10}$). So $\deg A_n = 2(n-2)$.

**On‑shell identities.** Conservation $\sum\omega_i=0$, $\sum\sigma_i\omega_i^2=0$ give, for the two minus legs,
$$\omega_1+\omega_2=-\!\!\sum_{j\ge3}\omega_j=-e_1(x),\qquad
  \omega_1\omega_2=\sum_{3\le a<b}\omega_a\omega_b=e_2(x),\qquad
  \omega_1^2+\omega_2^2=\sum_{j\ge3}\omega_j^2,$$
where $x=(\omega_3,\dots,\omega_n)$ are the plus frequencies. (Verified numerically.)

---

## 2. The amplitude is piecewise — *not* a single rational function

This contradicts the naive "single rational function with poles" expectation, but it is what
`BGAmplitude` actually computes (confirmed by the reference Mathematica itself), and it matches the
code's own comment that there are **no poles in this sector**.

**Evidence / proof.**
* A direct scan over thousands of points shows $|A_n|/(\text{scale})^{2(n-2)}$ stays bounded ($\lesssim 3$
  for $n=5$) — i.e. **no real poles**; the propagator "poles" $\omega_S^2=|k_S|$ cancel in the full sum.
* In the open region where the smallest $|\omega|$ is a minus leg, the amplitude equals
  $2^{n-1}\omega_1\omega_2(\min(\omega_1^2,\omega_2^2))^{n-3}$ **exactly** (e.g. $112/112$ tested points at
  $n=5$, $420/420$ at $n=6$, $0$ failures). On the sub‑region $\{\omega_1^2<\omega_2^2\}$ this is the
  *rational* function $2^{n-1}\omega_1\omega_2\,\omega_1^{2(n-3)}$, and on $\{\omega_2^2<\omega_1^2\}$ it is the
  *different* rational function $2^{n-1}\omega_1\omega_2\,\omega_2^{2(n-3)}$. A single rational function
  cannot equal two different ones on two open sets — hence **no single rational function exists**.
* Concretely the value jumps form across the wall $|\omega_j|=|\omega_\mu|$ (a minus/plus pair): e.g. for
  $n=5$ with $\omega_2=2,\omega_3=5/2$, $A_5/(\omega_1\omega_2)=256$ for $\omega_4>2$ but $207,112,\dots$ for
  $\omega_4=\tfrac32,1,\dots$. The transition is governed by $\operatorname{sign}(k_{24})=\operatorname{sign}(\omega_4^2-\omega_2^2)$.

The chambers are the sign patterns of the composite momenta $k_S=\sum_{i\in S}\sigma_i\omega_i^2$. Only the
**type‑1** channels (one $\sigma=-1$ leg + some $\sigma=+1$ legs) have $k_S$ of indefinite sign; the
all‑plus channels have $k_S=\sum\omega_i^2>0$ identically. Hence only type‑1 $|k_S|$ produce chambers,
and they are exactly what appears in the complete formula (§5).

---

## 3. Principal‑regime closed form (general $n$)

**Statement.** If $\min_i\omega_i^2$ is attained by a $\sigma=-1$ leg (leg 1 or 2), then for all $n\ge4$
$$A_n = i\,2^{\,n-1}\,\omega_1\omega_2\,\bigl(\min(\omega_1^2,\omega_2^2)\bigr)^{n-3}.$$
Equivalently, if the legs are sorted so that the softest minus leg has frequency $\omega_{\min}$,
$A_n = i\,2^{n-1}\,\omega_1\omega_2\,\omega_{\min}^{\,2(n-3)}$. This is the regime of every `MakeKinematics`
example in `OnShellBG.m` (positive, comparable free frequencies make a $\sigma=-1$ leg the softest).

**How it was found.** Reconstructing $A_5$ along slices and fitting showed $A_5/(\omega_1\omega_2)$ is a
perfect power $(2\,\omega_{\min})^{2(n-3)}$ in this regime; generalising the $2^{n-1}$ prefactor across
$n=5,6$ ($16,32$) gives $2^{n-1}$, and the exponent $2(n-3)$ follows from homogeneity.

**Verification (exact, 0 error).**  (filled in §6.)

---

## 4. $n=4$: the degenerate case

For $n=4$ the two‑minus manifold is rigid: solving the two conservation laws forces the four
frequencies into two opposite pairs, $\omega=(-b,\,a,\,b,\,-a)$. Then the sub‑channels $\{1,3\}$ and
$\{2,4\}$ have $\omega_S=k_S=0$ simultaneously, so `BGAmplitude` returns `Indeterminate` (a $0/0$ in the
propagator) — it cannot be evaluated directly at $n=4$. Approaching the manifold from off‑shell
($\omega\to(-b,a,b+\varepsilon,-a+\varepsilon)$, $\varepsilon\to0$) the limit is finite and equals the formula:

| $(a,b)$ | predicted $A_4/i = 8\,\omega_1\omega_2\min(\omega_1^2,\omega_2^2)$ | BG limit $\varepsilon\to0$ |
|---|---|---|
| $(2,3)$ | $-192$ | $\to-191.978\ (\varepsilon=10^{-4})$ |
| $(3,5)$ | $-1080$ | $\to-1079.92$ |
| $(2,5)$ | $-320$ | $\to-319.96$ |
| $(4,3)$ | $-864$ | $\to-863.99$ |

(Here $n-3=1$, so $A_4=i\,2^{3}\omega_1\omega_2\min(\omega_1^2,\omega_2^2)$.)

---

## 5. Complete $n=5$ formula (every chamber)

A single global expression that reproduces `BGAmplitude` for **arbitrary** $n=5$ kinematics is
$$A_5=i\Bigl[\,P_0+\sum_{\mu\in\{1,2\}}\sum_{j\in\{3,4,5\}}P_{\mu j}\,\bigl|\omega_j^2-\omega_\mu^2\bigr|\Bigr].$$
With $E_1,E_2,E_3,P_4$ the elementary‑symmetric / power‑sum functions of the **plus** legs
$(\omega_3,\omega_4,\omega_5)$ (note $E_2=\omega_1\omega_2$),
$$P_0 = 8\,E_2\,\bigl(P_4-4E_1E_3\bigr),\qquad P_4=\omega_3^4+\omega_4^4+\omega_5^4 .$$
For each pair $(\mu,j)$ write $\mu'$ = the *other* minus leg and let $e_1,e_2$ be the elementary
symmetric functions of the *two plus legs other than $j$*; then
$$P_{\mu j}=8\bigl(e_1^3\omega_{\mu'}+2e_1e_2\,\omega_j-e_1e_2\,\omega_{\mu'}-e_1\omega_{\mu'}^3+2e_2^2+e_2\omega_{\mu'}^2\bigr).$$
(These coefficients are one exact representative of a fit that is unique on the resonant manifold; the
evaluator `closed_form.A5_complete` loads the exact rationals from `kabs_sol5.pkl`.)

**Verification.** Evaluated at **800 random points** (random signs/magnitudes, spanning all chambers —
the softest leg was observed to be each of the five legs): **0 mismatches, max relative error $0$.**

The same ansatz with only single $|k_{\mu j}|$ factors is *inconsistent* for $n\ge6$: there the formula
needs **products** of $|k_S|$ (multilinear in the type‑1 momenta), reflecting the $(n-3)$ nested soft
channels — e.g. when the $n-3$ softest legs are all $\sigma=+1$ one finds the clean limit
$A_n=i\,2^{n-1}(n-3)!\,\omega_1\omega_2\prod_{\text{softest }n-3\text{ plus}}\omega_j^2$.

---

## 6. Numerical evidence

All comparisons use exact rational arithmetic; "0 error" means the formula and `BGAmplitude` are the
*same rational number*. (Tables below are generated by `verify_*.py` / `closed_form.py`.)

### 6a. Explicit per‑point checks (exact rational; `rel.err = 0`)

| n | free freqs | `BGAmplitude` | closed form | rel.err | which |
|---|------------|-------------|-------------|---------|-------|
| 4 | $(-3,2,3,-2)$ rigid | `Indeterminate` (degenerate) | $-192\,i$ | $\to0$ (limit) | principal |
| 5 | $\{2,5/2,3\}$ | $-2304\,i$ | $-2304\,i$ | $0$ | complete |
| 5 | $\{2,5/2,3/2\}$ | $-\tfrac{5589}{4}\,i$ | $-\tfrac{5589}{4}\,i$ | $0$ | complete |
| 5 | $\{2,5/2,1\}$ | $-\tfrac{7504}{11}\,i$ | $-\tfrac{7504}{11}\,i$ | $0$ | complete |
| 5 | $\{-3,5/2,7/2\}$ | $+\tfrac{925}{72}\,i$ | $+\tfrac{925}{72}\,i$ | $0$ | complete |
| 5 | $\{7/3,-11/5,13/4\}$ | $-\tfrac{24803269216}{448147875}\,i$ | (same) | $0$ | complete |
| 6 | $\{3/2,2,5/2,3\}$ | $-\tfrac{11907}{4}\,i$ | $-\tfrac{11907}{4}\,i$ | $0$ | principal |
| 6 | $\{2,3,7/2,11/3\}$ | $-\tfrac{6588416}{219}\,i$ | (same) | $0$ | principal |
| 7 | $\{3/2,2,5/2,3,7/2\}$ | $-\tfrac{7302393}{400}\,i$ | (same) | $0$ | principal |
| 8 | $\{3/2,2,5/2,3,7/2,4\}$ | $-\tfrac{37496115}{352}\,i$ | $-\tfrac{37496115}{352}\,i$ | $0$ | principal |
| 8 | $\{2,5/2,3,7/2,4,9/2\}$ | $-\tfrac{115343360}{39}\,i$ | $-\tfrac{115343360}{39}\,i$ | $0$ | principal |

The $n=5$ rows deliberately include three *different chambers* (softest leg = $\omega_2$, then a plus
leg, with the value changing form) and a point with a sign‑flipped minus leg — the **complete** $n=5$
formula nails all of them.

### 6b. Bulk random verification (exact, all 0 error)

| test | points | result |
|------|--------|--------|
| $n=5$ **complete** formula, fully random (signs+magnitudes, all chambers) | 800 | 800/800 exact, max rel.err $=0$ |
| $n=5$ principal formula, random points with softest = minus leg | 400 | 400/400 exact |
| $n=6$ principal formula, random signs, softest = minus | 40 (+420 systematic) | all exact |
| $n=7$ principal formula, random signs, softest = minus | 8 | 8/8 exact |
| $n=4$ principal formula vs off‑shell $\varepsilon\to0$ limit | 4 | all converge to formula |


---

## 7. Reasoning — how this was obtained

1. **Exact fast backend.** Ported BG to exact Gaussian‑rational Python, validated against Mathematica.
2. **Scaling & invariants.** Found $\deg A_n=2(n-2)$ and the minus‑leg identities $\omega_1\omega_2=e_2(x)$, $\omega_1+\omega_2=-e_1(x)$.
3. **Attempted a single rational fit** (denominator = products of channel factors). It failed at every
   denominator degree — the symptom that $A_n$ is *not* rational.
4. **Discovered the chamber structure** by chamber‑resolved symbolic BG and by tracking where the value
   "jumps form"; identified the controlling quantities as the type‑1 $|k_{\mu j}|=|\omega_j^2-\omega_\mu^2|$
   (confirmed by the code's "no poles" comment — the amplitude is bounded/piecewise, not pole‑carrying).
5. **Clean principal‑regime law** $2^{n-1}\omega_1\omega_2(\min(\omega_1^2,\omega_2^2))^{n-3}$ extracted from
   slice fits and verified across $n$.
6. **Complete $n=5$ law**: fit $A=P_0+\sum P_{\mu j}|k_{\mu j}|$ over many chambers; the linear system is
   consistent (a *single* polynomial $P_0$ and family $P_{\mu j}$ reproduce every chamber), giving an
   explicit global closed form, verified on 800 random points.

### Files
`bg_defs.m` (re‑typed defs), `bg.py` (exact evaluator), `closed_form.py` (formula evaluator),
`fit_kabs.py`/`fit_kabs_gen.py` (global $|k|$ fit), `verify_*.py` (checks), `*.pkl` (exact fit data).
