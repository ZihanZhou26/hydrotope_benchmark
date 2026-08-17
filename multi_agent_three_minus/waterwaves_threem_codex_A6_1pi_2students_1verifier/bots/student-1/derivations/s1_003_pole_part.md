# Pole-part construction for the three-minus six-point amplitude

## Conventions

Let \(M=\{1,2,3\}\), \(P=\{4,5,6\}\), and define

\[
\mathcal H(b;c,d)
=b-(b-\omega_c^2)_+-(b-\omega_d^2)_+
 +(b-\omega_c^2-\omega_d^2)_+ .
\]

The real stripped two-minus four-point block is

\[
h_4(a,b;c,d)=8\,\omega_a\omega_b\,
\mathcal H\!\left(\min(\omega_a^2,\omega_b^2);c,d\right),
\qquad A_4^{2-}=i g^{-1}h_4 .
\]

For a channel \(T=\{m,p,q\}\), with \(m\in M\) and
\(\{p,q\}\subset P\), set

\[
Q_T=\omega_p^2+\omega_q^2-\omega_m^2,\qquad
d_T=(\omega_m+\omega_p+\omega_q)^2-Q_T
=2(\omega_m+\omega_p)(\omega_m+\omega_q).
\]

Only \(Q_T>0\) is retained.  If \(M\setminus\{m\}=\{r,s\}\) and
\(P\setminus\{p,q\}=\{t\}\), choose an auxiliary on-shell internal
frequency \(x_T\) with \(x_T^2=Q_T\).  The \(T\)-side block uses the
minus pair \((m,x_T)\) and plus pair \((p,q)\).  On the complementary
side, globally flip all spatial momentum signs and use the minus pair
\((t,-x_T)\) and plus pair \((r,s)\).  Thus

\[
\begin{aligned}
h_{4,L}&=8\,\omega_m x_T\,
\mathcal H\!\left(\min(\omega_m^2,Q_T);p,q\right),\\
h_{4,R}&=-8\,\omega_t x_T\,
\mathcal H\!\left(\min(\omega_t^2,Q_T);r,s\right),\\
h_{4,L}h_{4,R}
&=-64\,\omega_m\omega_t Q_T\,
\mathcal H\!\left(\min(\omega_m^2,Q_T);p,q\right)
\mathcal H\!\left(\min(\omega_t^2,Q_T);r,s\right).
\end{aligned}
\]

The branch of \(x_T\) cancels.

## Propagator normalization

The supplied BG oracle uses

\[
\mathrm{Propagator}=-\frac{i}{D_T},\qquad
D_T=\frac{\omega_T^2}{|k_T|}-g .
\]

Because \(|k_T|=Q_T/g\),

\[
\mathrm{Propagator}=-i\,\frac{Q_T}{g\,d_T}.
\]

Consequently the direct factorization graph is

\[
A_{6,T}
=A_{4,L}\left(-i\,\frac{Q_T}{g\,d_T}\right)A_{4,R}
=i g^{-3}\frac{Q_T h_{4,L}h_{4,R}}{d_T}.
\]

The candidate complete rational part is therefore

\[
\boxed{
P_{\mathrm{pole}}(\omega)
=-64\sum_{\substack{m\in M,\ \{p,q\}\subset P\\Q_T>0}}
\frac{\omega_m\omega_t Q_T^2}{d_T}\,
\mathcal H\!\left(\min(\omega_m^2,Q_T);p,q\right)
\mathcal H\!\left(\min(\omega_t^2,Q_T);r,s\right)
}.
\]

At \(\omega=(-8,2,3,4,5,-6)\), the exact value is
\(P_{\mathrm{pole}}=42588288/7\).  Using the supplied exact BG anchor
\(A_6/i=-9190656/7\), the residual is the integer
\(-7396992\).  In contrast, omitting the required propagator numerator
\(Q_T\) leaves denominator \(7\).

## Why this removes the complete rational part

Inside any fixed absolute-momentum chamber, the BG oracle is a rational
function.  Every denominator comes from a BG propagator.  At a genuine
six-point triple-channel pole, the sum of trees containing that edge
factorizes with unit graph multiplicity into the two lower on-shell
amplitudes and that propagator.  The \(Q_T<0\) orientation has a
one-minus four-point factor and hence zero residue.  The \(Q_T>0\)
orientation has precisely the two blocks written above.  Therefore the
displayed orbit sum has the same principal part as \(A_6/i\) at every
nonzero-residue propagator divisor.  Subtracting it removes all such
divisors; within a chamber the remainder is polynomial.  Different
off-pole extensions of a residue can only shift that polynomial
remainder.

