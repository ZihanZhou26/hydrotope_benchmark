# Case 2: true hint

`prompt.md` and `OnShellBG.m` are the files supplied for this blind condition.
The prompt gives the correct piecewise-polynomial structural hint described in
the paper.

Each model directory separates the run from material added afterward:

- files at the model-directory root are the original workspace artifacts
  produced or retained by the agent during the run;
- `post_run/` contains records created later for the paper and audit, including
  the canonical `thinking_log.tex` and `thinking_log.pdf` and the standardized
  visible event records.

Nothing in `post_run/` was available to the agent during the benchmark run.
Only one canonical formatted thinking log is retained for each model.
