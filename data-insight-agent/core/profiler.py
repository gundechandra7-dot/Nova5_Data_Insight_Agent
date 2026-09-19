"""
Comprehensive Statistical Profiling and Hygiene Engine.
Computes data types, distributions, missing values, outliers, correlations, and executive summaries.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd


class DataProfiler:
    """Profiles Pandas DataFrames to extract deep statistical and data-hygiene insights."""

    @classmethod
    def profile(cls, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return {
                "shape": (0, 0),
                "columns": {},
                "summary": "Dataset is empty.",
                "completeness_pct": 0.0,
                "duplicate_rows": 0,
            }

        total_rows = len(df)
        total_cols = len(df.columns)
        total_cells = total_rows * total_cols

        # 1. Column classifications
        col_types = cls._classify_columns(df)
        numeric_cols = col_types["numeric"]
        cat_cols = col_types["categorical"]
        date_cols = col_types["datetime"]
        bool_cols = col_types["boolean"]
        text_cols = col_types["text"]

        # 2. Missing values analysis
        missing_counts = df.isnull().sum().to_dict()
        missing_pcts = {k: round((v / total_rows) * 100, 2) for k, v in missing_counts.items()}
        total_missing_cells = int(df.isnull().sum().sum())
        completeness_pct = round(((total_cells - total_missing_cells) / total_cells) * 100, 2) if total_cells > 0 else 0.0

        # 3. Duplicate rows
        duplicate_rows = int(df.duplicated().sum())
        duplicate_pct = round((duplicate_rows / total_rows) * 100, 2) if total_rows > 0 else 0.0

        # 4. Numeric Column Profiles (Descriptive stats, skew, outliers)
        numeric_stats = {}
        outlier_summary = {}
        for col in numeric_cols:
            series = df[col].dropna()
            if not series.empty:
                q1 = float(series.quantile(0.25))
                q3 = float(series.quantile(0.75))
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outliers = series[(series < lower_bound) | (series > upper_bound)]
                outlier_count = len(outliers)
                outlier_pct = round((outlier_count / len(series)) * 100, 2)

                outlier_summary[col] = {
                    "count": outlier_count,
                    "pct": outlier_pct,
                    "lower_bound": round(lower_bound, 3),
                    "upper_bound": round(upper_bound, 3),
                }

                numeric_stats[col] = {
                    "mean": round(float(series.mean()), 3),
                    "std": round(float(series.std()), 3) if len(series) > 1 else 0.0,
                    "min": round(float(series.min()), 3),
                    "q25": round(q1, 3),
                    "median": round(float(series.median()), 3),
                    "q75": round(q3, 3),
                    "max": round(float(series.max()), 3),
                    "skew": round(float(series.skew()), 3) if len(series) > 2 else 0.0,
                    "zeros_count": int((series == 0).sum()),
                    "zeros_pct": round(((series == 0).sum() / len(series)) * 100, 2),
                }

        # 5. Categorical Column Profiles
        categorical_stats = {}
        for col in cat_cols:
            series = df[col].dropna()
            val_counts = series.value_counts()
            top_5 = val_counts.head(5).to_dict()
            categorical_stats[col] = {
                "unique_count": int(series.nunique()),
                "top_values": top_5,
                "top_category": str(val_counts.index[0]) if not val_counts.empty else None,
                "top_freq": int(val_counts.iloc[0]) if not val_counts.empty else 0,
            }

        # 6. Datetime Column Profiles
        datetime_stats = {}
        for col in date_cols:
            series = df[col].dropna()
            if not series.empty:
                min_date = series.min()
                max_date = series.max()
                datetime_stats[col] = {
                    "min": str(min_date),
                    "max": str(max_date),
                    "range_days": (max_date - min_date).days if hasattr((max_date - min_date), "days") else None,
                }

        # 7. Correlation Analysis
        correlations: Dict[str, float] = {}
        corr_matrix: Optional[Dict[str, Dict[str, float]]] = None
        if len(numeric_cols) >= 2:
            num_df = df[numeric_cols].dropna()
            if len(num_df) > 2:
                corr_df = num_df.corr(method="pearson").round(3)
                corr_matrix = corr_df.to_dict()
                # Find strongest non-trivial correlations
                for i, c1 in enumerate(numeric_cols):
                    for j, c2 in enumerate(numeric_cols):
                        if i < j:
                            val = corr_df.loc[c1, c2]
                            if not np.isnan(val) and abs(val) >= 0.5:
                                correlations[f"{c1} vs {c2}"] = float(val)

        # 8. Data Health Alerts
        alerts = []
        if duplicate_rows > 0:
            alerts.append(f"⚠️ **Duplicate Rows**: Found {duplicate_rows} ({duplicate_pct}%) duplicate rows.")
        for col, pct in missing_pcts.items():
            if pct > 40:
                alerts.append(f"🚨 **High Missing Values**: Column `{col}` has {pct}% missing values.")
            elif pct > 15:
                alerts.append(f"⚠️ **Missing Values**: Column `{col}` has {pct}% missing values.")
        for col, o_info in outlier_summary.items():
            if o_info["pct"] > 5:
                alerts.append(f"🔍 **Significant Outliers**: `{col}` has {o_info['count']} outliers ({o_info['pct']}% of records).")
        for col in df.columns:
            if df[col].nunique() == 1 and total_rows > 1:
                alerts.append(f"ℹ️ **Constant Column**: `{col}` has only 1 unique value across all rows.")

        profile_data = {
            "total_rows": total_rows,
            "total_columns": total_cols,
            "col_types": col_types,
            "completeness_pct": completeness_pct,
            "total_missing_cells": total_missing_cells,
            "missing_counts": missing_counts,
            "missing_pcts": missing_pcts,
            "duplicate_rows": duplicate_rows,
            "duplicate_pct": duplicate_pct,
            "numeric_stats": numeric_stats,
            "outlier_summary": outlier_summary,
            "categorical_stats": categorical_stats,
            "datetime_stats": datetime_stats,
            "correlations": correlations,
            "corr_matrix": corr_matrix,
            "alerts": alerts,
        }

        # Formatted string for LLM Agent prompt
        profile_data["llm_summary_prompt"] = cls.format_for_prompt(profile_data)

        return profile_data

    @classmethod
    def _classify_columns(cls, df: pd.DataFrame) -> Dict[str, List[str]]:
        numeric = []
        categorical = []
        datetime_cols = []
        boolean_cols = []
        text_cols = []

        for col in df.columns:
            dtype = df[col].dtype
            if pd.api.types.is_numeric_dtype(dtype) and not pd.api.types.is_bool_dtype(dtype):
                # If numeric but only 2 unique values and not float, could be binary flag
                numeric.append(col)
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                datetime_cols.append(col)
            elif pd.api.types.is_bool_dtype(dtype):
                boolean_cols.append(col)
            else:
                # Check if it can be parsed as datetime
                if any(kw in str(col).lower() for kw in ["date", "time", "timestamp", "year_month"]):
                    try:
                        converted = pd.to_datetime(df[col], errors="coerce")
                        if converted.notna().sum() >= 0.5 * len(df):
                            df[col] = converted
                            datetime_cols.append(col)
                            continue
                    except Exception:
                        pass

                # String or object: check unique ratio
                non_null = df[col].dropna()
                nunique = non_null.nunique()
                total = len(non_null)
                if total > 0 and (nunique / total > 0.8 and nunique > 50):
                    text_cols.append(col)
                else:
                    categorical.append(col)

        return {
            "numeric": numeric,
            "categorical": categorical,
            "datetime": datetime_cols,
            "boolean": boolean_cols,
            "text": text_cols,
        }

    @classmethod
    def format_for_prompt(cls, profile: Dict[str, Any]) -> str:
        """Formats the profile into a high-density, context-rich summary for LLM ingestion."""
        lines = [
            f"Dataset Dimensions: {profile['total_rows']} rows x {profile['total_columns']} columns",
            f"Data Completeness: {profile['completeness_pct']}% (Total missing cells: {profile['total_missing_cells']})",
            f"Duplicate Rows: {profile['duplicate_rows']} ({profile['duplicate_pct']}%)",
            "",
            "Column Classification:",
            f"- Numeric: {', '.join(profile['col_types']['numeric']) or 'None'}",
            f"- Categorical: {', '.join(profile['col_types']['categorical']) or 'None'}",
            f"- Datetime: {', '.join(profile['col_types']['datetime']) or 'None'}",
            f"- Text / High-Cardinality ID: {', '.join(profile['col_types']['text']) or 'None'}",
            "",
            "Numeric Column Key Statistics (Mean, Median, Min, Max, Outliers):"
        ]

        for col, stats in profile["numeric_stats"].items():
            outlier_info = profile["outlier_summary"].get(col, {})
            outlier_str = f", Outliers: {outlier_info.get('count', 0)} ({outlier_info.get('pct', 0)}%)" if outlier_info else ""
            lines.append(
                f"- {col}: Mean={stats['mean']}, Median={stats['median']}, Range=[{stats['min']} to {stats['max']}], Std={stats['std']}, Skew={stats['skew']}{outlier_str}"
            )

        if profile["categorical_stats"]:
            lines.append("\nTop Categorical Distributions:")
            for col, cat_info in profile["categorical_stats"].items():
                top_items = [f"'{k}': {v}" for k, v in list(cat_info['top_values'].items())[:3]]
                lines.append(f"- {col} ({cat_info['unique_count']} unique): Top -> {', '.join(top_items)}")

        if profile["datetime_stats"]:
            lines.append("\nDatetime Spans:")
            for col, dt_info in profile["datetime_stats"].items():
                lines.append(f"- {col}: from {dt_info['min']} to {dt_info['max']} (Span: {dt_info['range_days']} days)")

        if profile["correlations"]:
            lines.append("\nKey Correlations (|r| >= 0.5):")
            for pair, r_val in list(profile["correlations"].items())[:8]:
                lines.append(f"- {pair}: r = {r_val}")

        if profile["alerts"]:
            lines.append("\nData Quality Alerts:")
            for alert in profile["alerts"]:
                lines.append(f"- {alert}")

        return "\n".join(lines)
