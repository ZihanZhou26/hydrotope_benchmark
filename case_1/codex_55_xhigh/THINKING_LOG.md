# Rewritten Thinking Log for the Two-Minus Benchmark

## Abstract

This document contains a rewritten summary of the reasoning and process used
for the `waterhedron_benchmark_blind/case_1` task.  It follows the narrative
style of the reference file in `thinking_log_format`, but it is a concise
process summary rather than a verbatim hidden chain of thought.

## Rewritten Thinking Log

The task asked for a closed-form analytic formula for the tree amplitude
`A_n` in the two-minus sector, valid for all `n >= 4`, and specifically
claimed that the answer should be a single global rational function of the
frequencies.  The first step was to locate the case directory, read only the
permitted task files, `prompt.md` and `OnShellBG.m`, and avoid using the
pre-existing sibling solution directory.  The requested output location was
interpreted as
`/home/zihanz/waterhedron_benchmark_blind/case_1/codex_55_xhigh`, because no
separate `waterhedron_benchmark_blind_case_1` directory existed.

The supplied Wolfram file contained exact Berends-Giele recursion code plus
stock tests.  Running the whole file directly was not useful because the
built-in tests entered a slow `n = 8` symbolic example.  That run was stopped,
and targeted Wolfram snippets were used instead by loading the definitions
while suppressing the stock print-driven test section.  During the first
attempts the host entered a severe memory-pressure state and refused to fork
even trivial commands with `Out of memory (os error 12)`.  A temporary blocker
report was written, then replaced once process creation recovered.

The decisive check was to start at `n = 4`, since the requested formula was
supposed to hold for every `n >= 4`.  In the two-minus sector with

```text
sigma = {-1, -1, 1, 1}
free frequencies = {-x, y}, x > 0, y > 0
```

the supplied kinematic solver gives

```text
{omega1, omega2, omega3, omega4} = {-y, -x, y, x}.
```

Symbolic evaluation of the supplied `BGAmplitude` on this family did not give
a single rational expression.  It gave the chamber-dependent result

```text
A4 = Piecewise[
  {{8 I x^3 y, x < y}, {8 I x y^3, x > y}},
  24 I y^4
]
```

The two open-branch formulas differ by

```text
8 I x y (x^2 - y^2).
```

This is the central obstruction.  A rational function that agrees with
`8 I x^3 y` on the open set `x < y` must be that rational function
identically.  It therefore cannot also agree with `8 I x y^3` on the open set
`x > y`, unless those two polynomials are identical, which they are not.  So
the supplied BG code contradicts the prompt's claim that there is a single
global rational expression with no chamber decomposition.

There was also a numerical issue at four points.  Direct exact numeric
evaluation at the same four-point kinematics hit a zero-momentum internal
channel and returned `Indeterminate`.  The finite piecewise formula only
appears when the calculation is kept symbolic long enough for the branch
structure and cancellations to be exposed.  This makes the prompt's requested
machine-precision numerical verification at `n = 4` ill-defined for the
supplied implementation.

Five-point checks were still useful for orientation.  Targeted Wolfram
evaluations gave, for example,

```text
free = {-2, 3, 4}      -> A5 = 184.64768 I
free = {2, 5/2, 3}     -> A5 = -2304 I
```

To reduce repeated Wolfram startup cost and continue the exploration, two
Python ports of the permitted BG definitions were written: `bg_numeric.py` for
floating-point exploration and `bg_exact.py` for exact rational arithmetic.
The numeric port matched the targeted Wolfram five-point values.  Exact
interpolation attempts against simple symmetric rational ansatzes failed with
inconsistent systems, and a one-parameter five-point Wolfram
`PiecewiseExpand` produced a large chamber-dependent expression.  These checks
reinforced the four-point obstruction rather than removing it.

The final verification artifact was therefore focused on the minimal
contradiction.  The script `verify_n4_contradiction.m` loads only the supplied
definitions, constructs the four-point two-minus family above, prints the
symbolic piecewise amplitude, prints the difference between the open-branch
formulas, and records the direct exact numeric `Indeterminate` behavior.  Its
saved output is `verify_n4_contradiction.out`.

The final report does not present an unverified formula.  Instead, it records
that the benchmark prompt is inconsistent with the supplied `BGAmplitude`: the
required global rational answer cannot exist for all `n >= 4` because it
already fails at `n = 4`.

## Artifacts

The generated files in `codex_55_xhigh` are:

```text
REPORT.md
LOG.md
THINKING_LOG.md
bg_exact.py
bg_numeric.py
verify_n4_contradiction.m
verify_n4_contradiction.out
```
