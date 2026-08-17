# n=7 three-minus, round 8: corrected single-wall exponents, the cross-term mechanism, and the cross-term closing order

**student-1, round 8 (2026-06-27).** Exact-rational against my own copy of `bg.cpp`
(`bots/student-1/code/bg.cpp`; shared oracle untouched); the heavier modular work uses a
new fast finite-field oracle `bgmod` (validated == `./bg` reduced mod p at n=5,6,7) and the
Python cross-check `modbg`.

Sector n=7: minus legs {1,2,3}, plus legs {4,5,6,7}. Fixed (PI-verified) framing:
$$A_7 = i\,2^{6}g^{-4}\,\frac{N_7}{D_7},\qquad D_7=\prod_{i\in M,j\in P}(\omega_i+\omega_j)\ (12\text{ pairs, pole order }1),\qquad \deg N_7 = 5n-13 = 22,$$
$N_7$ EVEN under $\omega\to-\omega$, $S_3(\text{minus})\times S_4(\text{plus})$-symmetric (NO $Z_2$ at $n\ge7$).
$a_i=\omega_i^2$ (minus), $b_j=\omega_j^2$ (plus), $(x)_+=\max(x,0)$.

## 0. Headline — s1_022 is CORRECTED

Round 7 (s1_022) conjectured: the *pure* single-wall (1=2) exponent is $n-3=4$, and the
observed jump order 2 is a $(1{=}1)\times(1{=}1)$ matching cross-term forced onto the (1=2)
wall. **This is wrong.** The observed orders ARE the pure exponents:
$$\boxed{(1{=}1)\to 1,\qquad (1{=}2)\to 2,\qquad (1{=}3)\to 4\ (=n-3)\quad\text{at }n=7,}$$
each a *clean, chamber-independent* truncated-power coefficient (the jump divides exactly by
$(\text{wall fn})^{e}$). The forcing $(1{=}1)^2$ cross-term contributes **nothing** at a generic
(1=2) crossing — see §2.

## 1. The wall map (re-confirmed) and exact exponents

42 mixed walls $= (1{=}1)[12]\cup(1{=}2)[18]\cup(1{=}3)[12]$ (one minus-singleton canonical form
per wall; the $(2{=}\cdot)$ complements are the same loci).

On clean **single-wall** ($sd=1$) crossings, fitting $N_7(t)$ exactly on each side and reading the
order of $J=N_R-N_L$ AND verifying $J/(\text{wall fn})^{e}$ is an exact polynomial (`r8_e13.py`,
exact `./bg`; `r8_xterm_diag.py`, exact `./bg`):

| wall | jump order | $J/v^e$ exact-divides | clean coeff? |
|---|---|---|---|
| (1=1) $a_i=b_j$ | 1 | yes ($e=1$) | yes |
| (1=2) $a_i=b_j+b_k$ | 2 | yes ($e=2$) | yes |
| (1=3) $a_i=b_j+b_k+b_l$ | 4 | yes ($e=4$) | yes |

n=6 controls reproduce $(1{=}1)\to1$, $(1{=}2)\to3$.

## 2. Why the $(1{=}1)^2$ cross-term does NOT lower the (1=2) order — the $X+Y=v$ mechanism

Take the (1=2) wall $W:\ a_2=b_4+b_5$, coordinate $v:=a_2-b_4-b_5$ ($v=0$ on $W$). The only
$(1{=}1)^2$ cross-term whose forced locus is $W$ uses the complementary legs: minus $\{1,3\}$,
plus $\{6,7\}$, i.e. $(b_6-a_1)_+(b_7-a_3)_+$ (and the $6\leftrightarrow7$ partner). From the
manifold sum rule $a_1+a_2+a_3=b_4+b_5+b_6+b_7$,
$$X+Y:=(b_6-a_1)+(b_7-a_3)=(b_6+b_7)-(a_1+a_3)=a_2-b_4-b_5=v.$$
ON $W$ ($v=0$): $X=-Y$. At a **generic** wall point $X_0\ne0$, so in a whole neighbourhood one of
$X,Y$ stays $<0$ $\Rightarrow$ $(X)_+(Y)_+\equiv0$ locally $\Rightarrow$ **the cross-term is smooth (zero)
across $W$ and contributes no jump**. (It only "wakes up" at the codim-2 corner $X_0=Y_0=0$, i.e.
$a_1=b_6,\ a_3=b_7$.) Numerically confirmed: at 4 distinct generic (1=2) crossings, BOTH forcing
matchings give $X,Y$ of opposite sign throughout, product $=0$ (`r8_xterm_diag.py`).

Hence the measured $(1{=}2)\to2$ is the genuine pure exponent, with a clean coefficient
$(a_i-b_j-b_k)_+^{2}\tilde Q$. (At n=6 the (1=2) wall has no such forcing pair — its complement
$(2{=}1)$ has only one plus leg — so n=6 gives the clean $(1{=}2)\to3=n-3$.)

