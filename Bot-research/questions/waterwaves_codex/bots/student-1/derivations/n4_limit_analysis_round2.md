# Round 2 $n=4$ Limit Analysis

Timestamp: `2026-06-24T22:13:54`

## Strict kinematics

For $n=4$ in the two-minus sector,
$$
\sigma=(-1,-1,+1,+1),
$$
the two resonant constraints force
$$
\omega=(-b,a,b,-a),\qquad K=(-b^2,-a^2,b^2,a^2),
$$
where $a=\omega_2=-\omega_4$ and $b=\omega_3=-\omega_1$.

Thus two opposite-sign pairs have zero total energy and momentum:
$$
\omega_1+\omega_3=0,\quad K_1+K_3=0,
$$
and
$$
\omega_2+\omega_4=0,\quad K_2+K_4=0.
$$

The copied oracle raises `SIGFPE` in strict exact on-shell mode. The
$\{2,4\}$ zero pair appears as a rest-side Berends--Giele subcurrent with a
zero propagator denominator. The $\{1,3\}$ zero pair also has to be lifted:
probes that perturb only $K_4$ still raise `SIGFPE`, consistent with the
vertex kernel seeing a zero internal momentum sum from the canceling root-side
pair.

## Off-shell paths

I tested four raw `--amp` paths, each lifting both zero pairs:

- `k_plus_12`: $K_3=b^2(1+\epsilon)$ and $K_4=a^2(1+2\epsilon)$ with all
  $\omega_i$ fixed.
- `k_plus_31`: $K_3=b^2(1+3\epsilon)$ and $K_4=a^2(1+\epsilon)$ with all
  $\omega_i$ fixed.
- `plus_legs_onshell`: $\omega_3=b(1+\epsilon)$ and
  $\omega_4=-a(1+2\epsilon)$, with $K_3=\omega_3^2$ and
  $K_4=\omega_4^2$.
- `negative_momenta`: $K_1=-b^2(1-\epsilon)$ and
  $K_2=-a^2(1-2\epsilon)$ with all $\omega_i$ fixed.

For each path I used
$$
\epsilon=10^{-1},10^{-2},10^{-3},10^{-4},10^{-5},10^{-6},10^{-8},
10^{-10},10^{-12},10^{-14},10^{-16},10^{-18}.
$$

The full exact rational outputs are in
`bots/student-1/data/n4_limit_probes_round2.json`; the readable table is
`bots/student-1/data/n4_limit_probes_round2.md`.

## Conjectured limit

The data support the path-independent limiting prescription
$$
A_4(-b,a,b,-a)=-8i\,a b\,\min(a^2,b^2).
$$
Equivalently, on the strict $n=4$ two-minus locus,
$$
A_4=-8i\,\omega_2\omega_3\min(\omega_2^2,\omega_3^2),
\qquad
\omega_1=-\omega_3,\quad \omega_4=-\omega_2.
$$

At $\epsilon=10^{-18}$, the largest relative residual of any tested path
against this conjectured limit is about $2.0\times10^{-12}$, occurring in the
$b\ll a$ momentum-only paths. The other required cases are smaller, with the
$b\gg a$ paths below $9.6\times10^{-14}$ and the generic paths below
$4.9\times10^{-18}$.

This does not remove the direct strict-oracle singularity. It supplies a
candidate limiting value for PI verification if the group accepts raw
off-shell limits as the $n=4$ prescription.
