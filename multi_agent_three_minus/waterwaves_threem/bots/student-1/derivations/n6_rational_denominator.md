# n=6 three-minus: the explicit rational denominator $\prod_{i\in M,j\in P}(\omega_i+\omega_j)$

**student-1, round 3 (2026-06-26).** All exact-rational against my own copy of `bg.cpp`
(`bots/student-1/code/bg.cpp`, byte-identical to the shared oracle; shared one untouched).

## 0. Summary / headline

The three-minus $A_6$ (minus legs $1,2,3$; plus legs $4,5,6$) is **piecewise-rational**
with an **explicit, fully symmetric denominator**:

$$\boxed{\;A_6 \;=\; i\,2^{5} g^{-3}\;\frac{N(\omega)}{\displaystyle\prod_{i\in\{1,2,3\}}\prod_{j\in\{4,5,6\}}(\omega_i+\omega_j)}\;,\qquad N=\text{piecewise polynomial (a spline)}.\;}$$

The denominator $D_9:=\prod_{i\in M,j\in P}(\omega_i+\omega_j)$ (9 mixed pairs, degree 9) is
invariant under the full sector symmetry $S_3(\text{minus})\times S_3(\text{plus})\times Z_2(\text{swap})=S_3\wr Z_2$,
so the numerator $N=A_6\,D_9/(i\,2^5g^{-3})$ inherits the symmetry. $N$ is a degree
$8+9=17$ homogeneous spline.

This **reconciles and corrects** the round-2 split:
- it confirms my round-2 claim **s1_005** ($A_6$ is rational, not polynomial);
- it shows the **box-spline / multivariate-B-spline the team is hunting (student-2 s2_008, PI degree-law) lives in the NUMERATOR $N$**, not in $A_6$ itself. The PI/round-1 "gate" ($A_6$ polynomial) was the inference *finite $\Rightarrow$ polynomial*, which is false: a rational function whose poles are all shielded outside the physical chambers is finite everywhere yet not polynomial.

## 1. Where the denominator comes from (BG structure)

Reading `bg.cpp` (`EKernel/FKernel/Vertex/Propagator/BGCurrent`), the only sources of
kinematic denominators are:

- **`FKernel`** divides by momentum **magnitudes** $|k_B|$ of its arguments
  (`FKernel(3)=-1-p_0p_1/(|p_0||p_1|)`, recursion divides by `qp1,qp2`). Here
  $k_B=\sum_{i\in B}\sigma_i\omega_i^2$.
- **`Propagator`** $=-i/(\omega_S^2/|k_S|-g)=-i\,|k_S|/(\omega_S^2-g|k_S|)$: contributes
  $|k_S|$ to the **numerator** and the physical channel denom $(\omega_S^2-g|k_S|)$, which
  **cancels** on-shell (no factorization poles: round-1 gate, my s1_006, student-2 s2_002).

So $A_6 = (\text{polynomial in }\omega,|k_B|)/\prod_{\text{surviving}}|k_B|$. At $n\le5$ all
$|k_B|$ cancel (the two-minus / $n=5$ laws are polynomial); at $n=6$ some survive — hence
rational. Within a chamber each $|k_B|=\varepsilon_B k_B$ is a fixed-sign polynomial, so $A_6$
is a genuine ratio of polynomials.

## 2. $A_6$ is rational — exact reconstruction (no fitting ansatz)

On a 1-D slice held inside ONE analytic piece (all mixed walls $k_S=0$ **and** all six
same-type orderings $\omega_i^2\lessgtr\omega_j^2$ frozen), vary $\omega_4=a+t$ with
$\omega_2,\omega_3,\omega_5$ fixed; legs $1,6$ are solved by the oracle, giving
$\omega_1,\omega_6=(\text{deg-2})/\,\text{sumFree}$, $\text{sumFree}=\omega_2+\omega_3+\omega_4+\omega_5=-(\omega_1+\omega_6)$.
Multiplying by $\text{sumFree}^8$ clears ONLY the solve denominator. Exact rational
reconstruction (`rat_denom.py`, Padé over $\mathbb Q$, verified on held-out points) gives,
at base $(\omega_2,\omega_3,\omega_4,\omega_5)=(1,-\tfrac{27}{10},\tfrac{43}{10},\tfrac{12}{5})$:

$$A_6\cdot\text{sumFree}^8=\frac{N(t)}{D(t)},\qquad \deg N=11,\ D(t)=(5t+8)(10t+53)/424\ (\deg D=2).$$

$\deg D=2\ne0$ proves $A_6$ is **not** a degree-8 polynomial in the six frequencies
(a polynomial would force $A_6\,\text{sumFree}^8$ polynomial, $\deg D=0$). **Control:** the
identical test on the known-polynomial $n=5$ law returns $\deg D=0$ (polynomial) at $p=1$
(`n5_poly_control.py`) — the method is sound, so the $n=6$ result is genuine rationality.

The two roots are at $\omega_4=-\omega_2$ (i.e. $\omega_2+\omega_4=0$) and $\omega_4=-\omega_3$
($\omega_3+\omega_4=0$): mixed-pair **sum** conditions, not the squared walls.

## 3. The denominator is $\prod(\omega_i+\omega_j)$ over mixed pairs — perfect matchings

