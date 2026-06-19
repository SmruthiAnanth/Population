from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


def assert_non_empty(df: pd.DataFrame, label: str) -> None:
    assert isinstance(df, pd.DataFrame), f"{label} is not a DataFrame"
    assert len(df) > 0, f"{label} is empty"


def assert_required_columns(df: pd.DataFrame, columns: Iterable[str], label: str) -> None:
    missing = [c for c in columns if c not in df.columns]
    assert not missing, f"{label} missing required columns: {missing}"


def assert_not_too_many_missing(df: pd.DataFrame, column: str, min_non_missing_share: float, label: str) -> None:
    assert column in df.columns, f"{label} missing column: {column}"
    share = df[column].notna().mean()
    assert share >= min_non_missing_share, (
        f"{label}.{column} non-missing share {share:.3f} < {min_non_missing_share:.3f}"
    )


def assert_no_duplicates(df: pd.DataFrame, keys: list[str], label: str) -> None:
    assert_required_columns(df, keys, label)
    dup = df.duplicated(keys).sum()
    assert dup == 0, f"{label} has {dup} duplicate rows on keys: {keys}"


def assert_exported(path: Path) -> None:
    assert path.exists(), f"Expected export not found: {path}"


def merge_diagnostics(
    left: pd.DataFrame,
    right: pd.DataFrame,
    left_on: list[str],
    right_on: list[str],
    how: str = "left",
) -> dict:
    before = len(left)
    merged = left.merge(right, left_on=left_on, right_on=right_on, how=how, indicator=True)
    after = len(merged)

    left_only = int((merged["_merge"] == "left_only").sum())
    both = int((merged["_merge"] == "both").sum())
    right_only = int((merged["_merge"] == "right_only").sum())

    return {
        "rows_before": before,
        "rows_after": after,
        "rows_lost": before - both,
        "rows_lost_pct": ((before - both) / before * 100.0) if before else 0.0,
        "matched": both,
        "left_only": left_only,
        "right_only": right_only,
    }
