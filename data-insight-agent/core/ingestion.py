"""
Universal Multi-Format Ingestion Engine.
Supports CSV, TSV, Excel (.xlsx, .xls, .ods), JSON, Parquet, Feather, SQLite, and structured text.
"""

import io
import os
import csv
import json
import sqlite3
from typing import Dict, Any, Tuple, List, Optional
import pandas as pd


class IngestionEngine:
    """Universal data loader that normalizes arbitrary files into Pandas DataFrames."""

    @staticmethod
    def detect_format(file_name: str) -> str:
        ext = os.path.splitext(file_name)[1].lower()
        mapping = {
            ".csv": "csv",
            ".tsv": "tsv",
            ".txt": "text",
            ".xlsx": "excel",
            ".xls": "excel",
            ".ods": "excel",
            ".json": "json",
            ".jsonl": "jsonl",
            ".parquet": "parquet",
            ".pq": "parquet",
            ".feather": "feather",
            ".db": "sqlite",
            ".sqlite": "sqlite",
            ".sqlite3": "sqlite",
        }
        return mapping.get(ext, "unknown")

    @staticmethod
    def inspect_sqlite(file_bytes_or_path) -> List[str]:
        """Returns list of table names from a SQLite database."""
        try:
            if isinstance(file_bytes_or_path, (bytes, io.BytesIO)):
                if isinstance(file_bytes_or_path, io.BytesIO):
                    raw_bytes = file_bytes_or_path.getvalue()
                else:
                    raw_bytes = file_bytes_or_path
                
                temp_db = sqlite3.connect(":memory:")
                temp_db.deserialize(raw_bytes)
                cursor = temp_db.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
                temp_db.close()
                return tables
            elif isinstance(file_bytes_or_path, str) and os.path.exists(file_bytes_or_path):
                conn = sqlite3.connect(file_bytes_or_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
                conn.close()
                return tables
        except Exception:
            pass
        return []

    @staticmethod
    def inspect_excel_sheets(file_obj) -> List[str]:
        """Returns sheet names from an Excel file without leaking the file handle."""
        try:
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
            with pd.ExcelFile(file_obj) as excel_file:
                sheets = list(excel_file.sheet_names)
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
            return sheets
        except Exception:
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
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
        """
        Loads data from file object or path into a Pandas DataFrame.
        Returns (dataframe, metadata_dict).
        """
        fmt = cls.detect_format(file_name)
        df: Optional[pd.DataFrame] = None
        metadata: Dict[str, Any] = {
            "file_name": file_name,
            "detected_format": fmt,
            "available_sheets": [],
            "available_tables": [],
            "warnings": [],
        }

        # 1. CSV / TSV / Text
        if fmt in ("csv", "tsv", "text"):
            content_sample = None
            if hasattr(file_obj, "read"):
                pos = file_obj.tell() if hasattr(file_obj, "tell") else 0
                sample_bytes = file_obj.read(4096)
                if hasattr(file_obj, "seek"):
                    file_obj.seek(pos)
                
                try:
                    content_sample = sample_bytes.decode("utf-8")
                    encoding = "utf-8"
                except UnicodeDecodeError:
                    content_sample = sample_bytes.decode("latin-1", errors="replace")
                    encoding = "latin-1"
            else:
                encoding = "utf-8"

            delimiter = "," if fmt == "csv" else ("\t" if fmt == "tsv" else None)
            if delimiter is None and content_sample:
                try:
                    dialect = csv.Sniffer().sniff(content_sample)
                    delimiter = dialect.delimiter
                except Exception:
                    delimiter = ","

            try:
                df = pd.read_csv(file_obj, sep=delimiter, encoding=encoding, on_bad_lines="skip")
            except Exception:
                if hasattr(file_obj, "seek"):
                    file_obj.seek(0)
                df = pd.read_csv(file_obj, sep=None, engine="python", on_bad_lines="skip")

        # 2. Excel
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

        # 6. SQLite
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
                metadata["warnings"].append("No tables found in SQLite database.")
            conn.close()

        else:
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
            df = pd.read_csv(file_obj, on_bad_lines="skip")

        if df is None:
            raise ValueError(f"Unable to parse dataset from {file_name}")

        # Clean column names
        df.columns = [str(c).strip() for c in df.columns]

        # Auto-parse datetime columns
        for col in df.columns:
            if df[col].dtype == "object":
                col_lower = col.lower()
                if any(kw in col_lower for kw in ["date", "time", "timestamp", "created_at", "updated_at", "year_month"]):
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
