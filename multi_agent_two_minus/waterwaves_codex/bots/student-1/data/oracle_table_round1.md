# Round 1 Oracle Table

Private oracle build: `bots/student-1/code/bg` from copied `bg.cpp`.
All primary values below use exact GMP rational mode. The final column is the relative difference between exact rational $\operatorname{Im} A_n$ converted to double and the oracle's `--double` path.

| case | $n$ | regime | free $\omega_2,\ldots,\omega_{n-1}$ | signs | solved $\omega_1,\ldots,\omega_n$ | $A_n$ | double rel. diff. |
| --- | ---: | --- | --- | --- | --- | --- | ---: |
| s1_n4_generic | 4 | generic | `2,3` | `-1,-1,1,1` | `-3, 2, 3, -2` | strict on-shell oracle: exact `SIGFPE`, double `nan`; raw probe $\epsilon=1/1000000000000$ gives $i\,(-5759999999995187999999983979000000001989/30000000000028999999999980875000000000)$ | n/a |
| s1_n4_large_plus | 4 | one plus-sign free leg much larger | `2,100` | `-1,-1,1,1` | `-100, 2, 100, -2` | strict on-shell oracle: exact `SIGFPE`, double `nan`; raw probe $\epsilon=1/1000000000000$ gives $i\,(-407999986987758079983857148959354812501/63750000000032524999960906250000000)$ | n/a |
| s1_n4_small_plus | 4 | one plus-sign free leg much smaller | `2,1/100` | `-1,-1,1,1` | `-1/100, 2, 1/100, -2` | strict on-shell oracle: exact `SIGFPE`, double `nan`; raw probe $\epsilon=1/1000000000000$ gives $i\,(-257279485491585761373459360561597446367999999/16080000003216080200000008000100000000000000000000)$ | n/a |
| s1_n5_generic | 5 | generic | `2,5/2,3` | `-1,-1,1,1,1` | `-9/2, 2, 5/2, 3, -3` | $i\,(-2304)$ | 0.000e+00 |
| s1_n5_large_plus | 5 | one plus-sign free leg much larger | `2,100,3` | `-1,-1,1,1,1` | `-701/7, 2, 100, 3, -34/7` | $i\,(-358912/7)$ | 2.389e-09 |
| s1_n5_small_plus | 5 | one plus-sign free leg much smaller | `2,1/100,3` | `-1,-1,1,1,1` | `-50167/16700, 2, 1/100, 3, -335/167` | $i\,(-4013309833/52187500000)$ | 3.973e-11 |
| s1_n6_generic | 6 | generic | `2,5/2,3,7/2` | `-1,-1,1,1,1,1` | `-289/44, 2, 5/2, 3, 7/2, -195/44` | $i\,(-295936/11)$ | 2.502e-14 |
| s1_n6_large_plus | 6 | one plus-sign free leg much larger | `2,100,3,7/2` | `-1,-1,1,1,1,1` | `-43579/434, 2, 100, 3, 7/2, -1755/217` | $i\,(-89249792/217)$ | 1.655e-06 |
| s1_n6_small_plus | 6 | one plus-sign free leg much smaller | `2,1/100,3,7/2` | `-1,-1,1,1,1,1` | `-448351/85100, 2, 1/100, 3, 7/2, -5517/1702` | $i\,(-2152030998328351/1329687500000000)$ | 6.433e-10 |
| s1_n7_generic | 7 | generic | `2,5/2,3,7/2,4` | `-1,-1,1,1,1,1,1` | `-529/60, 2, 5/2, 3, 7/2, 4, -371/60` | $i\,(-4333568/15)$ | 5.797e-12 |
| s1_n7_large_plus | 7 | one plus-sign free leg much larger | `2,100,3,7/2,4` | `-1,-1,1,1,1,1,1` | `-45379/450, 2, 100, 3, 7/2, 4, -2623/225` | $i\,(-743489536/225)$ | 4.008e-03 |
| s1_n7_small_plus | 7 | one plus-sign free leg much smaller | `2,1/100,3,7/2,4` | `-1,-1,1,1,1,1,1` | `-948751/125100, 2, 1/100, 3, 7/2, 4, -12325/2502` | $i\,(-242871148142199211249/9773437500000000000)$ | 8.727e-09 |
