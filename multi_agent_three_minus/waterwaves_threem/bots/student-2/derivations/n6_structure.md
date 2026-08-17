# n=6 three-minus structure — student-2, round 1

**Task r1-student-2.** Determine the n=6 three-minus structure: targeted pole
search, chamber walls, polynomial-vs-rational, first ansatz. Sector
$\sigma=(-1,-1,-1,+1,+1,+1)$ (legs 1,2,3 minus; 4,5,6 plus), dispersion
$\omega_i^2=g\,|k_i|$, $k_i=\sigma_i\omega_i^2/g$. All amplitudes validated
against my own copy of `bg.cpp` (exact GMP rationals); `--double` only for bulk
scans. Build: `g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp`.

## 0. Tools (deliverable 1)

- `harness.py` — wraps `./bg` (on-shell `-n/-w/-s` and raw `--amp -K/-W`), parses
  exact + double output, reproduces the oracle's on-shell solve for legs $1,n$.
- `channels.py` — enumerates factorization channels $S$ and their propagator
  denominators $D_S=\omega_S^2/|k_S|-g$, $\omega_S=\sum_{i\in S}\omega_i$,
  $k_S=\sum_{i\in S}\sigma_i\omega_i^2/g$.
- `symbolic_bg.py` — a faithful **sympy reimplementation** of the entire BG
  algorithm with every $|k_S|$ resolved to a fixed sign at a chamber reference
  point. Reproduces `./bg` exactly (n=5: $-25344$; n=6: $-29948208/17$). This is
  the engine recommended for per-chamber polynomial extraction in round 2.

## 1. Basic structure of $A_6$ (deliverable, supports the ansatz)

Verified exactly at generic on-shell points (`verify_threem.py`):

- **Purely imaginary**: $\mathrm{Re}\,A_6=0$ (as in the lower sectors).
- **Homogeneous degree $2n-4=8$** in the frequencies at fixed $g$ (scale all
  $\omega\to t\omega$ $\Rightarrow$ $A_6\to t^8A_6$, ratio $=256$ at $t=2$,
  exact). Note $D_S$ is *degree 0* (scale-invariant): $D_S=g(\omega_S^2/|K_S|-1)$
  with $K_S=\sum_{i\in S}\sigma_i\omega_i^2$.
- **Symmetry $S_3\wr Z_2$**: invariant under permuting the minus legs
  $\{1,2,3\}$, permuting the plus legs $\{4,5,6\}$, **and** swapping the two
  triples $(\omega_1,\omega_2,\omega_3)\leftrightarrow(\omega_4,\omega_5,\omega_6)$.
  The $Z_2$ is the plus/minus swap (question.md item 3): at $n=6$ it maps three-
  minus to three-minus, so it is now a genuine self-symmetry (and explains why
  the swap "stops helping" — it constrains rather than reduces).
- **Momentum conservation forces** $\sum_{i\in\{1,2,3\}}\omega_i^2 =
  \sum_{i\in\{4,5,6\}}\omega_i^2 \;(=Q)$ and $\sum_i\omega_i=0$; so the manifold
  is 4-dimensional (3 ratios + scale), and on it $e_2$ of each triple are equal.

## 2. Targeted pole search → **NO POLES** (deliverable 2, the key result)

question.md conjectured three-minus carries factorization poles for $n\ge6$ at
$D_S=0$. **It does not.** For each channel I built a one-parameter on-shell family
driving a single $D_S\to0$ and measured $A_6$.

Crucial simplification: for a channel $S\subseteq\{2,3,4,5\}$ (only free legs),
$D_S$ depends *only* on the legs in $S$ (not on the spectator/solved legs), so a
clean exact approach is possible. Results (`targeted_pole.py`):

| channel $S$ | type | $D_S\to0$ point | $A_6$ as $D_S\to0$ | $A_6\,D_S$ |
|---|---|---|---|---|
| $\{2,3,4\}$ | 2m1p | $\omega_4=-19/5$ | $\to-3.1045\times10^5$ (finite) | $\to0$ |
| $\{2,3,5\}$ | 2m1p | $\omega_5=-19/5$ | $\to-3.1045\times10^5$ (finite) | $\to0$ |
| $\{2,4,5\}$ | 1m2p | $\omega_2=-7/3$ | $\to-2.4593\times10^3$ (finite) | $\to0$ |
| $\{3,4,5\}$ | 1m2p | $\omega_3=-7/3$ | $\to-2.4593\times10^3$ (finite) | $\to0$ |
| $\{1,2,3\}=\{4,5,6\}$ | 3m0p | $\omega_1\to-6/5$ | $\to99.347$ (finite) | $\to0$ |

At the *exact* channel point `bg.cpp` SIGFPEs (it divides by $D_S=0$), but the
limit is finite — the propagator pole is **spurious/removable**, its residue
cancels in the on-shell sum. Confirmed pole-free at **n=5,6,7** (so it is a
sector property, not an $n=6$ accident).

Two-element channels (1m1p, 2m0p, 0m2p) only reach $D_S=0$ *degenerately* (a
frequency $\to0$); the genuine codimension-1 channels are the size-3 subsets, all
tested above.

