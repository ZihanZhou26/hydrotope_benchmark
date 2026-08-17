# n=6 three-minus, round 4: the MINIMAL denominator is a single cubic invariant, and the spline jump structure

**student-1, round 4 (2026-06-26).** All exact-rational against my own copy of
`bg.cpp` (`bots/student-1/code/bg.cpp`, byte-identical to the shared oracle; shared
one untouched). One-command checks: `python3 verify_min_denom.py` and
`python3 jumps_smoothness.py`.

## 0. Headline

The round-3 team result was
$$A_6=i\,2^5g^{-3}\,\frac{N_{17}}{D_9},\qquad D_9=\prod_{i\in\{1,2,3\}}\prod_{j\in\{4,5,6\}}(\omega_i+\omega_j)\ (\deg 9),\quad N_{17}=\text{spline, }\deg 17,$$
with $D_9$ asserted **minimal** (PI post_009, student-2 s2_010). **Two corrections /
simplifications, both proven & verified exactly:**

1. **On the resonant manifold $D_9$ is a perfect cube of a single cubic invariant:**
$$\boxed{\;\prod_{i\in M,\,j\in P}(\omega_i+\omega_j)\;=\;(\omega_1\omega_2\omega_3+\omega_4\omega_5\omega_6)^3\;=\;(e_3^-+e_3^+)^3\;}$$
   (PROVEN below; symbolic resultant + 8/8 random points).

2. **The true minimal denominator is that cubic to the FIRST power**, not the third:
$$\boxed{\;A_6=i\,2^5g^{-3}\,\frac{N(\omega)}{\omega_1\omega_2\omega_3+\omega_4\omega_5\omega_6}\;,\qquad N=\text{piecewise polynomial (spline), }\deg 11\;}$$
   ($N$ is $S_3(\text{minus})\times S_3(\text{plus})\times Z_2$-symmetric and **odd** under
   $\omega\to-\omega$). $D_9$ is a correct *sufficient* denominator but over-clears by
   $(e_3^-+e_3^+)^2$; the team's degree-17 numerator is my degree-11 $N$ times
   $(e_3^-+e_3^+)^2$. Verified: $A_6\cdot(e_3^-+e_3^+)$ is a genuine polynomial (pure-sumFree
   reconstruction) on **8 slices across 4 chamber types**, and the pole order of $A_6$ at
   $(e_3^-+e_3^+)=0$ is exactly **1**.

## 1. The invariant reduction (why everything lives in 4 variables)

$A_6$ is $S_3(\text{minus})\times S_3(\text{plus})\times Z_2$-symmetric (student-2 s2_003,
PI-reverified). On the manifold the two conservation laws fix the symmetric invariants:
$$\sum_i\omega_i=0\ \Rightarrow\ e_1^-=-e_1^+,\qquad \sum_i\sigma_i\omega_i^2=0\ \Rightarrow\ e_2^-=e_2^+,$$
($e_k^{\pm}$ = elementary symmetric of the minus/plus triple). So everything symmetric
reduces to **four invariants**
$$e_1:=e_1^+,\quad e_2:=e_2^+,\quad e_3^-:=\omega_1\omega_2\omega_3,\quad e_3^+:=\omega_4\omega_5\omega_6,$$
matching the 4 dimensions of the manifold. The $Z_2$ swap acts as
$(e_1,e_2,e_3^-,e_3^+)\mapsto(-e_1,e_2,e_3^+,e_3^-)$. (This makes student-2's
$e_2(\text{minus})=e_2(\text{plus})$ identity, s2_008, the second conservation law.)

## 2. Proof that $D_9=(e_3^-+e_3^+)^3$

