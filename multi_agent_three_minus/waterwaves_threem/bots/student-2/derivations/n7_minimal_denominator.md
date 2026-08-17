# Round 6 (student-2, top-down): the all-$n$ minimal denominator, pinned at $n=7$

**One-command check:** `python3 bots/student-2/code/verify_r6.py`
(EXACT rational; own copy of `bg.cpp` via `harness.py`).
Supporting scripts: `n7_denom_algebra.py`, `n7_mindenom.py`, `n7_factorid.py`,
`n7_geom.py`, `alln_denom.py`, `residue_n7.py`.

## 0. Status going in

PI-verified state (round 6 context): $A_n^{3-}=i\,2^{n-1}g^{3-n}\,N_n/D_n^{\min}$.
At $n=6$ the minimal denominator is the single cubic $D_6^{\min}=\omega_1\omega_2\omega_3+
\omega_4\omega_5\omega_6=e_3^-+e_3^+$ to the **first** power; $D_9=\prod_{i\in M,j\in P}
(\omega_i+\omega_j)=(e_3^-+e_3^+)^3$ over-clears. The $n\neq6$ minimal denominator was
**OPEN** (the cube-collapse was known to be special to the equal triples at $n=6$).

This note **resolves the open $n=7$ (and all $n\neq6$) minimal denominator.**

## 1. The all-$n$ denominator mechanism (exact algebra, no oracle)

Write the minus cubic and the plus "sum-polynomial"
$$p_-(x)=\prod_{i\in M}(x-\omega_i)\ (\deg 3),\qquad
  Q_n(x)=\prod_{j\in P}(x+\omega_j)\ (\deg n-3).$$
Then the free product of all $3(n-3)$ mixed-pair sums is a resultant:
$$D_n^{\text{free}}:=\prod_{i\in M}\prod_{j\in P}(\omega_i+\omega_j)
   =\prod_{i\in M}Q_n(\omega_i)=\operatorname{Res}(p_-,Q_n).$$

On the resonant manifold the two conservation laws give $e_1^-=-e_1^+$ and
$e_2^-=e_2^+$ (power-sum identity). Reduce $Q_n$ modulo $p_-$:
$$Q_n(x)=q_n(x)\,p_-(x)+r_n(x),\qquad \deg r_n\le 2,$$
so that $Q_n(\omega_i)=r_n(\omega_i)$ at every minus root and
$$\boxed{\,D_n^{\text{free}}=\prod_{i\in M} r_n(\omega_i)=\operatorname{Res}(p_-,r_n).\,}$$
Verified exact at 5 generic on-shell points each for $n=6,7,8$ (`n7_denom_algebra.py`,
`alln_denom.py`, part A of `verify_r6.py`).

**The collapse is controlled by $\deg r_n$:**

| $n$ | $\deg Q_n$ | $\deg r_n$ | $D_n^{\text{free}}$ on manifold | minimal denominator |
|----|----|----|----|----|
| 5  | 2 | 2 | $\prod_i r_5(\omega_i)$ (deg 6) | (cancels: $A_5$ polynomial) |
| **6**  | 3 | **0** | $(e_3^-+e_3^+)^3$ (perfect cube) | $(e_3^-+e_3^+)^1$, pole order 1 |
| 7  | 4 | 1 | $\prod_i(c\,\omega_i+d)$ (deg 12) | **full product, pole order 1** |
| 8  | 5 | 2 | $\prod_i r_8(\omega_i)$ (deg 15) | full product, pole order 1 |
| $\ge9$ | $n-3$ | 2 | (deg $3(n-3)$) | full product, pole order 1 |

$n=6$ is the **unique** case where $\deg p_-=\deg Q_n=3$, forcing $r_6=Q_6-p_-=
e_3^-+e_3^+$ **constant**, hence the perfect cube and the cube-root minimal
denominator. For every $n\neq6$ (so $\deg r_n\ge1$) the free product is **not** a
perfect power and there is **no collapse**.

### $n=7$ explicitly
With $a$ from $Q_7=(x+a)p_-+r_7$: matching $x^3$ gives $a=e_1^++e_1^-=0$, so
$r_7(x)=Q_7(x)-x\,p_-(x)=c\,x+d$ with
$$c=e_3^-+e_3^+,\qquad d=e_4^+ .$$
Therefore (verified exact)
$$D_7^{\text{free}}=\prod_{i\in M}(c\,\omega_i+d)
   =c^3 e_3^- + c^2 d\,e_2 - c\,d^2 e_1^+ + d^3,\qquad e_2:=e_2^-=e_2^+ .$$

## 2. $n=7$ minimal denominator = the FULL product, pole order 1 (oracle, exact)

Two independent confirmations against `./bg` (own copy), EXACT rational.

