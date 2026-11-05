"""
app.py
==============================================================
TruthLens AI — Main Application Entry Point

AI Powered Fake News Detection and Media Bias Analysis System

Run with:
    streamlit run app.py
==============================================================
"""

import streamlit as st

from config import (
    APP_NAME,
    APP_TAGLINE,
    APP_ICON,
    APP_VERSION,
    NAV_ITEMS,
    THEME_COLORS,
    DEFAULT_SESSION_STATE,
    ASSETS_DIR,
)
import database  # noqa: F401 (ensures DB tables are initialized on startup)

from pages import dashboard, detector, url_analysis, bias, history, analytics, about, settings


# ==============================================================
# PAGE CONFIG (must be first Streamlit call)
# ==============================================================
st.set_page_config(
    page_title=f"{APP_NAME} — {APP_TAGLINE}",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==============================================================
# SESSION STATE INITIALIZATION
# ==============================================================
for key, value in DEFAULT_SESSION_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==============================================================
# THEME INJECTION (CSS variables + stylesheet)
# ==============================================================
def inject_theme():
    theme_name = st.session_state.get("theme", "light")
    palette = THEME_COLORS[theme_name]

    root_vars = "\n".join([f"    --{k.replace('_', '-')}: {v};" for k, v in palette.items()])

    try:
        with open(ASSETS_DIR / "styles.css", "r", encoding="utf-8") as f:
            base_css = f.read()
    except FileNotFoundError:
        base_css = ""

    st.markdown(
        f"""
        <style>
        :root {{
{root_vars}
        }}
        {base_css}
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_theme()


# ==============================================================
# LANDING PAGE
# ==============================================================
def render_landing_page():
    stats = database.get_summary_stats()

    st.markdown(
        f"""
        <div class="hero-container">
            <div class="hero-title">🛡️ {APP_NAME}</div>
            <div class="hero-subtitle">{APP_TAGLINE}. Detect misinformation, uncover media bias,
            and understand the news you read — powered by state-of-the-art transformer AI.</div>
            <div class="hero-stats">
                <div><div class="hero-stat-number">{stats['total_analyzed']}</div><div class="hero-stat-label">Articles Analyzed</div></div>
                <div><div class="hero-stat-number">{stats['real_count']}</div><div class="hero-stat-label">Verified Real</div></div>
                <div><div class="hero-stat-number">{stats['fake_count']}</div><div class="hero-stat-label">Flagged Fake</div></div>
                <div><div class="hero-stat-number">98%+</div><div class="hero-stat-label">Model Accuracy*</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        if st.button("🚀 Start Detection", use_container_width=True, type="primary"):
            st.session_state["current_page"] = "detector"
            st.session_state["app_started"] = True
            st.rerun()

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<h2 style='text-align:center;'>Everything you need to fight misinformation</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color: var(--text-secondary); max-width:650px; margin: 0 auto 2rem auto;'>"
        "A complete AI-powered toolkit for detecting fake news, analyzing bias, and "
        "understanding the credibility of any article — in seconds.</p>",
        unsafe_allow_html=True,
    )

    features = [
        ("🔍", "AI Fake News Detection", "Fine-tuned RoBERTa/BERT models classify articles as Real or Fake with confidence scoring."),
        ("🔗", "Instant URL Analysis", "Paste any news link and we'll automatically fetch, parse, and analyze the full article."),
        ("⚖️", "Media Bias Detection", "Understand political framing with Left/Center/Right classification and a visual bias meter."),
        ("🧠", "Explainable AI", "See exactly which words and phrases influenced each prediction — no black boxes."),
        ("📊", "Rich Analytics", "Track trends, confidence distributions, and source patterns across all your analyses."),
        ("🕒", "Full History", "Every analysis is saved, searchable, exportable, and always available for review."),
    ]

    for row_start in range(0, len(features), 3):
        cols = st.columns(3)
        for i, (icon, title, desc) in enumerate(features[row_start:row_start + 3]):
            with cols[i]:
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
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="app-footer">
            <p>*Accuracy figures reflect benchmark performance on standard fake-news datasets, not a guarantee for every input.</p>
            <p>{APP_NAME} v{APP_VERSION} · Built with Streamlit, PyTorch & HuggingFace Transformers</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================
# SIDEBAR NAVIGATION
# ==============================================================
def render_sidebar():
    with st.sidebar:
        st.markdown(
            f"""<div class="sidebar-brand">🛡️ {APP_NAME}</div>""",
            unsafe_allow_html=True,
        )

        if st.button("🏠 Home / Landing Page", use_container_width=True):
            st.session_state["current_page"] = "landing"
            st.rerun()

        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            "<p style='color: var(--text-secondary); font-size:0.75rem; "
            "text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.5rem;'>Navigation</p>",
            unsafe_allow_html=True,
        )

        for item in NAV_ITEMS:
            if st.button(
                f"{item['icon']}  {item['label']}",
                key=f"nav_{item['key']}",
                use_container_width=True,
            ):
                st.session_state["current_page"] = item["key"]
                st.session_state["app_started"] = True
                st.rerun()

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="text-align:center; color: var(--text-secondary); font-size:0.75rem;">
                {APP_NAME} v{APP_VERSION}<br>Running on localhost
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==============================================================
# PAGE ROUTER
# ==============================================================
def render_page(page_name):

    if page_name == "dashboard":
        from pages import dashboard
        dashboard.render()

    elif page_name == "detector":
        from pages import detector
        detector.render()

    elif page_name == "url_analysis":
        from pages import url_analysis
        url_analysis.render()

    elif page_name == "bias":
        from pages import bias
        bias.render()

    elif page_name == "history":
        from pages import history
        history.render()

    elif page_name == "analytics":
        from pages import analytics
        analytics.render()

    elif page_name == "about":
        from pages import about
        about.render()

    elif page_name == "settings":
        from pages import settings
        settings.render()

    else:
        st.warning("Page not found.")


def main():
    render_sidebar()

    current_page = st.session_state.get("current_page", "landing")

    if current_page == "landing" or not st.session_state.get("app_started", False):
        render_landing_page()
    try:
        render_page(current_page)
    except Exception as e:
        st.error(f"⚠️ Something went wrong while loading this page: {e}")
        st.info("Try navigating to a different page or refreshing the app.")
        
    else:
            st.warning("Page not found. Redirecting to Dashboard.")
            dashboard.render()


if __name__ == "__main__":
    main()
