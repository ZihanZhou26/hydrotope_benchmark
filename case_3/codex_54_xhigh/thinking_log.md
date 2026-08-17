# Rewritten Thinking Log for the Two-Minus Water-Wave Amplitude

## Abstract

This document is an expanded rewritten summary of the reasoning process used to solve the benchmark task in `case_3`. It follows the style of the example in `thinking_log_format`: a title, an abstract, and a continuous technical narrative. It is not a raw private chain-of-thought transcript. Instead, it records the concrete hypotheses that were tested, the examples that were generated, the failed reconstruction attempts, the branch issues that had to be isolated, and the exact checks that led to the final formula.

## Rewritten Thinking Log

The target was to find a closed-form expression for the tree-level on-shell amplitude `A_n` in the two-minus sector

```math
\sigma = (-1,-1,+1,\dots,+1),
```

using only the benchmark prompt and the Wolfram source `OnShellBG.m`. The answer had to be valid for all `n \ge 4`, and it had to be supported by numerical evidence at least through `n = 7`.

The first step was to identify what the supplied code actually computes. The essential ingredients were the recursive interaction kernels `EKernel` and `FKernel`, the fully symmetrized vertex, the propagator, the set-partition generator, and the Berends–Giele current recursion. The `MakeKinematics` routine was especially important, because it does not produce arbitrary two-minus kinematics; it picks a particular branch by treating `\omega_2,\dots,\omega_{n-1}` as inputs and solving linearly for `\omega_1` and `\omega_n`. That detail turned out to matter later, because the final formula is cleanest when stated on that standard benchmark branch.

At the outset there were several plausible possibilities for the structure of the answer. It could have vanished identically, as happened in the one-minus sector tested at the bottom of `OnShellBG.m`. It could have been a large symmetric polynomial in all frequencies. It could have factorized into a simple monomial times a small coefficient depending only on `n`. It could also have depended strongly on which two legs carried the negative signs, because the recursion and kinematic solver together break manifest permutation symmetry once one chooses a branch. The working strategy was therefore to generate exact low-point data, look for scaling laws, and then test increasingly sharp ansätze rather than assume a structure too early.

To make those tests practical, I created an exact SymPy port of the BG recursion in [analysis.py](/home/zihanz/waterhedron_benchmark_blind/case_3/codex_54_xhigh/analysis.py). This was not a conceptual change to the algorithm; it was a copy of the same kernels, vertex, propagator, partitions, and recursion into a format that made repeated exact sampling easier. The first version of that port unnecessarily called `nsimplify` inside the absolute-value helper, and that made some evaluations much slower than they needed to be. After removing that step, the code became usable for exact experiments through `n = 7`.

The first batch of exact data already ruled out the trivial vanishing hypothesis. For the standard two-minus sign pattern,

```math
\sigma = (-1,-1,+1,\dots,+1),
```

I evaluated several points:

```math
n=5,\quad \text{freeW}=\left\{2,\frac52,3\right\},\quad
\omega=\left(-\frac92,2,\frac52,3,-3\right),\quad
A_5=-2304\,i,
```

```math
n=6,\quad \text{freeW}=\left\{\frac32,2,\frac52,3\right\},\quad
\omega=\left(-\frac{49}{9},\frac32,2,\frac52,3,-\frac{32}{9}\right),\quad
A_6=-\frac{11907}{4}\,i,
```

```math
n=7,\quad \text{freeW}=\{1,2,3,4,5\},\quad
\omega=\left(-\frac{139}{15},1,2,3,4,5,-\frac{86}{15}\right),\quad
A_7=-\frac{8896}{15}\,i.
```

These examples immediately suggested three basic facts. First, the amplitudes were clearly not zero. Second, the results were purely imaginary at all tested points. Third, the answers were exact rationals times `i`, which made it reasonable to aim for exact symbolic pattern extraction rather than floating-point fitting.