**(a) gcd / over-clearing on a single-chamber $F$-const slice** (`n7_mindenom.py`,
`verify_r6.py` B). On a slice held in one chamber, $A_n/i\cdot D_n^{\text{free}}$ is an
exact polynomial $N_{\text{full}}(t)$; the over-clearing $=\deg\gcd(N_{\text{full}},
D_n^{\text{free}})$ measures how much of $D_n^{\text{free}}$ cancels.
- **$n=6$ CONTROL** (collapse known): over-clearing $=8$, reduced denom degree $4$ on
  the slice (= the $(e_3^-+e_3^+)^2$ over-clearing of the cube). The method **detects
  collapse**.
- **$n=7$ TARGET**: over-clearing $=\mathbf{0}$ on **two** different chambers; the
  reduced denominator equals $D_7^{\text{free}}$ (slice degree 14 = the 12 mixed pairs).

**(b) factor identification** (`n7_factorid.py`). On the slice the reduced denominator
factors into exactly the **nine non-constant** slice mixed-pair forms
$(\omega_i+\omega_j)(t)$ — matched factor-by-factor, leftover degree 0 — each to
**power 1**. (Three of the twelve pairs are constant on this particular $F$-const slice:
$(\omega_1+\omega_7)=-\!\sum_{\text{free}}\omega$ and two minus–plus pairs of fixed legs.)

$$\boxed{\,D_7^{\min}=\prod_{i\in M}\prod_{j\in P}(\omega_i+\omega_j)\quad(\deg 12,\ \text{pole order }1).\,}$$
Hence $\deg N_7=(2n-4)+3(n-3)=22$, and the "$\deg N_n=5n-13$" law holds for **all
$n\ge7$**; $n=6$ is the lone exception ($\deg N_6=11$).

## 3. Geometric reason for the $n=6$ vs $n\ge7$ dichotomy

A mixed pair vanishing, $\omega_i+\omega_j=0$, lies on the momentum wall $k_{ij}=
\omega_j^2-\omega_i^2=0$ (the **sum** branch; the difference branch $\omega_i=\omega_j$ is
the kink). 
- **$n=6$:** one pair $\Rightarrow$ a full perfect matching $\Rightarrow$ $e_3^-+e_3^+=0$;
  all nine sum-walls coincide on the single irreducible hypersurface $\{e_3^-+e_3^+=0\}$.
  Minimal denominator $=$ that one cubic.
- **$n=7$:** a single pair vanishes **alone** — `n7_geom.py` exhibits the on-manifold
  point $\omega=(-5,3,8,5,-2,\frac{-9\pm\sqrt{57}}2)$ where only $(1,4)$ vanishes and the
  other eleven pairs do not. So the twelve sum-walls are **distinct** codim-1 loci;
  minimal denominator $=$ their product, pole order 1 on each.

The amplitude remains **finite everywhere physically** (the poles are shielded behind
chamber walls, as established at $n=6$): $\{e_3^-+e_3^+=0\}$ / the matching walls are
reached only outside the physical chambers.

## 4. Boundary / recursion handles (re-confirmed exact)

- **Soft theorem / numerator recursion** (`verify_r6.py` D, `verify_r4.py`):
  $A_n^{3-}\to 2(n-3)\,\omega_p^2 A_{n-1}$ for any external $\omega_p\to0$ (plus leg
  $\to$ three-minus $A_{n-1}$; minus leg $\to$ two-minus). On the numerator, plus-leg
  soft: $N_n\to(n-3)g\,\omega_1\omega_2\omega_3\,\omega_p^2 N_{n-1}^{3-}$ (s2_012).
- **$n=5$ boundary:** $A_5$ equals the known two-minus truncated-power law (D_5 fully
  cancels; soft limit lands here).

## 5. New top-down handle from $n=7$: single-pair residues (`residue_n7.py`)

Because a single pair vanishes alone at $n=7$, the residue $\operatorname{Res}=
\lim_{\omega_i+\omega_j\to0}(\omega_i+\omega_j)A_7$ is accessible by a **one-parameter**
limit (impossible at $n=6$, where every matching point is a triple collision). Extracted
exactly at the linear-factor walls of a chamber; it is **consistent** (equal residues at
walls sharing the same remaining-leg values) but is **not** a naive two-minus
sub-amplitude on the remaining 5 legs (the ratio is not clean) — consistent with the
residue being chamber/branch-dependent (s2_016). This is a usable, novel constraint that
$n=7$ provides for the still-open numerator core.

## 6. What remains OPEN

The explicit numerator $N_n$ (a degree-$5n-13$, $S_3(M)\times S_{n-3}(P)$-symmetric spline
with the now-fixed denominator and the PI-verified $(1{=}2)$ coefficient $Q$). The
denominator, degrees, symmetry, parity, soft recursion, and matching-pole structure are
all pinned for **all $n$**; the $(1{=}1)$ matching cross-term part of the numerator is the
remaining piece (student-1's bottom-up).
