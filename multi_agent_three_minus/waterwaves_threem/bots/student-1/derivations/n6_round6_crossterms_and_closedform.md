# n=6 three-minus, round 6: the (1=1) cross-terms are matching PAIRS (exp 1,1), and the FULL closed form for $N_6$

**student-1, round 6 (2026-06-27).** All exact-rational against my own copy of
`bg.cpp` (`bots/student-1/code/bg.cpp`; shared oracle untouched), independently
cross-checked by the native-Python BG port `pybg.py` (== `./bg` at n=5,6,7).

## 0. Result (headline)

The numerator $N_6 = A_6\,(e_3^-+e_3^+)/(i\,2^5 g^{-3})$ is an explicit
truncated-power (box) spline. Writing $a_i=\omega_i^2$ (minus legs $i\in M=\{1,2,3\}$),
$b_j=\omega_j^2$ (plus legs $j\in P=\{4,5,6\}$), $(x)_+=\max(x,0)$:

$$\boxed{\,N_6 = B \;+\; \sum_{i\in M,\,j\in P}(b_j-a_i)_+\,P_{ij}
 \;+\!\!\sum_{\substack{i\ne k\in M\\ j\ne l\in P}}\!\!(b_j-a_i)_+(b_l-a_k)_+\,R_{ij,kl}
 \;+\; \sum_{\substack{i\in M\\ \{j,k\}\subset P}}(a_i-b_j-b_k)_+^{3}\,Q_{ijk}\,}$$

and then $A_6 = i\,2^5 g^{-3}\,N_6/(e_3^-+e_3^+)$, $e_3^-=\omega_1\omega_2\omega_3$,
$e_3^+=\omega_4\omega_5\omega_6$.

- **(1=1) single walls** $\{a_i=b_j\}$: truncated power **exponent 1**, coefficient
  $P_{ij}$ (degree 9), the $S_3\times S_3$-orbit image of a reference $P^0$.
- **(1=1) matching PAIRS** $\{a_i=b_j\}\cap\{a_k=b_l\}$ ($i\ne k$, $j\ne l$, i.e. two
  *disjoint* mixed edges — which on the manifold force the third edge, completing a
  perfect matching): a **2-wall product, exponent (1,1)**, coefficient $R$ (degree 7),
  the orbit image of a reference $R^0$. **This is the box-spline cross-term** (s1_014/s1_016).
- **(1=2) walls** $\{a_i=b_j+b_k\}$: exponent **3**, coefficient $Q_{ijk}$ (degree 5),
  the PI-verified explicit polynomial (s1_015).
- $B$ = smooth $S_3\wr Z_2$-symmetric base (degree 11), a polynomial in the four
  invariants $(e_1,e_2,e_3^-,e_3^+)$.

**No matching-TRIPLE product** $(b_j-a_i)_+(b_l-a_k)_+(b_n-a_m)_+$ is needed: triple
columns add nothing to the span (verified). So the (1=1) box spline is **second order**
(pairwise cross-terms close it).

The closed form is **VERIFIED EXACTLY** against `./bg` and `pybg`: 16/16 generic points
across 8 distinct chamber types, residual 0; and two-sided limits onto a (1=1) wall, a
(1=2) wall, and a matching corner all match `./bg` exactly at $\varepsilon=10^{-1},10^{-2},10^{-3}$
(the form is finite and continuous through every wall). Self-contained evaluator:
`bots/student-1/code/r6_closedform.py`.

## 1. How the cross-term form was found (the key measurement)

The decisive step was to measure the (1=1) single-wall jump *coefficient* as a function
of position along the wall, and watch it cross a matching sub-wall.

**Setup (`r6_xt2.py`/`r6_xt4.py`).** On an F-constant slice with $w_2,w_3$ fixed and
base $(a,b)=(w_2,w_5^\star)$, at $t=0$ one is exactly on the wall $\{a_2=b_4\}$
($w_4=w_2$) with $w_5=w_5^\star$; $\sum_{\rm free}\omega$ is fixed so $N(t)$ is polynomial
in $t$ on each side. The jump across $t=0$ is $N_R-N_L=k_{24}(t)\,P_{24}(t)$,
$k_{24}=t(2w_2+t)$, and $P_{24}(0)$ is the on-wall jump coefficient at the wall point
$(w_2,w_3,w_4{=}w_2,w_5{=}w_5^\star)$.

