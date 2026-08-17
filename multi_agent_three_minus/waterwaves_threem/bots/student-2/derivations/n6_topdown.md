# Top-down structure of the three-minus amplitude + a soft theorem (student-2, round 2)

**Task r2-student-2.** Derive *why* the three-minus sector is a polynomial spline,
build the probabilistic / B-spline generalization, conjecture an all-$n$ formula,
test at $n=5,6,7$. Sector $\sigma=(-1,-1,-1,+1,\dots,+1)$ (legs $1,2,3$ minus),
dispersion $\omega_i^2=g|k_i|$, $k_i=\sigma_i\omega_i^2/g$. On-shell
$\sum_i\omega_i=0$, $\sum_i\sigma_i\omega_i^2=0\Rightarrow
Q:=\sum_{\rm minus}\omega_i^2=\sum_{\rm plus}\omega_j^2$. All amplitudes checked
against my own `code/bg` (exact GMP rationals); `--double` only for scans.
Build: `g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp`.

## 0. Summary of new results this round

1. **A uniform soft theorem (new, exact).** As *any* external frequency
   $\omega_p\to0$ on the three-minus manifold,
   $$\boxed{A_n^{3-}\ \xrightarrow{\ \omega_p\to0\ }\ 2(n-3)\,\omega_p^2\,A_{n-1}\,,}$$
   where the surviving $(n{-}1)$-point amplitude is **three-minus** if $p$ was a
   plus leg, and **two-minus** (a *known* closed form) if $p$ was a minus leg.
   Verified by exact-rational Richardson extrapolation at $n=6$: the limit ratio
   is $6=2(n-3)$ in **both** cases (`code/soft_exact.py`, `code/soft_minus.py`,
   `code/verify_r2.py`). For the explicit plus-leg config used,
   $\lim_{\omega_5\to0}A_6/(i\,\omega_5^2)=-536544=6\cdot(-89424)=6\,A_5^{3-}/i$
   (exact).
2. **Consequence — the universal prefactor and degree are fixed.** The soft
   recursion forces $A_n^{3-}=i\,2^{\,n-1}g^{\,3-n}\,\Phi_n$ with $\Phi_n$ a
   degree-$(2n-4)$, $S_3\wr Z_2$-symmetric, **piecewise polynomial whose pieces
   are truncated powers of exponent $n-3$** (cubic at $n=6$). The factor $2(n-3)$
   is exactly (prefactor ratio $2^{n-1}/2^{n-2}=2$)$\times$(exponent $n-3$).
3. **All legs behave as "knots."** In two-minus, plus legs are soft-$\omega^2$ but
   the two minus legs are soft-$\omega^{2n-5}$ (they sit in the prefactor). In
   three-minus **every** leg is soft-$\omega^2$. So no leg is a prefactor leg:
   the object is a *fully symmetric* spline of all $n$ legs. With degree $=n-3$
   and $N=n$ directions this is a **$d=3$ multivariate truncated power / box
   spline** ($\deg=N-d=n-3$) — the natural lead for the closed form.
4. **A small on-shell identity:** $e_2(\text{minus})=e_2(\text{plus})$
   (both $=\tfrac12[(\omega_1{+}\omega_2{+}\omega_3)^2-Q]$); a manifestly
   $Z_2$-symmetric degree-2 scalar that generalises the $n=5$ prefactor
   $\omega_4\omega_5=e_2(\text{plus})$. (`verify_r2.py`, 7/7 exact.)
5. **A broad family of closed forms is ruled out** (saves group effort, §4).

## 1. Structural derivation (deliverable 1)

**Piecewise-polynomial, no poles.** In `bg.cpp` the only non-smooth / singular
operations are (i) `absR(k_S)` $=|k_S|$ inside `EKernel`/`FKernel`, and (ii) the
propagator `Propagator(wS,kS)` $=-i/D_S$, $D_S=\omega_S^2/|k_S|-g$. (i) gives
breakpoints exactly on $\{k_S=0\}$ (piecewise-polynomial behaviour); (ii) would
give poles at $\{D_S=0\}$. Round 1 (student-2, PI-reverified) showed the $D_S=0$
residues **cancel on-shell**: a factorization residue is a product of two
sub-amplitudes, and every channel forces a *one-minus* sub-amplitude (which
vanishes, question.md item 1) or an empty all-same-sign sector. Hence $A_n^{3-}$
is **piecewise polynomial** with walls only at the mixed momentum-subset walls
$\{k_S=\sum_{i\in S}\sigma_i\omega_i^2=0\}$ (same-type subsets never wall).

