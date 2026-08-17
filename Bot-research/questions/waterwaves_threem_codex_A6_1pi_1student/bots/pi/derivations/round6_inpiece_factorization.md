# PI round 6 — exact in-piece reconstruction and factorization of $H$

Timestamp: 2026-07-26T17:03:58 UTC. All exact (fresh `bg_r6`, GMP rational),
verified by exact `Fraction` arithmetic (not just modular).

## Method (why this succeeded where pi_v_019 stalled)

$H=A_6/(i\prod_k\omega_k)$ is exactly degree-2 homogeneous [pi_v_012], and **all
53 surfaces** (18 walls + 35 factorization surfaces $h_S$) are homogeneous of
degree 2, so **one true piece is a cone**. Scale each point to $\omega_2=1$:
with $x=\omega_3/\omega_2,\ y=\omega_4/\omega_2,\ z=\omega_5/\omega_2$ the target
$$h(x,y,z)\equiv H/\omega_2^2$$
is an **inhomogeneous rational function of only 3 variables**. This collapses the
4-variable degree-$\le d$ fit (pi_v_019, which died before reaching the needed
degree) to a tractable 3-variable one. Fit $h=P/Q$ by a modular null-space search
of $[\,M_{\le d}\mid -h\,M_{\le d}\,]$; the minimal $d$ with a null vector gives
$\deg P$; extract the unique null vector, CRT + rational-reconstruct over 5 primes,
and **factor** $Q$.

Code: `bots/pi/code/round6_reconstruct.py` (collect + rank scan),
`round6_extract_np.py` (multi-prime null vector, CRT, exact validation, factor).
Evidence: `round6_scan.out`, `round6_QP.txt` (piece A); `round6_scan_B.out`,
`round6_QP_B.txt` (piece B); points in `round6_points{,_B}.json`.

## Result — two independent true pieces, each exact on 1000 points

Rank scan finds a rational representation only at high degree and **nowhere
below** (monotone): piece A first at $d=12$, piece B at $d=11$; the homogeneous
in-piece denominator has degree **10** in both. Extraction + `sympy.factor`, with
**exact `Fraction` validation 1000/1000 (bad=0)** against `bg_r6`:

Chart variables $x=\omega_3/\omega_2,\ y=\omega_4/\omega_2,\ z=\omega_5/\omega_2$
(free legs $2,3$ minus; $4,5$ plus; legs $1,6$ eliminated by conservation).

- **Piece A** (base $\omega=(-7,9,-8,-3,-4,13)$):
  $$Q_A\ \propto\ x\,(x+y)(x+z)(y+1)(z+1)\,Q_a\,Q_b .$$
- **Piece B** (base $\omega=(-13,4,3,8,7,-9)$):
  $$Q_B\ \propto\ y\,z\,(x+y)(x+z)(y+1)(z+1)\,Q_a\,Q_b .$$

with the **same two irreducible quadratics in both pieces**
$$Q_a=x^2+xy+xz+x+yz+y+z+1,\qquad Q_b=xy+xz+x+y^2+yz+y+z^2+z .$$

## Homogenized building blocks (signed frequencies)

Multiplying each factor by the appropriate power of $\omega_2$ (chart legs
$2,3$ minus, $4,5$ plus):

| chart factor | homogeneous | type |
|---|---|---|
| $x$        | $\omega_3$ | single minus leg |
| $y,\ z$    | $\omega_4,\ \omega_5$ | single plus legs |
| $x+y$      | $\omega_3+\omega_4$ | mixed pair sum |
| $x+z$      | $\omega_3+\omega_5$ | mixed pair sum |
| $y+1$      | $\omega_2+\omega_4$ | mixed pair sum |
| $z+1$      | $\omega_2+\omega_5$ | mixed pair sum |
| $Q_a$      | $e_2(\omega_2,\omega_3,\omega_4,\omega_5)+\omega_2^2+\omega_3^2$ | irreducible quadratic |
| $Q_b$      | $e_2(\omega_2,\omega_3,\omega_4,\omega_5)+\omega_4^2+\omega_5^2$ | irreducible quadratic |

Pulling the $\omega_2$ back through $H=P_h/(\omega_2 Q_h)$, the **homogeneous
in-piece denominator of $H$** is
$$D=\big(\text{chamber-selected single legs }\textstyle\prod\omega_i\big)\times
(\omega_3+\omega_4)(\omega_3+\omega_5)(\omega_2+\omega_4)(\omega_2+\omega_5)\times Q_a Q_b,$$
degree $10$ in both pieces. The **four mixed-pair factors and the two quadratics
are chart-universal (identical in A and B)**; only the **single-leg product is
chamber-dependent** (A: $\{\omega_3\}$; B: $\{\omega_4,\omega_5\}$ — up to the
$\omega_2$ carried by $H=P_h/(\omega_2Q_h)$, the single-leg content is
$\{\omega_2,\omega_3\}$ vs $\{\omega_2,\omega_4,\omega_5\}$).

## Physical identity of the universal quadratics (verified symbolically)

With $S=\{2,3,4,5\}=\{1,6\}^c$, $\omega_S=\omega_2+\omega_3+\omega_4+\omega_5$,
$g\,k_S=\omega_4^2+\omega_5^2-\omega_2^2-\omega_3^2$:
$$Q_a+Q_b=\omega_S^2,\qquad 4\,Q_aQ_b=\omega_S^4-k_S^2=h_S\,(\omega_S^2+|k_S|),
\quad h_S=\omega_S^2-|k_S|.$$
So $Q_a,Q_b$ are the two sign-branches of the **complementary internal-line
inverse propagator $h_{\{2,3,4,5\}}=h_{\{1,6\}}$**; their product carries the
**removable factorization surface** $h_S$. Since $A_6$ is finite at $h_S=0$
[pi_v_006], the numerator $P$ must vanish on the active branch — removability
made explicit.

## Why every prior denominator search failed (resolves the round-5 puzzle)

The genuine denominator factors are **signed** — single legs $\omega_i$, mixed
pair sums $\omega_i+\omega_j$, and the two signed quadratics $Q_a,Q_b$. Every
excluded family [s1_015, pi_v_017, pi_v_019] was built from **even** blocks
($a_i\pm b_j$, $a_i+a_j$, $T$, $p$, $\omega_i\omega_j$): those are the wrong
parity, so no product of them can clear $H$. The single-$Q$ picture was not dead
— it was being searched in the wrong (even) ring.

## Numerator (piece A, for the record)

$\deg P=12$; `factor(P_A)` $= y\,z\,(x+y+z+1)\cdot(\text{irreducible deg-8})/2$,
i.e. plus-leg singles $\omega_4\omega_5$, the total $x+y+z+1=\omega_S/\omega_2$,
and a degree-8 core. The **compactness of that degree-8 core is the remaining open
problem** (see task). Under minus$\leftrightarrow$plus swap the single-leg content
trades between $P$ and $Q$ (A's $Q$ has $\omega_3$-type minus singles; its $P$ has
$\omega_4\omega_5$ plus singles), consistent with pi_v_005 symmetry.

## Status

VERIFIED (exact, 2 independent chambers, 1000 pts each): the in-piece $H=P/Q$ with
the factored degree-10 signed denominator above. OPEN (student): the chamber
selection rule for the single-leg factors, the chart-independent symmetric
statement, and the compact structure of the degree-8 numerator core.
