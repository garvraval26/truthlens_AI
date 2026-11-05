"""
pages/settings.py
==============================================================
Settings page — theme switching (Dark/Light), history
management, model configuration display, and theme color
reference.
==============================================================
"""

import streamlit as st
import database
from config import (
    THEME_COLORS,
    PRIMARY_MODEL_NAME,
    FALLBACK_MODEL_NAME,
    BIAS_MODEL_NAME,
    MAX_SEQUENCE_LENGTH,
    HIGH_CONFIDENCE_THRESHOLD,
    MEDIUM_CONFIDENCE_THRESHOLD,
    MAX_UPLOAD_SIZE_MB,
    ALLOWED_UPLOAD_EXTENSIONS,
)


def render():
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <h1 style="margin-bottom:0.2rem;">⚙️ Settings</h1>
            <p style="color: var(--text-secondary); font-size: 1rem;">
                Customize your experience and manage application data.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ----------------------------------------------------------
    # APPEARANCE
    # ----------------------------------------------------------
    st.markdown("#### 🎨 Appearance")

    current_theme = st.session_state.get("theme", "light")

    theme_col1, theme_col2 = st.columns(2)
    with theme_col1:
        if st.button(
            "☀️ Light Mode" + (" ✓" if current_theme == "light" else ""),
            use_container_width=True,
        ):
            st.session_state["theme"] = "light"
            st.rerun()
    with theme_col2:
        if st.button(
            "🌙 Dark Mode" + (" ✓" if current_theme == "dark" else ""),
            use_container_width=True,
        ):
            st.session_state["theme"] = "dark"
            st.rerun()

    st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)
    st.markdown("##### Theme Color Palette")

    palette = THEME_COLORS[current_theme]
    swatch_cols = st.columns(len(palette))
    displayable = {
        k: v for k, v in palette.items()
        if v.startswith("#") or v.startswith("rgb")
    }
    swatch_cols = st.columns(min(len(displayable), 6))
    for i, (name, color) in enumerate(list(displayable.items())[:6]):
        with swatch_cols[i]:
            st.markdown(
                f"""
                <div style="text-align:center;">
                    <div style="width:100%; height:50px; border-radius:10px; background:{color if color.startswith('#') else '#6C5CE7'}; border:1px solid var(--border-color);"></div>
                    <p style="font-size:0.7rem; color: var(--text-secondary); margin-top:0.3rem;">{name.replace('_', ' ').title()}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ----------------------------------------------------------
    # MODEL SETTINGS (read-only display)
    # ----------------------------------------------------------
    st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🧠 Model Settings")

    st.markdown(
        f"""
        <div class="glass-card">
            <table style="width:100%; color: var(--text-primary); border-collapse: collapse;">
                <tr>
                    <td style="padding:6px 0; color: var(--text-secondary);">Primary Fake-News Model</td>
                    <td style="padding:6px 0; text-align:right;"><code>{PRIMARY_MODEL_NAME}</code></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; color: var(--text-secondary);">Fallback Model</td>
                    <td style="padding:6px 0; text-align:right;"><code>{FALLBACK_MODEL_NAME}</code></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; color: var(--text-secondary);">Bias Detection Model</td>
                    <td style="padding:6px 0; text-align:right;"><code>{BIAS_MODEL_NAME}</code></td>
                </tr>
                <tr>
                    <td style="padding:6px 0; color: var(--text-secondary);">Max Sequence Length</td>
                    <td style="padding:6px 0; text-align:right;">{MAX_SEQUENCE_LENGTH} tokens</td>
                </tr>
                <tr>
                    <td style="padding:6px 0; color: var(--text-secondary);">High Confidence Threshold</td>
                    <td style="padding:6px 0; text-align:right;">{HIGH_CONFIDENCE_THRESHOLD * 100:.0f}%</td>
                </tr>
                <tr>
                    <td style="padding:6px 0; color: var(--text-secondary);">Medium Confidence Threshold</td>
                    <td style="padding:6px 0; text-align:right;">{MEDIUM_CONFIDENCE_THRESHOLD * 100:.0f}%</td>
                </tr>
                <tr>
                    <td style="padding:6px 0; color: var(--text-secondary);">Max Upload Size</td>
                    <td style="padding:6px 0; text-align:right;">{MAX_UPLOAD_SIZE_MB} MB</td>
                </tr>
                <tr>
                    <td style="padding:6px 0; color: var(--text-secondary);">Allowed File Types</td>
                    <td style="padding:6px 0; text-align:right;">{', '.join(ALLOWED_UPLOAD_EXTENSIONS)}</td>
                </tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Model settings are configured in `config.py`. Restart the app after "
        "changing model names for the new configuration to take effect."
    )

    # ----------------------------------------------------------
    # DATA MANAGEMENT
    # ----------------------------------------------------------
    st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🗄️ Data Management")

    stats = database.get_summary_stats()
    st.markdown(
        f"""
        <div class="glass-card">
            <p style="margin:0; color: var(--text-secondary);">
                Currently storing <strong>{stats['total_analyzed']}</strong> prediction record(s) in the local SQLite database.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)

    confirm = st.checkbox("I understand this will permanently delete all history.")
    if st.button("🗑️ Clear All History", disabled=not confirm, type="primary"):
        try:
            count = database.clear_all_history()
            st.success(f"Successfully deleted {count} record(s).")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to clear history: {e}")

    # ----------------------------------------------------------
    # ABOUT / VERSION
    # ----------------------------------------------------------
    st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align:center; color: var(--text-secondary); font-size:0.85rem;">
            Changes to appearance apply instantly. Data management actions are permanent.
        </div>
        """,
        unsafe_allow_html=True,
    )
