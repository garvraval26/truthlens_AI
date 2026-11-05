"""
pages/about.py
==============================================================
About page — project overview, objectives, technology stack,
dataset information, references, and developer information.
==============================================================
"""

import streamlit as st
from config import APP_NAME, APP_VERSION, DEVELOPER_NAME, DEVELOPER_YEAR


def render():
    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
            <h1 style="margin-bottom:0.2rem;">ℹ️ About {APP_NAME}</h1>
            <p style="color: var(--text-secondary); font-size: 1rem;">
                Learn more about the project, its goals, and the technology behind it.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ----------------------------------------------------------
    # PROJECT OVERVIEW
    # ----------------------------------------------------------
    st.markdown(
        f"""
        <div class="glass-card">
            <h3>📌 Project Overview</h3>
            <p style="color: var(--text-secondary);">
                <strong>{APP_NAME}</strong> is an AI-powered platform designed to help readers,
                researchers, and journalists critically evaluate news content. It combines a
                fine-tuned transformer-based language model with a media bias classifier to
                assess both the <em>factual reliability</em> and <em>political framing</em>
                of an article — all in real time, from a single dashboard.
            </p>
            <p style="color: var(--text-secondary); margin-bottom:0;">
                The system was built as a final-year major project to demonstrate the
                practical application of Natural Language Processing (NLP), transformer
                architectures, and full-stack AI product design.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ----------------------------------------------------------
    # OBJECTIVES
    # ----------------------------------------------------------
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🎯 Objectives")

    objectives = [
        ("🧠", "Accurate Classification", "Leverage transformer models (BERT/RoBERTa) to classify news as Real or Fake with high confidence."),
        ("⚖️", "Bias Transparency", "Surface the political leaning of content so readers can factor framing into their judgment."),
        ("🔍", "Explainability", "Move beyond black-box predictions by highlighting the linguistic signals behind each result."),
        ("📊", "Data-Driven Insight", "Track usage patterns and trends over time through an analytics dashboard."),
    ]

    obj_cols = st.columns(2)
    for i, (icon, title, desc) in enumerate(objectives):
        with obj_cols[i % 2]:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ----------------------------------------------------------
    # TECHNOLOGY STACK
    # ----------------------------------------------------------
    st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🛠️ Technology Stack")

    tech_col1, tech_col2, tech_col3 = st.columns(3)

    with tech_col1:
        st.markdown(
            """
            <div class="glass-card">
                <strong>Frontend</strong>
                <ul style="color: var(--text-secondary); padding-left: 1.2rem;">
                    <li>Streamlit</li>
                    <li>Custom CSS (Glassmorphism)</li>
                    <li>Plotly & Altair</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tech_col2:
        st.markdown(
            """
            <div class="glass-card">
                <strong>Backend / AI</strong>
                <ul style="color: var(--text-secondary); padding-left: 1.2rem;">
                    <li>Python 3.10+</li>
                    <li>HuggingFace Transformers</li>
                    <li>PyTorch</li>
                    <li>FastAPI</li>
                    <li>Scikit-Learn</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tech_col3:
        st.markdown(
            """
            <div class="glass-card">
                <strong>Data & Storage</strong>
                <ul style="color: var(--text-secondary); padding-left: 1.2rem;">
                    <li>SQLite</li>
                    <li>Pandas / NumPy</li>
                    <li>Newspaper3k</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ----------------------------------------------------------
    # DATASET
    # ----------------------------------------------------------
    st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="glass-card">
            <h4 style="margin-top:0;">📚 Dataset</h4>
            <p style="color: var(--text-secondary); margin-bottom:0;">
                The underlying classification model is fine-tuned on publicly available
                fake-news benchmark datasets such as <strong>LIAR</strong>, <strong>FakeNewsNet</strong>,
                and the <strong>ISOT Fake News Dataset</strong>, which contain thousands of
                labeled real and fake news articles across multiple domains.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ----------------------------------------------------------
    # REFERENCES
    # ----------------------------------------------------------
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="glass-card">
            <h4 style="margin-top:0;">📖 References</h4>
            <ul style="color: var(--text-secondary); padding-left: 1.2rem; margin-bottom:0;">
                <li>Devlin et al., "BERT: Pre-training of Deep Bidirectional Transformers", 2018</li>
                <li>Liu et al., "RoBERTa: A Robustly Optimized BERT Pretraining Approach", 2019</li>
                <li>Wang, W. Y., "LIAR: A Benchmark Dataset for Fake News Detection", 2017</li>
                <li>HuggingFace Transformers Documentation — huggingface.co/docs</li>
                <li>Streamlit Documentation — docs.streamlit.io</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ----------------------------------------------------------
    # DEVELOPER INFO
    # ----------------------------------------------------------
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="glass-card" style="text-align:center;">
            <h4 style="margin-top:0;">👨‍💻 Developer Information</h4>
            <p style="color: var(--text-secondary); margin-bottom:0.2rem;">{DEVELOPER_NAME}</p>
            <p style="color: var(--text-secondary); margin-bottom:0.2rem;">Version {APP_VERSION} · {DEVELOPER_YEAR}</p>
            <p style="color: var(--text-secondary); margin-bottom:0;">
                Built with ❤️ using Python, Streamlit, and HuggingFace Transformers.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
