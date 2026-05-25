from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer


PathLike = str | Path


def build_vectorizer(config: dict[str, Any]) -> TfidfVectorizer:
    vectorizer_cfg = config["vectorizer"]
    extra_stop_words = set(vectorizer_cfg.get("extra_stop_words", []))
    stop_words = set(ENGLISH_STOP_WORDS).union(extra_stop_words)
    return TfidfVectorizer(
        max_features=vectorizer_cfg["max_features"],
        min_df=vectorizer_cfg["min_df"],
        max_df=vectorizer_cfg["max_df"],
        ngram_range=tuple(vectorizer_cfg["ngram_range"]),
        stop_words=sorted(stop_words),
        token_pattern=vectorizer_cfg["token_pattern"],
        lowercase=True,
    )


def load_baseline_doc_topics(
    baseline_dir: PathLike,
    journal_slug: str,
) -> pd.DataFrame | None:
    path = Path(baseline_dir) / journal_slug / "document_topic_weights.csv"
    if not path.exists():
        return None
    return pd.read_csv(path)


def aggregate_topic_prevalence(
    doc_topics: pd.DataFrame,
    records: pd.DataFrame,
    time_col: str,
    min_docs: int,
) -> pd.DataFrame:
    topic_cols = [col for col in doc_topics.columns if col.startswith("topic_")]
    merged = doc_topics.merge(records, on="file_path", how="inner")
    merged = merged.dropna(subset=[time_col])

    grouped = merged.groupby(time_col)
    rows: list[dict[str, Any]] = []
    for period, frame in grouped:
        if len(frame) < min_docs:
            continue
        topic_mean = frame[topic_cols].mean(axis=0)
        total = topic_mean.sum()
        if total <= 0:
            continue
        normalized = topic_mean / total
        for topic_name, value in normalized.items():
            rows.append(
                {
                    "period": period,
                    "topic": topic_name,
                    "prevalence": float(value),
                    "n_docs": len(frame),
                }
            )

    return pd.DataFrame(rows)


def build_topic_labels(topic_words_path: PathLike, top_n: int = 3) -> dict[str, str]:
    path = Path(topic_words_path)
    if not path.exists():
        return {}

    df = pd.read_csv(path)
    labels: dict[str, str] = {}
    for topic_id in sorted(df["topic_id"].unique()):
        words = (
            df[df["topic_id"] == topic_id]
            .sort_values("rank")
            .head(top_n)["word"]
            .dropna()
            .astype(str)
            .tolist()
        )
        labels[f"topic_{topic_id}"] = ", ".join(words)
    return labels


def smooth_yearly_matrix(
    matrix: pd.DataFrame,
    window: int,
) -> pd.DataFrame:
    if window <= 1 or matrix.empty:
        return matrix
    smoothed = matrix.copy()
    values = matrix.to_numpy(dtype=float)
    half = window // 2
    padded = np.pad(values, ((half, half), (0, 0)), mode="edge")
    for idx in range(values.shape[0]):
        smoothed.iloc[idx, :] = padded[idx : idx + window, :].mean(axis=0)
    return smoothed
