from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_HISTORY_DIR = Path(".dift") / "history"
DEFAULT_HISTORY_FILE = "history.jsonl"


def save_history_record(
    report: Any,
    old_dataset: str,
    new_dataset: str,
    key: str | None,
    threshold: float,
    report_format: str,
    history_dir: str | None = None,
) -> Path:
    """Save one comparison history record as JSONL."""
    target_dir = Path(history_dir) if history_dir else DEFAULT_HISTORY_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    history_path = target_dir / DEFAULT_HISTORY_FILE

    record = {
        "timestamp": datetime.now(UTC).isoformat(),
        "old_dataset": old_dataset,
        "new_dataset": new_dataset,
        "key": key,
        "threshold": threshold,
        "report_format": report_format,
        "risk_level": report.summary.risk_level,
        "summary": report.summary.model_dump(),
        "schema": {
            "columns_added": report.schema_diff.columns_added,
            "columns_removed": report.schema_diff.columns_removed,
            "type_changes": len(report.schema_diff.type_changes),
        },
        "rows": {
            "added_rows": report.row_diff.added_rows,
            "removed_rows": report.row_diff.removed_rows,
            "changed_rows": report.row_diff.changed_rows,
            "unchanged_rows": report.row_diff.unchanged_rows,
        },
        "quality": {
            "null_spikes": sum(
                1 for item in report.quality_diff.null_diffs if item.is_spike
            ),
            "duplicate_spike": report.quality_diff.duplicate_diff.is_spike,
            "duplicate_severity": report.quality_diff.duplicate_diff.severity,
        },
        "numeric": {
            "drifted_columns": [
                item.column for item in report.numeric_diff if item.is_drifted
            ],
            "drifted_count": sum(1 for item in report.numeric_diff if item.is_drifted),
        },
        "categorical": {
            "shifted_columns": [
                item.column for item in report.categorical_diff if item.is_shifted
            ],
            "shifted_count": sum(
                1 for item in report.categorical_diff if item.is_shifted
            ),
        },
        "outliers": {
            "spike_columns": [
                item.column for item in report.outlier_diff if item.is_spike
            ],
            "spike_count": sum(1 for item in report.outlier_diff if item.is_spike),
        },
    }

    with history_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")

    return history_path


def load_history(history_dir: str | None = None) -> list[dict[str, Any]]:
    """Load all saved comparison history records."""
    target_dir = Path(history_dir) if history_dir else DEFAULT_HISTORY_DIR
    history_path = target_dir / DEFAULT_HISTORY_FILE

    if not history_path.exists():
        return []

    records: list[dict[str, Any]] = []

    for line in history_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))

    return records


def clear_history(history_dir: str | None = None) -> Path:
    """Delete comparison history file."""
    target_dir = Path(history_dir) if history_dir else DEFAULT_HISTORY_DIR
    history_path = target_dir / DEFAULT_HISTORY_FILE

    if history_path.exists():
        history_path.unlink()

    target_dir.mkdir(parents=True, exist_ok=True)
    return history_path