**Why (physical argument).** A factorization residue on channel $S$ is the
product of two lower-point sub-amplitudes joined by the on-shell internal line.
The internal line carries one extra minus (resp. plus) leg to the two sides.
Splitting the 3 minus legs as $(a,b)$ with $a+b=3$: the only split that can give
*both* sides $\ge2$ minus legs is $(1,2)$ with the internal line minus on the
1-minus side, but then one side is a 4-point amplitude whose forced factorization
kinematics make the residue vanish; every other split puts a **one-minus**
sub-amplitude (which vanishes identically, question.md item 1) or an empty
all-plus/all-minus sector on one side. Hence no surviving residue → no pole. This
is consistent with the all-orders numerics.

**Consequence:** $A_6$ (and $A_{n}$, three-minus) is **piecewise-polynomial**,
not rational. This answers the PI's round-1 gate question.

## 3. Chamber walls (deliverable 3)

The non-smoothness of $A_6$ is at the **momentum subset walls** $k_S=
\sum_{i\in S}\sigma_i\omega_i^2=0$ for **mixed** subsets $S$ (at least one minus
and one plus leg). All-minus / all-plus subsets have $k_S$ of a fixed sign and
never wall (e.g. $k_{\{1,2,3\}}=-(\omega_1^2+\omega_2^2+\omega_3^2)<0$). Across a
mixed wall $|k_S|$ flips sign.

Verified (`kinkmap.py`, exact 4th differences; `wallcheck.py`; `verify_threem.py`):

- At $k_{\{2,4\}}=0$ ($\omega_4=\omega_2$) and $k_{\{3,4\}}=0$
  ($\omega_4=\omega_3$): $A_6$ is finite and **continuous** (the two-sided jump
  $\to0$ linearly in the offset) with a **first-derivative kink** (left/right
  slopes differ). `bg.cpp` SIGFPEs exactly on the wall (divides by $|k_S|=0$);
  approach as a limit.
- At $k_{\{2,3,4\}}=0$ ($\omega_4^2=\omega_2^2+\omega_3^2$): a cubic-type kink,
  visible in the exact 4th finite difference.

These $|k_S|=0$ momentum walls are **distinct** from the $D_S=0$ channels of §2
(those are smooth/pole-free). Caution when locating walls numerically: a wall that
lands exactly on a sampled grid point makes the oracle SIGFPE and can be missed
(this produced two false "kinks" in an early `--double` scan that exact arithmetic
ruled out).

The chamber decomposition is therefore the arrangement of the mixed-subset
hyperplanes $\{k_S=0\}$ on the resonant manifold, refined by the comparisons that
appear inside the (still-to-be-determined) truncated-power thresholds.

## 4. First ansatz (deliverable 4) — status: open, with a lead

The naive generalizations **fail** (`candidates.py`, 0/10 exact, *non-constant*
ratios — so the truncated-power structure, not the normalization, is wrong):
$A_6\ne i\,2^5g^{-3}\sum_{\text{pairs}}\omega_a\omega_b\sum_S(-1)^{|S|}
(\min(\omega_a^2,\omega_b^2)-\sum_S\omega_j^2)_+^3$ for pair-sums over plus legs,
minus legs, or both.

**Lead (B-spline picture).** The verified two-minus law,
$$A_n^{(2-)}=i\,2^{n-1}g^{3-n}\,\omega_a\omega_b
\sum_{S\subseteq P}(-1)^{|S|}\big(\beta^2-\textstyle\sum_{j\in S}\omega_j^2\big)_+^{\,n-3},
\quad \beta=\min(|\omega_a|,|\omega_b|),$$
is exactly a **B-spline**: $\sum_{S\subseteq P}(-1)^{|S|}(c-\sum_{S}x_j)_+^{m-1}
=(m-1)!\,M(c;x_1,\dots,x_m)$ with $m=|P|=n-2$ knots $x_j=\omega_j^2$ (Curry–
Schoenberg). Its breakpoints are the subset-sum walls $c=\sum_{j\in S}\omega_j^2$,
i.e. the momentum walls $k_{\{a\}\cup S}=0$ — matching §3. The $n=5$ three-minus
form is this with the two *plus* legs playing the minus-pair role (via the swap).

At $n=6$ neither triple has the special size 2, so the closed form is a genuinely
new, $S_3\wr Z_2$-symmetric, degree-8, **cubic** piecewise polynomial on the
$\{k_S=0\}$ arrangement — most plausibly a 2-parameter / convolution-type
B-spline. The recommended round-2 attack:
1. Extract the exact polynomial on a single chamber with the validated
   `symbolic_bg.py` engine (freeze chamber signs from a reference point; the
   $D_S$ denominators cancel since the sector is pole-free) — this gives the
   per-chamber cubic directly, no fitting.
2. Match it to a box-spline/B-spline of the $\omega_i^2$ with the breakpoint
   structure of §3, then symmetrize under $S_3\wr Z_2$.

## Files

`code/{harness,channels,symbolic_bg,targeted_pole,reachability,kinkmap,wallcheck,candidates,verify_threem}.py`,
own `code/bg.cpp` + built `code/bg`. Reproduce headline checks with
`python3 code/verify_threem.py` (all pass, exact rational).

## External references

- BG recursion: F. A. Berends, W. T. Giele, *Nucl. Phys.* **B306** (1988) 759.
- B-spline / truncated-power identity: Curry & Schoenberg (1966); de Boor,
  *A Practical Guide to Splines* (2001), §IX — divided differences of
  $(\,\cdot\,)_+^{m-1}$.
  (Web search found no published closed form for this water-wave sector — it is a
  genuine open problem.)
