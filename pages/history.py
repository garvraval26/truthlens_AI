"""
pages/history.py
==============================================================
History page — browse, search, filter, delete, and export all
past predictions stored in SQLite.
==============================================================
"""

import streamlit as st
import database
from utils import format_percentage, format_datetime, truncate_text


def render():
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <h1 style="margin-bottom:0.2rem;">🕒 History</h1>
            <p style="color: var(--text-secondary); font-size: 1rem;">
                View, search, and manage every article you've analyzed.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ----------------------------------------------------------
    # SEARCH / FILTER CONTROLS
    # ----------------------------------------------------------
    search_col, filter_col, export_col = st.columns([2, 1, 1])

    with search_col:
        keyword = st.text_input("🔎 Search by headline or source", placeholder="e.g. election, bbc.com...")

    with filter_col:
        prediction_filter = st.selectbox("Filter by prediction", ["All", "Real", "Fake"])

    with export_col:
        st.markdown("<div style='height: 1.75rem;'></div>", unsafe_allow_html=True)
        export_clicked = st.button("📤 Export CSV", use_container_width=True)

    df = database.search_predictions(keyword=keyword, prediction_filter=prediction_filter)

    if export_clicked:
        if df.empty:
            st.warning("There is no data to export.")
        else:
            try:
                path = database.export_to_csv()
                with open(path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Export",
                        data=f,
                        file_name=path.split("/")[-1],
                        mime="text/csv",
                        use_container_width=True,
                    )
                st.success(f"Export ready: {path.split('/')[-1]}")
            except Exception as e:
                st.error(f"Failed to export history: {e}")

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    if df.empty:
        st.info("No records found. Try adjusting your search/filter, or analyze some articles first!")
        return

    st.caption(f"Showing {len(df)} record(s)")

    # ----------------------------------------------------------
    # RECORD LIST WITH DELETE ACTION
    # ----------------------------------------------------------
    for _, row in df.iterrows():
        badge_class = "badge-real" if row["prediction"] == "Real" else "badge-fake"

        rec_col1, rec_col2 = st.columns([5, 1])

        with rec_col1:
            st.markdown(
                f"""
                <div class="glass-card" style="padding: 1rem 1.4rem; margin-bottom: 0.6rem;">
                    <div style="display:flex; justify-content:space-between; flex-wrap: wrap; gap: 0.6rem;">
                        <div>
                            <strong>{truncate_text(row['headline'], 90)}</strong><br>
                            <span style="color: var(--text-secondary); font-size: 0.82rem;">
                                {format_datetime(row['timestamp'])} · Source: {row['source']} · Bias: {row['bias']}
                            </span>
                        </div>
                        <div style="text-align:right;">
                            <span class="badge {badge_class}">{row['prediction']}</span>
                            <span style="font-size:0.8rem; color: var(--text-secondary); display:block; margin-top:2px;">
                                {format_percentage(row['confidence'])}
                            </span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with rec_col2:
            if st.button("🗑️ Delete", key=f"delete_{row['id']}", use_container_width=True):
                try:
                    database.delete_prediction(int(row["id"]))
                    st.toast("Record deleted.", icon="🗑️")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not delete record: {e}")

    # ----------------------------------------------------------
    # CLEAR ALL
    # ----------------------------------------------------------
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    with st.expander("⚠️ Danger Zone"):
        st.write("This will permanently delete ALL history records. This action cannot be undone.")
        if st.button("🗑️ Clear Entire History", type="secondary"):
            try:
                count = database.clear_all_history()
                st.success(f"Deleted {count} record(s) from history.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to clear history: {e}")
