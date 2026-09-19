# 🧠 Data Insight AI Agent

An autonomous Data Analysis, Interactive Visualization, and Insight-Generating AI Agent capable of ingesting arbitrary data files, profiling distributions, detecting outliers and hygiene issues, building interactive charts, and providing conversational AI data assistance via a sandboxed Code Interpreter.

---

## 🌟 Key Features

1. **Universal Multi-Format Ingestion**:
   - **Tabular**: CSV (`.csv`), TSV (`.tsv`), Excel (`.xlsx`, `.xls`, `.ods` with multi-sheet switcher).
   - **Columnar**: Apache Parquet (`.parquet`, `.pq`), Feather (`.feather`).
   - **Semi-Structured**: JSON (`.json`, `.jsonl` with automatic record flattening).
   - **Relational Databases**: SQLite (`.db`, `.sqlite`, `.sqlite3` with multi-table browser).
   - **Unstructured / Logs**: Delimited text files (`.txt`, `.log`).

2. **Deep Statistical Profiling & Hygiene**:
   - Automatic feature type classification (Numeric, Categorical, Datetime, Boolean, Text ID).
   - Descriptive statistics (Mean, Median, Std, Quartiles, Skewness, Zero counts).
   - Data hygiene audits: Missingness % heatmap, duplicate row counter, constant feature alerts.
   - Outlier detection using Interquartile Range (IQR) bounds.
   - Pearson correlation matrix with automated strongest relationship detection.

3. **Smart Interactive Visualizations (Plotly)**:
   - Automated insight charts (Time-series trends with range sliders, correlation heatmaps, categorical frequencies, distribution histograms with box marginals, bivariate scatter with regression trendlines).
   - Custom Interactive Chart Builder (Bar, Line, Scatter, Area, Histogram, Box, Violin, Pie, Treemap, Heatmap) with color groupings, facet subplots, and customizable palettes.

4. **Conversational AI Agent & Code Interpreter**:
   - Powered by Google Gemini (`gemini-2.5-flash`, `gemini-1.5-pro`) or an offline statistical fallback engine.
   - Natural language Q&A: translates user questions into safe Python/Pandas/Plotly scripts.
   - Sandboxed local execution environment with security guards against unauthorized system calls.
   - Dynamic rendering of answers, interactive charts, and data tables.

5. **Stakeholder Export**:
   - Download standalone responsive HTML reports with embedded interactive Plotly charts.
   - Download Markdown summary reports.
   - Export processed & cleaned CSV files.

---

## 🚀 Quickstart Guide

### 1. Run the Application
From the project directory:
```bash
python -m streamlit run app.py
```

### 2. Configure AI (Optional)
Add your Gemini API Key in the sidebar or create a `.env` file:
```env
GEMINI_API_KEY=your_key_here
```
*(If no API key is provided, the agent runs in offline statistical reasoning mode with automated profiling and rule-based queries).*

### 3. Try Demo Datasets
In the sidebar, use the **Load Sample Datasets** dropdown to test:
- 📈 `sales_data.csv` (Retail transactions)
- 👥 `customer_churn.xlsx` (Multi-sheet customer and subscription data)
- 📱 `app_metrics.json` (Nested app telemetry)
- ⚡ `sensor_readings.parquet` (High-frequency IoT sensors)
- 🏢 `company_analytics.db` (SQLite relational database)

---

## 📂 Project Architecture

```
data-insight-agent/
├── app.py                      # Main Streamlit web application & user interface
├── requirements.txt            # Package dependencies
├── .env.example                # Sample environment configuration
├── README.md                   # System documentation
├── core/
│   ├── __init__.py
│   ├── ingestion.py            # Multi-format data loader & schema detector
│   ├── profiler.py             # Statistical profiling, hygiene & outlier engine
│   ├── visualizer.py           # Plotly smart charts & interactive chart builder
│   ├── code_interpreter.py     # Sandboxed execution of generated Python code
│   ├── agent.py                # Gemini orchestration & conversational reasoning
│   └── report_generator.py     # HTML & Markdown report exporter
├── samples/                    # Pre-generated sample datasets
│   ├── generate_samples.py
│   ├── sales_data.csv
│   ├── customer_churn.xlsx
│   ├── app_metrics.json
│   ├── sensor_readings.parquet
│   └── company_analytics.db
└── tests/
    └── test_agent_suite.py     # Automated unit test suite
```

---

## 🧪 Running Unit Tests
```bash
python tests/test_agent_suite.py
```
All 10 unit tests cover multi-format ingestion, profiling, chart generation, sandboxed execution, and report generation.
