# ICDM 2026 Applied Track — Paper Plan

Based on [Academic Research Skills](https://github.com/Imbad0202/academic-research-skills) conference-paper workflow.

## Track Decision

**Selected track:** ICDM 2026 **Applied Track** (not Research Track)

**Rationale:** Our work delivers (i) a real-world interdisciplinary benchmark on optimization literature, (ii) a deployed/reproducible analytics pipeline, (iii) comprehensive experimental analysis of NMF-based topic mining, and (iv) practical applications for journal selection and reviewer-paper matching. This aligns directly with the Applied Track call: new datasets/benchmarks, comprehensive algorithm analysis, and deployed academic analytics.

Submission portal: https://wi-lab.com/cyberchair/2026/icdm26/scripts/submit.php?subarea=DM  
Select **Applied Track** under Track.

Deadline: **June 6, 2026** (AoE)

## Primary Topic Mapping (ICDM 2026)

| ICDM topic | Our fit |
|---|---|
| **Heterogeneous Data Mining** | Text abstracts + bibliographic paths + year/month metadata |
| **Modeling, Visualization & Recommendations** | Topic modeling, temporal heatmaps, journal recommendation |
| **Novel Applications (physical sciences / engineering)** | Scientometric analysis of optimization research corpus |
| **Applied Track: New dataset/benchmark** | 37,664 abstracts, 18 journals, 1967–2019 |
| **Applied Track: Comprehensive experimental analysis** | NMF baseline, temporal evolution, cross-journal metrics |

Secondary fit: **CPS & Complex Time-Evolving Networks** (temporal topic dynamics), but not primary framing.

## Working Title

**OptLitBench: A Reproducible Benchmark for Temporal Topic Mining and Cross-Journal Analytics on Optimization Literature**

Alternative short title: *Temporal Topic Analytics and Journal Matching on 37K Optimization Abstracts*

## Core Claims (verify against repo artifacts)

1. We release **OptLitBench**, a curated benchmark of **37,664** abstract records from **18** optimization journals.
2. We provide a **reproducible pipeline** (config + code + locked dependencies) for TF-IDF + NMF topic mining.
3. We propose **cross-journal metrics** (cosine/JSD similarity, KL specialization, distinctive z-score, temporal JSD) to separate common vs. distinctive research themes.
4. We demonstrate **two applied tasks**: (a) journal recommendation for authors, (b) reviewer–manuscript matching via topic-vector similarity.
5. Temporal visualizations (year × topic heatmaps; year-month where available) reveal interpretable evolution patterns (e.g., interior-point methods, CP/MIP, structural optimization).

## Evidence Files (Material Passport)

| Artifact | Path |
|---|---|
| Baseline summary | `results/baseline/summary.csv` |
| Temporal metrics | `results/temporal/analysis_report.json` |
| Journal profiles | `results/temporal/journal_recommendation_profiles.csv` |
| Cosine similarity | `results/temporal/journal_cosine_similarity.csv` |
| Specialization index | `results/temporal/journal_specialization_index.csv` |
| Distinctive topics | `results/temporal/distinctive_topics.csv` |
| Temporal divergence | `results/temporal/journal_temporal_divergence.csv` |
| Figures | `results/temporal/figures/` |
| Config | `config/baseline_config.yaml`, `config/temporal_config.yaml` |
| Code | `src/` |

## IMRaD / IEEE Section Plan

1. **Abstract** (~150–200 words): problem, OptLitBench, method, metrics, key findings, applications.
2. **Introduction**: scientometric need in optimization; gap in reproducible cross-journal temporal benchmarks; contributions (bulleted).
3. **Related Work**: topic modeling (LDA/NMF), dynamic/scientometric text mining, journal recommendation, benchmark datasets.
4. **Problem Formulation**: document-term matrix, NMF decomposition, temporal aggregation, journal profile vectors.
5. **OptLitBench & Pipeline**: dataset statistics, parsing, date extraction, per-journal + global NMF, reproducibility.
6. **Cross-Journal Analytics Metrics**: cosine, JSD, KL specialization, distinctive z-score, temporal JSD; interpretation.
7. **Experiments**: baseline quality, temporal patterns (case journals), cross-journal clustering findings.
8. **Applications**: journal recommendation algorithm; reviewer matching algorithm; example queries.
9. **Discussion & Limitations**: English-centric preprocessing, metadata noise, single algorithm baseline, future Poisson NMF/BERTopic.
10. **Conclusion**.
11. **References** (IEEE style).

## Reproducibility Checklist (ICDM Applied Track)

- [x] Public code structure in repository
- [x] Config YAML files
- [x] `requirements.txt` + `requirements-lock.txt`
- [ ] Add `REPRODUCIBILITY.md` with one-command rerun (optional follow-up)
- [ ] Complete ICDM reproducibility checklist at submission time
- [ ] Prepare anonymized single-blind version (no author names in submitted PDF if required — Applied Track is **single-blind**, author names allowed)

## Figures for Paper (select from generated assets)

| Fig | File | Caption idea |
|---|---|---|
| 1 | `figures/cross_journal/journal_cosine_clustermap.png` | Cross-journal topic similarity |
| 2 | `figures/journals/mathematical_programming_topic_year_heatmap.png` | Temporal topic evolution (MP) |
| 3 | `figures/journals/cpaior_topic_year_heatmap.png` | CPAIOR specialization |
| 4 | `figures/cross_journal/distinctive_topics_heatmap.png` | Distinctive themes by journal |
| 5 | `figures/cross_journal/journal_specialization_index.png` | Specialization ranking |
| 6 | `figures/cross_journal/journal_temporal_divergence.png` | Early vs late topic shift |

## Writing Notes (ARS human-in-the-loop)

- Keep all numbers traceable to CSV/JSON outputs.
- Do **not** claim LLM-based topic labeling unless implemented.
- Position NMF as **baseline** with clear upgrade path (Poisson NMF, BERTopic) in future work.
- Applied Track emphasizes **utility** — foreground journal/reviewer matching and benchmark release.
