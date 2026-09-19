"""
AI Agent & Reasoning Engine.
Generates automated executive insights and handles conversational Natural Language to Code (Code Interpreter)
using Google GenAI (Gemini) with offline heuristic fallback.
"""

import os
import re
from typing import Dict, Any, List, Optional
import pandas as pd
from dotenv import load_dotenv

from core.code_interpreter import CodeInterpreter, duckdb

load_dotenv()


class DataAgent:
    """Intelligent reasoning agent for data understanding, Q&A, and insight generation."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                self.client = None

    def generate_executive_insights(self, df: pd.DataFrame, profile: Dict[str, Any]) -> str:
        """Generates comprehensive executive summary and strategic findings."""
        if self.client:
            try:
                prompt = f"""
You are a Principal Data Scientist and Executive Business Strategist.
Analyze the following dataset profile and provide deep, professional executive insights.

DATASET PROFILE:
{profile.get('llm_summary_prompt', '')}

DATA HEAD (SAMPLE ROWS):
{df.head(5).to_string()}

Provide your analysis in clean, beautifully formatted Markdown with these exact sections:
1. 🎯 **Executive Summary**: Core nature and scope of this dataset.
2. 💡 **Key Discoveries & Notable Patterns**: Highlight strongest trends, interesting distributions, or dominant segments.
3. ⚠️ **Data Quality & Risk Flags**: Highlight missing values, outliers, data skew, or duplicate records.
4. 🚀 **Strategic Recommendations & Next Steps**: 3-4 specific high-impact analytical questions or operational actions to take based on this data.

