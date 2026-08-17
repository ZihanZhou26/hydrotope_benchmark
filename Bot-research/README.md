# Multi-agent workflows

The `questions/` directory contains the multi-agent runs used in the paper.

For the two-minus water-wave problem:

- `questions/waterwaves/`: PI and two student agents using Claude Opus 4.8;
- `questions/waterwaves_codex/`: PI and two student agents using Codex GPT-5.5.

For the three-minus six-point analysis:

- `questions/waterwaves_threem/`: the main PI and two-student run that found
  the complete explicit formula for \(A_6\) and passed 140 tests in 58
  chambers;
- `questions/waterwaves_threem_codex_A6_1pi_1student/`: the PI and one-student
  comparison run, which obtained formulas in two chambers but did not cover
  all chambers;
- `questions/waterwaves_threem_codex_A6_1pi_2students_1verifier/`: the PI,
  two-student, and verifier comparison run, which found and independently
  checked the complete \(A_6\) formula.

The corresponding single-agent three-minus run is stored separately in
`three_minus_single/` at the repository root.

Each question folder is self-contained. It includes the question and prompts,
the orchestration scripts, PI and student session records, generated code and
data, the shared board, the final group summary, and a human-readable
`RUN_REPORT.md`.

For a concise result, begin with `RUN_REPORT.md`, `summary/FINAL_SUMMARY.md`,
or `summary/SOLVED.md`, depending on which files are present in the relevant
question folder.
