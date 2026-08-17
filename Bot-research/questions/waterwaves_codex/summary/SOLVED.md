# Solved: two-minus closed form

Timestamp: `2026-06-24T22:35:42`

Produced by `student-2` in session `2026-06-24T22-25-01.json`, with the $n=4$
limiting prescription supplied by `student-1` in session
`2026-06-24T22-13-54.json`, and independently verified by the PI using
`bots/pi/code/bg`.

Let $m=n-2$, $u=-\omega_1$, $v=\omega_2$, and
$p_j=\omega_{j+2}$ for $j=1,\ldots,m$. Define
$$
(x)_+^d=\begin{cases}
x^d,&x>0,\\
0,&x\leq0.
\end{cases}
$$
Then, in the two-minus sector $\sigma=(-1,-1,+1,\ldots,+1)$,
$$
\frac{A_n}{i}=-2^{n-1}uv
\sum_{S\subseteq\{1,\ldots,m\}}(-1)^{|S|}
\left(v^2-\sum_{j\in S}p_j^2\right)_+^{n-3}.
$$

Equivalently,
$$
A_n=-i\,2^{n-1}uv
\sum_{S\subseteq\{1,\ldots,m\}}(-1)^{|S|}
\left(v^2-\sum_{j\in S}p_j^2\right)_+^{n-3}.
$$

For $n=4$, strict two-minus kinematics are
$$
\omega=(-b,a,b,-a),
$$
and the formula gives
$$
A_4(-b,a,b,-a)=-8i\,ab\,\min(a^2,b^2).
$$
The direct strict oracle call is singular because two opposite-sign pairs have
zero total $(\omega,K)$, so the PI accepts this value as the path-independent
raw `--amp` limiting prescription.

## PI Verification

The PI copied `bg.cpp` to `bots/pi/code/bg.cpp`, built `bots/pi/code/bg`, and
ran `python3 bots/pi/code/verify_truncated_power.py`. Full details are in
`bots/pi/data/pi_truncated_power_verification.json`.

For the finite on-shell rows below, `free` means the oracle input
$\omega_2,\ldots,\omega_{n-1}$. Every listed comparison had exact residual $0$.

| $n$ | regime | free | full $\omega$ | $A_n/i$ | rel. err. |
| ---: | --- | --- | --- | ---: | ---: |
| $5$ | generic | $5,4,4$ | $(-88/13,5,4,4,-81/13)$ | $-3259520/13$ | $0$ |
| $5$ | large positive leg | $5,20,3$ | $(-146/7,5,20,3,-50/7)$ | $-4309920/7$ | $0$ |
| $5$ | small positive leg | $5,1/100,3$ | $(-80267/26700,5,1/100,3,-1336/267)$ | $-240801/556250$ | $0$ |
| $5$ | signed | $5,3,-3$ | $(-9/5,5,3,-3,-16/5)$ | $-944784/625$ | $0$ |
| $6$ | generic | $4,2,3,5$ | $(-109/14,4,2,3,5,-87/14)$ | $-14314752/7$ | $0$ |
| $6$ | large positive leg | $2,50,3,4$ | $(-3001/59,2,50,3,4,-480/59)$ | $-12292096/59$ | $0$ |
| $6$ | small positive leg | $5,2,1/100,3$ | $(-40091/9100,5,2,1/100,3,-510/91)$ | $-4329828/284375$ | $0$ |
| $6$ | signed | $5,-1,1,1$ | $(-7/6,5,-1,1,1,-29/6)$ | $-1943515/4374$ | $0$ |
| $7$ | generic | $5,2/3,7/2,7/2,2/3$ | $(-1069/160,5,2/3,7/2,7/2,2/3,-3193/480)$ | $-79831105907/52488$ | $0$ |
| $7$ | large positive leg | $2,50,3,4,5$ | $(-3321/64,2,50,3,4,5,-775/64)$ | $-1700352$ | $0$ |
| $7$ | small positive leg | $4,2,1/100,3,5$ | $(-1091401/140100,4,2,1/100,3,5,-8714/1401)$ | $-7465143549564/4560546875$ | $0$ |
| $7$ | signed | $5,-1,1,1,2$ | $(-23/8,5,-1,1,1,2,-41/8)$ | $-88320$ | $0$ |

For $n=4$, direct strict on-shell calls at $(a,b)=(2,3)$, $(2,100)$, and
$(2,1/100)$ exited singular in the PI copy. The PI therefore checked the raw
`--amp` limit at $\epsilon=10^{-18}$ along four paths for each regime:

- `k_plus_12`: $K_3=b^2(1+\epsilon)$ and
  $K_4=a^2(1+2\epsilon)$.
- `k_plus_31`: $K_3=b^2(1+3\epsilon)$ and
  $K_4=a^2(1+\epsilon)$.
- `plus_legs_onshell`: $\omega_3=b(1+\epsilon)$,
  $\omega_4=-a(1+2\epsilon)$, $K_3=\omega_3^2$, and
  $K_4=\omega_4^2$.
- `negative_momenta`: $K_1=-b^2(1-\epsilon)$ and
  $K_2=-a^2(1-2\epsilon)$.

The relative residuals against $A_4=-8i\,ab\,\min(a^2,b^2)$ were:

| regime | `k_plus_12` | `k_plus_31` | `plus_legs_onshell` | `negative_momenta` |
| --- | ---: | ---: | ---: | ---: |
| $(a,b)=(2,3)$ | $1.802083333333\times10^{-18}$ | $4.885416666667\times10^{-18}$ | $1.020833333333\times10^{-18}$ | $2.625000000000\times10^{-18}$ |
| $(a,b)=(2,100)$ | $3.189326000000\times10^{-14}$ | $9.564975500000\times10^{-14}$ | $3.135010000000\times10^{-15}$ | $6.452500000000\times10^{-16}$ |
| $(a,b)=(2,1/100)$ | $1.999999500625\times10^{-12}$ | $9.999985018750\times10^{-13}$ | $1.017512500000\times10^{-16}$ | $1.999999500625\times10^{-12}$ |

The maximum finite-row relative error is $0$, and the maximum accepted $n=4$
limit relative residual is $1.999999500625\times10^{-12}$.
