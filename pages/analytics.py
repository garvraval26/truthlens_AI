"""
pages/analytics.py
==============================================================
Analytics page — deeper interactive charts for exploring
historical prediction data.

Charts:
    - Prediction distribution (donut)
    - Confidence distribution (histogram)
    - Monthly usage trend (area/line)
    - Most common sources (horizontal bar)
==============================================================
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

import database
from config import CHART_COLOR_SEQUENCE


def render():
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <h1 style="margin-bottom:0.2rem;">📈 Analytics</h1>
            <p style="color: var(--text-secondary); font-size: 1rem;">
                Explore deeper insights and trends across all your analyzed articles.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = database.get_all_predictions()

    if df.empty:
        st.info(
            "No analytics available yet. Analyze some articles in **News Detector** "
            "or **URL Analyzer** to start building your analytics dashboard."
        )
        return

    # ----------------------------------------------------------
    # ROW 1: Prediction Distribution + Confidence Histogram
    # ----------------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Prediction Distribution")
        pred_counts = df["prediction"].value_counts().reset_index()
        pred_counts.columns = ["prediction", "count"]

        fig = px.pie(
            pred_counts,
            names="prediction",
            values="count",
            hole=0.5,
            color="prediction",
            color_discrete_map={"Real": "#00B894", "Fake": "#FF6B6B"},
        )
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(
            height=340,
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Confidence Score Distribution")
        fig = px.histogram(
            df,
            x="confidence",
            nbins=20,
            color_discrete_sequence=["#6C5CE7"],
        )
        fig.update_layout(
            height=340,
            margin=dict(t=10, b=10, l=10, r=10),
            xaxis_title="Confidence Score",
            yaxis_title="Number of Articles",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            bargap=0.05,
        )
        st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------------
    # ROW 2: Monthly Usage Trend
    # ----------------------------------------------------------
    st.markdown("#### Monthly Usage Trend")
    monthly_df = database.get_monthly_usage()

    if len(monthly_df) < 2:
        st.info("Not enough data across multiple months to show a usage trend yet.")
    else:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=monthly_df["month"],
                y=monthly_df["count"],
                mode="lines+markers",
                fill="tozeroy",
                line=dict(color="#00D2D3", width=3, shape="spline"),
                fillcolor="rgba(0, 210, 211, 0.15)",
                marker=dict(size=8),
            )
        )
        fig.update_layout(
            height=320,
            margin=dict(t=10, b=10, l=10, r=10),
            xaxis_title="Month",
            yaxis_title="Articles Analyzed",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------------
    # ROW 3: Most Common Sources + Bias Breakdown
    # ----------------------------------------------------------
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### Most Common Sources")
        top_sources = database.get_top_sources(limit=8)
        if top_sources.empty:
            st.info("No source data available yet.")
        else:
            fig = px.bar(
                top_sources.sort_values("count"),
                x="count",
                y="source",
                orientation="h",
                color_discrete_sequence=["#6C5CE7"],
                text="count",
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(
                height=340,
                margin=dict(t=10, b=10, l=10, r=10),
                xaxis_title="Articles Analyzed",
                yaxis_title="",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown("#### Bias Category Breakdown")
        bias_df = database.get_bias_distribution()
        if bias_df.empty:
            st.info("No bias data available yet.")
        else:
            fig = px.bar(
                bias_df,
                x="bias",
                y="count",
                color="bias",
                color_discrete_sequence=CHART_COLOR_SEQUENCE,
                text="count",
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(
                height=340,
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
                xaxis_title="",
                yaxis_title="Articles",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------------
    # SUMMARY TABLE
    # ----------------------------------------------------------
    st.markdown("#### Summary Statistics")
    summary_stats = {
        "Metric": [
            "Total Articles Analyzed",
            "Average Confidence",
            "Highest Confidence",
            "Lowest Confidence",
            "Most Common Bias",
        ],
        "Value": [
            len(df),
            f"{df['confidence'].mean() * 100:.1f}%",
            f"{df['confidence'].max() * 100:.1f}%",
            f"{df['confidence'].min() * 100:.1f}%",
            df["bias"].mode()[0] if not df["bias"].mode().empty else "N/A",
        ],
    }
    st.dataframe(summary_stats, use_container_width=True, hide_index=True)
