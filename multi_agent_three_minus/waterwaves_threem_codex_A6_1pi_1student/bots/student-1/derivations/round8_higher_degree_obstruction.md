# Round 8: exact higher-chamber degree obstruction

## Chamber and constrained cone fit

This note concerns the realized full-sign chamber `12ea165a03`, whose base
free frequencies are

$$
(\omega_2,\omega_3,\omega_4,\omega_5)=(9,8,2,-5).
$$

Put

$$
x=\frac{\omega_3}{\omega_2},\qquad
y=\frac{\omega_4}{\omega_2},\qquad
z=\frac{\omega_5}{\omega_2},\qquad
h(x,y,z)=\frac{A_6}{i\prod_{\ell=1}^6\omega_\ell\,\omega_2^2}.
$$

Because $H=A_6/(i\prod_\ell\omega_\ell)$ is homogeneous of degree two, a
reduced dehomogenized representation with numerator degree at most $d$ can
be sought with denominator degree at most $d-2$.  The exact interpolation
matrix is

$$
\left[
M_{\le d}(x,y,z)\ \middle|\ -h\,M_{\le d-2}(x,y,z)
\right].
$$

Its column counts are $741$, $924$, and $1135$ for $d=12,13,14$.

## Exact modular rank result

All points have the same complete $53$-entry sign vector.  The first $1050$
exact-GMP points gave

$$
\begin{array}{c|c|c|c}
d&\text{fit rows}&\text{columns}&
\text{nullity mod }(2147483647,2147483629)\\ \hline
12&801&741&(0,0)\\
13&984&924&(0,0).
\end{array}
$$

A freshly copied and built `bg.cpp` then supplied $200$ additional exact
same-signature points.  At $d=14$, using $1195$ fit rows and retaining $55$
rows outside the rank matrix, the ranks were

$$
(1135,1135,1135)
$$

over the primes

$$
(2147483647,2147483629,2147483587),
$$

so the nullities were $(0,0,0)$.  The SHA-256 hashes of the immutable source
and the student copy both equal
`bd1afe67c45e1e9403c03a0b78373ebb492235be56fc1e5ee9281cbbec9040c1`.

Full column rank modulo any one of these primes proves full column rank over
$\mathbb Q$: after clearing input denominators, a maximal minor is nonzero
modulo the prime and hence is a nonzero integer.  Thus this is an exact
negative result, not a numerical-rank estimate.

Consequently this chamber has no rational representation satisfying

$$
\deg P\le14,\qquad \deg Q\le12.
$$

Under the known degree-two homogeneity, a homogeneous numerator and
denominator may be chosen with degrees differing by two.  Their degrees must
therefore obey

$$
\boxed{\deg P_{\rm hom}\ge15,\qquad \deg Q_{\rm hom}\ge13.}
$$

This is strictly more complicated than pieces A/B, whose reduced
dehomogenized degrees are $(12,9)$ and whose homogeneous denominator degree
is $10$.  The rectangular test does not claim separate lower bounds on both
reduced dehomogenized degrees.

## Requested equal-bound scan

The PI's original degree scan uses the larger matrix

$$
\left[
M_{\le d}(x,y,z)\ \middle|\ -h\,M_{\le d}(x,y,z)
\right].
$$

The persisted exact dataset was extended to $1450$ same-signature rows.  The
equal-bound results were

$$
\begin{array}{c|c|c|c}
d&\text{fit rows}&\text{columns}&\text{nullity}\\ \hline
13&1180&1120&(0,0)\\
14&1420&1360&(0,0,0).
\end{array}
$$

Hence the minimal equal-bound dehomogenized degree satisfies

$$
\boxed{d_{\rm eq}=\min\{d:h=P/Q,\ \deg P,\deg Q\le d\}\ge15.}
$$

No null vector exists at either requested degree, so there is no $Q$ to
factor at $d=13$ or $14$.

## Consequence for signed-channel masters

The four-block A seed has reduced common denominator degree $9$.  The new
rank obstruction rules out every sign-activated augmentation whose combined
reduced denominator has degree at most $12$; homogeneity would give a
numerator of degree at most $14$, contradicting the full-rank calculation.
In particular, merely adjoining one independent linear, quadratic, or cubic
denominator factor to the A common denominator cannot generate
`12ea165a03`.  A surviving rational signed-channel master must introduce at
least four additional net denominator degrees in this chamber, or reorganize
the seed into blocks whose least common denominator already has degree at
least $13$.

No factor of the higher-chamber denominator is identified by a null result,
and no full-domain compact evaluator follows from this obstruction.

## Reproducibility and verification status

The implementation is
`bots/student-1/code/round8_higher_reconstruct.py`; its lean result and log
are `bots/student-1/data/round8_higher_reconstruct.json` and
`bots/student-1/data/round8_higher_reconstruct.log`.  Technician thread
`/root/technician` implemented and ran the staged calculation in $78.61$ s
for the top-up pass.  The student independently inspected the asymmetric
monomial bounds, all recorded ranks/nullities, the CRT/null-vector smoke
test, and the matching source hashes before registering this claim.

The final complete point set is persisted at
`bots/student-1/data/round8_pts_12ea165a03_1450.json`, with SHA-256
`85163b920ac6871edbe953b4eb6861566d48c5827a3782fe5d6d6a465123a698`.
It contains $1450$ rows, $1448$ distinct $(x,y,z)$ triples, and all $1450$
rows independently reproduce the target sign vector.  As student-owned
cross-checks, rotated fit subsets were recomputed over the additional prime
$2147483399$.  The asymmetric $d=14$ matrix again had rank $1135/1135$, and
the equal-bound $d=14$ matrix had rank $1360/1360$.  The compact record is
`bots/student-1/data/round8_student_verification.json`.
