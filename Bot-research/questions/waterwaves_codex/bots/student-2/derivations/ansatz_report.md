# Student-2 ansatz report

Timestamp: `2026-06-24T22:00:14Z`

## Setup

I copied `bg.cpp` to `bots/student-2/code/bg.cpp` and built the private oracle:

```sh
g++ -O2 -std=c++17 -I"$(brew --prefix gmp)/include" -L"$(brew --prefix gmp)/lib" -o bg bg.cpp -lgmpxx -lgmp
```

All data below come from this copied exact-rational oracle unless noted.

Let
$$u=-\omega_1,\qquad v=\omega_2,\qquad p_a=\omega_{a+2}\quad (a=1,\ldots,m),\qquad m=n-2,$$
where the $p_a$ are the $\sigma=+1$ legs.  The on-shell constraints imply
$$e_1(p)=u-v,\qquad e_2(p)=-uv.$$
Thus nontrivial symmetric dependence starts at $e_3(p)$ for $n\geq 5$.

## Generated artifacts

- `bots/student-2/data/oracle_dataset.json`: exact oracle rows for $n=4,5,6,7$.
- `bots/student-2/data/ansatz_checks.json`: exact residuals for tested ansatz families.
- `bots/student-2/data/structural_checks.json`: permutation and homogeneity checks.
- `bots/student-2/code/analyze_ansatz.py`: reproduction script.

## Structural checks

For finite oracle rows, the amplitude was purely imaginary.  Positive-sign leg
permutation checks passed:

$$A_5(-9/2,2,5/2,3,-3)=A_5(-9/2,2,3,5/2,-3)=-2304\,i,$$

and

$$A_6(-289/44,2,5/2,3,7/2,-195/44)=A_6(-289/44,2,3,5/2,7/2,-195/44)=-295936\,i/11.$$

Scaling all frequencies by $2$ gave
$$A_5\mapsto 64A_5,\qquad A_6\mapsto 256A_6,\qquad A_7\mapsto 1024A_7,$$
consistent with homogeneity degree $2n-4$ in these tests.

## Failed ansatz families

The product-only ansatz
$$A_n/i=C_n\,e_m(p)$$
fails immediately.  The ratios $(A_n/i)/e_m(p)$ are not constant:

- $n=5$: $512/5,\ 58880/3087,\ 16/13125,\ 566866496/2626965,\ 100848/325,\ 8748/35$.
- $n=6$: $4734976/20475,\ 2137920/3283,\ 2506/92109375,\ 7515666594688/8310049605,\ 29579/7,\ 161838/343$.
- $n=7$: $17334272/38955,\ 19904/38314453125,\ 3581189569594112/1049894992575,\ 4886720/67$.

The broader family
$$A_n/i=e_m(p)\,P_{n-2}(u,v),$$
where $P_{n-2}$ is an arbitrary homogeneous polynomial in $u,v$, also fails on
held-out rows:

- $n=5$: fitting $P_3$ exactly on 4 rows gives held-out residuals
  $$\frac{42098703590200259394261536919533210051}{235249865900301201984675178831524},\quad
  \frac{325290696040822287553023590406}{6166686595027444825823495},$$
  with max relative residual about $1.72\times 10^1$.
- $n=6$: fitting $P_4$ exactly on 5 rows gives held-out residual
  $$\frac{575947664143372749488902019636661299323864808925577772589561578367594663250273621224}{18044027808592923858620113311156501635197007814960425821730188142092033213045},$$
  with relative residual about $3.15\times 10^1$.

The simple monomial-like forms
$$A_n/i=-2^{n-1}e_muv,\qquad
A_n/i=-2^{n-1}e_m u^{n-3}v,\qquad
A_n/i=-2^{n-1}e_m uv^{n-3},$$
and
$$A_n/i=-2^{n-1}e_m\frac{(uv)^{n-2}}{u+v}$$
all fail with nonzero residuals in `ansatz_checks.json`; max relative residuals are already large at $n=5$.

## Oracle singularity observed

For $n=4$, exact on-shell two-minus kinematics force
$$\omega=(-b,a,b,-a),$$
so the oracle encounters zero-momentum subcurrents.  The exact path exits with
`SIGFPE`, and double mode returns `nan`.  I recorded five such exact failures in
`oracle_dataset.json`.  I do not treat these as amplitude evidence.

One $n=7$ non-generic exact row also failed with `SIGFPE`:
`free_w = 5,1/7,2,3,4`.  Other nearby non-generic rows at $n=5,6,7$ produced finite exact values and were included.

## Conclusion

I did not find a final formula.  The useful narrowing result is that $A_n/i$ is
not captured by $e_m(p)$ times a function of only the two negative-sign legs
$u,v$.  A viable symmetric formula must involve additional positive-leg
elementary symmetric data beyond the full product, starting with $e_3(p)$ and
higher for $n\geq 6$, or must be a more complicated rational expression with
subchannel-sensitive structure.
