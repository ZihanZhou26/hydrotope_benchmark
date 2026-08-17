# n=6 three-minus, round 5: the numerator $N_6$ is a BOX SPLINE (not a simple truncated-power sum), with the explicit (1=2) jump coefficient $Q$

**student-1, round 5 (2026-06-27).** All exact-rational against my own copy of
`bg.cpp` (`bots/student-1/code/bg.cpp`, shared oracle untouched). Independent
cross-check by a faithful native-Python BG port (`pybg.py`, matches `./bg` exactly
at n=5,6,7). One-command-ish checks: `r5_verify.py`, `r5_getQ.py`, `r5_Mfit.py`,
`r5_control.py`, `r5_crossterm.py`.

Baseline (PI-reverified through round 5):
$$A_6=i\,2^5 g^{-3}\,\frac{N(\omega)}{\omega_1\omega_2\omega_3+\omega_4\omega_5\omega_6},\qquad
N=\text{degree-11, }S_3\wr Z_2\text{-symmetric, }\omega\to-\omega\text{-odd, CONTINUOUS spline}.$$
Kinks live only on the **mixed** walls (same-type orderings $\omega_i=\omega_j$ are
analytic — re-confirmed here, `_sametype.py`): the **(1=1)** walls
$a_i=b_j$ ($a_i=\omega_i^2$ minus, $b_j=\omega_j^2$ plus) with jump exponent **1**,
and the **(1=2)** walls $a_i=b_j+b_k$ with jump exponent **3** (s1_013).

## 0. Headline (two results, both decisive)

1. **The round-5 task premise is WRONG.** $N$ is **NOT** a simple single-wall
   truncated-power spline
   $$N \overset{?}{=} B+\sum_{(1{=}1)}(k_{ij})_+\,P_{ij}+\sum_{(1{=}2)}(k_{ijk})_+^3\,Q_{ijk}.$$
   $N$ is a **genuine box spline**: its piecewise polynomial in each chamber is
   *not* recovered by a base plus chamber-independent single-wall corrections.
   The (1=1) jump coefficient is **chamber-dependent** (cross-terms appear at wall
   intersections). Proven by an exact modular fit with controls (§2).

2. **The (1=2) part IS simple, and I extracted its coefficient exactly.** The (1=2)
   jump is a single chamber-independent truncated power; the coefficient $Q$ is an
   explicit degree-5 polynomial (§3). After subtracting the full (1=2) correction,
   $M=N-\sum_{(1{=}2)}(k_{ijk})_+^3 Q_{ijk}$ is **(1=2)-smooth** (verified jump $=0$
   at 10/10 (1=2) walls across $\ge4$ chamber types).

## 1. Method and infrastructure

- **F-constant slices** ($\omega_4=a+t,\ \omega_5=b-t$, $\sum_{\rm free}\omega$ fixed)
  make every $\omega_i(t)$ — including the solved legs $1,6$ — *polynomial* in $t$,
  so $N(t)$ is a genuine polynomial; reconstruct each chamber piece exactly.
- **Single-wall crossings only** (mixed-wall signature `msig` flips by exactly one);
  same-type orderings allowed to vary (analytic). Jump $=N_+-N_-$, oriented to the
  $(k_S>0)$-active convention.
- **Batch oracle.** I added a `--batch` mode to my `bg.cpp` copy (reads many on-shell
  points from stdin, exact GMP, per-point `ZeroDiv` guard so a wall-hit no longer
  SIGFPE-aborts the whole run). ~one process for thousands of points.
- **Independent evaluator.** `pybg.py` is a faithful native-Python transcription of
  the BG recursion; it reproduces `./bg` exactly at n=5,6,7 (used as a second oracle).
- Modular RREF (prime $2^{61}-1$) for rank/consistency; exact rationals for final
  coefficients (the float/clustered-node hazard is avoided throughout).

## 2. Proof that $N$ is a box spline (simple form fails)

Reduce away the (1=2) part first (it is clean, §3): set
$M=N-\sum_{(1{=}2)}(k_{ijk})_+^3 Q_{ijk}$. By construction $M$ has **only (1=1)
kinks** (verified (1=2)-smooth, §3). If $N$ were a simple spline, $M$ would be a
simple **(1=1)** spline:
$$M \overset{?}{=} B+\sum_{i\in M,\,j\in P}|k_{ij}|\,P_{ij},\qquad k_{ij}=b_j-a_i,$$
with a global symmetric base $B$ and a single $S_3\wr Z_2$-orbit coefficient $P$
(degree 9). I fit this exactly:

- **Basis.** $B$ = the 12 $G$-symmetric, $\omega\to-\omega$-odd, weighted-degree-11
  monomial classes in the invariants $(e_1,e_2,e_3^-,e_3^+)$ (complete for the smooth
  part). (1=1) correction = $S_3\times S_3$ orbit-sum over the 9 walls of
  $|k_{ij}|\cdot$(template), templates = the 125 manifold-independent $H$-invariant
  degree-9 monomials ($H=$ stabilizer of the reference wall). **137 columns total.**
- **Real $M$:** 187 exact on-shell points → columns have **full rank 137** but
  the system is **INCONSISTENT** (held-out fails). So $M\notin\mathrm{span}\{$base,
  single-(1=1)$\}$. (`r5_Mfit.py`.)
