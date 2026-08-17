# Reduced denominator, sheet scan, and pair-wall diagnostics

## 1. The nine-factor denominator is a perfect cube

Let
\[
M=\{1,2,3\},\qquad P=\{4,5,6\},
\]
and write \(e_r^-\) and \(e_r^+\) for the elementary symmetric
polynomials of \(\{\omega_m:m\in M\}\) and
\(\{\omega_p:p\in P\}\), respectively.  The two on-shell conservation
laws imply
\[
e_1^+=-e_1^-,
\qquad
e_2^+=e_2^-.
\]
The second identity follows by writing the equality of the two sums of
squares as
\[
(e_1^-)^2-2e_2^-=(e_1^+)^2-2e_2^+.
\]

Define the degree-three symmetric polynomial
\[
\boxed{C=e_3^-+e_3^+
=\omega_1\omega_2\omega_3+\omega_4\omega_5\omega_6.}
\]
For a fixed \(m\in M\), consider
\[
Y(z)=\prod_{p\in P}(z+\omega_p)
=z^3-e_1^-z^2+e_2^-z+e_3^+.
\]
Since \(\omega_m\) is a root of
\[
X(z)=z^3-e_1^-z^2+e_2^-z-e_3^-,
\]
one obtains the labeled identity
\[
\boxed{\prod_{p\in P}(\omega_m+\omega_p)=Y(\omega_m)=C.}
\]
Multiplying it over the three minus legs proves
\[
\boxed{\Delta=\prod_{m\in M,p\in P}(\omega_m+\omega_p)=C^3.}
\]
Thus the round-1 degree-nine denominator was a cube in the on-shell
coordinate ring.

For a surviving channel \(T=\{m,p,q\}\), with \(r\) the omitted plus
leg,
\[
d_T=2(\omega_m+\omega_p)(\omega_m+\omega_q),
\]
so the same identity gives
\[
\boxed{\frac1{d_T}=\frac{\omega_m+\omega_r}{2C}.}
\]
Therefore every factorization term has common denominator \(C\), not
\(\Delta\).

In the standard rational coordinates
\[
\omega=(-a,b,c,d,e,-f),\quad
S=b+c+d+e,\quad
a=d+e+\frac{bc-de}{S},\quad
f=b+c-\frac{bc-de}{S},
\]
the identity is also visible as
\[
C=-\frac{(b+d)(b+e)(c+d)(c+e)}{S},
\qquad
\Delta=C^3.
\]

## 2. Exact evidence that \(C\) is minimal

The fresh student-2 oracle was built from the copied `bg.cpp`.  At 750
exact on-shell points, spanning all eight momentum words and 19 distinct
energy-sign patterns,
\[
\Delta=C^3
\]
held exactly.  The channel identity above held in all \(5079/5079\)
active \(Q_T>0\) tests.

On three affine paths
\[
b=b_0+t,\qquad d=d_0-t,\qquad c=c_0,\qquad e=e_0,
\]
all six frequencies are affine in \(t\), and the complete pair/triple
sign signature was held fixed.  Twelve exact values fitted
\[
B(t)=C(t)\,A_6(t)/i
\]
as a polynomial and three further exact holdouts had zero residual on
each path.  The data were
\[
\begin{array}{c|c|c}
(b_0,c_0,d_0,e_0)&C(t)&\gcd_{\mathbb Q[t]}(B,C)\\ \hline
(1,1,3,2)&\frac{12}{7}(t^2-t-12)&1\\
(1,1,3,3)&2(t^2-16)&2\\
(1,1,3,4)&\frac{20}{9}(t^2+t-20)&1
\end{array}
\]
where the constant \(2\) is a unit over \(\mathbb Q[t]\).  Direct
degree-eight polynomial interpolation of \(A_6/i\) was inconsistent
(the twelve-point interpolant had degree eleven).  Hence a proper
divisor of \(C\) cannot be the generic denominator on these chamber
restrictions.  Together with the analytic upper bound, this gives
\[
\boxed{D_{\min}=C,\qquad \deg D_{\min}=3.}
\]
Since \(A_6/i\) is homogeneous of degree eight, its reduced cleared
numerator \(C A_6/i\) is homogeneous of degree eleven.

As a separate arithmetic check, after scaling every rational
kinematics point to primitive integer frequencies, \(C A_6/i\) was an
integer in all \(750/750\) cases.  The same statement held for the
pole-subtracted degree-eight remainder described below.

## 3. Pole subtraction and the actual pair-wall order

