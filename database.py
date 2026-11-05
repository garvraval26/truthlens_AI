"""
database.py
==============================================================
SQLite database layer for the AI Powered Fake News Detection
and Media Bias Analysis System.

Handles:
    - Table creation (auto-migrate on import)
    - Inserting predictions
    - Fetching history (with search/filter)
    - Deleting records
    - Exporting to CSV
    - Aggregate stats for Dashboard / Analytics
==============================================================
"""

import sqlite3
import pandas as pd
from datetime import datetime
from contextlib import contextmanager
from pathlib import Path

from config import DATABASE_PATH, EXPORTS_DIR


# ==============================================================
# CONNECTION HELPER
# ==============================================================
@contextmanager
def get_connection():
    """
    Context-managed SQLite connection.
    Ensures connections are always closed and errors are raised
    cleanly instead of leaking open file handles.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise RuntimeError(f"Database error: {e}")
    finally:
        if conn:
            conn.close()


# ==============================================================
# TABLE INITIALIZATION
# ==============================================================
def init_db():
    """
    Creates the predictions table if it does not already exist.
    Safe to call multiple times (idempotent).
    """
    schema = """
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        headline TEXT NOT NULL,
        content_snippet TEXT,
        prediction TEXT NOT NULL CHECK (prediction IN ('Real', 'Fake')),
        confidence REAL NOT NULL,
        bias TEXT DEFAULT 'Unknown',
        bias_confidence REAL DEFAULT 0.0,
        source TEXT DEFAULT 'Manual Input',
        source_url TEXT,
        analysis_type TEXT DEFAULT 'text',
        timestamp TEXT NOT NULL
    );
    """
    with get_connection() as conn:
        conn.execute(schema)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON predictions(timestamp);"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_prediction ON predictions(prediction);"
        )


# ==============================================================
# INSERT
# ==============================================================
def insert_prediction(
    headline: str,
    content_snippet: str,
    prediction: str,
    confidence: float,
    bias: str = "Unknown",
    bias_confidence: float = 0.0,
    source: str = "Manual Input",
    source_url: str = None,
    analysis_type: str = "text",
) -> int:
    """
    Inserts a new prediction record into the database.
    Returns the newly created row id.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query = """
        INSERT INTO predictions
        (headline, content_snippet, prediction, confidence, bias,
         bias_confidence, source, source_url, analysis_type, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    with get_connection() as conn:
        cursor = conn.execute(
            query,
            (
                headline[:500] if headline else "Untitled Article",
                (content_snippet[:1000] if content_snippet else ""),
                prediction,
                float(confidence),
                bias,
                float(bias_confidence),
                source,
                source_url,
                analysis_type,
                timestamp,
            ),
        )
        return cursor.lastrowid


# ==============================================================
# FETCH
# ==============================================================
def get_all_predictions(limit: int = None) -> pd.DataFrame:
    """
    Returns all predictions as a pandas DataFrame, most recent first.
    """
    query = "SELECT * FROM predictions ORDER BY id DESC"
    if limit:
        query += f" LIMIT {int(limit)}"

    with get_connection() as conn:
        df = pd.read_sql_query(query, conn)
    return df


def search_predictions(keyword: str = "", prediction_filter: str = "All") -> pd.DataFrame:
    """
    Searches predictions by headline keyword and/or prediction label.
    """
    query = "SELECT * FROM predictions WHERE 1=1"
    params = []

    if keyword:
        query += " AND (headline LIKE ? OR source LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    if prediction_filter and prediction_filter != "All":
        query += " AND prediction = ?"
        params.append(prediction_filter)

    query += " ORDER BY id DESC"

    with get_connection() as conn:
        df = pd.read_sql_query(query, conn, params=params)
    return df


def get_prediction_by_id(record_id: int) -> dict:
    """Fetches a single prediction record by its id."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM predictions WHERE id = ?", (record_id,)
        ).fetchone()
        return dict(row) if row else None


# ==============================================================
# DELETE
# ==============================================================
def delete_prediction(record_id: int) -> bool:
    """Deletes a single prediction record by id."""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM predictions WHERE id = ?", (record_id,))
        return cursor.rowcount > 0


def clear_all_history() -> int:
    """Deletes ALL prediction records. Returns number of rows deleted."""
    with get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM predictions")
        count = cursor.fetchone()[0]
        conn.execute("DELETE FROM predictions")
        conn.execute("DELETE FROM sqlite_sequence WHERE name='predictions'")
        return count


# ==============================================================
# EXPORT
# ==============================================================
def export_to_csv(filename: str = None) -> str:
    """
    Exports all predictions to a CSV file inside the exports directory.
    Returns the full path to the generated file.
    """
    if not filename:
        filename = f"history_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    export_path = Path(EXPORTS_DIR) / filename
    df = get_all_predictions()
    df.to_csv(export_path, index=False)
    return str(export_path)


# ==============================================================
# AGGREGATE STATS (Dashboard / Analytics)
# ==============================================================
def get_summary_stats() -> dict:
    """
    Returns high-level aggregate statistics used on the Dashboard.
    """
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
        real_count = conn.execute(
            "SELECT COUNT(*) FROM predictions WHERE prediction = 'Real'"
        ).fetchone()[0]
        fake_count = conn.execute(
            "SELECT COUNT(*) FROM predictions WHERE prediction = 'Fake'"
        ).fetchone()[0]
        avg_confidence = conn.execute(
            "SELECT AVG(confidence) FROM predictions"
        ).fetchone()[0]

    return {
        "total_analyzed": total or 0,
        "real_count": real_count or 0,
        "fake_count": fake_count or 0,
        "avg_confidence": round(avg_confidence, 4) if avg_confidence else 0.0,
    }


def get_bias_distribution() -> pd.DataFrame:
    """Returns count of each bias category for charting."""
    query = """
        SELECT bias, COUNT(*) as count
        FROM predictions
        GROUP BY bias
        ORDER BY count DESC
    """
    with get_connection() as conn:
        df = pd.read_sql_query(query, conn)
    return df


def get_monthly_usage() -> pd.DataFrame:
    """Returns count of predictions grouped by month for trend charts."""
    query = """
        SELECT strftime('%Y-%m', timestamp) as month, COUNT(*) as count
        FROM predictions
        GROUP BY month
        ORDER BY month ASC
    """
    with get_connection() as conn:
        df = pd.read_sql_query(query, conn)
    return df


def get_top_sources(limit: int = 10) -> pd.DataFrame:
    """Returns the most frequently analyzed sources."""
    query = """
        SELECT source, COUNT(*) as count
        FROM predictions
        WHERE source IS NOT NULL AND source != ''
        GROUP BY source
        ORDER BY count DESC
        LIMIT ?
    """
    with get_connection() as conn:
        df = pd.read_sql_query(query, conn, params=(limit,))
    return df


def get_recent_activity(limit: int = 5) -> pd.DataFrame:
    """Returns the most recent N predictions for the Dashboard feed."""
    query = """
        SELECT headline, prediction, confidence, bias, timestamp
        FROM predictions
        ORDER BY id DESC
        LIMIT ?
    """
    with get_connection() as conn:
        df = pd.read_sql_query(query, conn, params=(limit,))
    return df


# ==============================================================
# AUTO-INITIALIZE ON IMPORT
# ==============================================================
init_db()
