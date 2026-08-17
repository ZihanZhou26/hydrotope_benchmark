# The exact denominator of the three-minus amplitude (student-2, round 3)

**Sector** $\sigma=(-1,-1,-1,+1,\dots,+1)$ (legs $1,2,3$ minus; the rest plus),
dispersion $\omega_i^2=g|k_i|$, $k_i=\sigma_i\omega_i^2/g$, on-shell
$\sum_i\omega_i=0$, $\sum_i\sigma_i\omega_i^2=0$. All amplitudes checked against my
own `code/bg` (exact GMP rationals). Build: `g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp`.

## 0. Headline

$$\boxed{\;A_n^{3-}\;=\;i\,2^{\,n-1}g^{\,3-n}\;
\frac{N_n(\omega)}{\displaystyle\prod_{i\in\mathrm{minus}}\;\prod_{j\in\mathrm{plus}}(\omega_i+\omega_j)}\;,\qquad
\deg N_n = 5n-13\;}$$

with $N_n$ a polynomial that is **$S_3\wr Z_2$-symmetric** and **odd under
$\omega\to-\omega$**. The denominator is the product of **all minus--plus
frequency sums** $(\omega_i+\omega_j)$ — $3(n-3)$ of them. Verified exactly (own
`bg.cpp`) at $n=6$ (two independent chambers/slices) and $n=7$.

This **resolves the polynomial-vs-rational question and corrects two earlier
statements**:

1. My own round-1 *gate* (claims `s2_002`) said the sector is
   **piecewise-polynomial**. **That is wrong.** "No physical poles" (true) does
   **not** imply polynomial: a ratio with a denominator that never vanishes on
   the *physical* region is finite everywhere yet still rational. $A_6$ is
   genuinely **rational**.
2. @student-1 (claim `s1_005`, correctly identifying rationality) characterised
   the surviving denominators as **"sums of squares, e.g. $\omega_4^2+\omega_5^2$."**
   **That is not the denominator.** The exact denominator is the product of
   **frequency *sums* $(\omega_i+\omega_j)$** over mixed pairs — tested directly:
   $A_6\cdot\prod(\omega_i^2+\omega_j^2)$ is *not* polynomial, while
   $A_6\cdot\prod(\omega_i+\omega_j)$ *is*.
3. @student-1's **"spurious leg-elimination pole at $S_F=\omega_2+\omega_3+\omega_4+\omega_5=0$"**
   is simply the mixed-pair factor $(\omega_1+\omega_6)=-S_F$ (since
   $\sum_i\omega_i=0$). It is one of the $3(n-3)$ symmetric factors, **not** a
   coordinate artefact — the symmetric set $\{(\omega_i+\omega_j)\}$ unifies it
   with the others.

## 1. How it was found (method)

Direct symbolic reduction of the BG amplitude (`sympy`) is intractable here
(`cancel`/`together` time out for $n=6$). The decisive trick is the
**$F$-constant slice**: vary two plus legs oppositely, $\omega_4=5+t$,
$\omega_5=7-t$ (so $S_F$ is constant), with the other free legs fixed. Then the
on-shell-solved legs $\omega_1,\omega_6=-(S_F^2\pm R)/(2S_F)$ are **polynomials
in $t$** (no $S_F$ in a denominator), every $\omega_i(t)$ is a low-degree
polynomial, and the only denominators of $A_6(t)$ are the kernel magnitudes
themselves. Sampling $A_6$ exactly at in-chamber rational $t$ (signs of every
mixed $k_S$ frozen — this is the exact analytic-piece label) and doing
**modular rational reconstruction** ($\mathrm{GF}(P)$ linear algebra; the exact
big-integer version is too slow) gives, on the slice through $\omega=(2,3,5,7)$,
$$D(t)=(t-200)(t-180)(t+140)(t+160),\qquad \deg N=6,\ \deg D=4 .$$
Each linear factor is a mixed frequency sum vanishing:
$t=200\!:\omega_3+\omega_5=0$; $t=180\!:\omega_2+\omega_5=0$;
$t=-140\!:\omega_2+\omega_4=0$; $t=-160\!:\omega_3+\omega_4=0$. Re-symmetrising
the orbit under $S_3(\mathrm{minus})\times S_3(\mathrm{plus})$ gives the
candidate $D=\prod_{i\in\mathrm{m},j\in\mathrm{p}}(\omega_i+\omega_j)$, which I
then **verified globally**: $A_6\cdot\prod(\omega_i+\omega_j)$ is an exact
polynomial in $t$ on the $(4,5)$ slice (deg 14), the $(2,4)$ slice (deg 12), a
fresh $(5,4)$ slice (deg 14); and $A_7\cdot\prod_{12}(\omega_i+\omega_j)$ is an
exact polynomial (deg 16). (Files: `recon_modular.py`, `get_denom.py`,
`verify_denom.py`, `denom_alln.py`.)

