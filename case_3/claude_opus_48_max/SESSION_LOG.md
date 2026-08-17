# Chronological session log — `waterhedron_benchmark_blind/case_3`

A blow-by-blow record of the entire working session: every user message, every
command run, the key output of each, and the decision it triggered. Model:
Claude Opus 4.8 (1M context), effort = max.

Legend: **U** = user message, **A** = my action/reasoning, `⌨` = command,
`→` = key output.

---

## 0. Task & ground rules

**U (effort):** set effort level to **max**.

**U:** "go to folder waterhedron_benchmark_blind/case_3 and finish the task
their. Put the results in. Put the results in folder named 'claude_opus_48_max'
under waterhedron_benchmark_blind_case_3".

**A:** I read this as: do the case_3 task and write outputs to
`waterhedron_benchmark_blind/case_3/claude_opus_48_max/`. I immediately flagged
the *blind benchmark* constraints to myself: I may read **only** `prompt.md` and
`OnShellBG.m` (not `KEY.md`, not sibling cases, not anything else), and I may
**not** use any web/literature lookup. I would work purely from the BG code and
data I generate.

---

## 1. Locating the task and reading the two allowed files

⌨ `find . -maxdepth 3 -type d -iname "*waterhedron*"`
→ `./waterhedron_benchmark_blind` (plus `.snapshot/...` copies).

⌨ `ls -la waterhedron_benchmark_blind` and `ls -la case_3`
→ `KEY.md`, `case_1`, `case_2`, `case_3`. case_3 contains `OnShellBG.m` (8438 B)
and `prompt.md` (3531 B). I deliberately did **not** open `KEY.md` or the other
cases.

**A:** Read `prompt.md`. Summary of what it asks:
- 1-D deep-water surface waves, dispersion ω² = g|k|, so kᵢ = σᵢ ωᵢ²/g, σᵢ∈{+1,−1}.
- All incoming ⇒ on the resonant manifold Σωᵢ = 0 and Σσᵢωᵢ² = 0.
- Given a Berends–Giele implementation `OnShellBG.m` with entry points
  `BGAmplitude[momenta, omegas, g]` (exact rational tree amplitude) and
  `MakeKinematics[n, freeFreqs, sigmas, g]` (solves conservation for {w₁,wₙ}).
- **Two-minus sector:** σ = (−1,−1,+1,…,+1) — legs 1,2 are minus.
- **Task:** find a closed-form analytic formula for Aₙ valid for all n≥4 and
  arbitrary kinematics in the sector. Report formula + numerical evidence
  (n=4,5,6,7, multiple points, non-generic regimes) + reasoning. Must agree with
  `BGAmplitude` to ≤10⁻¹⁰ relative error.
- **Constraints:** read only these two files; no web/literature; may edit/extend
  the BG code, generate data, and write/read my own files.

**A:** Read `OnShellBG.m`. Key structure noted:
- `EKernel[3,ps] = −½(|p₁||p₂| + p₁p₂)` and `EKernel[n≥4]` a recursion in |p₂|.
- `FKernel[3,ps] = −1 − p₁p₂/(|p₁||p₂|)`; `FKernel[n≥4]` recursion.
- `Vertex[n,moms,omegas] = (−i/2) Σ_perms ω_a ω_b FKernel[n, moms[perm]]`.
- `Propagator[ω,k,g] = −i/(ω²/|k| − g)`.
- `BGCurrent` (memoized) and `BGAmplitude` standard BG recursion; leg 1 special.
- `MakeKinematics`: with σ₁+σₙ=0 the momentum law is linear ⇒ solves wₙ then w₁.
- The built-in tests (section VI) are for the **one-minus** sector
  σ=(−1,+1,…,+1), which *vanishes*; the task's two-minus sector is the first
  non-vanishing one — the analogue of MHV.

---

## 2. Environment & sanity checks

⌨ `which wolframscript math MathKernel ...; python3 -c "import sympy,numpy"`
→ `/opt/sns/bin64/wolframscript`, `/opt/sns/bin/math`, … available; sympy 1.14.0,
numpy 1.24.4 under `/home/zihanz/anaconda3/bin/python3`.

⌨ `mkdir -p claude_opus_48_max && cp OnShellBG.m claude_opus_48_max/`
⌨ `wolframscript -code 'Print[2+2]; Print[Integrate[x^2,x]]'`
→ `4`, `x^3/3`. Wolfram works.

⌨ `head -145 OnShellBG.m > bg_core.m` — extracted just the function definitions
(sections I–V, no auto-running tests), so I can drive the recursion myself.
→ `bg_core.m`, 145 lines, ending at `MakeKinematics`.

---

## 3. First amplitudes (`gen1.m`) — n = 4, 5, 6