The next hypothesis was homogeneity. Since the dispersion relation is quadratic in the frequencies and the recursion is built from homogeneous algebraic ingredients, there was a good chance that `A_n` would scale by a fixed power under a common rescaling `\omega_i \mapsto \lambda \omega_i`. I tested this directly by doubling the free frequencies in representative examples. The ratios were:

```math
n=5:\quad \frac{A_5(2\,\text{freeW})}{A_5(\text{freeW})}=64=2^6,
```

```math
n=6:\quad \frac{A_6(2\,\text{freeW})}{A_6(\text{freeW})}=256=2^8,
```

```math
n=7:\quad \frac{A_7(2\,\text{freeW})}{A_7(\text{freeW})}=1024=2^{10}.
```

This fixed the homogeneity degree as

```math
A_n(\lambda \omega_1,\dots,\lambda \omega_n)
=
\lambda^{2n-4} A_n(\omega_1,\dots,\omega_n).
```

That was the first serious constraint on the answer. Any plausible closed form now had to carry total degree `2n-4`.

At `n = 5` I then tried to reconstruct the answer as a generic homogeneous expression in a smaller set of variables. One natural guess was that, once `\omega_1` had been solved from the constraints, the amplitude might be expressible as a symmetric degree-six polynomial in the remaining three legs `\omega_3,\omega_4,\omega_5`. To test that, I computed the elementary symmetric polynomials

```math
e_1=\omega_3+\omega_4+\omega_5,\qquad
e_2=\omega_3\omega_4+\omega_3\omega_5+\omega_4\omega_5,\qquad
e_3=\omega_3\omega_4\omega_5,
```

and fit `A_5/i` on a seven-dimensional basis

```math
e_1^6,\;
e_1^4 e_2,\;
e_1^3 e_3,\;
e_1^2 e_2^2,\;
e_1 e_2 e_3,\;
e_2^3,\;
e_3^2.
```

This fit succeeded on the interpolation points, but it failed badly on hold-out data. For example, at `freeW = {2,4,5}` the actual value was

```math
A_5 = -\frac{40448}{11} i,
```

whereas the fitted polynomial predicted

```math
A_5 = -\frac{104785134878}{19487171} i.
```

That was a decisive failure, not a rounding issue. It showed that the amplitude was not behaving like a generic symmetric degree-six polynomial in that subset of legs.

I also explored a second reconstruction idea: perhaps the amplitude became polynomial only after multiplying by a suitable power of the total input sum

```math
s = \omega_2 + \cdots + \omega_{n-1}.
```

The concrete test was to try, at `n = 5`, to fit `A_5 s^q / i` as a homogeneous polynomial of degree `6+q` in the free variables for `q = 0,1,\dots,6`. Each of those linear systems turned out to be singular. That failure did not identify the formula, but it was informative: it suggested that the answer lived on a much lower-dimensional ansatz than a generic rational function of the free variables.

The decisive observation came from dividing out the simplest monomial consistent with the homogeneity count. Because `\omega_1` is solved linearly by `MakeKinematics` and `\omega_2` is the first free input, I checked whether

```math
\frac{A_n}{i\,\omega_1\,\omega_2^{2n-5}}
```

was constant. That ratio stabilized immediately. The exact values were

```math
n=5:\quad \frac{A_5}{i\,\omega_1\,\omega_2^5}=16,
```

```math
n=6:\quad \frac{A_6}{i\,\omega_1\,\omega_2^7}=32,
```

```math
n=7:\quad \frac{A_7}{i\,\omega_1\,\omega_2^9}=64.
```

I checked the same ratio on additional points at each multiplicity, and it stayed fixed. That suggested the formula

```math
A_n = 2^{n-1} i\, \omega_1\, \omega_2^{2n-5}.
```

This was simple enough that the next question was no longer how to guess it, but how broadly it was supposed to hold.

At that point I turned to branch dependence. The benchmark’s `MakeKinematics` does not parametrize all two-minus configurations uniformly; it solves one specific branch of the constraints. I tested simple permutations at `n = 5` to see whether the monomial formula was merely an artifact of the labeling. For the point

