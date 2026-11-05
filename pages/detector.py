"""
pages/detector.py
==============================================================
News Detector page — the core fake-news detection feature.

Users can:
    - Paste article text directly
    - Upload a .txt / .pdf / .docx file

On clicking "Analyze", the app runs the AI model, displays
prediction + confidence + bias + explainability, and saves
the result to the SQLite history table.
==============================================================
"""

import time
import streamlit as st
import plotly.graph_objects as go

import database
from model import analyze_article
from utils import (
    extract_text_from_upload,
    validate_text_input,
    format_percentage,
    get_confidence_label,
    get_bias_emoji,
    InvalidInputError,
    FileParsingError,
)


def _render_confidence_gauge(confidence: float, prediction: str):
    color = "#00B894" if prediction == "Real" else "#FF6B6B"
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=confidence * 100,
            number={"suffix": "%", "font": {"size": 36}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar": {"color": color},
                "bgcolor": "rgba(0,0,0,0.04)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 55], "color": "rgba(253, 203, 110, 0.25)"},
                    {"range": [55, 80], "color": "rgba(108, 92, 231, 0.2)"},
                    {"range": [80, 100], "color": "rgba(0, 184, 148, 0.2)"},
                ],
            },
        )
    )
    fig.update_layout(
        height=260,
        margin=dict(t=30, b=10, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#000000"},
    )
    return fig


def _render_result(result: dict, headline: str, source: str, source_url: str, analysis_type: str, original_text: str):
    prediction = result["prediction"]
    confidence = result["confidence"]
    badge_class = "badge-real" if prediction == "Real" else "badge-fake"
    icon = "✅" if prediction == "Real" else "🚫"

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="glass-card" style="text-align:center;">
            <div style="font-size: 3rem;">{icon}</div>
            <h2 style="margin: 0.3rem 0;">
                <span class="badge {badge_class}" style="font-size:1.3rem; padding: 0.5rem 1.4rem;">
                    {prediction.upper()}
                </span>
            </h2>
            <p style="color: var(--text-secondary);">{get_confidence_label(confidence)} — {format_percentage(confidence)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.plotly_chart(
            _render_confidence_gauge(confidence, prediction), use_container_width=True
        )

    with col2:
        st.markdown("##### Probability Breakdown")
        probs = result["probabilities"]
        for label, value in probs.items():
            bar_color = "#00B894" if label == "Real" else "#FF6B6B"
            st.markdown(
                f"""
                <div style="margin-bottom: 0.9rem;">
                    <div style="display:flex; justify-content:space-between; font-size:0.9rem;">
                        <span>{label}</span><span>{format_percentage(value)}</span>
                    </div>
                    <div class="confidence-bar-track">
                        <div class="confidence-bar-fill" style="width:{value*100}%; background:{bar_color};"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("##### Media Bias")
        bias_emoji = get_bias_emoji(result["bias"])
        st.markdown(
            f"""
            <div class="bias-meter-container">
                <span style="font-weight:600;">{bias_emoji} {result['bias'].title()}</span>
                <span class="badge badge-neutral">{format_percentage(result['bias_confidence'])}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # EXPLAINABLE AI SECTION
    # --------------------------------------------------------
    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🔍 Why This Prediction?")

    explanation = result["explanation"]
    st.markdown(
        f"""<div class="glass-card">{explanation['summary']}</div>""",
        unsafe_allow_html=True,
    )

    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        st.markdown("**✅ Credibility Indicators**")
        if explanation["positive_indicators"]:
            for word in explanation["positive_indicators"]:
                st.markdown(f"<span class='badge badge-real' style='margin:3px;'>{word}</span>", unsafe_allow_html=True)
        else:
            st.caption("None detected.")

    with exp_col2:
        st.markdown("**⚠️ Sensationalism Indicators**")
        if explanation["negative_indicators"]:
            for word in explanation["negative_indicators"]:
                st.markdown(f"<span class='badge badge-fake' style='margin:3px;'>{word}</span>", unsafe_allow_html=True)
        else:
            st.caption("None detected.")

    st.markdown(
        "<p style='color: var(--text-secondary); font-size:0.8rem; margin-top:0.8rem;'>"
        "Note: keyword indicators are a transparency aid. The core prediction is generated "
        "by the neural network's deep contextual understanding of the full text."
        "</p>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # SAVE TO DATABASE
    # --------------------------------------------------------
    try:
        database.insert_prediction(
            headline=headline,
            content_snippet=original_text[:300],
            prediction=prediction,
            confidence=confidence,
            bias=result["bias"],
            bias_confidence=result["bias_confidence"],
            source=source,
            source_url=source_url,
            analysis_type=analysis_type,
        )
        st.toast("Result saved to History ✅", icon="💾")
    except Exception as e:
        st.warning(f"Could not save this result to history: {e}")


def render():
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <h1 style="margin-bottom:0.2rem;">🔍 News Detector</h1>
            <p style="color: var(--text-secondary); font-size: 1rem;">
                Paste an article or upload a file to detect whether it's Real or Fake news.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    input_mode = st.radio(
        "Choose input method:",
        ["✍️ Paste Text", "📁 Upload File"],
        horizontal=True,
    )

    article_text = ""
    headline = ""

    if input_mode == "✍️ Paste Text":
        headline = st.text_input("Headline (optional)", placeholder="e.g. Local council approves new park funding")
        article_text = st.text_area(
            "Paste the full article text here",
            height=260,
            placeholder="Paste the news article content you want to analyze...",
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload a .txt, .pdf, or .docx file",
            type=["txt", "pdf", "docx"],
        )
        if uploaded_file is not None:
            try:
                with st.spinner("Extracting text from file..."):
                    article_text = extract_text_from_upload(uploaded_file)
                headline = uploaded_file.name
                st.success(f"Extracted {len(article_text)} characters from **{uploaded_file.name}**")
                with st.expander("Preview extracted text"):
                    st.write(article_text[:1000] + ("..." if len(article_text) > 1000 else ""))
            except FileParsingError as e:
                st.error(str(e))

    analyze_clicked = st.button("🚀 Analyze", type="primary", use_container_width=True)

    if analyze_clicked:
        try:
            validate_text_input(article_text)

            progress_placeholder = st.empty()
            progress_bar = st.progress(0)

            stages = [
                (20, "Preprocessing text..."),
                (45, "Running fake-news classification model..."),
                (70, "Analyzing political bias..."),
                (90, "Generating explainability report..."),
                (100, "Finalizing results..."),
            ]
            for pct, message in stages:
                progress_placeholder.markdown(
                    f"<p class='scanning-text'>⏳ {message}</p>", unsafe_allow_html=True
                )
                progress_bar.progress(pct)
                time.sleep(0.3)

            result = analyze_article(
    text=article_text,
    headline=headline,
)

            progress_placeholder.empty()
            progress_bar.empty()

            display_headline = headline.strip() if headline and headline.strip() else "Untitled Article"

            _render_result(
                result,
                headline=display_headline,
                source="Manual Input" if input_mode == "✍️ Paste Text" else "File Upload",
                source_url=None,
                analysis_type="text" if input_mode == "✍️ Paste Text" else "file",
                original_text=article_text,
            )

        except InvalidInputError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"An unexpected error occurred during analysis: {e}")