- **CONTROL (machinery is sound):** a *synthetic* simple (1=1) spline
  $M_{\rm test}=\sum_{\rm walls}|k_{ij}|\,(\text{fixed template})$ fed through the
  *same* fitter returns **CONSISTENT**, rank 137 (`r5_control.py`). So the real-$M$
  inconsistency is genuine, not a basis/code artifact.
- **Explicit cross-term:** the mixed second difference
  $D(\varepsilon)=N_{++}-N_{+-}-N_{-+}+N_{--}$ around a (1=1)$\times$(1=1)
  intersection is **nonzero** (`r5_crossterm.py`). A simple spline gives the
  ordinary smooth $O(\varepsilon^2)$; here $D$ is *more* singular, $O(\varepsilon)$,
  because the chosen difference-branch walls $\{a_2=b_4\},\{a_3=b_5\}$ **force a
  third**, $\{a_1=b_6\}$ (on-shell $a_2=b_4,\ a_3=b_5\Rightarrow a_1=b_6$): the
  (1=1) walls intersect in **matchings**, exactly the entangled-matching geometry
  (s2_011/s1_011, now seen on the difference branch).

**Conclusion.** The closed form must include **cross-terms** (products of
intersecting-wall truncated powers) — i.e. a genuine box spline, *not* the simple
sum in the round-5 task. The (1=1) jump coefficient is chamber-dependent; the
(1=2) one is not.

## 3. The explicit (1=2) jump coefficient $Q$ (exact, verified)

For the reference (1=2) wall $\{a_i=b_j+b_k\}$ (minus leg $i$; plus pair $\{j,k\}$;
excluded plus leg $l$; other two minus legs $p,q$), write
$$A_1=\omega_p+\omega_q,\ A_2=\omega_p\omega_q,\quad B_1=\omega_j+\omega_k,\ B_2=\omega_j\omega_k,\quad y=\omega_l .$$
The jump of $N$ across the wall is $N_+-N_-=(k_{ijk})^3\,Q_{ijk}$ with
$k_{ijk}=a_i-b_j-b_k$, and (a representative modulo the on-shell ideal; $\omega_i$
does not appear in this gauge)
$$\boxed{\,Q=A_2B_1\big(y^2-A_1^2-A_1B_1+A_2-B_2\big)+B_2\,y\big(A_2-B_1y-B_2\big)\,}$$
expanded
$$Q=-A_1^2A_2B_1-A_1A_2B_1^2+A_2^2B_1-A_2B_1B_2+A_2B_1y^2+A_2B_2y-B_1B_2y^2-B_2^2y .$$
$Q$ is degree 5, odd under $\omega\to-\omega$, $S_2(\{p,q\})\times S_2(\{j,k\})$-symmetric.

**Validation.**
- Extracted by exact reconstruction of single-(1=2)-wall jumps on many F-const
  slices, relabelled to the reference wall by the $S_3\times S_3$ symmetry; the
  resulting (point, $Q$-value) data fits a degree-5 $H'$-symmetric polynomial with
  **rank 34, fully consistent, held-out clean**, **0/55 exact mismatches**
  (`r5_getQ.py`).
- Globally: $\sum_{(1{=}2)\text{ walls}}(k_{ijk})_+^3 Q_{ijk}$ (all 9 walls, orientation
  $k_{ijk}=a_i-b_j-b_k$, active when $>0$) subtracted from $N$ gives an exactly
  (1=2)-**smooth** $M$ at **10/10** tested (1=2) walls spanning $\ge4$ chamber types
  (`r5_verify.py`). This is the strong, representation-independent check that $Q$ is
  the correct global (1=2) coefficient.

## 4. Status and recommendation

- **SOLVED/extended this round:** the (1=2) jump coefficient $Q$ (explicit, verified);
  the structural fact that $N$ is a **box spline** with **cross-terms**, not the
  simple single-wall sum (this corrects the round-5 task premise for both students
  and the PI); (1=2) jumps clean / (1=1) jumps chamber-dependent; cross-terms carried
  by the (difference-branch) **matching** intersections.
- **OPEN (the whole remaining problem):** the cross-term / box-spline structure of
  the (1=1) sector. Concretely, build
  $$N=B+\sum_{(1{=}2)}(k_{ijk})_+^3 Q_{ijk}+\Big[\text{(1=1) box-spline part}\Big],$$
  where the bracket is **not** $\sum|k_{ij}|P_{ij}$ but a box spline on the (1=1)
  arrangement whose cross-terms are organized by perfect matchings $\sigma:M\to P$
  (three difference-branch walls $a_i=b_{\sigma(i)}$ coincide). Natural next ansatz:
  matching-indexed products $\prod_{i}(k_{i\sigma(i)})_+$ with truncated-power
  numerators, dovetailing student-2's matching/Cauchy partial-fraction picture
  (s2_013) and the $d=3$ box-spline lead (s2_008) — now correctly targeted at the
  cross-term part rather than the (failed) simple sum.

## Reproduce
```
cd bots/student-1/code
g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp
python3 pybg.py          # independent evaluator == ./bg (n=5,6,7)
python3 r5_getQ.py        # extract Q (1=2): rank 34, 0 mismatches
python3 r5_verify.py      # M=N-corr12 is (1=2)-smooth 10/10; pybg cross-check
python3 r5_control.py     # control: synthetic simple spline -> CONSISTENT
python3 r5_Mfit.py        # real M -> full rank 137, INCONSISTENT (box spline)
python3 r5_crossterm.py   # explicit nonzero mixed 2nd difference (cross-term)
```
