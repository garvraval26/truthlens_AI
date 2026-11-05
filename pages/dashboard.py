"""
pages/dashboard.py
==============================================================
Dashboard page — high-level overview of system usage.

Displays:
    - Total Analyzed Articles
    - Real / Fake counts
    - Average Confidence
    - Pie chart (Real vs Fake)
    - Bar graph (Bias distribution)
    - Line chart (Monthly usage trend)
    - Recent Activity feed
==============================================================
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

import database
from config import CHART_COLOR_SEQUENCE
from utils import format_percentage, format_datetime, truncate_text


def render():
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <h1 style="margin-bottom:0.2rem;">📊 Dashboard</h1>
            <p style="color: var(--text-secondary); font-size: 1rem;">
                A real-time overview of all fake news detection and bias analysis activity.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stats = database.get_summary_stats()

    # ----------------------------------------------------------
    # METRIC CARDS
    # ----------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)

    metric_data = [
        (col1, "Total Analyzed", stats["total_analyzed"], "📰"),
        (col2, "Real News", stats["real_count"], "✅"),
        (col3, "Fake News", stats["fake_count"], "🚫"),
        (col4, "Avg. Confidence", format_percentage(stats["avg_confidence"]), "🎯"),
    ]

    for col, label, value, icon in metric_data:
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{icon} {label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    if stats["total_analyzed"] == 0:
        st.info(
            "No data yet. Head over to **News Detector** or **URL Analyzer** to "
            "run your first analysis — your dashboard will populate automatically."
        )
        return

    # ----------------------------------------------------------
    # CHARTS ROW 1: Pie + Bar
    # ----------------------------------------------------------
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### Prediction Distribution")
        pie_df = database.get_all_predictions()
        pie_counts = pie_df["prediction"].value_counts().reset_index()
        pie_counts.columns = ["prediction", "count"]

        fig_pie = px.pie(
            pie_counts,
            names="prediction",
            values="count",
            color="prediction",
            color_discrete_map={"Real": "#00B894", "Fake": "#FF6B6B"},
            hole=0.55,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(
            showlegend=True,
            margin=dict(t=10, b=10, l=10, r=10),
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        st.markdown("#### Bias Distribution")
        bias_df = database.get_bias_distribution()

        if bias_df.empty:
            st.info("No bias data available yet.")
        else:
            fig_bar = px.bar(
                bias_df,
                x="bias",
                y="count",
                color="bias",
                color_discrete_sequence=CHART_COLOR_SEQUENCE,
                text="count",
            )
            fig_bar.update_traces(textposition="outside")
            fig_bar.update_layout(
                showlegend=False,
                margin=dict(t=10, b=10, l=10, r=10),
                height=320,
                xaxis_title="",
                yaxis_title="Articles",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # ----------------------------------------------------------
    # CHART ROW 2: Line chart (monthly trend)
    # ----------------------------------------------------------
    st.markdown("#### Usage Trend Over Time")
    monthly_df = database.get_monthly_usage()

    if monthly_df.empty or len(monthly_df) < 2:
        st.info("Not enough historical data yet to show a usage trend. Keep analyzing articles!")
    else:
        fig_line = go.Figure()
        fig_line.add_trace(
            go.Scatter(
                x=monthly_df["month"],
                y=monthly_df["count"],
                mode="lines+markers",
                line=dict(color="#6C5CE7", width=3, shape="spline"),
                marker=dict(size=8, color="#00D2D3"),
                fill="tozeroy",
                fillcolor="rgba(108, 92, 231, 0.12)",
            )
        )
        fig_line.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=300,
            xaxis_title="Month",
            yaxis_title="Articles Analyzed",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # ----------------------------------------------------------
    # RECENT ACTIVITY
    # ----------------------------------------------------------
    st.markdown("#### 🕒 Recent Activity")
    recent_df = database.get_recent_activity(limit=6)

    if recent_df.empty:
        st.info("No recent activity yet.")
    else:
        for _, row in recent_df.iterrows():
            badge_class = "badge-real" if row["prediction"] == "Real" else "badge-fake"
            st.markdown(
                f"""
                <div class="glass-card" style="padding: 1rem 1.4rem; margin-bottom: 0.7rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap: wrap; gap: 0.5rem;">
                        <div>
                            <strong>{truncate_text(row['headline'], 80)}</strong><br>
                            <span style="color: var(--text-secondary); font-size: 0.85rem;">
                                {format_datetime(row['timestamp'])} · Bias: {row['bias']}
                            </span>
                        </div>
                        <div style="text-align:right;">
                            <span class="badge {badge_class}">{row['prediction']}</span><br>
                            <span style="font-size:0.8rem; color: var(--text-secondary);">
                                {format_percentage(row['confidence'])} confidence
                            </span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
