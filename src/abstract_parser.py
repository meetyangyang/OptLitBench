from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.date_parser import parse_date_from_path


@dataclass(frozen=True)
class AbstractRecord:
    journal: str
    file_path: str
    title: str
    abstract: str
    year: int | None = None
    month: int | None = None
    year_month: str | None = None


def _extract_section(lines: list[str], start_label: str, end_labels: set[str]) -> str:
    start_idx = None
    for idx, line in enumerate(lines):
        if line.strip().lower() == start_label.lower():
            start_idx = idx + 1
            break

    if start_idx is None:
        return ""

    content_lines: list[str] = []
    for line in lines[start_idx:]:
        stripped = line.strip()
        if stripped.lower() in end_labels:
            break
        if stripped:
            content_lines.append(stripped)

    return " ".join(content_lines).strip()


def parse_abstract_file(path: Path, journal: str) -> AbstractRecord | None:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None

    lines = [line.strip() for line in text.splitlines()]
    non_empty = [line for line in lines if line]
    if len(non_empty) < 2:
        return None

    title = non_empty[0]
    abstract = _extract_section(lines, "Abstract", {"keywords", "key words"})
    if not abstract:
        # Fallback: use everything after the author line when Abstract marker is missing.
        abstract = " ".join(non_empty[2:]).strip()

    if len(abstract.split()) < 8:
        return None

    parsed_date = parse_date_from_path(str(path), journal_name=journal)

    return AbstractRecord(
        journal=journal,
        file_path=str(path),
        title=title,
        abstract=abstract,
        year=parsed_date.year if parsed_date else None,
        month=parsed_date.month if parsed_date else None,
        year_month=parsed_date.year_month if parsed_date else None,
    )


def load_journal_abstracts(journal_dir: Path, journal_name: str) -> list[AbstractRecord]:
    records: list[AbstractRecord] = []
    for path in sorted(journal_dir.rglob("*.txt")):
        record = parse_abstract_file(path, journal_name)
        if record is not None:
            records.append(record)
    return records
