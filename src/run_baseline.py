from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.abstract_parser import load_journal_abstracts
from src.journal_registry import discover_journals, safe_journal_slug
from src.nmf_topic_model import fit_nmf_topics, format_topic_summary


def load_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def run_baseline(config_path: Path, project_root: Path) -> pd.DataFrame:
    config = load_config(config_path)
    data_dir = project_root / config["project"]["data_dir"]
    results_root = project_root / config["project"]["results_dir"]
    results_root.mkdir(parents=True, exist_ok=True)

    journals = discover_journals(
        data_dir=data_dir,
        database_journals=config["journals"]["database_journals"],
    )

    summary_rows: list[dict[str, Any]] = []
    run_meta = {
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "config_path": str(config_path),
        "project_root": str(project_root),
        "journal_count": len(journals),
    }
    (results_root / "run_metadata.json").write_text(
        json.dumps(run_meta, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    for journal in journals:
        print(f"[INFO] Processing journal: {journal.name}")
        records = load_journal_abstracts(journal.path, journal.name)
        n_docs = len(records)

        journal_slug = safe_journal_slug(journal.name)
        journal_result_dir = results_root / journal_slug
        journal_result_dir.mkdir(parents=True, exist_ok=True)

        if n_docs < config["quality"]["min_documents"]:
            status = "skipped_too_few_documents"
            summary_rows.append(
                {
                    "journal": journal.name,
                    "status": status,
                    "n_documents": n_docs,
                    "n_topics": None,
                    "n_vocabulary": None,
                    "reconstruction_error": None,
                    "result_dir": str(journal_result_dir),
                }
            )
            print(f"[WARN] Skipped {journal.name}: only {n_docs} documents")
            continue

        documents = [record.abstract for record in records]
        try:
            fit_result = fit_nmf_topics(documents, config)
        except ValueError as exc:
            status = "failed_vectorization"
            summary_rows.append(
                {
                    "journal": journal.name,
                    "status": status,
                    "n_documents": n_docs,
                    "n_topics": None,
                    "n_vocabulary": None,
                    "reconstruction_error": None,
                    "result_dir": str(journal_result_dir),
                    "error": str(exc),
                }
            )
            print(f"[ERROR] Failed {journal.name}: {exc}")
            continue

        if fit_result["n_vocabulary"] < config["quality"]["min_vocabulary"]:
            status = "skipped_too_few_terms"
            summary_rows.append(
                {
                    "journal": journal.name,
                    "status": status,
                    "n_documents": n_docs,
                    "n_topics": fit_result["n_topics"],
                    "n_vocabulary": fit_result["n_vocabulary"],
                    "reconstruction_error": fit_result["reconstruction_error"],
                    "result_dir": str(journal_result_dir),
                }
            )
            print(
                f"[WARN] Skipped {journal.name}: vocabulary size "
                f"{fit_result['n_vocabulary']} is too small"
            )
            continue

        topics_df = fit_result["topics_df"]
        topics_df.to_csv(journal_result_dir / "topic_words.csv", index=False, encoding="utf-8-sig")

        summary_lines = format_topic_summary(topics_df, top_n=10)
        (journal_result_dir / "topic_summary.txt").write_text(
            "\n".join(summary_lines) + "\n",
            encoding="utf-8",
        )

        doc_topic_df = pd.DataFrame(
            fit_result["doc_topic_matrix"],
            columns=[f"topic_{idx}" for idx in range(fit_result["n_topics"])],
        )
        doc_topic_df.insert(0, "title", [record.title for record in records])
        doc_topic_df.insert(0, "file_path", [record.file_path for record in records])
        doc_topic_df.to_csv(
            journal_result_dir / "document_topic_weights.csv",
            index=False,
            encoding="utf-8-sig",
        )

        metrics = {
            "journal": journal.name,
            "status": "success",
            "n_documents": fit_result["n_documents"],
            "n_topics": fit_result["n_topics"],
            "n_vocabulary": fit_result["n_vocabulary"],
            "reconstruction_error": fit_result["reconstruction_error"],
            "top_words_per_topic": config["topics"]["top_words"],
        }
        (journal_result_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        summary_rows.append(
            {
                "journal": journal.name,
                "status": "success",
                "n_documents": metrics["n_documents"],
                "n_topics": metrics["n_topics"],
                "n_vocabulary": metrics["n_vocabulary"],
                "reconstruction_error": metrics["reconstruction_error"],
                "result_dir": str(journal_result_dir),
            }
        )
        print(
            f"[OK] {journal.name}: docs={metrics['n_documents']}, "
            f"topics={metrics['n_topics']}, vocab={metrics['n_vocabulary']}"
        )

    summary_df = pd.DataFrame(summary_rows).sort_values("journal")
    summary_df.to_csv(results_root / "summary.csv", index=False, encoding="utf-8-sig")
    return summary_df


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    config_path = project_root / "config" / "baseline_config.yaml"
    summary_df = run_baseline(config_path=config_path, project_root=project_root)
    success_count = (summary_df["status"] == "success").sum()
    print(f"[DONE] Completed baseline for {success_count}/{len(summary_df)} journals")


if __name__ == "__main__":
    main()
