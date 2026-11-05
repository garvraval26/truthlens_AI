"""
config.py
==============================================================
Central configuration file for the AI Powered Fake News
Detection and Media Bias Analysis System.

All paths, constants, model settings, theme colors, and
app-wide configuration values live here so that no other
module hard-codes magic strings/numbers.
==============================================================
"""

import os
from pathlib import Path

# ==============================================================
# BASE PATHS
# ==============================================================
BASE_DIR = Path(__file__).resolve().parent

ASSETS_DIR = BASE_DIR / "assets"
PAGES_DIR = BASE_DIR / "pages"
MODELS_DIR = BASE_DIR / "models"
DATABASE_DIR = BASE_DIR / "database"
UPLOADS_DIR = BASE_DIR / "uploads"
EXPORTS_DIR = BASE_DIR / "exports"

# Ensure required runtime directories exist
for directory in [ASSETS_DIR, MODELS_DIR, DATABASE_DIR, UPLOADS_DIR, EXPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ==============================================================
# DATABASE CONFIG
# ==============================================================
DATABASE_PATH = str(DATABASE_DIR / "fake_news.db")

# ==============================================================
# APP METADATA
# ==============================================================
APP_NAME = "TruthLens AI"
APP_TAGLINE = "AI Powered Fake News Detection & Media Bias Analysis"
APP_VERSION = "1.0.0"
APP_ICON = "🛡️"

DEVELOPER_NAME = "Final Year Major Project"
DEVELOPER_YEAR = "2026"

# ==============================================================
# MODEL CONFIG
# ==============================================================
# Primary model (fine-tuned RoBERTa for fake news classification)
PRIMARY_MODEL_NAME = "hamzab/roberta-fake-news-classification"

# Fallback model if primary is unavailable
FALLBACK_MODEL_NAME = "jy46604790/Fake-News-Bert-Detect"

# Secondary fallback (guaranteed to exist on HuggingFace Hub)
SAFE_FALLBACK_MODEL_NAME = "distilbert-base-uncased"

# Bias detection model (zero-shot classification pipeline)
BIAS_MODEL_NAME = "facebook/bart-large-mnli"
BIAS_LABELS = ["left-leaning", "center / neutral", "right-leaning"]

MAX_SEQUENCE_LENGTH = 512
MODEL_CACHE_DIR = str(MODELS_DIR)

# Confidence thresholds
HIGH_CONFIDENCE_THRESHOLD = 0.80
MEDIUM_CONFIDENCE_THRESHOLD = 0.55

# ==============================================================
# FILE UPLOAD CONFIG
# ==============================================================
ALLOWED_UPLOAD_EXTENSIONS = ["txt", "pdf", "docx"]
MAX_UPLOAD_SIZE_MB = 10

# ==============================================================
# URL ANALYSIS CONFIG
# ==============================================================
REQUEST_TIMEOUT_SECONDS = 10
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# ==============================================================
# THEME / COLOR PALETTE
# ==============================================================
THEME_COLORS = {
    "light": {
        "bg_primary": "#F7F8FC",
        "bg_secondary": "#FFFFFF",
        "bg_card": "rgba(255, 255, 255, 0.7)",
        "text_primary": "#111827",
        "text_secondary": "#6B7280",
        "accent_primary": "#6C5CE7",
        "accent_secondary": "#00D2D3",
        "success": "#00B894",
        "danger": "#FF6B6B",
        "warning": "#FDCB6E",
        "border": "rgba(0, 0, 0, 0.08)",
        "gradient_hero": "linear-gradient(135deg, #6C5CE7 0%, #00D2D3 100%)",
    },
    "dark": {
        "bg_primary": "#0F1117",
        "bg_secondary": "#161925",
        "bg_card": "rgba(255, 255, 255, 0.05)",
        "text_primary": "#F3F4F6",
        "text_secondary": "#9CA3AF",
        "accent_primary": "#8B7CF6",
        "accent_secondary": "#00E5E8",
        "success": "#00D9A5",
        "danger": "#FF7675",
        "warning": "#FFC048",
        "border": "rgba(255, 255, 255, 0.08)",
        "gradient_hero": "linear-gradient(135deg, #4834D4 0%, #00B4B4 100%)",
    },
}

# Chart color sequences (Plotly / Altair)
CHART_COLOR_SEQUENCE = ["#6C5CE7", "#00D2D3", "#00B894", "#FF6B6B", "#FDCB6E"]

# ==============================================================
# NAVIGATION CONFIG
# ==============================================================
NAV_ITEMS = [
    {"label": "Dashboard", "icon": "📊", "key": "dashboard"},
    {"label": "News Detector", "icon": "🔍", "key": "detector"},
    {"label": "URL Analyzer", "icon": "🔗", "key": "url_analysis"},
    {"label": "Bias Detection", "icon": "⚖️", "key": "bias"},
    {"label": "History", "icon": "🕒", "key": "history"},
    {"label": "Analytics", "icon": "📈", "key": "analytics"},
    {"label": "About", "icon": "ℹ️", "key": "about"},
    {"label": "Settings", "icon": "⚙️", "key": "settings"},
]

# ==============================================================
# SESSION STATE DEFAULTS
# ==============================================================
DEFAULT_SESSION_STATE = {
    "theme": "light",
    "current_page": "landing",
    "app_started": False,
    "last_prediction": None,
}

# ==============================================================
# ENVIRONMENT / SECRETS (optional external services)
# ==============================================================
NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "")
