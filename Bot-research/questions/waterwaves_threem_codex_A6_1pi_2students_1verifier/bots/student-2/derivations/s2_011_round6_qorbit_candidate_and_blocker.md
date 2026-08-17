# Round-6 clean-\(q\) candidate and verification blocker

## State correction adopted

The round-5 claim \(s2\_010\) is retired.  This session uses the
verifier- and PI-confirmed triple-wall orbit
\[
R_Q=-32\sum_{m\in M}\sum_{\substack{p<q\\p,q\in P}}
  (Q_{m;pq})_+^3\,\omega_m\omega_t,
\qquad \{t\}=P\setminus\{p,q\}.
\]
There is no \(\max\)-selector and no \((q_{mt})_+\) correction.
Accordingly,
\[
S=R_{\rm spline}-R_Q
\]
is the object whose remaining pair-wall spline must be integrated.
This correction is adopted from verifier V3 and PI check
\(pi\_vchk\_004\); it was not independently recomputed in this session.

## Unified intrinsic wall trace

For a labeled pair \((m,p)\), put
\[
a=\omega_m,\qquad b=\omega_p,\qquad
q=b^2-a^2.
\]
Let \(x,y\) be the two other minus-leg frequencies and set
\[
s=x+y,\qquad v=xy,
\]
\[
F=a s^3+v(s^2-2v),\qquad
D=2a^3+3a^2s+a(s^2+v)-sv.
\]
Finally let
\[
\beta=\min_{j\notin\{m,p\}}|\omega_j|.
\]
The two previously reconstructed same- and opposite-energy traces have
the single form
\[
\boxed{
\left.H_{mp}\right|_{q_{mp}=0}
=-32\beta^2\big[F+(a+b)D\big].}
\]
Indeed, on the same-energy component \(b=a\),
\[
F+2aD
=4a^4+6a^3s+2a^2(s^2+v)+(as+v)(s^2-2v),
\]
while on the opposite-energy component \(b=-a\) it reduces to \(F\).
Direct symbolic expansion gave zero residual in both identities.  This
is an algebraic repackaging of the exact wall traces already verified
in \(s2\_007\), not a fresh BG extraction from \(S\).

## Compact two-block candidate for the full pair orbit

The natural candidate to retest after the corrected \(R_Q\) subtraction
is the round-3 intrinsic two-block construction.  For every
\((m,p)\), retain the definitions above.

If the four-leg minimum is another minus leg, name it \(y\), name the
other minus leg \(x\), and define
\[
L=3a^2+2a(s+b)-v+b(2x+y),
\]
\[
H^{(-\beta)}_{mp}
=-32y^2\big[F+(a+b)D\big]
-32q\,y^2L+32xb\,q^2.
\]

If the minimum is another plus leg \(z\), define
\[
\begin{aligned}
K={}&A_0+sA_1+s^2A_2+vB_0+svB_1,\\
A_0={}&a^4+4a^3b+4a^3z+4a^2b^2+6a^2bz+ab^3+2ab^2z,\\
A_1={}&4a^3+8a^2b+7a^2z+5ab^2+7abz+b^3+b^2z,\\
A_2={}&3a^2+4ab+3az+b^2+bz,\\
B_0={}&3a^2+2ab+az,\qquad B_1=3a+b,
\end{aligned}
\]
\[
H^{(+\beta)}_{mp}
=-32z^2\big[F+(a+b)D\big]+32qK.
\]
The active table-free candidate is
\[
\boxed{
R_q^{\rm cand}
=\sum_{m\in M}\sum_{p\in P}(q_{mp})_+
  H_{mp}^{(\beta)},}
\]
where the sector of the minimizing leg selects one of the two displayed
blocks.  It contains nine orbit terms and two analytic block types; it
does not use a chamber coefficient table.  Both blocks restrict to the
unified trace above because their correction terms contain \(q\).

The decisive unperformed test is
\[
R_{0,\mathcal C}
=R_{{\rm spline},\mathcal C}-R_{Q,\mathcal C}
-R_{q,\mathcal C}^{\rm cand}
\]
for the eight exact round-3 branch cells.  The candidate is promoted
only if all eight expressions are the same global polynomial, followed
by fresh exact BG holdouts and isolated \(q/Q\)-wall checks.

## Orchestration blocker and verification status

Immediately before implementation, the required registry preflight
found no existing technician.  The sole `/root/technician` thread was
then created with the complete exact pipeline specification.  It
exhausted its context without writing an artifact.  A tightly scoped
continuation on the same required thread also exhausted its context
without an artifact.  The student-role protocol forbids spawning a
replacement or implementing the nontrivial harness in the main
research session.

Therefore:

- the unified wall-trace identity is algebraically checked;
- the two displayed off-wall blocks retain their prior \(4/4\) exact
  polynomial evidence from \(s2\_008\);
- the corrected-\(R_Q\) cure test, fresh \(S\)-wall audit, global
  \(R_0\) comparison, beta-tie audit, and fresh BG assembly holdouts
  were **not run**;
- no complete or verified \(R_q\) is claimed this round.