Let the plus "sum-cubic" be $Q(x):=\prod_{j\in P}(x+\omega_j)=x^3+e_1^+x^2+e_2^+x+e_3^+$, and
the minus cubic $p_-(x):=\prod_{i\in M}(x-\omega_i)=x^3-e_1^-x^2+e_2^-x-e_3^-$. On the manifold
$-e_1^-=e_1^+=e_1$ and $e_2^-=e_2^+=e_2$, so
$$p_-(x)=x^3+e_1x^2+e_2x-e_3^-,\qquad Q(x)=x^3+e_1x^2+e_2x+e_3^+,$$
i.e. **$Q$ and $p_-$ share every coefficient except the constant term**, hence
$$Q(x)-p_-(x)=e_3^-+e_3^+\quad(\text{a constant}).$$
For each minus root $\omega_i$ ($p_-(\omega_i)=0$) this gives $Q(\omega_i)=e_3^-+e_3^+$, and
$$D_9=\prod_{i\in M}\prod_{j\in P}(\omega_i+\omega_j)=\prod_{i\in M}Q(\omega_i)=(e_3^-+e_3^+)^3.\qquad\blacksquare$$
(Confirmed symbolically by `sp.resultant(p_-,Q)` $=(e_3^-+e_3^+)^3$ and numerically 8/8 in
`inv.py`.)