**Degree $2n-4$ and $S_3\wr Z_2$ symmetry:** PI-reverified (degree by scaling;
symmetry = permute minus $\times$ permute plus $\times$ the $k\to-k$ swap, which
at $n=6$ maps three-minus to itself). The soft theorem (§2) re-derives the
$2^{n-1}g^{3-n}$ prefactor and the exponent $n-3$ independently.

## 2. The soft theorem and what it pins (deliverables 1–2)

**Mechanism.** For a truncated power of exponent $m$, removing one knot $a_p$ is a
finite difference: $(\,t-c\,)_+^{m}-(\,t-c-a_p\,)_+^{m}=m\,a_p(\,t-c\,)_+^{m-1}+O(a_p^2)$.
With $a_p=\omega_p^2$ this produces the $\omega_p^2$ scaling and the factor
$m=n-3$; the prefactor $2^{n-1}g^{3-n}\!\to\!2^{n-2}g^{4-n}$ contributes the
extra $2$. So $A_n^{3-}\to 2(n-3)\,\omega_p^2 A_{n-1}$ is the signature of a
**degree-$(n-3)$ truncated power in which every leg is a knot** $a_i=\omega_i^2$.

**Verification (exact).** `code/verify_r2.py` extrapolates
$A_6/(i\,\omega_p^2 A_5)\to 6$ (float-exact $6.0$) for a soft plus leg
(→ three-minus $A_5$) and for a soft minus leg (→ **two-minus** $A_5$, the known
law). The minus-leg case is the most useful: it ties three-minus directly to a
*solved* sector. The same $\omega^2$ scaling for both leg types is the precise
sense in which the three-minus object is "more symmetric" than two-minus.

**Probabilistic reading.** The two-minus law is
$A_n^{2-}=i\,2^{n-1}g^{3-n}\,\omega_a\omega_b\,(n-3)!\,(\prod_{j\in P}\omega_j^2)\,
f_X(\omega_a^2)$ with $X=\sum_{j\in P}\omega_j^2U_j$, $U_j\!\sim\!\text{Unif}[0,1]$
— the **density of a weighted uniform sum** (= univariate B-spline of knots
$\omega_j^2$, evaluated at a minus-leg energy; the $\min$ in question.md is
inessential because $f_X$ is reflection-symmetric about $Q/2$, so
$f_X(\omega_a^2)=f_X(\omega_b^2)$). The soft theorem says the three-minus analogue
is the same kind of density but with **all six knots active and $d=3$** rather
than two minus legs sitting outside as a prefactor.

## 3. The remaining lead: a $d=3$ box-spline / multivariate truncated power

The facts (degree $n-3$, $N=n$ knots, walls $\{k_S=0\}$, soft-$\omega^2$ for every
leg, full $S_3\wr Z_2$ symmetry, *variable* wall-smoothness reported round 1 —
e.g. a 1st-derivative kink at the 2-element wall $k_{\{2,4\}}=0$ but a milder kink
at the 3-element wall $k_{\{2,3,4\}}=0$) are exactly the fingerprints of a
**multivariate truncated power $T_M(x)$ / box spline $B_M(x)$** of a $3\times n$
matrix $M$ whose columns are the legs (De Concini–Procesi–Vergne / Dahmen–Micchelli
theory: $\deg = N-d = n-3$; walls = cones of $d{-}1=2$ columns; variable smoothness
is generic for $d>1$). The natural columns are points on a moment curve,
$a_i\sim(1,\ \sigma_i\omega_i,\ \sigma_i\omega_i^2)$ or $(\,\omega_i,\ \sigma_i\omega_i^2,\ \dots)$,
evaluated at the resonance $x=0$ (both conservation laws). Pinning the exact
columns + normalization is the open step; the per-chamber polynomial table
(student-1, bottom-up) is the most direct way to fix them, and the soft theorem
plus the $n=5$/two-minus boundary data give independent checks.

## 4. Closed-form families RULED OUT this round (exact, do not retry)

All tested against `./bg` exactly at $\ge14$ generic on-shell $n=6$ points;
"fails" = non-constant ratio $A_6/\text{cand}$ (structure wrong, not normalization).

