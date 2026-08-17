# Detailed chronological session log

Faithful reconstruction of the session: every user message, my narration sentence-by-sentence, each command, and each key output. `[U]` = user, `[A]` = my narration, `$` = bash command, `wl:` = Wolfram file written, `→` = key output.

---

## [U] Message 1
> `/effort max`
> "go to folder waterhedron_benchmark_blind/case_2 and finish the task there. Put the results in. Put the results in folder named "claude_opus_48_max" under waterhedron_benchmark_blind_case_2"

### [A] "I'll start by exploring the task folder to understand what needs to be done."
`$ find . -maxdepth 3 -type d -name "*waterhedron*"`
→ `./waterhedron_benchmark_blind` (plus .snapshot copies)

`$ cd waterhedron_benchmark_blind && ls -la && ls -la case_2/`
→ benchmark has `KEY.md, case_1, case_2, case_3`; `case_2/` has `OnShellBG.m`, `prompt.md`

**Read `prompt.md`** → Task: find a closed-form analytic formula for tree-level n-point on-shell amplitudes `A_n` for 1D deep-water surface waves in the **two-minus sector** σ=(−1,−1,+1,…,+1). Dispersion ω²=g|k|, k=σω²/g. On-shell: Σω=0, Σσω²=0. Hint: piecewise homogeneous polynomial in {ω}. Must report formula + chamber decomposition + numerical evidence (n=4,5,6,7, multiple chambers) + reasoning. **Constraints:** only `prompt.md` and `OnShellBG.m` readable; no web/literature; may extend/run BG code and write/read own files.

**Read `OnShellBG.m`** → Berends–Giele recursion (exact rational). Key internal note: the only `Abs` is `mag[k]=Abs[k]`, applied to **momenta** k=σω², never to ω.

### [A] "This is a research benchmark task. Let me understand it fully:"
- "**Goal**: Find a closed-form analytic formula for the tree-level n-point on-shell amplitude `A_n` … in the **two-minus sector**."
- "**Hint**: The answer is a *piecewise homogeneous polynomial* in the frequencies {ω_i}."
- "**Constraints**: I may only read `prompt.md` and `OnShellBG.m` (done), no web/literature."
### [A] "Let me set up the environment and output directory."
`$ mkdir -p claude_opus_48_max; which wolframscript math …; python3 --version`
→ `/opt/sns/bin64/wolframscript`; python `3.9.13` at anaconda3

### [A] "wolframscript is available. Let me verify it works with a quick test before running the full benchmark."
`$ wolframscript -code 'Print[2+2]; Print[Integrate[x^2,x]]'`
→ `4`, `x^3/3`

### [A] "wolframscript works. Now let me think about the structure before diving in."
### [A] "**Key observation**: … the momenta are k_i = σ_i ω_i², so |k_i| = ω_i² (unambiguous for external legs). But the BG recursion forms *internal* momenta k_S = Σ σ_i ω_i², and **|k_S| is where the piecewise/chamber structure comes from** — the sign of each internal momentum sum defines a kinematic chamber."
`wl: bg_defs.wl` (BG definitions copied verbatim from OnShellBG.m, sections I–V)

### [A] "Now let me probe the basic structure: compute A_n in the two-minus sector and determine the homogeneity degree."
`wl: probe1.wl`  →  `$ wolframscript -file probe1.wl`
→ n=4: **`A_4 = Indeterminate`** (allW={−5/3,4/3,5/3,−4/3}, a 0/0)
→ n=5: **`A_5 = (−16384*I)/81`**, `A_5(2w)/A_5(w) = 64` (=2⁶)
→ n=6: `A_6 = (−75759616*I)/72171`, ratio `256` (=2⁸)
→ conclusion: **degree = 2(n−2)**, A purely imaginary.