**Scanning $w_5^\star$ across the matching sub-wall $\{a_3=b_5\}$** (at $w_5^\star=w_3$;
note on $\{a_2=b_4\}$ this forces $a_1=b_6$, completing the matching $2{\to}4,3{\to}5,1{\to}6$):
exact per-side rational reconstruction gives $P_{24}$ as **two different** rational
functions of $w_5$, and their difference factors as
$$P_{24}^{R}-P_{24}^{L}=\frac{270\,S\,(S-5)(S+5)(11S+73)(S^2+11S+48)}{(S+11)^2},\qquad S=w_5,$$
with $(S-5)(S+5)=w_5^2-w_3^2=k_{35}$ **to the first power** (no further $(S\mp 5)$ factor).
So the single-wall coefficient $P_{24}$ **kinks** across the matching partner $\{a_3=b_5\}$,
with jump $=k_{35}\cdot R$, $R$ a polynomial. Hence $N_6$ carries a term
$(k_{24})_+(k_{35})_+R$: a **2-wall product, each exponent 1**. (`r6_xt3.py`,`r6_xt4.py`.)

This both *proves* the cross-term (overturning the simple single-wall sum, s1_014, with a
direct measurement) and *pins its form* (a matching-pair product, not an arbitrary wall
pair; cf. s1_016).

## 2. Global determination (rank-100 exact fit) and "no triple"

Working with $M=N_6-\sum_{(1=2)}(a_i-b_j-b_k)_+^3 Q_{ijk}$ (the PI-verified $Q$ subtracted;
$M$ is a pure (1=1) spline, (1=2)-smooth — re-confirmed `r5_corr.py`), I tested whether
$$M \overset{?}{=} \text{base}(B)\;+\;\text{single}(1{=}1)\;+\;\text{pair}(1{=}1)\;+\;\text{triple}(1{=}1)$$
via an EXACT modular fit (`r6_fit.py`, $p=2^{61}-1$, EXACT relu from Fraction signs), each
level built as the full-group ($|G|=72$) orbit-sum of a reference truncated-power product
times template monomials (base: 12 $G$-symmetric odd deg-11 invariant classes; single:
$(k_{03})_+\times$ deg-9 mode-$P$ templates; pair: $(k_{03})_+(k_{14})_+\times$ deg-7
monomials; triple: $(k_{03})_+(k_{14})_+(k_{25})_+\times$ deg-5 monomials). Greedy
rank-tracking with held-out (340 points):

| level | rank after | added |
|---|---|---|
| base | 12 | 12 |
| + single (1=1) | 67 | **+55** |
| + pair (1=1) | 100 | **+33** |
| + triple (1=1) | 100 | **+0** |

$M$ is **CONSISTENT** (in the span) with rank 100 and a 240-point margin. The **triple
adds nothing** — matching-triple products lie in the span of base+single+pair, so the
(1=1) box spline closes at pairwise cross-terms. Then I solved the rank-100 system mod $p$
and **rational-reconstructed all 100 coefficients exactly** (`r6_extract.py`).

## 3. Explicit reference coefficient polynomials

(Representatives; the decomposition has the usual gauge freedom $(k)_+=\tfrac12(|k|+k)$,
so the smooth parts can be shifted between $B$ and the truncated-power coefficients. What
is gauge-invariant: the structure, the exponents, the wall *jumps*, and the assembled
$N_6$.) Full text in `code/r6_polys.txt`.

