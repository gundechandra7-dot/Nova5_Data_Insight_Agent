"""
Interactive Visualization Engine using Plotly.
Generates automated smart charts (distributions, correlations, time-series, categorical)
and supports a fully customizable interactive chart builder.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class Visualizer:
    """Plotly-based visualization generator for automatic insights and custom dashboards."""

    TEMPLATE = "plotly_dark"

    @classmethod
    def generate_smart_charts(cls, df: pd.DataFrame, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyzes the data profile and returns a curated list of high-value charts.
        Each item is a dict with: {'title': str, 'description': str, 'fig': go.Figure, 'category': str}.
        """
        charts: List[Dict[str, Any]] = []
        if df.empty:
            return charts

        numeric_cols = profile.get("col_types", {}).get("numeric", [])
        cat_cols = profile.get("col_types", {}).get("categorical", [])
        date_cols = profile.get("col_types", {}).get("datetime", [])

        # 1. Correlation Heatmap
        if len(numeric_cols) >= 2:
            num_df = df[numeric_cols].dropna()
            if len(num_df) > 3:
                corr = num_df.corr().round(2)
                fig_corr = px.imshow(
                    corr,
                    text_auto=True,
                    aspect="auto",
                    color_continuous_scale="RdBu_r",
                    zmin=-1,
                    zmax=1,
                    title="Correlation Matrix Heatmap",
                    template=cls.TEMPLATE,
                )
                fig_corr.update_layout(margin=dict(l=40, r=40, t=50, b=40))
                charts.append({
                    "title": "Correlation Matrix",
                    "description": "Examines linear relationships across all numeric variables. Dark red indicates strong positive correlation; dark blue indicates strong inverse relationship.",
                    "fig": fig_corr,
                    "category": "Correlation",
                })

        # 2. Time-Series Trends
        if date_cols and numeric_cols:
            dt_col = date_cols[0]
            val_col = numeric_cols[0]
            # Sort by date
            ts_df = df[[dt_col, val_col]].dropna().sort_values(by=dt_col)
            if len(ts_df) > 1:
                fig_ts = px.line(
                    ts_df,
                    x=dt_col,
                    y=val_col,
                    title=f"Time Series Trend: {val_col} over {dt_col}",
                    template=cls.TEMPLATE,
                )
                fig_ts.update_xaxes(rangeslider_visible=True)
                fig_ts.update_layout(margin=dict(l=40, r=40, t=50, b=40))
                charts.append({
                    "title": f"Temporal Trend: {val_col}",
                    "description": f"Tracks changes and fluctuations of {val_col} across chronological timestamps.",
                    "fig": fig_ts,
                    "category": "Time Series",
                })

        # 3. Categorical Distributions (Top categories)
        for cat_col in cat_cols[:2]:
            val_counts = df[cat_col].value_counts().head(10).reset_index()
            val_counts.columns = [cat_col, "Count"]
            if len(val_counts) > 1:
                # If few categories, donut chart, else horizontal bar chart
                if len(val_counts) <= 5:
                    fig_cat = px.pie(
                        val_counts,
                        names=cat_col,
                        values="Count",
                        hole=0.45,
                        title=f"Distribution of {cat_col}",
                        template=cls.TEMPLATE,
                    )
                else:
                    fig_cat = px.bar(
                        val_counts,
                        x="Count",
                        y=cat_col,
                        orientation="h",
                        title=f"Top 10 Frequencies in {cat_col}",
                        template=cls.TEMPLATE,
                        color="Count",
                        color_continuous_scale="Viridis",
                    )
                    fig_cat.update_layout(yaxis=dict(autorange="reversed"))

                fig_cat.update_layout(margin=dict(l=40, r=40, t=50, b=40))
                charts.append({
                    "title": f"Distribution: {cat_col}",
                    "description": f"Displays volume and category frequency breakdown for {cat_col}.",
                    "fig": fig_cat,
                    "category": "Categorical",
                })

        # 4. Numeric Distributions & Box Plots
        for num_col in numeric_cols[:2]:
            fig_hist = px.histogram(
                df,
                x=num_col,
                marginal="box",
                title=f"Distribution & Outlier Spread: {num_col}",
                template=cls.TEMPLATE,
                color_discrete_sequence=["#2b5c8f"],
            )
            fig_hist.update_layout(margin=dict(l=40, r=40, t=50, b=40))
            charts.append({
                "title": f"Distribution: {num_col}",
                "description": f"Visualizes frequency distribution, skewness, median, quartiles, and potential outliers for {num_col}.",
                "fig": fig_hist,
                "category": "Distribution",
            })

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

                fig_scatter = px.scatter(
                    df,
                    x=col1,
                    y=col2,
                    color=color_arg,
                    title=f"Bivariate Relationship: {col1} vs {col2}",
                    template=cls.TEMPLATE,
                )
                try:
                    valid = df[[col1, col2]].dropna()
                    if len(valid) > 2:
                        m, b = np.polyfit(valid[col1], valid[col2], 1)
                        x_pts = np.linspace(float(valid[col1].min()), float(valid[col1].max()), 40)
                        y_pts = m * x_pts + b
                        fig_scatter.add_trace(go.Scatter(
                            x=x_pts,
                            y=y_pts,
                            mode="lines",
                            name="Linear Fit",
                            line=dict(color="#38bdf8", width=2, dash="dash")
                        ))
                except Exception:
                    pass

                fig_scatter.update_layout(margin=dict(l=40, r=40, t=50, b=40))
                charts.append({
                    "title": f"Relationship: {col1} vs {col2}",
                    "description": f"Displays bivariate scatter relationship between {col1} and {col2}.",
                    "fig": fig_scatter,
                    "category": "Relationship",
                })

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
        """Constructs a custom Plotly figure based on user parameters."""
        chart_type = chart_type.lower()
        fig_title = title or f"{chart_type.capitalize()} of {y_col or ''} by {x_col or ''}".strip()
        kwargs: Dict[str, Any] = {
            "template": cls.TEMPLATE,
            "title": fig_title,
        }

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