### [A] "The n=4 point hit a degeneracy. Let me understand why: `MakeKinematics` solves for legs {1,n}, and for n=4 this **forces ω_4 = −ω_2**, making the internal momentum k_{2,4} = 0 (a spurious singular locus, not the generic kinematics). The full on-shell variety is richer. Let me verify this analytically and build a flexible kinematics solver."
`wl: probe2.wl` (symbolic MakeKinematics check + flexible solver `MakeKinAB`)  →  run
→ `MakeKinematics n=4 allW = {−w3, w2, w3, −w2}` (so ω₄=−ω₂ always)
→ generic solve (legs 1,3) e.g. allW={−3,1,−1,3}, k24=8 — **still `Indeterminate`** (now k_{1,4}=0): n=4 is *always* on a degenerate locus.

### [A] "Now I understand n=4 fully. … Let me focus on getting clean data for n=5,6,7 (where `MakeKinematics` works) to find the formula."
`wl: probe3.wl` (data dump n=5,6,7)  →  run
→ n=5 ω=(−4,1,2,3,−2) `A₅=−64 i`; ω=(−13/2,2,3,5,−7/2) `−3328 i`; etc.
→ free {1,2,4} and {1,4,2} give the **same** A₅=−544 i/7 (first hint of plus-leg symmetry)
→ repeated-frequency points → Indeterminate.

---

## Discovering the piecewise structure

### [A] "All amplitudes are purely imaginary, homogeneous of degree **2(n−2)**." + observations that reordering middle freqs gives same value (symmetry) and different magnitudes give different values (chambers).
### [A] "The cleanest route is a **symbolic** computation within one fixed chamber. Let me try computing A_5 symbolically with ordering assumptions to resolve all the `Abs`."
`wl: probe4.wl` (symbolic A₅, assume 0<a<b<c)  →  run
→ printed ω₅=−(a+b)(a+c)/(a+b+c) etc., then **"No more memory available. Mathematica kernel has shut down."** (nested Abs of rationals explode)

### [A] "Symbolic blew up on memory … Better approach: **exact polynomial interpolation within a chamber**." (fit to symmetric functions of the plus legs)
`wl: lib.wl` (helpers: `kvec`, `chamberSig`, `plusESP`, `genPt`, `ampR`)
`wl: fit5.wl`  →  run
→ 27 points, **1 chamber** (sig {−1,1,…,1}); fit coeffs ugly; **max residual ≈ 3.6e10/1.6e9** — fit FAILED.

### [A] "The fit failed completely — so A_5/(−I) is **not** a polynomial in the plus-leg symmetric functions… Let me test the actual symmetry directly by permuting legs."
`wl: symtest.wl`  →  run
→ base ω=(−124/13,1,4,8,−45/13) `A=1984/13`; **all 6 plus-leg permutations and the 1↔2 swap give 1984/13** ⟹ Bose-symmetric. (a plus↔minus swap breaks momentum → garbage, as expected)

### [A] "A_5 is confirmed fully symmetric … So it *must* reduce to a polynomial in (P1,P2,P3) — yet my fit failed. Let me run careful diagnostics."
`wl: diag5.wl`  →  run
→ `A(3w)/A(w)=729` (=3⁶, degree 6 confirmed); discovered my "diverse" points clustered (all had P1+P2=−1); **LS residual ≈ 107** (numeric, unreliable).

### [A] "The issue: my sampled points are **clustered** (ω_2 ∈ {1,2,3} only)… Let me redo with diverse exact sampling and proper exact residual checks."
`wl: fit5b.wl`  →  run
→ 39 pts, 1 chamber, matrix rank 7 (full), rank-7 solve — **exact residual ≈ 5×10¹¹**. ⟹ A is provably **not** one symmetric polynomial → it is **piecewise**.

### [A] "Even with exact arithmetic … the residual is HUGE … Let me compute A_5 **exactly along a 1-parameter line** … and look at its actual analytic form."
`wl: probe6.wl` (symbolic 1-param line)  →  run
→ **"No more memory available"** again, but captured ω(t)=(−(133+13t)/(13+t), t, 4, 9, −(36+13t+t²)/(13+t)).

### [A] "Univariate symbolic also blows up… Let me reconstruct A_5(t) along a line by **exact rational interpolation**."
`wl: probe7.wl` (compute A at rational t, test if A·(13+t)^p is polynomial)  →  run
→ **`p=1: A₅(t)·(13+t) = 208 t⁶ + 2128 t⁵`** — a polynomial!
→ ⟹ `A₅(t) = 16 t⁵(13t+133)/(13+t) = −16 ω₁ ω₂⁵`.

