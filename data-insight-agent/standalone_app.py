"""
================================================================================
🧠 DATA INSIGHT AI AGENT - ALL-IN-ONE STANDALONE APPLICATION
================================================================================
Entire architecture in a single, completely self-contained Python file.
Includes:
- Multi-format Ingestion Engine (CSV, TSV, Excel, JSON, Parquet, Feather, SQLite, Text)
- Deep Statistical Profiling, Data Hygiene & Outlier Detection
- Smart Automated Visualizations & Interactive Custom Chart Builder (Plotly)
- Sandboxed Python / Pandas Code Interpreter Sandbox
- AI Reasoning & Conversational Agent (Google Gemini API + Offline Statistical Engine)
- Standalone HTML & Markdown Executive Report Generator
- Built-in In-Memory Synthetic Sample Dataset Generator (Retail Sales, Churn, IoT, etc.)
- Full Streamlit Web Dashboard with Persistent Bottom Chat Input Box

Usage:
  pip install streamlit pandas plotly openpyxl pyarrow duckdb python-dotenv statsmodels google-genai
  streamlit run standalone_app.py
================================================================================
"""

import os
import io
import sys
import csv
import json
import sqlite3
import datetime
import re
from typing import Dict, Any, Tuple, List, Optional

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import duckdb
from dotenv import load_dotenv

load_dotenv()


# ==============================================================================
# 1. INGESTION ENGINE
# ==============================================================================
class IngestionEngine:
    """Universal multi-format data loader supporting tabular, columnar, hierarchical, and SQL formats."""

    @staticmethod
    def detect_format(file_name: str) -> str:
        ext = os.path.splitext(file_name)[1].lower()
        mapping = {
            ".csv": "csv", ".tsv": "tsv", ".txt": "text",
            ".xlsx": "excel", ".xls": "excel", ".ods": "excel",
            ".json": "json", ".jsonl": "jsonl",
            ".parquet": "parquet", ".pq": "parquet", ".feather": "feather",
            ".db": "sqlite", ".sqlite": "sqlite", ".sqlite3": "sqlite",
        }
        return mapping.get(ext, "unknown")

    @staticmethod
    def inspect_sqlite(file_bytes_or_path) -> List[str]:
        try:
            if isinstance(file_bytes_or_path, (bytes, io.BytesIO)):
                raw_bytes = file_bytes_or_path.getvalue() if isinstance(file_bytes_or_path, io.BytesIO) else file_bytes_or_path
                temp_db = sqlite3.connect(":memory:")
                temp_db.deserialize(raw_bytes)
                tables = [r[0] for r in temp_db.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall() if not r[0].startswith("sqlite_")]
                temp_db.close()
                return tables
            elif isinstance(file_bytes_or_path, str) and os.path.exists(file_bytes_or_path):
                conn = sqlite3.connect(file_bytes_or_path)
                tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall() if not r[0].startswith("sqlite_")]
                conn.close()
                return tables
        except Exception:
            pass
        return []

    @staticmethod
    def inspect_excel_sheets(file_obj) -> List[str]:
        try:
            excel_file = pd.ExcelFile(file_obj)
            return excel_file.sheet_names
        except Exception:
            return ["Sheet1"]

    @classmethod
    def load_data(
        cls,
        file_obj,
        file_name: str,
        sheet_name: Optional[str] = None,
        table_name: Optional[str] = None,
        sql_query: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        fmt = cls.detect_format(file_name)
        df: Optional[pd.DataFrame] = None
        metadata: Dict[str, Any] = {
            "file_name": file_name,
            "detected_format": fmt,
            "available_sheets": [],
            "available_tables": [],
            "warnings": [],
        }

        # 1. CSV / TSV / Delimited Text
        if fmt in ("csv", "tsv", "text"):
            content_sample = None
            encoding = "utf-8"
            if hasattr(file_obj, "read"):
                pos = file_obj.tell() if hasattr(file_obj, "tell") else 0
                sample_bytes = file_obj.read(4096)
                if hasattr(file_obj, "seek"):
                    file_obj.seek(pos)
                try:
                    content_sample = sample_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    content_sample = sample_bytes.decode("latin-1", errors="replace")
                    encoding = "latin-1"

            delimiter = "," if fmt == "csv" else ("\t" if fmt == "tsv" else None)
            if delimiter is None and content_sample:
                try:
                    delimiter = csv.Sniffer().sniff(content_sample).delimiter
                except Exception:
                    delimiter = ","

            try:
                df = pd.read_csv(file_obj, sep=delimiter, encoding=encoding, on_bad_lines="skip")
            except Exception:
                if hasattr(file_obj, "seek"):
                    file_obj.seek(0)
                df = pd.read_csv(file_obj, sep=None, engine="python", on_bad_lines="skip")

        # 2. Excel (.xlsx, .xls, .ods)
        elif fmt == "excel":
            sheets = cls.inspect_excel_sheets(file_obj)
            metadata["available_sheets"] = sheets
            selected_sheet = sheet_name if sheet_name and sheet_name in sheets else (sheets[0] if sheets else "Sheet1")
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
            df = pd.read_excel(file_obj, sheet_name=selected_sheet)
            metadata["selected_sheet"] = selected_sheet

        # 3. JSON / JSONL
        elif fmt in ("json", "jsonl"):
            try:
                if hasattr(file_obj, "seek"):
                    file_obj.seek(0)
                if fmt == "jsonl":
                    df = pd.read_json(file_obj, lines=True)
                else:
                    if hasattr(file_obj, "read"):
                        raw = file_obj.read()
                        if isinstance(raw, bytes):
                            raw = raw.decode("utf-8", errors="replace")
                        parsed = json.loads(raw)
                    else:
                        with open(file_obj, "r", encoding="utf-8") as f:
                            parsed = json.load(f)
                    
                    if isinstance(parsed, list):
                        df = pd.json_normalize(parsed)
                    elif isinstance(parsed, dict):
                        found_nested = False
                        for key in ["data", "items", "records", "results", "rows", "values", "metrics", "series"]:
                            if key in parsed and isinstance(parsed[key], list):
                                df = pd.json_normalize(parsed[key])
                                found_nested = True
                                break
                        if not found_nested:
                            df = pd.json_normalize(parsed)
            except Exception:
                if hasattr(file_obj, "seek"):
                    file_obj.seek(0)
                df = pd.read_json(file_obj)

        # 4. Parquet
        elif fmt == "parquet":
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
            df = pd.read_parquet(file_obj)

        # 5. Feather
        elif fmt == "feather":
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
            df = pd.read_feather(file_obj)

        # 6. SQLite Database
        elif fmt == "sqlite":
            if hasattr(file_obj, "read"):
                raw_bytes = file_obj.read() if hasattr(file_obj, "read") else file_obj
                conn = sqlite3.connect(":memory:")
                conn.deserialize(raw_bytes)
            else:
                conn = sqlite3.connect(file_obj)

            tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall() if not r[0].startswith("sqlite_")]
            metadata["available_tables"] = tables
            target_table = table_name if table_name and table_name in tables else (tables[0] if tables else None)
            if sql_query:
                df = pd.read_sql_query(sql_query, conn)
            elif target_table:
                df = pd.read_sql_query(f'SELECT * FROM "{target_table}"', conn)
                metadata["selected_table"] = target_table
            else:
                df = pd.DataFrame()
            conn.close()

        else:
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
            df = pd.read_csv(file_obj, on_bad_lines="skip")

        if df is None:
            raise ValueError(f"Unable to parse dataset from {file_name}")

        df.columns = [str(c).strip() for c in df.columns]

        # Datetime heuristic parsing
        for col in df.columns:
            if df[col].dtype == "object":
                col_lower = col.lower()
                if any(kw in col_lower for kw in ["date", "time", "timestamp", "created_at", "updated_at"]):
                    try:
                        converted = pd.to_datetime(df[col], errors="coerce")
                        if converted.notna().sum() >= 0.5 * len(df):
                            df[col] = converted
                    except Exception:
                        pass

        metadata["rows"] = int(df.shape[0])
        metadata["columns"] = int(df.shape[1])
        metadata["memory_kb"] = round(df.memory_usage(deep=True).sum() / 1024, 2)
        return df, metadata


