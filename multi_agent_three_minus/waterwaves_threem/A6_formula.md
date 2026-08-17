# The $n=6$ three-minus amplitude $A_6$ — explicit closed form

Self-contained statement of the **PI-verified** closed form for the tree-level 6-point
amplitude in the three-minus sector $\sigma=(-1,-1,-1,+1,+1,+1)$ (minus legs $M=\{1,2,3\}$,
plus legs $P=\{4,5,6\}$), with **all reference polynomials** written out. Source:
`bots/student-1/code/r6_closedform.py` (assembled evaluator) and `r6_polys.txt`; verified
$140/140$ generic points across $58$ chamber labels plus non-generic, $g$-homogeneity, and
two-sided wall limits (residual $0$, exact rational).

---

## Master formula

$$
\boxed{\,A_6 \;=\; i\,2^{5}\,g^{-3}\,\frac{N_6(\omega)}{e_3^- + e_3^+}\,},
\qquad e_3^-=\omega_1\omega_2\omega_3,\quad e_3^+=\omega_4\omega_5\omega_6 .
$$

$A_6$ is **purely imaginary**, homogeneous of degree $2n-4=8$ in $\omega$, even under
$\omega\to-\omega$, and $S_3(\text{minus})\wr Z_2(\text{swap})$-symmetric. The denominator
$e_3^-+e_3^+$ is the **minimal** denominator (pole order $1$); it is *shielded* — it never
vanishes on a physical chamber interior — so $A_6$ is finite everywhere yet genuinely rational
(there are **no factorization poles**).

### Notation

- $a_i \equiv \omega_i^2$ for minus legs $i\in M$; $\quad b_j \equiv \omega_j^2$ for plus legs $j\in P$.
- $(x)_+ \equiv \max(x,0)$ (truncated power).
- Symmetric invariants on the resonant manifold ($\textstyle\sum_i\omega_i=0$,
  $\sum_i\sigma_i\omega_i^2=0$, so $e_1^+=-e_1^-$ and $e_2^+=e_2^-$):
  $$e_1\equiv e_1^+ = -e_1^-,\qquad e_2\equiv e_2^+=e_2^-,\qquad e_3^-=\omega_1\omega_2\omega_3,\qquad e_3^+=\omega_4\omega_5\omega_6 .$$

---

## The numerator $N_6$ — a degree-11 truncated-power (box) spline

$$
N_6 \;=\; B
\;+\!\!\sum_{i\in M,\,j\in P}\!\! (b_j-a_i)_+\,P_{ij}
\;+\!\!\sum_{\substack{i\ne k\in M\\ j\ne l\in P}}\!\!\! (b_j-a_i)_+\,(b_l-a_k)_+\,R_{ij,kl}
\;+\!\!\sum_{\substack{i\in M\\ \{j,k\}\subset P}}\!\! (a_i-b_j-b_k)_+^{3}\,Q_{ijk}.
$$

| term | wall | exponent | coefficient |
|---|---|--:|---|
| base | (smooth) | — | $B$ (deg 11) |
| single $(1{=}1)$ | $a_i=b_j$ | $1$ | $P_{ij}$ (deg 9) |
| matching-pair $(1{=}1)$ | $a_i=b_j$ **and** $a_k=b_l$ (disjoint edges) | $(1,1)$ | $R_{ij,kl}$ (deg 7) |
| $(1{=}2)$ | $a_i=b_j+b_k$ | $3$ | $Q_{ijk}$ (deg 5) |

$N_6$ has degree $11$, is **odd** under $\omega\to-\omega$, is $S_3\wr Z_2$-symmetric, and is
**continuous** across every wall (the kinks are finite — not poles). A matching-**triple**
cross-term is *not* needed (verified: it adds nothing to the span).

**Orbit construction.** $B$, $P$, $R$, $Q$ below are written for one *reference* wall/pair;
the coefficients $P_{ij}$, $R_{ij,kl}$, $Q_{ijk}$ for every other wall are the images of the
reference under the relabeling $g\in G=S_3(\text{minus})\times S_3(\text{plus})\rtimes Z_2$
($|G|=72$) that carries the reference wall to the target. The assembled $N_6$ is the full
$G$-orbit sum and is symmetric by construction; the exact bookkeeping is in
`r6_closedform.py` (which applies all $72$ relabelings). A **gauge freedom** exists
(using $(k)_+=\tfrac12(|k|+k)$ one may shift smooth parts between $B$ and the truncated-power
coefficients); what is gauge-invariant is the *structure*, the *exponents*, the wall *jumps*,
and the assembled $N_6$.

