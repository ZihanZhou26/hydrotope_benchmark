# Paper materials

- `neurips_latex/main.tex`: manuscript source
- `neurips_latex/main.pdf`: compiled manuscript
- `neurips_latex/references.bib`: bibliography
- `figures/`: final figure PDFs and their available sources
- `checkpoint_profiles/`: per-run milestone annotations used for Fig. 4
- `baseline_run_manifest.md`: outcome labels and per-run audit

Build the manuscript from `paper/neurips_latex`:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```