# ==============================================================================
# 2. STATISTICAL PROFILER & DATA HYGIENE
# ==============================================================================
class DataProfiler:
    """Extracts deep statistical summaries, missingness metrics, outlier bounds, and correlation insights."""

    @classmethod
    def profile(cls, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return {"total_rows": 0, "total_columns": 0, "completeness_pct": 0.0, "alerts": []}

        total_rows = len(df)
        total_cols = len(df.columns)
        total_cells = total_rows * total_cols

        col_types = cls._classify_columns(df)
        numeric_cols = col_types["numeric"]
        cat_cols = col_types["categorical"]
        date_cols = col_types["datetime"]

        missing_counts = df.isnull().sum().to_dict()
        missing_pcts = {k: round((v / total_rows) * 100, 2) for k, v in missing_counts.items()}
        total_missing_cells = int(df.isnull().sum().sum())
        completeness_pct = round(((total_cells - total_missing_cells) / total_cells) * 100, 2) if total_cells > 0 else 0.0

        duplicate_rows = int(df.duplicated().sum())
        duplicate_pct = round((duplicate_rows / total_rows) * 100, 2) if total_rows > 0 else 0.0

        numeric_stats = {}
        outlier_summary = {}
        for col in numeric_cols:
            series = df[col].dropna()
            if not series.empty:
                q1 = float(series.quantile(0.25))
                q3 = float(series.quantile(0.75))
                iqr = q3 - q1
                lb = q1 - 1.5 * iqr
                ub = q3 + 1.5 * iqr
                outliers = series[(series < lb) | (series > ub)]
                outlier_summary[col] = {
                    "count": len(outliers),
                    "pct": round((len(outliers) / len(series)) * 100, 2),
                    "lower_bound": round(lb, 3),
                    "upper_bound": round(ub, 3),
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
                    "zeros_pct": round(((series == 0).sum() / len(series)) * 100, 2),
                }

        categorical_stats = {}
        for col in cat_cols:
            series = df[col].dropna()
            val_counts = series.value_counts()
            categorical_stats[col] = {
                "unique_count": int(series.nunique()),
                "top_values": val_counts.head(5).to_dict(),
                "top_category": str(val_counts.index[0]) if not val_counts.empty else None,
                "top_freq": int(val_counts.iloc[0]) if not val_counts.empty else 0,
            }

        datetime_stats = {}
        for col in date_cols:
            series = df[col].dropna()
            if not series.empty:
                datetime_stats[col] = {
                    "min": str(series.min()),
                    "max": str(series.max()),
                    "range_days": (series.max() - series.min()).days if hasattr((series.max() - series.min()), "days") else None,
                }

        correlations = {}
        if len(numeric_cols) >= 2:
            num_df = df[numeric_cols].dropna()
            if len(num_df) > 2:
                corr_df = num_df.corr(method="pearson").round(3)
                for i, c1 in enumerate(numeric_cols):
                    for j, c2 in enumerate(numeric_cols):
                        if i < j:
                            val = corr_df.loc[c1, c2]
                            if not np.isnan(val) and abs(val) >= 0.5:
                                correlations[f"{c1} vs {c2}"] = float(val)

        alerts = []
        if duplicate_rows > 0:
            alerts.append(f"⚠️ **Duplicate Rows**: Found {duplicate_rows} ({duplicate_pct}%) duplicate records.")
        for col, pct in missing_pcts.items():
            if pct > 40:
                alerts.append(f"🚨 **High Missingness**: Feature `{col}` has {pct}% missing values.")
            elif pct > 15:
                alerts.append(f"⚠️ **Missing Data**: Feature `{col}` has {pct}% missing values.")
        for col, o_info in outlier_summary.items():
            if o_info["pct"] > 5:
                alerts.append(f"🔍 **Significant Outliers**: `{col}` has {o_info['count']} outliers ({o_info['pct']}% of records).")

        return {
            "total_rows": total_rows, "total_columns": total_cols,
            "col_types": col_types, "completeness_pct": completeness_pct,
            "total_missing_cells": total_missing_cells, "missing_counts": missing_counts,
            "duplicate_rows": duplicate_rows, "duplicate_pct": duplicate_pct,
            "numeric_stats": numeric_stats, "outlier_summary": outlier_summary,
            "categorical_stats": categorical_stats, "datetime_stats": datetime_stats,
            "correlations": correlations, "alerts": alerts,
        }

    @classmethod
    def _classify_columns(cls, df: pd.DataFrame) -> Dict[str, List[str]]:
        numeric, categorical, datetime_cols, boolean_cols, text_cols = [], [], [], [], []
        for col in df.columns:
            dtype = df[col].dtype
            if pd.api.types.is_numeric_dtype(dtype) and not pd.api.types.is_bool_dtype(dtype):
                numeric.append(col)
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                datetime_cols.append(col)
            elif pd.api.types.is_bool_dtype(dtype):
                boolean_cols.append(col)
            else:
                if any(kw in str(col).lower() for kw in ["date", "time", "timestamp"]):
                    try:
                        converted = pd.to_datetime(df[col], errors="coerce")
                        if converted.notna().sum() >= 0.5 * len(df):
                            df[col] = converted
                            datetime_cols.append(col)
                            continue
                    except Exception:
                        pass
                non_null = df[col].dropna()
                if len(non_null) > 0 and (non_null.nunique() / len(non_null) > 0.8 and non_null.nunique() > 50):
                    text_cols.append(col)
                else:
                    categorical.append(col)
        return {"numeric": numeric, "categorical": categorical, "datetime": datetime_cols, "boolean": boolean_cols, "text": text_cols}


# ==============================================================================
# 3. INTERACTIVE VISUALIZER
# ==============================================================================
class Visualizer:
    """Plotly-based visualization generator for automatic insights and custom dashboards."""

    TEMPLATE = "plotly_dark"

    @classmethod
    def generate_smart_charts(cls, df: pd.DataFrame, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        charts = []
        if df.empty:
            return charts

        numeric_cols = profile.get("col_types", {}).get("numeric", [])
        cat_cols = profile.get("col_types", {}).get("categorical", [])
        date_cols = profile.get("col_types", {}).get("datetime", [])

        # 1. Correlation Matrix Heatmap
        if len(numeric_cols) >= 2:
            num_df = df[numeric_cols].dropna()
            if len(num_df) > 3:
                corr = num_df.corr().round(2)
                fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1, title="Correlation Matrix Heatmap", template=cls.TEMPLATE)
                fig_corr.update_layout(margin=dict(l=40, r=40, t=50, b=40))
                charts.append({"title": "Correlation Matrix", "description": "Measures linear relationships across all numerical variables.", "fig": fig_corr})

        # 2. Time-Series Trend
        if date_cols and numeric_cols:
            dt_col = date_cols[0]
            val_col = numeric_cols[0]
            ts_df = df[[dt_col, val_col]].dropna().sort_values(by=dt_col)
            if len(ts_df) > 1:
                fig_ts = px.line(ts_df, x=dt_col, y=val_col, title=f"Time Series Trend: {val_col} over {dt_col}", template=cls.TEMPLATE)
                fig_ts.update_xaxes(rangeslider_visible=True)
                fig_ts.update_layout(margin=dict(l=40, r=40, t=50, b=40))
                charts.append({"title": f"Temporal Trend: {val_col}", "description": f"Tracks changes of {val_col} over time.", "fig": fig_ts})

        # 3. Top Categorical Breakdowns
        for cat_col in cat_cols[:2]:
            val_counts = df[cat_col].value_counts().head(10).reset_index()
            val_counts.columns = [cat_col, "Count"]
            if len(val_counts) > 1:
                if len(val_counts) <= 5:
                    fig_cat = px.pie(val_counts, names=cat_col, values="Count", hole=0.45, title=f"Distribution of {cat_col}", template=cls.TEMPLATE)
                else:
                    fig_cat = px.bar(val_counts, x="Count", y=cat_col, orientation="h", title=f"Top 10 Frequencies in {cat_col}", template=cls.TEMPLATE, color="Count", color_continuous_scale="Viridis")
                    fig_cat.update_layout(yaxis=dict(autorange="reversed"))
                fig_cat.update_layout(margin=dict(l=40, r=40, t=50, b=40))
                charts.append({"title": f"Distribution: {cat_col}", "description": f"Category volume breakdown for {cat_col}.", "fig": fig_cat})

        # 4. Numeric Distributions & Box Outlier Spread
        for num_col in numeric_cols[:2]:
            fig_hist = px.histogram(df, x=num_col, marginal="box", title=f"Distribution & Outlier Spread: {num_col}", template=cls.TEMPLATE, color_discrete_sequence=["#1e3a8a"])
            fig_hist.update_layout(margin=dict(l=40, r=40, t=50, b=40))
            charts.append({"title": f"Distribution: {num_col}", "description": f"Visualizes frequency distribution, skewness, median, and outliers for {num_col}.", "fig": fig_hist})

        # 5. Strongest Relationship Scatter
        if len(numeric_cols) >= 2 and profile.get("correlations"):
            top_pair = list(profile["correlations"].keys())[0]
            col1, col2 = top_pair.split(" vs ")
            if col1 in df.columns and col2 in df.columns:
                color_arg = cat_cols[0] if cat_cols else None
                trendline_opt = None
                try:
                    import statsmodels
                    trendline_opt = "ols"
                except Exception:
                    trendline_opt = None
                try:
                    fig_scatter = px.scatter(df, x=col1, y=col2, color=color_arg, trendline=trendline_opt, title=f"Bivariate Relationship: {col1} vs {col2}", template=cls.TEMPLATE)
                except Exception:
                    fig_scatter = px.scatter(df, x=col1, y=col2, color=color_arg, title=f"Bivariate Relationship: {col1} vs {col2}", template=cls.TEMPLATE)
                fig_scatter.update_layout(margin=dict(l=40, r=40, t=50, b=40))
                charts.append({"title": f"Relationship: {col1} vs {col2}", "description": f"Scatter plot of {col1} versus {col2}.", "fig": fig_scatter})

        return charts

    @classmethod
    def create_custom_chart(
        cls,
        df: pd.DataFrame,
        chart_type: str,
        x_col: Optional[str] = None,
        y_col: Optional[str] = None,
        color_col: Optional[str] = None,
        size_col: Optional[str] = None,
        facet_col: Optional[str] = None,
        title: Optional[str] = None,
        color_theme: str = "Viridis",
    ) -> go.Figure:
        chart_type = chart_type.lower()
        kwargs: Dict[str, Any] = {"template": cls.TEMPLATE, "title": title or f"{chart_type.capitalize()} of {y_col or ''} by {x_col or ''}".strip()}
        if color_col and color_col != "None":
            kwargs["color"] = color_col
        if facet_col and facet_col != "None":
            kwargs["facet_col"] = facet_col

        if chart_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col, color_continuous_scale=color_theme, **kwargs)
        elif chart_type == "line":
            fig = px.line(df, x=x_col, y=y_col, **kwargs)
        elif chart_type == "scatter":
            if size_col and size_col != "None":
                kwargs["size"] = size_col
            fig = px.scatter(df, x=x_col, y=y_col, color_continuous_scale=color_theme, **kwargs)
        elif chart_type == "area":
            fig = px.area(df, x=x_col, y=y_col, **kwargs)
        elif chart_type == "histogram":
            fig = px.histogram(df, x=x_col, y=y_col, marginal="box", **kwargs)
        elif chart_type == "box":
            fig = px.box(df, x=x_col, y=y_col, **kwargs)
        elif chart_type == "violin":
            fig = px.violin(df, x=x_col, y=y_col, box=True, points="all", **kwargs)
        elif chart_type == "pie":
            fig = px.pie(df, names=x_col, values=y_col, hole=0.3, **kwargs)
        elif chart_type == "treemap":
            path = [c for c in [color_col, x_col] if c and c != "None"] or [x_col]
            fig = px.treemap(df, path=path, values=y_col, **kwargs)
        elif chart_type == "heatmap":
            num_cols = df.select_dtypes(include=["number"]).columns
            corr = df[num_cols].corr().round(2)
            fig = px.imshow(corr, text_auto=True, color_continuous_scale=color_theme, **kwargs)
        else:
            fig = px.scatter(df, x=x_col, y=y_col, **kwargs)

        fig.update_layout(margin=dict(l=40, r=40, t=50, b=40))
        return fig


