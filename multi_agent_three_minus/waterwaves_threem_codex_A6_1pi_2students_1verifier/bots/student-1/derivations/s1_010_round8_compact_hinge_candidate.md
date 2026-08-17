# Claim `s1_010`: exact compact hinge candidate for the complete \(A_6\)

## Statement

Let
\[
M=\{1,2,3\},\qquad P=\{4,5,6\},\qquad
h_{mp}=(\omega_p^2-\omega_m^2)_+ .
\]
For \(m\in M\), write \(M\setminus\{m\}=\{r,s\}\).  For \(p\in P\),
write \(P\setminus\{p\}=\{t,z\}\), and let
\(\phi:\{r,s\}\widetilde\longrightarrow\{t,z\}\) run over the two
bijections.  Define
\[
\begin{aligned}
R_q={}&4\sum_{m\in M}\sum_{p\in P}
h_{mp}\,H_1\!\left(
\omega_m,\omega_p,\omega_r+\omega_s,\omega_r\omega_s\right)\\
&+2\sum_{m\in M}\sum_{p\in P}\sum_{\phi}
h_{r,\phi(r)}h_{s,\phi(s)}
H_2\!\left(
\omega_m,\omega_p,\omega_r+\omega_s,\omega_r\omega_s,
\omega_r\omega_{\phi(r)}+\omega_s\omega_{\phi(s)}
\right).
\end{aligned}
\]
The two seed polynomials are
\[
\begin{aligned}
H_1(a,b,s,v)=2\big[&
12s^6-21s^5a-22s^5b-115s^4v-48s^4ab-58s^4b^2\\
&+36s^3va+44s^3vb+13s^3a^3+12s^3a^2b-5s^3ab^2-4s^3b^3\\
&+268s^2v^2+25s^2va^2+308s^2vab+323s^2vb^2\\
&-16s^2a^4-66s^2a^3b-62s^2a^2b^2+30s^2ab^3+42s^2b^4\\
&+240sv^2a+240sv^2b-92sva^3+14sva^2b+328svab^2\\
&\quad+222svb^3\\
&-64sa^4b-212sa^3b^2-206sa^2b^3-32sab^4+26sb^5\\
&-8v^3+42v^2a^2+72v^2ab+30v^2b^2\\
&-36va^4-112va^3b-78va^2b^2+36vab^3+38vb^4\\
&+4a^6-44a^4b^2-112a^3b^3-112a^2b^4-40ab^5
\big],
\end{aligned}
\]
and
\[
\begin{aligned}
H_2(a,b,s,v,c)=-4\big[&
4cs^2+4csa+4csb+22ca^2+4cab-22cb^2\\
&+4s^4+4s^3a+4s^3b-8s^2v+12s^2a^2-16s^2b^2\\
&-8sva-8svb+sa^3-9sab^2-4sb^3\\
&-23va^2+19vb^2+12a^4+22a^3b-12a^2b^2-22ab^3
\big].
\end{aligned}
\]

Put
\[
u=\omega_1+\omega_2+\omega_3,\qquad
v=\omega_1\omega_2+\omega_1\omega_3+\omega_2\omega_3,\qquad
e_-=\omega_1\omega_2\omega_3,\qquad
e_+=\omega_4\omega_5\omega_6 .
\]
The global piece is
\[
\begin{aligned}
R_0=H_0(u,v,e_-,e_+)=16\big[&
69e_-^2v-126e_-e_+u^2-18e_-e_+v-40e_-uv^2\\
&+42e_+^2u^2-57e_+^2v-52e_+u^5+204e_+u^3v\\
&\quad-54e_+uv^2\\
&+4u^8-32u^6v+68u^4v^2-16u^2v^3
\big].
\end{aligned}
\]
Then the newly reconstructed regular remainder is
\[
\boxed{S=R_0+R_q.}
\]

For completeness, define
\[
Q_{m;pq}=\omega_p^2+\omega_q^2-\omega_m^2,
\qquad
R_Q=-32\sum_{\substack{m\in M\\\{p,q\}\subset P}}
(Q_{m;pq})_+^3\,\omega_m\omega_t ,
\]
where \(t=P\setminus\{p,q\}\).  Define
\[
\mathcal H(B;c,d)=B-(B-\omega_c^2)_+-(B-\omega_d^2)_+
 +(B-\omega_c^2-\omega_d^2)_+ .
\]
For \(M\setminus\{m\}=\{r,s\}\), \(P\setminus\{p,q\}=\{t\}\), and
\[
d_{m;pq}=2(\omega_m+\omega_p)(\omega_m+\omega_q),
\]
the settled pole part is
\[
\begin{aligned}
P_{\rm pole}=-64
\sum_{\substack{m\in M,\ \{p,q\}\subset P\\Q_{m;pq}>0}}
\frac{\omega_m\omega_tQ_{m;pq}^2}{d_{m;pq}}\,
&\mathcal H\!\left(\min(\omega_m^2,Q_{m;pq});p,q\right)\\
\times{}&
\mathcal H\!\left(\min(\omega_t^2,Q_{m;pq});r,s\right).
\end{aligned}
\]
The complete round-8 candidate is therefore
\[
\boxed{
A_6=i\,g^{-3}\left(P_{\rm pole}+R_Q+R_0+R_q\right).
}
\]

