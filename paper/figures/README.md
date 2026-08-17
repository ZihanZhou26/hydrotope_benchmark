# Paper figures

This directory contains only figures used by `paper/neurips_latex/main.tex`
and the local sources needed to regenerate them.

| Included PDF | Regeneration source |
| --- | --- |
| `summary_figure.pdf` | `summary_figure_code.py` |
| `MAE_symbolic_regression_n5.pdf` | archived final asset; generator not present in this repository |
| `checkpoint_raster.pdf` | `evaluate_checkpoint_mae.py`, `checkpoint_formula_mae.csv`, `checkpoint_mae_n8_points.csv`, and `make_checkpoint_raster.py` |
| `four_run_comparison.pdf` | `four_run_comparison.tex` |
| `student_teacher_rounds_native_tikz.pdf` | `student_teacher_rounds_native_tikz.tex` |
| `three_minus_a6_workflow_tikz.pdf` | `three_minus_a6_workflow_tikz.tex` |
| `a6_architecture_editorial_tikz.pdf` | `a6_architecture_editorial_tikz.tex` |
| `MAE_symbolic_regression_n7.pdf` | archived final asset; generator not present in this repository |

Temporary LaTeX files (`.aux`, `.fdb_latexmk`, `.fls`, and `.log`) and raster
preview exports are intentionally excluded. The manuscript also contains an
optional reference to `appendix_other_approaches_mae.pdf`; because that asset
is not present, the compiled appendix uses its existing placeholder.