# ==============================================================================
# 4. CODE INTERPRETER EXECUTION SANDBOX
# ==============================================================================
class CodeInterpreter:
    """Executes generated Python / Plotly code securely against active DataFrame."""

    DISALLOWED = ["os", "subprocess", "shutil", "sys", "socket", "urllib", "requests", "http", "pathlib", "importlib", "__import__"]

    @classmethod
    def execute(cls, code_str: str, df: pd.DataFrame) -> Dict[str, Any]:
        match = re.search(r"```(?:python)?\s*([\s\S]*?)\s*```", code_str.strip())
        clean_code = match.group(1).strip() if match else code_str.strip()

        for mod in cls.DISALLOWED:
            if re.search(rf"\b(import\s+{mod}|from\s+{mod}|__import__\s*\(\s*['\"]{mod}['\"])\b", clean_code):
                return {"success": False, "stdout": "", "error": f"Security restriction: module '{mod}' is prohibited.", "fig": None, "result_df": None, "code": clean_code}

        buffer = io.StringIO()
        old_stdout = sys.stdout
        scope: Dict[str, Any] = {"df": df.copy(), "pd": pd, "np": np, "px": px, "go": go, "duckdb": duckdb, "fig": None, "result_df": None, "result": None}

        try:
            sys.stdout = buffer
            exec(clean_code, scope, scope)
            sys.stdout = old_stdout

            fig = scope.get("fig")
            if not isinstance(fig, (go.Figure, dict)):
                fig = None

            raw_res = scope.get("result_df")
            if raw_res is None:
                raw_res = scope.get("result")

            result_df = raw_res if isinstance(raw_res, pd.DataFrame) else (raw_res.to_frame() if isinstance(raw_res, pd.Series) else None)
            return {"success": True, "stdout": buffer.getvalue(), "fig": fig, "result_df": result_df, "error": None, "code": clean_code}
        except Exception as e:
            sys.stdout = old_stdout
            return {"success": False, "stdout": buffer.getvalue(), "fig": None, "result_df": None, "error": str(e), "code": clean_code}
        finally:
            sys.stdout = old_stdout


