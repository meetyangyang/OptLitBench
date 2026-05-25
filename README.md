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
├── Data_Abstract/          # OptLitBench corpus (37,664 abstracts)
├── config/                 # YAML experiment configs
├── src/                    # Python pipeline
├── results/                # Precomputed baseline & temporal results
├── paper/icdm2026/         # ICDM 2026 IEEE LaTeX manuscript
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

## Paper & Overleaf

- LaTeX source: `paper/icdm2026/main.tex`
- Overleaf ZIP: `paper/icdm2026/OptLitBench_ICDM2026_overleaf.zip`
- Import the ZIP directly into [Overleaf](https://www.overleaf.com/) (New Project → Upload Project)

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

Academic research use. Abstract texts remain subject to original publisher terms.

## Contact

Corresponding author: Yang Yang, Criminal Investigation Police University of China.

GitHub: https://github.com/meetyangyang/OptLitBench
