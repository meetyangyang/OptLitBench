from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from scipy.stats import zscore
from sklearn.decomposition import NMF
from sklearn.metrics.pairwise import cosine_similarity

from src.temporal_analysis import build_vectorizer


def _normalize_distribution(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    values = np.clip(values, 0.0, None)
    total = values.sum()
    if total <= 0:
        return np.ones_like(values) / len(values)
    return values / total


def fit_global_topics(
    records_df: pd.DataFrame,
    config: dict[str, Any],
) -> dict[str, Any]:
    n_topics = config["global_topics"]["n_topics"]
    project_cfg = config["project"]
    nmf_cfg = config["nmf"]

    vectorizer = build_vectorizer(config)
    doc_term = vectorizer.fit_transform(records_df["abstract"].tolist())
    feature_names = vectorizer.get_feature_names_out()

    model = NMF(
        n_components=n_topics,
        init=nmf_cfg["init"],
        max_iter=nmf_cfg["max_iter"],
        solver=nmf_cfg["solver"],
        random_state=project_cfg["random_state"],
    )
    doc_topic = model.fit_transform(doc_term)

    # Topic labels from top words.
    top_words = 8
    topic_labels: list[str] = []
    topic_rows: list[dict[str, Any]] = []
    for topic_idx, weights in enumerate(model.components_):
        top_idx = np.argsort(weights)[::-1][:top_words]
        words = [feature_names[i] for i in top_idx]
        topic_labels.append(", ".join(words[:4]))
        for rank, word_idx in enumerate(top_idx, start=1):
            topic_rows.append(
                {
                    "topic_id": topic_idx,
                    "rank": rank,
                    "word": feature_names[word_idx],
                    "weight": float(weights[word_idx]),
                }
            )

    doc_topic_df = pd.DataFrame(
        doc_topic,
        columns=[f"global_topic_{idx}" for idx in range(n_topics)],
    )
    doc_topic_df["file_path"] = records_df["file_path"].values
    doc_topic_df["journal"] = records_df["journal"].values
    doc_topic_df["year"] = records_df["year"].values

    return {
        "model": model,
        "vectorizer": vectorizer,
        "doc_topic_df": doc_topic_df,
        "topic_words_df": pd.DataFrame(topic_rows),
        "topic_labels": topic_labels,
    }


def journal_topic_profiles(doc_topic_df: pd.DataFrame) -> pd.DataFrame:
    topic_cols = [col for col in doc_topic_df.columns if col.startswith("global_topic_")]
    profiles = doc_topic_df.groupby("journal")[topic_cols].mean()
    normalized = profiles.div(profiles.sum(axis=1), axis=0).fillna(0.0)
    normalized.columns = [f"T{idx}" for idx in range(len(topic_cols))]
    return normalized


def compute_similarity_matrices(profiles: pd.DataFrame) -> dict[str, pd.DataFrame]:
    values = profiles.to_numpy(dtype=float)
    cosine = cosine_similarity(values)
    jsd = np.zeros((len(profiles), len(profiles)))
    for i in range(len(profiles)):
        for j in range(len(profiles)):
            jsd[i, j] = jensenshannon(values[i], values[j], base=2.0) ** 2

    index = profiles.index.tolist()
    return {
        "cosine": pd.DataFrame(cosine, index=index, columns=index),
        "jsd": pd.DataFrame(jsd, index=index, columns=index),
    }


def compute_specialization_index(profiles: pd.DataFrame) -> pd.Series:
    global_profile = _normalize_distribution(profiles.mean(axis=0).to_numpy())
    scores: dict[str, float] = {}
    for journal, row in profiles.iterrows():
        journal_profile = _normalize_distribution(row.to_numpy())
        mask = (global_profile > 0) & (journal_profile > 0)
        kl = np.sum(journal_profile[mask] * np.log2(journal_profile[mask] / global_profile[mask]))
        scores[journal] = float(kl)
    return pd.Series(scores, name="specialization_kl").sort_values(ascending=False)


def identify_common_and_distinctive_topics(
    profiles: pd.DataFrame,
    topic_labels: list[str],
    zscore_threshold: float,
    common_threshold: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    global_mean = profiles.mean(axis=0)
    prevalence_rows: list[dict[str, Any]] = []
    for topic_col in profiles.columns:
        topic_idx = int(topic_col.replace("T", ""))
        label = topic_labels[topic_idx] if topic_idx < len(topic_labels) else topic_col
        values = profiles[topic_col]
        z_vals = zscore(values.to_numpy(dtype=float))
        for journal, prevalence in values.items():
            prevalence_rows.append(
                {
                    "journal": journal,
                    "topic": topic_col,
                    "topic_label": label,
                    "prevalence": float(prevalence),
                    "global_mean": float(global_mean[topic_col]),
                    "zscore": float(z_vals[profiles.index.get_loc(journal)]),
                }
            )

    prevalence_df = pd.DataFrame(prevalence_rows)
    min_prevalence = profiles.min(axis=0)
    common_topics = min_prevalence[min_prevalence >= common_threshold].index.tolist()
    distinctive_df = prevalence_df[prevalence_df["zscore"] >= zscore_threshold].copy()
    distinctive_df = distinctive_df.sort_values(["journal", "zscore"], ascending=[True, False])

    common_df = prevalence_df[prevalence_df["topic"].isin(common_topics)].copy()
    common_df = common_df.sort_values(["topic", "prevalence"], ascending=[True, False])
    return common_df, distinctive_df


def compute_temporal_divergence(
    doc_topic_df: pd.DataFrame,
    window_years: int = 5,
) -> pd.DataFrame:
    topic_cols = [col for col in doc_topic_df.columns if col.startswith("global_topic_")]
    valid = doc_topic_df.dropna(subset=["year"]).copy()
    valid["year"] = valid["year"].astype(int)
    valid = valid.sort_values("year")

    rows: list[dict[str, Any]] = []
    for journal, journal_df in valid.groupby("journal"):
        years = sorted(journal_df["year"].unique())
        if len(years) < window_years * 2:
            continue
        mid = len(years) // 2
        early_years = set(years[:mid])
        late_years = set(years[mid:])
        early = journal_df[journal_df["year"].isin(early_years)][topic_cols].mean()
        late = journal_df[journal_df["year"].isin(late_years)][topic_cols].mean()
        divergence = float(jensenshannon(_normalize_distribution(early), _normalize_distribution(late), base=2.0) ** 2)
        rows.append(
            {
                "journal": journal,
                "early_period": f"{min(early_years)}-{max(early_years)}",
                "late_period": f"{min(late_years)}-{max(late_years)}",
                "temporal_jsd": divergence,
            }
        )
    return pd.DataFrame(rows).sort_values("temporal_jsd", ascending=False)


def build_journal_recommendation_table(profiles: pd.DataFrame, topic_labels: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for journal, row in profiles.iterrows():
        top_topics = row.sort_values(ascending=False).head(5)
        rows.append(
            {
                "journal": journal,
                "top_topics": "; ".join(
                    f"{topic} ({topic_labels[int(topic[1:])]}): {value:.3f}"
                    for topic, value in top_topics.items()
                ),
                "specialization_hint": "broad" if row.max() < 0.15 else "focused",
            }
        )
    return pd.DataFrame(rows)
