from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer


def choose_topic_count(n_documents: int, min_topics: int, max_topics: int) -> int:
    if n_documents < 100:
        return min_topics
    estimated = round(math.sqrt(n_documents / 50))
    return max(min_topics, min(max_topics, estimated))


def build_vectorizer(config: dict[str, Any]) -> TfidfVectorizer:
    vectorizer_cfg = config["vectorizer"]
    ngram_range = tuple(vectorizer_cfg["ngram_range"])
    return TfidfVectorizer(
        max_features=vectorizer_cfg["max_features"],
        min_df=vectorizer_cfg["min_df"],
        max_df=vectorizer_cfg["max_df"],
        ngram_range=ngram_range,
        stop_words=vectorizer_cfg["stop_words"],
        token_pattern=vectorizer_cfg["token_pattern"],
        lowercase=True,
    )


def fit_nmf_topics(
    documents: list[str],
    config: dict[str, Any],
) -> dict[str, Any]:
    project_cfg = config["project"]
    topics_cfg = config["topics"]
    nmf_cfg = config["nmf"]

    vectorizer = build_vectorizer(config)
    doc_term_matrix = vectorizer.fit_transform(documents)
    feature_names = vectorizer.get_feature_names_out()

    n_topics = choose_topic_count(
        n_documents=len(documents),
        min_topics=topics_cfg["min_topics"],
        max_topics=topics_cfg["max_topics"],
    )

    model = NMF(
        n_components=n_topics,
        init=nmf_cfg["init"],
        max_iter=nmf_cfg["max_iter"],
        alpha_W=nmf_cfg["alpha_W"],
        alpha_H=nmf_cfg["alpha_H"],
        l1_ratio=nmf_cfg["l1_ratio"],
        solver=nmf_cfg["solver"],
        random_state=project_cfg["random_state"],
    )

    doc_topic_matrix = model.fit_transform(doc_term_matrix)
    topic_term_matrix = model.components_

    top_words = topics_cfg["top_words"]
    topic_rows: list[dict[str, Any]] = []
    for topic_idx, topic_weights in enumerate(topic_term_matrix):
        top_indices = np.argsort(topic_weights)[::-1][:top_words]
        for rank, word_idx in enumerate(top_indices, start=1):
            topic_rows.append(
                {
                    "topic_id": topic_idx,
                    "rank": rank,
                    "word": feature_names[word_idx],
                    "weight": float(topic_weights[word_idx]),
                }
            )

    topics_df = pd.DataFrame(topic_rows)
    reconstruction_error = float(model.reconstruction_err_)

    return {
        "vectorizer": vectorizer,
        "model": model,
        "doc_term_matrix": doc_term_matrix,
        "doc_topic_matrix": doc_topic_matrix,
        "feature_names": feature_names,
        "topics_df": topics_df,
        "n_topics": n_topics,
        "n_documents": len(documents),
        "n_vocabulary": len(feature_names),
        "reconstruction_error": reconstruction_error,
    }


def format_topic_summary(topics_df: pd.DataFrame, top_n: int = 10) -> list[str]:
    lines: list[str] = []
    for topic_id in sorted(topics_df["topic_id"].unique()):
        words = (
            topics_df[topics_df["topic_id"] == topic_id]
            .sort_values("rank")
            .head(top_n)["word"]
            .tolist()
        )
        lines.append(f"Topic {topic_id}: {', '.join(words)}")
    return lines
