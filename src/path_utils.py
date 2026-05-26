from __future__ import annotations

from pathlib import Path


def to_repo_relative(path: Path | str, repo_root: Path) -> str:
    candidate = Path(path)
    try:
        return candidate.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        normalized = str(path).replace("\\", "/")
        for anchor in ("Data_Abstract/", "results/", "config/", "src/"):
            if anchor in normalized:
                return anchor + normalized.split(anchor, 1)[1]
        return normalized
