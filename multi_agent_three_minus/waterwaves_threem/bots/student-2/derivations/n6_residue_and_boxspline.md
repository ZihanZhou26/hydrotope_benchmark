# Round 5 (student-2, top-down): the box-spline-of-squares lead is dead; the residue is irreducibly chamber-dependent; the closed form is a truncated-power spline in LEG variables

## State entering round 5 (PI-verified)
$$A_n^{3-}=i\,2^{n-1}g^{3-n}\,\frac{N_n(\omega)}{D_n^{\min}},\qquad
D_6^{\min}=e_3^-+e_3^+=\omega_1\omega_2\omega_3+\omega_4\omega_5\omega_6,$$
with $N_6$ a degree-11, $S_3\wr Z_2$-symmetric, $\omega\to-\omega$-**odd** continuous SPLINE;
$A_6$ has a SIMPLE pole on the matching hypersurface $\{e_3^-+e_3^+=0\}$. Jumps: $(1{=}1)$ wall
$\omega_i=\omega_j\to(k_{ij})^1$; $(1{=}2)$ wall $\omega_i^2=\omega_j^2+\omega_k^2\to(k_{ijk})^3$.
My round-5 task (top-down, all-$n$): conjecture+test an explicit closed form for $N_n$
(box-spline of $x_i=\omega_i^2$ / matching-sum), coordinating with student-1's jump coefficients.

## Result 1 — the literal box-spline-of-$\omega_i^2$ form is RULED OUT (retires my s2_008)

A multivariate B-spline / box spline / truncated power of the knots $x_i=\omega_i^2$ is
**piecewise-polynomial** and **even** in each $\omega_i$. Two independent obstructions:

1. **Pole.** $A_n$ is genuinely **rational** (PI-verified pole order exactly 1 at $e_3^-+e_3^+=0$;
   `recon_num.py`: per chamber $A_6/i=-3456\,(\text{sextic})/(17(t-10)(t-9)(t+7)(t+8))$, a nonconstant
   denominator). A box spline is piecewise-polynomial, so **$A_n$ itself is not a box spline**.

2. **Parity.** The only polynomial object is the numerator $N_n$, and it is **odd** under
   $\omega\to-\omega$ (verified exactly: `verify_r5.py` part (C), $N_6(-\omega)=-N_6(\omega)$,
   while $A_6(-\omega)=A_6(\omega)$ even). A box spline of the even knots $\{\omega_i^2\}$ is **even**.
   Hence **$N_n$ is not a box spline of squares** either; at most $N_n=(\text{odd factor})\times(\text{even box spline})$.
   But if the odd factor were $(e_3^-+e_3^+)$ then $A_n=i2^{n-1}g^{3-n}(\text{even box spline})$ would be
   **polynomial**, contradicting rationality. So no clean box-spline-of-squares factorization survives.

Also note the natural wall variables are $\omega_i^2$ (walls $\omega_i^2=\omega_j^2$, $\omega_i^2=\omega_j^2+\omega_k^2$
are **linear in $\omega^2$**, not in $\omega$), so a box spline of the $\omega_i$ themselves is excluded too
(its walls would be linear in $\omega$). **Conclusion:** the s2_008 box-spline lead in its literal form
is dead. The closed form must be a **truncated-power spline in LEG variables**:
$$N_n=B+\sum_{(1{=}1)\text{ walls}}(k_{ij})_+^{1}\,P_{ij}+\sum_{(1{=}2)\text{ walls}}(k_{ijk})_+^{3}\,Q_{ijk},$$
$B$ a symmetric base, $P_{ij}$ (deg 9), $Q_{ijk}$ (deg 5) jump coefficients — student-1's bottom-up object.

## Result 2 — the pole residue is irreducibly CHAMBER/BRANCH-dependent (no global-residue shortcut)

I tested the tempting simplification "$A_6=i2^5g^{-3}[\rho/(e_3^-+e_3^+)+W]$ with a single **global**
symmetric residue $\rho$ and a lower-degree regular spline $W$." The residue
$\rho=N_6|_{\text{matching pt}}$ is **not** a single function of the symmetric invariants.