---

## Reference coefficient polynomials (explicit)

### Base $B$ (degree 11, $S_3\wr Z_2$-symmetric)

$$B=(e_3^-+e_3^+)\,\frac{\tilde B}{5},$$
$$
\begin{aligned}
\tilde B =\;& 5e_1^{6}e_2 - 64e_1^{5}e_3^- + 64e_1^{5}e_3^+ - 125e_1^{4}e_2^{2}
+ 395e_1^{3}e_2 e_3^- - 395e_1^{3}e_2 e_3^+ \\
&+ 910e_1^{2}e_2^{3} - 870e_1^{2}(e_3^-)^{2} - 2660e_1^{2}e_3^- e_3^+ - 870e_1^{2}(e_3^+)^{2} \\
&+ 1485e_1 e_2^{2}e_3^- - 1485e_1 e_2^{2}e_3^+ + 80e_2^{4}
+ 600e_2(e_3^-)^{2} - 855e_2 e_3^- e_3^+ + 600e_2(e_3^+)^{2}.
\end{aligned}
$$
The explicit factor $(e_3^-+e_3^+)$ means the base contributes **no** residue at the pole.

### Single $(1{=}1)$ coefficient $P^0$ (degree 9)

Reference wall $\{a_1=b_4\}$. Spectator variables: $A_1=\omega_2+\omega_3$,
$A_2=\omega_2\omega_3$ (other minus legs), $B_1=\omega_5+\omega_6$, $B_2=\omega_5\omega_6$
(other plus legs), $y=\omega_4$ (in this gauge $P^0$ does not contain $x=\omega_1$). For a
general wall $\{a_i=b_j\}$, take $A_{1,2}$ over the other two minus legs, $B_{1,2}$ over the
other two plus legs, $y=\omega_j$.

$$
\begin{aligned}
P^0=\frac{1}{20}\Big(&
-10A_1^{3}A_2B_1^{4} + 5A_1^{2}A_2^{2}B_1^{3} + 40A_1^{2}A_2B_1^{3}B_2 + 5A_1^{2}B_1^{5}B_2
- 40A_1^{2}B_1^{3}B_2^{2} \\
&+ 90A_1A_2^{3}B_1^{2} + 55A_1A_2^{2}B_1^{4} - 140A_1A_2^{2}B_1^{2}B_2 + 5A_1A_2B_1^{6}
- 40A_1A_2B_1^{4}B_2 \\
&+ 50A_1A_2B_1^{2}B_2^{2} - 5A_1B_1^{4}B_2^{2} + 65A_1B_1^{2}B_2^{3}
- 60A_2^{4}B_1 - 45A_2^{3}B_1^{3} + 25A_2^{3}B_1B_2 \\
&+ 15A_2^{2}B_1^{5} - 50A_2^{2}B_1^{3}B_2 + 80A_2^{2}B_1B_2^{2} - 5A_2B_1^{3}B_2^{2}
- 115A_2B_1^{2}B_2^{2}y \\
&- 180A_2B_1B_2^{3} - 85A_2B_1B_2^{2}y^{2} - 100A_2B_2^{3}y
- 18B_1^{5}B_2^{2} + 60B_1^{3}B_2^{3} + 10B_1^{3}B_2^{2}y^{2} \\
&+ 135B_1^{2}B_2^{3}y + 10B_1^{2}B_2^{2}y^{3} + 25B_1B_2^{4} + 70B_1B_2^{3}y^{2}
- 30B_2^{4}y + 30B_2^{3}y^{3} + 2B_2^{2}y^{5}\Big).
\end{aligned}
$$

### Matching-pair $(1{=}1)$ coefficient $R^0$ (degree 7)

Reference disjoint pair $\{a_1=b_4\}\,\&\,\{a_2=b_5\}$ (matched edges $1\!\to\!4$, $2\!\to\!5$;
leftover minus leg $3$, leftover plus leg $6$); raw variables $\omega_1,\dots,\omega_6$. Note
the overall $\omega_6^2$ (leftover-plus-leg squared) factor. For a general disjoint pair,
relabel $(1,2,3)\to(i,k,m)$ and $(4,5,6)\to(j,l,n)$ with $m$ the leftover minus leg and $n$
the leftover plus leg.

