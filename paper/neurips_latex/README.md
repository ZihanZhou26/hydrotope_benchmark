# NeurIPS Workshop LaTeX Draft

This folder contains the LaTeX version of the waterhedron agentic-discovery paper draft.

## Official Template

Download the official NeurIPS 2026 Overleaf template here:

https://www.overleaf.com/latex/templates/formatting-instructions-for-neurips-2026/bjdwqfdkyftc

The template page is authored by the NeurIPS 2026 Program Chairs and lists the workshop options:

```tex
\usepackage[sglblindworkshop]{neurips_2026}
\usepackage[dblblindworkshop]{neurips_2026}
```

For the local project here, place the downloaded `neurips_2026.sty` in this directory:

```text
paper/neurips_latex/neurips_2026.sty
```

Then compile:

```sh
cd paper/neurips_latex
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

The current `main.tex` uses `dblblindworkshop` by default. If the target workshop is single blind, change it to `sglblindworkshop`.

`workshoptitle` is currently a placeholder and should be replaced once the exact NeurIPS workshop is chosen.
