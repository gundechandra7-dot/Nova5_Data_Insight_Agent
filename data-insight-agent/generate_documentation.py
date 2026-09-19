"""
Script to generate:
1. Data_Insight_AI_Agent_Documentation.docx (Complete Microsoft Word Document)
2. Data_Insight_AI_Agent_Whitepaper.html (Beautiful standalone printable whitepaper)
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

DOCS_DIR = r"C:\Users\HP\.gemini\antigravity\scratch\data-insight-agent"
os.makedirs(DOCS_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. BUILD WORD DOCUMENT (.docx)
# -----------------------------------------------------------------------------
def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def create_docx():
    doc = Document()

    # Set page margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Styles
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = title_p.add_run("DATA INSIGHT AI AGENT")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(26)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(30, 58, 138)  # Deep Navy

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = sub_p.add_run("Technical Whitepaper, System Architecture & Operational Blueprint")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(14)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(100, 116, 139)

    meta_p = doc.add_paragraph()
    meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_meta = meta_p.add_run("Universal Multi-Format Ingestion | Agentic Code Interpreter | Automated Visual Analytics")
    run_meta.font.name = "Arial"
    run_meta.font.size = Pt(10)
    run_meta.font.color.rgb = RGBColor(71, 85, 105)

    doc.add_paragraph().paragraph_format.space_after = Pt(18)

    # 1. Executive Summary
    h1 = doc.add_heading("1. Executive Overview & Mission", level=1)
    h1.paragraph_format.space_before = Pt(12)
    
    p = doc.add_paragraph(
        "The Data Insight AI Agent is an autonomous, end-to-end data intelligence system engineered "
        "to compress the exploratory data analysis (EDA) and business insight lifecycle from hours "
        "to seconds. Organizations frequently struggle with fragmented data silos formatted across CSV, "
        "multi-tab Excel workbooks, nested JSON payloads, columnar Parquet files, and relational SQLite "
        "databases. Traditional BI suites require manual schema mapping, SQL query authoring, and rigid dashboard design.\n\n"
        "This platform introduces an agentic AI paradigm: an intelligent agent that universally ingests arbitrary "
        "files, executes deep non-parametric statistical profiling, automatically renders multi-dimensional "
        "Plotly visualizations, and provides natural-language conversational reasoning backed by a sandboxed "
        "Python Code Interpreter with self-healing capabilities."
    )
    p.paragraph_format.space_after = Pt(12)

    # 2. System Architecture
    doc.add_heading("2. System Architecture & Component Design", level=1)
    doc.add_paragraph(
        "The architecture is organized into five decoupled, highly cohesive modular layers designed for "
        "low latency, high data hygiene, and fail-safe execution:"
    )

    # Architecture Table
    table = doc.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    hdr_cells = table.rows[0].cells
    hdr_titles = ["System Layer", "Core Engine Module", "Key Responsibilities"]
    for i, title in enumerate(hdr_titles):
        hdr_cells[i].text = title
        hdr_cells[i].paragraphs[0].runs[0].font.bold = True
        hdr_cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(hdr_cells[i], "1E3A8A")

    layers = [
        ("1. Ingestion Layer", "core/ingestion.py", "Universal file parser detecting signatures for CSV, TSV, XLSX, XLS, ODS, JSON, JSONL, Parquet, Feather, SQLite DB, and structured text. Normalizes inputs into optimized DataFrames."),
        ("2. Profiling & Hygiene", "core/profiler.py", "Performs schema inference, completeness audits, missingness % analysis, duplicate tracking, IQR outlier identification, and Pearson correlation matrices."),
        ("3. Visualization Layer", "core/visualizer.py", "Automated smart charts (distributions, trends, correlations, categorical breakdowns) and an interactive 10-type custom chart builder powered by Plotly."),
        ("4. AI Reasoning & Execution", "core/agent.py & core/code_interpreter.py", "Orchestrates Google Gemini foundation models, generates sandboxed Python code, parses AST security restrictions, executes code safely, and self-heals syntax errors."),
        ("5. Presentation & Export", "app.py & core/report_generator.py", "Responsive Streamlit dashboard with a persistent bottom chat bar, interactive data grids, KPI scorecards, and 1-click HTML/Markdown report export."),
    ]

    for layer, mod, resp in layers:
        row_cells = table.add_row().cells
        row_cells[0].text = layer
        row_cells[0].paragraphs[0].runs[0].font.bold = True
        row_cells[1].text = mod
        row_cells[2].text = resp
        for c in row_cells:
            set_cell_background(c, "F8FAFC")

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # 3. Machine Learning & AI Taxonomy
    doc.add_heading("3. Machine Learning & AI Taxonomy", level=1)
    doc.add_paragraph(
        "The platform combines Generative Foundation AI with Classical Statistical Learning:"
    )

    p_ai = doc.add_paragraph()
    p_ai.add_run("A. Large Language Models (Generative AI):\n").bold = True
    p_ai.add_run(
        "The agent integrates Google Gemini models (gemini-2.5-flash, gemini-1.5-pro, gemini-1.5-flash) "
        "via the official google-genai SDK. These multimodal/reasoning LLMs are leveraged for:\n"
        "  • Intent Extraction: Discerning user analytical objectives from ambiguous prompts.\n"
        "  • Code Synthesis: Translating natural questions into verified pandas/duckdb/plotly execution code.\n"
        "  • Strategic Synthesis: Converting raw numerical matrices into executive strategic narratives.\n\n"
    )

    p_ai.add_run("B. Agentic Archetype (ReAct & Code Interpreter Pattern):\n").bold = True
    p_ai.add_run(
        "The agent operates under the Reason-Act-Observe-Reflect architecture. Rather than hallucinating numerical "
        "answers directly, the agent acts as an autonomous data engineer that writes deterministic Python code, "
        "executes the script against the in-memory dataframe, inspects the standard output and generated Plotly objects, "
        "and synthesizes an answer based strictly on verified ground-truth data.\n\n"
    )

    p_ai.add_run("C. Classical Machine Learning & Descriptive Statistics:\n").bold = True
    p_ai.add_run(
        "  • Non-Parametric Distribution Modeling: Quantiles, interquartile ranges, skewness, and kurtosis.\n"
        "  • Bivariate Correlation Inference: Pearson product-moment linear correlation analysis.\n"
        "  • Parametric Linear Regression: Ordinary Least Squares (OLS) trendline fitting for continuous bivariate pairs."
    )

    # 4. Mathematical Formulations & Algorithms
    doc.add_heading("4. Algorithms & Mathematical Formulations", level=1)

    doc.add_heading("Algorithm 1: Outlier Detection via Tukey's Fences (IQR Method)", level=2)
    doc.add_paragraph(
        "To identify anomalies without assuming strict Gaussian normality across arbitrary datasets, "
        "the profiler computes the Interquartile Range (IQR) on all continuous numeric vectors:"
    )
    doc.add_paragraph(
        "  IQR = Q3 - Q1\n"
        "  Lower Fence = Q1 - 1.5 * IQR\n"
        "  Upper Fence = Q3 + 1.5 * IQR\n"
        "Any datum x falling outside [Lower Fence, Upper Fence] is flagged as an anomaly."
    )

    doc.add_heading("Algorithm 2: Pearson Product-Moment Correlation", level=2)
    doc.add_paragraph(
        "Linear dependencies between numerical features X and Y are computed using Pearson's correlation coefficient r:\n"
        "  r = Cov(X, Y) / (Std(X) * Std(Y))\n"
        "The engine surfaces feature pairs with |r| >= 0.5 as notable dependencies."
    )

    doc.add_heading("Algorithm 3: Sandboxed Execution & AST Security Filter", level=2)
    doc.add_paragraph(
        "Before executing any LLM-synthesized code snippet, the CodeInterpreter executes a lexical and regex guard "
        "that blocks dangerous system modules (os, sys, subprocess, shutil, socket, urllib, pathlib, __import__) "
        "and restricts file-write operations. Code runs within an isolated execution dictionary containing only "
        "df, pd, np, px, go, and duckdb."
    )

    doc.add_heading("Algorithm 4: Self-Healing Auto-Correction Loop", level=2)
    doc.add_paragraph(
        "If a generated code snippet triggers a runtime exception or syntax error, the agent intercepts the error traceback, "
        "injects the failure context into a targeted diagnostic prompt, and submits it back to the LLM for automated repair "
        "before returning results to the user."
    )

    # 5. Dual-Engine Architecture: Gemini vs Offline Fallback
    doc.add_heading("5. Model Strategy & Zero-Downtime Fallback", level=1)
    doc.add_paragraph(
        "A critical enterprise feature of this application is its dual-engine resiliency:"
    )
    doc.add_paragraph(
        "• Mode 1: Connected Mode (Gemini API):\n"
        "  When a GEMINI_API_KEY is supplied (via .env file or the live sidebar input), the agent unlocks unbounded "
        "  natural-language reasoning, nuanced ad-hoc query translation, custom calculations, and executive summaries.\n\n"
        "• Mode 2: Offline Statistical Engine:\n"
        "  If no API key is provided or if network connectivity is unavailable, the application gracefully operates "
        "  using a deterministic heuristic engine. The engine tokenizes user prompts to identify target metrics, "
        "  time dimensions, and categorical groupings, executing verified templates for distributions, trends, "
        "  scatter relationships, and data quality audits without crashing."
    )

    # 6. Security, API Key Management & Governance
    doc.add_heading("6. Security, Governance & API Management", level=1)
    doc.add_paragraph(
        "• API Key Protection: Keys are ingested via local .env files (using python-dotenv) or masked password input "
        "fields in Streamlit session state. Keys are never transmitted to third parties or logged to disk.\n"
        "• Sandboxed Compute: All pandas operations execute against memory copies of the DataFrame to prevent unintended mutations.\n"
        "• Data Privacy: In offline mode, zero data ever leaves the local machine. In Gemini mode, only column schemas, "
        "statistical summaries, and a tiny head preview (3-5 rows) are sent to the model."
    )

    # 7. Deployment & Hosting Guide
    doc.add_heading("7. Deployment & Infrastructure Blueprint", level=1)
    doc.add_paragraph(
        "• Streamlit Community Cloud (Recommended): Connect GitHub repository and deploy in 1 click.\n"
        "• Hugging Face Spaces: Native Streamlit runtime with free GPU/CPU tiers.\n"
        "• Docker / Container Deployment: Dockerfile with Python 3.11-3.14 and exposed port 8501.\n"
        "• Vercel Deployment: Can be deployed on Vercel via Stlite (Streamlit compiled to WebAssembly via Pyodide) "
        "for 100% static, client-side execution."
    )

    docx_path = os.path.join(DOCS_DIR, "Data_Insight_AI_Agent_Documentation.docx")
    doc.save(docx_path)
    print(f"Successfully generated DOCX: {docx_path}")
    return docx_path


# -----------------------------------------------------------------------------
# 2. BUILD STANDALONE HTML WHITEPAPER (.html)
# -----------------------------------------------------------------------------
def create_html_whitepaper():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Insight AI Agent - Technical Whitepaper & Documentary</title>
    <style>
        :root {
            --primary: #1e3a8a;
            --primary-light: #3b82f6;
            --accent: #10b981;
            --bg-page: #f8fafc;
            --bg-card: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --code-bg: #1e293b;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-page);
            color: var(--text-main);
            margin: 0;
            padding: 40px 20px;
            line-height: 1.65;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: var(--bg-card);
            border-radius: 14px;
            padding: 50px 60px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.06);
            border: 1px solid var(--border);
        }
        .header {
            border-bottom: 2px solid var(--border);
            padding-bottom: 30px;
            margin-bottom: 40px;
            text-align: center;
        }
        .badge {
            display: inline-block;
            background: #dbeafe;
            color: var(--primary);
            font-size: 12px;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: 999px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 12px;
        }
        h1 {
            color: var(--primary);
            font-size: 34px;
            margin: 0 0 12px 0;
            font-weight: 800;
        }
        .subtitle {
            font-size: 18px;
            color: var(--text-muted);
            max-width: 750px;
            margin: 0 auto 16px auto;
        }
        .meta-bar {
            font-size: 13px;
            color: var(--text-muted);
        }
        h2 {
            color: var(--primary);
            font-size: 22px;
            margin-top: 40px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        h3 {
            color: #1e293b;
            font-size: 17px;
            margin-top: 24px;
        }
        p, li {
            color: #334155;
            font-size: 15px;
        }
        .diagram-box {
            background: #f1f5f9;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 24px;
            margin: 20px 0;
            font-family: 'Courier New', Courier, monospace;
            font-size: 13px;
            overflow-x: auto;
            line-height: 1.4;
            color: #0f172a;
        }
        .callout {
            background: #eff6ff;
            border-left: 4px solid var(--primary-light);
            border-radius: 0 8px 8px 0;
            padding: 18px 22px;
            margin: 20px 0;
        }
        .callout-title {
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 6px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }
        th, td {
            border: 1px solid var(--border);
            padding: 12px 14px;
            text-align: left;
        }
        th {
            background: var(--primary);
            color: #ffffff;
            font-weight: 600;
        }
        tr:nth-child(even) {
            background: #f8fafc;
        }
        .formula-box {
            background: #fdf4ff;
            border: 1px solid #f0abfc;
            border-radius: 8px;
            padding: 14px 20px;
            margin: 16px 0;
            font-family: 'Times New Roman', Times, serif;
            font-size: 17px;
            color: #701a75;
        }
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin: 24px 0;
        }
        .card {
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        .card h4 {
            margin: 0 0 8px 0;
            color: var(--primary);
            font-size: 16px;
        }
        .code-block {
            background: var(--code-bg);
            color: #f8fafc;
            border-radius: 8px;
            padding: 16px;
            font-family: Consolas, Monaco, monospace;
            font-size: 13px;
            overflow-x: auto;
        }
        @media print {
            body { background: #fff; padding: 0; }
            .container { box-shadow: none; border: none; padding: 0; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="badge">Architecture Blueprint & Whitepaper</span>
            <h1>Data Insight AI Agent</h1>
            <div class="subtitle">An Autonomous, Multi-Format Data Intelligence Agent with Sandboxed Code Execution, Statistical Profiling & Interactive Visual Analytics</div>
            <div class="meta-bar">
                <strong>Model Core:</strong> Google Gemini 2.5 Flash / 1.5 Pro &nbsp;|&nbsp;
                <strong>Pattern:</strong> ReAct & Code Interpreter &nbsp;|&nbsp;
                <strong>Engine:</strong> Streamlit, Plotly, DuckDB, Pandas
            </div>
        </div>

        <h2>1. Executive Overview & Product Vision</h2>
        <p>The <strong>Data Insight AI Agent</strong> is an intelligent system designed to eliminate the friction of exploratory data analysis (EDA). Traditional data analysis workflows require data engineers to write bespoke ingestion scripts for different file formats, formulate manual SQL/pandas aggregations, and hand-craft charts in BI tools like Tableau or PowerBI.</p>
        <p>This system replaces manual EDA with a unified agentic loop: users provide arbitrary data files (CSV, multi-tab Excel, nested JSON, Parquet, or SQLite databases), and the agent autonomously handles ingestion, data hygiene audits, outlier discovery, interactive Plotly visualization, and conversational natural-language Q&A backed by deterministic Python code execution.</p>

        <h2>2. End-to-End System Architecture</h2>
        <div class="diagram-box">
+---------------------------------------------------------------------------------------------------+
|                                      USER / DATA ANALYST                                          |
+---------------------------------------------------------------------------------------------------+
                                                  |
                         (Uploads CSV, Excel, JSON, Parquet, SQLite OR Types Prompts)
                                                  v
+---------------------------------------------------------------------------------------------------+
| 1. UNIVERSAL INGESTION LAYER (core/ingestion.py)                                                  |
|    - Automatic magic-byte & extension detection                                                   |
|    - Delimiter sniffing & encoding fallback (UTF-8, Latin-1)                                      |
|    - Excel multi-sheet inspector & SQLite database schema inspector                               |
|    - Normalization into memory-optimized Pandas DataFrame (df)                                    |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
| 2. STATISTICAL PROFILER & HYGIENE ENGINE (core/profiler.py)                                       |
|    - Type classification: Numeric, Categorical, Datetime, Boolean, Text ID                       |
|    - Completeness Audit: Missing % per feature, Total missing cells, Duplicate record detector   |
|    - Outlier Detection: Tukey's Fences (1.5 * IQR bounds)                                         |
|    - Correlation Engine: Pearson Product-Moment correlation matrix & top dependencies (|r| >= 0.5)|
|    - LLM Prompt Synthesis: High-density contextual prompt serialization                          |
+---------------------------------------------------------------------------------------------------+
                                                  |
                         +------------------------+------------------------+
                         |                                                 |
                         v                                                 v
+--------------------------------------------------+  +--------------------------------------------+
| 3. VISUALIZATION ENGINE (core/visualizer.py)     |  | 4. AI AGENT REASONING (core/agent.py)      |
|    - Automated Smart Charts:                     |  |    - Foundation Model: Google Gemini       |
|      * Pearson Correlation Heatmap               |  |      (gemini-2.5-flash / gemini-1.5-pro)   |
|      * Temporal Trends with Range Sliders        |  |    - Zero-Downtime Offline Fallback        |
|      * Categorical Frequency & Donut Charts      |  |    - Natural Language to Code Synthesis   |
|      * Histograms with Marginal Box Plots        |  |    - Self-Healing Auto-Correction Loop    |
|    - Custom Interactive Chart Builder (10 types) |  +--------------------------------------------+
+--------------------------------------------------+                       |
                         |                                                 v
                         |                            +--------------------------------------------+
                         |                            | 5. SANDBOXED CODE INTERPRETER              |
                         |                            |    (core/code_interpreter.py)              |
                         |                            |    - AST Security Module Filter            |
                         |                            |    - Isolated Execution Scope              |
                         |                            |    - Real-time Plotly Figure Extraction    |
                         |                            +--------------------------------------------+
                         |                                                 |
                         +------------------------+------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
| 6. PRESENTATION & EXPORT LAYER (app.py & core/report_generator.py)                                |
|    - Streamlit Responsive Dashboard with Permanent Bottom Chat Box                                |
|    - Dynamic Plotly Interactive Charts, Summary DataGrids & Code Toggle Expander                  |
|    - 1-Click Exportable Standalone HTML Executive Reports & Markdown Summaries                    |
+---------------------------------------------------------------------------------------------------+
        </div>

        <h2>3. Machine Learning & AI Classification</h2>
        <div class="card-grid">
            <div class="card">
                <h4>🧠 Generative AI</h4>
                <p>Google Gemini 2.5 Flash / 1.5 Pro models orchestrate conversational understanding, complex query translation, and executive strategic synthesis.</p>
            </div>
            <div class="card">
                <h4>🤖 Agentic Archetype</h4>
                <p>Implements the <strong>ReAct (Reasoning + Acting)</strong> & <strong>Code Interpreter</strong> pattern. Never hallucinates numbers; it writes code to calculate ground truth.</p>
            </div>
            <div class="card">
                <h4>📊 Statistical ML</h4>
                <p>Non-parametric statistical profiling, quantiles, Interquartile Range (IQR) outlier modeling, and Pearson correlation coefficients.</p>
            </div>
            <div class="card">
                <h4>🛡️ Self-Healing Execution</h4>
                <p>Reflection loop that catches runtime exceptions, reflects on tracebacks, and automatically submits auto-repair prompts.</p>
            </div>
        </div>

        <h2>4. Core Mathematical Algorithms</h2>

        <h3>A. Outlier Detection via Tukey's Fences (IQR Method)</h3>
        <p>Unlike Z-score metrics that incorrectly assume Gaussian normal distribution, the agent employs non-parametric Interquartile Range fences to detect outliers robustly:</p>
        <div class="formula-box">
            <strong>IQR = Q3 - Q1</strong><br>
            Lower Bound = Q1 - (1.5 &times; IQR)<br>
            Upper Bound = Q3 + (1.5 &times; IQR)<br>
            <em>Anomaly Condition: value &lt; Lower Bound OR value &gt; Upper Bound</em>
        </div>

        <h3>B. Pearson Product-Moment Correlation Matrix</h3>
        <p>Linear dependencies across all numeric feature combinations are determined via normalized covariance:</p>
        <div class="formula-box">
            <strong>r<sub>xy</sub> = &sum;[(x<sub>i</sub> - x̄)(y<sub>i</sub> - ȳ)] / [ &radic;&sum;(x<sub>i</sub> - x̄)<sup>2</sup> &times; &radic;&sum;(y<sub>i</sub> - ȳ)<sup>2</sup> ]</strong>
        </div>

        <h3>C. Lexical & AST Security Analysis</h3>
        <p>Before any synthesized code snippet is passed to the execution namespace, it is evaluated against a disallowed module regex:</p>
        <div class="code-block">
DISALLOWED = ["os", "subprocess", "shutil", "sys", "socket", "urllib", "requests", "http", "pathlib", "__import__"]
# Any matching token terminates execution before bytecode evaluation
        </div>

        <h2>5. Dual-Engine Resiliency: Gemini vs Offline Fallback</h2>
        <table>
            <thead>
                <tr>
                    <th>Capability</th>
                    <th>Gemini Online Mode (Connected)</th>
                    <th>Offline Statistical Fallback Mode</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Activation</strong></td>
                    <td>GEMINI_API_KEY present in .env or UI sidebar</td>
                    <td>Automatic fallback when no API key is provided</td>
                </tr>
                <tr>
                    <td><strong>Reasoning Depth</strong></td>
                    <td>Deep qualitative context, complex domain analogies</td>
                    <td>Deterministic, template-driven statistical facts</td>
                </tr>
                <tr>
                    <td><strong>Code Generation</strong></td>
                    <td>Arbitrary ad-hoc pandas, numpy, and duckdb scripts</td>
                    <td>Targeted intent parsing for 8 core chart/stat archetypes</td>
                </tr>
                <tr>
                    <td><strong>Data Privacy</strong></td>
                    <td>Metadata & 3-row preview sent to Gemini API</td>
                    <td><strong>100% Local</strong> — Zero network transmission</td>
                </tr>
                <tr>
                    <td><strong>Visual Output</strong></td>
                    <td>Dynamic Plotly charts tailored to any natural prompt</td>
                    <td>Interactive Plotly histograms, bars, lines, and heatmaps</td>
                </tr>
            </tbody>
        </table>

        <h2>6. Security, API Key Management & Governance</h2>
        <div class="callout">
            <div class="callout-title">Enterprise Security Safeguards</div>
            <ul>
                <li><strong>Stateless API Key Handling:</strong> API keys entered in the sidebar reside strictly in ephemeral Streamlit session state and are never logged or stored to disk.</li>
                <li><strong>Memory Copy Isolation:</strong> The Code Interpreter executes transformations strictly on <code>df.copy()</code>, preventing accidental modification or corruption of the source dataset.</li>
                <li><strong>Restricted Builtins:</strong> Host-level file writing (<code>open(..., 'w')</code>) and system process spawns are strictly blocked by the AST interpreter guard.</li>
            </ul>
        </div>

        <h2>7. Downloadable Deliverables</h2>
        <p>The following pre-compiled documentation packages are available in your project folder:</p>
        <ul>
            <li><strong>Microsoft Word Document:</strong> <code>Data_Insight_AI_Agent_Documentation.docx</code></li>
            <li><strong>Standalone HTML Whitepaper:</strong> <code>Data_Insight_AI_Agent_Whitepaper.html</code></li>
            <li><strong>Single All-in-One Python Code:</strong> <code>standalone_app.py</code></li>
            <li><strong>Portable Zip Package:</strong> <code>data_insight_agent.zip</code></li>
        </ul>
    </div>
</body>
</html>
"""
    html_path = os.path.join(DOCS_DIR, "Data_Insight_AI_Agent_Whitepaper.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Successfully generated HTML Whitepaper: {html_path}")
    return html_path


if __name__ == "__main__":
    create_docx()
    create_html_whitepaper()
