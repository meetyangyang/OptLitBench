"""Rewrite absolute paths in committed result artifacts to repo-relative paths."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.path_utils import to_repo_relative

PATH_COLUMNS = {"file_path", "result_dir", "path", "source_path", "config_path", "project_root"}


def sanitize_csv(path: Path, repo_root: Path) -> bool:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return False
        target_cols = [col for col in reader.fieldnames if col in PATH_COLUMNS]
        if not target_cols:
            return False
        rows = list(reader)

    changed = False
    for row in rows:
        for col in target_cols:
            original = row.get(col, "")
            if not original:
                continue
            updated = to_repo_relative(original, repo_root)
            normalized = str(original).replace("\\", "/")
            if updated != normalized:
                changed = True
            row[col] = updated

    if not changed:
        return False

    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return True


def sanitize_json(path: Path, repo_root: Path) -> bool:
    payload = json.loads(path.read_text(encoding="utf-8"))
    changed = False

    def walk(node):
        nonlocal changed
        if isinstance(node, dict):
            for key, value in node.items():
                if key in PATH_COLUMNS and isinstance(value, str):
                    updated = to_repo_relative(value, repo_root)
                    if updated != value:
                        node[key] = updated
                        changed = True
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(payload)
    if changed:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return changed


def main() -> None:
    repo_root = ROOT
    updated: list[str] = []
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file():
            continue
        if "Data_Abstract" in path.parts:
            continue
        if path.suffix.lower() == ".csv" and sanitize_csv(path, repo_root):
            updated.append(str(path.relative_to(repo_root).as_posix()))
        elif path.suffix.lower() == ".json" and sanitize_json(path, repo_root):
            updated.append(str(path.relative_to(repo_root).as_posix()))

    if updated:
        print(f"[OK] Sanitized {len(updated)} files")
        for item in updated[:20]:
            print(f"  - {item}")
        if len(updated) > 20:
            print(f"  ... and {len(updated) - 20} more")
    else:
        print("[OK] No path sanitization needed")


if __name__ == "__main__":
    main()