```math
\omega=(-4,1,2,3,-2),
```

the amplitude was unchanged under swapping legs `1` and `2`, and also unchanged under swapping legs `3` and `4`; in each of those cases the numerical value remained `-64 i`. That was consistent with the underlying amplitude being more symmetric than the parametrization. However, I also tested nonstandard input choices with negative free frequencies. For example:

```math
\text{freeW}=\{-1,2,3\}
\quad\Longrightarrow\quad
\omega=\left(-\frac72,-1,2,3,-\frac12\right),
\quad
A_5=\frac{49}{2} i,
```

while some other atypical choices with vanishing input sum produced singular kinematics. Those experiments showed that the clean monomial statement should be phrased for the standard benchmark branch rather than for arbitrary sign choices in the free inputs.

Once the candidate formula had survived the exploratory phase, I switched to strict source-level verification. The file [verify_formula.wls](/home/zihanz/waterhedron_benchmark_blind/case_3/codex_54_xhigh/verify_formula.wls) reimplemented the recursion from `OnShellBG.m` and compared `BGAmplitude` directly to the candidate expression on exact rational test points. This was important because the final answer needed to be tied back to the original Wolfram implementation, not only to the SymPy port.

The exact checks for `n = 5,6,7` all succeeded. A representative sample is:

```math
n=5,\quad \text{freeW}=\{1,2,3\},\quad
\omega=\{-4,1,2,3,-2\},\quad
BG=-64i,\quad
\text{candidate}=-64i,
```

```math
n=5,\quad \text{freeW}=\left\{2,\frac52,3\right\},\quad
\omega=\left\{-\frac92,2,\frac52,3,-3\right\},\quad
BG=-2304i,\quad
\text{candidate}=-2304i,
```

```math
n=6,\quad \text{freeW}=\{1,3,5,7\},\quad
\omega=\left\{-\frac{169}{16},1,3,5,7,-\frac{87}{16}\right\},\quad
BG=-338i,\quad
\text{candidate}=-338i,
```

```math
n=6,\quad \text{freeW}=\{2,3,4,9\},\quad
\omega=\left\{-\frac{71}{6},2,3,4,9,-\frac{37}{6}\right\},\quad
BG=-\frac{145408}{3}i,\quad
\text{candidate}=-\frac{145408}{3}i,
```

```math
n=7,\quad \text{freeW}=\{2,3,5,7,11\},\quad
\omega=\left\{-\frac{123}{7},2,3,5,7,11,-\frac{73}{7}\right\},\quad
BG=-\frac{4030464}{7}i,\quad
\text{candidate}=-\frac{4030464}{7}i.
```

In each of those examples the exact symbolic difference `BGAmplitude - candidate` simplified to zero.

The prompt also asked for non-generic tests. To cover that requirement, I deliberately chose points where one free input was very small compared with the others:

```math
n=5,\quad \text{freeW}=\left\{\frac{1}{10},3,11\right\},\quad
\omega=\left(-\frac{548}{47},\frac{1}{10},3,11,-\frac{1147}{470}\right),
```

```math
A_5 = -\frac{274}{146875} i,
```

```math
n=6,\quad \text{freeW}=\left\{\frac{1}{10},2,5,11\right\},\quad
\omega=\left(-\frac{2388}{181},\frac{1}{10},2,5,11,-\frac{8881}{1810}\right),
```

```math
A_6 = -\frac{597}{14140625} i,
```

```math
n=7,\quad \text{freeW}=\left\{\frac{1}{10},2,3,5,13\right\},\quad
\omega=\left(-\frac{529}{33},\frac{1}{10},2,3,5,13,-\frac{2333}{330}\right),
```

```math
A_7 = -\frac{529}{515625000} i.
```

In each case the BG recursion and the candidate formula agreed exactly. These were useful checks because they made it much less plausible that the monomial form was only a large-frequency or generic-position phenomenon.

