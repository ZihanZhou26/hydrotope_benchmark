# Hydrotope benchmark

This repository contains the run records, generated code, and supporting data
for a study of how AI agents discover analytic formulas for one-dimensional
surface-water-wave scattering.

The benchmark asks an agent to infer the complete two-minus hydrotope formula
from a Berends--Giele amplitude evaluator. Eighteen single-agent runs compare
three prompt conditions: a false hint, a true structural hint, and no hint. The
repository also contains the PI--student team runs and the six-point
three-minus calculation discussed in the paper.

## Start here

- [Single-agent run index](original_thinking_log_index.md)
- [False-hint runs](case_1/README.md)
- [True-hint runs](case_2/README.md)
- [No-hint runs](case_3/README.md)

## Repository structure

| Path | Contents |
| --- | --- |
| `case_1/` | Six single-agent runs with the false hint |
| `case_2/` | Six single-agent runs with the true hint |
| `case_3/` | Six single-agent runs with no hint |
| `multi_agent_two_minus/` | PI and two-student two-minus workflows using Claude and Codex |
| `multi_agent_three_minus/` | Single- and multi-agent records for the six-point three-minus analysis |

Each single-agent result folder keeps the original agent workspace at its root.
Files added later for the paper and audit are separated under `post_run/`.
These include the canonical formatted thinking log and the standardized visible
message and tool-event records. The visible records do not claim to reconstruct
unrecorded private model reasoning.

## Repeat a blind single-agent run

Create an isolated working directory and copy only `prompt.md` and
`OnShellBG.m` from one `case_N` directory into it. Do not copy the recorded
model-run directories, another case, or another run. Instruct the agent to read
the two copied files. The original tests prohibited internet and literature
lookup.

After the run, compare the proposed formula with the exact evaluator across
several values of `n` and frequency chambers.

## Notes

- The repository contains research artifacts supporting the paper.
- Generated LaTeX caches, synchronization files, Python caches, and compiled
  executables are intentionally excluded.
- Mathematica/Wolfram Language is required for scripts that call
  `OnShellBG.m`; Python and C++ alternatives are included for many checks.
