# Round-7 continuous symmetrization and the off-wall-cofactor obstruction

## Objective and settled input

This round uses the verifier- and PI-confirmed decomposition
\[
S=R_{\rm spline}-R_Q,\qquad
R_Q=-32\sum_{m\in M}\sum_{\substack{p<q\\p,q\in P}}
 (Q_{m;pq})_+^3\,\omega_m\omega_{\bar p}.
\]
The old two-block selector \(s2\_012\) is retired.  For a labeled pair
\((m,p)\), put
\[
a=\omega_m,\quad b=\omega_p,\quad q=b^2-a^2,
\]
and let \(x,y\) denote the other two minus frequencies.  Define
\[
s=x+y,\qquad v=xy,
\]
\[
F=as^3+v(s^2-2v),\qquad
D=2a^3+3a^2s+a(s^2+v)-sv,
\]
\[
E=F+(a+b)D,\qquad
\beta^2=\min_{j\notin\{m,p\}}\omega_j^2.
\]
The confirmed wall value is
\[
\left.H_{mp}\right|_{q=0}=-32\beta^2E.
\]

## A manifestly continuous candidate

The minus-minimizer local block from \(s2\_011\) contains the correction
\[
-32q\,y^2L_y+32xbq^2,\qquad
L_y=3a^2+2a(s+b)-v+b(2x+y).
\]
Its average under \(x\leftrightarrow y\) is residual-minus symmetric and
contains no signed argmin selector.  Exact simplification gives
\[
\frac{y^2L_y+x^2L_x}{2}
=\frac12\left(
[3a^2+2a(s+b)-v](s^2-2v)+bs(s^2-v)
\right).
\]
This motivates the compact brick
\[
\boxed{
B^{\rm sym}_{mp}
=-32\beta^2E
-16q\left(
[3a^2+2a(s+b)-v](s^2-2v)+bs(s^2-v)
\right)
+16bsq^2 .}
\]
The candidate orbit is
\[
R_q^{\rm sym}=\sum_{m\in M}\sum_{p\in P}(q_{mp})_+B^{\rm sym}_{mp}.
\]
It has nine orbit terms and three short degree-six blocks.  It is
table-free.  The only minimum is the scalar \(\beta^2\), which can be
implemented continuously by folding
\[
\mu(u,v)=u-(u-v)_+
\]
over the four environment squares.  Thus every \(B^{\rm sym}_{mp}\) is
continuous at cross-sector magnitude ties.  It also restricts to the
confirmed trace because both correction terms vanish at \(q=0\).

## Exact rejection

I substituted this brick into the verifier's independent exact wall
extraction and continuation harness, with its already-built exact GMP
oracle and confirmed implementations of \(P_{\rm pole}\), \(R_Q\), and
\(S\).  This is diagnostic reuse of the verifier harness, not a fresh
student-2 oracle build.

The outcomes are:

* the branch jump of \(S\) is divisible by \(q_{mp}\): \(24/24\);
* the extracted cofactor at the wall equals \(-32\beta^2E\): \(24/24\);
* \(B^{\rm sym}_{mp}\) equals the extracted cofactor off the wall:
  \(0/24\);
* \(R_q^{\rm sym}\) is continuous in value on the cure battery:
  \(T_{\rm contin}=0\) on \(18/18\) crossings;
* nevertheless \(T=S-R_q^{\rm sym}\) is a single degree-eight
  polynomial across the wall on \(0/18\) crossings.  It retains a
  nonzero continuation jump on \(18/18\).

For the first isolated wall, \(q_{23}=0\) at \(t_0=-1/2\), the exact
left-polynomial/right-point residual is
\[
\frac{136585204640161305617743}
{14238281250000000}\ne0,
\]
while the two branch limits at the wall agree exactly.

Therefore the candidate solves only the \(C^0\) selector problem.  It
does not reproduce the full degree-six cofactor away from \(q=0\).
The missing nested construction must retain the exact \(q\) and \(q^2\)
off-wall information of the local blocks while coupling different
pair terms so their selector jumps cancel.  A construction determined
only by the common wall trace, even if every brick is globally
continuous, is underdetermined and fails the required smooth/global
\(R_0\) test.

## Cross-sector matching witness

At a tie between the selected other-minus frequency \(y\) and an
other-plus frequency \(z=y\), the old plus- and minus-selector blocks
differ by
\[
H^{(+)}-H^{(-)}
=32q\,J(a,b,x,y),
\]
where direct exact expansion gives a nonzero quartic \(J\).  At the
on-shell witness
\[
(a,b,x,y,z)=(2,4,13/2,-7/2,-7/2)
\]
one finds
\[
J=-\frac{881}{16},\qquad H^{(+)}-H^{(-)}=-21144.
\]
This nonzero \(q\)-proportional mismatch is the precise datum that a
coupled positive-part correction must redistribute between pair
orbits.

## Reproducibility

* Independent exact oracle and \(S\) implementation:
  `bots/verifier/code/r6_core.py`
* Exact cofactor extraction:
  `bots/verifier/code/r6_checkC2.py`
* Exact continuation/cure harness:
  `bots/verifier/code/r6_checkC.py`
* Stored 18-wall result:
  `bots/student-2/data/r6_checkC.json`
* Compact result summary:
  `bots/student-2/data/round7_symmetric_candidate_summary.json`

The required reusable technician thread was dispatched with a bounded
exact-fit script and then a much smaller existing-data fit.  It
exhausted context on both dispatches and wrote no artifact.  Per the
student protocol, no replacement technician or main-session fit
harness was created.