The only serious obstruction appeared at `n = 4`. There the raw recursion returned `Indeterminate` in both Wolfram and the SymPy port. This was not just one bad sample point; it occurred systematically on the two-minus four-point branch. I then tried to isolate what kind of singularity was present.

The first observation was that even the direct four-point vertex evaluation landed on `nan`, so the problem was not just an artifact of a deeper current recursion at larger `n`. The next question was whether a tiny deformation would resolve it. A first attempt changed only one external momentum, or equivalently perturbed the kinematics in a way that preserved too much of the original cancellation pattern. Those partial deformations still returned `nan`, which indicated that the `0/0` structure was more stubborn than a one-leg perturbation could remove.

The successful regularization was a generic multi-leg deformation of the external momenta while keeping the external frequencies fixed. For

```math
\omega = (-x,a,x,-a),
```

I used

```math
k = \left(-x^2-\delta,\,-a^2-2\delta,\,x^2+3\delta,\,a^2+5\delta\right).
```

This pushed the computation away from the exact singular locus without changing the target limiting frequencies. For `a = 2`, `x = 3`, the candidate formula predicts

```math
A_4 = 8i\,\omega_1\omega_2^3 = -192 i.
```

The regularized BG values were

```math
\delta=10^{-5}:\quad -191.9997900004083297\,i,
```

```math
\delta=10^{-6}:\quad -191.9999790000040833\,i,
```

```math
\delta=10^{-7}:\quad -191.9999979000000408\,i.
```

The errors decreased linearly with the deformation size, and the values converged cleanly toward `-192 i`.

I repeated the same check at a second point, `a = 3/2` and `x = 5`, where the formula predicts

```math
A_4 = -135 i.
```

The regularized sequence was

```math
\delta=10^{-5}:\quad -134.9988300050099720\,i,
```

```math
\delta=10^{-6}:\quad -134.9998830000501000\,i,
```

```math
\delta=10^{-7}:\quad -134.9999883000005010\,i.
```

Again the computation converged steadily to the predicted value. That established that the apparent `n = 4` failure of the raw code was a removable singularity of the implementation, not a failure of the formula.

I also made one attempt to extend the exact checks to `n = 8`. The SymPy recursion did begin the calculation, but exact simplification became slow enough that it was no longer the best use of time once the pattern had already been nailed down at `n = 5,6,7`, the extreme points had been checked, and the `n = 4` endpoint had been resolved. I therefore stopped that extra computation rather than spend additional time on a verification point that was not required by the prompt.

After that, the remaining task was to package the result cleanly. The exact Wolfram comparison was written to [verify_formula.out](/home/zihanz/waterhedron_benchmark_blind/case_3/codex_54_xhigh/verify_formula.out). The small-frequency tests were written to [extreme_checks.out](/home/zihanz/waterhedron_benchmark_blind/case_3/codex_54_xhigh/extreme_checks.out). The `n = 4` regularization study was written to [n4_limit_check.out](/home/zihanz/waterhedron_benchmark_blind/case_3/codex_54_xhigh/n4_limit_check.out). The concise benchmark answer was written to [result.md](/home/zihanz/waterhedron_benchmark_blind/case_3/codex_54_xhigh/result.md).

The final conclusion is that, on the standard `MakeKinematics` branch used by the benchmark in the two-minus sector,

```math
A_n = 2^{n-1} i\, \omega_1\, \omega_2^{2n-5},\qquad n \ge 4.
```

The extended search path leading to that answer can be summarized as follows. Exact low-point data ruled out vanishing. Scaling fixed the degree. A symmetric-polynomial fit in the remaining legs failed. A denominator-reconstruction attempt using powers of the input sum also failed. A monomial ratio test then exposed the formula immediately. Exact Wolfram checks confirmed it for `n = 5,6,7`. Finally, a generic off-shell regularization showed that the same formula gives the correct resolved limit at `n = 4`.
