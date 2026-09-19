"""
Data Insight AI Agent - Streamlit Application.
Dark, clean, and minimalist user interface with universal multi-format data ingestion,
statistical profiling, smart dark-mode Plotly charts, and an autonomous AI code interpreter.
"""

import os
import io
import sys
from typing import Optional
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath("."))

from core.ingestion import IngestionEngine
from core.profiler import DataProfiler
from core.visualizer import Visualizer
from core.agent import DataAgent
from core.report_generator import ReportGenerator

load_dotenv()

# Page Setup
st.set_page_config(
    page_title="Nova5 — Data Insight Agent",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Nova5 UI
st.markdown("""
<style>
    .stApp {
        background: #0b0f19;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .block-container {
        max-width: 1180px;
        padding-top: 1.25rem;
        padding-bottom: 6rem;
    }
    .nova-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.25rem;
    }
    .nova-name {
        font-size: 1.8rem;
        font-weight: 750;
        letter-spacing: -0.7px;
        color: #f8fafc;
        margin: 0;
    }
    .nova-status {
        font-size: 0.78rem;
        color: #94a3b8;
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 999px;
        padding: 6px 11px;
    }
    .upload-card {
        background: #111827;
        border: 1px solid #243047;
        border-radius: 14px;
        padding: 22px 24px 18px;
        margin: 0 auto 18px;
    }
    .section-title {
        font-size: 1.02rem;
        font-weight: 650;
        color: #f8fafc;
        margin-bottom: 4px;
    }
    .section-subtitle {
        font-size: 0.82rem;
        color: #94a3b8;
        margin-bottom: 12px;
    }
    .clean-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 16px;
    }
    [data-testid="stMetric"] {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 12px 16px;
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-weight: 700 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 1px solid #1f2937;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 15px;
        font-size: 0.88rem;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom: 2px solid #38bdf8 !important;
    }
    [data-testid="stChatMessage"] {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .chat-heading {
        margin-top: 24px;
        margin-bottom: 8px;
        font-size: 1.05rem;
        font-weight: 650;
        color: #f8fafc;
    }
    .stButton>button {
        border-radius: 7px;
        font-size: 0.84rem;
        font-weight: 500;
    }
    [data-testid="stFileUploader"] {
        background: #0f172a;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Session State
if "df" not in st.session_state: st.session_state.df = None
if "metadata" not in st.session_state: st.session_state.metadata = {}
if "profile" not in st.session_state: st.session_state.profile = {}
if "smart_charts" not in st.session_state: st.session_state.smart_charts = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "executive_insights" not in st.session_state: st.session_state.executive_insights = None
if "pending_prompt" not in st.session_state: st.session_state.pending_prompt = None
if "cached_report" not in st.session_state: st.session_state.cached_report = None

samples_dir = os.path.join(os.path.abspath("."), "samples")

def set_dataset(df: pd.DataFrame, filename: str, meta: Optional[dict] = None):
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValueError("The loaded object is not a pandas DataFrame.")
    if df.empty:
        raise ValueError(f"{filename} did not contain any data rows.")
    st.session_state.df = df
    st.session_state.metadata = meta or {
        "file_name": filename,
        "detected_format": os.path.splitext(filename)[1].replace(".", "")
    }
    st.session_state.profile = DataProfiler.profile(df)
    st.session_state.smart_charts = Visualizer.generate_smart_charts(df, st.session_state.profile)
    st.session_state.executive_insights = None
    st.session_state.cached_report = None


def load_sample(filename: str):
    fpath = os.path.join(samples_dir, filename)
    if not os.path.exists(fpath):
        raise FileNotFoundError(f"Sample dataset not found: {filename}")
    with open(fpath, "rb") as f:
        df, meta = IngestionEngine.load_data(io.BytesIO(f.read()), filename)
    set_dataset(df, filename, meta)


# Configuration is environment-based so no settings/sidebar panel is exposed to users.
api_key_input = os.getenv("GEMINI_API_KEY", "")
model_choice = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
agent = DataAgent(api_key=api_key_input, model_name=model_choice)

# Header — agent name at top-left, no brain logo.
status_text = "Gemini AI Active" if api_key_input else "Offline Statistical Mode"
st.markdown(
    f'<div class="nova-header"><div class="nova-name">Nova5</div><div class="nova-status">● {status_text}</div></div>',
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# CENTER FILE UPLOAD SECTION
# -----------------------------------------------------------------------------
st.markdown('<div class="upload-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Upload your data</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">CSV, Excel, JSON, Parquet, SQLite and text datasets are supported.</div>',
    unsafe_allow_html=True,
)

uc1, uc2 = st.columns([5, 2])
with uc1:
    uploaded = st.file_uploader(
        "Upload dataset",
        type=["csv", "tsv", "xlsx", "xls", "ods", "json", "jsonl", "parquet", "feather", "db", "sqlite", "txt"],
        label_visibility="collapsed",
    )
with uc2:
    sample_map = {
        "Demo dataset...": None,
        "Sales & Profit (CSV)": "sales_data.csv",
        "Customer Churn (Excel)": "customer_churn.xlsx",
        "App Metrics (JSON)": "app_metrics.json",
        "IoT Sensors (Parquet)": "sensor_readings.parquet",
        "Company DB (SQLite)": "company_analytics.db",
    }
    selected_sample = st.selectbox("Demo dataset", list(sample_map.keys()), label_visibility="collapsed")
    if selected_sample != "Demo dataset..." and st.button("Load demo", use_container_width=True):
        try:
            load_sample(sample_map[selected_sample])
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"Loaded **{sample_map[selected_sample]}** ({len(st.session_state.df):,} rows, {len(st.session_state.df.columns)} cols). Ask me anything about the data.",
                "fig": None, "result_df": None, "code": None,
            })
            st.rerun()
        except Exception as e:
            st.error(f"Could not load sample: {e}")

if uploaded is not None and st.session_state.metadata.get("file_name") != uploaded.name:
    with st.spinner("Analyzing your dataset..."):
        try:
            df, meta = IngestionEngine.load_data(uploaded, uploaded.name)
            set_dataset(df, uploaded.name, meta)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"Uploaded **{uploaded.name}** ({len(df):,} rows × {len(df.columns)} columns). Ask me a question below.",
                "fig": None, "result_df": None, "code": None,
            })
            st.rerun()
        except Exception as e:
            st.error(f"Error loading file: {e}")

if st.session_state.df is not None:
    meta = st.session_state.metadata
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{len(st.session_state.df):,}")
    c2.metric("Columns", f"{len(st.session_state.df.columns):,}")
    c3.metric("Completeness", f"{st.session_state.profile.get('completeness_pct', 100)}%")
    c4.metric("Duplicates", f"{st.session_state.profile.get('duplicate_rows', 0):,}")
    st.caption(f"Active dataset: **{meta.get('file_name', 'Unknown')}**")

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATA SECTIONS — directly below upload
# -----------------------------------------------------------------------------
tab_data, tab_profile, tab_viz = st.tabs([
    "📂 Data Preview",
    "📊 Profiling & Health",
    "📈 Visualizations",
])

with tab_data:
    if st.session_state.df is not None:
        meta = st.session_state.metadata
        if meta.get("available_sheets") and len(meta["available_sheets"]) > 1:
            s_choice = st.selectbox(
                "Active Sheet",
                meta["available_sheets"],
                index=meta["available_sheets"].index(meta.get("selected_sheet", meta["available_sheets"][0])),
            )
            if s_choice != meta.get("selected_sheet") and uploaded is not None:
                uploaded.seek(0)
                df, m = IngestionEngine.load_data(uploaded, meta["file_name"], sheet_name=s_choice)
                set_dataset(df, meta["file_name"], m)
                st.rerun()
        st.dataframe(st.session_state.df.head(100), use_container_width=True)
        with st.expander("Schema & Data Types"):
            df = st.session_state.df
            st.dataframe(pd.DataFrame([
                {"Column": c, "Type": str(df[c].dtype), "Nulls": int(df[c].isna().sum()), "Unique": int(df[c].nunique())}
                for c in df.columns
            ]), use_container_width=True)
    else:
        st.info("Upload a dataset above or choose a demo dataset.")

with tab_profile:
    if st.session_state.df is not None:
        prof = st.session_state.profile
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Rows", f"{prof.get('total_rows', 0):,}")
        k2.metric("Features", f"{prof.get('total_columns', 0):,}")
        k3.metric("Completeness", f"{prof.get('completeness_pct', 100)}%")
        k4.metric("Duplicates", f"{prof.get('duplicate_rows', 0):,}")
        if prof.get("alerts"):
            for alert in prof["alerts"]:
                st.warning(alert)
        if prof.get("numeric_stats"):
            st.markdown("##### Numeric Statistics")
            st.dataframe(
                pd.DataFrame(prof["numeric_stats"]).T[["mean", "std", "min", "median", "max", "skew"]],
                use_container_width=True,
            )
        if prof.get("outlier_summary"):
            outlier_rows = [
                {"Feature": k, "Outliers": v["count"], "Pct": f"{v['pct']}%"}
                for k, v in prof["outlier_summary"].items() if v["count"] > 0
            ]
            if outlier_rows:
                st.markdown("##### Outliers Detected (1.5 × IQR)")
                st.dataframe(pd.DataFrame(outlier_rows), use_container_width=True)
    else:
        st.info("Load a dataset to view profiling metrics.")

with tab_viz:
    if st.session_state.df is not None:
        v_mode = st.radio("Mode", ["Curated Insights", "Custom Builder"], horizontal=True, label_visibility="collapsed")
        if v_mode == "Curated Insights":
            smart_charts = st.session_state.get("smart_charts") or Visualizer.generate_smart_charts(st.session_state.df, st.session_state.profile)
            if smart_charts:
                for chart in smart_charts:
                    st.markdown(f"**{chart['title']}** — *{chart['description']}*")
                    st.plotly_chart(chart["fig"], use_container_width=True)
            else:
                st.info("Not enough numeric or categorical columns for automated charts.")
        else:
            df = st.session_state.df
            cols = ["None"] + list(df.columns)
            c1, c2, c3 = st.columns(3)
            ctype = c1.selectbox("Chart Type", ["Bar", "Line", "Scatter", "Area", "Histogram", "Box", "Violin", "Pie", "Heatmap"])
            xcol = c2.selectbox("X-Axis", list(df.columns))
            ycol = c3.selectbox("Y-Axis", cols, index=1 if len(cols) > 2 else 0)
            c4, c5 = st.columns(2)
            color_c = c4.selectbox("Color Group (Optional)", cols)
            theme_c = c5.selectbox("Theme Palette", ["Viridis", "Plasma", "Turbo", "Blues", "Sunset"])
            try:
                fig = Visualizer.create_custom_chart(
                    df, ctype, x_col=xcol,
                    y_col=None if ycol == "None" else ycol,
                    color_col=color_c, color_theme=theme_c,
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error generating chart: {e}")
    else:
        st.info("Load a dataset to generate visualizations.")

# -----------------------------------------------------------------------------
# CHAT — after the data workspace; Streamlit keeps the input fixed at bottom
# -----------------------------------------------------------------------------
st.markdown('<div class="chat-heading">Nova5 Chat</div>', unsafe_allow_html=True)

if st.session_state.df is not None:
    num_cols = st.session_state.profile.get("col_types", {}).get("numeric", [])
    cat_cols = st.session_state.profile.get("col_types", {}).get("categorical", [])
    t_num = num_cols[0] if num_cols else "metric"
    t_cat = cat_cols[0] if cat_cols else "category"
    suggestions = [
        f"Top 5 {t_cat} by {t_num}",
        f"Distribution of {t_num}",
        "Summary statistics",
        "Check outliers and nulls",
    ]
    scols = st.columns(len(suggestions))
    for i, suggestion in enumerate(suggestions):
        if scols[i].button(suggestion, key=f"nova_sugg_{i}", use_container_width=True):
            st.session_state.pending_prompt = suggestion
            st.rerun()

    if st.button("Executive Summary", type="primary"):
        with st.spinner("Synthesizing insights..."):
            st.session_state.executive_insights = agent.generate_executive_insights(
                st.session_state.df, st.session_state.profile
            )
            st.rerun()

    if st.session_state.executive_insights:
        with st.expander("Executive AI Insights", expanded=True):
            st.markdown(st.session_state.executive_insights)

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("fig") is not None:
            st.plotly_chart(msg["fig"], use_container_width=True)
        if msg.get("result_df") is not None:
            st.dataframe(msg["result_df"], use_container_width=True)
        if msg.get("code"):
            with st.expander("View Analysis Code"):
                st.code(msg["code"], language="python")

# Persistent Streamlit chat input — rendered by Streamlit at the bottom of the page.
prompt = st.chat_input("Ask Nova5 about your data...") or st.session_state.pending_prompt
st.session_state.pending_prompt = None

if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    if st.session_state.df is None:
        pl = prompt.lower()
        try:
            if any(w in pl for w in ["sales", "retail"]):
                load_sample("sales_data.csv")
            elif any(w in pl for w in ["churn", "customer"]):
                load_sample("customer_churn.xlsx")
            elif any(w in pl for w in ["sensor", "iot"]):
                load_sample("sensor_readings.parquet")
        except Exception as e:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"I couldn't load the requested sample dataset: {e}",
                "fig": None, "result_df": None, "code": None,
            })
            st.rerun()

    with st.spinner("Nova5 is analyzing..."):
        res = agent.chat_query(
            prompt,
            st.session_state.df,
            st.session_state.profile,
            st.session_state.chat_history[:-1],
        )
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": res.get("answer", "I could not generate an answer."),
            "fig": res.get("fig"),
            "result_df": res.get("result_df"),
            "code": res.get("code"),
        })
    st.rerun()
