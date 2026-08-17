# Round-8 off-wall cofactor ground truth and nested-brick obstruction

## 1. The physical four-leg wall fan has only two strict cells

Fix a pair wall \(q_{mp}=\omega_p^2-\omega_m^2=0\), with \(m\) a
minus leg and \(p\) a plus leg.  Cancelling the tied squares in momentum
conservation gives
\[
\sum_{\substack{r\in P\\r\ne p}}\omega_r^2
=
\sum_{\substack{\ell\in M\\\ell\ne m}}\omega_\ell^2 .
\]
Thus the two remaining minus squares and the two remaining plus squares
have equal sums.  Write their strictly ordered magnitudes as two \(M\)
entries and two \(P\) entries.  If the smallest entry is \(M\), then the
largest must also be \(M\); otherwise the sum of the two \(M\) squares
would be strictly smaller than the sum of the two \(P\) squares.  The
same argument with \(M\) and \(P\) interchanged applies when the smallest
entry is \(P\).

Consequently the only physically realized strict four-environment
magnitude words on a pair wall are
\[
\boxed{\mathrm{MPPM}\quad\hbox{and}\quad\mathrm{PMMP}.}
\]
The other four combinatorial interleavings are impossible on shell.
This reduces the requested per-cell ground truth from six formal words
to two physical cells.  A direct exact enumeration using the established
on-shell affine-wall parameterizations also found precisely these two
words.

## 2. Exact local polynomial templates to be tested

For a labeled pair put
\[
a=\omega_m,\qquad b=\omega_p,\qquad q=b^2-a^2.
\]
Let \(x,y\) be the two other minus frequencies, with
\[
s=x+y,\qquad v=xy,
\]
and define
\[
F=as^3+v(s^2-2v),\qquad
D=2a^3+3a^2s+a(s^2+v)-sv,\qquad
E=F+(a+b)D.
\]
The two previously reconstructed raw cell templates are
\[
H^{(-)}=-32y^2E-32q\,y^2L_y+32xbq^2,
\qquad
L_y=3a^2+2a(s+b)-v+b(2x+y),
\]
when the minimal environment magnitude is the minus leg \(y\), and
\[
H^{(+)}=-32z^2E+32qK_z
\]
when it is the plus leg \(z\), where
\[
\begin{aligned}
K_z={}&A_0+sA_1+s^2A_2+vB_0+svB_1,\\
A_0={}&a^4+4a^3b+4a^3z+4a^2b^2+6a^2bz+ab^3+2ab^2z,\\
A_1={}&4a^3+8a^2b+7a^2z+5ab^2+7abz+b^3+b^2z,\\
A_2={}&3a^2+4ab+3az+b^2+bz,\\
B_0={}&3a^2+2ab+az,\qquad B_1=3a+b .
\end{aligned}
\]
The fresh exact quotient extraction gives the requested explicit
degree-six ground truth on one representative on-shell affine slice in
each physical cell.

For the \(\mathrm{MPPM}\) cell, take
\[
\omega(t)=(8,2,-3,-5,4,-6)
+t(4,3,1,-3,-1,-4),
\]
with the active wall \(q_{25}=0\) at \(t_0=1/2\).  The intrinsic
orientation is \(S|_{q_{25}>0}-S|_{q_{25}<0}=q_{25}H_{\mathrm{MPPM}}\),
and exact interpolation and division give
\[
\boxed{\begin{aligned}
H_{\mathrm{MPPM}}(t)={}&-29024t^6+20768t^5+310784t^4
+256704t^3\\
&-440800t^2-872928t-190656.
\end{aligned}}
\]

For the \(\mathrm{PMMP}\) cell, take
\[
\omega(t)=(10,-7,-6,-5,-4,12)
+t(1,1,1,-1,-1,-1),
\]
with the active wall \(q_{34}=0\) at \(t_0=1/2\).  With the same
intrinsic orientation,
\[
\boxed{\begin{aligned}
H_{\mathrm{PMMP}}(t)={}&-320t^6-2912t^5+4480t^4
+474752t^3\\
&-684416t^2+5101888t+8743168.
\end{aligned}}
\]

