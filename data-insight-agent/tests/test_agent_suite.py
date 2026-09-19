"""
Comprehensive Unit Test Suite for Data Insight Agent.
Tests:
- IngestionEngine across CSV, Excel, JSON, Parquet, SQLite
- DataProfiler profiling, data hygiene, and outlier detection
- Visualizer smart chart generation & custom chart builder
- CodeInterpreter execution, plotly output, and sandboxing
- ReportGenerator HTML and Markdown output
"""

import os
import sys
import unittest
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.ingestion import IngestionEngine
from core.profiler import DataProfiler
from core.visualizer import Visualizer
from core.code_interpreter import CodeInterpreter
from core.report_generator import ReportGenerator


class TestDataInsightAgent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.samples_dir = os.path.join(PROJECT_ROOT, "samples")

    def test_01_ingest_csv(self):
        csv_path = os.path.join(self.samples_dir, "sales_data.csv")
        self.assertTrue(os.path.exists(csv_path), "sales_data.csv must exist")
        df, meta = IngestionEngine.load_data(csv_path, "sales_data.csv")
        self.assertFalse(df.empty)
        self.assertEqual(meta["detected_format"], "csv")
        self.assertIn("Total_Revenue", df.columns)
        self.assertEqual(len(df), 500)

    def test_02_ingest_excel_multi_sheet(self):
        xlsx_path = os.path.join(self.samples_dir, "customer_churn.xlsx")
        self.assertTrue(os.path.exists(xlsx_path))
        # Inspect sheets
        sheets = IngestionEngine.inspect_excel_sheets(xlsx_path)
        self.assertIn("Customers", sheets)
        self.assertIn("Subscription_Plans", sheets)

        # Load first sheet
        df1, meta1 = IngestionEngine.load_data(xlsx_path, "customer_churn.xlsx", sheet_name="Customers")
        self.assertEqual(meta1["selected_sheet"], "Customers")
        self.assertIn("CustomerID", df1.columns)

        # Load second sheet
        df2, meta2 = IngestionEngine.load_data(xlsx_path, "customer_churn.xlsx", sheet_name="Subscription_Plans")
        self.assertEqual(meta2["selected_sheet"], "Subscription_Plans")
        self.assertIn("Plan_Name", df2.columns)

    def test_03_ingest_json(self):
        json_path = os.path.join(self.samples_dir, "app_metrics.json")
        self.assertTrue(os.path.exists(json_path))
        df, meta = IngestionEngine.load_data(json_path, "app_metrics.json")
        self.assertFalse(df.empty)
        self.assertIn("active_users", df.columns)

    def test_04_ingest_parquet(self):
        pq_path = os.path.join(self.samples_dir, "sensor_readings.parquet")
        self.assertTrue(os.path.exists(pq_path))
        df, meta = IngestionEngine.load_data(pq_path, "sensor_readings.parquet")
        self.assertFalse(df.empty)
        self.assertIn("Temperature_C", df.columns)
        self.assertEqual(len(df), 1000)

    def test_05_ingest_sqlite(self):
        db_path = os.path.join(self.samples_dir, "company_analytics.db")
        self.assertTrue(os.path.exists(db_path))
        tables = IngestionEngine.inspect_sqlite(db_path)
        self.assertIn("employees", tables)
        self.assertIn("departments", tables)

        df, meta = IngestionEngine.load_data(db_path, "company_analytics.db", table_name="employees")
        self.assertFalse(df.empty)
        self.assertIn("salary", df.columns)

    def test_06_data_profiler(self):
        csv_path = os.path.join(self.samples_dir, "sales_data.csv")
        df, _ = IngestionEngine.load_data(csv_path, "sales_data.csv")
        profile = DataProfiler.profile(df)

        self.assertEqual(profile["total_rows"], 500)
        self.assertIn("Total_Revenue", profile["numeric_stats"])
        self.assertIn("Region", profile["categorical_stats"])
        self.assertIn("Order_Date", profile["datetime_stats"])
        # Outlier detection
        self.assertIn("Total_Revenue", profile["outlier_summary"])
        self.assertGreater(profile["outlier_summary"]["Total_Revenue"]["count"], 0)
        # LLM prompt summary
        self.assertIn("Dataset Dimensions:", profile["llm_summary_prompt"])

    def test_07_visualizer_smart_charts(self):
        csv_path = os.path.join(self.samples_dir, "sales_data.csv")
        df, _ = IngestionEngine.load_data(csv_path, "sales_data.csv")
        profile = DataProfiler.profile(df)
        charts = Visualizer.generate_smart_charts(df, profile)

        self.assertGreater(len(charts), 0)
        for c in charts:
            self.assertIn("title", c)
            self.assertIn("fig", c)

    def test_08_code_interpreter_execution(self):
        csv_path = os.path.join(self.samples_dir, "sales_data.csv")
        df, _ = IngestionEngine.load_data(csv_path, "sales_data.csv")

        code = """
result_df = df.groupby('Region')['Total_Revenue'].sum().reset_index()
fig = px.bar(result_df, x='Region', y='Total_Revenue', title='Regional Revenue')
print(f"Top Region: {result_df.iloc[0]['Region']}")
"""
        res = CodeInterpreter.execute(code, df)
        self.assertTrue(res["success"])
        self.assertIsNotNone(res["fig"])
        self.assertIsNotNone(res["result_df"])
        self.assertIn("Top Region:", res["stdout"])

    def test_09_code_interpreter_safety_block(self):
        csv_path = os.path.join(self.samples_dir, "sales_data.csv")
        df, _ = IngestionEngine.load_data(csv_path, "sales_data.csv")

        malicious_code = "import os\nos.listdir('.')"
        res = CodeInterpreter.execute(malicious_code, df)
        self.assertFalse(res["success"])
        self.assertIn("restricted for security", res["error"])

    def test_10_report_generator(self):
        csv_path = os.path.join(self.samples_dir, "sales_data.csv")
        df, meta = IngestionEngine.load_data(csv_path, "sales_data.csv")
        profile = DataProfiler.profile(df)
        insights = "### Executive Summary\nStrong overall performance across regions."

        html = ReportGenerator.generate_html_report(meta, profile, insights)
        self.assertIn("AI Data Intelligence & Analytics Report", html)
        self.assertIn("sales_data.csv", html)

        md = ReportGenerator.generate_markdown_report(meta, profile, insights)
        self.assertIn("# Data Intelligence Report: sales_data.csv", md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
