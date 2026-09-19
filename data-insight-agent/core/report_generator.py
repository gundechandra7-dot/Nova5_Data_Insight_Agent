"""
Report Export Utility.
Generates comprehensive, styled HTML and Markdown executive reports.
"""

from typing import Dict, Any, List, Optional
import datetime
import plotly.graph_objects as go
import plotly.io as pio


class ReportGenerator:
    """Compiles dataset analysis, profile metrics, AI insights, and visual charts into standalone reports."""

    @classmethod
    def generate_html_report(
        cls,
        metadata: Dict[str, Any],
        profile: Dict[str, Any],
        insights_markdown: str,
        charts: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        timestamp = datetime.datetime.now().strftime("%B %d, %Y - %H:%M:%S")
        file_name = metadata.get("file_name", "Dataset")
        rows = profile.get("total_rows", 0)
        cols = profile.get("total_columns", 0)
        completeness = profile.get("completeness_pct", 100)
        duplicates = profile.get("duplicate_rows", 0)

        # Convert insights markdown roughly to HTML if simple
        insights_html = insights_markdown.replace("\n", "<br>")
        insights_html = insights_html.replace("### ", "<h3>").replace("## ", "<h2>").replace("# ", "<h1>")
        insights_html = insights_html.replace("**", "<strong>")

        # Render charts as HTML divs
        charts_html = ""
        if charts:
            for item in charts:
                fig = item.get("fig")
                if isinstance(fig, (go.Figure, dict)):
                    div_str = pio.to_html(fig, full_html=False, include_plotlyjs="cdn")
                    charts_html += f"""
                    <div class="chart-card">
                        <h3>{item.get('title', 'Chart')}</h3>
                        <p class="chart-desc">{item.get('description', '')}</p>
                        <div class="chart-container">{div_str}</div>
                    </div>
                    """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Data Intelligence Report - {file_name}</title>
    <style>
        :root {{
            --primary: #1e3a8a;
            --primary-light: #3b82f6;
            --bg-gray: #f8fafc;
            --card-border: #e2e8f0;
            --text-dark: #0f172a;
            --text-muted: #64748b;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-gray);
            color: var(--text-dark);
            margin: 0;
            padding: 30px 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        }}
        .header {{
            border-bottom: 2px solid var(--card-border);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 8px 0;
            color: var(--primary);
            font-size: 28px;
        }}
        .header .meta {{
            color: var(--text-muted);
            font-size: 14px;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}
        .metric-card {{
            background: #f1f5f9;
            border-radius: 8px;
            padding: 16px 20px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: 700;
            color: var(--primary-light);
        }}
        .metric-label {{
            font-size: 13px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .section-title {{
            font-size: 20px;
            color: var(--primary);
            margin: 30px 0 16px 0;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 8px;
        }}
        .insights-content {{
            background: #eff6ff;
            border-left: 4px solid var(--primary-light);
            padding: 20px;
            border-radius: 4px 8px 8px 4px;
            margin-bottom: 30px;
            font-size: 15px;
        }}
        .chart-card {{
            background: #ffffff;
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 24px;
        }}
        .chart-card h3 {{
            margin-top: 0;
            color: var(--text-dark);
        }}
        .chart-desc {{
            color: var(--text-muted);
            font-size: 13px;
            margin-bottom: 16px;
        }}
        @media print {{
            body {{ background: #fff; padding: 0; }}
            .container {{ box-shadow: none; padding: 0; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 AI Data Intelligence & Analytics Report</h1>
            <div class="meta">
                <strong>Source:</strong> {file_name} &nbsp;|&nbsp; 
                <strong>Format:</strong> {metadata.get('detected_format', '').upper()} &nbsp;|&nbsp; 
                <strong>Generated on:</strong> {timestamp}
            </div>
        </div>

        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-value">{rows:,}</div>
                <div class="metric-label">Total Rows</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{cols}</div>
                <div class="metric-label">Columns</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{completeness}%</div>
                <div class="metric-label">Completeness</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{duplicates}</div>
                <div class="metric-label">Duplicate Rows</div>
            </div>
        </div>

        <div class="section-title">🧠 Executive Insights & AI Synthesis</div>
        <div class="insights-content">
            {insights_html}
        </div>

        <div class="section-title">📈 Analytical Visualizations</div>
        {charts_html or '<p>No visual charts attached.</p>'}
    </div>
</body>
</html>
"""
        return html_content

    @classmethod
    def generate_markdown_report(
        cls,
        metadata: Dict[str, Any],
        profile: Dict[str, Any],
        insights_markdown: str,
    ) -> str:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            f"# Data Intelligence Report: {metadata.get('file_name', 'Dataset')}",
            f"*Generated on {timestamp}*",
            "",
            "## 1. Overview & Health Metrics",
            f"- **Detected Format**: {metadata.get('detected_format', '').upper()}",
            f"- **Total Rows**: {profile.get('total_rows', 0):,}",
            f"- **Total Columns**: {profile.get('total_columns', 0)}",
            f"- **Completeness**: {profile.get('completeness_pct', 100)}%",
            f"- **Duplicate Rows**: {profile.get('duplicate_rows', 0)}",
            "",
            "## 2. Column Classification",
            f"- **Numeric**: {', '.join(profile.get('col_types', {}).get('numeric', [])) or 'None'}",
            f"- **Categorical**: {', '.join(profile.get('col_types', {}).get('categorical', [])) or 'None'}",
            f"- **Datetime**: {', '.join(profile.get('col_types', {}).get('datetime', [])) or 'None'}",
            "",
            "## 3. Executive AI Insights",
            insights_markdown,
        ]
        return "\n".join(lines)