For cross-checking only, I independently implemented the compact
nine-channel pole expression from claim `s1_003`.  With
\[
\mathcal H(x;u,v)=x-(x-u^2)_+-(x-v^2)_+
 +(x-u^2-v^2)_+,
\]
the channel term used was
\[
P_T=-64\,
\frac{\omega_m\omega_t Q_T^2}{d_T}\,
\mathcal H(\min(\omega_m^2,Q_T);\omega_p,\omega_q)
\mathcal H(\min(\omega_t^2,Q_T);\omega_r,\omega_s),
\]
included only for \(Q_T>0\).  Here \(t\) is the omitted plus leg and
\(\{r,s\}=M\setminus\{m\}\).  The remainder is
\[
R=A_6/i-\sum_TP_T.
\]
Primitive degree-eight scaling made \(R\) integral at all \(750/750\)
oracle points, independently confirming that the rational denominator
was removed.

I crossed the representative pair wall
\[
q_{24}=\omega_4^2-\omega_2^2=0
\]
on paths \(b=t,\ d=B-t\), so the wall is at \(t_0=B/2\).  Every sample
was off the wall, and all other pair and triple signs were fixed.
Nine values on each side determined the polynomial branches of \(R\);
three additional points on each side and three still-closer holdouts
per side all had exact zero residual for the appropriate branch.

Three independent wall settings gave
\[
\begin{array}{c|c|c|c}
(B,c,e)&\deg R_L,\deg R_R&
\operatorname{ord}_{q_{24}}(R_L-R_R)&
\displaystyle\lim_{q_{24}\to0}\frac{R_L-R_R}{q_{24}}\\ \hline
(10,2,3)&(6,6)&1&12622720/27\\
(14,3,2)&(6,6)&1&8178488960/6859\\
(16,2,5)&(6,6)&1&30826928896/12167
\end{array}
\]
The full exact univariate branch polynomials and their factorizations
are in `bots/student-2/data/round2_exact.json`.

This is an adversarial result against the round brief's proposed
truncated-cubic opening: for this explicit pole convention, the
polynomial remainder has a **simple**, nonzero pair-wall jump
polynomial,
\[
R_L-R_R=q_{24}\,H_{24},
\]
where \(H_{24}\) is homogeneous of degree six.  Thus the minimal
possible orbit brick is of the form
\[
\sum_{m\in M,p\in P} q_{mp,+}\,H_{mp}(\omega),
\]
with the \(H_{mp}\) generated from one degree-six representative by
\(S_3(M)\times S_3(P)\).  The present data establish the power and orbit
rule but do not yet identify a compact multivariate formula for
\(H_{mp}\).  In particular, a cubic truncated-power brick is ruled out.

Before subtraction, the branch difference was rational, was not
divisible by \(C\), and also vanished only linearly at the wall.  Hence
the pole extension itself changes analytic branch at pair walls through
its lower-point positive-part blocks.  The strategic assertion that the
chosen \(P_{\rm pole}\) is pair-wall independent is false; one must
subtract it before assigning the polynomial jump to the spline.

## 4. Sheet coverage

The rational parametrization above is algebraic and allows arbitrary
signs of \(b,c,d,e,a,f\); away from \(S=0\), it covers the full real
on-shell solution set in this labeling.  An exhaustive exact scan over
\[
(b,c,d,e)\in(\{-8,\ldots,-1,1,\ldots,8\})^4
\]
retained 35,380 generic points.  It observed exactly the same eight
momentum words
\[
\{+-+--+,+--++-,+--+-+,+---++,
-+++--,-++-+-,-++--+,-+-++-\},
\]
and no occurrence of the only two additional prefix-admissible words
\(++---+\) or \(--+++-\).  The 750 fresh BG points used above contained
19 energy-sign patterns and also only these eight words.

This closes the numerical sheet-independence flag much more strongly,
but is not yet a symbolic exclusion proof for the two missing words.
A useful proof reduction is that the minus frequencies and the
negatives of the plus frequencies are the three real roots of two
monic cubics with identical quadratic and linear coefficients and only
their constant terms different.  A finite interlacing analysis of the
two cubic fibers should exclude the two missing absolute-value orders.

## Reproducibility

- Exact driver: `bots/student-2/code/round2_exact.py`
- Copied oracle source/binary: `bots/student-2/bg.cpp`,
  `bots/student-2/bg`
- Full exact output: `bots/student-2/data/round2_exact.json`
- Concise run report: `bots/student-2/data/round2_exact_report.md`
- Five-point harness calibration: \(3/3\) exact zero residuals
- Within-sector permutation checks: \(6/6\) exact zero residuals

