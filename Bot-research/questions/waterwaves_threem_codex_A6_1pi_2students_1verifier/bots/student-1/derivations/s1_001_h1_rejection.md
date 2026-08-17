# Exact rejection of the minus-pair truncated-cubic ansatz

## Ansatz

Let \(M=\{1,2,3\}\), \(P=\{4,5,6\}\), and for each pair
\(\{a,b\}\subset M\) let \(r=M\setminus\{a,b\}\).  For
\((e_m,e_p)\in\{\pm1\}^2\), define

\[
\Phi_{ab}^{e_m,e_p}(\omega)=
\omega_a\omega_b
\sum_{S\subseteq \{r\}\cup P}(-1)^{|S|}
\left[
\beta_{ab}^2
-e_m{\bf1}_{r\in S}\omega_r^2
-e_p\sum_{j\in S\cap P}\omega_j^2
\right]_+^3,
\qquad
\beta_{ab}^2=\min(\omega_a^2,\omega_b^2).
\]

The leading hypothesis is

\[
\frac{A_6}{i}=C\sum_{\{a,b\}\subset M}\Phi_{ab}^{e_m,e_p},
\]

with a constant \(C\) (equivalently \(C=32c\) in the PI's normalization).
We also tested the weaker labeled-pair relation

\[
\frac{A_6}{i}
=C_{12}\Phi_{12}^{e_m,e_p}
+C_{13}\Phi_{13}^{e_m,e_p}
+C_{23}\Phi_{23}^{e_m,e_p}.
\]

## A two-point exact contradiction for the leading sign choice

Fresh exact `bg` calls and an independent evaluation of the block give:

1. At
   \(\omega=(-5,1,1,3,-3,3)\),
   \[
   A_6/i=-1476,\qquad
   \sum_{a<b}\Phi_{ab}^{+,+}=-9.
   \]
   Hence any common coefficient would have to be \(C=164\).

2. At
   \[
   \omega=\left(-\frac{308}{17},6,10,4,14,-\frac{270}{17}\right),
   \]
   \[
   A_6/i=-\frac{164324622336}{85},\qquad
   \sum_{a<b}\Phi_{ab}^{+,+}=-\frac{819698688}{17}.
   \]
   Substitution of \(C=164\) leaves the nonzero exact residual
   \[
   \frac{A_6}{i}-164\sum_{a<b}\Phi_{ab}^{+,+}
   =\frac{507828301824}{85}.
   \]

Thus the most natural \(e_m=e_p=+1\) form is false without any numerical
tolerance or fitting ambiguity.

## Full exact scan

The reproducible batch used 80 nondegenerate exact rational on-shell samples
covering 15 full subset-sign signatures.  Both supplied six-point anchors were
reproduced exactly.  For every \((e_m,e_p)\in\{\pm1\}^2\):

- no common \(C\) exists;
- the three-column labeled-pair system is inconsistent, with
  \(\operatorname{rank}A=3\) and
  \(\operatorname{rank}[A|y]=4\), except the all-negative sign choice where
  the ranks are \(0\) and \(1\).

The homogeneous fallback contained every orbit-summed feature formed from:

- \(e_m,e_p=\pm1\);
- threshold \(\min(\omega_a^2,\omega_b^2)\) or
  \(\max(\omega_a^2,\omega_b^2)\);
- the nine degree-two prefactors
  \[
  \omega_a\omega_b,\quad
  \omega_a^2+\omega_b^2,\quad
  \omega_r^2,\quad
  (\omega_a+\omega_b)\omega_r,\quad
  (\omega_a+\omega_b)s_+,\quad
  \omega_rs_+,\quad s_+^2,\quad e_{2,+},\quad p_{2,+},
  \]
  where
  \(s_+=\sum_{j\in P}\omega_j\),
  \(e_{2,+}=\sum_{j<k\in P}\omega_j\omega_k\), and
  \(p_{2,+}=\sum_{j\in P}\omega_j^2\).

After exact column deduplication and on-shell identities, the 40-point training
matrix has rank \(14\), while its augmentation by \(A_6/i\) has rank \(15\).
Therefore even this combined 72-feature raw family is exactly inconsistent
before any holdout test.

## Verification

- Exact BG anchors:
  \[
  (-8,2,3,4,5,-6)\mapsto-\frac{9190656}{7}i,
  \]
  \[
  \left(-\frac{154}{17},3,5,2,7,-\frac{135}{17}\right)
  \mapsto-\frac{641893056}{85}i.
  \]
- Five-point harness calibration:
  \[
  \left(-\frac{14}{3},2,3,4,-\frac{13}{3}\right)
  \mapsto -19968\,i,
  \]
  exactly matching the sign-flipped two-minus truncated-square formula.
- `python3 -m py_compile` passes for all three Python scripts.
- The 80-point exact batch and the no-candidate verifier complete successfully;
  `verify_candidate.py` reports `NO VERIFIED CANDIDATE`.

Detailed machine evidence is in `bots/student-1/data/h1_results.json`; the
human-readable generated report is
`bots/student-1/derivations/h1_fit_report.md`.

