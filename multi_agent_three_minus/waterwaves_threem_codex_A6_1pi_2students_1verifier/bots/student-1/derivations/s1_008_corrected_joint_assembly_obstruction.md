# Claim `s1_008`: the corrected \(R_Q\) subtraction does not cure the \(q\)-assembly rank defect

## Question tested

At \(g=1\), form the settled pole-subtracted spline
\[
R_{\rm spline}=A_6/i-P_{\rm pole}
\]
with the degree-eight pole part \(P_{\rm pole}=S_1\) of `pole_batch.py`, and
subtract the confirmed cubic triple-wall orbit
\[
R_Q=-32\sum_{\substack{m\in\{1,2,3\}\\p<q\in\{4,5,6\}}}
(Q_{m;pq})_+^3\,\omega_m\omega_t,\qquad
Q_{m;pq}=\omega_p^2+\omega_q^2-\omega_m^2,
\]
where \(t\) is the omitted plus leg.  The clean remainder is
\[
S=R_{\rm spline}-R_Q.
\]

The round tested whether either of the two previous pair-wall assemblies
leaves a single dual-\(S_3\) symmetric degree-eight polynomial \(R_0\):

1. the path transport assembled from the two local
   \(H_{mp}^{(-\beta)}\) and \(H_{mp}^{(+\beta)}\) bricks;
2. the compact direct orbit
   \[
   T=-32\sum_{m,p}(q_{mp})_+\,\beta_{mp}^2G_m,\qquad
   \beta_{mp}=\min_{j\notin\{m,p\}}|\omega_j|,
   \]
   with \(G_m\) exactly as defined in `s1_005`.

## Corrected exact result

Neither assembly closes.  In the complete on-shell dual-symmetric basis
\[
\left\{u^iv^j(e_3^-)^k(e_3^+)^\ell:
i+2j+3k+3\ell=8\right\},
\qquad |\mathcal B_{\rm sym}|=17,
\]
both targets give
\[
\boxed{\operatorname{rank}A=17<18=\operatorname{rank}[A|y]}.
\]

| target for \(R_0\) | train rows | all exact rows | rank \(A\) | rank augmented |
|---|---:|---:|---:|---:|
| \(S-\) path increment | \(160\) | \(550\) | \(17\) | \(18\) |
| \(S-T\) | \(160\) | \(550\) | \(17\) | \(18\) |

The path increments themselves are cycle-consistent: there were zero path
disagreements.  Thus their failure is not a graph-orientation error; the
two local \(\beta\)-type bricks do not give the BG \(q\)-orbit globally.

As a second exact check, a greedy full-rank 17-point interpolation was made
for each target and tested on every other row.  Each interpolation fails
all \(533/533\) remaining exact points, spanning \(106\) full chamber
signatures and seven of the eight magnitude words not exhausted by the
17 fit rows.  The complete 550-point sample spans all eight realized words,
113 distinct full chamber signatures, and has word counts
\[
(6,74,86,108,86,84,101,5).
\]

Consequently the round-6 hypothesis that the old \(17<18\) defect was
caused only by the omitted \(R_Q\) orbit is false.  The order-one \(q\)-wall
assembly still lacks environment dependence beyond the tested
four-leg-minimum selector.  No global symmetric \(R_0\) can be extracted
from either tested \(R_q\), and no complete formula or definition-of-done
battery is claimed.

## Anchor and normalization guard

A first technician run accidentally used the degree-six negative control
\(S_0\), the second return of `build_channels`, instead of the settled pole
part \(S_1\), its third return.  That run is invalid and was overwritten.
The corrected harness now aborts unless the standing anchor is reproduced:
\[
\begin{aligned}
\omega&=(-8,2,3,4,5,-6),\\
A_6/i&=-9190656/7,\\
P_{\rm pole}&=42588288/7,\\
R_{\rm spline}&=-7396992.
\end{aligned}
\]
At the same point it finds
\[
R_Q=-136630560,\qquad S=129233568,\qquad
T=66248000,\qquad S-T=62985568,
\]
and both algebraic decompositions have zero anchor residual.

This interface audit also reveals that the old round-4 script underlying
`s1_005` selected \(S_0\) by tuple position.  Its detailed old numerical
residuals should therefore not be reused.  The structural obstruction is
re-established here from scratch with the correct \(P_{\rm pole}\) and the
confirmed \(R_Q\) subtraction.

## Self-verification and reproduction

The implementation-only technician thread was `/root/technician`.  I then
independently reran

```bash
python3 bots/student-1/code/round6_assembly.py \
  --qdir . --rows 320 --train 160 --hold 160 \
  --output bots/student-1/data/round6_assembly_selfcheck.json \
  --report bots/student-1/derivations/round6_assembly_selfcheck_report.md
```

The independent run rebuilt the immutable source copy exactly, with both
SHA-256 hashes equal to
`bd1afe67c45e1e9403c03a0b78373ebb492235be56fc1e5ee9281cbbec9040c1`,
and reproduced the anchor, sample counts, zero path disagreements, both
\(17<18\) ranks, and the same first inconsistent row.  Every amplitude
used in the result came from the fresh exact GMP binary
`bots/student-1/bg_round6`; no `--double` evaluations were used.

Detailed artifacts:

- implementation: `bots/student-1/code/round6_assembly.py`;
- primary exact output: `bots/student-1/data/round6_assembly.json`;
- independent exact rerun: `bots/student-1/data/round6_assembly_selfcheck.json`;
- raw reports: `bots/student-1/derivations/round6_assembly_raw_report.md` and
  `bots/student-1/derivations/round6_assembly_selfcheck_report.md`;
- fresh oracle source/binary: `bots/student-1/bg_round6.cpp`,
  `bots/student-1/bg_round6`.
