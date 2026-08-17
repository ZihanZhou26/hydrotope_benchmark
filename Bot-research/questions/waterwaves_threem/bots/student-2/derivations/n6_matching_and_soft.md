# Round 4 (student-2, top-down): soft recursion on $N_n$, and the matching-sum / Cauchy structure of $A_n$

**Sector** $\sigma=(-1,-1,-1,+1,\dots,+1)$, minus legs $M=\{1,2,3\}$, plus legs
$P=\{4,\dots,n\}$. Dispersion $\omega_i^2=g|k_i|$, on-shell $\sum_i\omega_i=0$,
$\sum_i\sigma_i\omega_i^2=0$. PI-verified baseline (post_009):
$$A_n^{3-}=i\,2^{\,n-1}g^{\,3-n}\,\frac{N_n(\omega)}{D_n(\omega)},\qquad
D_n=\prod_{i\in M}\prod_{j\in P}(\omega_i+\omega_j),$$
$N_n$ a continuous **spline** (deg $5n-13$, $S_3\wr Z_2$-symmetric, odd under
$\omega\to-\omega$). The open piece is the explicit $N_n$. All amplitudes below
checked against my own copy of `bg.cpp` (exact GMP rationals); one-command check
`python3 code/verify_r4.py`.

---

## 1. Soft-theorem recursion on the numerator $N_n$ (deliverable 1)

The soft theorem (claim `s2_006`, re-verified both legs this round, ratio
$=2(n-3)=6$ exactly at $n=6$):
$$A_n^{3-}\ \xrightarrow{\ \omega_p\to0\ }\ 2(n-3)\,\omega_p^2\,A_{n-1},$$
with $A_{n-1}$ **three-minus** if $p\in P$ and the known **two-minus** law if
$p\in M$. Multiplying by $D_n$ and using $A_m=i2^{m-1}g^{3-m}N_m/D_m$ turns this
into an explicit recursion on $N_n$, because the denominator factorises cleanly
in the soft limit:

**(a) Plus leg $p\to0$.** The three factors of $D_n$ containing $p$ are
$\prod_{i\in M}(\omega_i+\omega_p)\to\prod_{i\in M}\omega_i=\omega_1\omega_2\omega_3$,
so $D_n\to \omega_1\omega_2\omega_3\,D_{n-1}^{3-}$. Hence
$$\boxed{\ N_n\ \xrightarrow{\ \omega_p\to0\ }\
(n-3)\,g\,\omega_1\omega_2\omega_3\,\omega_p^{2}\,N_{n-1}^{3-}\ }$$
i.e. $N_n$ vanishes like $\omega_p^2$ and the coefficient of $\omega_p^2$ at
$\omega_p=0$ is $(n-3)g\,\omega_1\omega_2\omega_3\,N_{n-1}^{3-}$.

**(b) Minus leg $p\to0$** (remaining minus legs $a,b$). Now the three factors
$\prod_{j\in P}(\omega_p+\omega_j)\to\prod_{j\in P}\omega_j$, so
$D_n\to\big(\prod_{j\in P}\omega_j\big)\,D_{n-1}^{2-}$ with
$D_{n-1}^{2-}=\prod_{i\in\{a,b\}}\prod_{j\in P}(\omega_i+\omega_j)$, and
$$\boxed{\ N_n\ \xrightarrow{\ \omega_p\to0\ }\
(n-3)\,g\,\omega_p^{2}\,\omega_a\omega_b\;\Sigma\;
\Big(\prod_{j\in P}\omega_j\Big)\,D_{n-1}^{2-}\ },$$
$$\Sigma=\sum_{S\subseteq P}(-1)^{|S|}\big(\min(\omega_a^2,\omega_b^2)-\textstyle\sum_{j\in S}\omega_j^2\big)_+^{\,n-4}.$$

**Boundary.** $N_5=A_5\cdot\prod_{i\in M,\,j\in\{4,5\}}(\omega_i+\omega_j)/(i2^4g^{-2})$,
a known degree-12 polynomial (since $A_5$ is the polynomial three-minus law).

**Verification (exact, `verify_r4.py` part 1):** $\lim A_6/(i\,\omega_p^2)$ by
exact-rational Richardson, divided by the surviving amplitude evaluated at the
$\omega_p=0$ frequencies, equals $6$ for **both** a soft plus leg (surviving
$A_5^{3-}/i=-89424$, limit $-536544=6\cdot(-89424)$) and a soft minus leg
(surviving $A_5^{2-}/i=-365568$, limit $-2193408=6\cdot(-365568)$).