# ==============================================================================
# 5. AI AGENT & CONVERSATIONAL REASONING
# ==============================================================================
class DataAgent:
    """Orchestrates LLM prompts (Google Gemini) and smart offline heuristics."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    def generate_executive_insights(self, df: pd.DataFrame, profile: Dict[str, Any]) -> str:
        if self.client:
            try:
                prompt = f"""
You are a Principal Data Scientist and Executive Business Strategist.
Analyze this dataset profile:
Rows: {profile.get('total_rows')}, Columns: {profile.get('total_columns')}, Completeness: {profile.get('completeness_pct')}%
Numeric stats: {profile.get('numeric_stats')}
Top categories: {profile.get('categorical_stats')}
Correlations: {profile.get('correlations')}
Alerts: {profile.get('alerts')}

Sample Data:
{df.head(5).to_string()}

Provide clean Markdown with sections:
1. 🎯 **Executive Summary**
2. 💡 **Key Discoveries & Notable Patterns**
3. ⚠️ **Data Quality & Risk Flags**
4. 🚀 **Strategic Recommendations & Next Steps**
Cite specific metrics and numbers.
"""
                resp = self.client.models.generate_content(model=self.model_name, contents=prompt)
                if resp and resp.text:
                    return resp.text.strip()
            except Exception:
                pass

        # Offline heuristic fallback
        return self._generate_heuristic_insights(df, profile)

    def chat_query(
        self,
        query: str,
        df: Optional[pd.DataFrame] = None,
        profile: Optional[Dict[str, Any]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            return self._handle_no_data(query)

        profile = profile or {}
        if self.client:
            try:
                return self._gemini_chat(query, df, profile, chat_history)
            except Exception:
                pass

        return self._heuristic_chat(query, df, profile)

    def _handle_no_data(self, query: str) -> Dict[str, Any]:
        return {
            "answer": (
                f"Hello! I received your prompt: **\"{query}\"**.\n\n"
                "💡 **No dataset is loaded into the workspace yet.**\n\n"
                "- 📁 **Load a Demo Dataset**: Click one of the 1-click sample buttons on this page or use the sidebar.\n"
                "- 📤 **Upload a File**: Go to the **'📂 Ingestion & Preview'** tab to upload CSV, Excel, JSON, Parquet, or SQLite.\n\n"
                "Once loaded, I will immediately profile the data, generate interactive charts, and execute your questions!"
            ),
            "code": None, "stdout": "", "fig": None, "result_df": None, "error": None,
        }

    def _gemini_chat(self, query: str, df: pd.DataFrame, profile: Dict[str, Any], chat_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        cols_summary = ", ".join([f"{col} ({df[col].dtype})" for col in df.columns])
        code_prompt = f"""
You are an expert Python Data Science Code Interpreter.
Given pandas DataFrame `df` with columns: {cols_summary}.
Rows: {len(df)}. Sample: {df.head(3).to_dict(orient='records')}

User Question: "{query}"

Write Python code to answer the user.
- If asking for a chart, create Plotly figure `fig = px.bar(...)` or `fig = px.line(...)` or `fig = px.scatter(...)`.
- If tabular data answers the question, assign to `result_df`.
- Print summary metrics with `print(...)`.
Return ONLY python code in ```python ``` block.
"""
        resp = self.client.models.generate_content(model=self.model_name, contents=code_prompt)
        exec_res = CodeInterpreter.execute(resp.text if resp else "", df)

        synth_prompt = f"""
