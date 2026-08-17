# Closed-form A_n in the two-minus sector (1D deep-water surface waves)

**Sector:** σ = (−1, −1, +1, …, +1) — legs 1 and 2 carry σ = −1 (the *minus*
legs); legs 3…n carry σ = +1.  Dispersion ω_i² = g|k_i|, all momenta/frequencies
incoming, with Σωᵢ = 0 and Σσᵢωᵢ² = 0.

---

## 1. The formula

$$\boxed{\,A_n \;=\; 2^{\,n-1}\; i \;\, \omega_1\,\omega_2^{\,2n-5}\,\big/\,g^{\,n-3}\,}$$

equivalently, since |k₂| = ω₂²/g,

$$A_n \;=\; 2^{\,n-1}\, i\,\, \omega_1\,\omega_2\,|k_2|^{\,n-3}
        \;=\; 2^{\,n-1}\, i\,\, \omega_1\,\omega_2\,\Big(\tfrac{\omega_2^2}{g}\Big)^{n-3}.$$

Here **ω₁ and ω₂ are the two σ = −1 legs**.  Remarkably, the amplitude depends
**only on the two minus-leg frequencies** — the plus-leg frequencies
ω₃,…,ωₙ drop out entirely.

Explicit low-n cases (g general):

| n | A_n |
|---|-----|
| 4 | 8  i ω₁ ω₂³ / g     |
| 5 | 16 i ω₁ ω₂⁵ / g²    |
| 6 | 32 i ω₁ ω₂⁷ / g³    |
| 7 | 64 i ω₁ ω₂⁹ / g⁴    |
| 8 | 128 i ω₁ ω₂¹¹ / g⁵  |

### Domain of validity (important)

The two-minus amplitude is **piecewise-rational** in the kinematics (the
dispersion relation ω² = g|k| injects |k_S| = |Σ_{i∈S} σ_i ω_i²| into every
propagator and kernel, so the closed form is a *different* rational function in
each chamber of the hyperplane arrangement {k_S = 0} — the "waterhedron").

The boxed monomial is the value in the **principal chamber**, characterised
*exactly* (verified on 79 random points, see §3) by

$$|\omega_2| \;=\; \min_i |\omega_i| \qquad\text{(the free minus leg has the smallest magnitude).}$$

This chamber contains **every sorted, positive-frequency configuration** — in
particular all test kinematics used in `OnShellBG.m` ({3/2, 2, 5/2, …},
{1, 2, 3, 4, 5, 6}, {1, 3, 5, 7}, {2, 3, 7, 11}, …) and all "non-generic"
magnitude hierarchies in which the free minus leg ω₂ stays the smallest (one
plus leg ≫ or ≪ the others; ω₂ → 0; etc.).  Because the full amplitude is
Bose-symmetric, when both minus legs qualify one simply relabels so that ω₂ is
the smaller-magnitude minus leg.

Outside the principal chamber the amplitude is a different (still
closed-form, but chamber-dependent) rational function — see §4.

---

## 2. g-dependence and homogeneity

* Homogeneity in ω (fixed g):  A_n(λω) = λ^{2n−4} A_n(ω)  — verified
  (n=5 → 2⁶, n=6 → 2⁸).
* g-scaling:  A_n ∝ g^{−(n−3)} — verified symbolically
  (A₅ = 16 i ω₁ω₂⁵/g², A₆ = 32 i ω₁ω₂⁷/g³, exact, with `g` kept symbolic).

---

## 3. Numerical evidence (≤ 10⁻¹⁰ relative error — in fact **exact**)

All checks use **exact rational arithmetic**, so the relative error is identically
0, not merely < 10⁻¹⁰.  Two **independent** amplitude codes agree with the formula:

* (a) the supplied Mathematica `BGAmplitude` (`OnShellBG.m`, sections I–V), and
* (b) a from-scratch Python reimplementation of the Berends–Giele recursion in
  exact `Fraction` arithmetic (`waterwave_bg.py`) — which reproduces the
  Mathematica values (−891/2, −4224, −11907/4, −7302393/400, …) bit-for-bit.

### n = 4 (degenerate — verified as a limit)

The two-minus on-shell conditions *force* a zero pair at n=4 (ω₄=−ω₂, ω₃=−ω₁ ⇒
the {2,4} channel has ω=0 **and** k=0), so `BGAmplitude` returns
`Indeterminate` at the exact point.  The amplitude is finite as a limit
(ω²/|k| → 0 ⇒ that propagator → i/g).  Detuning ω₄ = −ω₂ + t and letting t→0:

```
predicted A_4 = -54 i        (= 8 i ω₁ ω₂³, ω₁=-2, ω₂=3/2)
 t=1e-2  →  -53.6098…  i
 t=1e-3  →  -53.9612…  i
 t=1e-6  →  -53.99996… i
 t=1e-9  →  -53.999999961… i
symbolic lim_{t→0} A_4 = -8 i a³ b  = 8 i ω₁ ω₂³   (difference EXACTLY 0)
```

### n = 5, 6, 7, 8 (exact, principal chamber)

