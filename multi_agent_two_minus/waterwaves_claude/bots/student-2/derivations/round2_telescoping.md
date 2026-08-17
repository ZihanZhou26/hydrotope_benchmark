# Round 2 (student-2): g-dependence + divided-difference (B-spline) structure

**Status of the question:** already SOLVED & accepted (post_004, `summary/SOLVED.md`).
This note addresses the two items the PI flagged as **open / not required**:

> *(i) a first-principles proof that the BG recursion telescopes to the B-spline
> form, and (ii) an explicit g-dependence check (verification was at g = 1).*

It does **not** revisit settled work. The accepted all-chamber form (student-1,
verified by the PI) is, at g = 1,

> `A_n = i · a_n`, `a_n = 2^{n-1} · ω₁ ω₂ · D_n`,
> `D_n = Σ_{S ⊆ {3..n}} (−1)^{|S|} · max(0, P − Σ_{j∈S} ω_j²)^{n-3}`, `P = min(ω₁²,ω₂²)`,

legs 1,2 the σ=−1 (minus) legs, legs 3..n the σ=+1 (plus) legs.

Throughout write `t_j ≡ ω_j²` (= |k_j| at g=1), `m ≡ n−3` (the exponent), and
`k ≡ n−2` (the number of plus legs). **Key observation: k = m+1** — we apply m+1
finite-difference operators to a truncated power of degree m. That object is, by
definition, a (univariate) **B-spline / divided difference**.

---

## Part A — g-dependence (PROVEN by homogeneity + verified bit-exact)

