# Claim `s1_009`: the round-7 continuous hinge-orbit test produced no scientific rank

## Continuity-constrained ansatz

I chose a top-down construction independent of the retired two-block
$\beta$ selector.  Put
$$
q_{mp}=\omega_p^2-\omega_m^2,\qquad
h_{mp}=(q_{mp})_+ ,
$$
for $m\in M=\{1,2,3\}$ and $p\in P=\{4,5,6\}$.  A seed of total
frequency degree eight is
$$
\prod_{m,p}h_{mp}^{r_{mp}}\prod_{i=1}^6\omega_i^{\alpha_i},
\qquad
\sum_{m,p}r_{mp}=d,\qquad
\sum_i\alpha_i=8-2d,
$$
with $1\leq d\leq4$.  Summing every seed over its distinct
$S_3(M)\times S_3(P)$ orbit gives a manifestly dual-symmetric, homogeneous,
globally continuous feature.  Products with $d\geq2$ are the candidate
higher-codimension cocycle corrections absent from nine independent
single-wall bricks.  The intended exact system was
$$
S=R_0+\sum_f c_f\Phi_f,
$$
where $R_0$ spans the established 17-dimensional global dual-symmetric
degree-eight basis.

This is a finite test of a polynomial-in-hinges realization of the missing
$q$-spline.  A successful sparse solution would be table-free; an
inconsistency would reject only this hinge algebra, not all multivariate
truncated-power constructions.

## Durable computation completed

The sole required implementation thread was `/root/technician`.  Its driver
`bots/student-1/code/round7_hinge_orbit.py` completed a fresh exact-GMP build
and the orbit enumeration before stalling:

- copied and compiled `bg.cpp` with identical SHA-256
  `bd1afe67c45e1e9403c03a0b78373ebb492235be56fc1e5ee9281cbbec9040c1`;
- reproduced the exact anchor
  $A_6/i=-9190656/7$, $P_{\rm pole}=42588288/7$,
  $R_Q=-136630560$, and $S=129233568$;
- read 550 exact rows spanning all eight realized magnitude words;
- generated 13,788 raw seeds and 588 nonzero canonical orbit features:
  $188$, $244$, $134$, and $22$ at hinge depths $1$, $2$, $3$, and $4$.

These facts are checkpointed in
`bots/student-1/data/round7_hinge_orbit.json`.

## Blocking implementation defects

No `rank_reports`, coefficient file, exact residual, or raw report was
produced.  The pure-Python modular elimination used full row reduction inside
every pivot loop and did not finish after the two allowed long waits.  I
interrupted the still-running thread rather than leave it consuming resources.

More importantly, inspection of the returned driver found that the implemented
matrix contains only the 588 hinge features.  It never appends the required
17 `basis_A` columns for $R_0$, despite the batch specification.  Therefore
even a late rank from that driver would not test the stated system and must
not be interpreted as a scientific obstruction.

The exact round-7 conclusion is consequently
$$
\boxed{\text{no continuity rank was obtained and no }R_q,\ R_0,\text{ or }A_6
\text{ candidate is claimed}.}
$$

## Narrow repair

Reuse the completed canonical feature enumeration, but:

1. append the 17 stored `basis_A` columns explicitly;
2. evaluate cumulative depths $d\leq1,2,3,4$ on the same word-spanning rows;
3. use a compiled finite-field backend (Wolfram `RowReduce`, Julia/Nemo, or
   FLINT), not Python scalar elimination;
4. require agreement of $\operatorname{rank}A$ and
   $\operatorname{rank}[A|S]$ at two primes before exact recovery;
5. only if consistent, recover a sparse rational support and verify it on all
   550 exact rows plus fresh BG holdouts.

This repair is sharply scoped; no BG resampling or orbit re-enumeration is
needed.

## Literature check

The public hydrotope paper still says the independent three-minus sector will
be treated in future work and cites *Surface water wave amplitudes and the
hydrohedron* only as “to appear”; no public sequel was found:

- N. Arkani-Hamed et al., *Surface Water Wave Scattering and the Hydrotope*,
  arXiv:2606.28280, https://arxiv.org/abs/2606.28280.

Its box-spline reference supports truncated-power searches, but not this
specific hinge basis.  Recent work on splines over hyperplane-arrangement fans
also stresses that such spline modules need not be free and can depend on the
geometry of the arrangement.  Thus a future failure of the simple hinge
algebra would point toward genuine module generators/Koszul syzygies rather
than refuting a compact nested spline:

- C. Checa et al., *Trivariate Splines on Fans of Hyperplane Arrangements and
  Koszul Homology*, arXiv:2606.18298,
  https://arxiv.org/abs/2606.18298.

