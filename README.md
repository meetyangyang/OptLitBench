# OptLitBench

**OptLitBench: A Reproducible Benchmark for Temporal Topic Mining and Cross-Journal Analytics on Optimization Literature**

Authors: **Yang Yang** (corresponding), **Ren Bo** — Criminal Investigation Police University of China (CIPUC), Shenyang, China

Target venue: [IEEE ICDM 2026 Applied Track](http://icdm2026.neu.edu.cn/CallforAppliedTrack/list.htm)

## Overview

OptLitBench provides:
- **37,664** abstract records from **18** optimization journals (1967–2019)
- Reproducible **TF-IDF + NMF** baseline topic modeling
- **Temporal analytics** (year/month topic prevalence, 300-DPI heatmaps)
- **Cross-journal metrics** (cosine/JSD, KL specialization, distinctive z-scores, temporal JSD)
- **Applications**: journal recommendation and reviewer–manuscript matching

## Repository Structure

```
OptLitBench/
├── Data_Abstract/          # OptLitBench corpus (see DATA_README.md)
├── config/                 # YAML experiment configs
├── src/                    # Python pipeline
├── results/                # Precomputed baseline & temporal results
├── paper/icdm2026/         # ICDM 2026 paper PDF only (LaTeX stays local)
├── scripts/                # Paper build + GitHub upload helpers
├── requirements.txt
└── requirements-lock.txt
```

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Baseline NMF topic analysis (18 journals)
python -m src.run_baseline

# Temporal evolution + cross-journal analytics
python -m src.run_temporal_analysis

# Journal recommendation demo
python -m src.match_manuscript --abstract "Your manuscript abstract here..."
```

## Reproduce paper results

| Paper artifact | Command / location |
|----------------|-------------------|
| Table I, per-journal topics | `python -m src.run_baseline` → `results/baseline/` |
| Figs 1–9, cross-journal tables | `python -m src.run_temporal_analysis` → `results/temporal/` |
| Journal recommendation (Sec. VI) | `python -m src.match_manuscript --abstract "..."` |

## Paper (local authoring vs GitHub)

**On GitHub** the repository only includes the compiled PDF:

- `paper/icdm2026/OptLitBench_ICDM2026.pdf`

**LaTeX sources, figures, and Overleaf ZIP stay local** (ignored by `.gitignore`):

- `paper/icdm2026/overleaf_package/` — edit `main.tex` here or import the generated ZIP into Overleaf
- `paper/icdm2026/OptLitBench_ICDM2026_overleaf.zip` — created locally, not pushed

Build/update the release PDF before pushing to GitHub:

```powershell
.\scripts\build_paper.ps1
```

This script syncs figures from `results/temporal/figures/`, compiles PDF when `pdflatex`/`latexmk` is available, writes `paper/icdm2026/OptLitBench_ICDM2026.pdf`, and refreshes the Overleaf ZIP. If LaTeX is not installed, compile on Overleaf and save the PDF to that path manually.

Helper scripts:

```powershell
.\scripts\prepare_paper_figures.ps1   # sync figures only
.\scripts\package_overleaf.ps1        # rebuild Overleaf ZIP only
.\scripts\sanitize_result_paths.py    # rewrite absolute paths in results/*.csv
.\scripts\upload_to_github.ps1        # push repository (PDF + code/data)
```

## Citation

If you use OptLitBench, please cite:

```bibtex
@inproceedings{yang2026optlitbench,
  author    = {Yang, Yang and Ren, Bo},
  title     = {OptLitBench: A Reproducible Benchmark for Temporal Topic Mining and Cross-Journal Analytics on Optimization Literature},
  booktitle = {IEEE International Conference on Data Mining (ICDM)},
  year      = {2026},
  note      = {Applied Track, under review}
}
```

## License

- **Code** (Python pipeline, scripts, configs): [MIT License](LICENSE)
- **Data** (`Data_Abstract/` abstracts): see [DATA_README.md](DATA_README.md) — research/benchmark use only; publisher terms still apply

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting and dependency audit guidance.

## Contact

Corresponding author: Yang Yang, Criminal Investigation Police University of China.

GitHub: https://github.com/meetyangyang/OptLitBench
