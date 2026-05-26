from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.abstract_parser import load_journal_abstracts
from src.cross_journal_analysis import (
    build_journal_recommendation_table,
    compute_similarity_matrices,
    compute_specialization_index,
    compute_temporal_divergence,
    fit_global_topics,
    identify_common_and_distinctive_topics,
    journal_topic_profiles,
)
from src.journal_registry import discover_journals, safe_journal_slug
from src.temporal_analysis import (
    aggregate_topic_prevalence,
    build_topic_labels,
    smooth_yearly_matrix,
)
from src.visualization import (
    save_distinctive_heatmap,
    save_similarity_clustermap,
    save_specialization_barplot,
    save_temporal_divergence_barplot,
    save_topic_month_heatmap,
    save_topic_year_heatmap,
    save_topic_year_lineplot,
)


def load_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def records_to_dataframe(records: list[Any]) -> pd.DataFrame:
    rows = [asdict(record) for record in records]
    return pd.DataFrame(rows)


def run_temporal_analysis(config_path: Path, project_root: Path) -> None:
    config = load_config(config_path)
    data_dir = project_root / config["project"]["data_dir"]
    baseline_dir = project_root / config["project"]["baseline_results_dir"]
    results_dir = project_root / config["project"]["results_dir"]
    figures_dir = results_dir / "figures"
    per_journal_dir = figures_dir / "journals"
    cross_dir = figures_dir / "cross_journal"
    per_journal_dir.mkdir(parents=True, exist_ok=True)
    cross_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "by_journal").mkdir(parents=True, exist_ok=True)

    journals = discover_journals(
        data_dir=data_dir,
        database_journals=config["journals"]["database_journals"],
    )

    all_records: list[Any] = []
    journal_manifest: list[dict[str, Any]] = []

    for journal in journals:
        records = load_journal_abstracts(journal.path, journal.name, repo_root=project_root)
        all_records.extend(records)
        journal_slug = safe_journal_slug(journal.name)
        doc_topics = pd.read_csv(baseline_dir / journal_slug / "document_topic_weights.csv")
        records_df = records_to_dataframe(records)
        topic_labels = build_topic_labels(
            baseline_dir / journal_slug / "topic_words.csv",
            top_n=config["temporal"]["top_words_label"],
        )

        yearly = aggregate_topic_prevalence(
            doc_topics=doc_topics,
            records=records_df,
            time_col="year",
            min_docs=config["temporal"]["min_docs_per_year"],
        )
        yearly.to_csv(results_dir / "by_journal" / f"{journal_slug}_yearly_prevalence.csv", index=False)

        if not yearly.empty:
            yearly_matrix = yearly.pivot(index="period", columns="topic", values="prevalence").fillna(0.0)
            yearly_matrix = yearly_matrix.sort_index()
            yearly_matrix = smooth_yearly_matrix(
                yearly_matrix,
                window=config["temporal"]["smooth_window_years"],
            )
            smoothed = yearly_matrix.reset_index().melt(id_vars="period", var_name="topic", value_name="prevalence")

            save_topic_year_heatmap(
                prevalence_df=yearly,
                topic_labels=topic_labels,
                output_path=per_journal_dir / f"{journal_slug}_topic_year_heatmap.png",
                title=f"{journal.name} — Topic Prevalence by Year",
                config=config,
            )
            save_topic_year_lineplot(
                prevalence_df=smoothed,
                topic_labels=topic_labels,
                output_path=per_journal_dir / f"{journal_slug}_topic_evolution_lines.png",
                title=f"{journal.name} — Topic Evolution Curves (Smoothed)",
                config=config,
            )

        monthly_records = records_df.dropna(subset=["year_month"])
        if not monthly_records.empty:
            monthly = aggregate_topic_prevalence(
                doc_topics=doc_topics,
                records=monthly_records,
                time_col="year_month",
                min_docs=config["temporal"]["min_docs_per_month"],
            )
            if len(monthly["period"].unique()) >= 6:
                monthly.to_csv(
                    results_dir / "by_journal" / f"{journal_slug}_monthly_prevalence.csv",
                    index=False,
                )
                save_topic_month_heatmap(
                    prevalence_df=monthly,
                    topic_labels=topic_labels,
                    output_path=per_journal_dir / f"{journal_slug}_topic_month_heatmap.png",
                    title=f"{journal.name} — Topic Prevalence by Year-Month",
                    config=config,
                )

        journal_manifest.append(
            {
                "journal": journal.name,
                "journal_slug": journal_slug,
                "n_records": len(records),
                "n_with_year": int(records_df["year"].notna().sum()),
                "n_with_month": int(records_df["year_month"].notna().sum()),
                "year_range": [
                    int(records_df["year"].min()),
                    int(records_df["year"].max()),
                ]
                if records_df["year"].notna().any()
                else None,
            }
        )

    (results_dir / "by_journal").mkdir(parents=True, exist_ok=True)
    pd.DataFrame(journal_manifest).to_csv(results_dir / "journal_manifest.csv", index=False, encoding="utf-8-sig")

    records_df = records_to_dataframe(all_records)
    records_df = records_df.dropna(subset=["year"])
    global_fit = fit_global_topics(records_df, config)
    global_fit["topic_words_df"].to_csv(results_dir / "global_topic_words.csv", index=False, encoding="utf-8-sig")
    global_fit["doc_topic_df"].to_csv(results_dir / "global_document_topics.csv", index=False, encoding="utf-8-sig")

    profiles = journal_topic_profiles(global_fit["doc_topic_df"])
    profiles.to_csv(results_dir / "journal_topic_profiles.csv", encoding="utf-8-sig")

    similarities = compute_similarity_matrices(profiles)
    similarities["cosine"].to_csv(results_dir / "journal_cosine_similarity.csv", encoding="utf-8-sig")
    similarities["jsd"].to_csv(results_dir / "journal_jsd_distance.csv", encoding="utf-8-sig")

    specialization = compute_specialization_index(profiles)
    specialization.to_csv(results_dir / "journal_specialization_index.csv", encoding="utf-8-sig", header=True)

    common_df, distinctive_df = identify_common_and_distinctive_topics(
        profiles=profiles,
        topic_labels=global_fit["topic_labels"],
        zscore_threshold=config["metrics"]["distinctive_zscore"],
        common_threshold=config["metrics"]["common_prevalence_threshold"],
    )
    common_df.to_csv(results_dir / "common_topics.csv", index=False, encoding="utf-8-sig")
    distinctive_df.to_csv(results_dir / "distinctive_topics.csv", index=False, encoding="utf-8-sig")

    temporal_div = compute_temporal_divergence(global_fit["doc_topic_df"])
    temporal_div.to_csv(results_dir / "journal_temporal_divergence.csv", index=False, encoding="utf-8-sig")

    recommendation_df = build_journal_recommendation_table(profiles, global_fit["topic_labels"])
    recommendation_df.to_csv(results_dir / "journal_recommendation_profiles.csv", index=False, encoding="utf-8-sig")

    save_similarity_clustermap(
        similarity_df=similarities["cosine"],
        output_path=cross_dir / "journal_cosine_clustermap.png",
        title="Cross-Journal Topic Similarity (Cosine)",
        config=config,
        metric_label="Cosine similarity",
    )
    save_similarity_clustermap(
        similarity_df=1.0 - similarities["jsd"],
        output_path=cross_dir / "journal_jsd_clustermap.png",
        title="Cross-Journal Topic Similarity (1 - JSD)",
        config=config,
        metric_label="1 - JSD",
    )
    save_specialization_barplot(
        specialization=specialization,
        output_path=cross_dir / "journal_specialization_index.png",
        title="Journal Specialization Index",
        config=config,
    )
    save_distinctive_heatmap(
        distinctive_df=distinctive_df,
        output_path=cross_dir / "distinctive_topics_heatmap.png",
        title="Distinctive Topics by Journal (z-score)",
        config=config,
    )
    save_temporal_divergence_barplot(
        divergence_df=temporal_div,
        output_path=cross_dir / "journal_temporal_divergence.png",
        title="Temporal Topic Shift (Early vs Late Period)",
        config=config,
    )

    profiles_for_plot = profiles.copy()
    profiles_for_plot.columns = global_fit["topic_labels"]
    save_topic_year_heatmap(
        prevalence_df=_profiles_to_prevalence(profiles_for_plot),
        topic_labels={col: col for col in profiles_for_plot.columns},
        output_path=cross_dir / "journal_topic_profile_heatmap.png",
        title="Journal Topic Profiles (Global Topics)",
        config=config,
        xlabel="Journal",
        ylabel="Topic",
    )

    analysis_report = {
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "visualization_recommendation": {
            "primary": "Year x Topic heatmap for temporal evolution",
            "secondary": "Smoothed line plot for topic trajectories",
            "monthly": "Year-Month heatmap when month metadata exists (Springer journals)",
            "cross_journal": "Cosine/JSD clustermap + specialization index + distinctive topic z-scores",
        },
        "metrics_used": [
            "Normalized topic prevalence by year/month",
            "Cosine similarity between journal topic profiles",
            "Jensen-Shannon divergence (JSD)",
            "KL specialization index relative to global profile",
            "Distinctive topic z-score",
            "Temporal JSD between early and late periods",
        ],
        "journal_count": len(journals),
        "documents_with_year": int(records_df.shape[0]),
    }
    (results_dir / "analysis_report.json").write_text(
        json.dumps(analysis_report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[DONE] Temporal and cross-journal analysis saved to {results_dir}")


def _profiles_to_prevalence(profiles: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for journal, row in profiles.iterrows():
        for topic, value in row.items():
            rows.append({"period": journal, "topic": topic, "prevalence": float(value)})
    return pd.DataFrame(rows)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    config_path = project_root / "config" / "temporal_config.yaml"
    run_temporal_analysis(config_path=config_path, project_root=project_root)


if __name__ == "__main__":
    main()