### [A] "**Breakthrough.** … along the line w3=4, w4=9, I get **A_5(t) = −16 ω₁ ω₂⁵**." + cross-checks:
- "free{1,4,11}: ω₁=−49/4, ω₂=1 → −16(−49/4)(1)=196 ✓"
- "free{2,5,11}: ω₁=−233/18, ω₂=2 → −16(−233/18)(32)=59648/9 ✓"
- "free{3,7,13}: ω₁=−369/23, ω₂=3 → −16(−369/23)(243)=1434672/23 ✓"
### [A] "So the P-basis fit failed because the formula is **not symmetric within a single chamber** — the global amplitude is symmetric, but it's *piecewise*, and swapping ω₁↔ω₂ *crosses a chamber wall*. In chamber C₂ = {ω₂ is the unique smallest |frequency|}: **A_5 = −16 ω₁ ω₂⁵**."

### [A] "Let me now map out all chambers by scanning along a line across the walls."
`wl: probe8.wl` (scan ω₂=t over wide range, reconstruct A per chamber)  →  run
→ **4 chambers** on the line:
  - C1 (ω₂²<all): `A=16t⁵(133+13t)/(13+t)` = −16 ω₁ω₂⁵
  - C2 (ω₃²<ω₂²<ω₄²): `A=512 t(133+13t)(t²−8)/(13+t)` = −16 ω₁ω₂ω₃²(2ω₂²−ω₃²)
  - C4 (ω₂²>ω₃²+ω₄²): `A=41472 t(133+13t)/(13+t)` = −32 ω₁ω₂ω₃²ω₄²
→ **wall-crossing rule**: difference between adjacent chambers ∝ ω₁ω₂(ω₂²−q_S)² (vanishes on the wall ω₂²=q_S).

### [A] "**Major breakthrough on the structure.** Each chamber wall-crossing adds a clean correction." + listed C1/C2/C4 polynomials.
### [A] "Also from earlier data: chamber-1 gives A_n = −2ⁿ⁻¹ ω₁ω₂^(2n−5) (verified n=5,6,7). This gives a **general conjecture**:"
> `A_n = 2^(n-1) ω₁ω₂ Σ_{S⊆{3..n}, ω₂²>q_S} (−1)^(|S|+1) (ω₂²−q_S)^(n−3),  q_S=Σ_{i∈S}ω_i²`
### [A] "Let me verify this against BG across many points and chambers, and resolve which minus-leg is 'active'."
`wl: verify1.wl`  →  run
→ n=5 (13 MakeKinematics pts): **max |residual| using leg2 = 0, using min = 0**
→ n=5 leg-1-SMALL points (8): **resid leg1=0, leg2=0, min=0** — formula is robust to which leg's square is the threshold.

### [A] "The formula **works for n=5** — and remarkably, using ω₁², ω₂², or the min all give **exactly 0 residual** across 21 points… Now let me verify n=6, n=7."
`wl: verify2.wl`  →  run (background)
→ **n=6: 35 pts, 11 distinct chambers, mismatches = 0** (useLeg1/useLeg2/useMin all 0)
→ **n=7: 26 pts, 12 distinct chambers, mismatches = 0**
→ leg-1-small n=6: resid 0.

### [A] (while waiting) "For n=4, the kinematics is **forced onto chamber walls** … which is exactly why BG returns Indeterminate." Prepared `n4limit.wl` (approach the degenerate point off-shell, extrapolate d→0).
`wl: n4limit.wl`  →  run
→ (a,b)=(1,3): formula `24`, BG(d)→ 23.99…→ **24**
→ (2,5): formula `320`, BG→ **320**; (3,7): formula `1512`, BG→ **1512**. ✓

### [A] "**n=4 confirmed via the limit**… So the formula holds for n=4 too."

---

## g-dependence, implementations, final verification