## 3. Cross-term closing order at n=7 (deliverable 2)

Using only the manifold sum rule $\sum_M a=\sum_P b$ (verified):

- **(1=1) box-spline closes at PAIRS — no triples.** Three disjoint (1=1) edges
  $\{a_1=b_4,a_2=b_5,a_3=b_6\}$ sum to $a_1+a_2+a_3=b_4+b_5+b_6$, but $\sum a=\sum b=b_4+b_5+b_6+b_7$,
  forcing $b_7=0$ — a **degenerate** (excluded-plus-leg-vanishes) locus, not a thick codim-3 corner.
  So a triple cross-term has no support; the pure-(1=1) sector closes at pairwise products, exactly
  as at n=6 (where the triple is the $e_3^-+e_3^+=0$ pole locus).
- **(1=1)×(1=2) mixed products are a GENUINELY NEW n≥7 possibility.** A disjoint
  $\{a_1=b_4\}\cap\{a_2=b_5+b_6\}$ corner forces $a_3=b_7$ automatically (codim 2, since $b_7$ stays
  free) — NON-degenerate. At n=6 the analog forces $a_3=0$ (degenerate), which is precisely why
  n=6 needed only (1=1) pairs and clean (1=2). Whether such a mixed cross-term actually appears in
  $N_7$ is settled only by the full modular fit (the one remaining structural unknown).

So the n=7 numerator candidate is
$$N_7 = B + \sum_{(1=1)}(b_j-a_i)_+P + \sum_{\substack{\text{disjoint}\\(1=1)\text{ pairs}}}(b_j-a_i)_+(b_l-a_k)_+R
 + \sum_{(1=2)}(a_i-b_j-b_k)_+^{2}\tilde Q + \sum_{(1=3)}(a_i-b_j-b_k-b_l)_+^{4}S\ \big[+\ (1{=}1)\times(1{=}2)?\big].$$

## 4. The clean (1=3) coefficient S (deliverable 1)

The (1=3) wall is uncontaminated by any (1=1)-type cross-term (no disjoint (1=1) pair forces it —
that would need the complement (2=1) which has only one free plus), so $(1{=}3)\to4=n-3$ is the
clean subset-sum exponent, the direct n=7 analog of n=6's $Q$ (exponent $n-3=3$).
[Explicit S: see §6 / claims s1_025.]

## 5. Infrastructure: a fast finite-field oracle

The exact GMP oracle is ~1 s/eval at n=7 (bignum blowup) and the Python BG ports are ~23 s/eval
(the n=7 recursion *combinatorics* dominate, NOT the arithmetic — so a Python modular port gives no
speedup). The win is a **compiled finite-field** port `bgmod.cpp`: over $F_p$ there is no bignum
blowup. Two subtleties solved: (i) the BG recursion's `abs()` is taken ONLY of momenta (integer
combos of the external $k_i$), so each field element carries its exact integer coefficient vector
over $K[1..N]$ and `abs` reads the sign EXACTLY (a long-double approximation is NOT safe — internal
recursion momenta can be tiny via cancellation); (ii) the memo key must be the exact residue tuple,
NOT a 64-bit hash (hash collisions corrupted ~10% of evaluations). With both fixed, `bgmod` matches
`./bg` (reduced mod p) at n=5,6,7 across many chamber points and is the engine for the modular
deg-22 fits. `modbg.py` is the (slow) Python cross-check.

## 6. Exponent conjecture for all n (for student-2's lift)

Pure exponents measured: n=5: $n-3=2$ (all subset-sum walls); n=6: $(1{=}1)1,(1{=}2)3$;
n=7: $(1{=}1)1,(1{=}2)2,(1{=}3)4$. These fit
$$e(n,q)=\begin{cases} q & q\le\lfloor (n-3)/2\rfloor\\ n-3 & q>\lfloor (n-3)/2\rfloor\end{cases}\qquad\text{(conjecture)}$$
for a (1=q) minus-singleton wall. Prediction at n=8: $(1{=}1)1,(1{=}2)2,(1{=}3)5,(1{=}4)5$ — a clean
test. The $(1{=}1)\to1$ "anomalous" exponent and the "top wall $\to n-3$" are the robust endpoints.

## 7. Reproduce
```
cd bots/student-1/code
g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp
g++ -O2 -std=c++17 -o bgmod bgmod.cpp -lgmpxx -lgmp
python3 r8_xterm_diag.py   # (1=2)->2 pure: cross-term locally 0, J/v^2 exact-divides
python3 r8_e13.py          # (1=3)->4 clean (J/v^4 divides), (1=1)/(1=2) controls
python3 modbg.py           # modbg == ./bg (mod p), n=5,6,7
```