- **Base** $B=(e_3^-+e_3^+)\cdot\tilde B/5$ with
  $\tilde B = 5e_1^6e_2-64e_1^5e_3^-+64e_1^5e_3^+-125e_1^4e_2^2+395e_1^3e_2e_3^-
  -395e_1^3e_2e_3^++910e_1^2e_2^3-870e_1^2(e_3^-)^2-2660e_1^2e_3^-e_3^+-870e_1^2(e_3^+)^2
  +1485e_1e_2^2e_3^--1485e_1e_2^2e_3^++80e_2^4+600e_2(e_3^-)^2-855e_2e_3^-e_3^++600e_2(e_3^+)^2$.
  (Here $e_1=e_1^+=-e_1^-$, $e_2=e_2^+=e_2^-$.) Note the explicit $(e_3^-+e_3^+)$ factor:
  the base contributes **no** residue at the pole (the pole/residue lives entirely in the
  truncated-power terms, which are nonzero on $\{e_3^-+e_3^+=0\}$).
- **Single (1=1)** coefficient, reference wall $\{a_1=b_4\}$, in
  $x{=}\omega_1,y{=}\omega_4,A_1{=}\omega_2{+}\omega_3,A_2{=}\omega_2\omega_3,
  B_1{=}\omega_5{+}\omega_6,B_2{=}\omega_5\omega_6$: $P^0$ is a degree-9 polynomial
  (34 monomials), e.g. $P^0=\tfrac1{20}\big(-10A_1^3A_2B_1^4+5A_1^2A_2^2B_1^3+\dots+2B_2^2y^5\big)$.
- **Pair (1=1)** coefficient, reference pair $\{a_1=b_4\}\&\{a_2=b_5\}$ (leftover minus
  leg 3, plus leg 6): $R^0=\omega_6^2\cdot\tfrac1{10}\big(10\omega_2\omega_3\omega_5\omega_6^2
  +20\omega_2\omega_5^4+\dots+9\omega_6^5\big)$ (degree 7, 23 monomials). Note the explicit
  $\omega_6^2$ factor (the leftover plus leg squared).
- **(1=2)** coefficient $Q$: the PI-verified s1_015 polynomial.

## 4. Verification (exact)

`r6_verify.py` (one command, uses my own `./bg` and `pybg`):
- 16/16 generic points, **8 distinct chamber types**, formula $=$ `./bg` $=$ `pybg`, residual 0.
- Two-sided limits, $\varepsilon\in\{10^{-1},10^{-2},10^{-3}\}$, formula $=$ `./bg` exactly on
  BOTH sides of: a (1=1) wall ($w_4\to w_2$), a (1=2) wall ($w_4^2\to w_2^2+w_3^2$), and a
  matching corner ($w_4\to w_2$ & $w_5\to w_3$). Continuous, finite (kinks, no poles) — as
  required (the oracle SIGFPEs *on* the wall; the closed form is exact there as a limit).
- `r6_closedform.py` (self-contained evaluator) reproduces `./bg` exactly.

## 5. Reproduce

```
cd bots/student-1/code
g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp
python3 r6_xt4.py        # the cross-term measurement: P_24 kinks; jump = k_35 * R (exp 1)
python3 r6_fit.py 340    # structure: base+single+pair = rank 100 CONSISTENT; triple +0
python3 r6_extract.py    # 100 exact coefficients (rational-reconstructed); 13/13 exact
python3 r6_coeffpoly.py  # explicit B, P0, R0 polynomials -> r6_polys.txt
python3 r6_verify.py     # 16/16 across 8 chamber types + 3 two-sided wall limits (vs ./bg & pybg)
python3 r6_closedform.py # self-contained A_6 evaluator
```

## 6. Status / open

- **CLOSED & VERIFIED:** the full $n=6$ three-minus amplitude — explicit truncated-power
  (box) spline numerator $N_6$ over the minimal denominator $(e_3^-+e_3^+)$, all
  coefficients exact, validated against the oracle generically, across chamber types, and
  through every wall as a two-sided limit.
- **The (1=1) cross-term question (the round-5/6 open frontier) is RESOLVED:** matching
  *pairs* (exp 1,1), no triples.
- **OPEN (all-$n$):** generalize to $n\ge7$. The structure should be: base + single(1=1)
  + pair(1=1) + (1=2)$^3$ + (1=3)$^?$ + higher cross-terms, over the denominator
  $\mathrm{Res}(p_-,Q_n)$ (minimal $n\ne6$ denominator still open, student-2). Whether
  matching-triple cross-terms appear at $n\ge7$ (more plus legs) is the first thing to check.
