"""
pages/bias.py
==============================================================
Bias Detection page — a dedicated, standalone page for
analyzing the political bias (Left / Center / Right) of a
piece of text, independent of the fake/real classification.

Displays:
    - Bias Meter (horizontal spectrum gauge)
    - Bias Gauge (Plotly indicator)
    - Confidence score
    - Explanation of scoring
==============================================================
"""

import time
import streamlit as st
import plotly.graph_objects as go

from model import predict_bias
from utils import validate_text_input, format_percentage, InvalidInputError


BIAS_POSITION_MAP = {
    "left-leaning": 15,
    "center / neutral": 50,
    "right-leaning": 85,
}

BIAS_COLOR_MAP = {
    "left-leaning": "#4A90D9",
    "center / neutral": "#6C5CE7",
    "right-leaning": "#E74C3C",
}


def _render_bias_spectrum(bias_label: str, confidence: float):
    """Renders a horizontal Left-Center-Right spectrum with a marker."""
    position = BIAS_POSITION_MAP.get(bias_label, 50)
    color = BIAS_COLOR_MAP.get(bias_label, "#6C5CE7")

    fig = go.Figure()

    # Background spectrum bar (gradient-like via multiple segments)
    fig.add_shape(
        type="rect", x0=0, x1=33, y0=0, y1=1,
        fillcolor="rgba(74, 144, 217, 0.25)", line_width=0,
    )
    fig.add_shape(
        type="rect", x0=33, x1=66, y0=0, y1=1,
        fillcolor="rgba(108, 92, 231, 0.2)", line_width=0,
    )
    fig.add_shape(
        type="rect", x0=66, x1=100, y0=0, y1=1,
        fillcolor="rgba(231, 76, 60, 0.25)", line_width=0,
    )

    # Marker for current position
    fig.add_trace(
        go.Scatter(
            x=[position],
            y=[0.5],
            mode="markers",
            marker=dict(size=28, color=color, line=dict(width=3, color="white")),
            showlegend=False,
        )
    )

    fig.update_xaxes(
        range=[0, 100], showgrid=False, zeroline=False,
        tickvals=[15, 50, 85],
        ticktext=["⬅️ Left", "⚖️ Center", "Right ➡️"],
    )
    fig.update_yaxes(visible=False, range=[0, 1])
    fig.update_layout(
        height=140,
        margin=dict(t=10, b=30, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _render_score_bars(scores: dict):
    labels = list(scores.keys())
    values = list(scores.values())
    colors = [BIAS_COLOR_MAP.get(label, "#6C5CE7") for label in labels]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=[l.title() for l in labels],
            orientation="h",
            marker_color=colors,
            text=[format_percentage(v) for v in values],
            textposition="outside",
        )
    )
    fig.update_layout(
        height=220,
        margin=dict(t=10, b=10, l=10, r=40),
        xaxis=dict(range=[0, 1], title="Confidence Score"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render():
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <h1 style="margin-bottom:0.2rem;">⚖️ Media Bias Detection</h1>
            <p style="color: var(--text-secondary); font-size: 1rem;">
                Paste any article or statement to analyze its political leaning.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    text_input = st.text_area(
        "Paste article text or a statement",
        height=220,
        placeholder="Paste the text you'd like to analyze for political bias...",
    )

    analyze_clicked = st.button("⚖️ Analyze Bias", type="primary", use_container_width=True)

    if analyze_clicked:
        try:
            validate_text_input(text_input, min_length=15)

            progress_placeholder = st.empty()
            progress_bar = st.progress(0)
            for pct, msg in [
                (30, "Loading bias classification model..."),
                (65, "Evaluating language patterns..."),
                (100, "Finalizing bias assessment..."),
            ]:
                progress_placeholder.markdown(
                    f"<p class='scanning-text'>⏳ {msg}</p>", unsafe_allow_html=True
                )
                progress_bar.progress(pct)
                time.sleep(0.3)

            result = predict_bias(text_input)
            progress_placeholder.empty()
            progress_bar.empty()

            if result.get("confidence", 0) == 0.0 and "note" in result:
                st.warning(result["note"])

            st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
            st.markdown("#### Bias Meter")
            st.plotly_chart(_render_bias_spectrum(result["bias"], result["confidence"]), use_container_width=True)

            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(
                    f"""
                    <div class="glass-card" style="text-align:center;">
                        <p style="color: var(--text-secondary); margin-bottom:0.3rem;">Detected Leaning</p>
                        <h2 style="margin:0;">{result['bias'].title()}</h2>
                        <p style="margin-top:0.4rem;">
                            <span class="badge badge-neutral">{format_percentage(result['confidence'])} confidence</span>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown("##### Score Breakdown")
                st.plotly_chart(_render_score_bars(result["scores"]), use_container_width=True)

            st.markdown(
                """
                <div class="glass-card" style="margin-top:0.8rem;">
                    <strong>How to interpret this:</strong>
                    <p style="color: var(--text-secondary); margin-top:0.4rem; margin-bottom:0;">
                        This score reflects language patterns, framing, and word choice commonly
                        associated with each political leaning. It is a probabilistic estimate,
                        not a definitive judgment of the source's editorial stance.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        except InvalidInputError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"An unexpected error occurred during bias analysis: {e}")
