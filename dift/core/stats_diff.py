from __future__ import annotations

import polars as pl

from dift.reports.models import CategoricalDiff, NumericDiff, StatsDiff

NUMERIC_DTYPES = {
    pl.Int8,
    pl.Int16,
    pl.Int32,
    pl.Int64,
    pl.UInt8,
    pl.UInt16,
    pl.UInt32,
    pl.UInt64,
    pl.Float32,
    pl.Float64,
}

CATEGORICAL_DTYPES = {pl.String, pl.Categorical, pl.Enum, pl.Boolean}


def compare_stats(old: pl.DataFrame, new: pl.DataFrame, top_n: int = 10, threshold: float = 0.1 ) -> StatsDiff:
    """Compare numeric summary stats and categorical top values."""
    shared_cols = sorted(set(old.columns) & set(new.columns))
    numeric_diffs: list[NumericDiff] = []
    categorical_diffs: list[CategoricalDiff] = []

    for column in shared_cols:
        old_dtype = old.schema[column]
        new_dtype = new.schema[column]

        if old_dtype in NUMERIC_DTYPES and new_dtype in NUMERIC_DTYPES:
            old_series = old[column]
            new_series = new[column]

            o_min, n_min = _safe_float(old_series.min()), _safe_float(new_series.min())
            o_max, n_max = _safe_float(old_series.max()), _safe_float(new_series.max())
            o_mean, n_mean = _safe_float(old_series.mean()), _safe_float(new_series.mean())
            o_std, n_std = _safe_float(old_series.std()), _safe_float(new_series.std())

            mean_delta = abs(n_mean - o_mean) if n_mean is not None and o_mean is not None else 0            
            std_delta = abs(n_std - o_std) if n_std is not None and o_std is not None else 0
            
            o_range = o_max - o_min if o_max is not None and o_min is not None else 0
            n_range = n_max - n_min if n_max is not None and n_min is not None else 0
            range_delta = abs(n_range - o_range)

            is_drifted = (mean_delta > threshold) or (std_delta > threshold) or (range_delta > threshold)

            numeric_diffs.append(
                NumericDiff(
                    column=column,
                    old_min=o_min,
                    new_min=n_min,
                    old_max=o_max,
                    new_max=n_max,
                    old_mean=o_mean,
                    new_mean=n_mean,
                    delta_mean=_safe_delta(n_mean, o_mean),
                    old_std=o_std,
                    new_std=n_std,
                    delta_std=_safe_delta(n_std, o_std),
                    delta_range=_safe_delta(n_range, o_range),
                    is_drifted=is_drifted,
                    drift_threshold=threshold
                )
            )

        elif old_dtype in CATEGORICAL_DTYPES and new_dtype in CATEGORICAL_DTYPES:
            old_counts = _top_counts(old, column, top_n)
            new_counts = _top_counts(new, column, top_n)
            old_values = set(old_counts)
            new_values = set(new_counts)
            categorical_diffs.append(
                CategoricalDiff(
                    column=column,
                    values_added=sorted(map(str, new_values - old_values)),
                    values_removed=sorted(map(str, old_values - new_values)),
                    old_top_values={str(k): v for k, v in old_counts.items()},
                    new_top_values={str(k): v for k, v in new_counts.items()},
                )
            )

    return StatsDiff(numeric_diffs=numeric_diffs, categorical_diffs=categorical_diffs)


def _top_counts(df: pl.DataFrame, column: str, top_n: int) -> dict[object, int]:
    result = (
        df.group_by(column)
        .len()
        .sort("len", descending=True)
        .head(top_n)
        .to_dicts()
    )
    return {row[column]: row["len"] for row in result}


def _safe_float(value: object) -> float | None:
    if value is None:
        return None
    return float(value)


def _safe_delta(new_value: float | None, old_value: float | None) -> float | None:
    if new_value is None or old_value is None:
        return None
    return new_value - old_value