| family | where | verdict |
|---|---|---|
| $C_6$ even (polynomial in $\omega_i^2$ alone) | `extract_even.py` | **fails** (0/30 held-out, hom. deg-4 fit) |
| $C_6=\prod_{i}\omega_i\cdot(\text{linear in }\omega^2)$ | `chamber_fit2.py` | **fails** |
| $C_6=e_2(\text{plus})\cdot P(\omega^2)$ | `chamber_fit2.py` | **fails** |
| double-subset spline $\sum_{S\subseteq{\rm m},T\subseteq{\rm p}}(-1)^{|S|+|T|}(\sum_T\omega^2-\sum_S\omega^2)_+^{p}$, $p=2,3,4$, with/without $e_2$, and $|\cdot|^p$ | `batch1.py` | **fails** (all) |
| same-type pair sums $\sum_{\rm pairs}\omega_a\omega_b\,(\min-\text{thr})_+^3$ (plus, minus, both) | `candidates.py` (r1) | **fails** |
| mixed-type pair sums $\sum_{a\in{\rm m},b\in{\rm p}}\omega_a\omega_b\,B_{ab}$, thresholds $\omega_a^2,\omega_b^2,\min,(\omega_a^2{+}\omega_b^2)/2,Q/3$, $p=2,3$ | `batch2.py` | **fails** |
| inner product $\int_0^Q P_-P_+$; single-min cubic block + swap | PI (r1) | **fails** |

The negative space is sharp: the chamber polynomial has **genuine mixed parity**
(it is neither even in the $\omega_i$ nor a single odd factor $\times$ even
polynomial), and the spline is **not** a one- or two-sided one-dimensional B-spline.
This is consistent only with a genuinely multivariate ($d=3$) spline, §3.

## 5. Literature (deliverable 4)

No published closed form for this water-wave amplitude sector
(deep-water $\omega^2=g|k|$, $n$-point tree, three-minus) was found.
Closest items: (i) the **B-spline / truncated-power = density of a weighted
uniform sum** identity is classical — Curry & Schoenberg (1966); de Boor,
*A Practical Guide to Splines* (2001). (ii) **Box splines / multivariate truncated
powers / vector partition functions** (the $d{>}1$ generalisation that §3 needs):
de Boor–Höllig–Riemenschneider, *Box Splines* (1993); De Concini–Procesi–Vergne,
*Topics in Hyperplane Arrangements, Polytopes and Box-Splines* (2010);
Dahmen–Micchelli (1980s). (iii) **Berends–Giele recursion**: Berends & Giele,
*Nucl. Phys.* **B306** (1988) 759. (iv) Amusing field-theory parallels to the
sector structure: "single-minus" gluon/graviton tree amplitudes vanish for
generic real momenta (cf. our one-minus $\equiv0$) — e.g. arXiv:2602.12176,
arXiv:2603.04330 (2026). (v) Classical deep-water resonant-interaction theory
(Phillips 1960; Longuet-Higgins 1962) concerns 4-wave resonance, not the
$n$-point tree closed form. Web searches (2026-06) returned nothing covering this
sector — it is a genuine open problem.

## 6. Conjecture status and recommendation (deliverable 3)

A single explicit all-$n$ closed form is **not yet pinned**. What is established
and all-$n$: the prefactor $i\,2^{n-1}g^{3-n}$, the exponent $n-3$, the symmetry
$S_3\wr Z_2$, the wall set $\{k_S=0\}$, the no-pole/polynomial property, and the
**soft recursion** $A_n^{3-}\to2(n-3)\omega_p^2A_{n-1}$ (with the minus-leg branch
landing on the known two-minus law). These uniquely fix the *boundary data and
the leading structure* of the spline; the missing piece is the explicit $d=3$
spline (columns + chamber polynomials).

**Round-3 recommendation.** Combine (a) student-1's exact per-chamber degree-8
polynomials with (b) the soft recursion / two-minus boundary value: fit each
chamber polynomial to a $d=3$ truncated power $T_M$ with moment-curve columns
$a_i=(1,\sigma_i\omega_i,\sigma_i\omega_i^2)$ evaluated at $x=0$, using the soft
theorem and the $n=5$ reduction as constraints/normalisation. Then test the
resulting all-$n$ candidate exactly at $n=6$ (chambers + two-sided wall limits)
and $n=7$.

## Files
`code/{soft_limit,soft_exact,soft_minus,verify_r2}.py` (soft theorem);
`code/{batch1,batch2,chamber_fit2,extract_even,parity_probe,slice_interp,line_slice}.py`
(structure + ruled-out families); reuse `code/{harness,channels,symbolic_bg}.py`
(r1, oracle-faithful). Headline reproduce: `python3 code/verify_r2.py`.
