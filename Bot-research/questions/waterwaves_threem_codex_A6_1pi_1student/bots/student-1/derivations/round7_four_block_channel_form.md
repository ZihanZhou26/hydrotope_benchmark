# Round 7: exact four-block form and a box-spline obstruction

## Scope

This note concerns the two already reconstructed opposite true pieces.  It
does **not** extend them to the higher-degree chambers.  Its new content is an
exact partial-fraction reduction of the banked 31-term formula and a
structural no-go theorem for a purely polynomial positive-part master.

Put

$$
(u,v,r,s)=(\omega_2,\omega_3,\omega_4,\omega_5),\qquad
\Omega=u+v+r+s,
$$

and define

$$
\begin{aligned}
B_M&=u^2+v^2+uv+ur+us+vr+vs+rs,\\
B_P&=r^2+s^2+uv+ur+us+vr+vs+rs,\\
L&=(u+r)(u+s)(v+r)(v+s),\\
C(u;r,s)&=r^3(u+s)+s^3(u+r).
\end{aligned}
$$

As before, \(H=A_6/(i\prod_{\ell=1}^6\omega_\ell)\).

## Exact four-block identity

In the true piece containing
\((-7,9,-8,-3,-4,13)\), the 31-term core formula is identically equal to

$$
\boxed{
\begin{aligned}
H_A={}&
\frac{64rs(r^2+s^2)}{B_P}
-\frac{32r^2s^2(r^2+s^2)\Omega}
       {u(u+r)(u+s)B_M}\\
&-\frac{32rs\,\Omega\,C(u;r,s)}{uL}
-\frac{64rs(r^2+s^2)(u+r+s)}
       {v(u+r)(u+s)} .
\end{aligned}}
$$

The result for the opposite piece is the same four-block construction after
the set swap,

$$
H_B(u,v,r,s)=H_A(r,s,u,v).
$$

The displayed form is manifestly symmetric in \(r,s\).  Separate symmetry in
\(u,v\) is hidden term by term but follows from the exact identity with the
already proved pair-symmetric core.  If desired, it can be displayed
manifestly as the two-element orbit average
\(\frac12[H_A(u,v,r,s)+H_A(v,u,r,s)]\).

## How the reduction was obtained

Dehomogenize by \(u\) and write

$$
x=\frac vu,\qquad y=\frac ru,\qquad z=\frac su,\qquad
h=\frac{H}{u^2}.
$$

Let \(P_A,Q_A\) be the exact reconstructed polynomials in
`bots/pi/code/round6_QP.txt`.  Exact partial fractioning in \(x\) gives five
short terms.  The only two terms containing the spurious factor \(y-z\)
combine using

$$
\frac{1}{y-z}\left[
\frac1{(x+y)(y+1)}-\frac1{(x+z)(z+1)}
\right]
=-\frac{x+y+z+1}
{(x+y)(x+z)(y+1)(z+1)}.
$$

The resulting four-term dehomogenized expression is

$$
\begin{aligned}
\frac{P_A}{Q_A}={}&
\frac{64yz(y^2+z^2)}{B_P^{(d)}}
-\frac{32y^2z^2(y^2+z^2)(1+x+y+z)}
{(y+1)(z+1)B_M^{(d)}}\\
&-\frac{32yz(1+x+y+z)
[y^3(z+1)+z^3(y+1)]}
{(x+y)(x+z)(y+1)(z+1)}\\
&-\frac{64yz(y^2+z^2)(1+y+z)}
{x(y+1)(z+1)},
\end{aligned}
$$

where

$$
\begin{aligned}
B_M^{(d)}&=x^2+xy+xz+x+yz+y+z+1,\\
B_P^{(d)}&=xy+xz+x+y^2+yz+y+z^2+z.
\end{aligned}
$$

Homogenizing this identity gives the boxed formula.

## Exact verification

All checks used exact SymPy rationals:

1. `factor(gcd(P_A,Q_A))=1`, with
   \(\deg P_A=12\), \(\deg Q_A=9\), and \(Q_A\) nonconstant.
2. `cancel(P_A/Q_A - h_four_blocks) == 0`.
3. With
   \(h_B(x,y,z)=y^2h_A(z/y,1/y,x/y)\),
   `cancel(P_B/Q_B - h_B) == 0` against the independently reconstructed
   `round6_QP_B.txt`.
4. The underlying \(P_A/Q_A\) and \(P_B/Q_B\) were already compared with a
   freshly copied exact-GMP BG binary at \(24/24\) new rational points with
   zero residual in
   `bots/student-1/data/round6_compact_formula_check.json`.

Thus the four-block identity is an exact algebraic compression of an
independently BG-verified result, not a new numerical fit.

## Structural consequence for the master object

Consider any finite ansatz made only from polynomial prefactors and
positive-part/truncated-power blocks

$$
\sum_\alpha p_\alpha(\omega)\,
\bigl(q_\alpha(\omega)\bigr)_+^{m_\alpha},
\qquad m_\alpha\in\mathbb Z_{\geq0},
$$

including finite orbit sums and products of such blocks, but with no rational
channel denominators.  Inside a fixed full sign chamber, every positive part
is either zero or an ordinary polynomial power.  Hence the ansatz is
polynomial on that chamber.

The exact A-piece function is not polynomial.  If it agreed with a polynomial
on the nonempty open A chamber, rational-function uniqueness would imply
\(P_A=RQ_A\) as a polynomial identity.  This is impossible because \(Q_A\) is
nonconstant and \(\gcd(P_A,Q_A)=1\).  Therefore a pure polynomial
box-spline/truncated-power master is ruled out exactly, without a
finite-dimensional fitting assumption.

The surviving possibility is a **rational signed-channel sum**: positive-part
or Heaviside selectors may choose rational channel blocks.  The four-block
identity is positive evidence for a small seed set, and sign-dependent
activation could explain why another chamber has a larger common
denominator.  The higher-degree reconstruction is still required before that
possibility can be tested.

## Higher-chamber reconstruction status

The required technician thread was `/root/technician`.  It was dispatched
with a two-chamber, 1400-point, degree-13/14 cone/CRT batch and then one
shortened retry.  Both technician turns exhausted their isolated context
before creating code or registering a job.  In accordance with the student
workflow, no nontrivial replacement implementation was attempted in the
student session.  Consequently neither `12ea165a03` nor `7608cb858a` has a
new factored \(Q\) in this round.
