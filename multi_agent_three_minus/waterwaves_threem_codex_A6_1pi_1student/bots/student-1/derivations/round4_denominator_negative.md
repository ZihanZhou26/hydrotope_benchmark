# Round-4 denominator test: the square-free cross-sum hypothesis fails

Put
$$
a_i=\omega_i^2,\qquad b_j=\omega_{3+j}^2,\qquad
C_{ij}=a_i+b_j>0.
$$
For every mask $M\subseteq\{1,2,3\}\times\{1,2,3\}$, the tested candidate was
$$
Q_M=\prod_{(i,j)\in M}C_{ij},\qquad
P_M=H Q_M,\qquad \deg P_M=d_M=2+2|M|.
$$

The exact on-shell parametrization uses the four free signed frequencies
$f=(\omega_2,\omega_3,\omega_4,\omega_5)$ and
$U=\sum_{\alpha=2}^{5}\omega_\alpha$.  Both solved frequencies have a
degree-two numerator and denominator $U$.  Therefore, if $P_M$ were a
homogeneous polynomial of degree $d_M$ in the six signed frequencies, then
on every affine line $f(t)=f_0+t v$,
$$
Y_M(t)=H(t)Q_M(t)U(t)^{d_M}
$$
would be a univariate polynomial of degree at most $2d_M$.

`h_mask_scan_lean.py` generated six generic exact-GMP BG lines in the same
fixed sorted raw 18-wall chamber as the 720-point oracle.  Every retained
point passed both conservation equations, had zero real amplitude, and used
$H=(A_6/i)/\prod_k\omega_k$.  Each line supplied at least 59 rational points
(59, 61, 65, 65, 70, and 73 for the full mask).  For each of all $2^9=512$
masks, the first $2d_M+1$ values fixed the unique candidate polynomial over
$\mathbb F_{1000003}$ and 16 further values tested it.

Every mask failed on every line.  In particular, the full product
$$
Q_{\rm full}=\prod_{i=1}^{3}\prod_{j=1}^{3}(a_i+b_j),
\qquad d_{\rm full}=20,
$$
failed its modular holdouts on all six lines.  A modular holdout failure is
an exact negative result: a rational polynomial identity over $\mathbb Q$
whose sampled denominators are nonzero modulo the prime would reduce to the
same identity over that finite field.  Thus no square-free subproduct of the
nine $a_i+b_j$ clears the fixed-chamber denominator of $H$.

The test does **not** exclude higher powers of these factors or other
sign-definite factors such as same-set square sums.  Those are the next
denominator families to test.

Evidence:

- `bots/student-1/data/h_mask_scan_lean.json`
- `bots/student-1/data/h_mask_scan_lean.md`
- `bots/student-1/code/h_mask_scan_lean.py`
- fresh copied oracle source/binary:
  `bots/student-1/code/bg_round4.cpp`, `bots/student-1/code/bg_round4`