**What it gives / its limit.** The recursion fixes $N_n$ on every coordinate
hyperplane $\omega_p=0$ in terms of $N_{n-1}$, landing on the solved two-minus
sector. It does **not** determine $N_n$ uniquely: a polynomial is fixed by its
restrictions to all $\{\omega_p=0\}$ only up to a multiple of
$\prod_i\omega_i$. So the soft theorem + symmetry + degree leave a
$\big(\prod_i\omega_i\big)\times(\text{deg }5n-13-n\text{ symmetric})$ ambiguity
— a genuine reduction, but not a closed-form by itself.

---

## 2. The matching-sum / Cauchy structure of $A_n$ (deliverable 2)

The denominator $D_n=\prod_{i\in M,j\in P}(\omega_i+\omega_j)$ is a Cauchy /
"double-product" object. At $n=6$ ($|M|=|P|=3$) the natural $S_3\wr Z_2$-symmetric
objects with denominator exactly $D_9$ are the **permanent**
$\operatorname{perm}[1/(\omega_i+\omega_j)]=\sum_{\sigma\in S_3}\prod_i 1/(\omega_i+\omega_{\sigma(i)})$
and weighted variants $\operatorname{perm}[f(\omega_i,\omega_j)/(\omega_i+\omega_j)]$.

**New concrete finding — $A_6$ is a partial fraction over perfect matchings.**
On an $F$-constant slice $\omega_4=a+t,\ \omega_5=b-t$ (legs $1,6$ solved,
quadratic in $t$; one chamber), exact reconstruction gives
$$\frac{A_6}{i}\Big|_{\text{chamber}}=2^5g^{-3}\,
\frac{\text{(sextic in }t)}{\prod_{k}(t-r_k)},$$
and **every** denominator root $r_k$ is a **perfect-matching locus**
$\{\omega_i+\omega_{\sigma(i)}=0\ \forall i\in M\}$ for a bijection
$\sigma:M\to P$. Two clean chambers (`recon_num.py`, `residue.py`):
- $\omega=(2,3)$, slice $(5{+}t,7{-}t)$:
  $A_6/i\propto(55t^6{-}330t^5{+}1908t^4{-}5432t^3{-}1058129t^2{+}2126242t{+}43674470)/[(t{-}10)(t{-}9)(t{+}7)(t{+}8)]$;
- $\omega=(2,3)$, slice $(4{+}t,9{-}t)$:
  sextic$/[(t{-}12)(t{-}11)(t{+}6)(t{+}7)]$.

The reconstructed $D_9(t)$ on the slice is exactly these four linear forms
**cubed** (deg 12): each perfect matching uses three mixed pairs, and on the
slice those three collapse to one linear factor — the "$3{:}1$ over-clearing"
(student-1) and the **pairwise pole-collision** (claim `s2_011`). Consequently
$N_6=A_6D_9$ carries those factors **squared** ($3-1=2$), so per chamber
$$N_6 = (\text{sextic core})\times\!\!\prod_{\text{active matchings}}\!\!(\text{linear})^2 ,\qquad
A_6=\frac{\text{sextic}}{\prod_{\text{active matchings}}(\text{linear})}.$$

So $A_6$ has **simple poles exactly at the $3!=6$ perfect-matching loci**, with
clean rational residues (e.g. at $t=10$, matching $\{(1,4),(2,6),(3,5)\}$,
residue $3473280$). This is the matching-sum / Cauchy picture made explicit:
$A_n$ is a partial fraction over the matchings.

**Why the naive matching-residue sum does not directly close.** (i) *Degree.*
A pure $\operatorname{perm}[h/(\omega_i+\omega_j)]$ with a single kernel $h$ of
degree $d$ has homogeneous degree $3(d-1)$; matching $A_6$'s degree $8$ would
need $d=11/3\notin\mathbb Z$ — so $A_6$ is **not** a permanent of one kernel.
A global prefactor $\times$ permanent is needed. (ii) *Collisions.* At every
matching locus all three pairs vanish simultaneously (`s2_011`), so the
residues are entangled and not extractable by a one-parameter limit; the
slice-residues mix in the values of the other (frozen) matchings. (iii)
*Spline.* $A_6$ is a different rational function per chamber, so a single global
partial fraction cannot hold — the per-chamber residues differ (the poles are
shielded outside each chamber, `s1_009`). A genuine matching-sum closed form
must therefore have **piecewise (truncated-power) numerators**, consistent with
$N_n$ being a spline.

I computed $\operatorname{perm}[f/(\omega_i+\omega_j)]$ numerators for
$f\in\{1,\ \omega_i\omega_j,\ \omega_i^2+\omega_j^2,\ \omega_i^2\omega_j^2\}$
(`cauchy.py`): all are irreducible symmetric polynomials of degree
$6,9,?,?$ that do not, alone, reproduce $A_6$.

---

## 3. Box-spline reading of $N_n$ (deliverable 3)

`s2_008`'s $d=3$ truncated-power/box-spline lead was for $A_n$; since $A_n$ is
**rational** it cannot be a (polynomial) box spline, so the reading must target
the polynomial $N_n$. Two structural facts constrain it:

- **Parity.** $N_n$ is **odd** (deg $5n-13$). A box spline of the even knots
  $\{\omega_i^2\}$ is even, so $N_n=(\text{even, deg }2n-4)\times(\text{odd, deg }3(n-3))$,
  and the odd factor is forced to be the full $D_n$ (it carries the matching
  poles). Equivalently the box-spline content lives in the **even** factor
  $N_n/D_n=A_n/(i2^{n-1}g^{3-n})$ — which is exactly $A_n$, rational. So the box
  spline is **not** literally $N_n$; it is the per-chamber numerator core
  (the "sextic" of §2 at $n=6$) whose chamber-to-chamber differences are
  truncated powers.
- **Walls.** The breakpoints are the mixed $\{k_S=0\}$ walls (orbit types
  $\omega_i^2=\omega_j^2$ and $\omega_i^2=\omega_j^2+\omega_k^2$, `s1_004`),
  which in the variables $x_i=\omega_i^2$ are the hyperplane arrangement
  $\sum_{i\in S}\sigma_i x_i=0$ — precisely the singular cones of a $d=3$ box
  spline (degree $=n-3$ = the truncated-power exponent).

**Caution (verified).** A naive cross-wall jump extraction
$N_6^{A}(t)-N_6^{B}(t)$ on a tiny $F$-const slice does **not** cleanly factor
as $(k_S)^p$ (`jump.py`): over the slice range other (1=1) walls are crossed,
contaminating the single-chamber reconstruction (the jump fails to vanish at
the wall, violating continuity — a tell-tale of multi-wall contamination). The
clean per-wall truncated-power jumps require strict single-chamber tracking
(student-1's bottom-up task); I flag the hazard and defer to that pipeline.

---

## 4. All-$n$ status and tests (deliverable 4)

**Confirmed all-$n$ skeleton** (independent re-verification, `verify_r4.py`):
$A_n=i2^{n-1}g^{3-n}N_n/D_n$, $D_n=\prod_{i\in M,j\in P}(\omega_i+\omega_j)$;
$A_n\cdot D_n$ is an exact polynomial on a chamber slice at $n=6$ (deg 14) and
$n=7$ (deg 16). At $n>6$ the matchings are **injections** $M\hookrightarrow P$
(no perfect matching of all legs), and the poles sit on those injection loci.

**Tested candidate, ruled out (a clean negative).** The $n=5$ prefactor is
$\omega_4\omega_5=e_2(\text{plus})$, so a natural guess is that the swap-symmetric
$e_2$ ($=e_2(\text{plus})=e_2(\text{minus})$ on-shell) is a factor of $A_6$,
i.e. $e_2\mid N_6$. **It is not:** on three chambers $\gcd(N_6(t),e_2(t))$ has
degree $0$ on the slice (`e2test.py`), and a slice-restriction of a genuine
6-variable factor would have to divide, so $e_2\nmid N_6$ globally. The $n=5$
prefactor does **not** lift to a global $e_2$ factor at $n=6$.

**Determining handles assembled (for round 5):** (i) the soft recursion §1
(boundary = two-minus); (ii) the matching/partial-fraction structure §2 (poles
fixed at the matchings, simple, clean residues); (iii) full $S_3\wr Z_2$
symmetry + oddness + degree $5n-13$. A candidate $N_n$ must be a spline whose
pieces differ by $(k_S)^p$ truncated powers (box-spline §3) and which reduces
under §1 to the two-minus law. **Not yet a closed form** — the per-chamber
sextic core (degree $2n-4$ within each chamber) is the residual unknown; pinning
it (e.g. by fitting student-1's exact per-chamber polynomials to a $d=3$
truncated power and matching residues) is the remaining step.

## Reproduce
- `python3 code/verify_r4.py` — soft theorem (both legs, ratio 6); $D_n$ clears
  $A_n$ at $n=6,7$; poles at perfect matchings; per-chamber sextic core.
- `python3 code/recon_num.py` — per-chamber $A_6=$ sextic$/$matchings (factored).
- `python3 code/residue.py` / `residue2.py` — residues at the matching poles.
- `python3 code/soft_Nn.py` — soft recursion on $N_n$ (note: raw
  $N_6/\omega_p^2$ extrapolation is wall-contaminated; the clean check is in
  `verify_r4.py`).
- `python3 code/cauchy.py` — Cauchy permanent/determinant numerators.

## Literature (re-checked 2026-06)
No published closed form for this deep-water ($\omega^2=g|k|$) $n$-point
three-minus sector. Cauchy double-product / Schur context; box-spline theory:
de Boor–Höllig–Riemenschneider, *Box Splines* (1993); De Concini–Procesi–Vergne
(2010); Curry–Schoenberg (1966); amplitude method: Berends–Giele, *Nucl. Phys.*
**B306** (1988) 759.
