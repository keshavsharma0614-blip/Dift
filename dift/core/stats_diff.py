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


def compare_stats(
    old: pl.DataFrame,
    new: pl.DataFrame,
    top_n: int = 10,
    threshold: float = 0.1,
) -> StatsDiff:
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

            o_min = _safe_float(old_series.min())
            n_min = _safe_float(new_series.min())
            o_max = _safe_float(old_series.max())
            n_max = _safe_float(new_series.max())
            o_mean = _safe_float(old_series.mean())
            n_mean = _safe_float(new_series.mean())
            o_std = _safe_float(old_series.std())
            n_std = _safe_float(new_series.std())

            o_range = (
                o_max - o_min
                if o_max is not None and o_min is not None
                else None
            )
            n_range = (
                n_max - n_min
                if n_max is not None and n_min is not None
                else None
            )

            mean_shift_pct = _relative_change(n_mean, o_mean)
            std_shift_pct = _relative_change(n_std, o_std)
            range_shift_pct = _relative_change(n_range, o_range)

            is_drifted = any(
                shift is not None and shift >= threshold
                for shift in [mean_shift_pct, std_shift_pct, range_shift_pct]
            )

            severity = _classify_numeric_drift(
                mean_shift_pct=mean_shift_pct,
                std_shift_pct=std_shift_pct,
                range_shift_pct=range_shift_pct,
                threshold=threshold,
            )

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
                    mean_shift_pct=mean_shift_pct,
                    std_shift_pct=std_shift_pct,
                    range_shift_pct=range_shift_pct,
                    is_drifted=is_drifted,
                    drift_threshold=threshold,
                    severity=severity,
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

    return StatsDiff(
        numeric_diffs=numeric_diffs,
        categorical_diffs=categorical_diffs,
    )


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


def _relative_change(
    new_value: float | None,
    old_value: float | None,
) -> float | None:
    if new_value is None or old_value is None:
        return None

    baseline = abs(old_value)

    if baseline == 0:
        return abs(new_value) if new_value != 0 else 0.0

    return abs(new_value - old_value) / baseline


def _classify_numeric_drift(
    mean_shift_pct: float | None,
    std_shift_pct: float | None,
    range_shift_pct: float | None,
    threshold: float,
) -> str:
    shifts = [
        shift
        for shift in [mean_shift_pct, std_shift_pct, range_shift_pct]
        if shift is not None
    ]

    if not shifts:
        return "low"

    max_shift = max(shifts)

    if max_shift >= threshold * 5:
        return "high"

    if max_shift >= threshold * 2:
        return "medium"

    if max_shift >= threshold:
        return "low"

    return "low"


def _safe_delta(
    new_value: float | None,
    old_value: float | None,
) -> float | None:
    if new_value is None or old_value is None:
        return None
    return new_value - old_value