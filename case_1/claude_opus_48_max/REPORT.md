# Closed-form $A_n$ in the two-minus sector — results

**Author:** Claude Opus 4.8 (max effort). **Date:** 2026-06-20.
**Sector:** $\sigma=(-1,-1,+1,\dots,+1)$ (legs 1,2 minus; legs $3..n$ plus), deep-water
dispersion $\omega_i^2=g|k_i|$, $k_i=\sigma_i\omega_i^2/g$, on-shell
$\sum_i\omega_i=0$, $\sum_i\sigma_i\omega_i^2=0$.

Only `prompt.md` and `OnShellBG.m` were read; no external sources, no web search.

---

## 1. The formula

Let the legs be ordered as in `MakeKinematics`: legs $1,2$ are the two minus legs
($\sigma=-1$), legs $3,\dots,n$ the plus legs. For the **standard sampling** —
positive free frequencies in ascending order $0<\omega_2<\omega_3<\dots<\omega_{n-1}$,
exactly the style used in every `OnShellBG.m` example — one has
$|\omega_2|=\min_i|\omega_i|$, and then

$$
\boxed{\,A_n \;=\; 2^{\,n-1}\,i\,\;\omega_1\,\omega_2^{\,2n-5}\,}\qquad (n\ge 4).
$$

Equivalently, eliminating the two solved frequencies $\omega_1,\omega_n$ through the
conservation laws gives the **ratio-of-polynomials form** in the free frequencies
$\omega_2,\dots,\omega_{n-1}$, with a single simple pole on the factorization-channel
sub-energy $S_1\equiv\sum_{j=2}^{n-1}\omega_j=-(\omega_1+\omega_n)$:

$$
\boxed{\,A_n \;=\; -\,2^{\,n-2}\,i\;
\frac{\;\omega_2^{\,2n-5}\,\Big(S_1^{2}-\omega_2^{2}+\sum_{i=3}^{n-1}\omega_i^{2}\Big)\;}
{S_1}\,},
\qquad S_1=\sum_{j=2}^{n-1}\omega_j .
$$

The two forms are identical on shell: the conservation laws give
$\omega_1=-\dfrac{S_1^{2}-\omega_2^{2}+\sum_{i=3}^{n-1}\omega_i^{2}}{2S_1}$, and
substituting it into the first form yields the second. The numerator does **not**
vanish at $S_1=0$ (for $n=5$ it reduces to $-\omega_3\omega_4\neq0$ there), so the pole
is genuine — the amplitude is a true rational function of the free frequencies, **not a
plain polynomial**, with a simple pole on the channel sub-energy $S_1$. The mass
dimension is $\deg A_n=2n-4$ (verified by scaling), consistent with both forms.

Both forms are homogeneous of degree $2n-4$ and symmetric under permutations of the
plus legs $3,\dots,n-1$ (the lone *free* minus leg $\omega_2$ carries the high power).

### Worked values

| $n$ | free $\omega$ | $A_n$ |
|----|----------------|-------|
| 4 | $\{3/2,5/2\}$ | $-\tfrac{135}{2}i$ |
| 5 | $\{2,3,5\}$ | $-3328\,i$ |
| 5 | $\{3/2,2,5/2\}$ | $-\tfrac{891}{2}i$ |
| 6 | $\{2,3,5,7\}$ | $-\tfrac{753664}{17}i$ |
| 7 | $\{2,3,5,7,11\}$ | $-\tfrac{4030464}{7}i$ |

---

## 2. Numerical evidence (agreement with `BGAmplitude`)

All checks use the **provided** `BGAmplitude` (exact rational arithmetic) as ground
truth, plus an **independent** Gaussian-rational re-implementation in Python
(`waterhedron_two_minus.py`) as a second, fully separate check.

* **`verify_main.m`** (Wolfram, the reference code): at random ascending-positive
  points the closed form equals `BGAmplitude` **exactly** (`Simplify[BG−formula]===0`,
  relative error $0$):

  | $n$ | #points | exact match | $\omega_2=\min|\omega|$ | max rel.err |
  |----|---------|-------------|--------------------------|-------------|
  | 5 | 30 | 30/30 | always | 0 |
  | 6 | 18 | 18/18 | always | 0 |
  | 7 | 8  | 8/8   | always | 0 |

  (Plus the explicit spot checks $n=4,5,6,7$ above; see `verify_main.out`.)

* **`verify.py`** (independent exact Gaussian-rational BG, a fully separate
  implementation): exact match $n=5$: 40/40, $n=6$: 20/20, $n=7$: 6/6 — see
  `verify.out`. This is a completely separate codebase agreeing with both the
  Wolfram reference and the closed form.

* **`verify_n4.m`** ($n=4$): the on-shell conditions force $\omega_1=-\omega_3$,
  $\omega_4=-\omega_2$, so $k_2+k_4=0$ and $\omega_2+\omega_4=0$ — the $\{2,4\}$
  sub-current propagator becomes a removable $0/0$ and a *direct* numeric
  `BGAmplitude` returns `Indeterminate`. Taking the (unique, finite) limit with the
  absolute values kept symbolic gives, for $0<\omega_2<\omega_3$,
  $A_4=-8i\,\omega_2^{3}\omega_3=8i\,\omega_1\omega_2^{3}$ — exactly the formula.

