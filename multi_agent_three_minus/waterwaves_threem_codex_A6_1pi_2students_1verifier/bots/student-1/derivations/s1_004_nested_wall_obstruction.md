# Claim `s1_004`: the pair-wall brick is a nested spline

## Result

Let

$$
R(\omega)=A_6(\omega)/i-P_{\rm pole}(\omega)
$$

at $g=1$, with `s1_003`'s verifier-confirmed pole prescription.  Across
$q_{24}=\omega_4^2-\omega_2^2=0$, write the two analytic continuations as

$$
R_+-R_-=q_{24}H_{24}.
$$

The exact evidence below answers the round's pivotal question:

$$
\boxed{H_{24}\ \text{is itself a spline, not one global degree-six polynomial}.}
$$

This is an independent top-down cross-check of student-2's simultaneous
bottom-up finding `s2_007`.

## Exact extraction of $H_{24}$

Use the standard resonant coordinates

$$
\omega=(-a,b,c,d,e,-f),\qquad
S=b+c+d+e,
$$

$$
a=d+e+\frac{bc-de}{S},\qquad
f=b+c-\frac{bc-de}{S}.
$$

On the path

$$
b=t,\qquad d=B-t,
$$

$S=B+c+e$ is fixed and the pair wall is $t_0=B/2$.  Since

$$
q_{24}=(B-t)^2-t^2=-2B(t-t_0),
$$

I reconstructed the degree-eight branch polynomials $R_\pm(t)$ from nine
exact off-wall BG values per side, checked two further exact holdouts per
side, checked $R_+(t_0)=R_-(t_0)$, and evaluated

$$
H_{24}=
\frac{R_+'(t_0)-R_-'(t_0)}{-2B}.
$$

No BG evaluation was made on the wall.  At the independent anchor
$(B,c,e)=(10,2,3)$ this gives

$$
H_{24}=\frac{12622720}{27},
$$

exactly matching the previously supplied value.

## One finer wall that does not change $H_{24}$

Set

$$
B=10,\qquad c=u,\qquad e=6-u.
$$

All six wall frequencies are affine in $u$.  The channel
$Q_{1;\{4,6\}}$ is

$$
Q_{1;\{4,6\}}=12u-11,
$$

so it changes sign at $u=11/12$.  Independent degree-six fits to the
extracted $H_{24}(u)$ on both sides are identical; each has two exact zero
holdouts.  Thus this individual $Q$ wall is not the missing nested
subdivision.

## Decisive affine-line obstruction

On the same affine line, use seven exact points

$$
u\in
\left\{\frac76,\frac43,\frac32,\frac53,\frac{11}{6},2,\frac{13}{6}\right\}.
$$

They all have the nine-channel sign pattern
$(-,+,+,+,+,+,+,+,+)$.  They determine

$$
\begin{aligned}
P(u)
={}&\frac{2037485}{16}u^2+\frac{71013}{4}u^3
-\frac{27613}{8}u^4+\frac{657}{4}u^5-\frac{219}{16}u^6\\
={}&-\frac{u^2}{16}
\left(
219u^4-2628u^3+55226u^2-284052u-2037485
\right).
\end{aligned}
$$

The same-cell holdouts $u=7/3,5/2$ give exact zero residual.  Several
earlier changes of the nine-$Q$ pattern also leave the continuation equal
to $P(u)$.  However

$$
Q_{3;\{4,5\}}
=\omega_4^2+\omega_5^2-\omega_3^2
=61-12u
$$

changes sign at $u=61/12$, and on the other side the extracted wall brick
equals

$$
H_{24}(u)=P(6-u),
$$

not $P(u)$.  This identity holds exactly at all five tested values
$u=11/2,13/2,7,9,10$.  For example,

$$
\begin{array}{c|c}
u& H_{24}(u)-P(u)\\ \hline
11/2&-519844635/128\\
13/2&-632120265/128\\
7&-5086080\\
9&-2698200\\
10&4338495/4
\end{array}
$$

while $H_{24}(u)-P(6-u)=0$ at every one of these points.  Hence a single
polynomial $H_{24}$ is impossible, but the branch exchange has a compact
nested/min-like structure on this slice.

## Failure of the simplest top-down nested orbit

For every active channel $T=(m;\{p,q\})$, define the stripped product of
the two known four-point hydrotope blocks

$$
B_T=-64\,\omega_m\omega_{\bar p}Q_T\,
\mathcal H(\min(\omega_m^2,Q_T);p,q)\,
\mathcal H(\min(\omega_{\bar p}^2,Q_T);m',m'').
$$

I tested:

1. a global dual-$S_3$ degree-eight polynomial plus
   $\sum_{Q_T>0}B_T$;
2. the same global polynomial plus all eight orbit sums
   $\sum_{Q_T>0}Q_TP_j\mathcal H_L\mathcal H_R$, with every
   side-exchange-symmetric degree-two prefactor

$$
\begin{gathered}
\omega_m\omega_{\bar p},\quad
\omega_m^2+\omega_{\bar p}^2,\quad
\omega_m(\omega_p+\omega_q)+\omega_{\bar p}(\omega_{m'}+\omega_{m''}),\\
\omega_m(\omega_{m'}+\omega_{m''})+\omega_{\bar p}(\omega_p+\omega_q),\quad
(\omega_p+\omega_q)(\omega_{m'}+\omega_{m''}),\\
(\omega_p+\omega_q)^2+(\omega_{m'}+\omega_{m''})^2,\quad
\omega_p\omega_q+\omega_{m'}\omega_{m''},\quad Q_T.
\end{gathered}
$$

On 200 orbit-inequivalent exact rational BG points spanning all eight
sorted physical words, 61 full subset-sign signatures, and 32 nine-$Q$
patterns, the one-block model has
$\operatorname{rank}A=13<14=\operatorname{rank}[A|R]$; the eight-prefactor
model has $17<18$.  Thus the verified pole product does not by itself
generate the regular nested spline.

## Interpretation and remaining obstruction

The hydrotope paper's one-hyperplane inclusion--exclusion construction
explains a single truncated-power layer in the two-minus sector, but it
explicitly defers the independent three-minus six-point problem.  The
exact switch $P(u)\leftrightarrow P(6-u)$ after a finer $Q$ wall is direct
evidence that the six-point remainder needs coupled/nested chamber data,
such as products of linear truncated powers or an equivalent
two-dimensional positive-geometry construction.  This session does not
derive the full multivariate $H_{mp}$ or the global $R_0$, so it is an
exact obstruction and structural constraint, not the final compact
formula.

## Reproduction

```bash
python3 bots/student-1/code/round3_nested.py --qdir . --samples 200
python3 bots/student-1/code/round3_wall_brick.py
```

Detailed exact data:

- `bots/student-1/data/round3_nested_results.json`
- `bots/student-1/data/round3_wall_brick.json`
- `bots/student-1/derivations/round3_nested_raw_report.md`