## Exact chamber and pole prescription

- Every \(h_{mp}\) and \(Q_+\) is the ordinary positive part
  \((x)_+=\max(x,0)\).  Thus no flag or coefficient table is needed.
- At \(q_{mp}=0\), set \(h_{mp}=0\).  The formula is value-continuous;
  derivatives may jump.
- At \(Q_{m;pq}=0\), both \(R_Q\) and the corresponding pole channel
  have continuous zero limits.
- Evaluate a pole channel only for \(d_{m;pq}\ne0\).  At an isolated
  \(d_{m;pq}=0\) with nonzero numerator, take the ordinary two-sided
  rational simple-pole limit.  At coincident divisors, sum all active
  channels before taking the directional limit.

## How the formula was obtained

The tested top-down basis was
\[
\left\{
\operatorname{Orb}_{S_3\times S_3}
\left[\prod_{m,p}h_{mp}^{r_{mp}}\prod_i\omega_i^{\alpha_i}\right]:
\sum r_{mp}\le4,\quad
\sum_i\alpha_i+2\sum r_{mp}=8
\right\}
\oplus\mathcal B_{\rm global},
\]
where \(\mathcal B_{\rm global}\) is the complete 17-dimensional basis
\(\{u^iv^j e_-^ke_+^\ell:i+2j+3k+3\ell=8\}\).
After exact zero-column removal this is \(588+17=605\) columns.

On 900 fresh exact-GMP rows spanning all eight realized magnitude words,
three primes gave
\[
\operatorname{rank}A=\operatorname{rank}[A|S]=182
\quad
(p=2147483647,2147483629,2147483587).
\]
Wolfram `LinearSolve` recovered a rational particular solution on a
nonsingular \(182\times182\) subsystem, and direct `Fraction` arithmetic
verified it on all 900 equations.  Its 85 nonzero columns split as
47 depth-one, 25 depth-two, and 13 global terms; depths three and four
vanish.

The 47 depth-one seeds all belong to one single-hinge orbit.  The 25
depth-two seeds all belong to one two-edge matching orbit.  Converting
distinct-orbit normalization to a full Reynolds sum, averaging over the
edge stabilizers, and eliminating the remaining plus-pair invariants
with the two conservation equations gives exactly \(H_1,H_2,H_0\)
above.  The stabilizers reduce the two full 36-element sums to the
displayed \(9\) single-edge and \(18\) matching terms.

## Verification and compactness account

- Fresh copied `bg.cpp` SHA-256:
  `bd1afe67c45e1e9403c03a0b78373ebb492235be56fc1e5ee9281cbbec9040c1`.
- Exact coefficient solution: zero residual on all \(900/900\) matrix rows.
- Fresh excluded holdouts: zero residual on \(80/80\) exact BG rows,
  spanning six additional word buckets in the deterministic integer pool.
- The independent compact evaluator reconstructed \(R_0+R_q\) from the
  explicit \(H_0,H_1,H_2\) formulas and gave zero residual on all
  \(980/980\) rows; at
  \(\omega=(-8,2,3,4,5,-6)\) the assembled candidate gives
  \(A_6/i=-9190656/7\).

Evaluation uses three explicit polynomials containing \(46+23+13=82\)
monomials, \(9\) single-edge terms, \(18\) matching terms, \(9\)
\(Q\)-orbit terms, and \(9\) pole channels.  It loads no fitted
coefficient table.  Ordinary factorization finds no further nonconstant
factor in \(H_1\), \(H_2\), or \(H_0\).  The remaining acceptance issue is
whether the PI/verifier judges 82 displayed monomials sufficiently
human-readable under the problem's compactness bar; no claim is made that
the full definition-of-done wall, hierarchy, pole, permutation, and
five-point battery has already been completed.

## Reproducible artifacts

- Compact evaluator:
  `bots/student-1/code/round8_compact_candidate.py`
- Full result summary:
  `bots/student-1/data/round8_decisive_result.json`
- Preserved three-prime rank diagnostic:
  `bots/student-1/data/round8_hinge_decisive_diag.json`
- Exact recovered support:
  `bots/student-1/data/round8_hinge_decisive_solution.json`
- Wolfram recovery audit:
  `bots/student-1/data/round8_wolfram_recovery.json`
- Fresh holdouts:
  `bots/student-1/data/round8_fresh_holdouts.json`
