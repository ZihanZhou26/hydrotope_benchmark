# A6 local pipeline (student-1)

This directory contains the corrected stage scripts for pole approach, wall approach, and final ansatz fitting.

## Run commands
- Compile all scripts:
  - `python3 -m py_compile bots/student-1/code/calibration.py bots/student-1/code/domain_scan.py bots/student-1/code/pole_scan.py bots/student-1/code/wall_approach.py bots/student-1/code/wall_hinge_fit.py bots/student-1/code/wall_power_fit.py bots/student-1/code/wall_smoothness.py bots/student-1/code/ansatz_fit.py bots/student-1/code/common.py bots/student-1/code/exact_oracle.py`
- Run local wall-hinge fit + word census diagnostics:
  - `python3 bots/student-1/code/wall_hinge_fit.py`
- Run wall-power fit diagnostics (wall+P8 families and staged D1/S3/P8 checks):
  - `python3 bots/student-1/code/wall_power_fit.py`
- Run wall smoothness diagnostics (exact one-sided interpolation over `wall_approaches.json`):
  - `python3 bots/student-1/code/wall_smoothness.py`
- Run the full pipeline:
  - `bash bots/student-1/code/run_pipeline.sh`

## Orchestrated pipeline
`run_pipeline.sh` runs, in order:
1. `calibration.py`
2. `domain_scan.py`
3. `pole_scan.py`
4. `wall_approach.py`
5. `ansatz_fit.py`

Each script writes to `bots/student-1/data/*` and logs to `bots/student-1/data/*.log`.

## Pole scan strategy (`pole_scan.py`)
- Uses orbit decomposition of internal subsets under `S3 x S3` and set-swap.
- Supported compositions: `(2,0)`, `(1,1)`, `(3,0)`, `(2,1)` (with size-pair normalized by swap).
- `(2,0)` and `(1,1)` are recorded as algebraically degenerate and are **not** numerically scanned.
- For `(3,0)` and `(2,1)`, each affine family is:
  - `(w2,w3,w4,w5) = c + d*t` with 12 deterministic rational `(c,d)` pairs (see script constant `FAMILIES`).
- Pole condition uses exact finite-difference sign branch:
  - `h = (sum_T w)^2 - sign(q_T) * q_T`.
- Root scans are done by SymPy exact rational expressions (`factor/nroots` on cleared-denominator polynomials), with root centers stored at 14-decimal rational form.
- Side probes are at `t_c ± 10^{-d}` for `d=2..7`, exact (`common.solve_from_free` + `exact_oracle.evaluate_omega`).
- Rejection checks include nonzero free sum, nonzero `q`, no zero `w_i`, no wall zero in the 18 nondegenerate walls, and no inequivalent triple-pole `h=0`.
- Outputs:
  - `data/pole_approaches.json`
  - `data/pole_report.txt`

## Wall scan strategy (`wall_approach.py`)
- Targets nondegenerate wall composition orbits `(1,1)` and `(1,2)`.
- Uses the same 12 affine rational families and SymPy exact rational scanning.
- Rejections include free-sum/kinematic validity, external wall zeros, non-target wall zeros among 18 wall formulas, and other triple-pole `h=0`.
- Side probes: `t_c ± 10^{-d}` for `d=2..7`, exact BG evaluation.
- Requires both-side `|q|` decade scaling to pass for coverage classification.
- Outputs:
  - `data/wall_approaches.json`
  - `data/wall_report.txt`

## ansatz fit (`ansatz_fit.py`)
- Uses category features `r1_*` and `r2_*` with no `_Ixx` suffix.
- Uses `CategoryFeature(r, category)` and `CategoryFeature._b` with positive-part cube, alternating finite-difference signs.
- Keeps full subset-loop over `I` and per-feature invariance checks.

## H1 feature definition/counts
- Features are named by category pairs in
  - `r1_A_A_diag`, `r1_A_C`, `r1_A_R`, `r1_C_C_diag`, `r1_C_C_off`, `r1_C_R`, `r1_R_R_diag`, `r1_R_R_off`
  - `r2_A_A_diag`, `r2_A_A_off`, `r2_A_C`, `r2_A_R`, `r2_C_C_diag`, `r2_C_R`, `r2_R_R_diag`, `r2_R_R_off`
- Total counts in this script: `r1=8`, `r1+r2=16`.

## Dependencies and runtime
- Python 3.6+
- GMP-backed `bg` binary built by `run_pipeline.sh`
- `sympy` (exact rational root handling for pole/wall scans)
- Standard library modules used in these scripts.

## Known outputs in `bots/student-1/data`
- `calibration.txt`
- `domain_scan.log`, `domain_scan.json`/`domain_signatures.json`
- `wall_catalog.json`
- `pole_approaches.json`, `pole_report.txt`, `pole_scan.log`
- `wall_approaches.json`, `wall_report.txt`, `wall_approach.log`
- `h1_fit_report.json`, `h1_fit_report.txt`
- `fresh_structure_oracle.jsonl` — exact-oracle fresh train/holdout rows used by `wall_hinge_fit.py`
- `wall_hinge_fit.json` — compact dictionary of fit diagnostics (H3 feature inventory/ranking, exact consistency, residuals)
- `wall_hinge_fit.txt` — compact human-readable summary of the latest wall-hinge fit run
- `wall_power_fit.json` — expanded wall-power staging and consistency diagnostics (H2/H3/H4/D1/S3/P8 family checks)
- `wall_power_fit.txt` — compact human-readable summary of staged wall-power checks
- `wall_smoothness.json` — one-sided polynomial interpolation across `(1,1)` and `(1,2)` wall families
- `wall_smoothness.txt` — compact human-readable one-sided interpolation summary
- `word_census.json` — census over merged word classes used to characterize sign/configuration patterns