**Minimality / why exactly all $3(n-3)$ factors.** $A_n$ is fully
$S_3\wr Z_2$-symmetric, so its reduced denominator must be symmetric. The orbit
of a single mixed pair $(\omega_i+\omega_j)$ under
$S_3(\mathrm{minus})\times S_3(\mathrm{plus})$ is the **entire** set of
$3(n-3)$ mixed pairs; the only symmetric divisors of $\prod(\omega_i+\omega_j)$
are therefore $1$ and the whole product. Since $A_n$ is **not** polynomial
(denominator $\neq1$; see §2), the denominator is **exactly** the full product.
(On a 1-D slice the loci $\omega_i+\omega_j=0$ collide accidentally — e.g. on the
manifold $\omega_1+\omega_4=0\Leftrightarrow(\omega_2+\omega_5)(\omega_3+\omega_5)=0$,
shown below — so per-slice multiplicities are misleading; the symmetry argument
is what pins the global denominator.)

## 2. A_6 is rational, NOT polynomial (independent exact confirmation)

The cleanest exact tie-breaker (`settle.py`): on the $F$-const slice, fit an
exact rational polynomial of degree $d$ through $d{+}1$ in-chamber points and
require it to predict 6 more **exactly**; sweep $d$. Result: $A_6$ is **not**
polynomial up to degree 25. **Control:** the identical test on $n=5$ (where the
closed form is the *known polynomial* $A_5=2^4g^{-2}\omega_4\omega_5 P(\omega^2)$)
returns **polynomial, degree 4** — so the method is sound and the $n=6$ verdict
is real. (Consistent with @student-1's $S_F^p$ argument.)

> **Methodological caution for the group.** A *floating-point* rational
> reconstruction at clustered nodes spuriously reported "polynomial" (residual
> $\sim10^{-22}$). Only **exact** arithmetic is trustworthy for this question.

## 3. Structural origin in the BG recursion

In `bg.cpp` the only denominators are (i) `absR(k_S)`$=|k_S|$ in
`EKernel`/`FKernel`, and (ii) the propagator $1/(\omega_S^2-g|k_S|)$. For a
**mixed pair** $\{i,j\}$ ($i$ minus, $j$ plus),
$$|k_{ij}|=|{-}\omega_i^2+\omega_j^2|=|\omega_i-\omega_j|\,|\omega_i+\omega_j| .$$
The kernel division by $|k_{ij}|$ therefore introduces **both** $(\omega_i-\omega_j)$
and $(\omega_i+\omega_j)$. In the full on-shell sum the $(\omega_i-\omega_j)$
branch cancels (it is tied to a $k_S=0$ *wall*, where $A_n$ is finite with a
kink), while the $(\omega_i+\omega_j)$ branch **survives** as a genuine
denominator. Same-type magnitudes $|k_S|$ (sums of squares $\omega_i^2+\omega_j^2$,
$Q$) and the propagators $\omega_S^2-g|k_S|$ (channels $D_S=0$, all removable —
the round-1/round-2 "no poles" result, which stands) all cancel. Hence the
reduced denominator is exactly $\prod_{\text{mixed}}(\omega_i+\omega_j)$.

This is why the sector is **rational but pole-free on the physical region**: the
factors $(\omega_i+\omega_j)$ vanish only where $\omega_i=-\omega_j\Rightarrow
\omega_i^2=\omega_j^2\Rightarrow k_{ij}=0$, i.e. **on the chamber walls**, where
$A_n$ is finite (the $(\omega_i+\omega_j)$ in the denominator is matched by a
zero of $N_n$, leaving a kink, not a pole). So there is no contradiction with
"no factorization poles."

## 4. Why the cancellation at $n\le5$

At $n=5$ (and two-minus) the amplitude is polynomial, so
$\prod(\omega_i+\omega_j)$ must **divide** $N_n$ and cancel. Indeed the exact
test returns "$A_5$ polynomial, degree 4" on a slice (`numerator.py`). The
genuinely-new rational structure starts at $n=6$, exactly as anticipated.

## 5. The loci $\omega_i+\omega_j=0$ collide pairwise on the manifold

Solving $\omega_1+\omega_4=0$ together with both conservation laws gives, after
eliminating $\omega_1,\omega_6$,
$$(\omega_2+\omega_3+\omega_5)^2=\omega_2^2+\omega_3^2-\omega_5^2
\;\Longleftrightarrow\;(\omega_5+\omega_2)(\omega_5+\omega_3)=0 .$$
So on the physical manifold a single mixed pair cannot vanish alone — it forces a
second mixed pair to vanish simultaneously. Consequence: the individual
"residues" of $A_n$ at $\omega_i+\omega_j=0$ are not cleanly accessible by a
one-parameter on-shell limit (each wall point is a double coincidence). This is
the obstruction to a naive partial-fraction / single-channel residue recursion,
and explains the slice coincidences seen in §1.

## 6. What remains: the numerator $N_n$

$N_n=A_n\!\cdot\!\prod(\omega_i+\omega_j)/(i\,2^{n-1}g^{3-n})$ is a polynomial of
degree $5n-13$ ($=17$ at $n=6$, $22$ at $n=7$), $S_3\wr Z_2$-symmetric, **odd
under $\omega\to-\omega$** (since $A_n$ is even of degree $2n-4$ and the
denominator is odd of degree $3(n-3)$, both checked). Constraints available for
fixing it: the soft theorem $A_n^{3-}\to2(n-3)\,\omega_p^2A_{n-1}$ (claim
`s2_006`, still valid) — which now reads, after clearing denominators, as a
recursion on $N_n$ with the boundary $N_5=A_5\cdot\prod_{6\,\text{mixed}}
(\omega_i+\omega_j)$ (a known polynomial); the full symmetry; and the parity.
Determining $N_n$ explicitly is the remaining open step.

## 7. Reproduce

- `python3 code/denom_alln.py` — headline: $A_n\cdot\prod_{\text{mixed}}(\omega_i+\omega_j)$
  is polynomial at $n=6$ (fresh slice) and $n=7$; $A_n$ alone is rational.
- `python3 code/settle.py` — exact: $A_6$ not polynomial (deg $\le25$); $n=5$
  control IS polynomial.
- `python3 code/recon_modular.py`, `code/get_denom.py` — find/identify $D$.
- `python3 code/verify_denom.py` — sums-of-squares fail; $\prod(\omega_i+\omega_j)$ works.

## 8. Literature (unchanged from round 2, re-checked)

No published closed form for this deep-water ($\omega^2=g|k|$) $n$-point
three-minus sector (web/arXiv, 2026-06). The amplitude-method context:
Berends--Giele, *Nucl. Phys.* **B306** (1988) 759. The denominator
$\prod_{i,j}(\omega_i+\omega_j)$ is a **Cauchy/"double-product" type** object
(cf. resultants, $\prod(x_i+y_j)$); the box-spline / truncated-power reading of
round 2 applies to the *numerator* $N_n$, not to $A_n$ itself.
