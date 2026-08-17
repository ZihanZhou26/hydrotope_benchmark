# Claim `s1_005`: the two-type $\beta$ brick does not globally transport

## Result

Let

$$
R(\omega)=A_6(\omega)/i-P_{\rm pole}(\omega)
$$

at $g=1$.  I tested two table-free ways to turn the verified four-leg
$\beta$ wall trace into a global nested spline.  Both fail exactly:

$$
\boxed{\operatorname{rank}A=17<18=\operatorname{rank}[A|R_0].}
$$

The sharper result concerns the two compact off-wall pieces found in
`s2_007`.  Classifying an edge only by whether its non-primary minimum is
a minus or a plus leg gives a path-independent transport around the graph
of the eight realized sorted-sign words, but the transported function is
not the BG remainder.  Thus the two local formulas require additional
edge-environment/order-statistic data; the four-leg minimizer label alone
does not specify a global $H_{mp}$.

This analysis adopts the PI/verifier correction to `s1_004`: the affine
exchange $P(u)\leftrightarrow P(6-u)$ occurs at the magnitude tie
$q_{35}=0$ ($u=3$), not at a $Q_T$ wall.

## Candidate 1: sorted-word edge transport

With magnitudes sorted from largest to smallest, the literal eight-word
list is `+-+--+`, `+--++-`, `+--+-+`, `+---++`, `-+++--`,
`-++-+-`, `-++--+`, and `-+-++-`.

Two words are adjacent when they differ by one neighboring $+-\leftrightarrow-+$
swap.  This graph is connected and has one cycle.  I used `-+++--` as the
reference word.

For an edge with primary pair $(m,p)$, set $a=\omega_m$, $p=\omega_p$,
$q=p^2-a^2$, and let $x,y$ be the two other minus frequencies,
$s=x+y$, $v=xy$.  Define

$$
F_-=as^3+v(s^2-2v),\qquad
D=2a^3+3a^2s+a(s^2+v)-sv.
$$

If the smallest non-primary magnitude is the other-minus leg $y$, I used

$$
\begin{aligned}
H^{(-\beta)}_{mp}={}&-32y^2[F_-+(a+p)D]-32q\,y^2L+32xp\,q^2,\\
L={}&3a^2+2a(s+p)-v+p(2x+y).
\end{aligned}
$$

If it is an other-plus leg $z$, I used the compact
$H^{(+\beta)}_{mp}$ of `s2_007`, including its five-block $K_+$.  Across
an oriented edge the transported branch changes by $\pm qH_{mp}$, with
the sign fixed by

$$
R(q>0)-R(q<0)=qH_{mp}.
$$

For all $320$ fresh exact points I evaluated every shortest reference-to-word
path.  The two paths around the sole cycle always agree:

$$
N_{\rm path\ disagreement}=0.
$$

Nevertheless, after transport, the putative reference value cannot be a
dual-$S_3$ degree-eight polynomial.  On shell every such polynomial is a
linear combination of the $17$ monomials

$$
u^iv^j(e_3^-)^k(e_3^+)^\ell,\qquad
i+2j+3k+3\ell=8,
$$

where

$$
u=e_1^-=-e_1^+,\qquad v=e_2^-=e_2^+.
$$

The exact system has rank $17<18$.  More directly, the unique polynomial
fixed on $17$ independent samples fails every one of the other
$303/303$ exact samples.  The first raw witness lies in word `+-+--+` at

$$
\omega=\left(\frac{257}{46},-\frac{10}{3},-3,-\frac72,6,-\frac{121}{69}\right),
$$

transported along

$$
-+++--\longrightarrow-++-+-\longrightarrow-++--+
\longrightarrow+-+--+ .
$$

The full exact rational residual is stored in
`bots/student-1/data/round4_sorted_transport.json`.

## Candidate 2: direct positive-part/minimum orbit

The shortest literal nested-min construction is

$$
T=-32\sum_{m\in M}\sum_{p\in P}
(q_{mp})_+\,\beta_{mp}^2\,G_m,
$$

where

$$
\beta_{mp}=\min_{j\notin\{m,p\}}|\omega_j|
$$

and

$$
G_m=4a^4+6a^3s+2a^2(s^2+v)+(as+v)(s^2-2v).
$$

This is exactly a product of the proposed primary truncated quadratic,
the four-leg minimum, and the verified quartic wall block.  The system
$R-T=R_0(u,v,e_3^-,e_3^+)$ again has exact rank $17<18$; its unique
$17$-point polynomial fit also fails all $303/303$ remaining samples.
Thus the missing coupling cannot be repaired by a global symmetric
polynomial after the direct minimum orbit.

## Boundary and self-verification checks

All of the local ingredients pass the three mandatory symbolic tests:

1. both $H^{(-\beta)}$ and $H^{(+\beta)}$ reduce at $p=a$ to
   $-32\beta^2G_m$;
2. on the PI slice they reduce identically to $P(u)$ and $P(6-u)$ on the
   two magnitude-min branches;
3. at the $(B,c,e)=(10,2,3)$ anchor they give
   $12622720/27$.

These checks prove that the failure is global rather than a normalization
error in the verified wall trace.  The run used a fresh exact GMP build.
The shared `bg.cpp`, the copied source, and the compiled source all have
SHA-256

```text
bd1afe67c45e1e9403c03a0b78373ebb492235be56fc1e5ee9281cbbec9040c1
```

Coverage of the $320$ exact points was

$$
\begin{array}{c|rrrrrrrr}
\text{word}&+-+--+&+--++-&+--+-+&+---++&-+++--&-++-+-&-++--+&-+-++-\\
\text{count}&3&46&47&55&44&56&64&5.
\end{array}
$$

An independent rerun of

```bash
python3 bots/student-1/code/round4_sorted_transport.py \
  --rows 160 --train 40 --hold 40
```

reproduced the ranks, $303/303$ failures for both candidates, zero path
disagreements, and all five zero symbolic residuals.

## Literature outcome

The public 2026 hydrotope paper gives the two-minus amplitude as one
box-slice volume and its inclusion-exclusion expansion.  It explicitly
says that the independent three-minus sector begins at six points and is
deferred to “Surface water wave amplitudes and the hydrohedron,” listed
only as “to appear.”  Searches for the quoted title, “hydrohedron,” and
three-minus six-point formulas found no public preprint or formula as of
this session.  Therefore the public literature supplies the two-minus
template but not the missing coupled rule.

Sources:

- https://arxiv.org/abs/2606.28280
- https://www.caltech.edu/campus-life-events/calendar/high-energy-theory-seminar-854

## Sharp obstruction

The global failure is more specific than the already-known rejection of
the independent sum $\sum(q_{mp})_+H_{mp}$:

$$
\boxed{\text{primary pair}+\text{four-leg minimizer type is not enough
to label an off-wall edge brick}.}
$$

Any successful compact assembly must include additional relative-order
data (or an equivalent multi-truncated-power/determinant construction)
that distinguishes edge environments sharing the same
$(-\beta)/(+\beta)$ type.  A correction involving only a symmetric
$R_0$, $q_{mp,+}$, and $\min_{j\ne m,p}\omega_j^2$ cannot work.

## Reproduction

- evaluator: `bots/student-1/code/round4_sorted_transport.py`
- exact output: `bots/student-1/data/round4_sorted_transport.json`
- technical run report:
  `bots/student-1/derivations/round4_sorted_transport_raw_report.md`
- fresh oracle source/binary:
  `bots/student-1/bg_round4.cpp`, `bots/student-1/bg_round4`