The construction has one analytic building block \(\mathcal H\) and one
\(S_3(M)\times S_3(P)\) orbit representative,
\((m;p,q;t;r,s)=(1;4,5;6;2,3)\).  Its orbit contains nine channel terms.
No coefficient table is used.

## Chamber and limiting prescription

For a nondegenerate point, include a channel exactly when \(Q_T>0\) and
evaluate it only when \(d_T\ne0\).  At \(Q_T=0\), define the channel by
continuity to be zero.  Indeed, for small positive \(Q_T\), both
\(\mathcal H\) factors are \(O(Q_T)\), while the displayed numerator has
an additional \(Q_T^2\), so the channel vanishes at least as \(Q_T^4\)
when \(d_T\) stays nonzero.  The positive-part and `min` prescriptions
make all other \(A_4\) chamber walls continuous, though derivatives can
jump.

At an isolated \(d_T=0\) divisor with nonzero numerator, the formula is
the ordinary rational simple-pole limit and its coefficient with
respect to \(1/d_T\) is

\[
-64\,\omega_m\omega_t Q_T^2\,
\mathcal H\!\left(\min(\omega_m^2,Q_T);p,q\right)
\mathcal H\!\left(\min(\omega_t^2,Q_T);r,s\right).
\]

The exact BG evaluator has no separate numerical value on the divisor.
Approach it from \(d_T\ne0\).  If conservation forces several mixed-pair
divisors to meet, combine all active channel terms first and take the
common directional limit; do not assign a value to each singular term
separately.  A zero total residue is a removable limit, while a nonzero
one is a genuine factorization pole.

## Exact denominator diagnostics

An independent `Fraction` evaluation was run over the 80 exact GMP
six-point samples already stored in
`bots/student-1/data/exact_samples.json`.  These span four sorted
momentum-sign words and fifteen full subset-sign signatures.

- All 15 integer-frequency samples gave
  \(A_6/i-P_{\mathrm{pole}}\in\mathbb Z\).
- For every one of the 80 rational samples, if \(L\) is the least common
  multiple of the six frequency denominators, then
  \(L^8(A_6/i-P_{\mathrm{pole}})\in\mathbb Z\).  This is the scaling
  expected of a homogeneous degree-eight integer-coefficient chamber
  polynomial.
- The otherwise identical sum without the propagator numerator \(Q_T\)
  failed on 6 of the 15 integer-frequency samples, retaining denominator
  \(7\) in each failure.

Thus no observed mixed-pair factor from
\(\Delta=\prod_{m\in M,p\in P}(\omega_m+\omega_p)\) remains after the
proper subtraction.

The final reproducible run rebuilt the copied `bg.cpp` and freshly
re-evaluated 77 valid nondegenerate seeds (the script never uses the
stored amplitudes).  It covered four sorted momentum-sign words and
fifteen full subset-sign signatures.  The results were:

- \(16/16\) integer-frequency residuals integral;
- \(61/61\) rational-frequency residuals integral after multiplication
  by \(L^8\);
- no failures for the degree-eight \(S_1=P_{\mathrm{pole}}\) formula;
- the degree-six negative control \(S_0=\sum B_T/d_T\) failed the same
  test on \(3/16\) integer and \(24/61\) rational points.

Full commands and exact rows are in
`bots/student-1/code/pole_batch.py`,
`bots/student-1/data/pole_results.json`, and
`bots/student-1/derivations/pole_batch_report.md`.

## Four-point calibration caveat

Direct `bg -n 4` evaluation on real resonant \((-,-,+,+)\) kinematics is
singular: solving the two conservation laws forces pairwise-exchange
frequencies \((-\omega_3,\omega_2,\omega_3,-\omega_2)\), and a BG
subcurrent then has both zero momentum and zero frequency.  The oracle
raises `SIGFPE`, exactly as its documented wall/pole behavior predicts.
The known \(A_4\) formula is supplied as an allowed starting result.
Any oracle calibration must therefore be performed as a two-sided
off-singular limit, never by evaluating the resonant point itself.
The final batch examined 4032 rational grid seeds and confirmed that no
safe pointwise calibration case exists.  This is not a missing input:
the two-minus \(A_4\) formula is supplied by the question.
