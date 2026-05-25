# ICDM 2026 Applied Track — Submission Checklist

Conference: [IEEE ICDM 2026](http://icdm2026.neu.edu.cn/main.htm)  
Track: **Applied Track** — select under "Track" at submission  
Call: [Call for Applied Track Papers](http://icdm2026.neu.edu.cn/CallforAppliedTrack/list.htm)

## Key Dates (AoE)

| Milestone | Date |
|---|---|
| Paper submission | **June 6, 2026** |
| Notification | August 16, 2026 |
| Camera ready | September 16, 2026 |

## Format Requirements

- IEEE 2-column format, **≤ 10 pages** including references and appendices
- Template: https://www.ieee.org/conferences/publishing/templates.html
- **Single-blind** review (author names allowed in manuscript)
- Submit via: https://wi-lab.com/cyberchair/2026/icdm26/scripts/submit.php?subarea=DM

## Topic Alignment (copy to cover letter / submission form)

Primary ICDM topics:
1. **Heterogeneous Data Mining** — text abstracts + temporal bibliographic metadata
2. **Modeling, Visualization & Recommendations** — topic profiles, heatmaps, journal recommendation
3. **Novel Applications** — optimization / engineering research literature analytics

Applied Track bullets:
- **New dataset/benchmark**: OptLitBench (37,664 abstracts, 18 journals)
- **Comprehensive experimental analysis**: NMF baseline + cross-journal metrics + temporal evolution
- **Deployed academic system**: reproducible Python pipeline with released artifacts

## Reproducibility (required checklist at submission)

Prepare responses for ICDM reproducibility checklist:

- [ ] Algorithm pseudocode / pipeline description (Section IV in `main.tex`)
- [ ] Experimental methodology and hyperparameters (`config/*.yaml`)
- [ ] Public dataset description + access instructions (OptLitBench in repo)
- [ ] Code availability statement (GitHub URL — add before submission)
- [ ] Locked dependencies (`requirements-lock.txt`)
- [ ] Evaluation tables and figures (`results/`)

## Pre-Submission Tasks

1. Fill author names/affiliations in `main.tex`
2. Compile PDF: `pdflatex main && bibtex main && pdflatex main && pdflatex main`
3. Verify **page count ≤ 10**
4. Copy 4–6 figures from `results/temporal/figures/` into `paper/icdm2026/figures/` if moving repo
5. Add GitHub repository URL to abstract/footnote
6. Write reproducibility checklist answers
7. Contact for Applied Track queries: icdm2026.applied.chairs@gmail.com

## Suggested Paper Framing (1 sentence)

> We release OptLitBench, a reproducible benchmark and analytics pipeline for temporal topic mining on 37K optimization abstracts, with cross-journal metrics and applications to journal recommendation and reviewer matching.

## ARS Integrity Reminders

- All statistics in `main.tex` trace to CSV/JSON in `results/`
- Do not add citations without verifying bibliographic metadata
- Position NMF as baseline; avoid overstating novelty vs LDA/BERTopic
- Acknowledge limitations (English-only, metadata parsing, no editorial ground truth)