$$
\begin{aligned}
R^0=\frac{\omega_6^{2}}{10}\Big(&
10\,\omega_2\omega_3\omega_5\omega_6^{2} + 20\,\omega_2\omega_5^{4} + 30\,\omega_2\omega_5^{3}\omega_6
+ 50\,\omega_2\omega_5^{2}\omega_6^{2} + 30\,\omega_2\omega_5\omega_6^{3} \\
&+ 5\,\omega_3^{3}\omega_6^{2} + 50\,\omega_3^{2}\omega_5\omega_6^{2} + 20\,\omega_3^{2}\omega_6^{3}
+ 80\,\omega_3\omega_4\omega_5^{2}\omega_6 + 65\,\omega_3\omega_4\omega_5\omega_6^{2} \\
&+ 40\,\omega_3\omega_5^{3}\omega_6 + 90\,\omega_3\omega_5^{2}\omega_6^{2} + 90\,\omega_3\omega_5\omega_6^{3}
+ 15\,\omega_3\omega_6^{4} - 30\,\omega_4\omega_5^{3}\omega_6 \\
&+ 50\,\omega_4\omega_5^{2}\omega_6^{2} + 20\,\omega_4\omega_5\omega_6^{3}
+ 18\,\omega_5^{5} + 30\,\omega_5^{4}\omega_6 + 70\,\omega_5^{3}\omega_6^{2}
+ 90\,\omega_5^{2}\omega_6^{3} + 40\,\omega_5\omega_6^{4} + 9\,\omega_6^{5}\Big).
\end{aligned}
$$

### $(1{=}2)$ coefficient $Q$ (degree 5)

Reference wall $\{a_i=b_j+b_k\}$: minus leg $i$, plus pair $\{j,k\}$, excluded plus leg $l$,
other two minus legs $p,q$. Variables $A_1=\omega_p+\omega_q$, $A_2=\omega_p\omega_q$,
$B_1=\omega_j+\omega_k$, $B_2=\omega_j\omega_k$, $y=\omega_l$ (this gauge has no $\omega_i$).
The jump of $N_6$ across the wall is $(a_i-b_j-b_k)^3\,Q$.

$$
\boxed{\,Q = A_2 B_1\big(y^{2}-A_1^{2}-A_1B_1+A_2-B_2\big) + B_2\,y\big(A_2-B_1 y - B_2\big)\,}
$$
expanded,
$$
Q = -A_1^{2}A_2B_1 - A_1A_2B_1^{2} + A_2^{2}B_1 - A_2B_1B_2 + A_2B_1y^{2} + A_2B_2y
- B_1B_2y^{2} - B_2^{2}y .
$$
$Q$ is degree $5$, odd under $\omega\to-\omega$, and $S_2(\{p,q\})\times S_2(\{j,k\})$-symmetric.

---

## $n=5$ (for reference — polynomial, no denominator)

The same sector at $n=5$ (minus legs $1,2,3$; plus legs $4,5$) is the two-minus law on the
sign-flipped configuration (the plus/minus swap), degree-6, continuous:
$$
A_5 = i\,2^{4}\,g^{-2}\,\omega_4\omega_5\sum_{S\subseteq\{1,2,3\}}(-1)^{|S|}\Big(\beta^2-\textstyle\sum_{j\in S}\omega_j^2\Big)_+^{2},\qquad \beta=\min(|\omega_4|,|\omega_5|).
$$

---

## Verification & reproduction

PI independent check (`bots/pi/code/pi_r7_independent.py`, `pi_r7_walls.py`, own oracle + own
orbit-sum/assembly, only the published polynomials taken as the candidate): $140/140$ generic
points across $58$ chamber labels exact; $6/6$ non-generic (one frequency $\gg/\ll$ rest);
$3/3$ $g$-homogeneity ($g=2,\tfrac13,\tfrac72$); two-sided limits onto a $(1{=}1)$, a $(1{=}2)$,
and a matching corner all exact to $\varepsilon=10^{-4}$ (finite kinks, not poles).

```
cd bots/student-1/code
g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp
python3 r6_closedform.py    # self-contained A_6 evaluator vs the oracle (exact)
python3 r6_verify.py        # 16/16 across 8 chamber types + two-sided wall limits
# explicit polynomials: r6_polys.txt (B, P0, R0) and r5_corr.py / round-5 derivation (Q)
```