### A.1 Where g enters `bg.cpp`
Only two places:
1. On-shell kinematics: `K[i] = σ_i ω_i² / g` (dispersion ω² = g|k|). The two
   on-shell constraints `Σω=0`, `Σσω²=0` and the solved `ω₁, ω_n` are **g-independent**
   (the solver in `runMode` uses only the free ω's and signs). So **the ω's do not
   move when g changes**; only the momenta `K_i ∝ 1/g` do.
2. `Propagator`: `D = ω_S²/|k_S| − G`, returns `−i/D`. With `k_S = κ_S/g`
   (`κ_S ≡ Σ_{i∈S} σ_i ω_i²`, g-independent), `D = g·(ω_S²/|κ_S| − 1)` ⇒ each
   propagator scales as **1/g**.

### A.2 Homogeneity counting (the clean argument)
Consider the scaling `K → μK, G → G/μ` at fixed `W` (this is exactly what
`g → g/μ` does on-shell, since `K ∝ 1/g`, `G = g`). Under it:
- `Propagator`: `D = ω_S²/|k_S| − G → (1/μ)(ω_S²/|k_S| − G) = D/μ` ⇒ **degree +1**.
- `EKernel(n,·)` is homogeneous of degree **n−1** in its momenta (induction on the
  recursion: `E₃ ∝ |p||p'|+pp'` is degree 2; the `|p₂|^{n-3}·E₃` and `|p₂|^m·E_{n−m}`
  terms are each degree n−1). So `E_n → μ^{n-1}E_n`.
- `FKernel(n,·)` is homogeneous of degree **n−3** (similarly; `F₃` is degree 0).
- `Vertex(p)` = `(−i/2)Σ ω_a ω_b F_p(moms)` ⇒ degree **p−3** (the ω's are fixed).

Let `D(s)` be the scaling degree of `BGCurrent(S)`, `|S|=s`. `D(1)=0`; for `s≥2`
each term is `Vertex(m+1)[deg m−2] · ∏ BGCurrent(block)[Σ D(s_i)] · Propagator[+1]`.
Writing `D(s)=cs+e` and demanding m-independence forces `e=−1`, then `D(1)=c−1=0`
⇒ **`D(s) = s − 1`**.

`BGAmplitude(N)` sums `Vertex(m+1)[m−2] · ∏ BGCurrent(block)` over partitions of the
N−1 legs `{2..N}` (no overall propagator):
`deg = (m−2) + Σ_i (s_i − 1) = (m−2) + (N−1) − m = **N − 3**`.

Hence under `K→μK, G→G/μ`, `A_N → μ^{N−3} A_N`. With `μ = 1/g` (on-shell):

> **A_n(g) = g^{−(n−3)} · A_n(1) = g^{3−n} · A_n(1).**

### A.3 Two independent cross-checks of the exponent
- **Pure-ω scaling** `ω→ρω` (W→ρW, K→ρ²K, G fixed): same counting gives degree
  `2n−4`, **at any g** (not just g=1) — recovers the PI's scaling dimension and shows
  it is g-independent.
- **Combined** `ω→ρω, g→ρ²g` (so K fixed, W→ρW, G→ρ²G): every current is invariant
  and `A_n → ρ² A_n`. Consistency: `ρ^{2n−4}·(ρ²)^{3−n} = ρ²`. ✓

### A.4 g-restored closed form (verified BIT-EXACT)
> **A_n = i · g^{3−n} · 2^{n-1} · ω₁ ω₂ · Σ_{S⊆{3..n}} (−1)^{|S|} max(0, P − Σ_{j∈S} ω_j²)^{n−3}**

`code/round2_gcheck.py` vs our own `./bg` (exact rational), residual **≡ 0**:
- n=5,6,7 × g∈{1,2,3} × {principal, non-principal, extreme} — **21/21 exact**;
- n=8 × g∈{1,2} principal — exact (a₈: −33920/21 → −1060/21 = ÷2⁵);
- n=4 by δ→0 limit (exact-rational Neville) at g=1 **and** g=2: −24→−12, −320→−160,
  −1512→−756, −40→−20 (the g⁻¹ scaling), all exact.

Data: `data/round2_gcheck_output.txt`.

---

## Part B — divided-difference / B-spline structure (PROVEN, upgrades round-1 claims)

These were *verified numerically* in round 1; here they are **proved** as identities
(`code/round2_structure.py`, all symbolic/exact). Define the operator
`(T_t f)(P) = f(P − t)`.

**B.1 Operator form.** `D_n = [∏_{j=3}^{n}(1 − T_{t_j})] (P)_+^{m} |_{x=P}`, i.e. the
alternating subset sum **is** the (m+1)-fold finite difference of the truncated power
`(x)_+^{m}` at nodes `{t_3,…,t_n}`. *(Proven: operator-expansion == subset sum,
n=4..7.)*

**B.2 Principal-chamber collapse ⇒ student-2 round-1 result is a theorem.** If
`P ≤ t_j` for every plus leg j, then every `S≠∅` has `Σ_{j∈S} t_j ≥ P` so its term
truncates to 0; only `S=∅` survives and `D_n = P^{m} = ω₂^{2n−6}`. Hence
`a_n = 2^{n-1} ω₁ ω₂ · ω₂^{2n−6} = 2^{n-1} ω₁ ω₂^{2n−5}` — the round-1 principal-chamber
monomial, now derived from the all-chamber form (not just pattern-matched).

**B.3 Degree / homogeneity.** Each term is degree `2m` in ω (P, t_j are degree 2),
times `ω₁ω₂` (degree 2) ⇒ **2m+2 = 2n−4**. ✓

**B.4 Order-exceeds-degree vanishing.** Applying `m+1` difference operators to ANY
degree-`m` polynomial gives 0 *(proven symbolically)*. Consequence: in the
**full-overlap** region `P ≥ Σ_j t_j` (no truncation anywhere), `D_n` is `∏(1−T)`
applied to the plain polynomial `P^{m}` ⇒ **`D_n = 0`**. So the formula predicts the
amplitude *vanishes* once `P ≥ Σ_{plus} ω_j²`.
*On-shell this boundary is never reached:* the constraint `Σσω²=0` gives
`ω₁²+ω₂² = Σ_{j≥3} ω_j²`, so `P = min(ω₁²,ω₂²) ≤ (ω₁²+ω₂²)/2 < Σ_{plus} ω_j²` strictly
(unless a minus leg is 0). The vanishing region is a property of the analytic
continuation, just outside the physical locus — a clean self-consistency check.

**B.5 Continuity (kink, not pole).** `(x)_+^{m}` is `C^{m-1}`, so `D_n ∈ C^{m-1}=C^{n-4}`
across every chamber wall `P = Σ_{j∈S} t_j`. *(Verified: value and first derivative
match across a wall.)* This is exactly the round-1 observation that the propagator
`→0` at sign changes of `k_S` makes a **kink, not a pole**.

**B.6 Symmetry S₂ × S_{n−2} is MANIFEST.** `D_n` is symmetric in the plus nodes
`t_3..t_n` (⇒ `S_{n-2}` on plus legs, proven). The prefactor `ω₁ω₂` and
`P = min(ω₁²,ω₂²)` are symmetric under `1↔2` (⇒ `S₂` on minus legs, by inspection).
Round 1 had this only as an oracle observation.

**B.7 "Only the smaller minus enters."** Immediate from the form: the *larger* minus
appears solely through the prefactor `ω₁ω₂`; the value through `D_n` depends only on
`P = min(ω₁²,ω₂²)` — explaining the round-1 surprise structurally.

---

## Part C — telescoping from the BG recursion: what is and isn't settled

- **Settled here (the "what it telescopes TO"):** the accepted form is, exactly, a
  B-spline / (m+1)-fold divided difference of a truncated power (B.1), and *every*
  round-1 numerically-observed property (degree, principal collapse, continuity,
  S₂×S_{n−2} symmetry, only-P-enters, full-overlap vanishing) follows from that
  characterization as a theorem.
- **Structural origin in the kernels:** `EKernel(n,·)` carries an explicit
  `|p₂|^{n-3}` factor and `E₃ ∝ |p₁||p₂|+p₁p₂`, which seeds the degree-`m` truncated
  power and the `ω₂^{2n-6}` of the principal chamber; the `abs(k_S)` in
  `Propagator`/kernels are precisely what create the chamber walls
  `P = Σ_{j∈S} t_j` where the truncations `max(0,·)` switch on/off.
- **Still open (honestly):** a complete *term-by-term* proof that the partition sum
  in `BGAmplitude`/`BGCurrent` collapses to the alternating subset sum `D_n` for a
  general chamber. Part B reduces this to a single clean target (the B-spline), and
  Part A fixes the g-dependence, but the full combinatorial telescoping of the
  partition sum is not proven here. This remains the one genuinely open piece.

---

## Reproduce
- `code/round2_gcheck.py`  → `data/round2_gcheck_output.txt` (g-restored formula vs ./bg, exact)
- `code/round2_structure.py` → `data/round2_structure_output.txt` (B-spline theorems, symbolic)
- `figures/round2_structure.png` (g-scaling law + B-spline piecewise profile)