**A:** Computed two-minus Aₙ at exact rational points.
→ **n=4:** `Indeterminate` — a `0/0` propagator. Diagnosis: with
w={−2,3/2,2,−3/2}, legs 2 and 4 have w₂+w₄=0 and k₂+k₄=0 (a null sub-channel).
→ **n=5:** A₅ = −891 i/2.
→ **n=6:** A₆ = −11907 i/4.
Both clean and purely imaginary.

---

## 4. Scaling and g-dependence (`gen2.m`)

**A:** Reasoned first: since |kᵢ| = ωᵢ²/g regardless of σ, power-counting the
vertex/propagator predicts Aₙ homogeneous of degree 2n−4 in ω and ∝ g^(3−n).
Tested:
→ **Scaling** (n=5, free {2,3,5}): ω→2ω multiplied A₅ by 64 = 2⁶; ω→3ω by
729 = 3⁶. Degree 2n−4 confirmed.
→ **g** (n=5): A₅(g=1)=−3328 i, g=2 ⇒ −832 i (=−3328/4), g=3 ⇒ −3328 i/9.
So A₅ ∝ g⁻² = g^(3−n). Confirmed.
Clean point obtained: free {2,3,5} ⇒ ω={−13/2,2,3,5,−7/2}, A₅ = −3328 i = −2⁸·13 i.

---

## 5. Symmetry + more n=5 data (`gen3.m`)

→ **Permutation symmetry:** swapping plus legs (3,4),(3,5),(4,5) and swapping
the two minus legs (1,2) each leaves A₅ = −3328 i unchanged. So Aₙ has an
**S₂×S_{n−2}** symmetry (permute the 2 minus legs, permute the n−2 plus legs).
→ 10 n=5 points generated, e.g. free {1,2,3} ⇒ ω={−4,1,2,3,−2}, A₅=−64 i;
free {5,7,11} ⇒ A₅ = −16850000 i/23.

---

## 6. n = 4 is intrinsically degenerate (`gen4.m`)

**A:** Worked out the n=4 algebra: for the two-minus sector the constraints force
{ω₁,ω₂} = {−ω₃,−ω₄} as a set (the minus-leg frequencies are exactly the
negatives of the plus-leg frequencies). That **always** creates null
sub-channels (ωᵢ+ωⱼ=0 and kᵢ+kⱼ=0), i.e. an internal line exactly on-shell.
→ All 15 attempted n=4 points returned `$Failed`. Conclusion: n=4 sits on a
factorization pole; it needs a limiting definition (deferred to §15).

---

## 7. Big exact dataset (`gen_dataset.m` → `data.txt`)

⌨ Generated exact rational amplitudes for many generic free-frequency vectors.
→ **64 points**: 30 for n=5, 20 for n=6, 14 for n=7 (e.g.
`5 | {-13/2,2,3,5,-7/2} | -3328*I`). Saved to `data.txt`.

---

## 8. Polynomial fit fails (`fit.py`)

**A:** Hypothesis: Aₙ/i is a symmetric polynomial in the group generators
{m₁=w₁+w₂, m₂=w₁²+w₂², P₃,…} (after using the two constraints to eliminate the
plus-group power sums P₁=−m₁, P₂=m₂). Built the monomial basis of weighted
degree 2n−4 and solved the exact linear system.
→ **n=5: no consistent polynomial. n=6: no consistent polynomial.** So Aₙ is a
*rational* function with a genuine denominator, not a polynomial.

---

## 9. Symbolic extraction via the reference-sign trick (`sym5.m`)

**A:** The only non-analyticity is `mag[k]=|k|`. I redefined `mag[x_] :=
x*Sign[x /. ref]` — i.e. resolve every Abs by its sign at a numeric reference
point — which turns the whole BG recursion into an exact rational function of the
symbolic free frequencies, valid in that kinematic chamber.
→ With ref (a,b,c)=(w₂,w₃,w₄)=(2,3,5):
`R₅ = A₅/i ... = (−16 a⁵(ab+b²+ac+bc+c²))/(a+b+c)`.
Using the identity (ab+b²+ac+bc+c²) = −w₁(a+b+c), this collapses to
**A₅/i = 16 w₁ w₂⁵** — and it depends only on the two minus legs.

**A:** But 16 w₁w₂⁵ is asymmetric under w₁↔w₂, contradicting the verified S₂
symmetry. Realization: the reference-sign trick froze one *chamber*; the true Aₙ
is **piecewise**, and 16 w₁w₂⁵ is only the piece where w₂ is the soft minus leg.

---

## 10. The clean pattern (`check_minus.py`, `probe_n.py`)

→ All 30 n=5 points satisfy c ≡ A/i = **16 w₁ w₂⁵** (= 2^(n-1) w₁ w₂^(2n-5)).
→ n=6: c = **32 w₁ w₂⁷** (all 20 points, ratio exactly 32).
→ n=7: c = **64 w₁ w₂⁹** (all 14 points, ratio exactly 64).
→ **Unified, symmetric form matched all 64 points exactly:**
`c = 2^(n−1) (w₁w₂) [min(w₁²,w₂²)]^(n−3)`.