Both jump divisions have exact zero remainder.  Each degree-six
polynomial agrees with the applicable compact raw local formula at
seven distinct exact points in its \(q>0\) cell, hence the two
degree-six polynomials agree identically with those local formulas on
these slices.  Their wall values agree with
\(-32\beta^2[F+(a+b)D]\).

## 3. Explicit cross-sector cocycle

At the cross-sector tie \(z=y\), direct symbolic subtraction gives
\[
\left.H^{(+)}-H^{(-)}\right|_{z=y}=32q\,J(a,b,x,y),
\]
where
\[
\begin{aligned}
J={}&a^4+4a^3b+4a^3x+8a^3y+4a^2b^2+9a^2bx+14a^2by\\
&+3a^2x^2+16a^2xy+13a^2y^2+ab^3+5ab^2x+7ab^2y\\
&+4abx^2+17abxy+13aby^2+6ax^2y+12axy^2+5ay^3\\
&+b^3y+b^2x^2+3b^2xy+2b^2y^2+2bx^2y+5bxy^2
+2by^3-xy^3 .
\end{aligned}
\]
SymPy finds no nontrivial factor in this displayed quartic.  At
\[
(a,b,x,y,z)=\left(2,4,\frac{13}{2},-\frac72,-\frac72\right)
\]
one obtains
\[
J=-\frac{881}{16},\qquad 32qJ=-21144.
\]
Hence the difference of the old raw templates does not vanish on their
shared environment wall \(z^2-y^2=0\), and in particular is not
divisible by \(z^2-y^2\).

The equal-sums lemma makes the geometry sharper.  If the ordered
environment squares are \(u<U\) in the minus sector and \(v<V\) in the
plus sector, then \(u+U=v+V\).  At the boundary between
\(\mathrm{MPPM}\) and \(\mathrm{PMMP}\), equality of the two smallest
squares \(u=v\) forces equality of the two largest squares \(U=V\).
Thus the physical cell exchange is necessarily a simultaneous
two-\(q\)-wall event inside the primary \(q_{mp}=0\) wall.  It is not a
single secondary wall that can be integrated by one independent
positive-part fold.

This is an exact obstruction to turning those two raw templates,
unchanged, into one continuous brick by merely replacing their hard
minimum selector with continuous truncated powers.  It is not an
obstruction to a coupled orbit construction: a valid nested formula
must redistribute the off-wall coefficient among several
\((q_{mp})_+\) terms, so the extracted jump of one wall can receive
mixed-hinge contributions associated with another wall.

## 4. Verification state

The standalone extractor copied the immutable shared `bg.cpp` to
`bots/student-2/bg_round8.cpp`; both files have SHA-256
`bd1afe67c45e1e9403c03a0b78373ebb492235be56fc1e5ee9281cbbec9040c1`.
It rebuilt the GMP oracle on every run and reproduced the exact anchor
\[
\frac{A_6}{i}=-\frac{9190656}{7},\quad
P_{\rm pole}=\frac{42588288}{7},\quad
R_Q=-136630560,\quad S=129233568.
\]
For both cells, all eight non-active pair signs, all nine \(Q\)-signs,
and all six frequency signs remain fixed across the wall.  The two
degree-eight branch fits pass \(4/4\) exact held-out points; both jump
divisions have zero remainder and quotient degree six; the on-wall
trace passes \(2/2\); and the compact raw formulas pass \(14/14\)
off-wall exact points.  I independently reran
`bots/student-2/code/round8_offwall_ground_truth.py` after these checks
were added; it exited successfully and reproduced the same two
polynomials.

The full machine-readable record is
`bots/student-2/data/round8_offwall_ground_truth.json`, and the compact
report is
`bots/student-2/data/round8_offwall_ground_truth_report.md`.

No complete \(R_q\) is claimed.  The precise remaining obstruction is
the integration of the displayed nonzero codimension-two cocycle into
a symmetry-covariant mixed-hinge orbit whose subtraction leaves one
global polynomial \(R_0\); consequently the requested \(18\)-wall cure
test cannot yet be run for a valid candidate.
