# Group Meeting Notes

Timestamp: `2026-06-24T22:35:42`

No `matias` board instructions are present.

The group has solved the benchmark. `student-2` proposed the truncated-power
formula
$$
\frac{A_n}{i}=-2^{n-1}uv
\sum_{S\subseteq\{1,\ldots,m\}}(-1)^{|S|}
\left(v^2-\sum_{j\in S}p_j^2\right)_+^{n-3},
$$
where $m=n-2$, $u=-\omega_1$, $v=\omega_2$,
$p_j=\omega_{j+2}$, and $(x)_+^d=x^d$ for $x>0$ and $0$ otherwise.

`student-1` resolved the strict $n=4$ obstruction as a limiting prescription:
direct on-shell oracle calls remain singular, but raw off-shell probes lifting
both zero subcurrents converge to
$$
A_4(-b,a,b,-a)=-8i\,ab\,\min(a^2,b^2).
$$
The truncated-power formula specializes to exactly this value at $n=4$.

PI verification used a fresh copied oracle at `bots/pi/code/bg.cpp`, built as
`bots/pi/code/bg`, and an independent exact-rational checker at
`bots/pi/code/verify_truncated_power.py`. The finite checks cover 12 rows at
$n=5,6,7$, including generic, one large positive-sign frequency, one small
positive-sign frequency, and signed-frequency cases. Every finite residual was
exactly $0$.

For $n=4$, the PI confirmed the direct strict calls are singular at
$(a,b)=(2,3)$, $(2,100)$, and $(2,1/100)$. The accepted off-shell limit checks
used $\epsilon=10^{-18}$ and four paths for each regime:
`k_plus_12`, `k_plus_31`, `plus_legs_onshell`, and `negative_momenta`. The
maximum relative residual was $1.999999500625\times10^{-12}$, below the
$10^{-10}$ pass bar.

No further tasks are assigned. `summary/SOLVED.md` is now the final answer and
early-stop sentinel.
