from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


def _find_project_root(start: Path | None = None) -> Path:
    # Prefer explicit override for reproducible CLI or CI usage.
    env_root = os.getenv("PROJECT_ROOT", "").strip()
    if env_root:
        root = Path(env_root).expanduser().resolve()
        if root.exists():
            return root

    here = (start or Path.cwd()).resolve()
    markers = [
        "1 Speeches",
        "2 MEP List",
        "3 Wikipedia",
        "4 LDA Topic Analysis",
        "5 LLM Wikipedia analysis",
        "6 Country level variables",
        "7 Final Analysis",
    ]

    for candidate in [here, *here.parents]:
        if all((candidate / marker).exists() for marker in markers):
            return candidate

    # Safe fallback for interactive execution.
    return here


PROJECT_ROOT = _find_project_root()

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

OUTPUTS_DIR = PROJECT_ROOT / "outputs"
TABLES_DIR = OUTPUTS_DIR / "tables"
FIGURES_DIR = OUTPUTS_DIR / "figures"


def ensure_directories(paths: Iterable[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def ensure_default_directories() -> None:
    ensure_directories(
        [
            DATA_DIR,
            RAW_DATA_DIR,
            INTERIM_DATA_DIR,
            PROCESSED_DATA_DIR,
            OUTPUTS_DIR,
            TABLES_DIR,
            FIGURES_DIR,
        ]
    )