User asked: "{query}"
Code output: {exec_res['stdout']}
Table: {exec_res['result_df'].to_string() if exec_res['result_df'] is not None else 'None'}
Chart created: {'Yes' if exec_res['fig'] is not None else 'No'}
Synthesize a concise, friendly executive response.
"""
        synth_resp = self.client.models.generate_content(model=self.model_name, contents=synth_prompt)
        answer = synth_resp.text if synth_resp else (exec_res["stdout"] or "Analysis complete.")

        return {"answer": answer, "code": exec_res["code"], "stdout": exec_res["stdout"], "fig": exec_res["fig"], "result_df": exec_res["result_df"], "error": exec_res["error"]}

    def _heuristic_chat(self, query: str, df: pd.DataFrame, profile: Dict[str, Any]) -> Dict[str, Any]:
        q = query.lower()
        num_cols = profile.get("col_types", {}).get("numeric", [])
        cat_cols = profile.get("col_types", {}).get("categorical", [])
        date_cols = profile.get("col_types", {}).get("datetime", [])

        mentioned_num = [c for c in num_cols if c.lower() in q]
        mentioned_cat = [c for c in cat_cols if c.lower() in q]
        mentioned_date = [c for c in date_cols if c.lower() in q]

        target_num = mentioned_num[0] if mentioned_num else (num_cols[0] if num_cols else None)
        target_cat = mentioned_cat[0] if mentioned_cat else (cat_cols[0] if cat_cols else None)
        target_date = mentioned_date[0] if mentioned_date else (date_cols[0] if date_cols else None)

        code = ""
        # Distribution / Outliers / Box
        if any(w in q for w in ["distribution", "histogram", "spread", "outlier", "outliers", "box", "density"]) and target_num:
            code = (
                f"fig = px.histogram(df, x='{target_num}', marginal='box', title='Distribution & Outlier Spread of {target_num}', template='plotly_white', color_discrete_sequence=['#1e3a8a'])\n"
                f"q1 = float(df['{target_num}'].quantile(0.25))\n"
                f"q3 = float(df['{target_num}'].quantile(0.75))\n"
                f"iqr = q3 - q1\n"
                f"outliers = df[(df['{target_num}'] < q1 - 1.5*iqr) | (df['{target_num}'] > q3 + 1.5*iqr)]\n"
                f"result_df = df['{target_num}'].describe().to_frame().round(2)\n"
                f"print(f'Distribution for {target_num}: Mean={{df[\"{target_num}\"].mean():.2f}}, Median={{df[\"{target_num}\"].median():.2f}}. Found {{len(outliers)}} outliers.')"
            )
        # Scatter / Correlation
        elif any(w in q for w in ["scatter", "relationship", "vs", "versus", "against", "correlation", "heatmap"]):
            n1 = mentioned_num[0] if len(mentioned_num) > 0 else (num_cols[0] if len(num_cols) > 0 else None)
            n2 = mentioned_num[1] if len(mentioned_num) > 1 else (num_cols[1] if len(num_cols) > 1 else None)
            if "heatmap" in q or "correlation" in q:
                code = "num_df = df.select_dtypes(include=['number'])\nresult_df = num_df.corr().round(3)\nfig = px.imshow(result_df, text_auto=True, color_continuous_scale='RdBu_r', title='Feature Correlation Heatmap', template='plotly_white')\nprint('Generated correlation matrix heatmap.')"
            elif n1 and n2:
                color_str = f", color='{target_cat}'" if target_cat else ""
                code = f"fig = px.scatter(df, x='{n1}', y='{n2}'{color_str}, title='Scatter Plot: {n1} vs {n2}', template='plotly_white')\ncorr = df[['{n1}', '{n2}']].dropna().corr().iloc[0, 1].round(3)\nprint(f'Pearson correlation between {n1} and {n2}: r = {{corr}}')"
            else:
                code = "result_df = df.describe().round(2)\nprint('Computed numerical statistics.')"
        # Trends / Time Series
        elif any(w in q for w in ["trend", "time", "date", "over time", "monthly", "daily"]) and (target_date or date_cols) and target_num:
            dt = target_date or date_cols[0]
            code = f"ts = df.dropna(subset=['{dt}', '{target_num}']).sort_values(by='{dt}')\nfig = px.line(ts, x='{dt}', y='{target_num}', title='{target_num} Trend Over Time', template='plotly_white')\nfig.update_xaxes(rangeslider_visible=True)\nprint(f'Chronological trend of {target_num} across {dt}.')"
        # Categorical Breakdown / Bar Chart
        elif any(w in q for w in ["top", "highest", "largest", "bar", "plot", "chart", "breakdown"]) and (target_cat or cat_cols):
            cat = target_cat or cat_cols[0]
            if target_num:
                code = f"result_df = df.groupby('{cat}')['{target_num}'].sum().reset_index().sort_values(by='{target_num}', ascending=False).head(10)\nfig = px.bar(result_df, x='{cat}', y='{target_num}', title='Top {cat} by {target_num}', template='plotly_white', color='{target_num}', color_continuous_scale='Viridis')\nprint(f'Top {cat} ranked by total {target_num}.')"
            else:
                code = f"result_df = df['{cat}'].value_counts().head(10).reset_index()\nresult_df.columns = ['{cat}', 'Count']\nfig = px.bar(result_df, x='{cat}', y='Count', title='Top {cat} Counts', template='plotly_white', color='Count')\nprint(f'Top categories in {cat}.')"
        # Missing values
        elif any(w in q for w in ["missing", "null", "nan", "empty", "quality"]):
            code = "missing = df.isnull().sum()\nresult_df = pd.DataFrame({'Feature': missing.index, 'Missing Count': missing.values, 'Pct (%)': (missing.values / len(df) * 100).round(2)})\nresult_df = result_df[result_df['Missing Count'] > 0].sort_values(by='Missing Count', ascending=False)\nif result_df.empty:\n    print('Zero missing values found.')\nelse:\n    fig = px.bar(result_df, x='Feature', y='Missing Count', color='Missing Count', title='Missing Values per Feature', template='plotly_white')\n    print(f'Found {len(result_df)} features with missing data.')"
        # Summary
        elif any(w in q for w in ["describe", "summary", "stats"]):
            code = "result_df = df.describe().round(2)\nprint('Computed descriptive statistics across all numerical features.')"
        else:
            if num_cols:
                code = f"result_df = df.head(10)\nfig = px.histogram(df, x='{num_cols[0]}', title='Distribution of {num_cols[0]}', template='plotly_white')\nprint('Displayed first 10 records and primary metric distribution.')"
            else:
                code = "result_df = df.head(10)\nprint(f'Displayed first 10 rows of {len(df)} total records.')"

        res = CodeInterpreter.execute(code, df)
        ans = f"Analysis for: **{query}**\n\n"
        if res["stdout"]:
            ans += f"{res['stdout']}\n"
        if not self.api_key:
            ans += "\n*(Tip: Add your Gemini API key in the sidebar for custom deep natural language reasoning!)*"
        return {"answer": ans, "code": res["code"], "stdout": res["stdout"], "fig": res["fig"], "result_df": res["result_df"], "error": res["error"]}

    def _generate_heuristic_insights(self, df: pd.DataFrame, profile: Dict[str, Any]) -> str:
        rows = profile.get("total_rows", 0)
        cols = profile.get("total_columns", 0)
        completeness = profile.get("completeness_pct", 100)
        corrs = profile.get("correlations", {})
        alerts = profile.get("alerts", [])

        lines = [
            "### 🎯 Executive Summary",
            f"The ingested dataset comprises **{rows:,} records** across **{cols} features**, with an overall completeness score of **{completeness}%**.",
            "\n### 💡 Key Discoveries & Notable Patterns",
        ]
        if corrs:
            for pair, r_val in list(corrs.items())[:3]:
                lines.append(f"- **Linear Relationship**: Detected {'strong' if abs(r_val)>0.7 else 'moderate'} correlation between **{pair}** ($r = {r_val}$).")
        else:
            lines.append("- Primary numerical metrics show independent, multi-factor variance without dominant collinearity.")

        for num_c in profile.get("col_types", {}).get("numeric", [])[:2]:
            st = profile.get("numeric_stats", {}).get(num_c, {})
            if st:
                lines.append(f"- **Distribution for `{num_c}`**: Averages **{st.get('mean')}** (median: {st.get('median')}) ranging [{st.get('min')} to {st.get('max')}].")

        lines.append("\n### ⚠️ Data Quality & Risk Flags")
        if alerts:
            for a in alerts:
                lines.append(f"- {a}")
        else:
            lines.append("- ✅ Zero critical hygiene defects (no duplicate records, high completeness).")

        lines.append("\n### 🚀 Strategic Recommendations & Next Steps")
        lines.append("1. **Cohort Segmentation**: Group primary revenue/score metrics by dominant categorical dimensions.")
        lines.append("2. **Anomaly Investigation**: Inspect flagged outlier records to avoid bias in downstream predictive models.")
        lines.append("3. **Interactive Visualizations**: Review the **Visualizations** tab for automated smart charts.")
        return "\n".join(lines)


# ==============================================================================
# 6. REPORT GENERATOR
# ==============================================================================
class ReportGenerator:
    """Generates standalone HTML and Markdown reports."""

    @classmethod
    def generate_html_report(cls, metadata: Dict[str, Any], profile: Dict[str, Any], insights_markdown: str, charts: Optional[List[Dict[str, Any]]] = None) -> str:
        timestamp = datetime.datetime.now().strftime("%B %d, %Y - %H:%M:%S")
        charts_html = ""
        if charts:
            for item in charts:
                fig = item.get("fig")
                if isinstance(fig, (go.Figure, dict)):
                    div_str = pio.to_html(fig, full_html=False, include_plotlyjs="cdn")
                    charts_html += f"<div style='background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:20px;margin-bottom:20px;'><h3>{item.get('title')}</h3><p style='color:#64748b;'>{item.get('description')}</p>{div_str}</div>"

        insights_html = insights_markdown.replace("\n", "<br>").replace("### ", "<h3>").replace("## ", "<h2>").replace("**", "<strong>")
        return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Report - {metadata.get('file_name')}</title>
<style>body{{font-family:-apple-system,sans-serif;background:#f8fafc;color:#0f172a;padding:30px;}} .container{{max-width:1100px;margin:auto;background:#fff;padding:40px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.05);}} .kpi{{display:inline-block;width:22%;background:#f1f5f9;padding:16px;margin:1%;border-radius:8px;text-align:center;}} .kpi-val{{font-size:24px;font-weight:700;color:#2563eb;}}</style></head><body>
<div class="container"><h1>📊 AI Data Intelligence Report: {metadata.get('file_name')}</h1><p style="color:#64748b;">Generated: {timestamp}</p>
<div style="margin:24px 0;"><div class="kpi"><div class="kpi-val">{profile.get('total_rows',0):,}</div><div>Total Rows</div></div><div class="kpi"><div class="kpi-val">{profile.get('total_columns',0)}</div><div>Columns</div></div><div class="kpi"><div class="kpi-val">{profile.get('completeness_pct',100)}%</div><div>Completeness</div></div><div class="kpi"><div class="kpi-val">{profile.get('duplicate_rows',0)}</div><div>Duplicates</div></div></div>
<div style="background:#eff6ff;border-left:4px solid #3b82f6;padding:20px;border-radius:6px;margin:24px 0;"><h2>Executive AI Insights</h2>{insights_html}</div>
<h2>Analytical Visualizations</h2>{charts_html or '<p>No charts attached.</p>'}</div></body></html>"""

    @classmethod
    def generate_markdown_report(cls, metadata: Dict[str, Any], profile: Dict[str, Any], insights_markdown: str) -> str:
        return f"""# Data Intelligence Report: {metadata.get('file_name')}
*Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Dataset Summary
- **Rows**: {profile.get('total_rows', 0):,}
- **Columns**: {profile.get('total_columns', 0)}
- **Completeness**: {profile.get('completeness_pct', 100)}%
- **Duplicate Rows**: {profile.get('duplicate_rows', 0)}

## Executive AI Insights
{insights_markdown}
"""


