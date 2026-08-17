# Hydrotope benchmark

This repository contains the paper, prompts, run records, checking code, and
supporting data for a study of how AI agents discover analytic formulas for
one-dimensional surface-water-wave scattering.

The benchmark asks an agent to infer the complete two-minus hydrotope formula
from a Berends--Giele amplitude evaluator. Eighteen single-agent runs compare
three prompt conditions: a false hint, a true structural hint, and no hint. The
repository also contains the PI--student team runs and the six-point
three-minus calculation discussed in the paper.

## Start here

- [Paper PDF](paper/neurips_latex/main.pdf)
- [Paper source](paper/neurips_latex/main.tex)
- [Single-agent run index](original_thinking_log_index.md)
- [Condition map and exact target](KEY.md)
- [Per-run outcome audit](paper/baseline_run_manifest.md)
- [Fast C++ Berends--Giele evaluator](tools/README.md)

## Repository structure

| Path | Contents |
| --- | --- |
| `paper/` | LaTeX source, compiled paper, final figures, figure sources, and analysis tables |
| `case_1/` | Six single-agent runs with the false hint |
| `case_2/` | Six single-agent runs with the true hint |
| `case_3/` | Six single-agent runs with no hint |
| `Bot-research/questions/` | PI and two-student two-minus workflows using Claude and Codex |
| `recursive_scaffold/` | PI--student rediscovery run for the two-minus formula |
| `three_minus_recursive/` | PI--student run for the six-point three-minus amplitude |
| `three_minus_single/` | Independent three-minus derivation and verification material |
| `prompts/` | Shared task material and C++ oracle prompt package |
| `tools/` | Source for the fast exact and floating-point amplitude evaluator |

Each single-agent result folder keeps the original agent workspace at its root.
Files added later for the paper and audit are separated under `post_run/`.
These include the canonical formatted thinking log and the standardized visible
message and tool-event records. The visible records do not claim to reconstruct
unrecorded private model reasoning.

## Build the paper

A recent TeX Live installation with `pdflatex`, `bibtex`, TikZ, and the packages
loaded by `main.tex` is required.

```bash
cd paper/neurips_latex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The figure PDFs used by the manuscript are stored in `paper/figures/`. Their
available Python and TikZ sources are kept beside them and listed in
[`paper/figures/README.md`](paper/figures/README.md).

## Repeat a blind single-agent run

Create an isolated working directory and copy only `prompt.md` and
`OnShellBG.m` from one `case_N` directory into it. Do not copy the recorded
model-run directories, `KEY.md`, another case, or another run. Instruct the
agent to read the two copied files. The original tests prohibited internet and
literature lookup.

After the run, compare the proposed formula with the exact evaluator across
several values of `n` and frequency chambers. The scoring definitions and the
18 recorded outcomes are given in
[`paper/baseline_run_manifest.md`](paper/baseline_run_manifest.md).

## Build the fast evaluator

The C++ evaluator requires GMP:

```bash
g++ -O2 -std=c++17 -o bg tools/bg.cpp -lgmpxx -lgmp
./bg -n 5 -w 2,3,5 -s -1,-1,-1,1,1
```

See [`tools/README.md`](tools/README.md) for exact and floating-point usage.

## Notes

- The repository contains research artifacts and a working paper draft.
- Generated LaTeX caches, synchronization files, Python caches, and compiled
  executables are intentionally excluded.
- Mathematica/Wolfram Language is required for scripts that call
  `OnShellBG.m`; Python and C++ alternatives are included for many checks.