Reconstructing the in-chamber form along each free leg in turn (`multislice.py`) gives
denominator roots that always sit where THREE pair-sums vanish simultaneously — a
**perfect matching** of the minus triple to the plus triple ($\omega_i+\omega_{\sigma(i)}=0$
for a bijection $\sigma$). On the manifold a matching locus is codim-1 (a wall): if e.g.
$\omega_1+\omega_5=\omega_2+\omega_4=0$ then $\omega_3+\omega_6=0$ follows from $\sum\omega=0$,
and both conservation laws are automatically satisfied. There are $3!=6$ matchings; two of
them use the pair $(\omega_1,\omega_6)$, i.e. $\omega_1+\omega_6=-\text{sumFree}$, which is
why sumFree appears in the free-coordinate denominator.

The individual codim-1 factors are the **9 mixed-pair linear forms** $(\omega_i+\omega_j)$,
$i\in\{1,2,3\},j\in\{4,5,6\}$. (Only the SUM branch $\omega_i+\omega_j$ appears; the
difference branch $\omega_i-\omega_j$ of the squared wall $k_{ij}=\omega_j^2-\omega_i^2$ is
absent / cancelled.)

## 4. Verified result: $A_6\,D_9$ is a polynomial (across chambers)

Define $D_9=\prod_{i\in\{1,2,3\},j\in\{4,5,6\}}(\omega_i+\omega_j)$. Multiplying $A_6$ by
$D_9$ and reconstructing on a chamber slice yields a residual denominator that is a **pure
power of sumFree** — i.e. NO $(\omega_i\pm\omega_j)$ factor survives. A pure-sumFree residual
is exactly the signature that $A_6 D_9$ is a genuine polynomial in the six frequencies
restricted to the manifold (any 6-variable polynomial, after the leg-$1,6$ solve, becomes
$(\text{poly in free})/\text{sumFree}^{\le\deg}$).

Verified at **6 distinct chamber types** $\times$ **2 slice directions** each
(`test_D9_global.py`, `verify_denominator.py`), e.g.:

| chamber | residual (vary $\omega_4$) | residual (vary $\omega_5$) |
|---|---|---|
| T0 | $\text{sumFree}^{10}$ (pure) | $\text{sumFree}^{10}$ (pure) |
| T1 | $\text{sumFree}^{4}$ (pure) | $\text{sumFree}^{4}$ (pure) |
| T2 | $\text{sumFree}^{6}$ (pure) | $\text{sumFree}^{6}$ (pure) |
| T3,T4,T5 | $\text{sumFree}^{4}$ (pure) | $\text{sumFree}^{4}$ (pure) |

(The sumFree power is a coordinate artifact of the chart; it is not physical.)

## 5. Why finite everywhere yet rational — shielded poles

Each chamber's rational form $N_c/D_c$ has poles on matching walls $(\omega_i+\omega_j)=0$
that lie **outside** that chamber (shielded by the chamber boundary). Direct check
(`probe_pole.py`): the reference-chamber form has a denominator root at $t=-8/5$
($\omega_3+\omega_4=0$), but by $t\approx-1.5$ the kinematics have already **crossed a wall**
into a different chamber; the physical $A_6$ at $t=-8/5$ is finite ($A_6/i\approx5436$),
computed from the neighbouring chamber's form. So $A_6$ is finite on the whole manifold
(no physical poles) **and** genuinely rational — no contradiction.

## 6. Status of minimality / open items

- $D_9$ is **sufficient** (verified). Whether it is **minimal** is open: at a matching wall
  three of the nine factors vanish together, so $D_9$ over-clears $3{:}1$ there, and a
  per-chamber 1-D slice cannot decide minimality (a dropped factor's pole coincides with
  other factors' zeros on the slice). By $S_3\wr Z_2$ symmetry every mixed pair appears in
  some chamber's denominator, so the minimal GLOBAL denominator is plausibly all 9, but
  this needs a multivariate confirmation.
- **All-$n$ conjecture (SUPPORTED at n=7):**
  $A_n^{3-}=i\,2^{n-1}g^{3-n}\,N_n/\!\prod_{i\in\{1,2,3\},j\in\text{plus}}(\omega_i+\omega_j)$,
  $N_n$ a piecewise polynomial of degree $(2n-4)+3(n-3)$; at $n=5$ the denominator divides
  $N_5$ (cancels), recovering the polynomial $n=5$ law. **n=7 check (`test_n7.py`):**
  with $D_{12}=\prod_{i\in\{1,2,3\},j\in\{4,5,6,7\}}(\omega_i+\omega_j)$ (12 pairs),
  $A_7 D_{12}$ reconstructs on a chamber slice to a PURE power of sumFree (residual
  $\text{sumFree}^5$, no other factor) — i.e. $A_7 D_{12}$ is polynomial, exactly as
  conjectured.
- **Hand-off:** the box-spline / $d=3$ truncated-power program (student-2 s2_008), the soft
  theorem (s2_006), and the PI degree law should now target the polynomial **numerator**
  $N=A_6 D_9$ (degree 17, $S_3\wr Z_2$-symmetric), not $A_6$.

## Reproduce
```
cd bots/student-1/code
g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp     # if not built
python3 verify_denominator.py        # headline: rational + A_6*D9 polynomial across chambers
python3 rat_denom.py                  # exact in-chamber rational form, deg D=2
python3 multislice.py                 # denominator factors = mixed-pair sums (matchings)
python3 probe_pole.py                 # shielded-pole check (finite across the wall)
```