Reproduce: `wolframscript -file verify_main.m`, `wolframscript -file verify_n4.m`,
`python3 verify.py`, and the module self-test `python3 waterhedron_two_minus.py`.

---

## 3. How the formula was found (reasoning)

1. **Setup.** Re-implemented the two-minus kinematics on top of `OnShellBG.m`
   (`bg_core.m` holds the verbatim BG definitions) and confirmed
   $\deg A_n=2n-4$ by scaling $\omega_i\to\lambda\omega_i$.

2. **Sign-resolved symbolic amplitude.** The only obstruction to a rational form is the
   `Abs[k]` in the propagator/kernels: for external legs $|k_i|=\omega_i^2$ (clean), but
   internal momenta $k_S=\sum_{i\in S}\sigma_i\omega_i^2$ change sign across kinematic
   chambers. I computed the raw symbolic amplitude and resolved every `Abs[x]` by the
   sign of $x$ at a reference point (valid throughout that sign-chamber), then
   `Together`/`Factor`. For $n=5$, the chamber containing ascending-positive free
   frequencies gave
   $A_5=\dfrac{-16i\,\omega_2^5(\omega_2\omega_3+\omega_3^2+\omega_2\omega_4+\omega_3\omega_4+\omega_4^2)}{\omega_2+\omega_3+\omega_4}.$

3. **Constraint elimination → the monomial.** Using
   $\omega_2\omega_3+\omega_3^2+\omega_2\omega_4+\omega_3\omega_4+\omega_4^2
   =\omega_1(\omega_1+\omega_5)$ and $\omega_2+\omega_3+\omega_4=-(\omega_1+\omega_5)$
   on shell, this collapses to $A_5=16i\,\omega_1\omega_2^5$. The pattern
   $A_n=2^{n-1}i\,\omega_1\omega_2^{2n-5}$ was then conjectured and **verified directly**
   against `BGAmplitude` at $n=4,5,6,7$ (Section 2), including non-comparable points such
   as $\{2,3,100,101\}$. Re-introducing the solved $\omega_1$ gives the
   ratio-of-polynomials form of Section 1.

4. **Symmetry.** `BGAmplitude` is invariant under permutations of equal-$\sigma$ legs
   (checked explicitly), so the formula is symmetric in the plus legs; the high power
   sits on the smallest-magnitude (minus) leg $\omega_2$.

---

## 4. Important caveat — the amplitude is genuinely chamber-dependent

The benchmark hint asks for a single rational function "valid everywhere with no
piecewise/chamber decomposition." For this sector that is achievable **only within one
chamber**, for a precise reason:

* `BGAmplitude` is **piecewise**. The internal momenta $k_S$ flip sign across the
  sector, so the unregularized $|k_S|$ makes the amplitude a different rational function
  in each sign-chamber. Concretely $A_5(\omega_2,\omega_3,\omega_4)=16i\,\omega_1\omega_2^5$
  for $\{2,3,5\}$ but $16i\,\omega_1\omega_2\omega_3^2(2\omega_2^2-\omega_3^2)$ for
  $\{3,2,5\}$ — two *different* on-shell values ($-3328i$ vs $-16128i$), both confirmed
  against `BGAmplitude`.

* **No single global rational function exists** (identity theorem): the closed form
  equals the monomial $16i\,\omega_1\omega_2^5$ on the whole open chamber where
  $|\omega_2|=\min$, so any rational function agreeing with `BGAmplitude` there must *be*
  that monomial — which disagrees with `BGAmplitude` in other chambers.

The boxed formula is the closed form of the chamber selected by the standard
ascending-positive sampling (the chamber $|\omega_2|=\min_i|\omega_i|$), i.e. precisely
the regime of all `OnShellBG.m` examples and of the prompt's "generic, comparable
magnitude" guidance. For completeness the genuinely general $n=5$ rule (any chamber
fixed by the two smallest $|\omega|$) is implemented as `A_n5_general` in the Python
module and documented there.

---

## 5. Files

| file | contents |
|------|----------|
| `REPORT.md` | this report |
| `bg_core.m` | verbatim BG definitions from `OnShellBG.m` (sections I–V), loadable |
| `verify_main.m` | Wolfram verification of the formula vs `BGAmplitude`, $n=5,6,7$ |
| `verify_n4.m` | $n=4$ verification via the symbolic ($0/0$) limit |
| `waterhedron_two_minus.py` | independent BG port (float **and** exact Gaussian-rational), the closed forms, self-test |
| `verify.py` | independent exact/float verification sweep, $n=5..8$ |
| `waterhedron_two_minus_demo.ipynb` | runnable notebook (explore/tweak kinematics) |
| `probe*.m` | exploratory scripts used during the derivation |
