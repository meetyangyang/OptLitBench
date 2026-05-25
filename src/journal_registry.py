from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class JournalSpec:
    name: str
    path: Path


def discover_journals(data_dir: Path, database_journals: list[str]) -> list[JournalSpec]:
    database_names = set(database_journals)
    journals: list[JournalSpec] = []

    for entry in sorted(data_dir.iterdir()):
        if not entry.is_dir():
            continue

        if entry.name in database_names:
            for sub_entry in sorted(entry.iterdir()):
                if sub_entry.is_dir():
                    journals.append(JournalSpec(name=sub_entry.name, path=sub_entry))
        else:
            journals.append(JournalSpec(name=entry.name, path=entry))

    # Stable ordering for reproducible reports.
    return sorted(journals, key=lambda item: item.name.lower())


def safe_journal_slug(journal_name: str) -> str:
    slug = "".join(ch if ch.isalnum() else "_" for ch in journal_name.lower())
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_")
