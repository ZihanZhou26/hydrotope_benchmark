# Round 5: exact negative for simple-channel orbit sums

Timestamp: 2026-07-26T15:40:35 UTC.

## Ansatz tested

Set

$$
M=\{1,2,3\},\qquad P=\{4,5,6\},\qquad
H=\frac{A_6}{i\prod_{j=1}^{6}\omega_j}.
$$

For each pair or triple channel define

$$
\Omega_S=\sum_{i\in S}\omega_i,\qquad
K_S=\sum_{i\in S}\sigma_i\omega_i^2,\qquad
h_S=\Omega_S^2-|K_S|.
$$

There are $15$ pair channels and $10$ triple channels after identifying a
triple with its complement.  Under
$G=(S_3\times S_3)\rtimes C_2$, they have four orbits represented by

$$
\{1,2\},\quad \{1,4\},\quad \{1,2,3\},\quad \{1,2,4\}.
$$

For an oriented channel $S$, split the legs into the four cells
$M\cap S$, $P\cap S$, $M\setminus S$, and $P\setminus S$.  Let $m_d$ denote
a monomial of weighted degree $d$ in the elementary symmetric polynomials of
these four cells.  The tested representation was the finite universal orbit
sum

$$
H=P_2+
\sum c_{S,m_4}\sum_{g\in G}\frac{m_4(g\omega)}{h_{gS}}
\sum d_{S,m_2,T}\sum_{g\in G}
 \frac{m_2(g\omega)\,|K_{gT}|}{h_{gS}}
\sum e_{S,T,U}\sum_{g\in G}
 \frac{|K_{gT}|\,|K_{gU}|}{h_{gS}}.
$$

Here $P_2$ runs over the complete degree-two $G$-invariant polynomial basis.
The $T,U$ pair tier uses stabilizer-relative channel pairs.  Every coefficient
is attached to a full symmetry orbit; there are no per-channel coefficients,
chamber flags, or fitted chamber tables.

After exact symbolic deduplication the stages contained:

- Stage A: $3$ polynomial plus $24$ signed-polynomial channel features,
  hence $27$ columns.
- Stage B: Stage A plus $300$ one-$|K|$ features and $263$ two-$|K|$
  features, hence $590$ columns.

All terms have the required degree: their numerators have degree four and
division by $h_S$ leaves degree two.

## Exact test

The technician thread `/root/technician` copied the immutable `bg.cpp`
byte-for-byte to `bots/student-1/code/bg_round5_channels.cpp`, built it against
GMP, and implemented the fit in
`bots/student-1/code/round5_channel_fit.py`.  The corrected production run used

```text
python3 bots/student-1/code/round5_channel_fit.py \
  --max-points 400 --max-attempts 20000 --bg-timeout 1.0 --holdout 120
```

Every sample was freshly evaluated by the copied exact BG binary.  The script
checked

$$
\sum_i\omega_i=0,\qquad
\sum_i\sigma_i\omega_i^2=0,\qquad
\Re A_6=0,
$$

and used the exact target $H=(A_6/i)/\prod_i\omega_i$.  It collected $790$
nondegenerate rational points, split as $670$ training and $120$ holdout
points, spanning $140$ momentum-wall signatures and $387$ full signatures
(the $18$ momentum walls plus $35$ factorization signs).  The deterministic
hierarchical families were included in the sample generator.

The modular feature cache was checked directly against exact rational feature
evaluation.  On both primes,

$$
p_1=2^{61}-1,\qquad p_2=1000000007,
$$

the ranks were

$$
\begin{array}{c|cc}
 & \operatorname{rank}X & \operatorname{rank}[X\mid H]\\ \hline
\text{Stage A} & 23&24\\
\text{Stage B} &166&167
\end{array}
$$

for both $p_1$ and $p_2$.  Thus both linear systems are inconsistent.

I independently reran the corrected construction on $220$ freshly evaluated
exact BG points, with $77$ momentum-wall and $149$ full signatures.  All
conservation checks and exact-to-modular feature checks passed.  For the full
$590$-column Stage B, both primes again gave
$\operatorname{rank}X=166$ and
$\operatorname{rank}[X\mid H]=167$.

## Conclusion and obstruction

The compact simple-propagator hypothesis does not work with any universal
homogeneous degree-four numerator assembled from signed cell-symmetric
polynomials and up to two absolute momentum sums.  This excludes a much wider
class than a bare polynomial numerator, while preserving the requested finite
orbit-sum structure.

It does **not** exclude all possible channel representations.  The next
missing analytic ingredient must be qualitatively different: compatible
multi-propagator terms $1/(h_Sh_T)$ inherited from deeper trees,
non-polynomial/sign-definite numerator blocks, or a genuine positive-part
construction not reducible to the tested $|K|$ orbit library.  Adding more
coefficients to the same simple-$h_S$ numerator class is not supported by this
test.