Be precise, quantitative (cite actual numbers and percentages), and avoid vague generic statements.
"""
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                pass

        # Offline Heuristic Engine Fallback
        return self._generate_heuristic_insights(df, profile)

    def chat_query(
        self,
        query: str,
        df: Optional[pd.DataFrame] = None,
        profile: Optional[Dict[str, Any]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Translates a natural language question into Python/Plotly code,
        executes it, and returns the narrative answer along with generated figures or tables.
        """
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            return self._handle_no_data_query(query)

        profile = profile or {}

        if self.client:
            try:
                return self._gemini_chat_pipeline(query, df, profile, chat_history)
            except Exception as e:
                # Fallback to heuristic query processor
                pass

        return self._heuristic_chat_pipeline(query, df, profile)

    def _handle_no_data_query(self, query: str) -> Dict[str, Any]:
        """Responds to user queries when no dataset has been loaded yet."""
        if self.client:
            try:
                resp = self.client.models.generate_content(
                    model=self.model_name,
                    contents=(
                        f"User prompt: {query}\n\n"
                        "Context: You are a friendly, highly capable Data Intelligence AI Agent. "
                        "Currently, no dataset has been loaded into the session yet. "
                        "Answer the user's question helpfully, and remind them that they can upload "
                        "any data file (CSV, Excel, JSON, Parquet, SQLite, Text) or select one of the "
                        "pre-built demo datasets (Retail Sales, Customer Churn, IoT Sensors, Company DB) "
                        "in the sidebar to run live data analytics, interactive charts, and executive insights."
                    ),
                )
                if resp and resp.text:
                    return {
                        "answer": resp.text.strip(),
                        "code": None,
                        "stdout": "",
                        "fig": None,
                        "result_df": None,
                        "error": None,
                    }
            except Exception:
                pass

        return {
            "answer": (
                f"Hello! I received your prompt: **\"{query}\"**.\n\n"
                "💡 **No dataset is loaded into the workspace yet.** Here is how to get started:\n\n"
                "- 📁 **Option 1: Load a Demo Dataset** — In the left sidebar under *'Load Sample Datasets'*, select **'📈 Sales & Profit (CSV)'** (or Churn, App Metrics, IoT Sensors) and click **Load Sample Dataset**.\n"
                "- 📤 **Option 2: Upload Your Own File** — Go to the **'📂 Ingestion & Preview'** tab and drag-and-drop your CSV, Excel, JSON, Parquet, or SQLite database.\n\n"
                "As soon as data is loaded, I'll automatically analyze distributions, detect outliers, create interactive charts, and run any custom code or prompts you write here!"
            ),
            "code": None,
            "stdout": "",
            "fig": None,
            "result_df": None,
            "error": None,
        }

    def _gemini_chat_pipeline(
        self,
        query: str,
        df: pd.DataFrame,
        profile: Dict[str, Any],
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Uses Gemini to generate Python/Plotly code, executes it, and synthesizes an answer."""
        cols_summary = ", ".join([f"{col} ({df[col].dtype})" for col in df.columns])
        history_context = ""
        if chat_history:
            formatted_history = "\n".join([f"{h['role'].upper()}: {h['content']}" for h in chat_history[-3:]])
            history_context = f"\nRECENT CONVERSATION CONTEXT:\n{formatted_history}\n"

        available_libs = "`pd` (pandas), `np` (numpy), `px` (plotly.express), `go` (plotly.graph_objects)"
        if duckdb is not None:
            available_libs += ", `duckdb`"

        code_prompt = f"""
You are an expert Python Data Science Code Interpreter.
Given a pandas DataFrame named `df` with columns:
{cols_summary}

DATASET PROFILE:
- Rows: {len(df)}, Columns: {len(df.columns)}
- Sample Data (first 3 rows):
{df.head(3).to_dict(orient='records')}
{history_context}
USER QUESTION: "{query}"

Write clean Python code to answer the user's question.
RULES:
1. The DataFrame is already loaded as `df`.
2. Available libraries: `pd` (pandas), `np` (numpy), `px` (plotly.express), `go` (plotly.graph_objects), `duckdb`.
3. If the user asks for a chart or visualization, create a Plotly figure and assign it to the variable `fig` (e.g. `fig = px.bar(...)` or `fig = px.line(...)`). Use template='plotly_dark'.
4. If tabular data answers the question, assign it to `result_df` (e.g. `result_df = df.groupby(...).agg(...)`).
5. Print any key summary metrics or answers directly using `print(...)`.
6. DO NOT import forbidden packages (os, sys, subprocess, etc.).
7. Return ONLY the executable python code inside a ```python ``` markdown block. No conversational preamble.
"""
        code_response = self.client.models.generate_content(
            model=self.model_name,
            contents=code_prompt,
        )
        generated_code = code_response.text.strip() if code_response and code_response.text else ""
        if not generated_code:
            return {
                "answer": "I couldn't generate analysis code for that request. Please rephrase the question or specify the column(s) you want to analyze.",
                "code": None, "stdout": "", "fig": None, "result_df": None,
                "error": "Gemini returned no executable code.",
            }

        # Execute code in the restricted interpreter.
        exec_result = CodeInterpreter.execute(generated_code, df)

        # If execution failed, attempt 1 auto-fix retry
        if not exec_result["success"]:
            retry_prompt = f"""
The previous Python code failed with error:
{exec_result['error']}

PREVIOUS CODE:
{exec_result['code']}

DATAFRAME COLUMNS:
{cols_summary}

Please fix the Python code to resolve the error. Return ONLY the corrected code in a ```python ``` block.
"""
            retry_res = self.client.models.generate_content(
                model=self.model_name,
                contents=retry_prompt,
            )
            if retry_res and retry_res.text:
                exec_result = CodeInterpreter.execute(retry_res.text, df)

        # Synthesize the final narrative answer. If synthesis fails, preserve the
        # successful execution result instead of throwing away the analysis.
        synth_prompt = f"""
You are a warm, highly articulate Data Intelligence AI Assistant.
The user asked: "{query}"

CODE EXECUTED:
{exec_result['code']}

EXECUTION CONSOLE OUTPUT:
{exec_result['stdout']}

RESULT DATA TABLE:
{exec_result['result_df'].to_string() if exec_result['result_df'] is not None else 'None'}

CHART CREATED:
{'Yes, an interactive Plotly figure was generated.' if exec_result['fig'] is not None else 'No chart generated.'}

Synthesize a clear, concise, and helpful answer for the user. Highlight key figures, trends, or insights.
Do NOT dump raw code in your text response (the UI will show the code toggle automatically).
"""
        try:
            synth_response = self.client.models.generate_content(
                model=self.model_name,
                contents=synth_prompt,
            )
            answer_text = synth_response.text.strip() if synth_response and synth_response.text else None
        except Exception:
            answer_text = None

        if not answer_text:
            if exec_result["success"]:
                answer_text = exec_result["stdout"].strip() or "Analysis completed successfully."
            else:
                answer_text = f"I couldn't complete that analysis. {exec_result['error']}"

        return {
            "answer": answer_text,
            "code": exec_result["code"],
            "stdout": exec_result["stdout"],
            "fig": exec_result["fig"],
            "result_df": exec_result["result_df"],
            "error": exec_result["error"],
        }

    def _generate_heuristic_insights(self, df: pd.DataFrame, profile: Dict[str, Any]) -> str:
        """Rule-based analytical insight generator when no LLM API key is present."""
        rows = profile.get("total_rows", 0)
        cols = profile.get("total_columns", 0)
        num_cols = profile.get("col_types", {}).get("numeric", [])
        cat_cols = profile.get("col_types", {}).get("categorical", [])
        date_cols = profile.get("col_types", {}).get("datetime", [])
        completeness = profile.get("completeness_pct", 100)
        corrs = profile.get("correlations", {})
        alerts = profile.get("alerts", [])

        summary_lines = [
            "### 🎯 Executive Summary",
            f"The ingested dataset comprises **{rows:,} records** across **{cols} features**, with an overall completeness score of **{completeness}%**.",
        ]

        if date_cols:
            summary_lines.append(f"It contains longitudinal time-series data indexed by `{', '.join(date_cols)}`.")
        if num_cols:
            summary_lines.append(f"Quantitative metrics include `{', '.join(num_cols[:4])}`{' and others' if len(num_cols) > 4 else ''}.")

        summary_lines.append("\n### 💡 Key Discoveries & Notable Patterns")
        if corrs:
            top_corrs = list(corrs.items())[:3]
            for pair, r_val in top_corrs:
                direction = "positive" if r_val > 0 else "inverse"
                strength = "strong" if abs(r_val) > 0.7 else "moderate"
                summary_lines.append(f"- **Linear Relationship**: Detected a {strength} {direction} correlation between **{pair}** ($r = {r_val}$).")
        else:
            summary_lines.append("- Independent variables exhibit dispersed, non-linear relationships across feature pairs.")

        for num_c in num_cols[:2]:
            st = profile.get("numeric_stats", {}).get(num_c, {})
            if st:
                summary_lines.append(f"- **Distribution for `{num_c}`**: Averages **{st.get('mean')}** (median: {st.get('median')}) ranging between **{st.get('min')}** and **{st.get('max')}**.")

        for cat_c in cat_cols[:2]:
            ct = profile.get("categorical_stats", {}).get(cat_c, {})
            if ct and ct.get("top_category"):
                summary_lines.append(f"- **Top Category in `{cat_c}`**: The dominant class is **'{ct['top_category']}'** accounting for {ct['top_freq']} instances.")

        summary_lines.append("\n### ⚠️ Data Quality & Risk Flags")
        if alerts:
            for alert in alerts:
                summary_lines.append(f"- {alert}")
        else:
            summary_lines.append("- ✅ No severe data hygiene defects (zero duplicate rows and excellent record completeness).")

        summary_lines.append("\n### 🚀 Strategic Recommendations & Next Steps")
        summary_lines.append("1. **Deep Dive Segmentation**: Group primary numerical targets by leading categorical dimensions to unearth subgroup variance.")
        if date_cols:
            summary_lines.append(f"2. **Seasonality & Trend Modeling**: Conduct moving average or decomposition analysis on `{date_cols[0]}` to isolate cyclical swings.")
        summary_lines.append("3. **Anomaly & Outlier Treatment**: Investigate extreme outliers flagged in high-variance continuous columns to prevent model distortion.")
        summary_lines.append("4. **Natural Language Querying**: Use the AI Assistant chat tab to drill down into specific cohorts, top percentiles, or custom slices.")

        return "\n".join(summary_lines)

    def _heuristic_chat_pipeline(self, query: str, df: pd.DataFrame, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Handles analytics and visualization queries offline using intent matching and code generation."""
        q = query.lower()
        numeric_cols = profile.get("col_types", {}).get("numeric", [])
        cat_cols = profile.get("col_types", {}).get("categorical", [])
        date_cols = profile.get("col_types", {}).get("datetime", [])

        # Smart column name matching from query
        mentioned_num = [c for c in numeric_cols if c.lower() in q]
        mentioned_cat = [c for c in cat_cols if c.lower() in q]
        mentioned_date = [c for c in date_cols if c.lower() in q]

        # Domain synonym dictionary for intuitive natural language mapping
        synonyms = {
            "sales": ["total_revenue", "revenue", "sales", "amount", "total_sales"],
            "revenue": ["total_revenue", "revenue", "sales", "amount"],
            "profit": ["total_profit", "profit", "net_profit", "margin"],
            "units": ["units_sold", "units", "quantity", "volume", "count"],
            "price": ["unit_price", "price", "monthly_charges", "charge", "fee"],
            "discount": ["discount_rate", "discount"],
            "cost": ["cost", "expense"],
            "churn": ["churn", "status"],
            "temp": ["temperature_c", "temperature", "temp"],
            "temperature": ["temperature_c", "temperature", "temp"],
            "pressure": ["pressure_psi", "pressure"],
            "users": ["active_users", "users", "customerid"],
            "user": ["active_users", "users", "customerid"],
        }
        for word, candidates in synonyms.items():
            if re.search(rf"\b{word}\b", q):
                for cand in candidates:
                    for c in numeric_cols:
                        if c.lower() == cand and c not in mentioned_num:
                            mentioned_num.append(c)
                    for c in cat_cols:
                        if c.lower() == cand and c not in mentioned_cat:
                            mentioned_cat.append(c)

        target_num = mentioned_num[0] if mentioned_num else (numeric_cols[0] if numeric_cols else None)
        target_cat = mentioned_cat[0] if mentioned_cat else (cat_cols[0] if cat_cols else None)
        target_date = mentioned_date[0] if mentioned_date else (date_cols[0] if date_cols else None)

        code = ""

        # 1. Distribution / Histogram / Outliers / Spread / Box plot
        if any(w in q for w in ["distribution", "histogram", "spread", "outlier", "outliers", "box", "density"]):
            if target_num:
                code = (
                    f"fig = px.histogram(df, x='{target_num}', marginal='box', title='Distribution & Outlier Spread of {target_num}', template='plotly_dark', color_discrete_sequence=['#1e3a8a'])\n"
                    f"q1 = float(df['{target_num}'].quantile(0.25))\n"
                    f"q3 = float(df['{target_num}'].quantile(0.75))\n"
                    f"iqr = q3 - q1\n"
                    f"outliers = df[(df['{target_num}'] < q1 - 1.5*iqr) | (df['{target_num}'] > q3 + 1.5*iqr)]\n"
                    f"result_df = df['{target_num}'].describe().to_frame().round(2)\n"
                    f"print(f'Computed distribution metrics for {target_num}. Found {{len(outliers)}} outliers using 1.5*IQR bounds.')"
                )
            else:
                code = "result_df = df.describe().round(2)\nprint('No continuous numeric features found for distribution.')"

        # 2. Scatter / Relationship / Correlation / Bivariate
        elif any(w in q for w in ["scatter", "relationship", "vs", "versus", "against", "correlation", "heatmap"]):
            if len(mentioned_num) >= 2:
                n1, n2 = mentioned_num[0], mentioned_num[1]
            elif len(numeric_cols) >= 2:
                n1, n2 = numeric_cols[0], numeric_cols[1]
            else:
                n1, n2 = None, None

            if "heatmap" in q or "correlation" in q:
                code = (
                    "num_df = df.select_dtypes(include=['number'])\n"
                    "result_df = num_df.corr().round(3)\n"
                    "fig = px.imshow(result_df, text_auto=True, color_continuous_scale='RdBu_r', title='Feature Correlation Heatmap', template='plotly_dark')\n"
                    "print('Generated correlation matrix heatmap.')"
                )
            elif n1 and n2:
                color_opt = f", color='{target_cat}'" if target_cat else ""
                code = (
                    f"fig = px.scatter(df, x='{n1}', y='{n2}'{color_opt}, title='Scatter Plot: {n1} vs {n2}', template='plotly_dark')\n"
                    f"corr = df[['{n1}', '{n2}']].dropna().corr().iloc[0, 1].round(3)\n"
                    f"print(f'Pearson correlation between {n1} and {n2}: r = {{corr}}')"
                )
            else:
                code = "result_df = df.describe().round(2)\nprint('Computed numerical statistics.')"

        # 3. Time Series / Trend / Temporal
        elif any(w in q for w in ["trend", "time", "date", "over time", "monthly", "daily", "timeline"]) and (target_date or date_cols):
            dt = target_date or date_cols[0]
            num = target_num or (numeric_cols[0] if numeric_cols else None)
            if num:
                code = (
                    f"ts = df.dropna(subset=['{dt}', '{num}']).sort_values(by='{dt}')\n"
                    f"fig = px.line(ts, x='{dt}', y='{num}', title='{num} Trend Over Time', template='plotly_dark')\n"
                    f"fig.update_xaxes(rangeslider_visible=True)\n"
                    f"print(f'Plotted chronological trend of {num} over {dt}.')"
                )
            else:
                code = f"result_df = df['{dt}'].value_counts().reset_index()\nfig = px.bar(result_df, x='{dt}', y='count', title='Records over Time', template='plotly_dark')"

        # 4. Pie / Donut Chart / Share / Proportion
        elif any(w in q for w in ["pie", "donut", "share", "proportion", "percentage"]) and (target_cat or cat_cols):
            cat = target_cat or cat_cols[0]
            num = target_num
            if num:
                code = (
                    f"result_df = df.groupby('{cat}')['{num}'].sum().reset_index()\n"
                    f"fig = px.pie(result_df, names='{cat}', values='{num}', hole=0.35, title='{num} Share by {cat}', template='plotly_dark')\n"
                    f"print(f'Generated donut chart for {num} broken down by {cat}.')"
                )
            else:
                code = (
                    f"result_df = df['{cat}'].value_counts().head(8).reset_index()\n"
                    f"result_df.columns = ['{cat}', 'Count']\n"
                    f"fig = px.pie(result_df, names='{cat}', values='Count', hole=0.35, title='Distribution of {cat}', template='plotly_dark')\n"
                    f"print(f'Generated donut chart for {cat}.')"
                )

        # 5. Missing values / Data Quality query
        elif any(w in q for w in ["missing", "null", "nan", "empty", "quality", "clean"]):
            code = (
                "missing = df.isnull().sum()\n"
                "result_df = pd.DataFrame({'Feature': missing.index, 'Missing Count': missing.values, 'Percentage (%)': (missing.values / len(df) * 100).round(2)})\n"
                "result_df = result_df[result_df['Missing Count'] > 0].sort_values(by='Missing Count', ascending=False)\n"
                "if result_df.empty:\n"
                "    print('Great news! Zero missing values found across all features.')\n"
                "else:\n"
                "    fig = px.bar(result_df, x='Feature', y='Missing Count', color='Missing Count', title='Missing Values per Feature', template='plotly_dark')\n"
                "    print(f'Found {len(result_df)} features with missing data.')"
            )

        # 6. Top / Highest / Largest / Breakdown / General Plot or Chart request
        elif any(w in q for w in ["top", "highest", "largest", "best", "most", "bar", "plot", "chart", "visualize", "graph", "breakdown"]) and (cat_cols or numeric_cols):
            cat = target_cat or (cat_cols[0] if cat_cols else None)
            num = target_num or (numeric_cols[0] if numeric_cols else None)
            if cat and num:
                code = (
                    f"result_df = df.groupby('{cat}')['{num}'].sum().reset_index().sort_values(by='{num}', ascending=False).head(10)\n"
                    f"fig = px.bar(result_df, x='{cat}', y='{num}', title='Top {cat} by Total {num}', template='plotly_dark', color='{num}', color_continuous_scale='Viridis')\n"
                    f"print(f'Computed top {cat} ranked by total {num}.')"
                )
            elif cat:
                code = (
                    f"result_df = df['{cat}'].value_counts().head(10).reset_index()\n"
                    f"result_df.columns = ['{cat}', 'Count']\n"
                    f"fig = px.bar(result_df, x='{cat}', y='Count', title='Top {cat} Counts', template='plotly_dark', color='Count', color_continuous_scale='Blues')\n"
                    f"print(f'Computed top 10 categories in {cat}.')"
                )
            elif num:
                code = (
                    f"fig = px.histogram(df, x='{num}', marginal='box', title='Distribution of {num}', template='plotly_dark')\n"
                    f"result_df = df['{num}'].describe().to_frame().round(2)\n"
                    f"print(f'Plotted distribution of {num}.')"
                )

        # 7. Summary / Describe query
        elif any(w in q for w in ["describe", "summary", "stats", "overview"]):
            code = "result_df = df.describe().round(2)\nprint('Computed descriptive statistics across all numerical features.')"

        # 8. General fallback
        else:
            if numeric_cols:
                code = f"result_df = df.head(10)\nfig = px.histogram(df, x='{numeric_cols[0]}', title='Distribution of {numeric_cols[0]}', template='plotly_dark')\nprint('Displayed first 10 records along with primary metric distribution.')"
            else:
                code = "result_df = df.head(10)\nprint(f'Displayed first 10 rows of {len(df)} total records.')"

        exec_res = CodeInterpreter.execute(code, df)
        answer = f"Here is the analysis for: **{query}**.\n\n"
        if exec_res["stdout"]:
            answer += f"{exec_res['stdout']}\n"
        if not self.api_key:
            answer += "\n*(Tip: Add your Gemini API key in the sidebar for custom deep natural language reasoning and tailored ad-hoc code generation!)*"

        return {
            "answer": answer,
            "code": exec_res["code"],
            "stdout": exec_res["stdout"],
            "fig": exec_res["fig"],
            "result_df": exec_res["result_df"],
            "error": exec_res["error"],
        }
