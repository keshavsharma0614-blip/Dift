from __future__ import annotations

from pathlib import Path

from dift.io.sql_reader import read_sql_query, read_sql_table

import polars as pl

SUPPORTED_EXTENSIONS = {".csv", ".parquet", ".xlsx", ".xls", ".json"}


class DatasetReadError(ValueError):
    """Raised when Dift cannot read a dataset."""


def read_dataset(path: str | Path) -> pl.DataFrame:
    """Read local datasets or SQL datasets into a Polars DataFrame."""

    path_str = str(path)

    # =========================================================================
    # SQL DATABASE SUPPORT
    # Format:
    # sqlite:///database.db::table_name
    # sqlite:///database.db::SELECT * FROM users
    # =========================================================================
    if path_str.startswith(("sqlite://", "postgresql://", "mysql://")):
        if "::" not in path_str:
            raise DatasetReadError(
                "SQL dataset format must be: connection_string::table_or_query"
            )

        connection_string, target = path_str.split("::", 1)

        # Detect query vs table
        if target.strip().lower().startswith("select "):
            return read_sql_query(connection_string, target)

        return read_sql_table(connection_string, target)

    # =========================================================================
    # LOCAL FILE SUPPORT
    # =========================================================================
    dataset_path = Path(path)

    if not dataset_path.exists():
        raise DatasetReadError(f"Dataset not found: {dataset_path}")

    suffix = dataset_path.suffix.lower()

    if suffix == ".csv":
        return pl.read_csv(dataset_path)

    if suffix == ".parquet":
        return pl.read_parquet(dataset_path)

    if suffix in {".xlsx", ".xls"}:
        return pl.read_excel(dataset_path, engine="fastexcel")

    if suffix == ".json":
        return pl.read_json(dataset_path)

    raise DatasetReadError(
        f"Unsupported dataset type '{suffix}'. "
        f"Supported types: {sorted(SUPPORTED_EXTENSIONS)}"
    )