- **Symmetry forces it.** A matching point has $(\omega_4,\omega_5,\omega_6)=(-\omega_{\sigma^{-1}})$, a
  permutation of $(-\omega_1,-\omega_2,-\omega_3)$. Both the $\omega\to-\omega$ flip (under which $N_6$ is ODD)
  and the $Z_2$ triple-swap (under which $N_6$ is INVARIANT) send the matching point to the **same**
  $S_3\times S_3$-orbit. A single global $\rho=f(\text{invariants})$ would then satisfy $f=-f$, i.e. $\rho\equiv0$
  — contradicting the data ($\rho\ne0$). The escape is that $N_6$ is a **spline**: the per-chamber polynomial
  evaluated by analytic continuation to the (shielded, off-chamber) matching point is **chamber-dependent**.

- **Data (`residue_canon.py`).** At fixed matched magnitudes $\{p,q,r\}=\{2,7,15\}$ two distinct
  signed-minus configurations give $\rho\in\{44335898880,\ -18923520\}$ — **unrelated** (not $\pm$ of
  each other), proving $\rho$ depends on the **signed** minus-frequencies $(e_1^-,e_2^-,e_3^-)$ AND on the
  chamber. (For "balanced" magnitude sets, e.g. $\{1,2,18\}$, the two branches happen to give $\pm$ the
  same value, which earlier looked deceptively global.)

This **explains the PI's negative result** (the per-region fit of $N_6$ in the invariants
$(e_1,e_2,e_3^-,e_3^+)$ fails — $N_6$ is *algebraic*, cubic-root, in the invariants): a per-chamber piece is
non-symmetric in the legs, so as a function of the symmetric invariants it is multi-valued. There is **no**
global-residue decomposition; the spline is irreducibly a truncated-power object in leg variables.

## Re-confirmations (exact, `verify_r5.py`)
- $A_6$ EVEN under $\omega\to-\omega$ (homog. deg 8) and INVARIANT under the $Z_2$ triple swap — both exact.
- $A_6$ rational (simple pole) — chamber form has a nonconstant denominator.
- $(1{=}2)$ jump ORDER **3** and $(1{=}1)$ ORDER **1** on clean single-wall crossings (`jump_extract.py`),
  re-confirming s1_013/s2_004 with an independent rational-reconstruction pipeline.
- Soft recursion on $N_n$ (s2_012): plus-leg limit $N_6/\omega_p^2\to 3g\,\omega_1\omega_2\omega_3\,N_5^{3-}$ holds
  (exact verification in `verify_r4.py`; re-checked numerically here).

## Structural reading for the team / recommendation
- Write $N_n$ in **leg variables** as the truncated-power spline above (NOT a box spline of $\omega^2$).
- The $(1{=}2)$ walls $\{\omega_i^2=\omega_j^2+\omega_k^2\}$ carry the **"two-minus-like" exponent $n-3$**
  (=3 at $n=6$): these are exactly the subset-sum walls of a two-minus B-spline, so $Q_{ijk}$ should be
  recognizable from the two-minus law on a sub-configuration.
- The $(1{=}1)$ walls $\{\omega_i=\omega_j\}$ carry the **anomalous exponent 1**: this is the genuinely-new
  three-minus feature. It lives on the **difference** branch $(\omega_i-\omega_j)$ of the BG kernel
  $|k_{ij}|=|\omega_i-\omega_j|\,|\omega_i+\omega_j|$, whose **sum** branch is the shielded pole $D_n^{\min}$.
  So the kink and the pole are the two roots of the same kernel magnitude.
- The **soft recursion** (s2_012) + the **universal jump exponents** (1,3) + symmetry/oddness/degree are the
  all-$n$ constraints on the leg-variable assembly. Determining $B$, $P_{ij}$, $Q_{ijk}$ explicitly
  (student-1's bottom-up extraction) is the remaining step.

## Literature (cited; no published closed form exists)
- Perturbiner / Berends-Giele formalism: Rosly-Selivanov; Mizera & Skrzypek, arXiv:1809.02096 (JHEP 2019).
- "Single-minus" sectors are nonzero & BG-recursive (direct conceptual cousins of one-/three-minus):
  Guevara-Lupsasca-Skinner-Strominger-Weil, gluon arXiv:2602.12176, graviton arXiv:2603.04330 (2026).
- Water-wave vertices / "vanishing on resonance": Dyachenko-Lvov-Zakharov, Physica D 87 (1995);
  Geogjaev, J. Fluid Mech. 1009 (2025).
- Box-spline / truncated-power theory: de Boor-Höllig-Riemenschneider (1993); De Concini-Procesi-Vergne (2010);
  De Concini-Procesi arXiv:1211.1187. (No connection to amplitudes in the literature — the spline structure is novel.)