This also explains the team's **"entangled matching poles"** (student-2 s2_011): if a
single mixed pair vanishes, $\omega_i+\omega_j=0$, then $Q(\omega_i)=0$, so $e_3^-+e_3^+=0$,
so $Q(\omega_{i'})=0$ for *all* minus roots — every minus leg is matched to a plus leg.
$\{D_9=0\}=\{e_3^-+e_3^+=0\}$ is a **single irreducible codim-1 hypersurface** (the
perfect-matching locus), not 9 independent walls.

## 3. The minimal denominator is $(e_3^-+e_3^+)^1$

On a 1-D chamber-interior slice, exact Padé-over-$\mathbb Q$ reconstruction of $A_6(t)$ gives
(e.g. anchor chamber $(\omega_2,\omega_3,\omega_4,\omega_5)=(2,3,5,7)$, vary $\omega_4$)
$$A_6(t)=\frac{N(t)}{(t+7)(t+8)(t+17)/952},\quad (e_3^-+e_3^+)(t)=\frac{-90(t+7)(t+8)}{t+17},\quad \text{sumFree}(t)=t+17.$$
The $(e_3^-+e_3^+)$-numerator $(t+7)(t+8)$ appears in $A_6$'s reduced denominator to the
**first power** (the $(t+17)$ is the leg-$1,6$ solve artifact, $=\text{sumFree}$). Hence the
pole order is 1.

Equivalently: $A_6\cdot(e_3^-+e_3^+)$ reconstructs to a **pure power of sumFree** (no
$(\omega_i\pm\omega_j)$ factor) — the signature of a genuine 6-frequency polynomial on the
manifold. Verified on 8 slices across 4 chamber types (`verify_min_denom.py` part A); the
pole multiplicity is exactly 1 (part D), with the $n$-control that $A_6$ itself is *not*
polynomial (team result, so the pole order is $\ge1$). Therefore the minimal denominator is
exactly $(e_3^-+e_3^+)$ and $N:=A_6(e_3^-+e_3^+)/(i2^5g^{-3})$ has degree $8+3=11$.

(The earlier "$D_9$ minimal" argument was correct *in the free 6-variable polynomial ring*
— the $S_3\times S_3$-orbit of one linear factor $(\omega_i+\omega_j)$ is all nine. But on
the manifold those nine factors are not independent: their product is $(e_3^-+e_3^+)^3$, and
$A_6$ has only a simple pole there.)

## 4. The numerator is a genuine spline — cross-wall jump structure

$N$ kinks across the **mixed** walls (the same-type orderings $\omega_4=\omega_5$ are
analytic — PI post_009; confirmed, since $A_6$ is symmetric and smooth across them). Two wall
orbits (s1_004), with **different** jump exponents (`jumps_smoothness.py`, exact, clean
single-wall crossings):

| wall orbit | locus | wall function $k_S$ | jump $N_A-N_B$ | smoothness |
|---|---|---|---|---|
| **(1=1)** | $\omega_i=\omega_j$ ($i$ minus, $j$ plus) | $k_{ij}=\omega_j^2-\omega_i^2$ | $\propto (k_{ij})^1$ | $C^0$ (first-deriv kink) |
| **(1=2)** | $\omega_i^2=\omega_j^2+\omega_k^2$ | $k_{ijk}=\omega_i^2-\omega_j^2-\omega_k^2$ | $\propto (k_{ijk})^3$ | $C^2$ (cubic kink) |

This **confirms** the team's qualitative reading ((1=2) "cubic kink" — s2_004) and **pins**
the exponents exactly. Note the kink at a (1=1) wall sits on the *difference* branch
$(\omega_i-\omega_j)$, while the denominator factor is the *sum* branch $(\omega_i+\omega_j)$
— the two roots of the BG kernel magnitude $|k_{ij}|=|\omega_i-\omega_j|\,|\omega_i+\omega_j|$;
the difference branch survives in the numerator (source of the kink), the sum branch is the
shielded denominator pole.

Contrast with $n=5$, where every wall has the *uniform* exponent $n-3=2$ (the $(\cdot)_+^2$
B-spline). At $n=6$ the exponents **split** (1 and 3). This rules out a single-exponent
truncated-power / box-spline ansatz for $N$ and is the central structural constraint for the
closed form.

## 5. Per-chamber $N$ (deliverable 1) and status of the closed form

- **Per chamber $N$ is a genuine degree-11 polynomial in the six frequencies** (verified
  pure-sumFree, §3, across chambers). Each chamber-piece is a *non-symmetric* polynomial in
  the legs (the legs are algebraic — cubic-root — functions of the symmetric invariants), so
  no single chamber-piece is a rational function of $(e_1,e_2,e_3^-,e_3^+)$; only the global
  (symmetric) $N$ is invariant-valued, and it is a **spline** in invariant space with kinks on
  the images of the mixed walls.
- **Closed form for $N$: still OPEN.** The bottom-up data now fixes: the exact (minimal)
  denominator $(e_3^-+e_3^+)$; $\deg N=11$; full $S_3\wr Z_2$ symmetry; oddness; the two wall
  orbits and their jump exponents (1 and 3); the $|\omega_i-\omega_j|$ kink mechanism from the
  BG kernel. The split exponents say $N$ is **not** a uniform-exponent multivariate
  truncated power; a faithful ansatz must reproduce a $(k_{ij})^1$ jump at (1=1) and a
  $(k_{ijk})^3$ jump at (1=2).

## 6. All-$n$ remark

For general $n$ (three minus legs $\{1,2,3\}$, $n-3$ plus legs),
$$\text{Den}_n=\prod_{i\in M,\,j\in P}(\omega_i+\omega_j)=\prod_{i\in M}Q_n(\omega_i)=\mathrm{Res}\big(p_-,Q_n\big),\quad Q_n(x)=\prod_{j\in P}(x+\omega_j).$$
The collapse $\text{Den}_6=(e_3^-+e_3^+)^3$ is **special to $n=6$** (equal-size triples make
$Q_6$ and $p_-$ share all but the constant coefficient). For $n=5$, $\text{Den}_5=\prod_{i\in
M}Q_5(\omega_i)$ with $Q_5$ quadratic — degree 6, no collapse, and it divides $N_5$ (the $n=5$
law is polynomial). For $n=7$, $\text{Den}_7$ is a degree-12 resultant with no perfect-power
collapse. The minimal-denominator power for $n\neq6$ is left open here.

## Reproduce
```
cd bots/student-1/code
g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp     # if not built
python3 inv.py                  # D9 = (e3m+e3p)^3 (symbolic resultant + numeric)
python3 verify_min_denom.py     # (P) cube identity; (A) minimal denom; (D) pole order = 1
python3 jumps_smoothness.py     # (1=1) jump order 1, (1=2) jump order 3
```
