"""Demo: journal recommendation and reviewer matching from abstract text."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def build_vectorizer(config: dict) -> TfidfVectorizer:
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


def load_artifacts(project_root: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    temporal_dir = project_root / "results" / "temporal"
    config_path = project_root / "config" / "temporal_config.yaml"
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    doc_topics = pd.read_csv(temporal_dir / "global_document_topics.csv")
    profiles = pd.read_csv(temporal_dir / "journal_topic_profiles.csv", index_col=0)
    topic_words = pd.read_csv(temporal_dir / "global_topic_words.csv")
    return doc_topics, profiles, topic_words, config


def refit_global_model(project_root: Path, config: dict) -> tuple[TfidfVectorizer, NMF, list[str]]:
    from src.abstract_parser import load_journal_abstracts
    from src.journal_registry import discover_journals

    data_dir = project_root / config["project"]["data_dir"]
    journals = discover_journals(data_dir, config["journals"]["database_journals"])
    records = []
    for journal in journals:
        records.extend(load_journal_abstracts(journal.path, journal.name))

    df = pd.DataFrame({"abstract": [r.abstract for r in records], "file_path": [r.file_path for r in records]})
    vectorizer = build_vectorizer(config)
    doc_term = vectorizer.fit_transform(df["abstract"].tolist())
    n_topics = config["global_topics"]["n_topics"]
    model = NMF(
        n_components=n_topics,
        init=config["nmf"]["init"],
        max_iter=config["nmf"]["max_iter"],
        solver=config["nmf"]["solver"],
        random_state=config["project"]["random_state"],
    )
    model.fit(doc_term)
    return vectorizer, model, df["file_path"].tolist()


def topic_vector_from_abstract(
    abstract: str,
    vectorizer: TfidfVectorizer,
    model: NMF,
) -> np.ndarray:
    vec = vectorizer.transform([abstract])
    return model.transform(vec)[0]


def recommend_journals(
    abstract: str,
    vectorizer: TfidfVectorizer,
    model: NMF,
    profiles: pd.DataFrame,
    top_k: int = 5,
) -> pd.DataFrame:
    query = topic_vector_from_abstract(abstract, vectorizer, model)
    profile_cols = profiles.columns.tolist()
    sims = cosine_similarity(query.reshape(1, -1), profiles.to_numpy())[0]
    ranked = (
        pd.DataFrame({"journal": profiles.index, "cosine_similarity": sims})
        .sort_values("cosine_similarity", ascending=False)
        .head(top_k)
    )
    return ranked


def match_reviewers(
    abstract: str,
    vectorizer: TfidfVectorizer,
    model: NMF,
    doc_topics: pd.DataFrame,
    journal: str | None = None,
    top_k: int = 10,
) -> pd.DataFrame:
    query = topic_vector_from_abstract(abstract, vectorizer, model)
    topic_cols = [c for c in doc_topics.columns if c.startswith("global_topic_")]
    candidates = doc_topics.copy()
    if journal:
        candidates = candidates[candidates["journal"] == journal]

    matrix = candidates[topic_cols].to_numpy()
    sims = cosine_similarity(query.reshape(1, -1), matrix)[0]
    candidates = candidates.assign(similarity=sims)
    return candidates.sort_values("similarity", ascending=False).head(top_k)[
        ["journal", "file_path", "similarity"]
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Journal recommendation and reviewer matching demo")
    parser.add_argument("--abstract", required=True, help="Manuscript abstract text")
    parser.add_argument("--journal", default=None, help="Restrict reviewer matching to one journal")
    parser.add_argument("--top-journals", type=int, default=5)
    parser.add_argument("--top-papers", type=int, default=10)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    doc_topics, profiles, _, config = load_artifacts(project_root)
    vectorizer, model, _ = refit_global_model(project_root, config)

    journal_rank = recommend_journals(args.abstract, vectorizer, model, profiles, args.top_journals)
    paper_rank = match_reviewers(
        args.abstract,
        vectorizer,
        model,
        doc_topics,
        journal=args.journal,
        top_k=args.top_papers,
    )

    output = {
        "journal_recommendations": journal_rank.to_dict(orient="records"),
        "reviewer_paper_matches": paper_rank.to_dict(orient="records"),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