# ==============================================================================
# 7. IN-MEMORY DEMO DATASET GENERATOR
# ==============================================================================
class DemoDataFactory:
    """Generates rich in-memory sample datasets without needing external files."""

    @staticmethod
    def get_sales_data() -> pd.DataFrame:
        np.random.seed(42)
        n = 500
        dates = pd.date_range("2023-01-01", periods=n, freq="D")
        categories = np.random.choice(["Electronics", "Home & Kitchen", "Apparel", "Office Supplies", "Books"], n)
        regions = np.random.choice(["North America", "Europe", "Asia-Pacific", "Latin America", "Middle East"], n)
        channels = np.random.choice(["Online", "Retail Store", "Direct Sales", "Distributor"], n)
        units = np.random.randint(1, 50, n)
        unit_prices = np.random.choice([19.99, 49.99, 120.00, 299.99, 850.00], n)
        discounts = np.random.choice([0.0, 0.05, 0.1, 0.15, 0.25], n)
        revenue = np.round(units * unit_prices * (1 - discounts), 2)
        profit = np.round(revenue - (units * unit_prices * np.random.uniform(0.4, 0.7, n)), 2)
        df = pd.DataFrame({"Order_Date": dates, "Region": regions, "Category": categories, "Sales_Channel": channels, "Units_Sold": units, "Unit_Price": unit_prices, "Discount_Rate": discounts, "Total_Revenue": revenue, "Total_Profit": profit})
        df.loc[3, "Total_Revenue"] = 45000.0  # intentional outlier
        return df

    @staticmethod
    def get_churn_data() -> pd.DataFrame:
        np.random.seed(42)
        n = 300
        df = pd.DataFrame({
            "CustomerID": [f"CUST-{1000+i}" for i in range(n)],
            "Gender": np.random.choice(["Female", "Male"], n),
            "Tenure_Months": np.random.randint(1, 72, n),
            "Contract_Type": np.random.choice(["Month-to-month", "One year", "Two year"], n),
            "Payment_Method": np.random.choice(["Electronic check", "Mailed check", "Bank transfer", "Credit card"], n),
            "Monthly_Charges": np.round(np.random.uniform(20.0, 115.0, n), 2),
            "Churn": np.where(np.random.rand(n) < 0.25, "Yes", "No"),
        })
        return df

    @staticmethod
    def get_sensor_data() -> pd.DataFrame:
        np.random.seed(42)
        n = 800
        timestamps = pd.date_range("2024-06-01", periods=n, freq="15min")
        temps = np.round(np.random.normal(72.5, 4.2, n), 2)
        return pd.DataFrame({
            "Timestamp": timestamps,
            "Sensor_ID": np.random.choice(["SENSOR-A1", "SENSOR-B2", "SENSOR-C3"], n),
            "Temperature_C": temps,
            "Pressure_PSI": np.round(np.random.normal(101.3, 2.5, n), 2),
            "Machine_Status": np.where(temps > 81.0, "WARNING", "NORMAL"),
        })