| n | free frequencies | A_n  (BG = formula) | rel. err |
|---|------------------|---------------------|----------|
| 5 | {3/2, 2, 5/2}            | −891/2 · i                       | 0 |
| 5 | {2, 3, 7}               | −4224 · i                        | 0 |
| 5 | {1, 10, 100}            | −179360/111 · i                  | 0 |
| 5 | {1/1000, 1, 1}          | −1501/62531250000000000 · i      | 0 |
| 5 | {1, 1000, 10⁶}          | −1.60000…×10⁷ · i                | 0 |
| 6 | {3/2, 2, 5/2, 3}        | −11907/4 · i                     | 0 |
| 6 | {1, 3, 5, 7}            | −338 · i                         | 0 |
| 6 | {2, 3, 7, 11}           | −62686.60… · i                   | 0 |
| 6 | {1/100, 5, 50, 500}     | −1.616…×10⁻¹⁰ · i                | 0 |
| 7 | {3/2, 2, 5/2, 3, 7/2}   | −7302393/400 · i                 | 0 |
| 7 | {1, 2, 3, 4, 5}         | −8896/15 · i                     | 0 |
| 7 | {1/10, 2, 4, 8, 16}     | −1.3246…×10⁻⁶ · i                | 0 |
| 8 | {1, 2, 3, 4, 5, 6}      | −33920/21 · i                    | 0 |

(plus the full lists in `verify_main.m`, `waterwave_bg.py`.)

### Domain confirmation (randomised)

`stress_test.py` draws 79 random rational kinematics (n = 5, 6; mixed signs and
magnitudes) and checks the equivalence

> ( |ω₂| = minᵢ|ωᵢ| )  ⇔  ( formula equals BG exactly ).

**It holds for all 79 points** — confirming both the formula *and* the exact
boundary of its chamber.  Points where the predicate is false (e.g. a plus leg
smaller than ω₂, or ω₂ largest) correctly *fail* the monomial and live in other
chambers.

---

## 4. How I arrived at it (reasoning)

1. **Exact data.** Ran the supplied BG with rational kinematics; the two-minus
   amplitudes are purely imaginary rationals (the one-minus sector vanishes, so
   two-minus is the first non-trivial sector — an "MHV-like" structure).

2. **Scaling.** Fixed the homogeneity (deg 2n−4 in ω) and g-power (g^{−(n−3)}).

3. **Sign-frozen symbolic extraction.** The only obstruction to a symbolic
   amplitude is `mag = Abs` on composite momenta.  I overrode `mag[k]` to return
   `Sign[k|_{base}]·k` — freezing each momentum's sign at a numeric base point —
   which turns BG into an *exact rational function* valid throughout that base
   point's chamber.  In the principal chamber this gave, immediately,

   * A₅ = −16 i ω₂⁵ (ω₂ω₃+ω₃²+ω₂ω₄+ω₃ω₄+ω₄²)/(ω₂+ω₃+ω₄).

   Using the on-shell relations the numerator factor reduces to
   S·(S+ω₅) = −ω₁·S with S = ω₂+ω₃+ω₄, leaving **A₅ = 16 i ω₁ ω₂⁵** — the
   plus legs cancel.

4. **Pattern across n.**  The same extraction gives A₆ = 32 i ω₁ω₂⁷/g³,
   A₇ = 64 i ω₁ω₂⁹, A₈ = 128 i ω₁ω₂¹¹: coefficient 2^{n−1}, exponent 2n−5.

5. **Chamber map (the waterhedron).**  Factoring the sign-frozen amplitude in
   many chambers shows the building blocks are v₁=ω₂, v₂=ω₃, v₃=ω₄,
   Q = −ω₁S and (ω₂+ω₃)(ω₂+ω₄) = −ω₅S.  Different chambers select different
   monomials/polynomials in these, e.g. (n=5):
   * principal (|ω₂| smallest):  A₅ = 16 i ω₁ ω₂⁵
   * ω₂ largest, ω₂² > ω₃²+ω₄²:  A₅ = 32 i ω₁ ω₂ ω₃² ω₄²
   * ω₂ largest, ω₂² < ω₃²+ω₄²:  A₅ = −16 i ω₁ ω₂ (ω₂⁴−2ω₂²ω₃²+ω₃⁴−2ω₂²ω₄²+ω₄⁴)
   * ω₂ < 0 with |ω₂| not minimal: rational with a 1/S² factorisation pole.

   These agree on their shared walls (the amplitude is continuous) and all
   collapse to the boxed monomial in the principal chamber.

6. **Independent check.** Re-derived everything with a clean-room Python BG
   (exact `Fraction`s) — agrees to the last digit.

---

## 5. Files

| file | purpose |
|------|---------|
| `ANSWER.md`        | this report |
| `BGcore.m`         | definitions-only copy of `OnShellBG.m` (sec. I–V) used by all probes |
| `verify_main.m`    | principal-chamber verification, n=5,6,7 (exact) + documented non-principal mismatches |
| `verify_n4.m`      | n=4 degenerate-limit verification (numeric + symbolic) |
| `verify_n8.m`      | n=8 verification (exact) |
| `waterwave_bg.py`  | **independent** Python Berends–Giele recursion + formula + cross-check |
| `stress_test.py`   | 79-point randomised domain test (predicate ⇔ match) |
| `verify_formula.ipynb` | runnable notebook reproducing the Python cross-check |
| `probe*.m`         | exploration record (scaling, sign-frozen symbolic extraction, chamber factoring) |

Reproduce:
```
wolframscript -file verify_main.m         # exact, n=5,6,7
wolframscript -file verify_n4.m           # n=4 limit
python3 waterwave_bg.py                   # independent Python cross-check
python3 stress_test.py                    # randomised domain confirmation
```