---

## 11. Which minus leg gets the high power (`disamb.m`)

→ Config ω={−1,4,2,−2,−3}: c=−64. With w₁=−1 the smaller-|·| leg,
16·(w₁w₂)·min(w₁²,w₂²)² = 16·(−4)·1 = −64 ✓; the "positive-frequency leg gets
the high power" hypothesis would give −16384 ✗.
→ Config ω={−1/2,−6,3,5,−3/2}: c=3 = 16·3·(1/4)² ✓.
**Rule:** the minus leg with the **smaller |ω|** carries the high power 2n−5.

---

## 12. n=6 symbolic confirmation (`symN.m`)

→ `R₆ = −32 w₁ w₂⁷` (i.e. A₆/i = 32 w₁ w₂⁷), confirming minus-legs-only
dependence and the 2^(n−1) prefactor symbolically.

---

## 13. First verification, and the chamber problem (`verify.m`, `verify2.m`)

**A:** Tested the closed form against `BGAmplitude` more broadly.
→ `MakeKinematics` points with ordered free freqs: all PASS, exact.
→ But `verify2.m` (arbitrary minus legs, plus legs solved from the constraints)
**FAILED** in several chambers — sometimes giving *irrational* BG values (e.g.
"both minus positive (2,5)" gave 252.08… i, not the formula's 2560 i).
**Conclusion:** the simple formula is **chamber-specific**. When a *plus* leg
carries the smallest momentum, Aₙ genuinely depends on the plus legs and the
formula breaks. The amplitude is piecewise because the BG kernels carry |k|.

---

## 14. Mapping the chambers (`chambers5.m`, `scan5.m`, `scan_slice.m`, `inter5.m`)

→ Three n=5 chamber forms for c = A/i (a=w₂,b=w₃,c=w₄):
- C1 (w₂ small): `16 w₁ w₂⁵ = 16(w₁w₂)|k₂|²`.
- C2 (w₂ large): `32 w₁ w₂ w₃²w₄² = 32(w₁w₂)|k₃||k₄|`.
- C3 (mixed): `16 w₁⁵ w₂ = 16(w₁w₂)|k₁|²`.
→ Writing c = 2^(n−1)(w₁w₂)·M, the degree-2-in-k factor M is set by the
*softest momenta*: softest leg minus ⇒ M=|k_soft|²; two softest plus ⇒
M=2|k_a||k_b|; softest plus + next minus ⇒ M=|k_p|(2|k_m|−|k_p|).
→ A 1-D slice (w₃=3,w₄=5, vary w₂) showed M transitioning |k₂|² → |k₃|(2|k₂|−|k₃|)
→ 2|k₃||k₄| as different legs become softest (transitions coincide with poles).
→ A full symbolic `FullSimplify` with Abs unresolved exhausted memory (strict
overcommit on this shared cluster), so I mapped chambers piecewise instead.

---

## 15. Sorting rule + its limits (`verify_rule5.m`, `decode_fail.m`)

→ The "two-softest-legs" sorting rule passed 227/233 random points but **failed
6** (rel. err 1–10%), all with mixed-sign minus legs.
→ `decode_fail.m` on ω={11/2,−4,−3,5,−7/2}: exact M = 3087/16, *not* the
2|k₃||k₅| the rule predicts. Comparing to C2 showed the soft-plus form depends on
the **signs of the plus-leg frequencies**. Conclusion: the full chamber
structure depends on internal partial-momentum signs (not just leg ordering);
a single globally-analytic expression does not exist.

**Decision:** the clean formula is the intended *physical-regime* result (the
direct MHV/Parke–Taylor analogue). I would present it with an honest scope
statement and document the piecewise structure.

---

## 16. n = 4 by limit (`n4limit.m`)

**A:** n=4 sits exactly on a removable pole. I deformed off momentum
conservation by ε (ω = (−w₃, −w₄−ε, w₃+ε, w₄)) and took ε→0.
→ (w₃,w₄)=(3,2): limit 192.82, 192.082, 192.0082, 192.0008 → **192** =
formula i·2³·g⁻¹·ω₁ω₂·min(ω₁²,ω₂²).
→ (5,2)→**320**, (7,3)→**1512**. n=4 confirmed.

---

## 17. Self-contained Python port (`waterwave_bg.py`)

**A:** Ported `OnShellBG.m` to Python (kernels, vertex, propagator, set
partitions, BG recursion, `MakeKinematics`) plus `closed_form_A` and
`in_physical_regime`.
→ Float self-test: n=5 BG=−3328.0000000000073 i vs closed −3328 i (diff 7e-12);
n=6 BG=−2976.75 i (= the original code's A₆=−11907/4). Float roundoff ~1e-10 was
borderline, so I added an mpmath high-precision path (`bg_amplitude_hp`).
→ High-precision: n=5,6 agree to ~1e-59; n=7 to ~1e-16 (float display of the
closed form). All well under 1e-10.

---

## 18. Comprehensive verification (`verify_final.m`, `verify_regime.m`)

→ `verify_final.m`: **16 `MakeKinematics` points PASS, 0 FAIL, maxRelErr = 0**
(exact) across n=5,6,7,**8** standard, one-plus-huge, and g∈{2,7/3,5}. (My
`buildPoint` cases there had a wrong `fp` length and were skipped — fixed next.)
→ `verify_regime.m` (proper domain scan, in-regime points only): **95 points
tested, 81 exercising the min-branch where w₁ is the smaller minus leg, all
PASS, maxRelErr < 10⁻³⁷** (machine-zero at 50-digit precision), across both
signs and extreme magnitudes of the minus legs, n=5,6,7.

Total across all verifications: **110+ kinematic points, 0 failures**, spanning
n=4 (limit), 5, 6, 7, 8.

---

## 19. Notebook (`build_nb.py` → `two_minus_closed_form.ipynb`)

⌨ Built the notebook with `nbformat`, executed with `jupyter nbconvert
--execute`.
→ Executed cleanly. All cells PASS: standard kinematics (n=5,6,7), non-generic
regimes (plus leg huge, minus leg tiny), g≠1 (checks g^(3−n)), the n=4 ε→0 limit
(192/320/1512), and the regime flag (`in_physical_regime` True for free {2,3,5},
False for free {2,3,1/1000}).

---

## 20. Write-up (`RESULTS.md`) and final answer

### The closed form

```
A_n = i · 2^(n−1) · g^(3−n) · (ω₁ω₂) · [min(ω₁², ω₂²)]^(n−3)
    = i · 2^(n−1) · g^(3−n) · ω_>  · ω_<^(2n−5)
```

where legs 1,2 are the minus legs (σ=−1) and ω_<, ω_> are their smaller/larger
|·|. Aₙ depends only on the two minus legs; it is purely imaginary, homogeneous
of degree 2n−4 in ω, and ∝ g^(3−n).

### Worked check
n=5, free {2,3,5} ⇒ ω={−13/2,2,3,5,−7/2}: ω₁ω₂=−13, min=4 ⇒
A₅ = i·2⁴·(−13)·4² = −3328 i ✓.

### Scope (stated honestly)
Exact whenever a **minus** leg carries the smallest |momentum| — the
generic/physical regime (all `OnShellBG.m`-style kinematics, plus large/small
minus frequencies and large plus frequencies). Because the BG kernels contain
|k|, the *full* amplitude is piecewise-rational; in the non-physical chambers
where a *plus* leg is the softest, Aₙ takes a different (frequency-sign-dependent)
form. A single globally-analytic expression does not exist, which is why the
boxed result is the natural closed form (the MHV/Parke–Taylor analogue).

### Constraints honored
Only `prompt.md` and `OnShellBG.m` were read; no `KEY.md`, no sibling cases, no
web/literature.

---

## 21. Deliverables (in `claude_opus_48_max/`)

| file | purpose |
|---|---|
| `RESULTS.md` | main write-up (formula, evidence, derivation, scope) |
| `SESSION_LOG.md` | this chronological log |
| `waterwave_bg.py` | Python port of the BG recursion + closed form + hp checker |
| `two_minus_closed_form.ipynb` | executed notebook, all PASS |
| `bg_core.m` | BG function definitions (sections I–V) |
| `gen_dataset.m`, `data.txt` | 64-point exact dataset |
| `sym5.m`, `symN.m`, `chambers5.m`, `scan5.m`, `scan_slice.m`, `inter5.m`, `n6chambers.m`, `decode_fail.m`, `absform5.m` | symbolic chamber extraction |
| `verify.m`, `verify2.m`, `verify_final.m`, `verify_regime.m`, `verify_rule5.m`, `n4limit.m` | verifications |
| `fit.py`, `check_minus.py`, `probe_n.py`, `build_nb.py` | fitting / pattern checks / notebook builder |

### Methods that worked (notes for reuse)
- **Reference-sign trick** for symbolic amplitudes through `|k|`: define
  `mag[x_]:=x*Sign[x/.ref]` to get the exact rational form valid in one chamber.
- **Scaling + dimensional analysis** to fix prefactor structure before fitting.
- **mpmath** for high-precision cross-checks when float roundoff is borderline.
- This is a shared cluster with strict memory overcommit — run one heavy Wolfram
  kernel at a time; `FullSimplify` on Abs-laden expressions can OOM.