### [A] (g-check) `$ wolframscript … vary g` → "A_n is **not** g-independent."
→ A(g=2)=A(g=1)/4; A(g=5)=A(g=1)/25 → **A ∝ g^(−2)** for n=5.
`$ wolframscript … g-power for n=5,6,7`
→ `A(g=1)/A(g=2) = 2^(n−3)` for n=5,6,7 ⟹ **Aₙ ∝ g^(−(n−3))** (g's cancel if written with |k_j|=ω_j²/g).

### [A] "Confirmed: **A_n ∝ g^(−(n−3))** … Let me fix the Python module."
`py: two_minus_amplitude.py` (closed-form impl; edited docstring + added g factor)  →  `$ python3 two_minus_amplitude.py`
→ **ALL PASS** (8 stored BG values, n=4–7).

`wl: formula.wl` (one-function Wolfram impl)  →  run
→ A₅(−4,1,2,3,−2)=`−64 i`; A₆=`−1024 i/5`; A₄(−3,1,3,−1)=`−24 i`. ✓

### [A] Created TaskList (3 tasks). Wrote comprehensive `final_verify.wl`.
- First runs: had bugs — wrong free-frequency count ("ERROR: need n-2 free frequencies"); then a `Do` paired-iterator syntax error; then n=7 too slow → timeouts.
- Fix: compute the chamber (`activeSet`, cheap, no BG) for many points, then call slow `BGAmplitude` on **one representative per distinct chamber**.
`$ wolframscript -file final_verify.wl` (final clean run)
→ **n=4**: 5 pts, exact symbolic `lim_{d→0} BG = formula` (−24 i, −320 i, −1512 i, incl. a>b) ✓
→ **n=5**: 4 chambers, active-set sizes {1,2,3,4} — all match exactly
→ **n=6**: 8 chambers, sizes {1..8} — all match exactly
→ **n=7**: 12 chambers, sizes {1,2,3,4,5,6,8,10,12,13,15,16} (up to 16-term polynomials) — all match exactly
→ stress: n=5 76 pts/5 chambers, n=6 38 pts/14 chambers, n=7 7 pts/7 chambers — **0 mismatches**; `DONE.`

### [A] (identity check) `$ wolframscript … Σ_S (−1)^|S|(x−q_S)^(n−3)`
→ `= 0` for |P|=2,3,4,5 (n=4–7) — explains the ω₁²/ω₂² interchangeability.

### [A] Verified the two RESULTS.md chamber-polynomial simplifications: `$ wolframscript …` → both differences `0`.

`md: RESULTS.md` — wrote the full report (formula, chamber decomposition, worked examples, n=4 special case, evidence table, reasoning, files).

### [A] Final summary delivered. **Answer:**
> `Aₙ = −i · 2^(n−1) · g^(−(n−3)) · ω₁ω₂ · Σ_{S⊆{3..n}} (−1)^(|S|+1) [(ω₂²−q_S)₊]^(n−3)`, q_S=Σ_{j∈S}ω_j².

(Tasks 1–3 marked complete. Folder cleaned: removed superseded `evidence_extra.*`.)

---

## [U] Message 2
> "move everything you just generated to case_2/codex_55_xhigh"

### [A] "I'll move the whole folder to `codex_55_xhigh` and fix the hardcoded paths."
`$ mv claude_opus_48_max codex_55_xhigh`
`$ sed -i 's/claude_opus_48_max/codex_55_xhigh/g' *.wl`  (16 files)
`$ python3 two_minus_amplitude.py` → ALL PASS; `wolframscript … Get[lib.wl]` → `formula−BG = 0` (n=6 chamber). Old folder gone.

## [U] Message 3
> "sorry. change the name to claude_opus_48_max"

### [A] "I'll rename it back to `claude_opus_48_max` and restore the internal paths."
`$ mv codex_55_xhigh claude_opus_48_max`
`$ sed -i 's/codex_55_xhigh/claude_opus_48_max/g' *.wl`
→ no stale refs; Python ALL PASS; `lib.wl` loads (`sig[5]={−1,−1,1,1,1}`).

## [U] Message 4
> "get the chronological log: each message, each command, each key output"

### [A] Wrote condensed `SESSION_LOG.md` and presented it.

## [U] Message 5
> "put that in a markdown file" → confirmed `SESSION_LOG.md`.

## [U] Message 6
> "No. I want detailed version. sentence by sentence" → **this file**.