# ==============================================================================
# 8. STREAMLIT USER INTERFACE
# ==============================================================================
st.set_page_config(page_title="Data Insight AI Agent", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# Initialize Session States
if "df" not in st.session_state: st.session_state.df = None
if "metadata" not in st.session_state: st.session_state.metadata = {}
if "profile" not in st.session_state: st.session_state.profile = {}
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "executive_insights" not in st.session_state: st.session_state.executive_insights = None
if "pending_prompt" not in st.session_state: st.session_state.pending_prompt = None

def set_active_df(df: pd.DataFrame, name: str):
    st.session_state.df = df
    st.session_state.metadata = {"file_name": name, "detected_format": os.path.splitext(name)[1].replace(".", "") or "csv"}
    st.session_state.profile = DataProfiler.profile(df)
    st.session_state.executive_insights = None

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/brain.png", width=64)
    st.title("Settings & Data")

    api_key_input = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password", help="Optional: Enter Google Gemini key. If blank, offline engine is used.")
    model_choice = st.selectbox("Model", ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash"])
    st.success("🟢 Gemini Connected") if api_key_input else st.info("🟡 Offline Statistical Mode")

    st.markdown("---")
    st.subheader("📁 Load Sample Datasets")
    demo_choice = st.selectbox("Choose demo:", ["None", "📈 Retail Sales (CSV)", "👥 Customer Churn (Excel)", "⚡ IoT Sensors (Stream)"])
    if demo_choice != "None" and st.button("Load Dataset", use_container_width=True):
        if "Sales" in demo_choice: set_active_df(DemoDataFactory.get_sales_data(), "sales_data.csv")
        elif "Churn" in demo_choice: set_active_df(DemoDataFactory.get_churn_data(), "customer_churn.xlsx")
        elif "Sensor" in demo_choice: set_active_df(DemoDataFactory.get_sensor_data(), "sensor_readings.parquet")
        st.session_state.chat_history.append({"role": "assistant", "content": f"Loaded demo dataset **{demo_choice}** ({len(st.session_state.df):,} rows x {len(st.session_state.df.columns)} columns)!", "fig": None, "result_df": None, "code": None})
        st.rerun()

    if st.session_state.df is not None:
        st.markdown("---")
        st.subheader("📊 Active Dataset")
        st.write(f"**Source:** `{st.session_state.metadata.get('file_name')}`")
        st.write(f"**Rows:** {len(st.session_state.df):,} | **Cols:** {len(st.session_state.df.columns)}")
        st.write(f"**Completeness:** {st.session_state.profile.get('completeness_pct', 100)}%")
        if st.button("Clear Dataset", type="secondary", use_container_width=True):
            st.session_state.df = None
            st.session_state.metadata = {}
            st.session_state.profile = {}
            st.session_state.executive_insights = None
            st.rerun()

agent = DataAgent(api_key=api_key_input, model_name=model_choice)

# Main Title
st.markdown("<h1 style='color:#1e3a8a;margin-bottom:0;'>🧠 Data Insight AI Agent</h1>", unsafe_allow_html=True)
st.caption("Universal data intelligence. Ingest any file format, profile statistics, generate interactive charts, and run natural-language prompts.")

# Tabs
tab_ai, tab_ingest, tab_profile, tab_viz, tab_report = st.tabs(["💬 AI Agent & Chat", "📂 Ingestion & Preview", "📊 Profiling & Hygiene", "📈 Visualizations", "📑 Export Report"])

# TAB 1: Chat & AI Prompts
with tab_ai:
    if st.session_state.df is None:
        st.info("👋 Welcome! Upload a file in the **'📂 Ingestion & Preview'** tab, click a demo dataset in the sidebar, or click a quick-start button below:")
        q1, q2, q3 = st.columns(3)
        if q1.button("📈 Load Retail Sales & Profit (CSV)", use_container_width=True):
            set_active_df(DemoDataFactory.get_sales_data(), "sales_data.csv")
            st.rerun()
        if q2.button("👥 Load Customer Churn (Excel)", use_container_width=True):
            set_active_df(DemoDataFactory.get_churn_data(), "customer_churn.xlsx")
            st.rerun()
        if q3.button("⚡ Load IoT Sensors (Parquet)", use_container_width=True):
            set_active_df(DemoDataFactory.get_sensor_data(), "sensor_readings.parquet")
            st.rerun()
        st.markdown("---")
    else:
        st.subheader("🧠 Executive AI Strategic Insights")
        c1, c2 = st.columns([3, 1])
        with c1: st.caption(f"Active dataset: `{st.session_state.metadata.get('file_name')}` ({len(st.session_state.df):,} rows x {len(st.session_state.df.columns)} columns)")
        with c2:
            if st.button("🚀 Generate Executive Summary", type="primary", use_container_width=True):
                with st.spinner("Synthesizing strategic insights..."):
                    st.session_state.executive_insights = agent.generate_executive_insights(st.session_state.df, st.session_state.profile)
                    st.rerun()

        if st.session_state.executive_insights:
            with st.expander("📑 View Executive AI Summary & Strategic Takeaways", expanded=True):
                st.markdown(st.session_state.executive_insights)

        st.markdown("---")
        st.subheader("💬 Prompt Suggestions")
        num_c = st.session_state.profile.get("col_types", {}).get("numeric", [])
        cat_c = st.session_state.profile.get("col_types", {}).get("categorical", [])
        t_num = num_c[0] if num_c else "value"
        t_cat = cat_c[0] if cat_c else "category"

        suggs = [f"What are the top 5 {t_cat} by total {t_num}?", f"Plot the distribution and outliers of {t_num}", "Show summary statistics for all numeric columns", "Are there any missing values or anomalies?"]
        p_cols = st.columns(len(suggs))
        for i, s_text in enumerate(suggs):
            if p_cols[i].button(s_text, key=f"sugg_{i}", use_container_width=True):
                st.session_state.pending_prompt = s_text
                st.rerun()

    st.subheader("💬 Conversation & Query History")
    if not st.session_state.chat_history:
        st.info("No messages yet. Type your prompt in the chat box below!")
    else:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("fig") is not None: st.plotly_chart(msg["fig"], use_container_width=True)
                if msg.get("result_df") is not None: st.dataframe(msg["result_df"], use_container_width=True)
                if msg.get("code"):
                    with st.expander("🛠️ View Executed Python Code"): st.code(msg["code"], language="python")

# TAB 2: Ingestion & Preview
with tab_ingest:
    st.subheader("Upload Any Data File")
    uploaded = st.file_uploader("Upload dataset", type=["csv", "tsv", "xlsx", "xls", "ods", "json", "jsonl", "parquet", "feather", "db", "sqlite", "txt"])
    if uploaded is not None:
        if st.session_state.metadata.get("file_name") != uploaded.name:
            with st.spinner("Ingesting dataset..."):
                try:
                    df, meta = IngestionEngine.load_data(uploaded, uploaded.name)
                    st.session_state.df = df
                    st.session_state.metadata = meta
                    st.session_state.profile = DataProfiler.profile(df)
                    st.session_state.chat_history.append({"role": "assistant", "content": f"Uploaded **{uploaded.name}** ({len(df):,} rows x {len(df.columns)} cols). Ask me anything in the chat!", "fig": None, "result_df": None, "code": None})
                    st.success(f"Loaded {uploaded.name} successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading file: {str(e)}")

    if st.session_state.df is not None:
        st.dataframe(st.session_state.df.head(100), use_container_width=True)
    else:
        st.info("Upload a file or choose a demo dataset in the sidebar.")

# TAB 3: Profiling & Hygiene
with tab_profile:
    if st.session_state.df is not None:
        prof = st.session_state.profile
        st.subheader("📊 Dataset Health & Statistical Profiling")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Rows", f"{prof.get('total_rows', 0):,}")
        k2.metric("Features", f"{prof.get('total_columns', 0)}")
        k3.metric("Completeness", f"{prof.get('completeness_pct', 100)}%")
        k4.metric("Duplicates", f"{prof.get('duplicate_rows', 0)}")

        if prof.get("alerts"):
            for a in prof["alerts"]: st.warning(a)

        if prof.get("numeric_stats"):
            st.markdown("### 🔢 Numeric Summary")
            st.dataframe(pd.DataFrame(prof["numeric_stats"]).T, use_container_width=True)

        if any(v["count"] > 0 for v in prof.get("outlier_summary", {}).values()):
            st.markdown("### 🔍 Outlier Detection (1.5*IQR)")
            st.dataframe(pd.DataFrame([{"Feature": col, **info} for col, info in prof["outlier_summary"].items() if info["count"] > 0]), use_container_width=True)
    else:
        st.info("Load a dataset first.")

# TAB 4: Visualizations
with tab_viz:
    if st.session_state.df is not None:
        viz_mode = st.radio("Mode:", ["🌟 Smart Curated Visualizations", "🛠️ Custom Chart Builder"], horizontal=True)
        if viz_mode == "🌟 Smart Curated Visualizations":
            charts = Visualizer.generate_smart_charts(st.session_state.df, st.session_state.profile)
            for c in charts:
                st.markdown(f"#### {c['title']}")
                st.caption(c["description"])
                st.plotly_chart(c["fig"], use_container_width=True)
                st.markdown("---")
        else:
            df = st.session_state.df
            cols = ["None"] + list(df.columns)
            c1, c2, c3 = st.columns(3)
            ctype = c1.selectbox("Chart Type", ["Bar", "Line", "Scatter", "Area", "Histogram", "Box", "Violin", "Pie", "Treemap", "Heatmap"])
            xcol = c2.selectbox("X-Axis", list(df.columns))
            ycol = c3.selectbox("Y-Axis", cols, index=1 if len(cols) > 2 else 0)
            c4, c5, c6 = st.columns(3)
            ccolor = c4.selectbox("Color Group", cols)
            cfacet = c5.selectbox("Facet Subplot", cols)
            ctheme = c6.selectbox("Color Theme", ["Viridis", "Plasma", "Plotly", "Tealgrn", "Sunset"])
            try:
                fig_c = Visualizer.create_custom_chart(df, ctype, x_col=xcol, y_col=None if ycol == "None" else ycol, color_col=ccolor, facet_col=cfacet, color_theme=ctheme)
                st.plotly_chart(fig_c, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating chart: {e}")
    else:
        st.info("Load a dataset first.")

# TAB 5: Export Report
with tab_report:
    if st.session_state.df is not None:
        st.subheader("📑 Export Executive Intelligence Reports")
        insights = st.session_state.executive_insights or "No executive insights synthesized yet. Visit AI Agent tab to generate."
        c_r1, c_r2 = st.columns(2)
        with c_r1:
            html = ReportGenerator.generate_html_report(st.session_state.metadata, st.session_state.profile, insights, Visualizer.generate_smart_charts(st.session_state.df, st.session_state.profile))
            st.download_button("📥 Download Standalone HTML Report", data=html, file_name=f"Report_{st.session_state.metadata.get('file_name', 'data')}.html", mime="text/html", type="primary", use_container_width=True)
        with c_r2:
            md = ReportGenerator.generate_markdown_report(st.session_state.metadata, st.session_state.profile, insights)
            st.download_button("📥 Download Markdown Report", data=md, file_name=f"Report_{st.session_state.metadata.get('file_name', 'data')}.md", mime="text/markdown", use_container_width=True)
    else:
        st.info("Load a dataset first.")

# PERSISTENT GLOBAL CHAT INPUT
user_prompt = st.chat_input("💬 Ask the AI Agent anything, write a prompt, or request a chart...")
prompt_to_run = user_prompt or st.session_state.pending_prompt
st.session_state.pending_prompt = None

if prompt_to_run:
    st.session_state.chat_history.append({"role": "user", "content": prompt_to_run})
    if st.session_state.df is None:
        pl = prompt_to_run.lower()
        if any(w in pl for w in ["sales", "retail"]): set_active_df(DemoDataFactory.get_sales_data(), "sales_data.csv")
        elif any(w in pl for w in ["churn", "customer"]): set_active_df(DemoDataFactory.get_churn_data(), "customer_churn.xlsx")
        elif any(w in pl for w in ["sensor", "iot"]): set_active_df(DemoDataFactory.get_sensor_data(), "sensor_readings.parquet")

    with st.spinner("Analyzing data and generating charts..."):
        res = agent.chat_query(prompt_to_run, st.session_state.df, st.session_state.profile, st.session_state.chat_history[:-1])
        st.session_state.chat_history.append({"role": "assistant", "content": res["answer"], "fig": res.get("fig"), "result_df": res.get("result_df"), "code": res.get("code")})
    st.rerun()
